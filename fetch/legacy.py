import re
import time
import smtplib
import requests
from datetime import datetime
from uuid import uuid4
from email.mime.text import MIMEText
from pydantic import BaseModel
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    EndSessionContent,
    chat_protocol_spec,
)

class LegacyCheckResponse(BaseModel):
    status: str
    message: str
    inactive_for: int = 0


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "youremail@gmail.com"   
SMTP_PASS = "apppassword"

def send_email(to_email: str, icp_address: str, inactive_for: int):
    msg = MIMEText(
        f"""
        <html>
        <body>
            <h2>🔔 Legacy Inactivity Alert</h2>
            <p>Hi,</p>
            <p>We detected inactivity for your ICP address:</p>
            <p><b>{icp_address}</b></p>
            <p>Inactive for: <b>{inactive_for} seconds</b></p>
            <p>If this was unexpected, please log in soon.</p>
            <br>
            <p>Best regards,<br>ChainPilot Legacy Agent</p>
        </body>
        </html>
        """,
        "html",
    )
    msg["Subject"] = "Legacy Alert: Inactivity Detected"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[EMAIL SENT] to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


def get_last_tx_timestamp(icp_address: str) -> int:
    url = f"https://ledger-api.internetcomputer.org/accounts/{icp_address}/transactions?limit=1&sort_by=-block_height"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        blocks = data.get("blocks", [])
        if blocks:
            return int(blocks[0]["created_at"])
    except Exception as e:
        print(f"[ICP ERROR] {e}")
    return 0


def check_user_inactivity(email: str, icp_address: str, threshold: int) -> LegacyCheckResponse:
    last_tx = get_last_tx_timestamp(icp_address)
    if last_tx == 0:
        return LegacyCheckResponse(
            status="error",
            message="No transaction found for this ICP address.",
            inactive_for=0,
        )

    now = int(time.time())
    inactive_for = now - last_tx

    if inactive_for > threshold:
        send_email(email, icp_address, inactive_for)
        return LegacyCheckResponse(
            status="alert",
            message=f"User inactive for {inactive_for} seconds, email alert sent to {email}",
            inactive_for=inactive_for,
        )
    else:
        return LegacyCheckResponse(
            status="ok",
            message=f"User active. Inactive for {inactive_for} seconds.",
            inactive_for=inactive_for,
        )


protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    text = ''.join(item.text for item in msg.content if isinstance(item, TextContent)).strip()
    if not text:
        return

    ctx.logger.info(f"[legacy_checker] Received chat: {text}")

    addr_match = re.search(r"([a-f0-9]{64})", text, re.IGNORECASE)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    threshold_match = re.search(r"(\d+)\s*(day|hour|minute)", text.lower())

    if not addr_match or not email_match:
        response_text = "Could not parse input. Please provide ICP address and email."
        result = LegacyCheckResponse(status="error", message=response_text)
    else:
        icp_address = addr_match.group(1)
        email = email_match.group(0)
        threshold = 3600
        if threshold_match:
            num = int(threshold_match.group(1))
            unit = threshold_match.group(2)
            if "day" in unit:
                threshold = num * 86400
            elif "hour" in unit:
                threshold = num * 3600
            elif "minute" in unit:
                threshold = num * 60

        result = check_user_inactivity(email, icp_address, threshold)
        response_text = result.message

    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=response_text),
                EndSessionContent(type="end-session"),
            ],
        ),
    )
    ctx.logger.info(f"[legacy_checker] Sent response to {sender}")


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


legacy_agent = Agent(
    name="legacy_checker",
    seed="legacy_secret",
    port=8005,
    mailbox=True,
    publish_agent_details=True,
)
legacy_agent.include(protocol, publish_manifest=True)


if __name__ == "__main__":
    legacy_agent.run()

import time
import smtplib
import requests
from datetime import datetime, timezone
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
    """Response model for legacy check operations"""
    status: str
    message: str
    inactive_for: int = 0
    last_activity_date: str = ""


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "chainpilot.team@gmail.com"   
SMTP_PASS = "asdm rprj mnbt ksqf"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_datetime(timestamp: int) -> str:
    """Format timestamp to YYYY-MM-DD HH:MM:SS format"""
    if timestamp == 0:
        return "Unknown"
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"

def send_email(to_email: str, icp_address: str, inactive_for: int, last_activity: str):
    duration_text = format_duration(inactive_for)
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0; font-size: 24px;">🔔 ChainPilot Legacy Alert</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Inactivity Detection System</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; 
                        border: 1px solid #e9ecef;">
                <p style="font-size: 16px; margin-bottom: 20px;">Hello,</p>
                
                <div style="background: white; padding: 15px; border-radius: 8px; 
                           border-left: 4px solid #dc3545; margin: 15px 0;">
                    <h3 style="color: #dc3545; margin-top: 0;">⚠️ Inactivity Detected</h3>
                    <p><strong>ICP Address:</strong><br>
                       <code style="background: #f8f9fa; padding: 2px 6px; border-radius: 4px; 
                                   font-family: monospace;">{icp_address}</code></p>
                    <p><strong>Inactive Duration:</strong> {duration_text}</p>
                    <p><strong>Last Activity:</strong> {last_activity}</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; 
                           border-left: 4px solid #2196f3; margin: 15px 0;">
                    <h4 style="color: #1976d2; margin-top: 0;">💡 What should you do?</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Check your ICP wallet for any issues</li>
                        <li>Verify your account security</li>
                        <li>If this was unexpected, please log in soon</li>
                        <li>Contact support if you need assistance</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;">
                        Generated on {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #666; font-size: 14px; margin-bottom: 0;">
                    Best regards,<br>
                    <strong>ChainPilot Legacy Monitoring System</strong><br>
                    <em>Keeping your crypto assets secure</em>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEText(html_content, "html")
    msg["Subject"] = f"🔔 ChainPilot Alert: Account Inactive for {duration_text}"
    msg["From"] = SMTP_USER
    msg["To"] = to_email.strip()

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ [EMAIL SENT] Successfully sent alert to {to_email}")
        return True
    except Exception as e:
        print(f"❌ [EMAIL ERROR] Failed to send email: {e}")
        return False


def get_last_tx_timestamp(icp_address: str) -> int:
    url = f"https://ledger-api.internetcomputer.org/accounts/{icp_address}/transactions?limit=1&sort_by=-block_height"
    
    try:
        print(f"🔍 [ICP API] Checking transactions for address: {icp_address[:10]}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        blocks = data.get("blocks", [])
        
        if blocks:
            timestamp = int(blocks[0]["created_at"])
            print(f"✅ [ICP API] Found last transaction at: {format_datetime(timestamp)}")
            return timestamp
        else:
            print(f"⚠️ [ICP API] No transactions found for address")
            return 0
            
    except requests.RequestException as e:
        print(f"❌ [ICP API ERROR] Network error: {e}")
        return 0
    except (KeyError, ValueError, IndexError) as e:
        print(f"❌ [ICP API ERROR] Data parsing error: {e}")
        return 0
    except Exception as e:
        print(f"❌ [ICP API ERROR] Unexpected error: {e}")
        return 0


def check_user_inactivity(email: str, icp_address: str, threshold: int) -> LegacyCheckResponse:
    
    print(f"🔎 [LEGACY CHECK] Starting inactivity check for {icp_address[:10]}...")
    print(f"📧 [LEGACY CHECK] Email: {email}")
    print(f"⏰ [LEGACY CHECK] Threshold: {format_duration(threshold)}")
    
    # Get last transaction timestamp
    last_tx = get_last_tx_timestamp(icp_address)
    
    if last_tx == 0:
        return LegacyCheckResponse(
            status="error",
            message="❌ No transaction found for this ICP address or API error occurred.",
            inactive_for=0,
            last_activity_date="Unknown"
        )

    # Calculate inactivity duration
    current_time = int(time.time())
    inactive_for = current_time - last_tx
    last_activity_date = format_datetime(last_tx)
    
    print(f"📊 [LEGACY CHECK] Last activity: {last_activity_date}")
    print(f"📊 [LEGACY CHECK] Inactive for: {format_duration(inactive_for)}")

    if inactive_for > threshold:
        print(f"🚨 [LEGACY CHECK] Threshold exceeded! Sending email alert...")
        email_sent = send_email(email, icp_address, inactive_for, last_activity_date)
        
        if email_sent:
            status_msg = f"🚨 User inactive for {format_duration(inactive_for)}. Email alert sent to {email}"
        else:
            status_msg = f"🚨 User inactive for {format_duration(inactive_for)}. Failed to send email alert to {email}"
            
        return LegacyCheckResponse(
            status="alert",
            message=status_msg,
            inactive_for=inactive_for,
            last_activity_date=last_activity_date
        )
    else:
        status_msg = f"✅ User is active. Last activity: {format_duration(inactive_for)} ago"
        print(f"✅ [LEGACY CHECK] {status_msg}")
        
        return LegacyCheckResponse(
            status="ok",
            message=status_msg,
            inactive_for=inactive_for,
            last_activity_date=last_activity_date
        )


def parse_threshold_from_text(text: str) -> int:
    threshold_match = re.search(r"(\d+)\s*(day|hour|minute)s?", text.lower())
    
    if threshold_match:
        num = int(threshold_match.group(1))
        unit = threshold_match.group(2)
        
        if "day" in unit:
            return num * 86400  
        elif "hour" in unit:
            return num * 3600   
        elif "minute" in unit:
            return num * 60
    
    return 3600  

protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc), 
            acknowledged_msg_id=msg.msg_id
        ),
    )

    text = ''.join(
        item.text for item in msg.content 
        if isinstance(item, TextContent)
    ).strip()
    
    if not text:
        await send_error_response(ctx, sender, "❌ Empty message received. Please provide ICP address and email.")
        return

    ctx.logger.info(f"💬 [LEGACY CHAT] Received from {sender[:16]}...: {text}")

    addr_match = re.search(r"([a-f0-9]{64})", text, re.IGNORECASE)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    
    if not addr_match or not email_match:
        error_msg = """❌ Could not parse input. Please provide:
        
📝 **Format:** `<ICP_ADDRESS> <EMAIL> [threshold]`

🔍 **Examples:**
• `a1b2c3d4e5f6... user@example.com`
• `a1b2c3d4e5f6... user@example.com 2 hours`
• `a1b2c3d4e5f6... user@example.com 1 day`

⚠️ **Requirements:**
• ICP address must be 64 characters (hex)
• Valid email address format
• Optional threshold: X minutes/hours/days"""
        
        await send_error_response(ctx, sender, error_msg)
        return

    icp_address = addr_match.group(1)
    email = email_match.group(0)
    threshold = parse_threshold_from_text(text)
    
    ctx.logger.info(f"📊 [LEGACY CHAT] Parsed - Address: {icp_address[:10]}..., Email: {email}, Threshold: {format_duration(threshold)}")

    try:
        result = check_user_inactivity(email, icp_address, threshold)
        
        if result.status == "error":
            response_text = f"❌ **Error:** {result.message}"
        elif result.status == "alert":
            response_text = f"""🚨 **Inactivity Alert Triggered**

📮 **ICP Address:** `{icp_address}`
📧 **Email:** {email}
⏰ **Inactive For:** {format_duration(result.inactive_for)}
📅 **Last Activity:** {result.last_activity_date}
🔔 **Status:** {result.message}

The user has exceeded the inactivity threshold of {format_duration(threshold)}."""
        else:  
            response_text = f"""✅ **User Activity Check - OK**

📮 **ICP Address:** `{icp_address}`
📧 **Email:** {email}
⏰ **Inactive For:** {format_duration(result.inactive_for)}
📅 **Last Activity:** {result.last_activity_date}
🎯 **Threshold:** {format_duration(threshold)}
✅ **Status:** User is active and within threshold."""

    except Exception as e:
        ctx.logger.error(f"❌ [LEGACY CHAT] Error processing request: {e}")
        response_text = f"❌ **System Error:** Failed to process legacy check. Please try again later.\n\nError: {str(e)}"

    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=response_text)],
        ),
    )
    
    ctx.logger.info(f"📤 [LEGACY CHAT] Response sent to {sender[:16]}...")

async def send_error_response(ctx: Context, sender: str, error_message: str):

    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=error_message)],
        ),
    )


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):

    ctx.logger.info(f"✅ [LEGACY CHAT] Acknowledgement received from {sender[:16]}...")


legacy_agent = Agent(
    name="legacy_checker",
    seed="legacy_secret_2",
    port=8010,
    mailbox=True,
    publish_agent_details=True,
)

legacy_agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    print("=" * 80)
    print("🔔 ChainPilot Legacy Checker Agent")
    print("=" * 80)
    print(f"📧 Email Service: {SMTP_USER}")
    print(f"🌐 Agent Address: {legacy_agent.address}")
    print(f"🔌 Port: 8010")
    print(f"📬 Mailbox: Enabled")
    print()
    print("🛠️  Features:")
    print("   • ICP address activity monitoring")
    print("   • Email alerts for inactive users")
    print("   • Configurable inactivity thresholds")
    print("   • Chat-based manual checks")
    print()
    print("📝 Usage Format:")
    print("   <ICP_ADDRESS> <EMAIL> [threshold]")
    print()
    print("💡 Examples:")
    print("   a1b2c3d4e5f6... user@example.com")
    print("   a1b2c3d4e5f6... user@example.com 2 hours")
    print("   a1b2c3d4e5f6... user@example.com 1 day")
    print()
    print("=" * 80)
    print("🚀 Starting Legacy Checker Agent...")
    print("📡 Connect via Agentverse mailbox for chat interface!")
    print("=" * 80)
    
    try:
        legacy_agent.run()
    except KeyboardInterrupt:
        print("\n👋 ChainPilot Legacy Checker shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")

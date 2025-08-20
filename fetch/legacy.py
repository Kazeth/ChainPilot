import time
import smtplib
import requests
from email.mime.text import MIMEText
from uagents import Agent, Context

legacy_agent = Agent(
    name="legacy_checker",
    seed="legacy_secret",
    port=8005,
    mailbox = True
)

# Data user (hardcoded untuk demo)
user = {
    "id": "user123",
    "email": "user@example.com",
    "icp_address": "c287e23d0c57058397596c20f6b03e6a1b6418ffd6c399da16f3c483a4afb675",
    "threshold": 3600,   # 1 jam
    "warned": False,
}

def get_last_tx_timestamp(icp_address: str) -> int:
    url = f"https://ledger-api.internetcomputer.org/accounts/{icp_address}/transactions?limit=1&sort_by=-block_height"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        blocks = data.get("blocks", [])
        if blocks:
            return int(blocks[0]["created_at"])
        else:
            print("⚠️ Tidak ada transaksi untuk address ini")
    except Exception as e:
        print(f"Error fetch ICP tx: {e}")
    return 0


def send_email(to_email: str, msg_body: str):
    msg = MIMEText(msg_body)
    msg["Subject"] = "⚠️ ICP Inactivity Warning"
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = to_email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("your_gmail@gmail.com", "APP_PASSWORD")  # app password gmail
            server.send_message(msg)
        print(f"📧 Email sent to {to_email}")
    except Exception as e:
        print(f"Email error: {e}")

# Cek inactivity tiap 1 menit
@legacy_agent.on_interval(period=60.0)
async def check_inactivity(ctx: Context):
    now = int(time.time())
    last_active = get_last_tx_timestamp(user["icp_address"])
    if last_active == 0:
        ctx.logger.info("Belum ada transaksi.")
        return
    else:
        ctx.logger.info(" ada transaksi.")
        
    if now - last_active > user["threshold"] and not user["warned"]:
        send_email(user["email"], f"Akun {user['icp_address']} tidak aktif > {user['threshold']} detik.")
        user["warned"] = True
        ctx.logger.info(f"⚠️ Warning dikirim ke {user['email']}")
    else:
        ctx.logger.info(f"User aktif, last tx {now - last_active} detik lalu.")

if __name__ == "__main__":
    legacy_agent.run()

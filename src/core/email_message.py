import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Celery

from core.settings import Config

app = Celery(
    "email",
    broker=f"redis://:{Config.redis.password}@{Config.redis.host}:{Config.redis.port}/0",
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = Config.email.login
PASSWORD = Config.email.password


@app.task
async def send_email_message(to_email: str, username: str):

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Привественное письмо"

    text = f"Здравствуйте {username}, спасибо что у нас"
    msg.attach(MIMEText(text, "plain", "utf-8"))

    # 3. Подключение к серверу и отправка
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, msg["To"], msg.as_string())
        print("Письмо успешно отправлено!")
    except Exception as e:  # noqa: BLE001
        print(f"Произошла ошибка при отправке: {e}")
    finally:
        if server:
            server.quit()

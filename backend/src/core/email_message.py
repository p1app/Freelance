import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Celery
from core.settings import config

app = Celery(
    "email",
    broker=f"redis://{config.redis.host}:{config.redis.port}/0",
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = config.email.login
PASSWORD = config.email.password


@app.task
def send_email_message(to_email: str, username: str):
    # 1. Создание сообщения
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Приветственное письмо"

    text = f"Здравствуйте, {username}! Спасибо, что вы с нами."
    msg.attach(MIMEText(text, "plain", "utf-8"))

    # 2. Подключение к серверу и отправка
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.ehlo()  # Знакомимся с сервером
        server.starttls()  # Включаем шифрование
        server.ehlo()  # Повторно знакомимся уже по защищенному каналу

        server.login(SENDER_EMAIL, PASSWORD)
        # Важно: передаем msg["To"], а не msg['To'] внутри метода
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Произошла ошибка при отправке: {e}")
        raise
    finally:
        if server:
            server.quit()

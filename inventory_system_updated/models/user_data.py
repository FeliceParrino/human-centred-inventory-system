import os
import smtplib
from email.message import EmailMessage

from database import get_connection
from models.schema import ensure_user_privacy_schema


def fetch_user_by_id(userID):
    ensure_user_privacy_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM `user` WHERE userID = %s', (userID,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def send_password_reset_email(email, reset_url):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_from = os.getenv('SMTP_FROM', smtp_user or 'noreply@inventory.local')

    if not smtp_host or not smtp_user or not smtp_password:
        return False

    message = EmailMessage()
    message['Subject'] = 'Inventory password reset'
    message['From'] = smtp_from
    message['To'] = email
    message.set_content(
        'You requested a password reset for Inventory.\n\n'
        f'Use this link within 30 minutes:\n{reset_url}\n\n'
        'If you did not request this, ignore this email.'
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)

    return True


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import settings


async def verify_mail(self, verify):

    msg = MIMEMultipart()
    message = str(self)

    password = settings.MAIL_PASSWORD
    msg["From"] = settings.MAIL_FROM
    msg["To"] = verify
    msg["Subject"] = "Subscription"

    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com: 587")

    server.starttls()

    server.login(msg["From"], password)

    server.sendmail(msg["From"], msg["To"], msg.as_string())

    server.quit()

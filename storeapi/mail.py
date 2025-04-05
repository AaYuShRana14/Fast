import smtplib
from email.message import EmailMessage
from storeapi.config import config
async def send_mail(to:str, body:str):
    msg=EmailMessage()
    msg["Subject"]="Verification Email"
    msg.set_content(body)
    msg["to"]=to
    msg["from"]=config.SENDER_MAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.SENDER_MAIL,config.MAIL_PASSKEY)
        smtp.send_message(msg)
        print("Email sent")


async def send_verification_mail(to:str,url:str):
    body = f"Click the link to verify your email: {url or 'Invalid URL'}"
    await send_mail(to,body)


async def send_joke_mail(email:str,joke:str):
    body = f"Here is a joke for you: {joke or 'No joke found'}"
    await send_mail(email,body)
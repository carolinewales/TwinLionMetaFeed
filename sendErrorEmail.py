from email.message import EmailMessage
import smtplib
import os

message = EmailMessage()
message['Subject'] = 'Twin Lion Meta Feed Action Failed'
message['From'] = os.environ['EMAIL_ADDRESS']
message['To'] = os.environ['EMAIL_ADDRESS']
message.set_content('An error has occured when exporting product feed(s)')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_PASSWORD'])
    smtp.send_message(message)
from email.message import EmailMessage
import smtplib
import os


logFile = 'output.log'
if not os.path.exists(logFile):
    output = 'No output.log file found.'
else:
    with open(logFile, 'r') as f:
        output = f.read()

message = EmailMessage()
message['Subject'] = 'Twin Lion Meta Feed Updated'
message['From'] = os.environ['EMAIL_ADDRESS']
message['To'] = os.environ['EMAIL_ADDRESS']
message.set_content('Successful update complete! You are awesome, have a good day. \n\nOutput:\n\n' + output[:6000])

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_PASSWORD'])
    smtp.send_message(message)

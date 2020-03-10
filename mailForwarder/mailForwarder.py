import imaplib
import smtplib
import os
import pprint
import email
from email.mime.text import MIMEText
from email.parser import Parser
import datetime

hostname = 'mailhost.example.com'
username = 'mailuser@example.com'
password = 'mypassword'

recipients = [
    "recipient1@anotherdomain.example.com",
    "recipient2@someotherplace.example.com"
]

now = datetime.datetime.now()
print (now.strftime("%Y-%m-%d %H:%M:%S"))

def open_connection():
    connection = imaplib.IMAP4_SSL(hostname)
    connection.login(username, password)
    return connection

if __name__ == '__main__':
    with open_connection() as c:
        typ, data = c.select('INBOX')
        #print (typ, data)
        num_msgs = int(data[0])
        print ('There are %d messages in INBOX' % num_msgs)
        
        typ, msg_ids = c.search(None, 'ALL');
        #print (typ, msg_ids)
        
        for msg in msg_ids[0].split():
            print ('Fetching message %d' % int(msg))
            typ, msg_data = c.fetch(msg, '(RFC822)')
            
            raw = email.message_from_bytes(msg_data[0][1])
            sender = raw["From"]
            senderName = email.utils.parseaddr(sender)[0]
            senderEmail = email.utils.parseaddr(sender)[1]
            to = raw["To"]
            subject = raw["Subject"]
            print("From: " + sender)
            print(senderName)
            print("To: " + to)
            print("Subject: " + subject)
            
            if senderEmail in recipients:
                #print("----")
                #print(raw)
                #print("----")

                raw.replace_header("From", "\""+senderName+"\" <"+username+">")
                raw.replace_header("To", ", ".join(recipients))
                raw.replace_header("Date", email.utils.formatdate(localtime=True))
                note = "Email from " + sender

                #if raw.is_multipart():
                #    plaintext_part = MIMEText(note, 'plain')
                #    raw.attach(plaintext_part)
                #    html_part = MIMEText(note, 'html')
                #    raw.attach(html_part)

                #    rawOutput = raw.as_string()

                #else:
                #rawOutput = raw.as_string() + "\n" + note

                try:
                    smtp = smtplib.SMTP(hostname, 25)
                    smtp.starttls()
                    smtp.login(username, password)
                    smtp.sendmail(username, recipients, raw.as_string())
                    c.copy(msg, 'Processed')
                    c.store(msg, '+FLAGS', '\\Deleted')
                except Exception as e:
                    print ("Error: unable to send email")
                    print (e)
                finally: 
                    smtp.quit()
            else:
                print(senderEmail + " not a valid sender")
                c.store(msg, '+FLAGS', '\\Deleted')

        c.expunge()
        c.close()

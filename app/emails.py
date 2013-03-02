from flask import render_template
from config import ADMINS
from flask.ext.mail import Message
from app import mail
from threading import Thread
from decorators import async

@async
def send_async_email(msg):
	mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = text_body
	msg.html = html_body
	send_async_email(msg)

def follower_notification(follower, followed):
    send_email("ThanksPress %s is now following you!" % follower.username,
        ADMINS[0],
        [followed.get_primary_email().email],
        render_template("emails/follower_notification.txt", 
            user = followed, follower = follower),
        render_template("emails/follower_notification.html", 
            user = followed, follower = follower))

def email_verification(email):
    send_email("ThanksPress email verification.",
        ADMINS[0],
        [email.email],
        render_template("emails/email_verification.txt", 
            email = email),
        render_template("emails/email_verification.html", 
            email = email))
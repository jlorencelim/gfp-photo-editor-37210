import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings


def email_users(user, subject, template, domain=None):
    sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_HOST_PASSWORD)
    from_email = Email(settings.DEFAULT_FROM_EMAIL)  # Change to your verified sender
    to_email = To(user.email)  # Change to your recipient
    subject = subject
    content = Content("text/html", template)
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()
    sg.client.mail.send.post(request_body=mail_json)
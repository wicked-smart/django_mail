from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.


class User(AbstractUser):
    pass 

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails_sent")
    recipients = models.ManyToManyField(User, related_name="emails_recieved")
    subject = models.CharField(max_length=256)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    forwarded_from = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name="forwards" )
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    bcc = models.ManyToManyField(User, blank=True, null=True, related_name="bccd")
    parent_email = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    thread = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name="reply_thread")


    def __str__(self):
        return f"{self.subject} <{self.user.email}>"
    
    def recipients_email_list(self):
        return [user.email for user in self.recipients.all()]

    def bcc_list(self):
        return [user.email for user in self.bcc.all()]
    
    def is_parent(self):
        return self.parent_email is None

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "sender": self.sender.email,
            "reciever": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "read": self.read, 
            "archived": self.archived
        }



class ScheduledEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_emails")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails_to_be_sent")
    recipients = models.ManyToManyField(User, related_name="emails_to_be_recieved")
    subject = models.CharField(max_length=256)
    body = models.TextField(blank=True)
    scheduled_datetime = models.DateTimeField()
    bcc = models.ManyToManyField(User, blank=True, null=True, related_name="bccd_to_be_emails")

    def __str__(self):
        return f"{self.subject} <{self.user.email}>"


class Attachment(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to='attachments/')

    def __str__(self):
        return f"{self.email} {self.file.name}"
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
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} <{self.user.email}>"
    
    def recipients_email_list(self):
        return [user.email for user in self.recipients.all()]

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



        

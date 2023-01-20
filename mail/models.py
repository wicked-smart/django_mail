from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass 

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails_sent")
    reciever = models.ManyToManyField(User, related_name="emails_recieved")
    subject = models.CharField(max_length=256)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    

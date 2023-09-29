from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.core.files import File
from django.utils.html import mark_safe
from PIL import Image
from pathlib import Path
from project3_cs50.settings import *
from pdf2image import convert_from_path

# Create your models here.


class User(AbstractUser):
    pass 


class UploadedFile(models.Model):
    file = models.FileField(upload_to="attachments/")
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)

    def __str__(self):
        return f"{self.file.name}"
'''
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            # Generate and save a thumbnail when an attachment is uploaded
            if not self.thumbnail:
                self.generate_thumbnail()
                super().save(*args, **kwargs)

    def generate_thumbnail(self):
    
        if self.file.name.endswith('.pdf'):
            # Generate thumbnail for PDF
            pages = convert_from_path(self.file.path, dpi=100)
            if pages:
                page = pages[0]
                thumbnail_path = BASE_DIR / MEDIA_ROOT / 'thumbnails'/ f"{self.file.name.split('/')[1]}"
                page.save(thumbnail_path, 'JPEG')
                with open(str(thumbnail_path), 'rb') as thumbnail_file:
                    self.thumbnail= File(thumbnail_file)
        else:
            # Generate thumbnail for image (as in your original code)
            img = Image.open(self.file.path)
            if img:
                img.thumbnail((100, 100))  # Adjust the size as needed
                thumbnail_path = BASE_DIR / MEDIA_ROOT / 'thumbnails'/ f"{self.file.name.split('/')[1]}"
                print("thumbnails path := ", thumbnail_path)
                img.save(str(thumbnail_path))
                with open(str(thumbnail_path), 'rb') as thumbnail_file:
                    self.thumbnail= File(thumbnail_file)


'''
    
    
    

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails_sent")
    recipients = models.ManyToManyField(User, related_name="emails_recieved")
    subject = models.CharField(max_length=256)
    body = models.TextField(blank=True)
    attachments = models.ManyToManyField(UploadedFile, related_name="attached_to") #add attachments
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
    attachments = models.ManyToManyField(UploadedFile, related_name="attachments_to") #add attachments
    recipients = models.ManyToManyField(User, related_name="emails_to_be_recieved")
    subject = models.CharField(max_length=256)
    body = models.TextField(blank=True)
    scheduled_datetime = models.DateTimeField()
    bcc = models.ManyToManyField(User, blank=True, null=True, related_name="bccd_to_be_emails")

    def __str__(self):
        return f"{self.subject} <{self.user.email}>"



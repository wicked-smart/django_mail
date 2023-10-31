from celery import shared_task
from .models import *


@shared_task
def add(a,b):
    return a+b

@shared_task
def send_email_at_scheduled_time(id, subject,reciepients, bcc,  body,  scheduled_time, attachments=None):
    try:
        sender = User.objects.get(pk=id)
        email = Email.objects.create(user=sender, 
                                    sender=sender, 
                                    subject=subject,
                                    body=body)


        #add all recipients 
        for valid_recipient_id in reciepients:
            reciepient = User.objects.get(pk=valid_recipient_id)
            email.recipients.add(reciepient)
        
        #all all bcc'd reciepients
        for bar in bcc:
            foobar = User.objects.get(pk=bar)
            email.recipients.add(foobar)
            email.bcc.add(foobar)

        #add attachements 
        for file in attachments:
            upload_file = UploadedFile(file=file)
            print("updalod_file path on server := ", upload_file.file.path)
            upload_file.save()
            email.attachments.add(upload_file)

        email.save()

        #After Succesfull sending email, delete the record from ScheduledEmail model
        scheduled_email = ScheduledEmail.objects.filter(user=sender, sender=sender, subject=subject, body=body, scheduled_datetime=scheduled_time)
        scheduled_email.delete()

    except Exception as e:
        print(e)
    
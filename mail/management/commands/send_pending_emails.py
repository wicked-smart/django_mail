from django.core.management.base import BaseCommand, CommandError
from mail.models import ScheduledEmail
from datetime import datetime
from mail.tasks import * 
import subprocess

class Command(BaseCommand):

    help = 'Send scheduled emails and terminate overdue tasks' 

    def handle(self, *args, **options):

        # Check if the Celery worker is running
        if not self.is_celery_worker_running():
            self.stdout.write(self.style.WARNING('Celery worker is not running. Scheduled tasks cannot be caught up.'))
            return
        
        now  = datetime.now()

        pending_emails = ScheduledEmail.objects.filter(scheduled_datetime__lte=now)
        if len(pending_emails) == 0:
            self.stdout.write(self.style.SUCCESS('No Pending Emails Remaining as of now!!'))
            return

        for email in pending_emails:
            recipients_id = [reciepient.id for reciepient in email.recipients.all() ]
            bcc_ids = [bcc.id for bcc in email.bcc.all() ]
            try:
                send_email_at_scheduled_time(email.user.id, email.subject, recipients_id, bcc_ids, email.body,email.scheduled_datetime)
                email.delete()
            except:
                raise CommandError(f"Error sending pending email {email.user.email}")

        self.stdout.write(self.style.SUCCESS('All pending Scheduled emails sent'))
    
    def is_celery_worker_running(self):
        try:
            # Check if the Celery worker process is running
            result = subprocess.run(['celery', '-A', 'mail', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
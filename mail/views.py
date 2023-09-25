from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, resolve 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse
from django.db.models import Q 
from pathlib import PurePath
from .tasks import *
from django.template.defaultfilters import linebreaksbr
import re
import json 
from .utils import CustomJSONEncoder
from datetime import datetime, timedelta
from celery.result import AsyncResult


# Create your views here.

def index(request):
    
    if request.user.is_authenticated:
        user = request.user
        emails = Email.objects.filter(recipients=user)
        return render(request, "mail/index.html", 
        {
            "emails": emails,
            "emails_count": emails.count()
         })
    else:
        return HttpResponseRedirect(reverse("login"))


#register
def register_view(request):
    if request.method == "GET":
        return render(request, "mail/register.html")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email= request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        username = email.split('@')[0]

        print(f"username:= {username}")
        


        if password != confirmation:
            return render(request, "mail/register.html", {"confirmation_error": "password and confirmation does not match!!"})
        
        try:
            user = User.objects.create_user(username=username)

            user.set_password(password)

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            

            user.save()

        except IntegrityError as e:
            return render(request, "mail/register.html", {"integrity_error": "User already exists! Try with different emailid..."})

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

#login to your email
def login_view(request):
    if request.method == "GET":
        return render(request, "mail/login.html")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"email := {email} and password := {password}")

        username = email.split('@')[0]
        print(username)

        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mail/login.html", {"login_error": "Invalid Username and/or Password !"})



#logout off your email
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



def email(request, mail_id):

    #mark mail as read
    Email.objects.filter(id=mail_id).update(read=True)
    email = Email.objects.get(pk=mail_id)

    
    # extract referer from http headers and pass the view name to the template file
    try:
        referrer = request.META['HTTP_REFERER']
        url_path = urlparse(referrer).path
        print(resolve(url_path).url_name)
        view_name = resolve(url_path).view_name
    
    except KeyError:
        return HttpResponseRedirect(reverse('index'))

    # Extract forward history
    email2 = email
    forward_history = []
    while email2:
        email2 = email2.forwarded_from
        if email2:
            forward_history.append(email2)

    #forward_history = forward_history[::-1]

    #  introduce line breaks
    for history_entry in forward_history:
        history_entry.body = linebreaksbr(history_entry.body)

    print(forward_history)
    # Prepare the forwarded message
    forwarded_message = ""
    for history in forward_history:
        
        forwarded_message += linebreaksbr(email.body)
        forwarded_message += f"<br>----------------Forwarded message------------<br>"
        forwarded_message += f"From: <b>{history.user.username}</b> &lt;{history.sender.email}&gt;<br>"
        forwarded_message += f"Date: {history.timestamp}|date:'D, d M Y, H:i'<br>"
        forwarded_message += f"Subject: {history.subject}<br><br>"
        forwarded_message += f"{history.body} <br><br>"
        

        print(forwarded_message)
    
    #prepare emails to display excluding bcc'd ones
    all_recipients = email.recipients_email_list()
    bcc_list = email.bcc_list()
    recipients_to_display = [recipient for recipient in all_recipients if recipient not in bcc_list]


    return render(request, "mail/email_detail.html", {
        "email": email,
        "redirect_view_name": view_name,
        "forward_history": forward_history,
        "forwarded_message": forwarded_message,
        "recipients_to_display": recipients_to_display
    })

def emails_sent(request):
    
    emails = Email.objects.filter(sender=request.user)


    return render(request, "mail/sent_emails.html", {
        "emails": emails,
        "emails_count": len(emails)
    })
    

def compose(request):

    if request.method == "GET":
        return render(request, "mail/compose.html",
            {
                "purpose": "compose"
            }
        )
    else:
        recipients = request.POST.get("recipients")
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        cc = request.POST.get("cc")
        bcc = request.POST.get("bcc")

        print("recipients := ", recipients)
        print("cc := ", cc)
        print("bcc := ", bcc)


        if recipients == None or len(recipients) == 0: 
            return render(request, "mail/compose.html", {
                "purpose": "compose",
                "recipients_error_message": "you need to have atleast one recipient"
                })
        
        elif subject == None or len(subject) == 0:
            return render(request, "mail/compose.html", {
                "purpose": "compose",
                "subject_error_message": "subject cannot be empty!!"
                })
        else:

            # make a valid email address list of recipients objects
            valid_recipients = []
            recipients = recipients.split(", ")
            cc = cc.split(", ")

            #merge cc with reciepients 
            for bar in cc:
                if bar not in recipients:
                    recipients.append(bar) 

            #bcc receipients 
            bcc = bcc.split(", ")

            for recipient in recipients:
                try:
                    user = User.objects.filter(email=recipient)
                    valid_recipients.append(user[0])
                
                except:
                    pass
            
            #build valid bcc list
            print("re := ", recipients)
            print("bccccc := ", bcc)
            valid_bcc = []
            for bar in bcc:
                try:
                    user = User.objects.filter(email=bar)
                    valid_bcc.append(user[0])
                
                except:
                    pass
            
            print("valid_bcc:= ", valid_bcc)
            
            email = Email.objects.create(user=request.user, sender=request.user)
            email.subject = subject
            email.body= body

            #add all recipients 
            for valid_recipient in valid_recipients:
                email.recipients.add(valid_recipient)
            
            #all all bcc'd reciepients
            for bar in valid_bcc:
                email.recipients.add(bar)
                email.bcc.add(bar)

            email.save()

            return HttpResponseRedirect(reverse("index"))


#function to forward your  email id
def forward(request, email_id):

    #get the email 
    email = Email.objects.get(id=email_id)

    if request.method == "GET":
        
        email2 = email
        forward_history = []

        while email2:
            email2 = email2.forwarded_from
            if email2:
                forward_history.append(email2)

        #forward_history = forward_history[::-1]

        #  introduce line breaks
        for history_entry in forward_history:
            history_entry.body = linebreaksbr(history_entry.body)

        print(forward_history)
        # Prepare the forwarded message
        forwarded_message = ""
        for history in forward_history:
            
            forwarded_message += linebreaksbr(email.body)
            forwarded_message += f"<br>----------------Forwarded message------------<br>"
            forwarded_message += f"From: <b>{history.user.username}</b> &lt;{history.sender.email}&gt;<br>"
            forwarded_message += f"Date: {history.timestamp}|date:'D, d M Y, H:i'<br>"
            forwarded_message += f"Subject: {history.subject}<br><br>"
            forwarded_message += f"{history.body} <br><br>"
            

            print(forwarded_message)


        
        return render(request, "mail/compose.html",
        {
            "purpose": "forward",
            "email": email,
            "forwarded_message": forwarded_message
        })
    
    else:
        
        subject = request.POST.get("subject")
        recipients = request.POST.get("recipients")
        body = request.POST.get("body") #error inserted

        x = re.sub("<[^<]+?>",'',body)
        idx = x.find("----------------Forwarded message------------")
        print(x)

        x = x[:idx]

        


        #find valid list 
        valid_recipients = []
        recipients = recipients.split(", ")

        for recipient in recipients:
            try:
                user = User.objects.filter(email=recipient)
                valid_recipients.append(user[0])
                
            except:
                pass

        # check for invalid or empty fields
        
        new_email = Email.objects.create(user=request.user, sender=request.user, forwarded_from=email)

        new_email.subject = subject
        new_email.body = x

        
        for recipient in valid_recipients:
            new_email.recipients.add(recipient)
        
        if len(valid_recipients) != 0:
            new_email.save()

        return HttpResponseRedirect(reverse("index"))


# reply function 
def reply(request, email_id):

    email= Email.objects.get(id=email_id)
    
    if request.method == 'GET':
        return render(request, "mail/compose.html",
            {
                "purpose": "reply",
                "email": email
                
            })
    
    elif request.method == 'POST':

        subject  = request.POST.get("subject")
        reply_body = request.POST.get("reply")  
        recipients = request.POST.get("recipients")

        print(reply_body)

        foo = re.sub("<[^<]+?>",'',reply_body)
        bar = re.sub(r'\s+', ' ', foo)
        
        recipients = recipients[4:]


        #find valid recipients list 
        valid_recipients = []
        recipients = recipients.split(", ")

        for recipient in recipients:
            try:
                user = User.objects.filter(email=recipient)
                valid_recipients.append(user[0])
                
            except:
                pass


        if not reply_body or len(bar) == 1:
            return render(request, "mail/compose.html", {
                "purpose": "reply",
                "email": email,
                "message": "Reply cannot be empty!!"
         })
        
        # save as reply
        
        new_reply = Email.objects.create(
                    user=request.user,
                    sender=request.user,
                    subject=subject,
                    body=reply_body,
                    parent_email=email,
                    thread=email.thread if email.thread else email
                )
            
        
        for recipient in valid_recipients:
            new_reply.recipients.add(recipient)

        new_reply.save()

        return HttpResponseRedirect(reverse('index'))
        
    
            
 
        



def reply_all(request, email_id):
   
    email= Email.objects.get(id=email_id)
    
    if request.method == 'GET':
        return render(request, "mail/compose.html",
            {
                "purpose": "reply all",
                "email": email
                
            })
    
    elif request.method == 'POST':

        subject  = request.POST.get("subject")
        reply_body = request.POST.get("reply_all")  
        recipients = request.POST.get("recipients")


        foo = re.sub("<[^<]+?>",'',reply_body)
        bar = re.sub(r'\s+', ' ', foo)


        recipients = recipients[4:]  


        #find valid recipients list 
        valid_recipients = []
        recipients = recipients.split(", ")

        for recipient in recipients:
            try:
                user = User.objects.filter(email=recipient)
                valid_recipients.append(user[0])
                
            except:
                pass


        if not reply_body or len(bar) == 1:
            return render(request, "mail/compose.html", {
                "purpose": "reply all",
                "email": email,
                "message": "Reply cannot be empty!!"
         })
        
        # save as reply
        
        new_reply = Email.objects.create(
                    user=request.user,
                    sender=request.user,
                    subject=subject,
                    body=reply_body,
                    parent_email=email,
                    thread=email.thread if email.thread else email
                )
            
        
        if email.forwarded_from is None:
            for recipient in valid_recipients:
                new_reply.recipients.add(recipient)
        else:
            #build forward list and attach all to the recipients list
            history = []
            while email:
                history.append(email)
                email = email.forwarded_from

            forward_history = history[::-1]
            print("forward history := ", forward_history)
            for forwarders in forward_history:
                new_reply.recipients.add(forwarders.user)

        
        new_reply.save()

        return HttpResponseRedirect(reverse('index'))
        
    # new_email.receipients.add(email.reciepients.all())
    # get forwarding history 
    


def schedule_send(request):
    
    if request.method == 'POST':
        print("request post:= ", request.POST)
        schedule_date_str = request.POST.get('scheduleDate')
        schedule_time_str = request.POST.get('scheduleTime')

        # Combine date and time strings into a single datetime object
        schedule_datetime_str = f'{schedule_date_str} {schedule_time_str}'
        scheduled_datetime = datetime.strptime(schedule_datetime_str, '%Y-%m-%d %H:%M')

        print(scheduled_datetime)
        print(type(scheduled_datetime))
        if scheduled_datetime < datetime.now():
             return render(request, "mail/compose.html", {
                "purpose": "compose",
                "recipients_error_message": "invalid schedule"
                })   
        
        recipients = request.POST.get("recipients")
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        cc = request.POST.get("cc")
        bcc = request.POST.get("bcc")

        print("recipients := ", recipients)
        print("cc := ", cc)
        print("bcc := ", bcc)


        if recipients == None or len(recipients) == 0: 
            return render(request, "mail/compose.html", {
                "purpose": "compose",
                "recipients_error_message": "you need to have atleast one recipient"
                })
        
        elif subject == None or len(subject) == 0:
            return render(request, "mail/compose.html", {
                "purpose": "compose",
                "subject_error_message": "subject cannot be empty!!"
                })
        else:

            # make a valid email address list of recipients objects
            valid_recipients = []
            recipients = recipients.split(", ")
            cc = cc.split(", ")

            #merge cc with reciepients 
            for bar in cc:
                if bar not in recipients:
                    recipients.append(bar) 

            #bcc receipients 
            bcc = bcc.split(", ")

            for recipient in recipients:
                try:
                    user = User.objects.filter(email=recipient)
                    valid_recipients.append(user[0])
                
                except:
                    pass
            
            #build valid bcc list
            print("re := ", recipients)
            print("bccccc := ", bcc)
            valid_bcc = []
            for bar in bcc:
                try:
                    user = User.objects.filter(email=bar)
                    valid_bcc.append(user[0])
                
                except:
                    pass
            
            print("valid_bcc:= ", valid_bcc)
            

            #Store the scheduled emails in the db
            scheduleEmail = ScheduledEmail.objects.create(
                user=request.user,
                sender=request.user,
                subject=subject,
                body=body,
                scheduled_datetime=scheduled_datetime
            )

            for recipient in valid_recipients:
                scheduleEmail.recipients.add(recipient)
            
            scheduleEmail.save()
            
    
            valid_recipients_ids = [recipient.id for recipient in valid_recipients ]
            valid_bcc_ids = [recipient.id for reciepient in valid_bcc]

            output = test_celery_connection.delay()
            print("celery result := ", output.get())

            #call tasks in tasks.py
            countdown = scheduled_datetime - datetime.now()
            email_sent = send_email_at_scheduled_time.apply_async(args=[request.user.id, subject, valid_recipients_ids, valid_bcc_ids, body, scheduled_datetime], countdown=countdown.seconds)
            return HttpResponseRedirect(reverse('index'))


def testing_celery():

    
    scheduled_time = datetime.now() + timedelta(minutes=3)
    countdown = scheduled_time - datetime.now()
    result = add.apply_async(args=[23,34], countdown=countdown.seconds)
    task_id= result.task_id
    result = AsyncResult(task_id)
    return HttpResponse({'result': result.get()})
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, resolve 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse
from pathlib import PurePath
import re

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



    #print email referrer
    return render(request, "mail/email_detail.html",
    {
        "email": email,
        "redirect_view_name": view_name
    })


def emails_sent(request):
    
    emails = Email.objects.filter(sender=request.user)

    return render(request, "mail/sent_emails.html", {
        "emails": emails,
        "emails_count": emails.count()
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

        print(body)

        if recipients == None or subject == None or body == None:
            return render(request, "mail/compose.html", {
                "purpose": "compose",
                "message": "some fields are missing "
                })
        else:

            # make a valid email address list of recipients objects
            valid_recipients = []
            recipients = recipients.split(", ")

            for recipient in recipients:
                try:
                    user = User.objects.filter(email=recipient)
                    valid_recipients.append(user[0])
                
                except:
                    pass
            
            email = Email.objects.create(user=request.user, sender=request.user)
            email.subject = subject
            email.body= body

            #add all recipients 
            for valid_recipient in valid_recipients:
                email.recipients.add(valid_recipient)
            
            email.save()

            return HttpResponseRedirect(reverse("index"))


#function to forward your  email id
def forward(request, email_id):

    #get the email 
    email = Email.objects.get(id=email_id)

    if request.method == "GET":
        return render(request, "mail/compose.html",
        {
           "purpose": "forward",
           "email": email
        })
    
    else:
        
        subject = request.POST.get("subject")
        recipients = request.POST.get("recipients")
        body = request.POST.get("body")

        x = re.sub("<[^<]+?>",'',body)

        print(type(body))

        print(body)
        print(x)

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
        
        new_email = Email.objects.create(user=request.user, sender=request.user)

        new_email.subject = subject
        new_email.body = body

        for recipient in valid_recipients:
            new_email.recipients.add(recipient)
        
        new_email.save()
        return HttpResponseRedirect(reverse("index"))
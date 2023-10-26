## Mail Web-app 
A Lighweight Gmail like web-app that let users send and receive emails in thier inbox.

# Screenshot of pages

# Tech stack used :
    * Django, Celery, Postgres (Backend)
    * Html, CSS, Bootstrap , jQuery (Frontend)
    * Heorku (Deployment)

# Features

    * Ability to sign up, login and logout
    * Welcome email on sign up containing information to get started 
    * Compose and send email, with cc/bcc enabled 
    * ‌Receive emails in Inbox and dynamically switch back to respective  inbox/sent/archived page from email detail page using HTTP_REFERER header field 
    * Schedule sending email at custom date and time using celery 
    * Forward emails to other users 
    * ‌UI showing the forward history of an email by adding a forwarded_from db field to Email model
‌    * **Reply** to an email  and it's recipient 
‌    * **Reply all**  to an email and it's forwarders and all recipients
    * ‌Both previous features made possible by adding thread_email , parent_email field in the db
‌    * Send multiple attachments with an email and UI showing all the downloadable attachments
‌    * Features like archiving old emails, deleting an email and mark emails read





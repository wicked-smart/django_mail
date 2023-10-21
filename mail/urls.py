from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('email/<int:mail_id>/', views.email, name="email"),
    path('emails_sent/', views.emails_sent, name="sent_emails"),
    path('compose/', views.compose, name="compose"),
    path('archived_emails/', views.archived_emails, name="archived_emails"),
    path('forward/<int:email_id>', views.forward, name="forward"),
    path('reply/<int:email_id>', views.reply, name="reply"),
    path('reply_all/<int:email_id>', views.reply_all, name="reply_all"),
    path('schedule_send/', views.schedule_send, name="schedule_send"),
    path('delete_email/<int:email_id>', views.delete_email, name="delete_email"),
    path('archive/<int:email_id>', views.archive, name="archive"),
    path('add', views.add, name="add")
]
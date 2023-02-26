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
    path('forward/<int:email_id>', views.forward, name="forward")
]
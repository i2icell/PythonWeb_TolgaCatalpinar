from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login, name='login'),
    path('homepage/', views.homepage, name='homepage'),
    path('forgot-password/', views.forgotPassword, name='forgot_password'),

]

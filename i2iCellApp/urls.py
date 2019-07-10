from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login, name='login'),
    path('homepage/', views.homepage, name='homepage'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('register/', views.register, name='register'),

]

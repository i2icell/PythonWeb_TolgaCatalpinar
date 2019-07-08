from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

posts = [
    {
        'phoneNum': '555',
        'password': '123'
    },
    {
        'phoneNum': '223',
        'password': '456'
    }
]
def login(request):
    context = {
        'posts': posts
    }
    return render(request, 'i2iCellApp/login.html', context)

def homepage(request):
    return render(request, 'i2iCellApp/homepage.html')

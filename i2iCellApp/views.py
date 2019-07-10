from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from requests.exceptions import ConnectionError
import requests
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import QueryDict
# Create your views here.

proxies = {
  "http": None,
  "https": None,
}

endpoint = 'http://68.183.75.84:8080/i2iCellService/services/Services/login'

def login(request):
    post = request.POST.copy()

    if post.get('login_button'):
        qd = QueryDict(mutable=True)
        qd.update(
            inputPhoneNumber=request.POST.get('phone_num'),
            inputPassword=request.POST.get('password')
        )

        print("---------------You are in")
        url = '{}?{}'.format(endpoint, qd.urlencode())
        print("---------------Url: " + url)
        response = requests.get(url, proxies=proxies)

        #result = response.text
        result = returnValidationValue(response.text)

        if(result == '1'):
            return render(request, 'i2iCellApp/homepage.html')
        else:
            #Phone number not found
            #Phone number and password does not match
            #No connection
            print(response)

            messages.error(request, "Yanlis Kullanici Numarasi Veya Sifre!")



    elif post.get('forgot_button'):
        return render(request, 'i2iCellApp/forgot_password.html')
    elif post.get('register_button'):
        return render(request, 'i2iCellApp/register.html')
    return render(request, 'i2iCellApp/login.html')

def returnValidationValue( response):
    searchedValue = "<ns:return>"

    lengthOfSeachedValue = len(searchedValue)

    startingIndexOfValue = response.index(searchedValue)
    lengthOfReturnValue = 1

    startingIndexOfReturnValue = startingIndexOfValue + lengthOfSeachedValue
    return (response[startingIndexOfReturnValue: startingIndexOfReturnValue + lengthOfReturnValue])

def homepage(request):
    return render(request, 'i2iCellApp/homepage.html')

def forgotPassword(request):
    return render(request, 'i2iCellApp/forgot_password.html')

def register(request):
    return render(request, 'i2iCellApp/register.html')

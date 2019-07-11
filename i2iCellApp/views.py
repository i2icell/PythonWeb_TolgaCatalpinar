from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from requests.exceptions import ConnectionError
import requests
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import QueryDict
import re
from datetime import date

# Create your views here.

proxies = {
    "http": None,
    "https": None,
}

loginEndpoint = 'http://68.183.75.84:8080/i2iCellService/services/Services/login'
registerEndpoint = 'http://68.183.75.84:8080/i2iCellService/services/Services/createAccount'
getBalancesEndpoint = 'http://68.183.75.84:8080/i2iCellService/services/Services/getBalances'

def loginEncodeUrl(inputPhoneNumber, inputPassword):
    qd = QueryDict(mutable=True)
    qd.update(
        inputPhoneNumber=inputPhoneNumber,
        inputPassword=inputPassword
    )

    url = '{}?{}'.format(loginEndpoint, qd.urlencode())
    return url


def login(request):
    post = request.POST.copy()

    if post.get('login_button'):

        inputPhoneNumber = request.POST.get('phone_num')
        inputPassword = request.POST.get('password')

        if len(inputPhoneNumber) <= 0 or len(inputPassword) <= 0:
            messages.error(request, "Bos alan birakilmamalidir!")
        elif inputPhoneNumber[0] == 0 or len(inputPhoneNumber) != 10:
            messages.error(request, "Telefon numaranizi basinda 0 olmadan 10 haneli giriniz.")
        elif not isValidPhoneNumber(inputPhoneNumber):
            messages.error(request, "Telefon numaraniz sadece rakamlardan olusabilir.")
        else:
            try:
                response = requests.get(loginEncodeUrl(inputPhoneNumber, inputPassword), proxies=proxies)
                request.session['phoneNumber'] = inputPhoneNumber
            except ConnectionError as e:
                print(e)
                messages.error(request, "Internet baglantiniz yok!")

            result = returnValidationValue(response.text)

            if result == '1':
                return render(request, 'i2iCellApp/homepage.html')
            else:
                messages.error(request, "Yanlis Kullanici Numarasi Veya Sifre!")

    elif post.get('forgot_button'):
        return render(request, 'i2iCellApp/forgot_password.html')
    elif post.get('register_button'):
        return render(request, 'i2iCellApp/register.html')

    return render(request, 'i2iCellApp/login.html')


def forgotPassword(request):
    post = request.POST.copy()
    if post.get('save_button'):
        print("forgot in")
    return render(request, 'i2iCellApp/forgotPassword.html')


def registerEncodeUrl(inputFirstName, inputLastName, inputPhoneNumber, inputEmail, inputPassword, inputBirthDate,
                      inputTcNumber):
    qd = QueryDict(mutable=True)
    qd.update(
        inputFirstName=inputFirstName,
        inputLastName=inputLastName,
        inputPhoneNumber=inputPhoneNumber,
        inputEmail=inputEmail,
        inputPassword=inputPassword,
        inputBirthDate=inputBirthDate,
        inputTcNumber=inputTcNumber
    )

    url = '{}?{}'.format(registerEndpoint, qd.urlencode())
    return url


def register(request):
    print("register method in")
    post = request.POST.copy()

    if post.get('create_user_button'):
        print("create button pressed")

        day = post.get('day_box', '0')
        month = post.get('month_box', '0')
        year = post.get('year_box', '0')

        tcNo = post.get('tc_no')
        userName = post.get('user_name')
        userLastName = post.get('user_last_name')
        birthDate = day + "/" + month + "/" + year
        phoneNumber = post.get('phone_number')
        password = post.get('password')
        email = post.get('email')

        try:
            if not isValidTCID(tcNo):
                messages.error(request, "Verilen Kimlik Numarasi Bilgileri Yanlistir!")

            elif not isUserOldEnough(12, birthDate):
                messages.error(request, "Kayit olmak icin yasiniz yetmemektedir.")

            elif not (len(phoneNumber) > 0 and len(password) > 0 and len(userLastName) > 0 and \
                  (len(day) > 0 and len(month) > 0 and len(year) > 0) and len(phoneNumber) > 0 and len(password) > 0):
                messages.error(request, "Bos alan birakilmamalidir!")
            elif not (phoneNumber[0] != 0 and len(phoneNumber) == 10):
                messages.error(request, "Telefon numaranizi basinda 0 olmadan 10 haneli giriniz.")

            elif not isValidPhoneNumber(phoneNumber):
                messages.error(request, "Telefon numaraniz sadece rakamlardan olusabilir.")
            elif not isValidPassword(password):
                messages.error(request,
                           "Sifreniz en az 10 karakterli olmali, kücük harf, büyük harf ve en az bir rakam icermelidir.")
            elif not isValidEmail(email):
                messages.error(request, "Bu email adresi gecerli degildir.")
            else:
                try:
                    response = requests.get(registerEncodeUrl(userName, userLastName,phoneNumber, email, password, birthDate, tcNo), proxies=proxies)
                    request.session['phoneNumber'] = phoneNumber
                except ConnectionError as e:
                    print(e)
                    messages.error(request, "Internet baglantiniz yok!")

                result = returnValidationValue(response.text)

                if result == '1':
                    return render(request, 'i2iCellApp/homepage.html')
                else:
                    messages.error(request, "Bu telefon numarasi zaten mevcut.")
                    return render(request, 'i2iCellApp/register.html')
        except:
                messages.error(request, "Gecerli bir tarih giriniz.")

    return render(request, 'i2iCellApp/register.html')


def returnValidationValue(response):
    try:
        searchedValue = "<ns:return>"

        lengthOfSeachedValue = len(searchedValue)

        startingIndexOfValue = response.index(searchedValue)
        lengthOfReturnValue = 1

        startingIndexOfReturnValue = startingIndexOfValue + lengthOfSeachedValue
        return (response[startingIndexOfReturnValue: startingIndexOfReturnValue + lengthOfReturnValue])
    except:
        return 0


def homepage(request):
    return render(request, 'i2iCellApp/homepage.html')


def isValidPhoneNumber(inputPhoneText):
    return inputPhoneText.isdigit()


def isValidTCID(value):
    value = str(value)

    if not len(value) == 11:
        return False

    if not value.isdigit():
        return False

    if int(value[0]) == 0:
        return False

    digits = [int(d) for d in str(value)]

    if not sum(digits[:10]) % 10 == digits[10]:
        return False

    if not (((7 * sum(digits[:9][-1::-2])) - sum(digits[:9][-2::-2])) % 10) == digits[9]:
        return False

    return True


def isValidPassword(inputPassword):
    if (any(x.isupper() for x in inputPassword) and any(x.islower() for x in inputPassword)
            and any(x.isdigit() for x in inputPassword) and len(inputPassword) >= 10):
        return True
    return False


def isValidEmail(email):
    return re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)


def isUserOldEnough(yearConstraint, birthDate):
    today = date.today().strftime('%Y/%m/%d')

    todayYear = today[0:4]
    todayMonth = today[5:7]
    todayDay = today[8:10]

    birthYear = birthDate[6:10]
    birthMonth = birthDate[3:5]
    birthDay = birthDate[0:2]

    fDate = date(int(birthYear), int(birthMonth), int(birthDay))
    lDate = date(int(todayYear), int(todayMonth), int(todayDay))

    dayDifference = lDate - fDate

    return (dayDifference.days / 365 > yearConstraint)

def getBalancesEncodeUrl(inputPhoneNumber):
    qd = QueryDict(mutable=True)
    qd.update(
        inputPhoneNumber=inputPhoneNumber,
    )

    url = '{}?{}'.format(getBalancesEndpoint, qd.urlencode())
    return url

def getBalances(request):
    try:
        phoneNumber = request.session['phoneNumber']
        messages.error(request, "phone number: " + phoneNumber)

        # response = requests.get("http://68.183.75.84:8080/i2iCellService/services/Services/getBalances?inputPhoneNumber=5552239999", proxies = proxies)
        response = requests.get(getBalancesEncodeUrl(phoneNumber), proxies=proxies)
        print(response.text)
        balances = extractBalances(request, response.text)
        gb = balances[0]
        sms = balances[1]
        dk = balances[2]

        return render(request, 'i2iCellApp/getBalances.html', {'gb': gb, 'sms' : sms, 'dk' : dk})
    except:
        return render(request, 'i2iCellApp/login.html')

def extractBalances(request, response):

    balances = []
    try:
        searchedValue = "<ns:return>"

        count = 0

        endingIndexOfStartReturn = []
        for match in re.finditer(searchedValue, response):
            print(match.end())
            endingIndexOfStartReturn.append(match.end())
            count += 1

        searchedValue = "</ns:return>"

        startingIndexOfEndReturn = []
        for match in re.finditer(searchedValue, response):
            print(match.start())
            startingIndexOfEndReturn.append(match.start())


        for i in range(len(endingIndexOfStartReturn)):
            balances.append(response[endingIndexOfStartReturn[i]: startingIndexOfEndReturn[i]])
            print(response[endingIndexOfStartReturn[i]: startingIndexOfEndReturn[i]])

    except:
        messages.error(request, "an error occurred")
    return balances
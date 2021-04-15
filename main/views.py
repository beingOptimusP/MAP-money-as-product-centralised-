from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .models import Bank,Profile


# Create your views here.
def home(request):
    bank=get_object_or_404(Bank,pk=1)
    context={
        'bank':bank
    }
    return render(request, 'home.html',context)

def signupuser(request):

    # return render(request, 'signup.html', {'form':UserCreationForm()})
    if request.method == 'GET':
        return render(request,'signup.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user=User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('dash')
            except IntegrityError:
                return render(request,'signup.html',{'error':'username is already taken, try another','form':UserCreationForm()})
        else:
            return render(request,'signup.html',{'error':'passwords didnt match','form':UserCreationForm()})


def dashboard(request):
    bank=get_object_or_404(Bank,pk=1)
    user = User.objects.get(username=request.user.username)

    if user.profile.Holdings != 0:
        user.profile.interest = bank.inflation
        user.save()
    else:
        user.profile.interest = 0
        user.save()

    if request.method == 'POST':
        if request.POST['option'] == 'withdraw':
            num = float(request.POST['num'])
            bank.in_bank=bank.in_bank-num
            user.profile.wallet=user.profile.wallet+num
            diff = bank.total_supply - bank.in_bank
            bank.inflation = (diff/bank.total_supply)*100
            bank.save()
            user.save()
            return redirect('dash')
        else:
            num = float(request.POST['num'])
            if num > user.profile.wallet:
                return render(request, 'dashboard.html',{'user':user,'error':'u are depositing more than ur wallet has'})
            else:
                bank.in_bank=bank.in_bank+num
                user.profile.Holdings+=num
                user.profile.interest = bank.inflation
                user.profile.wallet=user.profile.wallet-num
                diff = bank.total_supply - bank.in_bank
                bank.inflation = (diff/bank.total_supply)*100
                bank.save()
                user.save()
                return redirect('dash')

    return render(request, 'dashboard.html',{'user':user})


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == 'GET':
        return render(request,'login.html',{'form':AuthenticationForm()})
    else:
        user=authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user == None:
            return render(request,'login.html',{'form':AuthenticationForm(),'error':'password and username didnt match'})
        else:
            login(request,user)
            return redirect('dash')
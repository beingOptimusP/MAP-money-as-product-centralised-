from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .models import Bank,Profile,Transaction
from .forms import TransactionForm
import threading

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


# Create your views here.
def home(request):
    bank=get_object_or_404(Bank,pk=1)
    bank.in_bank += (bank.inflation*bank.in_bank)/(100*525600*10)
    bank.total_supply = bank.in_bank + bank.inflation*bank.total_supply/100
    bank.inflation = (bank.total_supply - bank.in_bank)*100/bank.total_supply
    bank.save()
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


    users = User.objects.all()
    for i in users:
        if i.profile.Holdings > 0:
            i.profile.Holdings += (bank.inflation*user.profile.Holdings)/(100*525600*10)
            i.save()


    tran1 = Transaction.objects.filter(user=request.user)
    tran2 = Transaction.objects.filter(to=request.user)
    trans = tran1.union(tran2)

    if request.method == 'POST':
        
        if 'deposit' in request.POST:
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
                return render(request, 'dashboard.html',{'user':user,'msg':'successful transaction'})
        if 'withdraw' in request.POST:
            num = float(request.POST['num'])
            if num > user.profile.Holdings:
                return render(request, 'dashboard.html',{'user':user,'error':'u are withdrawing more than ur holdings'})
            else:
                user.profile.Holdings -= num
                user.profile.wallet +=num
                user.save()
                return render(request, 'dashboard.html',{'user':user,'msg':'successful transaction'})

        

    return render(request, 'dashboard.html',{'user':user,'tran':trans})


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



def transact(request):
    if request.method == 'GET':
        return render(request,'transact.html',{'form':TransactionForm()})
    else:
        form = TransactionForm(request.POST)
        tran = form.save(commit=False)
        tran.user = request.user
        

        user1 = User.objects.get(username=tran.user)
        

        user=User.objects.all()
        for i in user:
            if tran.to == i.username:
                break
        else:
            return render(request,'transact.html',{'form':TransactionForm(),'error':'username does not exist'})


        user2 = User.objects.get(username=tran.to)

        if user1.profile.wallet < tran.amount :
            return render(request,'transact.html',{'form':TransactionForm(),'error':'u cannot send more than the amount ur wallet has'})
        elif user1.profile.wallet == user2.profile.wallet:
            return render(request,'transact.html',{'form':TransactionForm(),'error':'u cannot send money to urself'})
        else:
            user1.profile.wallet -= tran.amount 
            user2.profile.wallet += tran.amount
            user1.save()
            user2.save()
            tran.save()
            return render(request,'transact.html',{'form':TransactionForm(),'msg':'transaction was successful'})

        

        

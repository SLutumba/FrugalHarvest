from django.shortcuts import render, redirect
from . models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django import forms
from payments.forms import ShippingForm
from payments.models import ShippingAddress
import json
from cart.cart import Cart

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        user_pw = request.POST['password']
        user = authenticate(request, username = username, password= user_pw)
        if user is not None:
            login(request, user)  
            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("Successful login"))
            return redirect('home')
        else:
            messages.success(request, ("Unsuccessful login, Please try again"))
            return redirect('login')
    else:
        return render(request, 'login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ("Successfully logged out. Have a wonderful day!"))
    return redirect('home')

def register(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Account created. Please fill out user info below"))
            return redirect('update_info')
        else:
            messages.success(request, ("Unsuccessful registration. Try again"))
            return redirect('register')
    else:        
        return render(request, 'register.html', {'form':form})
    
    
def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product})

def category(request, cat):
    cat = cat.replace('-', ' ')
    try:
        category = Category.objects.get(name=cat)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("That category does not exist"))
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()

    return render(request, 'category_summary.html', {'categories':categories})

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request,current_user)
            messages.success(request, 'Successful update')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, 'Must be logged in')
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'Password updated. Log in again')
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request,"You need to be logged in to view this")
        return redirect('home')
    
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shippng_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shippng_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, 'Successful update')
            return redirect('home')
        return render(request, 'update_info.html', {'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request, 'Must be logged in')
        return redirect('home')
    
def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        searched = Product.objects.filter(name__icontains=searched)
        if not searched:
            messages.success(request, "That product does not exist")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})

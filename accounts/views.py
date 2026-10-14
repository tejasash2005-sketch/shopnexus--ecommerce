from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, AddressForm
from .models import CustomUser, Address
from orders.models import Order

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to ShopNexus, {user.first_name}! Your account has been created.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_spent = Order.objects.filter(user=request.user, payment_status='paid').aggregate(
        total=Sum('total_amount'))['total'] or 0
    return render(request, 'accounts/profile.html', {
        'orders': orders,
        'total_spent': total_spent,
        'order_count': Order.objects.filter(user=request.user).count(),
    })

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                request.user.addresses.update(is_default=False)
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add Address'})

@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            addr = form.save(commit=False)
            if addr.is_default:
                request.user.addresses.exclude(pk=pk).update(is_default=False)
            addr.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})

@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted.')
    return redirect('address_list')

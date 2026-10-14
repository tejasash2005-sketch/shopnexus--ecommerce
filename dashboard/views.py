from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, Avg
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser, Address
from store.models import Product, Category, Brand, Cart, Coupon, ProductImage
from orders.models import Order, OrderItem, Return
from payments.models import Payment
from reviews.models import Review
from wishlist.models import Wishlist
from analytics.models import SalesReport, SiteVisit, NewsletterSubscriber, LowStockAlert, AdminActivityLog
from .forms import ProductForm

@staff_member_required
def admin_dashboard(request):
    context = {
        'total_users': CustomUser.objects.count(),
        'total_revenue': Payment.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock_count': LowStockAlert.objects.filter(status='open').count(),
        'recent_activities': AdminActivityLog.objects.order_by('-created_at')[:10],
        'total_products': Product.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'new_users_today': CustomUser.objects.filter(date_joined__date=timezone.now().date()).count(),
        'total_orders': Order.objects.count(),
        'total_returns': Return.objects.count(),
        'subscribers': NewsletterSubscriber.objects.filter(status='active').count(),
        'avg_rating': round(Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0, 1),
    }
    return render(request, 'dashboard/overview.html', context)

# --- Accounts ---
@staff_member_required
def db_accounts(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    addresses = Address.objects.all().order_by('-created_at')[:20]
    return render(request, 'dashboard/accounts.html', {'users': users, 'addresses': addresses})

@staff_member_required
def toggle_user_status(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect('db_accounts')

@staff_member_required
def toggle_newsletter(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.newsletter_subscribed = not user.newsletter_subscribed
    user.save()
    messages.success(request, f"Newsletter subscription toggled for {user.username}.")
    return redirect('db_accounts')

# --- Store ---
@staff_member_required
def db_store(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    coupons = Coupon.objects.all()
    abandoned_carts = Cart.objects.annotate(item_count=Count('items')).filter(item_count__gt=0).order_by('-updated_at')
    return render(request, 'dashboard/store.html', {
        'products': products, 'categories': categories, 'brands': brands,
        'coupons': coupons, 'abandoned_carts': abandoned_carts
    })

@staff_member_required
def toggle_product_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    messages.success(request, f"Product {product.name} status updated.")
    return redirect('db_store')

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if request.FILES.get('image'):
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES.get('image'),
                    is_primary=True
                )
            messages.success(request, f"Product {product.name} added successfully!")
            return redirect('db_store')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add New Product'})

@staff_member_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            if request.FILES.get('image'):
                # Update or create primary image
                img = product.images.filter(is_primary=True).first()
                if img:
                    img.image = request.FILES.get('image')
                    img.save()
                else:
                    ProductImage.objects.create(
                        product=product,
                        image=request.FILES.get('image'),
                        is_primary=True
                    )
            messages.success(request, f"Product {product.name} updated successfully!")
            return redirect('db_store')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})

# --- Orders ---
@staff_member_required
def db_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders, 'status_choices': Order.STATUS_CHOICES})

@staff_member_required
def update_order_status(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        order.status = request.POST.get('status')
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated.")
    return redirect('db_orders')

@staff_member_required
def db_returns(request):
    returns = Return.objects.all().order_by('-created_at')
    return render(request, 'dashboard/returns.html', {'returns': returns})

@staff_member_required
def approve_return(request, pk):
    ret = get_object_or_404(Return, pk=pk)
    ret.status = 'approved'
    ret.save()
    messages.success(request, f"Return for order {ret.order.order_number} approved.")
    return redirect('db_returns')

# --- Payments ---
@staff_member_required
def db_payments(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'dashboard/payments.html', {'payments': payments})

# --- Reviews ---
@staff_member_required
def db_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'dashboard/reviews.html', {'reviews': reviews})

@staff_member_required
def approve_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, "Review approved.")
    return redirect('db_reviews')

@staff_member_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('db_reviews')

# --- Wishlist ---
@staff_member_required
def db_wishlist(request):
    wishlists = Wishlist.objects.annotate(product_count=Count('products')).all()
    return render(request, 'dashboard/wishlist.html', {'wishlists': wishlists})

# --- Analytics ---
@staff_member_required
def db_analytics(request):
    reports = SalesReport.objects.all().order_by('-date')
    visits = SiteVisit.objects.all().order_by('-created_at')[:100]
    subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    alerts = LowStockAlert.objects.filter(status='open')
    logs = AdminActivityLog.objects.all().order_by('-created_at')[:100]
    return render(request, 'dashboard/analytics.html', {
        'reports': reports, 'visits': visits, 'subscribers': subscribers,
        'alerts': alerts, 'logs': logs
    })

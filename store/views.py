from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Cart, CartItem, Coupon
from django.utils import timezone

def home_view(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True, parent=None)[:6]
    return render(request, 'store/home.html', {
        'featured_products': featured,
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'categories': categories,
    })

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True, parent=None)
    brands = Brand.objects.filter(is_active=True)

    # Filters
    category_slug = request.GET.get('category')
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    search = request.GET.get('q')

    if category_slug:
        cat = get_object_or_404(Category, slug=category_slug)
        products = products.filter(Q(category=cat) | Q(category__parent=cat))
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search) |
            Q(category__name__icontains=search) | Q(tags__icontains=search)
        )

    sort_options = {
        'price_asc': 'price', 'price_desc': '-price',
        'name': 'name', '-created_at': '-created_at',
    }

    if sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/product_list.html', {
        'products': page,
        'categories': categories,
        'brands': brands,
        'selected_category': category_slug,
        'selected_brand': brand_id,
        'search_query': search,
        'sort': sort,
        # FIX: was using wrong condition - paginator.count is always correct total
        'total_count': paginator.count,
    })

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    user_review = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        try:
            in_wishlist = request.user.wishlist.products.filter(pk=product.pk).exists()
        except:
            pass

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
        'reviews': reviews,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
    })


def get_or_create_cart(request):
    """
    FIX: Properly handles cart retrieval for both authenticated and anonymous users.
    For authenticated users, merges any existing session cart into the user cart.
    """
    if request.user.is_authenticated:
        user_cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'session_key': None})

        # Merge session cart into user cart if one exists
        session_key = request.session.session_key
        if session_key:
            try:
                session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                if session_cart.pk != user_cart.pk:
                    for session_item in session_cart.items.all():
                        existing = user_cart.items.filter(product=session_item.product).first()
                        if existing:
                            new_qty = existing.quantity + session_item.quantity
                            existing.quantity = min(new_qty, session_item.product.stock)
                            existing.save()
                        else:
                            session_item.cart = user_cart
                            session_item.save()
                    # Carry over coupon if user cart has none
                    if not user_cart.coupon and session_cart.coupon:
                        user_cart.coupon = session_cart.coupon
                        user_cart.save()
                    session_cart.delete()
            except Cart.DoesNotExist:
                pass

        return user_cart
    else:
        # Ensure a session key exists before using it
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    remaining = max(0, 500 - int(cart.subtotal))
    return render(request, 'store/cart.html', {'cart': cart, 'free_shipping_remaining': remaining})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    if product.stock < quantity:
        messages.error(request, f'Only {product.stock} units available.')
        return redirect('product_detail', slug=product.slug)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        new_qty = item.quantity + quantity
        if new_qty > product.stock:
            messages.warning(request, f'Only {product.stock} units available.')
            item.quantity = product.stock
        else:
            item.quantity = new_qty
    else:
        item.quantity = quantity
    item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items, 'message': f'{product.name} added to cart!'})
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart')


def remove_from_cart(request, item_id):
    # FIX: Validate cart ownership before deleting
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    # FIX: Validate cart ownership before updating
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            item.delete()
        elif qty > item.product.stock:
            # FIX: clamp to stock and save properly
            item.quantity = item.product.stock
            item.save()
            messages.warning(request, f'Quantity adjusted to available stock ({item.product.stock}).')
        else:
            item.quantity = qty
            item.save()
    return redirect('cart')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        cart = get_or_create_cart(request)
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                if cart.subtotal >= coupon.min_order_amount:
                    cart.coupon = coupon
                    cart.save()
                    messages.success(request, f'Coupon "{code}" applied! You save ₹{cart.discount_amount:.2f}')
                else:
                    messages.error(request, f'Minimum order amount is ₹{coupon.min_order_amount}')
            else:
                messages.error(request, 'Coupon is expired or invalid.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    return redirect('cart')


def remove_coupon(request):
    cart = get_or_create_cart(request)
    cart.coupon = None
    cart.save()
    messages.info(request, 'Coupon removed.')
    return redirect('cart')


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'store/category.html', {'category': category, 'products': page})


def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(category__name__icontains=query) | Q(brand__name__icontains=query) |
            Q(tags__icontains=query)
        )
    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'store/search.html', {'products': page, 'query': query})


def about_view(request):
    return render(request, 'store/about.html')


def contact_view(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you! We will get back to you soon.')
    return render(request, 'store/contact.html')

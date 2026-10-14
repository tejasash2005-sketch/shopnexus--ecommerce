from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .models import Wishlist

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        action = 'removed'
        msg = f'"{product.name}" removed from wishlist.'
    else:
        wishlist.products.add(product)
        action = 'added'
        msg = f'"{product.name}" added to wishlist!'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action, 'count': wishlist.item_count})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

@login_required
def clear_wishlist(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.clear()
    messages.info(request, 'Wishlist cleared.')
    return redirect('wishlist')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from store.models import Cart, CartItem
from accounts.models import Address
from .models import Order, OrderItem, OrderStatusHistory, Return
from decimal import Decimal

@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    addresses = request.user.addresses.all()
    default_address = addresses.filter(is_default=True).first() or addresses.first()

    if request.method == 'POST':
        # Get or create address
        address_id = request.POST.get('address_id')
        if address_id:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
        else:
            from accounts.forms import AddressForm
            addr_form = AddressForm(request.POST)
            if addr_form.is_valid():
                address = addr_form.save(commit=False)
                address.user = request.user
                address.save()
            else:
                messages.error(request, 'Please provide a valid shipping address.')
                return render(request, 'orders/checkout.html', {
                    'cart': cart,
                    'addresses': addresses,
                    'default_address': default_address,
                    'address_form': addr_form,
                })

        payment_method = request.POST.get('payment_method', 'cod')
        shipping_cost = Decimal('0') if cart.subtotal >= 500 else Decimal('50')
        tax_rate = Decimal('0.18')
        tax_amount = (cart.subtotal - cart.discount_amount) * tax_rate
        total = cart.subtotal - cart.discount_amount + shipping_cost + tax_amount

        order = Order.objects.create(
            user=request.user,
            payment_method=payment_method,
            full_name=address.full_name,
            email=request.user.email,
            phone=address.phone,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
            country=address.country,
            subtotal=cart.subtotal,
            discount_amount=cart.discount_amount,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total,
            coupon=cart.coupon,
            coupon_code=cart.coupon.code if cart.coupon else '',
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                unit_price=item.product.effective_price,
                total_price=item.subtotal,
            )
            # Decrease stock
            item.product.stock -= item.quantity
            item.product.save()

        OrderStatusHistory.objects.create(
            order=order, status='pending',
            note='Order placed successfully.', created_by=request.user
        )

        if cart.coupon:
            cart.coupon.used_count += 1
            cart.coupon.save()

        if payment_method == 'cod':
            order.payment_status = 'cod'
            order.status = 'confirmed'
            order.save()
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('order_success', pk=order.pk)

        elif payment_method == 'stripe':
            request.session['pending_order_id'] = order.pk
            return redirect('stripe_payment', pk=order.pk)

        # FIX: UPI and Net Banking were silently swallowed — now they go to simulate_payment
        elif payment_method in ('upi', 'netbanking'):
            request.session['pending_order_id'] = order.pk
            return redirect('simulate_payment', pk=order.pk)

        else:
            # Fallback for any unknown payment method
            order.payment_status = 'cod'
            order.status = 'confirmed'
            order.save()
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('order_success', pk=order.pk)

    from accounts.forms import AddressForm
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'default_address': default_address,
        'address_form': AddressForm(),
        'shipping_free_threshold': 500,
    })


@login_required
def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list_view(request):
    from django.core.paginator import Paginator
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'orders/order_list.html', {'orders': page})


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def cancel_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        OrderStatusHistory.objects.create(
            order=order, status='cancelled',
            note='Cancelled by customer.', created_by=request.user
        )
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    return redirect('order_detail', pk=pk)


@login_required
def return_request_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status != 'delivered':
        messages.error(request, 'Only delivered orders can be returned.')
        return redirect('order_detail', pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        Return.objects.create(order=order, user=request.user, reason=reason, description=description)
        messages.success(request, 'Return request submitted successfully!')
        return redirect('order_detail', pk=pk)
    return render(request, 'orders/return_request.html', {'order': order})

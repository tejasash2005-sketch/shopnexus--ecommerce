from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import Payment
import json

@login_required
def stripe_payment_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'amount_paise': int(order.total_amount * 100),
    }
    return render(request, 'payments/stripe_payment.html', context)


@login_required
def stripe_process_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        token = request.POST.get('stripeToken', '')
        import random, string
        txn_id = 'txn_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        Payment.objects.create(
            order=order, user=request.user,
            gateway='stripe', transaction_id=txn_id,
            amount=order.total_amount, currency='INR',
            status='success',
            gateway_response={'token': token, 'txn': txn_id}
        )
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.stripe_payment_intent = txn_id
        order.save()

        # Clear cart
        try:
            cart = request.user.cart
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
        except:
            pass

        messages.success(request, f'Payment successful! Order #{order.order_number} confirmed.')
        return redirect('order_success', pk=order.pk)
    return redirect('stripe_payment', pk=pk)


@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})


@login_required
def simulate_payment_view(request, pk):
    """Simulated payment for demo/testing (UPI, Net Banking, Stripe fallback)"""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action', 'success')
        import random, string
        txn_id = 'SIM_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

        if action == 'success':
            Payment.objects.create(
                order=order, user=request.user,
                gateway='stripe', transaction_id=txn_id,
                amount=order.total_amount, currency='INR',
                status='success',
            )
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            try:
                cart = request.user.cart
                cart.items.all().delete()
                cart.coupon = None
                cart.save()
            except:
                pass
            messages.success(request, f'✅ Payment Successful! Order #{order.order_number}')
            return redirect('order_success', pk=order.pk)
        else:
            Payment.objects.create(
                order=order, user=request.user,
                gateway='stripe', transaction_id=txn_id,
                amount=order.total_amount, currency='INR',
                status='failed', failure_reason='Payment declined by user.'
            )
            order.payment_status = 'failed'
            order.save()
            messages.error(request, 'Payment failed. Please try again.')
            # FIX: was redirecting to 'checkout' without pk — now goes back to cart
            return redirect('cart')

    return render(request, 'payments/simulate_payment.html', {'order': order})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .models import Review, ReviewHelpful
from orders.models import Order, OrderItem

@login_required
def add_review_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()

        if not title or not body:
            messages.error(request, 'Please fill all fields.')
            return redirect('product_detail', slug=product.slug)

        # Check verified purchase
        is_verified = OrderItem.objects.filter(
            order__user=request.user, product=product, order__payment_status='paid'
        ).exists()

        review, created = Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'title': title, 'body': body,
                      'is_verified_purchase': is_verified, 'is_approved': False}
        )
        if created:
            messages.success(request, 'Review submitted! It will appear after approval.')
        else:
            messages.success(request, 'Review updated! It will appear after re-approval.')

    return redirect('product_detail', slug=product.slug)


@login_required
def delete_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('product_detail', slug=product_slug)


@login_required
def mark_helpful_view(request, pk):
    review = get_object_or_404(Review, pk=pk)
    helpful, created = ReviewHelpful.objects.get_or_create(review=review, user=request.user)
    if not created:
        helpful.delete()
        review.helpful_count = max(0, review.helpful_count - 1)
        review.save()
        return JsonResponse({'action': 'removed', 'count': review.helpful_count})
    review.helpful_count += 1
    review.save()
    return JsonResponse({'action': 'added', 'count': review.helpful_count})


# FIX: was missing @login_required — unauthenticated users would get an error
@login_required
def my_reviews_view(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})

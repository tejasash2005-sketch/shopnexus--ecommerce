from django.db import models
from accounts.models import CustomUser, Address
from store.models import Product, Coupon
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cod', 'Cash on Delivery'),
    ]
    PAYMENT_METHODS = [
        ('stripe', 'Credit/Debit Card (Stripe)'),
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')

    # Shipping address (snapshot)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)

    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'ORD' + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'


class Return(models.Model):
    RETURN_REASONS = [
        ('defective', 'Defective/Damaged'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=RETURN_REASONS)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return for {self.order.order_number}"

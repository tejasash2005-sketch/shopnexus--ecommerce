from django.db import models
from accounts.models import CustomUser
from orders.models import Order

class Payment(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    transaction_id = models.CharField(max_length=200, blank=True)
    gateway_order_id = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    gateway_response = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_id = models.CharField(max_length=200, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.order.order_number}"

    class Meta:
        ordering = ['-created_at']

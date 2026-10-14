from django.db import models
from accounts.models import CustomUser
from store.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, blank=True, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    @property
    def item_count(self):
        return self.products.count()

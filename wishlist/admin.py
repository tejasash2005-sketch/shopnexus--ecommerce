from django.contrib import admin
from django.utils.html import format_html
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'item_count_badge', 'top_products', 'created_at']
    search_fields = ['user__username', 'user__email', 'products__name']
    readonly_fields = ['user', 'created_at']
    filter_horizontal = ['products']
    ordering = ['-created_at']

    fieldsets = (
        ('👤 Customer', {'fields': ('user',)}),
        ('💛 Wishlisted Products', {'fields': ('products',)}),
        ('🕓 Created', {'fields': ('created_at',)}),
    )

    def user_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}" style="font-weight:600">👤 {}</a>', url, obj.user.username)
    user_link.short_description = 'Customer'

    def item_count_badge(self, obj):
        count = obj.products.count()
        color = '#10b981' if count > 0 else '#9ca3af'
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-weight:600">'
            '💛 {}</span>', color, count
        )
    item_count_badge.short_description = 'Items'

    def top_products(self, obj):
        names = [p.name for p in obj.products.all()[:3]]
        if not names:
            return '—'
        text = ', '.join(names)
        if obj.products.count() > 3:
            text += f' +{obj.products.count() - 3} more'
        return text
    top_products.short_description = 'Products (preview)'

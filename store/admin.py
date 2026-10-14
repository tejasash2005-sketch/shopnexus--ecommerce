from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Avg
from .models import Category, Brand, Product, ProductImage, Cart, CartItem, Coupon


# ── Category ──────────────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'product_count_badge', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    def product_count_badge(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html(
            '<span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:10px;font-weight:600">{}</span>',
            count
        )
    product_count_badge.short_description = 'Live Products'


# ── Brand ─────────────────────────────────────────────────────────────────────
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'


# ── Product Images inline ─────────────────────────────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ['image', 'alt_text', 'is_primary', 'order', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px"/>', obj.image.url)
        return '—'
    preview.short_description = 'Preview'


# ── Product ───────────────────────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_image', 'name', 'category', 'brand',
        'price', 'price_display', 'stock', 'stock_badge', 'sales_count',
        'rating_display', 'is_active', 'is_featured', 'created_at',
    ]
    list_filter = ['is_active', 'is_featured', 'is_bestseller', 'category', 'brand', 'created_at']
    search_fields = ['name', 'sku', 'description', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    inlines = [ProductImageInline]
    readonly_fields = ['sku', 'created_at', 'updated_at', 'sales_count', 'rating_display']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('📝 Basic Info', {'fields': ('category', 'brand', 'name', 'slug', 'sku', 'short_description', 'description', 'tags')}),
        ('💰 Pricing & Stock', {'fields': ('price', 'discount_price', 'stock', 'weight', 'dimensions')}),
        ('⭐ Stats', {'fields': ('sales_count', 'rating_display')}),
        ('🏷 Status', {'fields': ('is_active', 'is_featured', 'is_bestseller')}),
        ('🕓 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['activate_products', 'deactivate_products', 'mark_featured', 'mark_bestseller']

    def product_image(self, obj):
        img = obj.primary_image
        if img:
            return format_html('<img src="{}" width="48" height="48" style="border-radius:6px;object-fit:cover;border:1px solid #e5e7eb"/>', img.image.url)
        return format_html('<div style="width:48px;height:48px;background:#f3f4f6;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:20px">📦</div>')
    product_image.short_description = ''

    def price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<strong style="color:#059669">₹{}</strong><br>'
                '<small style="text-decoration:line-through;color:#9ca3af">₹{}</small>'
                '<small style="color:#ef4444"> -{}%</small>',
                format(obj.discount_price, ',.0f'),
                format(obj.price, ',.0f'),
                obj.discount_percent
            )
        return format_html('<strong>₹{}</strong>', format(obj.price, ',.0f'))
    price_display.short_description = 'Price'

    def stock_badge(self, obj):
        if obj.stock == 0:
            return format_html('<span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">Out of Stock</span>')
        elif obj.stock < 10:
            return format_html('<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">⚠️ Low: {}</span>', obj.stock)
        return format_html('<span style="background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">{}</span>', obj.stock)
    stock_badge.short_description = 'Stock'

    def sales_count(self, obj):
        from orders.models import OrderItem
        total = OrderItem.objects.filter(product=obj).aggregate(s=Sum('quantity'))['s'] or 0
        return format_html('<span style="font-weight:600;color:#6366f1">{} sold</span>', total)
    sales_count.short_description = 'Sales'

    def rating_display(self, obj):
        r = obj.average_rating
        stars = '★' * int(r) + '☆' * (5 - int(r))
        color = '#10b981' if r >= 4 else '#f59e0b' if r >= 3 else '#ef4444' if r > 0 else '#9ca3af'
        return format_html('<span style="color:{}">{}</span> <small>({})</small>', color, stars, obj.review_count)
    rating_display.short_description = 'Rating'

    @admin.action(description='✅ Activate selected products')
    def activate_products(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f'{n} products activated.')

    @admin.action(description='🚫 Deactivate selected products')
    def deactivate_products(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, f'{n} products deactivated.')

    @admin.action(description='⭐ Mark as Featured')
    def mark_featured(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(request, f'{n} products marked as featured.')

    @admin.action(description='🏆 Mark as Bestseller')
    def mark_bestseller(self, request, queryset):
        n = queryset.update(is_bestseller=True)
        self.message_user(request, f'{n} products marked as bestseller.')


# ── Coupon ────────────────────────────────────────────────────────────────────
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code_badge', 'discount_display', 'min_order_amount',
        'usage_bar', 'valid_from', 'valid_to',
        'validity_badge', 'is_active',
    ]
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'created_at']

    def code_badge(self, obj):
        return format_html(
            '<code style="background:#f0f9ff;color:#0369a1;padding:4px 10px;'
            'border-radius:6px;font-size:13px;font-weight:700">{}</code>',
            obj.code
        )
    code_badge.short_description = 'Code'

    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html('<strong style="color:#7c3aed">{}% OFF</strong>', int(obj.discount_value))
        return format_html('<strong style="color:#059669">₹{} OFF</strong>', format(obj.discount_value, ',.0f'))
    discount_display.short_description = 'Discount'

    def usage_bar(self, obj):
        pct = min(int((obj.used_count / max(obj.max_uses, 1)) * 100), 100)
        color = '#ef4444' if pct >= 90 else '#f59e0b' if pct >= 60 else '#10b981'
        return format_html(
            '<div style="width:100px;background:#e5e7eb;border-radius:4px;height:10px;margin-bottom:2px">'
            '<div style="width:{pct}%;background:{color};height:10px;border-radius:4px"></div></div>'
            '<small>{used}/{max} uses</small>',
            pct=pct, color=color, used=obj.used_count, max=obj.max_uses
        )
    usage_bar.short_description = 'Usage'

    def validity_badge(self, obj):
        if obj.is_valid():
            return format_html('<span style="color:#10b981;font-weight:600">✅ Valid</span>')
        return format_html('<span style="color:#ef4444;font-weight:600">❌ Expired/Invalid</span>')
    validity_badge.short_description = 'Validity'


# ── Cart (Abandoned Cart Tracking) ────────────────────────────────────────────
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'subtotal_display', 'added_at']

    def subtotal_display(self, obj):
        return format_html('<strong>₹{}</strong>', format(obj.subtotal, ',.2f'))
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'cart_owner', 'total_items_badge', 'subtotal_display',
        'coupon', 'cart_type', 'created_at',
    ]
    list_filter = ['created_at', 'coupon']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['user', 'session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    ordering = ['-created_at']

    def cart_owner(self, obj):
        if obj.user:
            url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
            return format_html('<a href="{}">👤 {}</a>', url, obj.user.username)
        return format_html('<span style="color:#9ca3af">🔑 Guest ({})</span>', (obj.session_key or '')[:16])
    cart_owner.short_description = 'Owner'

    def total_items_badge(self, obj):
        return format_html('<span style="font-weight:700">{} items</span>', obj.total_items)
    total_items_badge.short_description = 'Items'

    def subtotal_display(self, obj):
        return format_html('<strong style="color:#059669">₹{}</strong>', format(obj.subtotal, ',.2f'))
    subtotal_display.short_description = 'Value'

    def cart_type(self, obj):
        if obj.user:
            return format_html('<span style="color:#3b82f6">Logged In</span>')
        return format_html('<span style="color:#9ca3af">Guest</span>')
    cart_type.short_description = 'Type'

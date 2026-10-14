from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewHelpful


class ReviewHelpfulInline(admin.TabularInline):
    model = ReviewHelpful
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product_link', 'user_link', 'star_rating',
        'title', 'is_approved', 'approval_badge', 'verified_badge',
        'helpful_count', 'created_at',
    ]
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'body']
    list_editable = ['is_approved']
    readonly_fields = ['product', 'user', 'helpful_count', 'created_at', 'updated_at']
    inlines = [ReviewHelpfulInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('📦 Product & User', {'fields': ('product', 'user')}),
        ('⭐ Review Content', {'fields': ('rating', 'title', 'body')}),
        ('✅ Moderation', {'fields': ('is_approved', 'is_verified_purchase', 'helpful_count')}),
        ('🕓 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['approve_reviews', 'reject_reviews']

    def product_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:store_product_change', args=[obj.product.pk])
        return format_html('<a href="{}" style="font-weight:600">{}</a>', url, obj.product.name[:40])
    product_link.short_description = 'Product'

    def user_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Customer'

    def star_rating(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        colors = {1: '#ef4444', 2: '#f97316', 3: '#f59e0b', 4: '#84cc16', 5: '#10b981'}
        return format_html(
            '<span style="color:{};font-size:16px" title="{}/5">{}</span>',
            colors.get(obj.rating, '#9ca3af'), obj.rating, stars
        )
    star_rating.short_description = 'Rating'

    def approval_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background:#d1fae5;color:#065f46;padding:2px 8px;'
                'border-radius:10px;font-size:11px;font-weight:600">✅ Approved</span>'
            )
        return format_html(
            '<span style="background:#fee2e2;color:#991b1b;padding:2px 8px;'
            'border-radius:10px;font-size:11px;font-weight:600">⏳ Pending</span>'
        )
    approval_badge.short_description = 'Status'

    def verified_badge(self, obj):
        if obj.is_verified_purchase:
            return format_html('<span style="color:#3b82f6;font-weight:600">🛒 Verified</span>')
        return format_html('<span style="color:#9ca3af">—</span>')
    verified_badge.short_description = 'Purchase'

    @admin.action(description='✅ Approve selected reviews')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"✅ {updated} reviews approved.")

    @admin.action(description='❌ Reject selected reviews')
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"❌ {updated} reviews rejected.")

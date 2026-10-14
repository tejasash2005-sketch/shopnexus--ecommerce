from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from .models import CustomUser, Address


# ── Address inline shown inside each User record ──────────────────────────────
class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    readonly_fields = ['created_at']
    fields = [
        'address_type', 'full_name', 'phone',
        'address_line1', 'address_line2',
        'city', 'state', 'zip_code', 'country',
        'is_default', 'created_at',
    ]


# ── Customer 360° view ─────────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'avatar_name', 'email', 'phone',
        'total_orders_badge', 'total_spent_badge',
        'city', 'country',
        'account_status', 'newsletter_badge',
        'date_joined',
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'newsletter_subscribed', 'is_email_verified',
        'country', 'date_joined',
    ]
    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'phone', 'city', 'state',
    ]
    inlines = [AddressInline]
    ordering = ['-date_joined']
    date_hierarchy = 'date_joined'
    readonly_fields = [
        'date_joined', 'last_login', 'created_at', 'updated_at',
        'total_orders_badge', 'total_spent_badge',
        'last_order_link', 'shopping_summary',
    ]

    fieldsets = (
        ('👤 Personal Information', {
            'fields': (
                'username', 'first_name', 'last_name',
                'email', 'phone', 'date_of_birth', 'profile_picture',
            )
        }),
        ('🏠 Default Address', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country'),
        }),
        ('🛒 Shopping Summary', {
            'fields': ('shopping_summary', 'total_orders_badge', 'total_spent_badge', 'last_order_link'),
        }),
        ('🔐 Account & Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_email_verified', 'newsletter_subscribed',
                'groups', 'user_permissions',
            ),
        }),
        ('🕓 Activity', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('email', 'phone', 'first_name', 'last_name')}),
    )

    # ── computed display columns ──────────────────────────────────────────────

    def avatar_name(self, obj):
        initials = (
            (obj.first_name[:1] if obj.first_name else '') +
            (obj.last_name[:1] if obj.last_name else '')
        ) or obj.username[:2].upper()
        colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6']
        color = colors[obj.pk % len(colors)]
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px">'
            '<div style="width:34px;height:34px;border-radius:50%;background:{};'
            'color:white;display:flex;align-items:center;justify-content:center;'
            'font-weight:700;font-size:13px;flex-shrink:0">{}</div>'
            '<div><strong>{}</strong><br>'
            '<small style="color:#6b7280">{}</small></div></div>',
            color, initials,
            obj.get_full_name() or obj.username,
            obj.username,
        )
    avatar_name.short_description = 'Customer'

    def total_orders_badge(self, obj):
        count = obj.orders.count()
        color = '#10b981' if count > 5 else '#3b82f6' if count > 0 else '#9ca3af'
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-weight:700">{} orders</span>',
            color, count,
        )
    total_orders_badge.short_description = '# Orders'

    def total_spent_badge(self, obj):
        total = obj.orders.filter(
            payment_status='paid'
        ).aggregate(s=Sum('total_amount'))['s'] or 0
        color = '#10b981' if total > 5000 else '#6366f1' if total > 0 else '#9ca3af'
        return format_html(
            '<strong style="color:{};font-size:13px">₹{}</strong>', color, format(total, ',.0f')
        )
    total_spent_badge.short_description = 'Total Spent'

    def last_order_link(self, obj):
        order = obj.orders.order_by('-created_at').first()
        if order:
            url = reverse('admin:orders_order_change', args=[order.pk])
            return format_html(
                '<a href="{}" style="font-weight:600">#{}</a> &nbsp;'
                '<span style="color:#6b7280">{}</span>',
                url, order.order_number, order.created_at.strftime('%d %b %Y'),
            )
        return '—'
    last_order_link.short_description = 'Last Order'

    def shopping_summary(self, obj):
        orders = obj.orders.all()
        paid = orders.filter(payment_status='paid')
        delivered = orders.filter(status='delivered')
        cancelled = orders.filter(status='cancelled')
        pending = orders.filter(status__in=['pending', 'confirmed', 'processing', 'shipped'])
        avg_val = paid.aggregate(a=Avg('total_amount'))['a'] or 0
        rows = [
            ('📦 Total Orders', orders.count()),
            ('✅ Delivered', delivered.count()),
            ('🚚 In Progress', pending.count()),
            ('❌ Cancelled', cancelled.count()),
            ('💰 Avg Order Value', f'₹{avg_val:,.0f}'),
            ('📍 Saved Addresses', obj.addresses.count()),
            ('💛 Wishlist Items', obj.wishlist.products.count() if hasattr(obj, 'wishlist') else 0),
        ]
        html = '<table style="border-collapse:collapse;width:100%;max-width:400px">'
        for label, val in rows:
            html += (
                f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280;font-size:13px">{label}</td>'
                f'<td style="padding:4px 0;font-weight:600;font-size:13px">{val}</td></tr>'
            )
        html += '</table>'
        return format_html(html)
    shopping_summary.short_description = 'Shopping Overview'

    def account_status(self, obj):
        if not obj.is_active:
            return format_html('<span style="color:#ef4444;font-weight:600">🚫 Banned</span>')
        if obj.is_superuser:
            return format_html('<span style="color:#8b5cf6;font-weight:600">👑 Superuser</span>')
        if obj.is_staff:
            return format_html('<span style="color:#3b82f6;font-weight:600">🛠 Staff</span>')
        return format_html('<span style="color:#10b981;font-weight:600">✅ Active</span>')
    account_status.short_description = 'Status'

    def newsletter_badge(self, obj):
        if obj.newsletter_subscribed:
            return format_html('<span style="color:#10b981">📧 Yes</span>')
        return format_html('<span style="color:#9ca3af">—</span>')
    newsletter_badge.short_description = 'Newsletter'

    # ── bulk actions ──────────────────────────────────────────────────────────
    actions = ['activate_users', 'deactivate_users', 'subscribe_newsletter']

    @admin.action(description='✅ Activate selected users')
    def activate_users(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f'{n} users activated.')

    @admin.action(description='🚫 Deactivate selected users')
    def deactivate_users(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, f'{n} users deactivated.')

    @admin.action(description='📧 Subscribe to newsletter')
    def subscribe_newsletter(self, request, queryset):
        n = queryset.update(newsletter_subscribed=True)
        self.message_user(request, f'{n} users subscribed to newsletter.')


# ── Standalone Address registry ────────────────────────────────────────────────
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'address_type_badge', 'full_name', 'phone',
        'full_address_display', 'is_default',
    ]
    list_filter = ['address_type', 'country', 'state', 'is_default']
    search_fields = [
        'user__username', 'user__email', 'full_name',
        'phone', 'city', 'state', 'zip_code',
    ]
    readonly_fields = ['user', 'created_at']
    ordering = ['-is_default', '-created_at']

    fieldsets = (
        ('👤 Customer', {'fields': ('user',)}),
        ('🏠 Address Details', {
            'fields': (
                'address_type', 'full_name', 'phone',
                'address_line1', 'address_line2',
                'city', 'state', 'zip_code', 'country',
                'is_default',
            )
        }),
        ('🕓 Saved On', {'fields': ('created_at',)}),
    )

    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}" style="font-weight:600">👤 {}</a>', url, obj.user.username)
    user_link.short_description = 'Customer'

    def address_type_badge(self, obj):
        icons = {'home': '🏠', 'work': '🏢', 'other': '📍'}
        return format_html('{} {}', icons.get(obj.address_type, '📍'), obj.get_address_type_display())
    address_type_badge.short_description = 'Type'

    def full_address_display(self, obj):
        parts = filter(None, [obj.address_line1, obj.address_line2, obj.city, obj.state, obj.zip_code, obj.country])
        return ', '.join(parts)
    full_address_display.short_description = 'Full Address'

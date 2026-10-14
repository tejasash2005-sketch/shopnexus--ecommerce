from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SiteVisit, SalesReport, AdminActivityLog,
    NewsletterSubscriber, LowStockAlert,
)


# ─────────────────────────────────────────────
# 1.  SALES REPORTS
# ─────────────────────────────────────────────
@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_orders_badge', 'revenue_display',
        'total_items_sold', 'new_customers',
        'avg_order_display', 'cancelled_orders', 'refunded_display',
    ]
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = [
        'date', 'total_orders', 'total_revenue', 'total_items_sold',
        'new_customers', 'cancelled_orders', 'refunded_amount',
        'average_order_value', 'created_at', 'updated_at',
    ]
    ordering = ['-date']
    date_hierarchy = 'date'

    fieldsets = (
        ('📅 Report Date', {
            'fields': ('date',)
        }),
        ('📦 Order Metrics', {
            'fields': ('total_orders', 'cancelled_orders', 'total_items_sold'),
        }),
        ('💰 Revenue Metrics', {
            'fields': ('total_revenue', 'average_order_value', 'refunded_amount'),
        }),
        ('👥 Customer Metrics', {
            'fields': ('new_customers',),
        }),
        ('🕓 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def total_orders_badge(self, obj):
        return format_html(
            '<span style="background:#3b82f6;color:white;padding:3px 10px;'
            'border-radius:12px;font-weight:600">{}</span>',
            obj.total_orders
        )
    total_orders_badge.short_description = 'Orders'

    def revenue_display(self, obj):
        return format_html(
            '<strong style="color:#10b981;font-size:14px">₹{}</strong>',
            format(obj.total_revenue, ',.2f')
        )
    revenue_display.short_description = 'Revenue'

    def avg_order_display(self, obj):
        return format_html('<span style="color:#6366f1">₹{}</span>', format(obj.average_order_value, ',.2f'))
    avg_order_display.short_description = 'Avg Order'

    def refunded_display(self, obj):
        color = '#ef4444' if obj.refunded_amount > 0 else '#9ca3af'
        return format_html('<span style="color:{}">₹{}</span>', color, format(obj.refunded_amount, ',.2f'))
    refunded_display.short_description = 'Refunded'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        totals = qs.aggregate(
            total_rev=Sum('total_revenue'),
            total_ord=Sum('total_orders'),
            total_cust=Sum('new_customers'),
        )
        extra_context['summary_stats'] = totals
        return super().changelist_view(request, extra_context=extra_context)


# ─────────────────────────────────────────────
# 2.  SITE VISITS / TRAFFIC ANALYTICS
# ─────────────────────────────────────────────
@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = [
        'path_display', 'user_display', 'ip_address',
        'referrer_short', 'created_at',
    ]
    list_filter = ['created_at']
    search_fields = ['path', 'ip_address', 'user__username', 'referrer']
    readonly_fields = ['path', 'ip_address', 'user', 'session_key',
                       'user_agent', 'referrer', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def path_display(self, obj):
        return format_html(
            '<code style="background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:12px">{}</code>',
            obj.path[:80]
        )
    path_display.short_description = 'Page Path'

    def user_display(self, obj):
        if obj.user:
            url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return format_html('<span style="color:#9ca3af">Guest</span>')
    user_display.short_description = 'User'

    def referrer_short(self, obj):
        if obj.referrer:
            return obj.referrer[:60] + ('…' if len(obj.referrer) > 60 else '')
        return '—'
    referrer_short.short_description = 'Referrer'


# ─────────────────────────────────────────────
# 3.  NEWSLETTER SUBSCRIBERS
# ─────────────────────────────────────────────
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'status', 'status_badge', 'source_badge',
        'linked_user', 'subscribed_at',
    ]
    list_filter = ['status', 'source', 'subscribed_at']
    search_fields = ['email', 'first_name', 'user__username']
    list_editable = ['status']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'ip_address', 'user']
    ordering = ['-subscribed_at']
    date_hierarchy = 'subscribed_at'

    fieldsets = (
        ('📧 Subscriber Info', {
            'fields': ('email', 'first_name', 'user'),
        }),
        ('📊 Status & Source', {
            'fields': ('status', 'source'),
        }),
        ('📝 Notes', {
            'fields': ('notes',),
        }),
        ('🕓 Timestamps', {
            'fields': ('subscribed_at', 'unsubscribed_at', 'ip_address'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_active', 'mark_unsubscribed']

    def status_badge(self, obj):
        colors = {
            'active': ('#10b981', '✅'),
            'unsubscribed': ('#ef4444', '🚫'),
            'bounced': ('#f59e0b', '⚠️'),
        }
        color, icon = colors.get(obj.status, ('#9ca3af', '?'))
        return format_html(
            '<span style="color:{};font-weight:600">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def source_badge(self, obj):
        icons = {
            'signup': '📝', 'checkout': '🛒',
            'footer': '🦶', 'popup': '💬', 'other': '📌',
        }
        return f"{icons.get(obj.source, '📌')} {obj.get_source_display()}"
    source_badge.short_description = 'Source'

    def linked_user(self, obj):
        if obj.user:
            url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '—'
    linked_user.short_description = 'Account'

    @admin.action(description='✅ Mark selected as Active')
    def mark_active(self, request, queryset):
        queryset.update(status='active', unsubscribed_at=None)
        self.message_user(request, f"{queryset.count()} subscribers marked active.")

    @admin.action(description='🚫 Unsubscribe selected')
    def mark_unsubscribed(self, request, queryset):
        queryset.update(status='unsubscribed', unsubscribed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} subscribers unsubscribed.")


# ─────────────────────────────────────────────
# 4.  LOW STOCK ALERTS
# ─────────────────────────────────────────────
@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display = [
        'product_link', 'stock_at_alert', 'threshold',
        'stock_level_bar', 'status', 'status_badge',
        'acknowledged_by', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['product__name', 'product__sku']
    list_editable = ['status']
    readonly_fields = ['product', 'stock_at_alert', 'created_at', 'acknowledged_at', 'updated_at']
    ordering = ['status', 'stock_at_alert']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📦 Product', {
            'fields': ('product', 'stock_at_alert', 'threshold'),
        }),
        ('🔔 Alert Status', {
            'fields': ('status', 'acknowledged_by', 'acknowledged_at'),
        }),
        ('📝 Notes', {
            'fields': ('notes',),
        }),
        ('🕓 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_acknowledged', 'mark_restocked', 'mark_dismissed']

    def product_link(self, obj):
        url = reverse('admin:store_product_change', args=[obj.product.pk])
        return format_html('<a href="{}" style="font-weight:600">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

    def stock_level_bar(self, obj):
        pct = min(int((obj.stock_at_alert / max(obj.threshold, 1)) * 100), 100)
        color = '#ef4444' if pct <= 25 else '#f59e0b' if pct <= 60 else '#10b981'
        return format_html(
            '<div style="width:120px;background:#e5e7eb;border-radius:6px;height:14px">'
            '<div style="width:{pct}%;background:{color};height:14px;border-radius:6px;'
            'transition:width .3s"></div></div>'
            '<small style="color:{color}">{stock} / {thresh}</small>',
            pct=pct, color=color, stock=obj.stock_at_alert, thresh=obj.threshold
        )
    stock_level_bar.short_description = 'Stock Level'

    def status_badge(self, obj):
        styles = {
            'open': ('background:#fef2f2;color:#ef4444;', '🔴 Open'),
            'acknowledged': ('background:#fffbeb;color:#d97706;', '🟡 Acknowledged'),
            'restocked': ('background:#f0fdf4;color:#16a34a;', '🟢 Restocked'),
            'dismissed': ('background:#f9fafb;color:#6b7280;', '⚫ Dismissed'),
        }
        style, label = styles.get(obj.status, ('', obj.status))
        return format_html(
            '<span style="{}padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">{}</span>',
            style, label
        )
    status_badge.short_description = 'Status'

    @admin.action(description='🟡 Mark as Acknowledged')
    def mark_acknowledged(self, request, queryset):
        queryset.update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} alerts acknowledged.")

    @admin.action(description='🟢 Mark as Restocked')
    def mark_restocked(self, request, queryset):
        queryset.update(status='restocked')
        self.message_user(request, f"{queryset.count()} alerts marked as restocked.")

    @admin.action(description='⚫ Dismiss selected alerts')
    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed')
        self.message_user(request, f"{queryset.count()} alerts dismissed.")


# ─────────────────────────────────────────────
# 5.  ADMIN ACTIVITY LOG
# ─────────────────────────────────────────────
@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'admin_user_display', 'action_badge',
        'model_name', 'object_repr_short', 'ip_address', 'description_short',
    ]
    list_filter = ['action_type', 'model_name', 'created_at', 'admin_user']
    search_fields = ['admin_user__username', 'model_name', 'object_repr', 'description']
    readonly_fields = [
        'admin_user', 'action_type', 'model_name', 'object_id',
        'object_repr', 'description', 'ip_address', 'created_at',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('👤 Who', {'fields': ('admin_user', 'ip_address')}),
        ('🔧 What', {'fields': ('action_type', 'model_name', 'object_id', 'object_repr')}),
        ('📝 Details', {'fields': ('description',)}),
        ('🕓 When', {'fields': ('created_at',)}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def admin_user_display(self, obj):
        if obj.admin_user:
            url = reverse('admin:accounts_customuser_change', args=[obj.admin_user.pk])
            return format_html(
                '<a href="{}" style="font-weight:600">👤 {}</a>',
                url, obj.admin_user.username
            )
        return format_html('<span style="color:#9ca3af">System</span>')
    admin_user_display.short_description = 'Admin'

    def action_badge(self, obj):
        configs = {
            'create':        ('#10b981', '➕'),
            'update':        ('#3b82f6', '✏️'),
            'delete':        ('#ef4444', '🗑️'),
            'login':         ('#6366f1', '🔑'),
            'logout':        ('#8b5cf6', '🚪'),
            'export':        ('#f59e0b', '📤'),
            'status_change': ('#06b6d4', '🔄'),
            'refund':        ('#ec4899', '💸'),
            'other':         ('#6b7280', '📌'),
        }
        color, icon = configs.get(obj.action_type, ('#6b7280', '📌'))
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:10px;font-size:11px">{} {}</span>',
            color, icon, obj.get_action_type_display()
        )
    action_badge.short_description = 'Action'

    def object_repr_short(self, obj):
        if obj.object_repr:
            return obj.object_repr[:50] + ('…' if len(obj.object_repr) > 50 else '')
        return '—'
    object_repr_short.short_description = 'Object'

    def description_short(self, obj):
        if obj.description:
            return obj.description[:60] + ('…' if len(obj.description) > 60 else '')
        return '—'
    description_short.short_description = 'Description'

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_badge', 'order_link', 'customer_link',
        'gateway_badge', 'amount_display', 'currency',
        'status_badge', 'refund_display', 'created_at',
    ]
    list_filter = ['gateway', 'status', 'currency', 'created_at']
    search_fields = [
        'transaction_id', 'order__order_number',
        'user__username', 'user__email', 'gateway_order_id',
    ]
    readonly_fields = [
        'order', 'user', 'gateway', 'transaction_id',
        'gateway_order_id', 'amount', 'currency', 'status',
        'gateway_response', 'failure_reason',
        'refund_amount', 'refund_id', 'refunded_at',
        'created_at', 'updated_at',
        'payment_detail_panel',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('💳 Transaction Overview', {
            'fields': ('payment_detail_panel',),
        }),
        ('🔗 Links', {
            'fields': ('order', 'user'),
        }),
        ('🏦 Gateway Details', {
            'fields': ('gateway', 'transaction_id', 'gateway_order_id', 'currency', 'amount', 'status'),
        }),
        ('💸 Refund Info', {
            'fields': ('refund_amount', 'refund_id', 'refunded_at', 'failure_reason'),
        }),
        ('📄 Gateway Response (Raw)', {
            'fields': ('gateway_response',),
            'classes': ('collapse',),
        }),
        ('🕓 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False

    # ── list columns ──────────────────────────────────────────────────────────

    def transaction_badge(self, obj):
        if obj.transaction_id:
            return format_html(
                '<code style="background:#f0f9ff;color:#0369a1;padding:3px 8px;'
                'border-radius:4px;font-size:11px">{}</code>',
                obj.transaction_id[:24] + ('…' if len(obj.transaction_id) > 24 else '')
            )
        return format_html('<span style="color:#9ca3af">—</span>')
    transaction_badge.short_description = 'Transaction ID'

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html(
            '<a href="{}" style="font-weight:600;font-family:monospace">#{}</a>',
            url, obj.order.order_number
        )
    order_link.short_description = 'Order'

    def customer_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">👤 {}</a><br>'
            '<small style="color:#6b7280">{}</small>',
            url, obj.user.username, obj.user.email
        )
    customer_link.short_description = 'Customer'

    def gateway_badge(self, obj):
        icons = {
            'stripe': ('💳', '#6772e5'),
            'cod':    ('💵', '#10b981'),
            'upi':    ('📱', '#f97316'),
            'netbanking': ('🏦', '#3b82f6'),
        }
        icon, color = icons.get(obj.gateway, ('💰', '#6b7280'))
        return format_html(
            '<span style="color:{};font-weight:600">{} {}</span>',
            color, icon, obj.get_gateway_display()
        )
    gateway_badge.short_description = 'Gateway'

    def amount_display(self, obj):
        return format_html(
            '<strong style="color:#059669;font-size:14px">₹{}</strong>',
            format(obj.amount, ',.2f')
        )
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        cfg = {
            'initiated': ('#f3f4f6', '#374151', '🔵'),
            'pending':   ('#fef3c7', '#92400e', '⏳'),
            'success':   ('#d1fae5', '#065f46', '✅'),
            'failed':    ('#fee2e2', '#991b1b', '❌'),
            'refunded':  ('#fce7f3', '#9d174d', '💸'),
            'cancelled': ('#f3f4f6', '#374151', '🚫'),
        }
        bg, fg, icon = cfg.get(obj.status, ('#f3f4f6', '#374151', '📌'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 9px;'
            'border-radius:12px;font-size:11px;font-weight:600">{} {}</span>',
            bg, fg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def refund_display(self, obj):
        if obj.refund_amount:
            return format_html(
                '<span style="color:#9d174d;font-weight:600">-₹{}</span><br>'
                '<small style="color:#6b7280">{}</small>',
                format(obj.refund_amount, ',.2f'),
                obj.refunded_at.strftime('%d %b %Y') if obj.refunded_at else 'pending',
            )
        return '—'
    refund_display.short_description = 'Refund'

    def payment_detail_panel(self, obj):
        html = f'''
        <table style="width:100%;border-collapse:collapse;max-width:600px">
          <tr><td style="padding:6px 0;color:#6b7280;width:180px">Transaction ID</td>
              <td style="font-family:monospace;font-weight:600">{obj.transaction_id or '—'}</td></tr>
          <tr><td style="padding:6px 0;color:#6b7280">Gateway Order ID</td>
              <td style="font-family:monospace">{obj.gateway_order_id or '—'}</td></tr>
          <tr><td style="padding:6px 0;color:#6b7280">Amount</td>
              <td style="font-weight:700;color:#059669;font-size:16px">₹{obj.amount:,.2f} {obj.currency}</td></tr>
          <tr><td style="padding:6px 0;color:#6b7280">Gateway</td>
              <td>{obj.get_gateway_display()}</td></tr>
          <tr><td style="padding:6px 0;color:#6b7280">Status</td>
              <td><strong>{obj.get_status_display()}</strong></td></tr>
        '''
        if obj.failure_reason:
            html += f'<tr><td style="padding:6px 0;color:#ef4444">Failure Reason</td><td style="color:#ef4444">{obj.failure_reason}</td></tr>'
        if obj.refund_amount:
            html += f'<tr><td style="padding:6px 0;color:#9d174d">Refund Amount</td><td style="color:#9d174d;font-weight:600">₹{obj.refund_amount:,.2f}</td></tr>'
            html += f'<tr><td style="padding:6px 0;color:#9d174d">Refund ID</td><td style="font-family:monospace">{obj.refund_id}</td></tr>'
        html += '</table>'
        return format_html(html)
    payment_detail_panel.short_description = '💳 Payment Record'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        stats = qs.filter(status='success').aggregate(
            total=Sum('amount'), count=Count('id')
        )
        extra_context['payment_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory, Return


# ── Inlines ────────────────────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_link', 'product_name', 'product_sku', 'quantity', 'unit_price', 'total_price', 'item_subtotal']
    fields = ['product_link', 'product_name', 'product_sku', 'quantity', 'unit_price', 'total_price', 'item_subtotal']

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:store_product_change', args=[obj.product.pk])
            return format_html('<a href="{}" style="font-weight:600">{}</a>', url, obj.product_name)
        return obj.product_name
    product_link.short_description = 'Product'

    def item_subtotal(self, obj):
        return format_html('<strong>₹{}</strong>', format(obj.total_price, ',.2f'))
    item_subtotal.short_description = 'Subtotal'


class OrderStatusInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status_badge', 'note', 'created_by', 'created_at']
    fields = ['status_badge', 'note', 'created_by', 'created_at']

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b', 'confirmed': '#3b82f6', 'processing': '#8b5cf6',
            'shipped': '#06b6d4', 'out_for_delivery': '#f97316', 'delivered': '#10b981',
            'cancelled': '#ef4444', 'returned': '#6b7280', 'refunded': '#ec4899',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.status.replace('_', ' ').title()
        )
    status_badge.short_description = 'Status'


# ── Order Admin ─────────────────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number_badge', 'customer_info', 'status_badge',
        'payment_badge', 'payment_method_badge',
        'items_summary', 'total_display',
        'shipping_city', 'tracking_display',
        'created_at',
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method',
        'created_at', 'country',
    ]
    search_fields = [
        'order_number', 'user__username', 'user__email',
        'full_name', 'phone', 'email',
        'city', 'state', 'tracking_number',
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at',
        'order_summary_panel', 'shipping_panel', 'pricing_panel',
    ]
    inlines = [OrderItemInline, OrderStatusInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('📋 Order Overview', {
            'fields': ('order_summary_panel',),
        }),
        ('📦 Order Details', {
            'fields': ('order_number', 'user', 'status', 'tracking_number', 'notes', 'admin_notes'),
        }),
        ('💳 Payment', {
            'fields': ('payment_status', 'payment_method', 'stripe_payment_intent'),
        }),
        ('🚚 Shipping Address', {
            'fields': ('shipping_panel',),
        }),
        ('💰 Pricing Breakdown', {
            'fields': ('pricing_panel',),
        }),
        ('🕓 Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',),
        }),
    )

    actions = [
        'mark_confirmed', 'mark_processing', 'mark_shipped',
        'mark_delivered', 'mark_cancelled',
    ]

    # ── list columns ──────────────────────────────────────────────────────────

    def order_number_badge(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="font-family:monospace;font-weight:700;'
            'font-size:13px;color:#1d4ed8">#{}</a>',
            url, obj.order_number
        )
    order_number_badge.short_description = 'Order #'

    def customer_info(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}" style="font-weight:600">👤 {}</a><br>'
            '<small style="color:#6b7280">{}</small><br>'
            '<small style="color:#6b7280">📞 {}</small>',
            url, obj.full_name or obj.user.username,
            obj.email, obj.phone,
        )
    customer_info.short_description = 'Customer'

    def status_badge(self, obj):
        cfg = {
            'pending':          ('#fef3c7', '#92400e', '⏳'),
            'confirmed':        ('#dbeafe', '#1e40af', '✅'),
            'processing':       ('#ede9fe', '#5b21b6', '⚙️'),
            'shipped':          ('#cffafe', '#155e75', '📦'),
            'out_for_delivery': ('#ffedd5', '#9a3412', '🚚'),
            'delivered':        ('#d1fae5', '#065f46', '✔️'),
            'cancelled':        ('#fee2e2', '#991b1b', '❌'),
            'returned':         ('#f3f4f6', '#374151', '↩️'),
            'refunded':         ('#fce7f3', '#9d174d', '💸'),
        }
        bg, fg, icon = cfg.get(obj.status, ('#f3f4f6', '#374151', '📌'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 9px;'
            'border-radius:12px;font-size:11px;font-weight:600;white-space:nowrap">'
            '{} {}</span>',
            bg, fg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_badge(self, obj):
        cfg = {
            'paid':     ('#d1fae5', '#065f46', '💳 Paid'),
            'pending':  ('#fef3c7', '#92400e', '⏳ Pending'),
            'failed':   ('#fee2e2', '#991b1b', '❌ Failed'),
            'refunded': ('#fce7f3', '#9d174d', '💸 Refunded'),
            'cod':      ('#e0e7ff', '#3730a3', '💵 COD'),
        }
        bg, fg, label = cfg.get(obj.payment_status, ('#f3f4f6', '#374151', obj.payment_status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 9px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, label
        )
    payment_badge.short_description = 'Payment'

    def payment_method_badge(self, obj):
        icons = {
            'stripe': '💳 Card', 'cod': '💵 COD',
            'upi': '📱 UPI', 'netbanking': '🏦 NetBanking',
        }
        return icons.get(obj.payment_method, obj.payment_method)
    payment_method_badge.short_description = 'Method'

    def items_summary(self, obj):
        items = obj.items.all()
        count = sum(i.quantity for i in items)
        products = ', '.join(i.product_name[:20] for i in items[:2])
        if items.count() > 2:
            products += f' +{items.count()-2} more'
        return format_html(
            '<span style="font-weight:600">{} item(s)</span><br>'
            '<small style="color:#6b7280">{}</small>',
            count, products
        )
    items_summary.short_description = 'Items'

    def total_display(self, obj):
        return format_html(
            '<strong style="color:#059669;font-size:14px">₹{}</strong>',
            format(obj.total_amount, ',.2f')
        )
    total_display.short_description = 'Total'

    def shipping_city(self, obj):
        return format_html(
            '📍 {}, {}<br><small style="color:#6b7280">{}</small>',
            obj.city, obj.state, obj.country
        )
    shipping_city.short_description = 'Ship To'

    def tracking_display(self, obj):
        if obj.tracking_number:
            return format_html(
                '<code style="background:#f0fdf4;padding:2px 6px;border-radius:4px;'
                'font-size:11px;color:#065f46">{}</code>',
                obj.tracking_number
            )
        return format_html('<span style="color:#9ca3af">—</span>')
    tracking_display.short_description = 'Tracking'

    # ── detail page panels ────────────────────────────────────────────────────

    def order_summary_panel(self, obj):
        items = obj.items.all()
        rows = ''.join(
            f'<tr style="border-bottom:1px solid #f3f4f6">'
            f'<td style="padding:8px 12px">{i.product_name}</td>'
            f'<td style="padding:8px 12px;text-align:center">{i.quantity}</td>'
            f'<td style="padding:8px 12px;text-align:right">₹{i.unit_price:,.2f}</td>'
            f'<td style="padding:8px 12px;text-align:right"><strong>₹{i.total_price:,.2f}</strong></td>'
            f'</tr>'
            for i in items
        )
        return format_html(
            '<table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px">'
            '<thead><tr style="background:#f9fafb">'
            '<th style="padding:10px 12px;text-align:left">Product</th>'
            '<th style="padding:10px 12px;text-align:center">Qty</th>'
            '<th style="padding:10px 12px;text-align:right">Unit Price</th>'
            '<th style="padding:10px 12px;text-align:right">Subtotal</th>'
            '</tr></thead><tbody>{}</tbody></table>',
            format_html(rows)
        )
    order_summary_panel.short_description = '🛒 Ordered Items'

    def shipping_panel(self, obj):
        return format_html(
            '<div style="background:#f8fafc;padding:16px;border-radius:8px;'
            'border:1px solid #e2e8f0;line-height:1.8">'
            '<strong style="font-size:14px">{}</strong><br>'
            '📞 {}<br>📧 {}<br>'
            '🏠 {}{}<br>'
            '📍 {}, {} — {}<br>'
            '🌍 {}'
            '</div>',
            obj.full_name, obj.phone, obj.email,
            obj.address_line1,
            (', ' + obj.address_line2) if obj.address_line2 else '',
            obj.city, obj.state, obj.zip_code,
            obj.country,
        )
    shipping_panel.short_description = '🚚 Shipping Address'

    def pricing_panel(self, obj):
        rows = [
            ('Subtotal', obj.subtotal),
            ('Discount', f'-₹{obj.discount_amount:,.2f}' if obj.discount_amount else '₹0.00'),
            ('Shipping', obj.shipping_cost),
            ('Tax', obj.tax_amount),
        ]
        html = '<table style="width:300px;border-collapse:collapse">'
        for label, val in rows:
            if isinstance(val, str):
                html += f'<tr><td style="padding:4px 8px;color:#6b7280">{label}</td><td style="padding:4px 8px;text-align:right;color:#ef4444">{val}</td></tr>'
            else:
                html += f'<tr><td style="padding:4px 8px;color:#6b7280">{label}</td><td style="padding:4px 8px;text-align:right">₹{val:,.2f}</td></tr>'
        html += (
            f'<tr style="border-top:2px solid #1f2937">'
            f'<td style="padding:8px;font-weight:700;font-size:15px">TOTAL</td>'
            f'<td style="padding:8px;text-align:right;font-weight:700;font-size:15px;color:#059669">₹{obj.total_amount:,.2f}</td>'
            f'</tr>'
        )
        if obj.coupon_code:
            html += f'<tr><td colspan="2" style="padding:4px 8px;color:#7c3aed;font-size:12px">🎟 Coupon: {obj.coupon_code}</td></tr>'
        html += '</table>'
        return format_html(html)
    pricing_panel.short_description = '💰 Pricing Breakdown'

    # ── bulk status actions ───────────────────────────────────────────────────

    @admin.action(description='✅ Mark as Confirmed')
    def mark_confirmed(self, request, queryset):
        n = queryset.update(status='confirmed')
        self.message_user(request, f'{n} orders confirmed.')

    @admin.action(description='⚙️ Mark as Processing')
    def mark_processing(self, request, queryset):
        n = queryset.update(status='processing')
        self.message_user(request, f'{n} orders set to processing.')

    @admin.action(description='📦 Mark as Shipped')
    def mark_shipped(self, request, queryset):
        n = queryset.update(status='shipped')
        self.message_user(request, f'{n} orders marked shipped.')

    @admin.action(description='✔️ Mark as Delivered')
    def mark_delivered(self, request, queryset):
        n = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{n} orders marked delivered.')

    @admin.action(description='❌ Mark as Cancelled')
    def mark_cancelled(self, request, queryset):
        n = queryset.update(status='cancelled')
        self.message_user(request, f'{n} orders cancelled.')


# ── Return / Refund Admin ──────────────────────────────────────────────────────
@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = [
        'order_link', 'customer_link', 'reason_badge',
        'status_badge', 'description_short', 'created_at',
    ]
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['order__order_number', 'user__username', 'description']
    readonly_fields = ['order', 'user', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('📦 Order & Customer', {'fields': ('order', 'user')}),
        ('↩️ Return Details', {'fields': ('reason', 'description', 'status', 'admin_response')}),
        ('🕓 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['approve_returns', 'reject_returns', 'complete_returns']

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}" style="font-weight:600;font-family:monospace">#{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def customer_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">👤 {}</a>', url, obj.user.username)
    customer_link.short_description = 'Customer'

    def reason_badge(self, obj):
        icons = {
            'defective': '⚠️', 'wrong_item': '📦',
            'not_as_described': '🔍', 'changed_mind': '🤔', 'other': '📌',
        }
        return f"{icons.get(obj.reason, '📌')} {obj.get_reason_display()}"
    reason_badge.short_description = 'Reason'

    def status_badge(self, obj):
        cfg = {
            'pending':   ('#fef3c7', '#92400e', '⏳'),
            'approved':  ('#d1fae5', '#065f46', '✅'),
            'rejected':  ('#fee2e2', '#991b1b', '❌'),
            'completed': ('#dbeafe', '#1e40af', '✔️'),
        }
        bg, fg, icon = cfg.get(obj.status, ('#f3f4f6', '#374151', '📌'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 9px;border-radius:12px;font-size:11px;font-weight:600">{} {}</span>',
            bg, fg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def description_short(self, obj):
        return obj.description[:60] + ('…' if len(obj.description) > 60 else '')
    description_short.short_description = 'Description'

    @admin.action(description='✅ Approve selected returns')
    def approve_returns(self, request, queryset):
        n = queryset.update(status='approved')
        self.message_user(request, f'{n} returns approved.')

    @admin.action(description='❌ Reject selected returns')
    def reject_returns(self, request, queryset):
        n = queryset.update(status='rejected')
        self.message_user(request, f'{n} returns rejected.')

    @admin.action(description='✔️ Mark as Completed')
    def complete_returns(self, request, queryset):
        n = queryset.update(status='completed')
        self.message_user(request, f'{n} returns completed.')

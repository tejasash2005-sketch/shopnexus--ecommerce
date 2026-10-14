from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Product, Category, Brand, Cart, CartItem, Coupon
from orders.models import Order, OrderItem, Return
from payments.models import Payment
from reviews.models import Review
from wishlist.models import Wishlist
from analytics.models import SalesReport, SiteVisit, NewsletterSubscriber, LowStockAlert, AdminActivityLog
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed advanced demo records for the professional dashboard'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding advanced data...')

        admin = User.objects.filter(is_superuser=True).first()
        users = list(User.objects.filter(is_superuser=False))
        products = list(Product.objects.all())

        if not products:
            self.stdout.write(self.style.ERROR('Please run seed_data first to create products!'))
            return

        # 1. Orders & Payments
        for i in range(20):
            user = random.choice(users)
            order = Order.objects.create(
                user=user,
                status=random.choice(['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']),
                payment_status=random.choice(['pending', 'paid']),
                payment_method=random.choice(['stripe', 'cod', 'upi']),
                full_name=f"{user.first_name} {user.last_name}",
                email=user.email,
                phone=user.phone,
                address_line1="123 Demo Street",
                city="Bangalore",
                state="Karnataka",
                zip_code="560001",
                country="India",
                subtotal=random.randint(500, 5000),
                total_amount=random.randint(500, 5000)
            )

            # Add Order Items
            OrderItem.objects.create(
                order=order,
                product=random.choice(products),
                product_name="Sample Product",
                quantity=random.randint(1, 3),
                unit_price=500,
                total_price=500
            )

            # Create Payment for Paid orders
            if order.payment_status == 'paid':
                Payment.objects.create(
                    order=order,
                    user=user,
                    gateway=order.payment_method,
                    transaction_id=f"TXN{random.randint(100000, 999999)}",
                    amount=order.total_amount,
                    status='success'
                )

        # 2. Returns
        delivered_orders = Order.objects.filter(status='delivered')[:5]
        for order in delivered_orders:
            Return.objects.get_or_create(
                order=order,
                user=order.user,
                defaults={
                    'reason': random.choice(['defective', 'wrong_item', 'changed_mind']),
                    'description': "Demo return description",
                    'status': 'pending'
                }
            )

        # 3. Reviews
        for i in range(20):
            u = random.choice(users)
            p = random.choice(products)
            if not Review.objects.filter(user=u, product=p).exists():
                Review.objects.create(
                    product=p,
                    user=u,
                    rating=random.randint(3, 5),
                    title="Great product",
                    body="I really liked this item. Highly recommended!",
                    is_approved=random.choice([True, False])
                )

        # 4. Wishlists
        for user in users:
            wishlist, _ = Wishlist.objects.get_or_create(user=user)
            wishlist.products.add(*random.sample(products, 3))

        # 5. Site Visits
        paths = ['/', '/shop/', '/cart/', '/profile/', '/about/']
        for i in range(50):
            SiteVisit.objects.create(
                path=random.choice(paths),
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user=random.choice(users + [None]),
                created_at=timezone.now() - timedelta(hours=random.randint(1, 48))
            )

        # 6. Low Stock Alerts
        for p in products[:3]:
            LowStockAlert.objects.get_or_create(
                product=p,
                defaults={'stock_at_alert': p.stock, 'threshold': 10, 'status': 'open'}
            )

        # 7. Sales Reports (Last 7 days)
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            SalesReport.objects.get_or_create(
                date=date,
                defaults={
                    'total_orders': random.randint(5, 15),
                    'total_revenue': random.randint(2000, 10000),
                    'total_items_sold': random.randint(10, 30),
                    'new_customers': random.randint(1, 5),
                    'average_order_value': random.randint(500, 1000)
                }
            )

        # 8. Admin Activity
        actions = ['create', 'update', 'status_change', 'login']
        for i in range(15):
            AdminActivityLog.objects.create(
                admin_user=admin,
                action_type=random.choice(actions),
                model_name=random.choice(['Product', 'Order', 'User']),
                object_repr="Sample Object",
                description="Demo activity log entry"
            )

        # 9. Newsletter Subscribers
        for u in users[:5]:
            NewsletterSubscriber.objects.get_or_create(
                email=u.email,
                defaults={'user': u, 'status': 'active', 'source': 'checkout'}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded advanced demo records!'))

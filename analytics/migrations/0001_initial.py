from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=500)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('session_key', models.CharField(blank=True, max_length=100)),
                ('user_agent', models.TextField(blank=True)),
                ('referrer', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.customuser')),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Site Visit', 'verbose_name_plural': 'Site Visits'},
        ),
        migrations.CreateModel(
            name='SalesReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_items_sold', models.PositiveIntegerField(default=0)),
                ('new_customers', models.PositiveIntegerField(default=0)),
                ('cancelled_orders', models.PositiveIntegerField(default=0)),
                ('refunded_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('average_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-date'], 'verbose_name': 'Sales Report', 'verbose_name_plural': 'Sales Reports'},
        ),
        migrations.CreateModel(
            name='AdminActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('create', 'Created'), ('update', 'Updated'), ('delete', 'Deleted'), ('login', 'Logged In'), ('logout', 'Logged Out'), ('export', 'Exported Data'), ('status_change', 'Status Changed'), ('refund', 'Issued Refund'), ('other', 'Other')], default='other', max_length=20)),
                ('model_name', models.CharField(blank=True, max_length=100)),
                ('object_id', models.CharField(blank=True, max_length=100)),
                ('object_repr', models.CharField(blank=True, max_length=500)),
                ('description', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to='accounts.customuser')),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Activity Log', 'verbose_name_plural': 'Activity Logs'},
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('active', 'Active'), ('unsubscribed', 'Unsubscribed'), ('bounced', 'Bounced')], default='active', max_length=20)),
                ('source', models.CharField(choices=[('signup', 'Signup Form'), ('checkout', 'Checkout'), ('footer', 'Footer'), ('popup', 'Popup'), ('other', 'Other')], default='signup', max_length=20)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('unsubscribed_at', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='newsletter_entry', to='accounts.customuser')),
            ],
            options={'ordering': ['-subscribed_at'], 'verbose_name': 'Newsletter Subscriber', 'verbose_name_plural': 'Newsletter Subscribers'},
        ),
        migrations.CreateModel(
            name='LowStockAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_at_alert', models.PositiveIntegerField()),
                ('threshold', models.PositiveIntegerField(default=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('acknowledged', 'Acknowledged'), ('restocked', 'Restocked'), ('dismissed', 'Dismissed')], default='open', max_length=20)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_alerts', to='store.product')),
                ('acknowledged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acknowledged_alerts', to='accounts.customuser')),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Low Stock Alert', 'verbose_name_plural': 'Low Stock Alerts'},
        ),
    ]

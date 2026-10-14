# 🛍️ ShopNexus

A full-stack **e-commerce platform** built with Django. ShopNexus covers the complete shopping journey — product catalog, cart with coupons, checkout, order tracking, payments, reviews and wishlists — plus a custom admin dashboard with sales analytics.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2%2B-092E20?logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![Stripe](https://img.shields.io/badge/Payments-Stripe%20(demo)-635BFF?logo=stripe&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

## ✨ Features

**Storefront**
- Product catalog with categories, brands, multi-image galleries and search
- Session and user-based shopping cart with coupon codes
- Checkout with saved or new shipping addresses
- Order tracking with status timeline, cancellation and return requests
- Star ratings and reviews with a "helpful" vote
- Wishlist with AJAX toggle
- Responsive Bootstrap 5 interface

**Payments**
- Cash on delivery, card (Stripe demo mode), UPI and net banking simulation
- Payment history for each customer

**Admin dashboard**
- Product, category and brand management with image uploads
- Order management with status updates and return approvals
- User management and account activation controls
- Review moderation and payment monitoring
- Sales analytics, site visits, low-stock alerts and newsletter subscribers
- Full Django admin with branded interface

## 🧰 Tech Stack

| Layer     | Technology                                |
|-----------|-------------------------------------------|
| Backend   | Python, Django 4.2+                       |
| Database  | SQLite (swappable for PostgreSQL/MySQL)   |
| Frontend  | Django templates, Bootstrap 5, Vanilla JS |
| Auth      | Custom user model (`accounts.CustomUser`) |
| Payments  | Stripe (demo mode)                        |
| Media     | Pillow                                    |

## 🚀 Getting Started

### Quick start (Windows)

Double-click `run_project.bat`. It installs dependencies, migrates, seeds data and starts the server.

### Manual setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/shopnexus-django-ecommerce.git
cd shopnexus-django-ecommerce

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Load sample data (products, users, coupons)
python manage.py seed_data

# 6. Start the server
python manage.py runserver
```

| URL                                  | Purpose                |
|--------------------------------------|------------------------|
| http://127.0.0.1:8000/               | Storefront             |
| http://127.0.0.1:8000/dashboard/     | Custom admin dashboard |
| http://127.0.0.1:8000/admin/         | Django admin           |

## 🔑 Demo Credentials

| Role     | Username   | Password   |
|----------|------------|------------|
| Admin    | `admin`    | `admin123` |
| Customer | `testuser` | `user123`  |

> ⚠️ Demo accounts created by `seed_data`. Change or remove them before any real deployment.

## 🎟️ Test Coupons

| Code        | Discount | Minimum Order |
|-------------|----------|---------------|
| `WELCOME20` | 20% off  | None          |
| `FLAT100`   | ₹100 off | ₹500          |
| `SAVE15`    | 15% off  | ₹1000         |

## 📁 Project Structure

```
├── manage.py
├── requirements.txt
├── run_project.bat
├── ecommerce_project/   # settings, root urls, wsgi/asgi
├── store/               # products, categories, brands, cart, coupons
├── accounts/            # custom user, profile, addresses
├── orders/              # checkout, order tracking, returns
├── payments/            # Stripe demo, payment simulation, history
├── reviews/             # ratings and helpful votes
├── wishlist/            # saved products
├── analytics/           # site visits, sales reports, stock alerts
├── dashboard/           # custom admin dashboard
├── templates/           # HTML templates
└── static/              # CSS and assets
```

## 🗄️ Data Models

`CustomUser` · `Address` · `Category` · `Brand` · `Product` · `ProductImage` · `Cart` · `CartItem` · `Coupon` · `Order` · `OrderItem` · `OrderStatusHistory` · `Return` · `Payment` · `Review` · `ReviewHelpful` · `Wishlist` · `SiteVisit` · `SalesReport` · `AdminActivityLog` · `NewsletterSubscriber` · `LowStockAlert`

## 🔒 Before Deploying to Production

- Move `SECRET_KEY`, `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY` to environment variables
- Set `DEBUG = False` and restrict `ALLOWED_HOSTS`
- Remove the seeded demo accounts
- Replace the console email backend with a real SMTP provider
- Use PostgreSQL/MySQL and serve with Gunicorn + Nginx
- Run `python manage.py collectstatic`

## 🛣️ Roadmap

- [ ] Live Stripe payment integration
- [ ] REST API (Django REST Framework)
- [ ] Email order confirmations
- [ ] Docker support
- [ ] Automated test suite

## 📄 License

Released under the [MIT License](LICENSE).

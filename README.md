# 🛍️ ShopNexus — Full-Stack Django E-Commerce Platform
**Final Year Project | Django + SQLite | Payment Integration**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install django pillow stripe

# 2. Run migrations
python manage.py migrate

# 3. Seed sample data (products, users, coupons)
python manage.py seed_data

# 4. Start development server
python manage.py runserver

# 5. Visit: http://127.0.0.1:8000
```

---

## 🔐 Login Credentials

| Role  | Username  | Password  | Access |
|-------|-----------|-----------|--------|
| Admin | `admin`   | `admin123`| Full Admin Panel + Website |
| User  | `testuser`| `user123` | Customer Portal |

**Admin Panel:** http://127.0.0.1:8000/admin/

---

## 📦 Tech Stack

| Layer        | Technology            |
|--------------|-----------------------|
| Backend      | Django 4.x (Python)   |
| Database     | SQLite3               |
| Frontend     | Bootstrap 5 + Vanilla JS |
| Auth         | Django Custom Auth    |
| Payments     | Stripe (simulated demo) |
| Icons        | Bootstrap Icons       |
| Fonts        | Google Poppins        |

---

## 🗂️ Project Structure

```
ecommerce_project/
├── accounts/        # USER MODULE — Auth, Profile, Address
├── store/           # STORE MODULE — Products, Categories, Cart
├── orders/          # ORDER MODULE — Checkout, Order Tracking
├── payments/        # PAYMENT MODULE — Stripe, COD, History
├── reviews/         # REVIEW MODULE — Ratings, Helpfulness
├── wishlist/        # WISHLIST MODULE — Save Products
├── templates/       # All HTML templates
├── static/css/      # Custom styles
└── manage.py
```

---

## 🛠️ Product Management (Admin Side)
- **Manual Product Addition**: Admins can manually add new products to the store via the dashboard.
- **Device Upload**: Choose and upload product images and thumbnails directly from your local device.
- **Comprehensive Details**: Apply all product details including pricing, stock, categories, brands, and descriptions.
- **User Visibility**: Once added in the admin panel, products are immediately visible to users in the "All Products" section.

---

## 🎯 6 Admin Modules

| Module | Features |
|--------|----------|
| **1. Product Management** | Add/Edit products, images, pricing, stock, featured flags |
| **2. Category & Brand** | Hierarchical categories, brand management, slugs |
| **3. Order Management** | View all orders, update status, add tracking, admin notes |
| **4. User Management** | View all users, edit profiles, manage permissions |
| **5. Coupon Management** | Create coupons (% / fixed), expiry, usage limits |
| **6. Review Moderation** | Approve/reject reviews, bulk actions, verified purchase badge |

---

## 👤 6 User Modules

| Module | Features |
|--------|----------|
| **1. Authentication** | Register, Login, Logout with session management |
| **2. Profile** | View/edit profile, order stats, profile picture upload |
| **3. Shopping Cart** | Add/update/remove items, coupon codes, free shipping threshold |
| **4. Checkout & Orders** | Saved addresses, payment selection, order tracking, cancel/return |
| **5. Payments** | COD, Stripe card, UPI, Net Banking (demo simulation) |
| **6. Wishlist & Reviews** | Save products, write reviews with star ratings, mark helpful |

---

## 💳 Coupon Codes (Test)

| Code       | Discount | Min Order |
|------------|----------|-----------|
| `WELCOME20`| 20% off  | No minimum |
| `FLAT100`  | ₹100 off | ₹500+ |
| `SAVE15`   | 15% off  | ₹1000+ |

---

## 🏗️ Database Models

- **CustomUser** — Extended Django User with phone, address, profile picture
- **Category** — Hierarchical with parent/child, slug auto-generation
- **Brand** — Product brands with logos
- **Product** — Full product with images, SKU, pricing, stock
- **ProductImage** — Multi-image with primary flag
- **Cart / CartItem** — Session + user cart, coupon support
- **Coupon** — % and fixed discounts with expiry and usage tracking
- **Order / OrderItem** — Complete order with address snapshot
- **OrderStatusHistory** — Full audit trail of status changes
- **Return** — Return request management
- **Payment** — Gateway, transaction ID, status tracking
- **Review / ReviewHelpful** — Star ratings with verified purchase
- **Wishlist** — M2M product wishlist per user
- **Address** — Multiple saved shipping addresses

---

## 🌟 Key Features

- ✅ Custom User Model with extended profile
- ✅ Multi-image product gallery
- ✅ Hierarchical categories
- ✅ Cart with coupon discount engine
- ✅ Checkout with saved/new address
- ✅ Order status tracker with timeline
- ✅ Payment simulation (Stripe demo mode)
- ✅ Star rating system with verified purchase
- ✅ Wishlist with AJAX toggle
- ✅ Admin panel with rich inline editing
- ✅ Full-text product search
- ✅ Responsive Bootstrap 5 UI
- ✅ Context processors for cart count & categories

---

*Built for Final Year Project — ShopNexus E-Commerce Platform*

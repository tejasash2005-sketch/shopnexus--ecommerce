from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),

    # Accounts
    path('accounts/', views.db_accounts, name='db_accounts'),
    path('accounts/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('accounts/<int:pk>/toggle-newsletter/', views.toggle_newsletter, name='toggle_newsletter'),

    # Store
    path('store/', views.db_store, name='db_store'),
    path('store/product/add/', views.add_product, name='add_product'),
    path('store/product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('store/product/<int:pk>/toggle/', views.toggle_product_status, name='toggle_product_status'),

    # Orders
    path('orders/', views.db_orders, name='db_orders'),
    path('orders/<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('orders/returns/', views.db_returns, name='db_returns'),
    path('orders/returns/<int:pk>/approve/', views.approve_return, name='approve_return'),

    # Payments
    path('payments/', views.db_payments, name='db_payments'),

    # Reviews
    path('reviews/', views.db_reviews, name='db_reviews'),
    path('reviews/<int:pk>/approve/', views.approve_review, name='approve_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),

    # Wishlist
    path('wishlist/', views.db_wishlist, name='db_wishlist'),

    # Analytics
    path('analytics/', views.db_analytics, name='db_analytics'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_view, name='wishlist'),
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('clear/', views.clear_wishlist, name='clear_wishlist'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<int:pk>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.order_list_view, name='order_list'),
    path('my-orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('my-orders/<int:pk>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('my-orders/<int:pk>/return/', views.return_request_view, name='return_request'),
]

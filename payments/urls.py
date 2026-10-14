from django.urls import path
from . import views

urlpatterns = [
    path('stripe/<int:pk>/', views.stripe_payment_view, name='stripe_payment'),
    path('stripe/<int:pk>/process/', views.stripe_process_view, name='stripe_process'),
    path('simulate/<int:pk>/', views.simulate_payment_view, name='simulate_payment'),
    path('history/', views.payment_history_view, name='payment_history'),
]

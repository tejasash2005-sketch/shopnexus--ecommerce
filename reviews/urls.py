from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:product_id>/', views.add_review_view, name='add_review'),
    path('delete/<int:pk>/', views.delete_review_view, name='delete_review'),
    path('helpful/<int:pk>/', views.mark_helpful_view, name='mark_helpful'),
    path('my-reviews/', views.my_reviews_view, name='my_reviews'),
]

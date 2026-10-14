from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('', include('store.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
    path('wishlist/', include('wishlist.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ── Professional Admin Branding ────────────────────────────────────────────────
admin.site.site_header  = "🛒 ShopNexus — Admin Control Panel"
admin.site.site_title   = "ShopNexus Admin"
admin.site.index_title  = "📊 Welcome to ShopNexus Dashboard"

from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_redirect(request):
    return redirect('admin_dashboard')

# You can also override the admin index view if you want it to be the dashboard
# But for now, I'll keep them separate as requested.


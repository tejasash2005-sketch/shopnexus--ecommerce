from .models import Cart, Category

def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            # FIX: only query if session_key exists and is non-empty
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            else:
                cart = None
        if cart:
            count = cart.total_items
    except:
        pass
    return {'cart_count': count}

def categories_list(request):
    categories = Category.objects.filter(is_active=True, parent=None)
    return {'nav_categories': categories}

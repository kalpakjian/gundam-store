from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from store.models import Cart


def auth_forms(request):
    """Inject login and register forms into all templates automatically."""
    return {
        'login_form': AuthenticationForm(),
        'register_form': UserCreationForm()
    }


def cart_item_count(request):
    """Inject cart item count into all templates for navbar badge."""
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            else:
                cart = None
        if cart:
            return {'cart_item_count': cart.items.count()}
    except Exception:
        pass
    return {'cart_item_count': 0}

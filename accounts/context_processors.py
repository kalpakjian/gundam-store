from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


def auth_forms(request):
    """Inject login and register forms into all templates automatically."""
    return {
        'login_form': AuthenticationForm(),
        'register_form': UserCreationForm()
    }

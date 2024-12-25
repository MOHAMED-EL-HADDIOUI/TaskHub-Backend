from django.http import HttpResponseForbidden

def role_required(role):
    """
    Décorateur pour restreindre l'accès à une vue en fonction du rôle de l'utilisateur.
    :param role: Rôle requis pour accéder à la vue (ex : 'MANAGER' ou 'USER').
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Vous n'avez pas l'autorisation d'effectuer cette action.")
        return _wrapped_view
    return decorator

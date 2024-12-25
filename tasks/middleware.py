from django.http import HttpResponseForbidden

# class RoleMiddleware:
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         # Exemple : Bloquer les utilisateurs sans rôle défini
#         if request.user.is_authenticated and not hasattr(request.user, 'role'):
#             return HttpResponseForbidden("Aucun rôle assigné à cet utilisateur.")
#         return self.get_response(request)

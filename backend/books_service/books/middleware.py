from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': 'Token manquant'}, status=401)
        # Appel User Service pour valider token
        return None

class RoleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Vérifier rôle selon request.user
        return None

from django.http import JsonResponse
from django.shortcuts import render
from teachers.models import Token
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def validate_token(request, token):
    try:
        token_obj = Token.objects.get(token=token)
        if token_obj.expires_at > timezone.now():
            return JsonResponse({'valid': True, 'message': 'Token válido y activo'}, status=200 )
        else:
            return JsonResponse({'valid': False, 'message': 'Token expirado'}, status=400)

        # Aquí puedes agregar lógica adicional si es necesario
    except Token.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Token no encontrado'}, status=404)

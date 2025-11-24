from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Token
from VARK.models import FormularioControlVark
from MBTI.models import FormularioControlMBTI
import random
import string
from django.db.models import Sum, Max
from django.utils import timezone

# Create your views here.
@login_required
def teachers_home(request):
    return render(request, 'teachers_home.html')   

@login_required
def tokens_view(request):
    tokens = Token.objects.filter(user=request.user)
    return render(request, 'teachers_tokens.html', {'tokens': tokens})

@login_required
def post_token(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método de solicitud no válido.'}, status=400)
    else:
        try: 
            user = request.user
            token_type = request.POST.get('token_type')
            expiration_date = request.POST.get('expiration')

            # Generamos un nuevo token de 24 caracteres alfanuméricos
            new_token = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
            new_token = Token.objects.create(
                user=user,
                token=new_token,
                token_type=token_type,
                expires_at=expiration_date
            )

            if new_token:
                return JsonResponse({'message': 'Token creado exitorsamente.', 'token': new_token.token})
            else:
                return JsonResponse({'error': 'Error al crear el token.'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def revoke_token(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método de solicitud no válido.'}, status=400)
    else:
        try:
            token_id = request.POST.get('revoke_token_id')
            token = Token.objects.get(id=token_id, user=request.user)
            token.delete()
            return JsonResponse({'message': 'Token revocado exitosamente.'})
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_reports(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método de solicitud no válido.'}, status=400)

    user = request.user

    # Tokens del usuario
    tokens = Token.objects.filter(user=user)

    # Separar tokens individuales y grupales
    tokens_ind = tokens.filter(token_type="INDIVIDUAL")
    tokens_grp = tokens.filter(token_type="GRUPAL")

    # ----------------------------
    # 1. REPORTES INDIVIDUALES VARK
    # ----------------------------
    reportes_ind = list(FormularioControlVark.objects.filter(token__in=tokens_ind))

    # ----------------------------
    # 2. REPORTES GRUPALES VARK (RESUMEN)
    # ----------------------------
    agrupados = (
        FormularioControlVark.objects
        .filter(token__in=tokens_grp)
        .values('token')
        .annotate(
            total_visual=Sum('resultado_visual'),
            total_auditivo=Sum('resultado_auditivo'),
            total_lectura=Sum('resultado_lectura_escritura'),
            total_kinest=Sum('resultado_kinestesico'),
            fecha=Max('fecha_completado')
        )
    )

    reportes_grp = []

    for r in agrupados:
        token_obj = Token.objects.get(id=r['token'])

        # Crear un “objeto reporte” compatible con el template
        class FakeReport:
            pass

        fr = FakeReport()
        fr.fecha_completado = r['fecha']
        fr.token = token_obj
        fr.alumno = type("AlumnoFake", (), {"nombre": f"Grupo {token_obj.token}"})
        fr.resultado_visual = r['total_visual']
        fr.resultado_auditivo = r['total_auditivo']
        fr.resultado_lectura_escritura = r['total_lectura']
        fr.resultado_kinestesico = r['total_kinest']

        reportes_grp.append(fr)

    # ----------------------------
    # 3. UNIFICAR LISTA FINAL
    # ----------------------------
    vark_reports = reportes_ind + reportes_grp

    # Ordenarlos por fecha (descendente)
    vark_reports.sort(key=lambda x: x.fecha_completado, reverse=True)


    # REPORTES INDIVIDUALES MBTI
    # ----------------------------
    mbti_reports = list(FormularioControlMBTI.objects.filter(token__in=tokens_ind))

    # REPORTES GRUPALES MBTI (RESUMEN)
    agrupados_mbti = (
        FormularioControlMBTI.objects
        .filter(token__in=tokens_grp)
        .values('token')
        .annotate(
            fecha=Max('fecha_completado')
        )
    )
    mbti_reports_grp = []

    for r in agrupados_mbti:
        token_obj = Token.objects.get(id=r['token'])

        # Crear un “objeto reporte” compatible con el template
        class FakeMBTIReport:
            pass

        fr = FakeMBTIReport()
        fr.fecha_completado = r['fecha']
        fr.token = token_obj
        fr.alumno = type("AlumnoFake", (), {"nombre": f"Grupo {token_obj.token}"})
        fr.tipo_resultante = "Varios"

        mbti_reports_grp.append(fr)

    mbti_reports += mbti_reports_grp

    return render(request, 'reports_list.html', {
        'vark_reports': vark_reports,
        'mbti_reports': mbti_reports
    })

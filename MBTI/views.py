from django.http import JsonResponse
from django.shortcuts import render
from .models import PreguntasMBTI, FormularioControlMBTI, MBTIDimension, MBTIRespuestaPregunta
from teachers.models import Alumno, Token
import re
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q

# Create your views here.
def mbti_test(request):
    preguntas = PreguntasMBTI.objects.all()
    context = {'preguntas': preguntas}
    return render(request, 'mbti_test.html', context)

def mbti_results(request):

    token = request.POST.get('token')
    name = request.POST.get('student_name')

    # Obtener token
    token_obj = Token.objects.filter(token=token).first()

    # Crear alumno
    alumno_obj = Alumno.objects.create(nombre=name, grupo=token_obj)

    # Crear control MBTI
    formulario_control = FormularioControlMBTI.objects.create(
        alumno=alumno_obj,
        token=token_obj
    )

    # -------------------------------
    # 1. Recolectar respuestas A/B
    # -------------------------------
    respuestas_temp = {}

    for key, value in request.POST.items():
        if key.startswith('q'):
            # Extraer número (ID de la pregunta)
            match = re.findall(r'\d+', key)
            if not match:
                continue

            pregunta_id = int(match[0])
            lado = 'A' if '_A' in key else 'B'

            if pregunta_id not in respuestas_temp:
                respuestas_temp[pregunta_id] = {}

            respuestas_temp[pregunta_id][lado] = int(value)

    # ----------------------------------------
    # 2. Guardar respuestas en la base de datos
    # ----------------------------------------
    for pregunta_id, vals in respuestas_temp.items():
        pregunta = PreguntasMBTI.objects.get(id=pregunta_id)

        MBTIRespuestaPregunta.objects.create(
            control=formulario_control,
            pregunta=pregunta,
            puntuacion_izquierda=vals.get('A', 0),
            puntuacion_derecha=vals.get('B', 0)
        )

    # ----------------------------------------
    # 3. Calcular el tipo MBTI resultante
    # ----------------------------------------
    dimensiones = {
        'E/I': 0,
        'S/N': 0,
        'T/F': 0,
        'J/P': 0
    }

    respuestas = MBTIRespuestaPregunta.objects.filter(control=formulario_control)

    for respuesta in respuestas:
        dim_code = f"{respuesta.pregunta.dimension_izq.code}/{respuesta.pregunta.dimension_der.code}"
        dimensiones[dim_code] += (
            respuesta.puntuacion_izquierda - respuesta.puntuacion_derecha
        )

    # Construir el tipo MBTI
    tipo_mbti = ''
    tipo_mbti += 'E' if dimensiones['E/I'] > 0 else 'I'
    tipo_mbti += 'S' if dimensiones['S/N'] > 0 else 'N'
    tipo_mbti += 'T' if dimensiones['T/F'] > 0 else 'F'
    tipo_mbti += 'J' if dimensiones['J/P'] > 0 else 'P'

    formulario_control.tipo_resultante = tipo_mbti
    formulario_control.energia = tipo_mbti[0]
    formulario_control.informacion = tipo_mbti[1]
    formulario_control.decisiones = tipo_mbti[2]
    formulario_control.estilo_vida = tipo_mbti[3]
    formulario_control.save()

    context = {
        'alumno': alumno_obj,
        'tipo_mbti': tipo_mbti,
        'dimensiones': dimensiones
    }

    return render(request, 'mbti_results.html', context)



@login_required
def dashboard_mbti(request):
    """Vista principal del dashboard MBTI"""
    user = request.user
    tokens = Token.objects.filter(user=user)
    
    # Obtener el filtro de la URL (por defecto: total)
    filtro = request.GET.get('filtro', 'total')
    token_id = request.GET.get('token_id', None)
    
    context = {
        'filtro': filtro,
        'tokens_individuales': tokens.filter(token_type="INDIVIDUAL"),
        'tokens_grupales': tokens.filter(token_type="GRUPAL"),
    }
    
    return render(request, 'dashboards/mbti_dashboard.html', context)


@login_required
def dashboard_mbti_data(request):
    """API endpoint para obtener datos del dashboard MBTI según filtros"""
    user = request.user
    filtro = request.GET.get('filtro', 'total')
    token_id = request.GET.get('token_id', None)
    
    tokens = Token.objects.filter(user=user)
    
    # Filtrar según tipo
    if filtro == 'individual':
        formularios = FormularioControlMBTI.objects.filter(token__in=tokens.filter(token_type="INDIVIDUAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    elif filtro == 'grupal':
        formularios = FormularioControlMBTI.objects.filter(token__in=tokens.filter(token_type="GRUPAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    else:  # total
        formularios = FormularioControlMBTI.objects.filter(token__in=tokens)
    
    # 1. Distribución por tipo MBTI (16 tipos)
    tipos_mbti = formularios.values('tipo_resultante').annotate(
        total=Count('id')
    ).order_by('-total')
    
    distribucion_tipos = {}
    for tipo in tipos_mbti:
        distribucion_tipos[tipo['tipo_resultante']] = tipo['total']
    
    # 2. Distribución por dimensiones individuales
    distribucion_energia = {
        'E': formularios.filter(energia='E').count(),
        'I': formularios.filter(energia='I').count()
    }
    
    distribucion_informacion = {
        'S': formularios.filter(informacion='S').count(),
        'N': formularios.filter(informacion='N').count()
    }
    
    distribucion_decisiones = {
        'T': formularios.filter(decisiones='T').count(),
        'F': formularios.filter(decisiones='F').count()
    }
    
    distribucion_estilo = {
        'J': formularios.filter(estilo_vida='J').count(),
        'P': formularios.filter(estilo_vida='P').count()
    }
    
    # 3. Agrupación por temperamentos (Keirsey)
    temperamentos = {
        'Guardianes (SJ)': formularios.filter(informacion='S', estilo_vida='J').count(),
        'Artesanos (SP)': formularios.filter(informacion='S', estilo_vida='P').count(),
        'Idealistas (NF)': formularios.filter(informacion='N', decisiones='F').count(),
        'Racionales (NT)': formularios.filter(informacion='N', decisiones='T').count()
    }
    
    # 4. Agrupación por roles (Analistas, Diplomáticos, Centinelas, Exploradores)
    roles = {
        'Analistas (INT)': formularios.filter(energia='I', informacion='N', decisiones='T').count(),
        'Diplomáticos (INF/ENF)': formularios.filter(Q(energia='I') | Q(energia='E'), informacion='N', decisiones='F').count(),
        'Centinelas (ISJ/ESJ)': formularios.filter(Q(energia='I') | Q(energia='E'), informacion='S', estilo_vida='J').count(),
        'Exploradores (ESP/ISP)': formularios.filter(Q(energia='I') | Q(energia='E'), informacion='S', estilo_vida='P').count()
    }
    
    # 5. Top 5 tipos más comunes
    top_tipos = list(tipos_mbti[:5])
    
    # 6. Evolución temporal
    evolucion = formularios.order_by('fecha_completado').values(
        'fecha_completado', 'tipo_resultante', 'energia', 'informacion', 
        'decisiones', 'estilo_vida'
    )[:20]
    
    # 7. Estadísticas generales
    total_formularios = formularios.count()
    
    # 8. Top estudiantes (solo individual)
    top_estudiantes = []
    if filtro == 'individual':
        estudiantes_data = formularios.values('alumno__nombre', 'tipo_resultante').annotate(
            total_tests=Count('id')
        ).order_by('-total_tests')[:5]
        
        top_estudiantes = list(estudiantes_data)
    
    return JsonResponse({
        'distribucion_tipos': distribucion_tipos,
        'distribucion_energia': distribucion_energia,
        'distribucion_informacion': distribucion_informacion,
        'distribucion_decisiones': distribucion_decisiones,
        'distribucion_estilo': distribucion_estilo,
        'temperamentos': temperamentos,
        'roles': roles,
        'top_tipos': top_tipos,
        'evolucion': list(evolucion),
        'total_formularios': total_formularios,
        'top_estudiantes': top_estudiantes
    })
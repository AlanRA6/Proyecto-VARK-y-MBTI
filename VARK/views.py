from django.http import JsonResponse
from django.shortcuts import render
from .models import PreguntaVark, VarkCategory, OpcionRespuesta, FormularioControlVark, RespuestaSeleccionada
from teachers.models import Alumno, Token
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Max


# Create your views here.
def vark_test(request):
    context = {}
    preguntas = PreguntaVark.objects.prefetch_related('opcionrespuesta_set').all()
    context['preguntas'] = preguntas
    return render(request, 'vark_test.html', context)

def vark_results(request):

    # Obtener token y estudiante del formulario
    try:
        token = request.POST.get('token')
        name = request.POST.get('student_name')

        token_obj = Token.objects.filter(token=token).first()
        alumno_obj = Alumno.objects.create(nombre=name, grupo=token_obj)  # Crear un nuevo alumno
        alumno_obj.save()

        # Crear el formulario de control VARK
        formulario_control = FormularioControlVark.objects.create(alumno=alumno_obj, token=token_obj)

        # Guardar las respuestas seleccionadas
        for key, value in request.POST.items():
            if key.startswith('q'):
                pregunta_id = int(key[1:])  # Extraer el ID de la pregunta

                pregunta = PreguntaVark.objects.get(id=pregunta_id)

                cat_code = value.split("(")[1].replace(")", "")

                categoria = VarkCategory.objects.get(code=cat_code)
                opcion_respuesta = OpcionRespuesta.objects.get(pregunta=pregunta, categoria=categoria)

                respuesta_seleccionada = RespuestaSeleccionada.objects.create(
                    control=formulario_control,
                    pregunta=pregunta,
                    opcion_respuesta=opcion_respuesta
                )
                respuesta_seleccionada.save()

        # Conteo de resultados
        category_counts = {'V': 0, 'A': 0, 'R': 0, 'K': 0}
        respuestas = RespuestaSeleccionada.objects.filter(control=formulario_control)
        for respuesta in respuestas:
            category_counts[respuesta.opcion_respuesta.categoria.code] += 1
        
        formulario_control.resultado_visual = category_counts['V']
        formulario_control.resultado_auditivo = category_counts['A']
        formulario_control.resultado_lectura_escritura = category_counts['R']
        formulario_control.resultado_kinestesico = category_counts['K']
        formulario_control.save()

        context = {
            'alumno': alumno_obj,
            'resultado_visual': formulario_control.resultado_visual,
            'resultado_auditivo': formulario_control.resultado_auditivo,
            'resultado_lectura_escritura': formulario_control.resultado_lectura_escritura,
            'resultado_kinestesico': formulario_control.resultado_kinestesico,
        }

        return render(request, 'vark_results.html', context)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


@login_required
def dashboard_vark(request):
    """Vista principal del dashboard VARK"""
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
    
    return render(request, 'dashboards/vark_dashboard.html', context)


@login_required
def dashboard_data(request):
    """API endpoint para obtener datos del dashboard según filtros"""
    user = request.user
    filtro = request.GET.get('filtro', 'total')
    token_id = request.GET.get('token_id', None)
    
    tokens = Token.objects.filter(user=user)
    
    # Filtrar según tipo
    if filtro == 'individual':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="INDIVIDUAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    elif filtro == 'grupal':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="GRUPAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    else:  # total
        formularios = FormularioControlVark.objects.filter(token__in=tokens)
    
    # 1. Totales por estilo de aprendizaje
    totales = formularios.aggregate(
        visual=Sum('resultado_visual'),
        auditivo=Sum('resultado_auditivo'),
        lectura=Sum('resultado_lectura_escritura'),
        kinestesico=Sum('resultado_kinestesico')
    )
    
    # 2. Promedios por estilo
    promedios = formularios.aggregate(
        visual=Avg('resultado_visual'),
        auditivo=Avg('resultado_auditivo'),
        lectura=Avg('resultado_lectura_escritura'),
        kinestesico=Avg('resultado_kinestesico')
    )
    
    # 3. Distribución de estilos dominantes
    distribucion = {'Visual': 0, 'Auditivo': 0, 'Lectura/Escritura': 0, 'Kinestésico': 0, 'Multimodal': 0}
    
    for f in formularios:
        max_valor = max(f.resultado_visual, f.resultado_auditivo, 
                       f.resultado_lectura_escritura, f.resultado_kinestesico)
        dominantes = []
        
        if f.resultado_visual == max_valor:
            dominantes.append('Visual')
        if f.resultado_auditivo == max_valor:
            dominantes.append('Auditivo')
        if f.resultado_lectura_escritura == max_valor:
            dominantes.append('Lectura/Escritura')
        if f.resultado_kinestesico == max_valor:
            dominantes.append('Kinestésico')
        
        if len(dominantes) > 1:
            distribucion['Multimodal'] += 1
        else:
            distribucion[dominantes[0]] += 1
    
    # 4. Evolución temporal (últimos resultados)
    evolucion = formularios.order_by('fecha_completado').values(
        'fecha_completado', 'resultado_visual', 'resultado_auditivo',
        'resultado_lectura_escritura', 'resultado_kinestesico'
    )[:20]
    
    # 5. Estadísticas generales
    total_formularios = formularios.count()
    
    # 6. Top 5 estudiantes (solo para vista individual)
    top_estudiantes = []
    if filtro == 'individual':
        estudiantes = formularios.values('alumno__nombre').annotate(
            total_puntos=Sum('resultado_visual') + Sum('resultado_auditivo') + 
                        Sum('resultado_lectura_escritura') + Sum('resultado_kinestesico'),
            visual=Avg('resultado_visual'),
            auditivo=Avg('resultado_auditivo'),
            lectura=Avg('resultado_lectura_escritura'),
            kinestesico=Avg('resultado_kinestesico')
        ).order_by('-total_puntos')[:5]
        
        top_estudiantes = list(estudiantes)
    
    return JsonResponse({
        'totales': totales,
        'promedios': {k: round(v, 2) if v else 0 for k, v in promedios.items()},
        'distribucion': distribucion,
        'evolucion': list(evolucion),
        'total_formularios': total_formularios,
        'top_estudiantes': top_estudiantes
    })
    """API endpoint para obtener datos del dashboard según filtros"""
    user = request.user
    filtro = request.GET.get('filtro', 'total')
    token_id = request.GET.get('token_id', None)
    
    tokens = Token.objects.filter(user=user)
    
    # Filtrar según tipo
    if filtro == 'individual':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="INDIVIDUAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    elif filtro == 'grupal':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="GRUPAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    else:  # total
        formularios = FormularioControlVark.objects.filter(token__in=tokens)
    
    # 1. Totales por estilo de aprendizaje
    totales = formularios.aggregate(
        visual=Sum('resultado_visual'),
        auditivo=Sum('resultado_auditivo'),
        lectura=Sum('resultado_lectura_escritura'),
        kinestesico=Sum('resultado_kinestesico')
    )
    
    # 2. Promedios por estilo
    promedios = formularios.aggregate(
        visual=Avg('resultado_visual'),
        auditivo=Avg('resultado_auditivo'),
        lectura=Avg('resultado_lectura_escritura'),
        kinestesico=Avg('resultado_kinestesico')
    )
    
    # 3. Distribución de estilos dominantes
    distribucion = {'Visual': 0, 'Auditivo': 0, 'Lectura/Escritura': 0, 'Kinestésico': 0, 'Multimodal': 0}
    
    for f in formularios:
        max_valor = max(f.resultado_visual, f.resultado_auditivo, 
                       f.resultado_lectura_escritura, f.resultado_kinestesico)
        dominantes = []
        
        if f.resultado_visual == max_valor:
            dominantes.append('Visual')
        if f.resultado_auditivo == max_valor:
            dominantes.append('Auditivo')
        if f.resultado_lectura_escritura == max_valor:
            dominantes.append('Lectura/Escritura')
        if f.resultado_kinestesico == max_valor:
            dominantes.append('Kinestésico')
        
        if len(dominantes) > 1:
            distribucion['Multimodal'] += 1
        else:
            distribucion[dominantes[0]] += 1
    
    # 4. Evolución temporal (últimos resultados)
    evolucion = formularios.order_by('fecha_completado').values(
        'fecha_completado', 'resultado_visual', 'resultado_auditivo',
        'resultado_lectura_escritura', 'resultado_kinestesico'
    )[:20]
    
    # 5. Estadísticas generales
    total_formularios = formularios.count()
    
    # 6. Top 5 estudiantes (solo para vista individual)
    top_estudiantes = []
    if filtro == 'individual':
        estudiantes = formularios.values('alumno__nombre').annotate(
            total_puntos=Sum('resultado_visual') + Sum('resultado_auditivo') + 
                        Sum('resultado_lectura_escritura') + Sum('resultado_kinestesico'),
            visual=Avg('resultado_visual'),
            auditivo=Avg('resultado_auditivo'),
            lectura=Avg('resultado_lectura_escritura'),
            kinestesico=Avg('resultado_kinestesico')
        ).order_by('-total_puntos')[:5]
        
        top_estudiantes = list(estudiantes)
    
    return JsonResponse({
        'totales': totales,
        'promedios': {k: round(v, 2) if v else 0 for k, v in promedios.items()},
        'distribucion': distribucion,
        'evolucion': list(evolucion),
        'total_formularios': total_formularios,
        'top_estudiantes': top_estudiantes
    })
    """API endpoint para obtener datos del dashboard según filtros"""
    user = request.user
    filtro = request.GET.get('filtro', 'total')
    token_id = request.GET.get('token_id', None)
    
    tokens = Token.objects.filter(user=user)
    
    # Filtrar según tipo
    if filtro == 'individual':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="INDIVIDUAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    elif filtro == 'grupal':
        formularios = FormularioControlVark.objects.filter(token__in=tokens.filter(token_type="GRUPAL"))
        if token_id:
            formularios = formularios.filter(token_id=token_id)
    else:  # total
        formularios = FormularioControlVark.objects.filter(token__in=tokens)
    
    # 1. Totales por estilo de aprendizaje
    totales = formularios.aggregate(
        visual=Sum('resultado_visual'),
        auditivo=Sum('resultado_auditivo'),
        lectura=Sum('resultado_lectura_escritura'),
        kinestesico=Sum('resultado_kinestesico')
    )
    
    # 2. Promedios por estilo
    promedios = formularios.aggregate(
        visual=Avg('resultado_visual'),
        auditivo=Avg('resultado_auditivo'),
        lectura=Avg('resultado_lectura_escritura'),
        kinestesico=Avg('resultado_kinestesico')
    )
    
    # 3. Distribución de estilos dominantes
    distribucion = {'Visual': 0, 'Auditivo': 0, 'Lectura/Escritura': 0, 'Kinestésico': 0, 'Multimodal': 0}
    
    for f in formularios:
        max_valor = max(f.resultado_visual, f.resultado_auditivo, 
                       f.resultado_lectura_escritura, f.resultado_kinestesico)
        dominantes = []
        
        if f.resultado_visual == max_valor:
            dominantes.append('Visual')
        if f.resultado_auditivo == max_valor:
            dominantes.append('Auditivo')
        if f.resultado_lectura_escritura == max_valor:
            dominantes.append('Lectura/Escritura')
        if f.resultado_kinestesico == max_valor:
            dominantes.append('Kinestésico')
        
        if len(dominantes) > 1:
            distribucion['Multimodal'] += 1
        else:
            distribucion[dominantes[0]] += 1
    
    # 4. Evolución temporal (últimos resultados)
    evolucion = formularios.order_by('fecha_completado').values(
        'fecha_completado', 'resultado_visual', 'resultado_auditivo',
        'resultado_lectura_escritura', 'resultado_kinestesico'
    )[:20]
    
    # 5. Estadísticas generales
    total_formularios = formularios.count()
    
    # 6. Top 5 estudiantes (solo para vista individual)
    top_estudiantes = []
    if filtro == 'individual':
        estudiantes = formularios.values('alumno__nombre').annotate(
            total_puntos=Sum('resultado_visual') + Sum('resultado_auditivo') + 
                        Sum('resultado_lectura_escritura') + Sum('resultado_kinestesico'),
            visual=Avg('resultado_visual'),
            auditivo=Avg('resultado_auditivo'),
            lectura=Avg('resultado_lectura_escritura'),
            kinestesico=Avg('resultado_kinestesico')
        ).order_by('-total_puntos')[:5]
        
        top_estudiantes = list(estudiantes)
    
    return JsonResponse({
        'totales': totales,
        'promedios': {k: round(v, 2) if v else 0 for k, v in promedios.items()},
        'distribucion': distribucion,
        'evolucion': list(evolucion),
        'total_formularios': total_formularios,
        'top_estudiantes': top_estudiantes
    })
from django.http import JsonResponse
from django.shortcuts import render
from .models import PreguntaVark, VarkCategory, OpcionRespuesta, FormularioControlVark, RespuestaSeleccionada
from teachers.models import Alumno, Token

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
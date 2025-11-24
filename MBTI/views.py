from django.http import JsonResponse
from django.shortcuts import render
from .models import PreguntasMBTI, FormularioControlMBTI, MBTIDimension, MBTIRespuestaPregunta
from teachers.models import Alumno, Token
import re

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
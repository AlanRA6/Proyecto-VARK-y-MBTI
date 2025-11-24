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
# Librerías de reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
from django.http import FileResponse

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

@login_required
def vark_individual_report(request, id):
    try:
        obj_exists = FormularioControlVark.objects.filter(id=id).exists()
        if not obj_exists:
            return JsonResponse({'error': 'Reporte no encontrado.'}, status=404)
        
        control_obj = FormularioControlVark.objects.get(id=id)
        
        respuestas = control_obj.respuestas.all()
        preguntas_y_respuestas = []
        for respuesta in respuestas:
            pregunta = respuesta.pregunta
            preguntas_y_respuestas.append({
                'pregunta': pregunta.texto,
                'opcion_seleccionada': respuesta.opcion_respuesta.inciso + ") " +  respuesta.opcion_respuesta.texto,
                'categoria': respuesta.opcion_respuesta.categoria.nombre
            })

        datos_pdf = {
            'alumno': str(control_obj.alumno), 
            'fecha': control_obj.fecha_completado.strftime("%d/%m/%Y"),
            'r_visual': control_obj.resultado_visual,
            'r_auditivo': control_obj.resultado_auditivo,
            'r_lect_escritura': control_obj.resultado_lectura_escritura,
            'r_kinestesico': control_obj.resultado_kinestesico,
            'preguntas_y_respuestas': preguntas_y_respuestas
        }

        buffer = io.BytesIO()
        generar_pdf_vark(buffer, datos_pdf)
        
        buffer.seek(0)

        filename = f"Reporte_VARK_{control_obj.alumno}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)
    except FormularioControlVark.DoesNotExist:
        return JsonResponse({'error': 'Reporte no encontrado.'}, status=404)
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return JsonResponse({'error': 'Error al generar el reporte.'}, status=500)

@login_required
def mbti_individual_report(request, id):

    try:
        obj_exists = FormularioControlMBTI.objects.filter(id=id).exists()
        if not obj_exists:
            return JsonResponse({'error': 'Reporte no encontrado.'}, status=404)
        
        control_obj = FormularioControlMBTI.objects.get(id=id)
        # Info general
        alumno = control_obj.alumno
        fecha_completado = control_obj.fecha_completado
        tipo_resultante = control_obj.tipo_resultante

        # Categorías
        energia = control_obj.energia
        informacion = control_obj.informacion
        decisiones = control_obj.decisiones
        estilo_vida = control_obj.estilo_vida

        # Obtener preguntas y respuestas
        respuestas = control_obj.respuestas.all()
        preguntas_y_respuestas = []
        for respuesta in respuestas:
            pregunta = respuesta.pregunta
            preguntas_y_respuestas.append({
                'pregunta': pregunta.texto,
                'puntuacion_izquierda': respuesta.puntuacion_izquierda,
                'puntuacion_derecha': respuesta.puntuacion_derecha,
                'dim_izq': pregunta.dimension_izq.nombre,
                'dim_der': pregunta.dimension_der.nombre
            })

        datos_pdf = {
            'alumno': str(alumno),
            'fecha': fecha_completado.strftime("%d/%m/%Y"),
            'tipo_resultante': tipo_resultante,
            'energia': str(energia), 
            'informacion': str(informacion),
            'decisiones': str(decisiones),
            'estilo_vida': str(estilo_vida),
            'preguntas_y_respuestas': preguntas_y_respuestas
        }

        buffer = io.BytesIO()
        generar_pdf_mbti(buffer, datos_pdf)
        buffer.seek(0)

        filename = f"Reporte_MBTI_{alumno}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)

    except FormularioControlMBTI.DoesNotExist:
        return JsonResponse({'error': 'Reporte no encontrado.'}, status=404)
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return JsonResponse({'error': 'Error al generar el reporte.'}, status=500)

def generar_pdf_vark(buffer, datos):
    """
    buffer: Objeto BytesIO o HttpResponse donde se escribirá el PDF.
    datos: Diccionario con la información del alumno y las respuestas.
    """
    # Configuración del documento
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    # Estilo para texto dentro de tablas (para que haga salto de línea automático)
    table_text_style = ParagraphStyle(
        'TableText', 
        parent=styles['Normal'], 
        fontSize=9, 
        leading=12
    )
    
    # Título
    elements.append(Paragraph("Reporte de Resultados VARK", title_style))
    elements.append(Spacer(1, 8))

    # Información del Alumno
    info_text = f"<b>Alumno:</b> {datos['alumno']}<br/><b>Fecha:</b> {datos['fecha']}"
    elements.append(Paragraph(info_text, normal_style))
    elements.append(Spacer(1, 8))

    # Tabla de Puntajes (V, A, R, K)
    data_puntajes = [
        ['Visual', 'Auditivo', 'Lectura/Escr.', 'Kinestésico'], # Encabezados
        [datos['r_visual'], datos['r_auditivo'], datos['r_lect_escritura'], datos['r_kinestesico']] # Valores
    ]

    t_puntajes = Table(data_puntajes, colWidths=[100, 100, 100, 100])
    t_puntajes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),       # Fondo gris encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco encabezado
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Centrar todo
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),    # Fuente negrita encabezado
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),             # Espacio extra encabezado
        ('GRID', (0, 0), (-1, -1), 1, colors.black),        # Bordes
    ]))
    elements.append(t_puntajes)
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("Detalle de Respuestas", styles['Heading2']))
    elements.append(Spacer(1, 8))

    # Encabezados de la tabla de preguntas
    table_data = [['Pregunta', 'Opción Seleccionada', 'Categoría']]

    # Llenado de filas
    for item in datos['preguntas_y_respuestas']:
        row = [
            Paragraph(item['pregunta'], table_text_style),
            Paragraph(item['opcion_seleccionada'], table_text_style),
            Paragraph(item['categoria'], table_text_style)
        ]
        table_data.append(row)

    # Creación de la tabla grande
    t_respuestas = Table(table_data, colWidths=[250, 180, 80])
    
    t_respuestas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), 
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))

    elements.append(t_respuestas)

    # Generar PDF
    doc.build(elements)


def generar_pdf_mbti(buffer, datos):
    """
    Genera un reporte PDF para resultados MBTI.
    """
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    # Un estilo grande y centrado para el resultado principal (Ej: INTJ)
    result_style = ParagraphStyle(
        'ResultStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1, # 0=Left, 1=Center, 2=Right
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    table_text_style = ParagraphStyle(
        'TableText', 
        parent=styles['Normal'], 
        fontSize=9, 
        leading=11
    )

    # --- ENCABEZADO ---
    elements.append(Paragraph("Reporte de Personalidad MBTI", styles['Heading1']))
    elements.append(Spacer(1, 10))

    info_text = f"<b>Alumno:</b> {datos['alumno']}<br/><b>Fecha:</b> {datos['fecha']}"
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # --- RESULTADO PRINCIPAL ---
    # Mostramos el tipo (ej. "ENFP") en grande
    elements.append(Paragraph(f"Tipo: {datos['tipo_resultante']}", result_style))
    elements.append(Spacer(1, 10))

    # --- TABLA DE DIMENSIONES (Resumen) ---
    # Mostramos las 4 dicotomías principales
    data_resumen = [
        ['Dimensión', 'Resultado / Preferencia'],
        ['Energía', datos['energia']],
        ['Información', datos['informacion']],
        ['Decisiones', datos['decisiones']],
        ['Estilo de Vida', datos['estilo_vida']],
    ]

    t_resumen = Table(data_resumen, colWidths=[150, 300])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (0, -1), colors.whitesmoke), # Columna izquierda gris claro
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 30))

    # --- DETALLE DE RESPUESTAS ---
    elements.append(Paragraph("Desglose de Respuestas", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Encabezados: Pregunta | Opción A (pts) | Opción B (pts)
    # Ajustamos para mostrar que hay dos lados en cada pregunta
    table_data = [['Pregunta', 'Dimensión A (Pts)', 'Dimensión B (Pts)']]

    for item in datos['preguntas_y_respuestas']:
        # Formateamos el texto para mostrar "NombreDimensión: Puntos"
        texto_izq = f"{item['dim_izq']}<br/><b>({item['puntuacion_izquierda']})</b>"
        texto_der = f"{item['dim_der']}<br/><b>({item['puntuacion_derecha']})</b>"

        row = [
            Paragraph(item['pregunta'], table_text_style),
            Paragraph(texto_izq, table_text_style), # Usamos paragraph para el salto de línea
            Paragraph(texto_der, table_text_style)
        ]
        table_data.append(row)

    # Tabla Detallada
    # Columna 1 ancha para la pregunta, 2 y 3 más angostas para los puntajes
    t_detalles = Table(table_data, colWidths=[260, 120, 120])
    
    t_detalles.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'), # Encabezados centrados
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Centrar las columnas de puntajes
    ]))

    elements.append(t_detalles)

    doc.build(elements)

def buscar_token(request, token, type):
    try:
        token_obj = Token.objects.filter(token=token).first()

        if not token_obj:
            return JsonResponse({'error': 'Token no encontrado.'}, status=404)

        # Obtener objetos de tests 
        if type == 'vark':
            reportes = FormularioControlVark.objects.filter(token=token_obj)
        elif type == 'mbti':
            reportes = FormularioControlMBTI.objects.filter(token=token_obj)
        else:
            return JsonResponse({'error': 'Tipo de test no válido.'}, status=400)
        
        reportes_data = []
        for reporte in reportes:
            reportes_data.append({
                'alumno': str(reporte.alumno),
                'fecha_completado': reporte.fecha_completado.strftime("%d/%m/%Y"),
                'id': reporte.id,
                'tipo': type
            })
        
        if not reportes_data:
            return JsonResponse({'error': 'No se encontraron reportes para este token.'}, status=404)
        
        return JsonResponse({'reportes': reportes_data}, status=200)

    except Exception as e:
        print(f"Error obteniendo reportes: {e}")
        return JsonResponse({'error': 'Error al encontrar el token.'}, status=500)

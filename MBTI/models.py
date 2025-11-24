from django.db import models
from teachers.models import Alumno

    
class MBTIDimension(models.Model):
    code = models.CharField(max_length=1, unique=True)  # E, I, S, N, T, F, J, P
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.code})"
    
    class Meta:
        verbose_name = "Dimensión MBTI"
        verbose_name_plural = "Dimensiones MBTI"

class PreguntasMBTI(models.Model):
    texto = models.CharField(max_length=255)
    dimension_izq = models.ForeignKey(MBTIDimension, on_delete=models.CASCADE, related_name='dim_left')
    dimension_der = models.ForeignKey(MBTIDimension, on_delete=models.CASCADE, related_name='dim_right')
    
    def __str__(self):
        return f"Pregunta {self.id} - {self.dimension_izq.code}/{self.dimension_der.code}"
    
    class Meta:
        verbose_name = "Pregunta MBTI"
        verbose_name_plural = "Preguntas MBTI"

class FormularioControlMBTI(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, null=True)
    fecha_completado = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Formulario MBTI {self.id} - {self.alumno}"
    
    class Meta:
        verbose_name = "Test MBTI"
        verbose_name_plural = "Tests MBTI"


class MBTIRespuestaPregunta(models.Model):
    control = models.ForeignKey(FormularioControlMBTI, on_delete=models.SET_NULL, null=True, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntasMBTI, on_delete=models.SET_NULL, null=True)
    puntuacion_izquierda = models.IntegerField()  # 0–10 por ejemplo E/S/T/J
    puntuacion_derecha = models.IntegerField()    # 0–10 por ejemplo I/N/F/P

    def __str__(self):
        return f"Resp {self.respuesta_encuesta.id} - Preg {self.pregunta.id}"
    
    class Meta:
        verbose_name = "Respuesta MBTI"
        verbose_name_plural = "Respuestas MBTI"


class MBTIResultado(models.Model):
    encuestado = models.ForeignKey(Alumno, on_delete=models.CASCADE, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    control = models.ForeignKey(FormularioControlMBTI, on_delete=models.SET_NULL, null=True)
    energia = models.CharField(max_length=1)     # E o I
    informacion = models.CharField(max_length=1) # S o N
    decisiones = models.CharField(max_length=1)  # T o F
    estilo_vida = models.CharField(max_length=1) # J o P

    tipo_resultante = models.CharField(max_length=4)  # ENFP, ISTJ, etc.

    def __str__(self):
        return f"{self.tipo_resultante} ({self.encuestado})"
    
    class Meta:
        verbose_name = "Resultado MBTI"
        verbose_name_plural = "Resultados MBTI"

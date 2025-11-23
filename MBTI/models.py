from django.db import models
from VARK.models import Pregunta, RespuestaEncuesta, Encuestado, Formulario


class MBTIDimension(models.Model):
    code = models.CharField(max_length=1, unique=True)  # E, I, S, N, T, F, J, P
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.code})"


class MBTIPreguntaDimension(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    dimension_izquierda = models.ForeignKey(
        MBTIDimension, on_delete=models.CASCADE, related_name='dim_left'
    )
    dimension_derecha = models.ForeignKey(
        MBTIDimension, on_delete=models.CASCADE, related_name='dim_right'
    )

    def __str__(self):
        return f"Preg {self.pregunta.id}: {self.dimension_izquierda.code} / {self.dimension_derecha.code}"


class MBTIRespuestaPregunta(models.Model):
    respuesta_encuesta = models.ForeignKey(RespuestaEncuesta, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)

    puntuacion_izquierda = models.IntegerField()  # 0–10 por ejemplo E/S/T/J
    puntuacion_derecha = models.IntegerField()    # 0–10 por ejemplo I/N/F/P

    def __str__(self):
        return f"Resp {self.respuesta_encuesta.id} - Preg {self.pregunta.id}"


class MBTIResultado(models.Model):
    encuestado = models.ForeignKey(Encuestado, on_delete=models.SET_NULL, null=True)
    formulario = models.ForeignKey(Formulario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    energia = models.CharField(max_length=1)     # E o I
    informacion = models.CharField(max_length=1) # S o N
    decisiones = models.CharField(max_length=1)  # T o F
    estilo_vida = models.CharField(max_length=1) # J o P

    tipo_resultante = models.CharField(max_length=4)  # ENFP, ISTJ, etc.

    def __str__(self):
        return f"{self.tipo_resultante} ({self.encuestado})"

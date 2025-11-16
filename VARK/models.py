from django.db import models
from django.contrib.auth.models import User


# -----------------------------
#   ENCUESTADO
# -----------------------------
class Encuestado(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    grupo = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.grupo})" if self.grupo else self.nombre


# -----------------------------
#   FORMULARIO
# -----------------------------
class Formulario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


# -----------------------------
#   PREGUNTA
# -----------------------------
class Pregunta(models.Model):
    texto = models.TextField()

    def __str__(self):
        return f"Pregunta {self.id}"


# -----------------------------
#   FORMULARIO-PREGUNTA (orden)
# -----------------------------
class FormularioPregunta(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    numero_pregunta = models.IntegerField()

    class Meta:
        ordering = ['numero_pregunta']

    def __str__(self):
        return f"{self.formulario.nombre} - Pregunta {self.numero_pregunta}"


# -----------------------------
#   CATEGORÍAS VARK
# -----------------------------
class VarkCategory(models.Model):
    code = models.CharField(max_length=1, unique=True)  # V, A, R, K
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.code})"


# -----------------------------
#   OPCIONES DE RESPUESTA
# -----------------------------
class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    inciso = models.CharField(max_length=1)  # A, B, C, D
    texto = models.TextField()
    categoria = models.ForeignKey(VarkCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pregunta.id}{self.inciso} - {self.texto[:40]}"


# -----------------------------
#   RESPUESTA ENCUESTA general
# -----------------------------
class RespuestaEncuesta(models.Model):
    encuestado = models.ForeignKey(Encuestado, on_delete=models.SET_NULL, null=True)
    formulario = models.ForeignKey(Formulario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuestas de {self.encuestado} - {self.fecha}"


# -----------------------------
#   RESPUESTAS SELECCIONADAS
# -----------------------------
class RespuestaSeleccionada(models.Model):
    respuesta_encuesta = models.ForeignKey(RespuestaEncuesta, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_respuesta = models.ForeignKey(OpcionRespuesta, on_delete=models.CASCADE)

    def __str__(self):
        return f"Resp {self.respuesta_encuesta.id} - Preg {self.pregunta.id} -> {self.opcion_respuesta.inciso}"

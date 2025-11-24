from django.db import models
from django.contrib.auth.models import User
from teachers.models import Alumno, Token


class PreguntaVark(models.Model):
    texto = models.TextField()

    def __str__(self):
        return f"Pregunta {self.id} - {self.texto}"
    
    class Meta:
        verbose_name = "Pregunta VARK"
        verbose_name_plural = "Preguntas VARK"

# -----------------------------
#   CATEGORÍAS VARK
# -----------------------------
class VarkCategory(models.Model):
    code = models.CharField(max_length=1, unique=True)  # V, A, R, K
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.code})"
    
    class Meta:
        verbose_name = "Categoría VARK"
        verbose_name_plural = "Categorías VARK"


# -----------------------------
#   OPCIONES VARK
# -----------------------------
class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(PreguntaVark, on_delete=models.CASCADE, null=True)
    inciso = models.CharField(max_length=1)  # A, B, C, D
    texto = models.TextField()
    categoria = models.ForeignKey(VarkCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.inciso} - {self.texto[:40]}"
    
    class Meta:
        verbose_name = "Opción VARK"
        verbose_name_plural = "Opciones VARK"

class FormularioControlVark(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_completado = models.DateTimeField(auto_now_add=True)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    resultado_visual = models.IntegerField(default=0)
    resultado_auditivo = models.IntegerField(default=0)
    resultado_lectura_escritura = models.IntegerField(default=0)
    resultado_kinestesico = models.IntegerField(default=0)

    def __str__(self):
        return f"Formulario {self.id} - {self.alumno.nombre} - {self.fecha_completado}"
    
    class Meta:
        verbose_name = "Test VARK"
        verbose_name_plural = "Tests VARK"

# -----------------------------
#   RESPUESTAS SELECCIONADAS
# -----------------------------
class RespuestaSeleccionada(models.Model):
    control = models.ForeignKey(FormularioControlVark, on_delete=models.CASCADE, null=True, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntaVark, on_delete=models.CASCADE, null=True)
    opcion_respuesta = models.ForeignKey(OpcionRespuesta, on_delete=models.CASCADE)

    def __str__(self):
        return f"Resp {self.opcion_respuesta.id} - Preg {self.pregunta.id} -> {self.opcion_respuesta.inciso}"
    
    class Meta:
        verbose_name = "Respuesta VARK"
        verbose_name_plural = "Respuestas VARK"

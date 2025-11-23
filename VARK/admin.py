from django.contrib import admin
from .models import (
    Encuestado,
    Formulario,
    Pregunta,
    FormularioPregunta,
    VarkCategory,
    OpcionRespuesta,
    RespuestaEncuesta,
    RespuestaSeleccionada
)

# -----------------------------
#   ENCUESTADO
# -----------------------------
@admin.register(Encuestado)
class EncuestadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "grupo")
    search_fields = ("nombre", "grupo")
    list_filter = ("grupo",)


# -----------------------------
#   FORMULARIO
# -----------------------------
@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


# -----------------------------
#   PREGUNTA
# -----------------------------
@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("id", "texto")
    search_fields = ("texto",)


# -----------------------------
#   FORMULARIO-PREGUNTA (orden)
# -----------------------------
@admin.register(FormularioPregunta)
class FormularioPreguntaAdmin(admin.ModelAdmin):
    list_display = ("id", "formulario", "pregunta", "numero_pregunta")
    list_filter = ("formulario",)
    ordering = ("formulario", "numero_pregunta")


# -----------------------------
#   CATEGORÍAS VARK
# -----------------------------
@admin.register(VarkCategory)
class VarkCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "nombre")
    search_fields = ("code", "nombre")


# -----------------------------
#   OPCIONES DE RESPUESTA
# -----------------------------
@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "pregunta", "inciso", "categoria", "texto_corto")
    list_filter = ("categoria", "pregunta")
    search_fields = ("texto",)

    def texto_corto(self, obj):
        return obj.texto[:50] + "..."
    texto_corto.short_description = "Texto"


# -----------------------------
#   RESPUESTA ENCUESTA
# -----------------------------
@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "encuestado", "formulario", "fecha")
    list_filter = ("formulario", "fecha")
    search_fields = ("encuestado__nombre",)


# -----------------------------
#   RESPUESTAS SELECCIONADAS
# -----------------------------
@admin.register(RespuestaSeleccionada)
class RespuestaSeleccionadaAdmin(admin.ModelAdmin):
    list_display = ("id", "respuesta_encuesta", "pregunta", "opcion_respuesta")
    list_filter = ("pregunta", "opcion_respuesta__categoria")
    search_fields = ("respuesta_encuesta__id",)

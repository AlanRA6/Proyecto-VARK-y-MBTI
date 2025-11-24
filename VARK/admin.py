from django.contrib import admin
from .models import (
    FormularioControlVark,
    PreguntaVark,
    VarkCategory,
    OpcionRespuesta,
    RespuestaSeleccionada
)


# -----------------------------
#   PREGUNTA
@admin.register(PreguntaVark)
class PreguntaVarkAdmin(admin.ModelAdmin):
    list_display = ("id", "texto")
    search_fields = ("texto",)

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
    list_filter = ("categoria",)
    search_fields = ("texto",)

    def texto_corto(self, obj):
        return obj.texto[:50] + "..."
    texto_corto.short_description = "Texto"


@admin.register(FormularioControlVark)
class FormularioControlVarkAdmin(admin.ModelAdmin):
    list_display = ("id", "alumno", "fecha_completado", "token", "resultado_visual", "resultado_auditivo", "resultado_lectura_escritura", "resultado_kinestesico")
    search_fields = ("alumno__nombre", "token__token")
    list_filter = ("fecha_completado",)

# -----------------------------
#   RESPUESTAS SELECCIONADAS
# -----------------------------
@admin.register(RespuestaSeleccionada)
class RespuestaSeleccionadaAdmin(admin.ModelAdmin):
    list_display = ("id", "control", "pregunta", "opcion_respuesta")
    list_filter = ("opcion_respuesta__categoria",)
    search_fields = ("control__id",)
from django.contrib import admin
from .models import (
    MBTIDimension,
    MBTIPreguntaDimension,
    MBTIRespuestaPregunta,
    MBTIResultado,
)


@admin.register(MBTIDimension)
class MBTIDimensionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "nombre")
    search_fields = ("code", "nombre")


@admin.register(MBTIPreguntaDimension)
class MBTIPreguntaDimensionAdmin(admin.ModelAdmin):
    list_display = ("id", "pregunta", "dimension_izquierda", "dimension_derecha")
    list_filter = ("dimension_izquierda", "dimension_derecha")
    search_fields = ("pregunta__texto",)


@admin.register(MBTIRespuestaPregunta)
class MBTIRespuestaPreguntaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "respuesta_encuesta",
        "pregunta",
        "puntuacion_izquierda",
        "puntuacion_derecha",
    )
    list_filter = ("pregunta",)
    search_fields = ("respuesta_encuesta__id",)


@admin.register(MBTIResultado)
class MBTIResultadoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "encuestado",
        "formulario",
        "fecha",
        "tipo_resultante",
        "energia",
        "informacion",
        "decisiones",
        "estilo_vida",
    )
    list_filter = ("tipo_resultante", "energia", "informacion", "decisiones", "estilo_vida")
    search_fields = ("encuestado__nombre", "tipo_resultante")

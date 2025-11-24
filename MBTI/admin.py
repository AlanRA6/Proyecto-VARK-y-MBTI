from django.contrib import admin
from .models import (
    PreguntasMBTI,
    FormularioControlMBTI,
    MBTIDimension,
    MBTIRespuestaPregunta,
    MBTIResultado,
)


@admin.register(PreguntasMBTI)
class PreguntasMBTIAdmin(admin.ModelAdmin):
    list_display = ("id", "texto", "dimension_izq", "dimension_der")
    search_fields = ("texto",)

@admin.register(FormularioControlMBTI)
class FormularioControlMBTIAdmin(admin.ModelAdmin):
    list_display = ("id", "alumno", "fecha_completado", "token")
    search_fields = ("alumno__nombre", "token")
    list_filter = ("fecha_completado",)


@admin.register(MBTIDimension)
class MBTIDimensionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "nombre")
    search_fields = ("code", "nombre")


@admin.register(MBTIRespuestaPregunta)
class MBTIRespuestaPreguntaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "control",
        "pregunta",
        "puntuacion_izquierda",
        "puntuacion_derecha",
    )
    list_filter = ()
    search_fields = ("control__id",)


@admin.register(MBTIResultado)
class MBTIResultadoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "encuestado",
        "fecha",
        "control",
        "tipo_resultante",
        "energia",
        "informacion",
        "decisiones",
        "estilo_vida",
    )
    list_filter = ("tipo_resultante", "energia", "informacion", "decisiones", "estilo_vida")
    search_fields = ("encuestado__nombre", "tipo_resultante")

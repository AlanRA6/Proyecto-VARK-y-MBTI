from django.contrib import admin
from .models import Token, Alumno
# Register your models here.
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "token_type", "created_at", "expires_at")
    search_fields = ("user__username", "token", "token_type")
    list_filter = ("token_type", "created_at", "expires_at")

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "grupo")
    search_fields = ("nombre", "grupo")
    list_filter = ("grupo",)



from django.contrib import admin
from .models import Curso, CategoriaAtividade, Aluno, Atividade, CursoCategoria

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(CategoriaAtividade)
class CategoriaAtividadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(CursoCategoria)
class CursoCategoriaAdmin(admin.ModelAdmin):
    list_display = ("curso", "categoria", "limite_horas")
    list_filter = ("curso", "categoria")

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("user", "curso")

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "aluno", "categoria", "horas", "data")

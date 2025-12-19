from django.contrib import admin
from .models import Curso, Categoria, Aluno, Atividade, CategoriaCurso

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ("curso", "categoria", "limite_horas")
    list_filter = ("curso", "categoria")

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("user", "curso")

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "aluno", "categoria", "horas", "data")

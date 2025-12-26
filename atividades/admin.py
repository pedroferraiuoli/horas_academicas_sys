from django.contrib import admin
from .models import Curso, Categoria, Aluno, Atividade, CategoriaCurso, CursoPorSemestre, Semestre

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome",)

@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ("curso_semestre", "categoria", "limite_horas")
    list_filter = ("curso_semestre", "categoria")

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("user", "curso")

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "aluno", "categoria", "horas", "data")

@admin.register(CursoPorSemestre)
class CursoPorSemestreAdmin(admin.ModelAdmin):
    list_display = ("curso", "semestre", "horas_requeridas")
    list_filter = ("curso", "semestre")

@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ("nome", "data_inicio", "data_fim")

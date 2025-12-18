from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.forms import ValidationError

from atividades.validators import ValidadorDeArquivo, ValidadorDeHoras

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True

class Semestre(BaseModel):
    nome = models.CharField(max_length=20)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome

class CategoriaAtividade(BaseModel):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Curso(BaseModel):
    nome = models.CharField(max_length=100)
    horas_requeridas = models.PositiveIntegerField(help_text="Horas totais necessárias para conclusão do curso")

    def __str__(self):
        return self.nome
    
class CursoCategoria(BaseModel):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='curso_categorias')
    categoria = models.ForeignKey('CategoriaAtividade', on_delete=models.CASCADE, related_name='curso_categorias')
    limite_horas = models.PositiveIntegerField(help_text="Limite máximo de horas para esta categoria neste curso")
    equivalencia_horas = models.CharField(max_length=50, help_text="Equivalência de horas (e.g., 1h = 1h)", null=True, blank=True, default="1h = 1h")
    semestre = models.ForeignKey('Semestre', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('curso', 'categoria', 'semestre')

    def __str__(self):
        return f"{self.curso.nome} - {self.categoria.nome} (Limite: {self.limite_horas}h) - {self.semestre.nome}"
    
    def ultrapassou_limite_pelo_aluno(self, aluno):
        total_horas = (
            aluno.atividades
            .filter(categoria=self)
            .aggregate(total=Sum('horas'))['total']
            or 0
        )
        return total_horas > self.limite_horas
    
class Coordenador(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coordenador')
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Coordenador de {self.curso.nome}"

class Aluno(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='alunos')
    semestre_ingresso = models.ForeignKey('Semestre', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.semestre_ingresso})"
    
    def horas_complementares_validas(self, apenas_aprovadas=False):
        total = 0
        if not self.curso:
            return 0
        
        from atividades.selectors import CursoCategoriaSelectors
        categorias = CursoCategoriaSelectors.get_curso_categorias_por_semestre_curso(
            self.curso,
            semestre=self.semestre_ingresso
        )

        for curso_categoria in categorias:
            atividades = self.atividades.filter(categoria=curso_categoria)

            if apenas_aprovadas:
                soma = sum(a.horas_aprovadas or 0 for a in atividades if a.horas_aprovadas is not None)
            else:
                soma = sum(a.horas for a in atividades)

            limite = curso_categoria.limite_horas or 0

            total += min(soma, limite) if limite > 0 else soma

        return total

class Atividade(BaseModel):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atividades')
    categoria = models.ForeignKey(CursoCategoria, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    observacoes_para_aprovador = models.TextField(blank=True, null=True)
    horas = models.PositiveIntegerField(help_text="Duração da atividade em horas")
    horas_aprovadas = models.PositiveIntegerField(null=True, blank=True)
    data = models.DateField()
    documento = models.FileField(upload_to='comprovantes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.aluno})"
    
    def clean(self):

        ValidadorDeArquivo.validar(self.documento)
        ValidadorDeHoras.validar_horas(self.horas, self.horas_aprovadas)
        
        return super().clean()
    
    def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
        self.clean()
        return super().save(force_insert, force_update, using, update_fields)
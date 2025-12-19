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

class Categoria(BaseModel):
    nome = models.CharField(max_length=100)
    especifica = models.BooleanField(default=False, help_text="Indica se a categoria é específica para algum curso")

    def __str__(self):
        return self.nome

class Curso(BaseModel):
    nome = models.CharField(max_length=100)
    horas_requeridas = models.PositiveIntegerField(help_text="Horas totais necessárias para conclusão do curso")

    def __str__(self):
        return self.nome
    
class CategoriaCurso(BaseModel):
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='categorias_curso')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='categorias')
    limite_horas = models.PositiveIntegerField(help_text="Limite máximo de horas para esta categoria neste curso")
    equivalencia_horas = models.CharField(max_length=50, help_text="Equivalência de horas (e.g., 1h = 1h)", null=True, blank=True, default="1h = 1h")
    semestre = models.ForeignKey('Semestre', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('curso', 'categoria', 'semestre')

    def __str__(self):
        return f"{self.curso.nome} - {self.categoria.nome} (Limite: {self.limite_horas}h) - {self.semestre.nome}"
    
    def ultrapassou_limite_pelo_aluno(self, aluno):
        from atividades.selectors import AtividadeSelectors
        total_horas = AtividadeSelectors.get_total_horas_por_aluno_categoria(
            aluno=aluno,
            curso_categoria=self
        )
        return total_horas > self.limite_horas
    
    def atingiu_limite_pelo_aluno(self, aluno):
        from atividades.selectors import AtividadeSelectors
        total_horas = AtividadeSelectors.get_total_horas_por_aluno_categoria(
            aluno=aluno,
            curso_categoria=self
        )
        return total_horas >= self.limite_horas
    
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

class Atividade(BaseModel):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atividades')
    categoria = models.ForeignKey(CategoriaCurso, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    observacoes_para_aprovador = models.TextField(blank=True, null=True)
    horas = models.PositiveIntegerField(help_text="Duração da atividade em horas")
    horas_aprovadas = models.PositiveIntegerField(null=True, blank=True)
    data = models.DateField()
    documento = models.FileField(upload_to='comprovantes/', null=True, blank=True)

    @property
    def status(self):
        if self.categoria.atingiu_limite_pelo_aluno(self.aluno) and self.horas_aprovadas is None:
            return 'Limite Atingido'
        if self.horas_aprovadas is None:
            return 'Aguardando'
        if self.horas_aprovadas == 0:
            return 'Rejeitada'    
        return f'{self.horas_aprovadas}h'

    def __str__(self):
        return f"{self.nome} ({self.aluno})"
    
    
    def clean(self):
        if self.documento:
            ValidadorDeArquivo.validar(self.documento)
        ValidadorDeHoras.validar_horas(self.horas, self.horas_aprovadas)
        
        return super().clean()
    
    def save(self):
        self.clean()
        return super().save()
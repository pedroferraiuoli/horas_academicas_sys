from django.db import models
from django.contrib.auth.models import User
from atividades.validators import ValidadorDeArquivo, ValidadorDeHoras
from django.utils.formats import date_format

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True

class Semestre(BaseModel):
    nome = models.CharField(max_length=20)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['data_inicio', 'data_fim'], name='semestre_periodo_idx'),
        ]

    def __str__(self):
        inicio = date_format(self.data_inicio, "F/Y") if self.data_inicio else ''
        fim = date_format(self.data_fim, "F/Y") if self.data_fim else ''
        return f"{self.nome} ({inicio} até {fim})"

class Categoria(BaseModel):
    nome = models.CharField(max_length=100)
    especifica = models.BooleanField(default=False, help_text="Indica se a categoria é específica para algum curso")

    def __str__(self):
        return self.nome

class Curso(BaseModel):
    nome = models.CharField(max_length=100)
    horas_requeridas = models.PositiveIntegerField(help_text="Horas totais necessárias para conclusão do curso. (Será aplicado somente para novos semestres!)")
    
    def __str__(self):
        return self.nome
    
class CursoPorSemestre(BaseModel):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='configuracoes_semestre')
    semestre = models.ForeignKey(Semestre, on_delete=models.PROTECT)
    horas_requeridas = models.PositiveIntegerField(
        help_text="Horas totais necessárias neste semestre"
    )
    
    class Meta:
        unique_together = ('curso', 'semestre')
        indexes = [
            models.Index(fields=['curso', 'semestre'], name='curso_semestre_idx'),
        ]
    
    def __str__(self):
        return f"{self.curso.nome} - {self.semestre.nome} ({self.horas_requeridas}h)"
    
class CategoriaCurso(BaseModel):
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='categorias_curso')
    limite_horas = models.PositiveIntegerField(help_text="Limite máximo de horas para esta categoria neste curso")
    equivalencia_horas = models.CharField(max_length=50, help_text="Equivalência de horas (e.g., 1h = 1h)", null=True, blank=True, default="1h = 1h")
    curso_semestre = models.ForeignKey(CursoPorSemestre, on_delete=models.CASCADE, related_name='categorias_curso')
    class Meta:
        unique_together = ('curso_semestre', 'categoria')
        indexes = [
            models.Index(fields=['curso_semestre', 'categoria'], name='cat_curso_semestre_idx'),
        ]

    def __str__(self):
        return f"{self.categoria.nome} ({self.limite_horas}h)"
    
    def ultrapassou_limite_pelo_aluno(self, aluno):
        from atividades.selectors import AtividadeSelectors
        total_horas = AtividadeSelectors.get_total_horas_aluno(
            aluno=aluno,
            categoria=self,
            apenas_aprovadas=True
        )
        return total_horas > self.limite_horas
    
    def atingiu_limite_pelo_aluno(self, aluno):
        from atividades.selectors import AtividadeSelectors
        total_horas = AtividadeSelectors.get_total_horas_aluno(
            aluno=aluno,
            categoria=self,
            apenas_aprovadas=True
        )
        return total_horas >= self.limite_horas
    
class Coordenador(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coordenador')
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Coordenador de {self.curso.nome}"

class Aluno(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, help_text="Nome completo do aluno")
    matricula = models.CharField(max_length=20, unique=True, help_text="Matrícula do aluno")
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='alunos')
    semestre_ingresso = models.ForeignKey('Semestre', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['matricula'], name='aluno_matricula_idx'),
        ]

    def __str__(self):
        return f"{self.nome} - {self.matricula} ({self.semestre_ingresso})"

class Atividade(BaseModel):

    status_choices = [
        ('Pendente', 'Pendente'),
        ('Aprovada', 'Aprovada'),
        ('Rejeitada', 'Rejeitada'),
        ('Limite Atingido', 'Limite Atingido'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atividades')
    categoria = models.ForeignKey(CategoriaCurso, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    observacoes_para_aprovador = models.TextField(blank=True, null=True)
    horas = models.PositiveIntegerField(help_text="Duração da atividade em horas")
    horas_aprovadas = models.PositiveIntegerField(null=True, blank=True)
    data = models.DateField()
    documento = models.FileField(upload_to='comprovantes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=status_choices, default='Pendente')

    class Meta:
        indexes = [
            models.Index(fields=['aluno', 'categoria'], name='ativ_aluno_cat_idx'),
            models.Index(fields=['aluno', 'status'], name='ativ_aluno_status_idx'),
        ]

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
    
class Notificacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.CharField(max_length=255)
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
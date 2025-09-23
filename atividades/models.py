from math import modf
from django.db import models
from django.contrib.auth.models import User

class CategoriaAtividade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    horas_requeridas = models.DecimalField(max_digits=5, decimal_places=2, help_text="Horas totais necessárias para conclusão do curso", default=0)

    def horas_requeridas_formatada(self):
        fracao_decimal, parte_inteira = modf(float(self.horas_requeridas))
        minutos = round(fracao_decimal * 60)
        return f"{int(parte_inteira)}:{minutos:02d}h"

    def __str__(self):
        return self.nome
    
class CursoCategoria(models.Model):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='curso_categorias')
    categoria = models.ForeignKey('CategoriaAtividade', on_delete=models.CASCADE, related_name='curso_categorias')
    limite_horas = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Limite máximo de horas para esta categoria neste curso")
    carga_horaria = models.CharField(max_length=50, help_text="Carga horária do curso (e.g., 2000h)", null=True, blank=True, default="1h = 1h")


    class Meta:
        unique_together = ('curso', 'categoria')

    def __str__(self):
        return f"{self.curso.nome} - {self.categoria.nome} (Limite: {self.limite_horas}h)"
    
    def limite_horas_formatado(self):
        fracao_decimal, parte_inteira = modf(float(self.limite_horas))
        minutos = round(fracao_decimal * 60)
        return f"{int(parte_inteira)}:{minutos:02d}h"
    
    def ultrapassou_limite_pelo_aluno(self, aluno):
        atividades = aluno.atividade_set.filter(categoria=self)
        total_horas = sum(float(a.horas) for a in atividades)
        return total_horas > float(self.limite_horas)

class Coordenador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coordenador')
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Coordenador de {self.curso.nome}"

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)


    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def horas_complementares_validas(self):
        total = 0
        if not self.curso:
            return 0
        # Para cada categoria vinculada ao curso, busca o vínculo CursoCategoria
        for cat in self.curso.curso_categorias.all():
            categoria = cat.categoria
            atividades = self.atividade_set.filter(categoria=cat)
            soma = sum(float(a.horas) for a in atividades)
            try:
                curso_categoria = CursoCategoria.objects.get(curso=self.curso, categoria=categoria)
                limite = float(curso_categoria.limite_horas)
            except CursoCategoria.DoesNotExist:
                limite = 0
            if limite > 0:
                total += min(soma, limite)
            else:
                total += soma
        return total
    
    def horas_complementares_validas_formatado(self):
        fracao_decimal, parte_inteira = modf(float(self.horas_complementares_validas()))
        minutos = round(fracao_decimal * 60)
        return f"{int(parte_inteira)}:{minutos:02d}h"

class Atividade(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CursoCategoria, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    data = models.DateField()
    documento = models.FileField(upload_to='comprovantes/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.aluno})"
    
    def horas_formatada(self):
        fracao_decimal, parte_inteira = modf(float(self.horas))
        minutos = round(fracao_decimal * 60)
        return f"{int(parte_inteira)}:{minutos:02d}h"

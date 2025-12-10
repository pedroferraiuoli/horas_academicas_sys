from math import modf
from django.db import models, transaction
from django.contrib.auth.models import User

class Semestre(models.Model):
    nome = models.CharField(max_length=20)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome
    
    @staticmethod
    def get_semestre_atual():
        from django.utils import timezone
        hoje = timezone.now().date()
        semestre_atual = Semestre.objects.filter(
            data_inicio__lte=hoje,
            data_fim__gte=hoje
        ).first()
        return semestre_atual
    
    def duplicate_categories_from(self, source_semestre):
        if source_semestre is None or source_semestre.id == self.id:
            return 0

        to_create = []
        with transaction.atomic():
            origem_qs = CursoCategoria.objects.filter(semestre=source_semestre).select_related('categoria', 'curso')
            cursos_por_id = {}
            for cc in origem_qs:
                cursos_por_id.setdefault(cc.curso_id, []).append(cc)

            for curso_id, curso_categorias in cursos_por_id.items():
                # ids já existentes no semestre destino para este curso
                existing_cat_ids = set(
                    CursoCategoria.objects.filter(curso_id=curso_id, semestre=self).values_list('categoria_id', flat=True)
                )
                for cc in curso_categorias:
                    if cc.categoria_id in existing_cat_ids:
                        continue
                    to_create.append(CursoCategoria(
                        curso_id=curso_id,
                        categoria_id=cc.categoria_id,
                        limite_horas=cc.limite_horas,
                        equivalencia_horas=cc.equivalencia_horas,
                        semestre=self
                    ))

            if to_create:
                CursoCategoria.objects.bulk_create(to_create)
        return len(to_create)

class CategoriaAtividade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    horas_requeridas = models.IntegerField(help_text="Horas totais necessárias para conclusão do curso")

    def __str__(self):
        return self.nome
    
    def get_categorias(self, semestre=None):
        if semestre:
            return self.curso_categorias.filter(semestre=semestre).select_related('categoria').all()
        return self.curso_categorias.select_related('categoria').all()
    
    
class CursoCategoria(models.Model):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='curso_categorias')
    categoria = models.ForeignKey('CategoriaAtividade', on_delete=models.CASCADE, related_name='curso_categorias')
    limite_horas = models.IntegerField(help_text="Limite máximo de horas para esta categoria neste curso")
    equivalencia_horas = models.CharField(max_length=50, help_text="Equivalência de horas (e.g., 1h = 1h)", null=True, blank=True, default="1h = 1h")
    semestre = models.ForeignKey('Semestre', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('curso', 'categoria', 'semestre')

    def __str__(self):
        return f"{self.curso.nome} - {self.categoria.nome} (Limite: {self.limite_horas}h) - {self.semestre.nome}"
    
    def ultrapassou_limite_pelo_aluno(self, aluno):
        atividades = aluno.atividades.filter(categoria=self)
        total_horas = sum(a.horas for a in atividades)
        return total_horas > self.limite_horas
    
    @staticmethod
    def get_curso_categorias(curso=None, semestre=None):
        qs = CursoCategoria.objects.all()
        if curso:
            qs = qs.filter(curso=curso)
        if semestre:
            qs = qs.filter(semestre=semestre)
        return qs
    


class Coordenador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coordenador')
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Coordenador de {self.curso.nome}"

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    semestre_ingresso = models.ForeignKey('Semestre', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.semestre_ingresso})"

    def horas_complementares_validas(self, apenas_aprovadas=None):
        total = 0
        if not self.curso:
            return 0
        # Para cada categoria vinculada ao curso, busca o vínculo CursoCategoria
        for cat in self.curso.get_categorias(semestre=self.semestre_ingresso):
            categoria = cat.categoria
            atividades = self.atividades.filter(categoria=cat)
            if apenas_aprovadas:
                soma = sum(a.horas_aprovadas or 0 for a in atividades if a.horas_aprovadas is not None)
            else:
                soma = sum(a.horas for a in atividades)
            try:
                curso_categoria = CursoCategoria.objects.get(curso=self.curso, categoria=categoria, semestre=self.semestre_ingresso)
                limite = curso_categoria.limite_horas
            except CursoCategoria.DoesNotExist:
                limite = 0
            if limite > 0:
                total += min(soma, limite)
            else:
                total += soma
        return total

class Atividade(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='atividades')
    categoria = models.ForeignKey(CursoCategoria, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    observacoes_para_aprovador = models.TextField(blank=True, null=True)
    horas = models.IntegerField(help_text="Duração da atividade em horas")
    horas_aprovadas = models.IntegerField(null=True, blank=True)
    data = models.DateField()
    documento = models.FileField(upload_to='comprovantes/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.aluno})"

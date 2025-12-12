import django_filters
from .models import Atividade, CursoCategoria, Semestre, Aluno
from django import forms
from django.db.models import Exists, OuterRef, Q


class CursoCategoriaFilter(django_filters.FilterSet):
    semestre = django_filters.ModelChoiceFilter(queryset=Semestre.objects.all(), label='Semestre', empty_label='Todos', widget=forms.Select(attrs={
            'class': 'form-select',   # coloque as classes que quiser
        }))

    class Meta:
        model = CursoCategoria
        fields = ['semestre']

class AlunosFilter(django_filters.FilterSet):
    semestre_ingresso = django_filters.ModelChoiceFilter(queryset=Semestre.objects.all(), label='Semestre', empty_label='Todos', widget=forms.Select(attrs={
            'class': 'form-select',
        }))
    tem_horas_a_validar = django_filters.ChoiceFilter(
        choices=(
            ('1', 'Com pendências'),
            ('0', 'Sem pendências'),
        ),
        label='Pendências',
        method='filter_tem_horas_a_validar',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todos"
    )

    class Meta:
        model = Aluno
        fields = ['semestre_ingresso', 'tem_horas_a_validar']


    def filter_tem_horas_a_validar(self, queryset, name, value):
        # se nenhum valor enviado, não filtra
        if not value:
            return queryset

        # subquery: existe atividade desse aluno com horas_aprovadas IS NULL ?
        pendencias_qs = Atividade.objects.filter(
            aluno_id=OuterRef('pk'),
            horas_aprovadas__isnull=True
        )

        # anota cada aluno com booleano tem_pendencia
        queryset = queryset.annotate(tem_pendencia=Exists(pendencias_qs))

        if str(value) == '1':
            return queryset.filter(tem_pendencia=True)
        if str(value) == '0':
            return queryset.filter(tem_pendencia=False)

        return queryset
    
class AtividadesFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=(
            ('1', 'Aprovadas'),
            ('0', 'Aguardando'),
        ),
        label='Status',
        method='filter_atividades_status',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas"
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CursoCategoria.objects.none(),
        label='Categorias',
        empty_label='Todas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Atividade
        fields = ['status', 'categoria']

    @property
    def aluno(self):
        req = getattr(self, 'request', None)
        if req and req.user.is_authenticated:
            return getattr(req.user, 'aluno', None)
        return None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        aluno = self.aluno

        if aluno:
            self.filters['categoria'].queryset = CursoCategoria.objects.filter(
                curso=aluno.curso,
                semestre=aluno.semestre_ingresso
            )


    def filter_atividades_status(self, queryset, name, value):
        if not value:
            return queryset

        # Aprovadas
        if value == '1':
            return queryset.filter(horas_aprovadas__isnull=False)

        # Aguardando
        if value == '0':
            return queryset.filter(horas_aprovadas__isnull=True)

        return queryset



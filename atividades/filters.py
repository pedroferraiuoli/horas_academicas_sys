import django_filters
from django.contrib.auth.models import User
from atividades.selectors import AlunoSelectors, CategoriaCursoSelectors, UserSelectors
from .models import Atividade, Curso, CategoriaCurso, Semestre, Aluno
from django import forms
from django.db.models import Q


class CategoriaCursoFilter(django_filters.FilterSet):
    semestre = django_filters.ModelChoiceFilter(queryset=Semestre.objects.all(), label='Semestre', empty_label='Todos', widget=forms.Select(attrs={
            'class': 'form-select',   # coloque as classes que quiser
        }))
    
    curso = django_filters.ModelChoiceFilter(queryset=Curso.objects.all(), label='Curso', empty_label='Todos', widget=forms.Select(attrs={
            'class': 'form-select',
        }))
    
    especifica = django_filters.BooleanFilter(
        field_name='categoria__especifica',
        label='Categorias',
        widget=forms.Select(choices=(
            ('', 'Todas'),
            ('true', 'Apenas Específicas'),
            ('false', 'Apenas Gerais'),
        ), attrs={'class': 'form-select'})
    )

    nome = django_filters.CharFilter(
        method='filtrar_nome',
        label='Nome',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por nome...'}
        )
    )

    class Meta:
        model = CategoriaCurso
        fields = ['semestre', 'curso', 'especifica']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
    
        if user and UserSelectors.is_user_coordenador(user):
            self.filters.pop('curso')

    def filtrar_nome(self, queryset, name, value):
        return queryset.filter(
            categoria__nome__icontains=value
        )

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

    nome = django_filters.CharFilter(
        method='filtrar_nome',
        label='Nome',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por nome...'}
        )
    )

    class Meta:
        model = Aluno
        fields = ['semestre_ingresso', 'tem_horas_a_validar', 'nome']

    def filtrar_nome(self, queryset, name, value):
        return queryset.filter(
            nome__icontains=value)

    def filter_tem_horas_a_validar(self, queryset, name, value):
        # se nenhum valor enviado, não filtra
        if not value:
            return queryset

        # anota cada aluno com booleano tem_pendencia
        queryset = AlunoSelectors._with_pendencia_annotation(queryset)

        if str(value) == '1':
            return queryset.filter(tem_pendencia=True)
        if str(value) == '0':
            return queryset.filter(tem_pendencia=False)

        return queryset
    
class AtividadesFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=(
            ('1', 'Aprovadas'),
            ('2', 'Rejeitadas'),
            ('0', 'Pendentes'),
        ),
        label='Status',
        method='filter_atividades_status',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas"
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaCurso.objects.none(),
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
            return AlunoSelectors.get_aluno_by_user(req.user)
        return None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        aluno = self.aluno

        if aluno:
            self.filters['categoria'].queryset = CategoriaCursoSelectors.get_categorias_curso(
                curso=aluno.curso,
                semestre=aluno.semestre_ingresso
            )


    def filter_atividades_status(self, queryset, name, value):
        if not value:
            return queryset

        # Aprovadas
        if value == '1':
            return queryset.filter(status='Aprovada')
        
        # Rejeitadas
        if value == '2':
            return queryset.filter(status='Rejeitada')

        # Pendentes
        if value == '0':
            return queryset.filter(status='Pendente')

        return queryset
    
class AtividadesCoordenadorFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=(
            ('1', 'Aprovadas'),
            ('2', 'Rejeitadas'),
            ('0', 'Pendentes'),
        ),
        label='Status',
        method='filter_atividades_status',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas"
    )

    nome_aluno = django_filters.CharFilter(
        method='filtrar_nome_aluno',
        label='Nome do Aluno',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por nome do aluno...'}
        )
    )

    matricula_aluno = django_filters.CharFilter(
        method='filtrar_matricula_aluno',
        label='Matrícula do Aluno',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por matrícula do aluno...'}
        )
    )

    aluno_id = django_filters.NumberFilter(widget=forms.HiddenInput(), method='filter_aluno_id')

    class Meta:
        model = Atividade
        fields = ['status', 'nome_aluno', 'aluno_id']

    def filter_aluno_id(self, queryset, name, value):
        return queryset.filter(aluno__id=value)

    def filtrar_nome_aluno(self, queryset, name, value):
        return queryset.filter(
            aluno__nome__icontains=value
        )
    
    def filtrar_matricula_aluno(self, queryset, name, value):
        return queryset.filter(
            aluno__matricula__icontains=value
        )
    
    def filter_atividades_status(self, queryset, name, value):
        if not value:
            return queryset

        # Aprovadas
        if value == '1':
            return queryset.filter(status='Aprovada')
        
        # Rejeitadas
        if value == '2':
            return queryset.filter(status='Rejeitada')

        # Pendentes
        if value == '0':
            return queryset.filter(status='Pendente')
        return queryset
    
    def __init__ (self, *args, aluno_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if aluno_id:
            self.filters.pop('nome_aluno')
            self.filters.pop('matricula_aluno')

        if not aluno_id:
            self.filters.pop('aluno_id')
            self.filters.pop('status')


class CursoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        method='filtrar_nome',
        label='Nome',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por nome...'}
        )
    )

    class Meta:
        model = Curso
        fields = ['nome']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
    
        if user and UserSelectors.is_user_coordenador(user):
            self.filters.pop('curso')

    def filtrar_nome(self, queryset, name, value):
        return queryset.filter(
            nome__icontains=value
        )
    
class CategoriaFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        method='filtrar_nome',
        label='Nome',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por nome...'}
        )
    )

    class Meta:
        model = CategoriaCurso
        fields = ['nome']

    def filtrar_nome(self, queryset, name, value):
        return queryset.filter(
            nome__icontains=value
        )
    
class UsuarioFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        method='filtrar_username',
        label='Username',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Buscar por username...'}
        )
    )

    class Meta:
        model = User
        fields = ['nome']

    def filtrar_username(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )
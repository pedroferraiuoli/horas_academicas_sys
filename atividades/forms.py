import re
from atividades.selectors import CategoriaCursoSelectors, SemestreSelectors, UserSelectors
from atividades.validators import ValidadorDeArquivo, ValidadorDeHoras, ValidadorDeNome
from .models import Curso, CategoriaCurso, Semestre, Categoria, Atividade, Aluno
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User

class SemestreForm(forms.ModelForm): 

    class Meta:
        model = Semestre
        fields = ['nome', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}, format='%d/%m/%Y'),
            'data_fim': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}, format='%d/%m/%Y')
        }

class AlterarEmailForm(forms.ModelForm):
    email = forms.EmailField(label='Novo e-mail', max_length=254)
    email_confirm = forms.EmailField(label='Confirme o novo e-mail', max_length=254)

    class Meta:
        model = User
        fields = ['email', 'email_confirm']

    def clean_email_confirm(self):
        email = self.cleaned_data.get('email')
        email_confirm = self.cleaned_data.get('email_confirm')
        if email and email_confirm and email != email_confirm:
            raise forms.ValidationError('Os e-mails não coincidem.')
        return email_confirm

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este e-mail já está em uso por outro usuário.')
        return email
    
class AdminUserForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput)
    tipo = forms.ChoiceField(choices=[('gestor', 'Gestor'), ('coordenador', 'Coordenador')], label='Tipo de usuário')
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso (apenas para Coordenador)', required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('As senhas não coincidem.')
        return cd.get('password2')

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        curso = cleaned_data.get('curso')
        if tipo == 'coordenador' and not curso:
            self.add_error('curso', 'Selecione o curso para o coordenador.')
        return cleaned_data

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome', 'horas_requeridas']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do curso'}),
            'horas_requeridas': forms.NumberInput(attrs={'placeholder': 'Horas requeridas para conclusão'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da categoria'})
        }

class CategoriaCursoForm(forms.ModelForm):

    class Meta:
        model = CategoriaCurso
        fields = ['curso', 'categoria', 'limite_horas', 'semestre']


    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not user:
            return

        coordenador = getattr(user, 'coordenador', None)

        if coordenador:
            self.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso_id)
            self.fields['curso'].initial = coordenador.curso

            semestre_atual = SemestreSelectors.get_semestre_atual()

            self.fields['categoria'].queryset = (CategoriaCursoSelectors.get_categorias_curso_disponiveis_para_associar(
                    coordenador.curso,
                    semestre_atual
                )
            )


class AtividadeForm(forms.ModelForm):

    class Meta:
        model = Atividade
        fields = ['categoria', 'nome', 'descricao', 'horas', 'data', 'documento', 'observacoes_para_aprovador']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}, format='%d/%m/%Y'),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'observacoes_para_aprovador': forms.Textarea(attrs={'rows': 4}),
            'documento': forms.ClearableFileInput(attrs={'accept': (
            '.pdf,'
            'application/pdf,'
            '.jpg,.jpeg,'
            'image/jpeg,'
            '.png,'
            'image/png,'
            '.doc,'
            'application/msword,'
            '.docx,'
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
                }
            )
        }

    def __init__(self, *args, aluno=None, categoria_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if aluno:
            categorias = CategoriaCursoSelectors.get_categorias_curso(curso=aluno.curso, semestre=aluno.semestre_ingresso)
            self.fields['categoria'].queryset = categorias

        if categoria_id:
            try:
                categoria = CategoriaCurso.objects.get(id=categoria_id)
                self.fields['categoria'].initial = categoria
            except CategoriaCurso.DoesNotExist:
                pass
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            ValidadorDeArquivo.validar(documento)
        return documento
    
    def clean_horas(self):
        horas = self.cleaned_data.get('horas')
        ValidadorDeHoras.validar_horas(horas)
        return horas

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Matrícula ou E-mail')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Se contém @, é email - busca o username correspondente
            if '@' in username:
                user_qs = User.objects.filter(email__iexact=username)
                if user_qs.exists():
                    # Usa o username do usuário encontrado
                    self.cleaned_data['username'] = user_qs.first().username
            else:
                # Se não tem @, trata como matrícula (que é o username)
                # Apenas garante case-insensitive
                user_qs = User.objects.filter(username__iexact=username)
                if user_qs.exists():
                    self.cleaned_data['username'] = user_qs.first().username
        
        return super().clean()

class UserRegistrationForm(forms.Form):
    nome = forms.CharField(label='Nome Completo', max_length=200, required=True)
    matricula = forms.CharField(label='Matrícula', max_length=50, required=True, widget=forms.NumberInput(attrs={'placeholder': 'Ex: 2023001234'}))
    email = forms.EmailField(label='E-mail', required=True)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput, required=True)
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso de Graduação', required=True)
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), label='Semestre de Ingresso')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('As senhas não coincidem.')
        return cd.get('password2')
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula and not matricula.isdigit():
            raise forms.ValidationError('A matrícula deve conter apenas números.')
        if Aluno.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Esta matrícula já está cadastrada.')
        if User.objects.filter(username=matricula).exists():
            raise forms.ValidationError('Esta matrícula já está em uso.')
        return matricula
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        ValidadorDeNome.validar_nome(nome)
        return nome

class CategoriaCursoDiretaForm(forms.Form):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso')
    nome = forms.CharField(label='Nome da categoria', max_length=100)
    limite_horas = forms.IntegerField(label='Limite de horas', min_value=0)
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), label='Semestre')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if UserSelectors.is_user_coordenador(user=user):
            coordenador = UserSelectors.get_coordenador_by_user(user)
            self.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso_id)
            self.fields['curso'].initial = coordenador.curso

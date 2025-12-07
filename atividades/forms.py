from django.contrib.auth.models import Group
from .models import Curso, CursoCategoria
from .models import CategoriaAtividade
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import Aluno, Curso, Semestre
from .models import Atividade, CategoriaAtividade

class SemestreForm(forms.ModelForm): 

    class Meta:
        model = Semestre
        fields = ['nome', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
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
    horas_requeridas_int = forms.IntegerField(label='Horas requeridas', min_value=0, required=False, initial=0)
    minutos_requeridos_int = forms.IntegerField(label='Minutos requeridos', min_value=0, max_value=59, required=False, initial=0)

    class Meta:
        model = Curso
        fields = ['nome', 'horas_requeridas_int', 'minutos_requeridos_int']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            horas = int(self.instance.horas_requeridas)
            minutos = int(round((self.instance.horas_requeridas - horas) * 60))
            self.fields['horas_requeridas_int'].initial = horas
            self.fields['minutos_requeridos_int'].initial = minutos

    def clean(self):
        cleaned_data = super().clean()
        horas = cleaned_data.get('horas_requeridas_int') or 0
        minutos = cleaned_data.get('minutos_requeridos_int') or 0
        cleaned_data['horas_requeridas'] = horas + (minutos / 60)
        return cleaned_data

    def save(self, commit=True):
        self.instance.horas_requeridas = self.cleaned_data['horas_requeridas']
        return super().save(commit=commit)

class CategoriaAtividadeForm(forms.ModelForm):

    class Meta:
        model = CategoriaAtividade
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da categoria'})
        }

class CategoriaCursoForm(forms.ModelForm):
    limite_horas_int = forms.IntegerField(label='Limite de Horas', min_value=0, required=False, initial=0)
    limite_minutos_int = forms.IntegerField(label='Limite de Minutos', min_value=0, max_value=59, required=False, initial=0)
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), label='Semestre')

    class Meta:
        model = CursoCategoria
        fields = ['curso', 'categoria', 'limite_horas_int', 'limite_minutos_int', 'semestre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            horas = int(self.instance.limite_horas)
            minutos = int(round((self.instance.limite_horas - horas) * 60))
            self.fields['limite_horas_int'].initial = horas
            self.fields['limite_minutos_int'].initial = minutos

    def clean(self):
        cleaned_data = super().clean()
        horas = cleaned_data.get('limite_horas_int') or 0
        minutos = cleaned_data.get('limite_minutos_int') or 0
        cleaned_data['limite_horas'] = horas + (minutos / 60)
        return cleaned_data

    def save(self, commit=True):
        self.instance.limite_horas = self.cleaned_data['limite_horas']
        return super().save(commit=commit)

class AtividadeForm(forms.ModelForm):
    horas_int = forms.IntegerField(label='Horas', min_value=0, required=False, initial=0)
    minutos_int = forms.IntegerField(label='Minutos', min_value=0, max_value=59, required=False, initial=0)

    class Meta:
        model = Atividade
        fields = ['categoria', 'nome', 'descricao', 'horas_int', 'minutos_int', 'data', 'documento']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }

    def __init__(self, *args, **kwargs):
        aluno = kwargs.pop('aluno', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            horas = int(self.instance.horas)
            minutos = int(round((self.instance.horas - horas) * 60))
            self.fields['horas_int'].initial = horas
            self.fields['minutos_int'].initial = minutos
        if aluno:
            categorias = aluno.curso.curso_categorias.all()
            self.fields['categoria'].queryset = categorias

    def clean(self):
        cleaned_data = super().clean()
        horas = cleaned_data.get('horas_int') or 0
        minutos = cleaned_data.get('minutos_int') or 0
        cleaned_data['horas'] = horas + (minutos / 60)
        return cleaned_data

    def save(self, commit=True):
        self.instance.horas = self.cleaned_data['horas']
        return super().save(commit=commit)

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuário ou Email')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            # Tenta autenticar por username (case insensitive)
            user_qs = User.objects.filter(username__iexact=username)
            if user_qs.exists():
                # Garante que o username usado é o correto (case insensitive)
                self.cleaned_data['username'] = user_qs.first().username
            else:
                # Se não existe username, tenta por email (case insensitive)
                user_qs_email = User.objects.filter(email__iexact=username)
                if user_qs_email.exists():
                    self.cleaned_data['username'] = user_qs_email.first().username
        return super().clean()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput)
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso de Graduação')
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), label='Semestre de Ingresso')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('As senhas não coincidem.')
        return cd.get('password2')

class CategoriaCursoDiretaForm(forms.Form):
    nome = forms.CharField(label='Nome da categoria', max_length=100)
    limite_horas = forms.DecimalField(label='Limite de horas', max_digits=5, decimal_places=2, min_value=0)
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), label='Semestre')

    def save(self, coordenador):
        categoria = CategoriaAtividade.objects.create(nome=self.cleaned_data['nome'])
        curso_categoria = CursoCategoria.objects.create(
            curso=coordenador.curso,
            categoria=categoria,
            limite_horas=self.cleaned_data['limite_horas'],
            semestre=self.cleaned_data['semestre']
        )
        return curso_categoria


import datetime
import re
import magic
from django.core.exceptions import ValidationError

class AtividadeValidators:
    
    @staticmethod
    def validar_arquivo(arquivo):
        MIME_PERMITIDOS = {
            'application/pdf',
            'image/jpeg',
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }

        TAMANHO_MAXIMO_MB = 15
        TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024

        # valida tamanho
        if arquivo.size > TAMANHO_MAXIMO_BYTES:
            raise ValidationError(
                f'O arquivo excede o tamanho máximo permitido de {TAMANHO_MAXIMO_MB} MB.'
            )

        # valida mime
        mime = magic.from_buffer(arquivo.read(2048), mime=True)
        arquivo.seek(0)

        if mime not in MIME_PERMITIDOS:
            raise ValidationError('Tipo de arquivo inválido.')
    
    @staticmethod
    def validar_horas(horas: int, horas_aprovadas: int = None):
        if horas <= 0 or horas is None:
            raise ValidationError('A quantidade de horas deve ser maior que zero.')
        if horas_aprovadas is not None:
            if horas_aprovadas < 0:
                raise ValidationError('A quantidade de horas aprovadas não pode ser negativa.')
            if horas_aprovadas > horas:
                raise ValidationError('As horas aprovadas não podem exceder as horas da atividade.')
            
class AlunoValidators:
    
    @staticmethod
    def validar_nome(nome: str):

        nome = re.sub(r'\s+', ' ', nome)

        partes = nome.split(' ')
        if len(partes) < 2:
            raise ValidationError('Informe nome e sobrenome.')

        for parte in partes:
            if len(parte) < 2:
                raise ValidationError(
                    'Cada parte do nome deve ter ao menos 2 letras.'
                )

        if re.search(r'\d', nome):
            raise ValidationError(
                'O nome não pode conter números.'
            )

        if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ ]+$', nome):
            raise ValidationError(
                'O nome não pode conter símbolos especiais.'
            )

        nome = ' '.join(p.capitalize() for p in partes)

        return nome
    
    @staticmethod
    def validar_matricula(matricula: str):
        if not matricula.isdigit():
            raise ValidationError('A matrícula deve conter apenas números.')
        
        MATRICULA_REGEX = r'^\d{11}$'
        if not re.match(MATRICULA_REGEX, matricula):
            raise ValidationError(
                "Matrícula deve conter exatamente 11 dígitos numéricos."
            )
       
        ano = int(matricula[:4])
        ano_atual = datetime.now().year

        if ano < 2000 or ano > ano_atual + 1:
            raise ValidationError("Ano da matrícula inválido.")
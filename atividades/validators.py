import magic
from django.core.exceptions import ValidationError


class ValidadorDeArquivo:
    MIME_PERMITIDOS = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]

    TAMANHO_MAXIMO_MB = 15
    TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024

    @classmethod
    def validar(cls, arquivo):
        cls._validar_tamanho(arquivo)
        cls._validar_mime(arquivo)

    @classmethod
    def _validar_tamanho(cls, arquivo):
        if arquivo.size > cls.TAMANHO_MAXIMO_BYTES:
            raise ValidationError(
                f'O arquivo excede o tamanho máximo permitido de {cls.TAMANHO_MAXIMO_MB} MB.'
            )

    @classmethod
    def _validar_mime(cls, arquivo):
        mime = magic.from_buffer(arquivo.read(2048), mime=True)
        arquivo.seek(0)

        if mime not in cls.MIME_PERMITIDOS:
            raise ValidationError('Tipo de arquivo inválido.')

class ValidadorDeHoras:
    
    @staticmethod
    def validar_horas(horas: int, horas_aprovadas: int = None):
        if horas <= 0 or horas is None:
            raise ValidationError('A quantidade de horas deve ser maior que zero.')
        if horas_aprovadas is not None:
            if horas_aprovadas < 0:
                raise ValidationError('A quantidade de horas aprovadas não pode ser negativa.')
            if horas_aprovadas > horas:
                raise ValidationError('As horas aprovadas não podem exceder as horas da atividade.')
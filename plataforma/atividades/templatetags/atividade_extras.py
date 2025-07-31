from math import modf
from django import template

register = template.Library()

@register.filter
def categoria_horas(atividades, categoria):
    horas = sum(a.horas for a in atividades if a.categoria == categoria)
    fracao_decimal, parte_inteira = modf(float(horas))
    minutos = round(fracao_decimal * 60)
    return f"{int(parte_inteira)}:{minutos:02d}h"

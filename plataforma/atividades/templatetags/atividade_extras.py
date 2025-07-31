from django import template

register = template.Library()

@register.filter
def categoria_horas(atividades, categoria):
    return sum(a.horas for a in atividades if a.categoria == categoria)

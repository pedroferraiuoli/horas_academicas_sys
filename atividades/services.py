from gettext import translation
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Aluno, Curso, Coordenador, CursoCategoria, Semestre
from django.db import transaction
    
class SemestreService:

    @staticmethod
    def criar_semestre_com_copia(form, copiar_de_id):
        if copiar_de_id and copiar_de_id != 'Nenhum':
            source_semestre = Semestre.objects.filter(id=copiar_de_id).first()
            if source_semestre:           
                SemestreService.duplicate_categories_from(form, source_semestre)
                return True          
        return False
    
    @staticmethod
    def duplicate_categories_from(semestre_novo, source_semestre):
        if source_semestre is None or source_semestre.id == semestre_novo.id:
            return False

        to_create = []
        with transaction.atomic():
            origem_qs = CursoCategoria.objects.filter(semestre=source_semestre).select_related('categoria', 'curso')
            cursos_por_id = {}
            for cc in origem_qs:
                cursos_por_id.setdefault(cc.curso_id, []).append(cc)

            for curso_id, curso_categorias in cursos_por_id.items():
                # ids já existentes no semestre destino para este curso
                existing_cat_ids = set(
                    CursoCategoria.objects.filter(curso_id=curso_id, semestre=semestre_novo).values_list('categoria_id', flat=True)
                )
                for cc in curso_categorias:
                    if cc.categoria_id in existing_cat_ids:
                        continue
                    to_create.append(CursoCategoria(
                        curso_id=curso_id,
                        categoria_id=cc.categoria_id,
                        limite_horas=cc.limite_horas,
                        equivalencia_horas=cc.equivalencia_horas,
                        semestre=semestre_novo
                    ))

            if to_create:
                CursoCategoria.objects.bulk_create(to_create)
                return True
        return False

class RegisterService:

    def register_user_with_aluno(form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        Aluno.objects.create(
            user=user,
            curso=form.cleaned_data['curso'],
            semestre_ingresso=form.cleaned_data['semestre'],
        )

        return user

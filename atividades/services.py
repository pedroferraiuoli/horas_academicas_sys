from atividades.selectors import AtividadeSelectors, CategoriaCursoSelectors, UserSelectors
from .models import Aluno, Atividade, Categoria, Coordenador, CategoriaCurso, Semestre
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Sum, QuerySet
from django.core.cache import cache

    
class SemestreService:

    @staticmethod
    def criar_semestre_com_copia(*, form, copiar_de_id):
        if copiar_de_id and copiar_de_id != 'Nenhum':
            source_semestre = Semestre.objects.filter(id=copiar_de_id).first()
            if source_semestre:           
                SemestreService.duplicate_categories_from(semestre_novo=form, source_semestre=source_semestre)
                return True          
        return False
    
    @staticmethod
    def duplicate_categories_from(*, semestre_novo, source_semestre):
        if source_semestre is None or source_semestre.id == semestre_novo.id:
            return False

        to_create = []
        with transaction.atomic():
            origem_qs = CategoriaCurso.objects.filter(semestre=source_semestre).select_related('categoria', 'curso')
            cursos_por_id = {}
            for cc in origem_qs:
                cursos_por_id.setdefault(cc.curso_id, []).append(cc)

            for curso_id, curso_categorias in cursos_por_id.items():
                # ids já existentes no semestre destino para este curso
                existing_cat_ids = set(
                    CategoriaCurso.objects.filter(curso_id=curso_id, semestre=semestre_novo).values_list('categoria_id', flat=True)
                )
                for cc in curso_categorias:
                    if cc.categoria_id in existing_cat_ids:
                        continue
                    to_create.append(CategoriaCurso(
                        curso_id=curso_id,
                        categoria_id=cc.categoria_id,
                        limite_horas=cc.limite_horas,
                        equivalencia_horas=cc.equivalencia_horas,
                        semestre=semestre_novo
                    ))

            if to_create:
                CategoriaCurso.objects.bulk_create(to_create)
                return True
        return False

class UserService:

    @staticmethod
    def register_user_with_aluno(*, form):
        from django.contrib.auth.models import User
        
        # Criar usuário usando matrícula como username
        matricula = form.cleaned_data['matricula']
        user = User.objects.create_user(
            username=matricula,  # Matrícula é o username nos bastidores
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )

        Aluno.objects.create(
            user=user,
            nome=form.cleaned_data['nome'],
            matricula=matricula,
            curso=form.cleaned_data['curso'],
            semestre_ingresso=form.cleaned_data['semestre'],
        )

        return user

    @staticmethod
    def criar_usuario_admin(*, form):
        """
        Cria usuário gestor ou coordenador com base no formulário
        """
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        tipo = form.cleaned_data['tipo']

        if tipo == 'gestor':
            grupo = Group.objects.get(name='Gestor')
            user.groups.add(grupo)

        elif tipo == 'coordenador':
            grupo = Group.objects.get(name='Coordenador')
            user.groups.add(grupo)

            curso = form.cleaned_data['curso']
            Coordenador.objects.create(
                user=user,
                curso=curso
            )

        return user
    
    @staticmethod
    def toggle_user_active_status(*, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return user
    
class AtividadeService:

    @staticmethod
    def invalidar_cache_aluno(aluno_id: int):
        """Invalida o cache de categorias para um aluno específico"""
        cache_key = f'categorias_aluno_{aluno_id}'
        cache.delete(cache_key)

    @staticmethod
    def aprovar_horas(*, atividade: Atividade, horas_aprovadas: int):
        
        if horas_aprovadas is None:
            raise ValueError('Informe a quantidade de horas.')
        
        if horas_aprovadas < 0:
            raise ValueError('Horas negativas não são permitidas')

        if horas_aprovadas > atividade.horas:
            raise ValueError('Horas aprovadas não podem exceder as horas da atividade')
        
        if atividade.status == 'Limite Atingido':
            raise ValueError('Não é possível aprovar horas para esta atividade, o limite da categoria já foi atingido.')
        
        if atividade.categoria.atingiu_limite_pelo_aluno(atividade.aluno) and atividade.horas_aprovadas is None:
            raise ValueError('Não é possível aprovar horas para esta atividade, o limite da categoria já foi atingido para este aluno.')

        atividade.horas_aprovadas = horas_aprovadas
        atividade.save()
        
        # Invalidar cache do aluno após aprovação
        AtividadeService.invalidar_cache_aluno(atividade.aluno_id)
        AtividadeService.recalcular_status_atividade(atividade=atividade)

    @staticmethod
    def recalcular_status_atividades_qs(atividades: QuerySet[Atividade]):
        for atividade in atividades:
            if atividade.categoria.atingiu_limite_pelo_aluno(atividade.aluno):
                atividade.status = 'Limite Atingido'
            elif atividade.horas_aprovadas is None:
                atividade.status = 'Pendente'
            elif atividade.horas_aprovadas == 0:
                atividade.status = 'Rejeitada'
            else:
                atividade.status = 'Aprovada' 
            atividade.save()

    @staticmethod
    def recalcular_status_atividade(atividade: Atividade):
        if atividade.horas_aprovadas is not None and atividade.horas_aprovadas > 0:
            atividade.status = 'Aprovada'
        else:
            atividade.status = 'Rejeitada'
        atividade.save()
        atividades = AtividadeSelectors.get_atividades_aluno(
            aluno=atividade.aluno,
            curso_categoria=atividade.categoria,
            aprovadas=False
        ).exclude(id=atividade.id)
        AtividadeService.recalcular_status_atividades_qs(atividades=atividades)

    @staticmethod
    def recalcular_status_atividades_apos_exclusao(aluno: Aluno, categoria: CategoriaCurso):
        atividades = AtividadeSelectors.get_atividades_aluno(
            aluno=aluno,
            curso_categoria=categoria,
            limite_atingido=True
        )
        AtividadeService.recalcular_status_atividades_qs(atividades=atividades)

    @staticmethod
    def exluir_atividade(atividade: Atividade):
        aluno = atividade.aluno
        categoria = atividade.categoria
        atividade.delete()
        AtividadeService.recalcular_status_atividades_apos_exclusao(aluno=aluno, categoria=categoria)
        AtividadeService.invalidar_cache_aluno(aluno.id)

    @staticmethod
    def cadastrar_atividade(*, form, aluno: Aluno):
        atividade = form.save(commit=False)
        atividade.aluno = aluno
        if atividade.categoria.atingiu_limite_pelo_aluno(aluno):
            atividade.status = 'Limite Atingido'
        atividade.save()
        AtividadeService.invalidar_cache_aluno(aluno.id)
        return atividade

class CategoriaCursoService:
   
   @staticmethod
   def create_categoria_curso_especifica(*, form, user: User):
        curso = form.cleaned_data['curso']

        if UserSelectors.is_user_coordenador(user):
            coordenador = UserSelectors.get_coordenador_by_user(user)
            if coordenador.curso != curso:
                raise ValueError('Coordenador só pode criar categorias para seu próprio curso.')
            
        categoria = Categoria.objects.create(nome=form.cleaned_data['nome'], especifica=True)
        curso_categoria = CategoriaCurso.objects.create(
            curso=form.cleaned_data['curso'],
            categoria=categoria,
            limite_horas=form.cleaned_data['limite_horas'],
            semestre=form.cleaned_data['semestre']
        )
        return curso_categoria
   
   @staticmethod
   def associar_categorias(*, curso, semestre, dados_post):
        """
        Associa categorias selecionadas ao curso no semestre específico.
        Processa apenas as categorias marcadas no formulário.
        """
        categorias_selecionadas = []
        
        # Extrair apenas as categorias marcadas do POST
        for key, value in dados_post.items():
            if key.startswith('cat_') and value == 'on':
                try:
                    categoria_id = int(key.replace('cat_', ''))
                    limite_key = f'horas_{categoria_id}'
                    limite = dados_post.get(limite_key, '0')
                    
                    # Validar limite de horas
                    try:
                        limite = int(limite)
                    except ValueError:
                        continue
                    
                    if limite <= 0:
                        continue
                    
                    categorias_selecionadas.append({
                        'categoria_id': categoria_id,
                        'limite_horas': limite
                    })
                except (ValueError, AttributeError):
                    continue
        
        if not categorias_selecionadas:
            raise ValueError('Nenhuma categoria válida foi selecionada. Marque as categorias e informe um limite de horas maior que zero.')
        
        # Verificar se as categorias selecionadas estão disponíveis para este curso/semestre
        categorias_disponiveis_ids = set(
            CategoriaCursoSelectors.get_categorias_curso_disponiveis_para_associar(
                curso=curso,
                semestre=semestre
            ).values_list('id', flat=True)
        )
        
        # Criar as associações em batch
        to_create = []
        for item in categorias_selecionadas:
            if item['categoria_id'] not in categorias_disponiveis_ids:
                continue  # Ignora categorias já associadas ou inválidas
            
            to_create.append(CategoriaCurso(
                curso=curso,
                categoria_id=item['categoria_id'],
                limite_horas=item['limite_horas'],
                semestre=semestre
            ))
        
        if not to_create:
            raise ValueError('As categorias selecionadas já estão associadas a este curso.')
        
        # Criar todas de uma vez (bulk_create é mais eficiente)
        CategoriaCurso.objects.bulk_create(to_create)
        
        return len(to_create)
   
class AlunoService:

    @staticmethod
    def calcular_horas_complementares_validas(
        *,
        aluno: Aluno,
        apenas_aprovadas: bool = False,
        categoria: CategoriaCurso = None
    ) -> int:
        if not aluno.curso:
            return 0
        
        if categoria:
            soma = AtividadeSelectors.get_total_horas_aluno(
                aluno=aluno,
                categoria=categoria,
                apenas_aprovadas=apenas_aprovadas
            )

            limite = categoria.limite_horas or 0
            total = min(soma, limite) if limite > 0 else soma
            return total

        categorias = CategoriaCursoSelectors.get_categorias_curso(
            curso=aluno.curso,
            semestre=aluno.semestre_ingresso
        )

        total = 0

        for curso_categoria in categorias:
            soma = AtividadeSelectors.get_total_horas_aluno(
                aluno=aluno,
                categoria=curso_categoria,
                apenas_aprovadas=apenas_aprovadas
            )

            limite = curso_categoria.limite_horas or 0
            total += min(soma, limite) if limite > 0 else soma

        return total
    

class RelatorioAlunoService:

    @staticmethod
    def gerar_dados_relatorio(*, aluno):
        categorias = CategoriaCursoSelectors.get_categorias_curso(
            curso=aluno.curso,
            semestre=aluno.semestre_ingresso
        )

        categorias_dados = []

        for categoria in categorias:
            atividades = AtividadeSelectors.get_atividades_aluno(
                aluno=aluno,
                curso_categoria=categoria,
                aprovadas=True
            )

            if not atividades.exists():
                continue

            horas_brutas = sum(a.horas_aprovadas for a in atividades)

            horas_validas = AlunoService.calcular_horas_complementares_validas(
                aluno=aluno,
                apenas_aprovadas=True,
                categoria=categoria
            )

            categorias_dados.append({
                'categoria': categoria,
                'atividades': atividades,
                'horas_brutas': horas_brutas,
                'horas_validas': horas_validas,
            })

        total_horas_validas = AlunoService.calcular_horas_complementares_validas(
            aluno=aluno,
            apenas_aprovadas=True
        )

        horas_requeridas = aluno.curso.horas_requeridas

        return {
            'aluno': aluno,
            'categorias': categorias_dados,
            'total_horas_validas': total_horas_validas,
            'horas_requeridas': horas_requeridas,
        }


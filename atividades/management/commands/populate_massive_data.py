from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from atividades.models import Curso, Categoria, CategoriaCurso, Aluno, Semestre, Atividade
from datetime import datetime, timedelta
from django.db import connection, transaction
import random
import time

class Command(BaseCommand):
    help = 'Popula o sistema com dados massivos: 50 alunos por curso/semestre e 50 atividades por aluno.'

    def handle(self, *args, **options):
        tempo_inicio = time.time()
        
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('POPULAÇÃO MASSIVA ULTRA-RÁPIDA (SQL PURO)'))
        self.stdout.write(self.style.WARNING('='*60))
        
        # Otimizações SQLite
        self.stdout.write('\n[OTIMIZAÇÃO] Configurando SQLite para máxima velocidade...')
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA synchronous = OFF")
            cursor.execute("PRAGMA journal_mode = MEMORY")
            cursor.execute("PRAGMA temp_store = MEMORY")
            cursor.execute("PRAGMA cache_size = 1000000")
        self.stdout.write(self.style.SUCCESS('  ✓ SQLite otimizado'))
        
        # Buscar todos os cursos e semestres
        cursos = list(Curso.objects.all())
        semestres = list(Semestre.objects.all())
        
        if not cursos:
            self.stdout.write(self.style.ERROR('Nenhum curso encontrado. Execute populate_initial_data primeiro.'))
            return
        
        if not semestres:
            self.stdout.write(self.style.ERROR('Nenhum semestre encontrado. Execute populate_initial_data primeiro.'))
            return
        
        # Nomes fictícios para alunos
        primeiros_nomes = [
            'João', 'Maria', 'Pedro', 'Ana', 'Lucas', 'Juliana', 'Carlos', 'Fernanda',
            'Rafael', 'Beatriz', 'Bruno', 'Camila', 'Gabriel', 'Larissa', 'Felipe',
            'Mariana', 'Diego', 'Amanda', 'Thiago', 'Letícia', 'André', 'Bianca',
            'Rodrigo', 'Carolina', 'Leonardo', 'Isabela', 'Gustavo', 'Natália', 'Matheus',
            'Bruna', 'Ricardo', 'Patrícia', 'Vinícius', 'Aline', 'Marcelo', 'Jéssica',
            'Daniel', 'Vanessa', 'Paulo', 'Cristina', 'Fernando', 'Renata', 'Alexandre',
            'Priscila', 'Fábio', 'Adriana', 'Henrique', 'Simone', 'Maurício', 'Tatiana'
        ]
        
        sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Lima', 'Pereira', 'Costa', 'Ferreira',
            'Rodrigues', 'Almeida', 'Nascimento', 'Carvalho', 'Araújo', 'Ribeiro', 'Martins',
            'Rocha', 'Alves', 'Monteiro', 'Mendes', 'Barbosa', 'Cardoso', 'Castro', 'Dias',
            'Gomes', 'Pinto', 'Ramos', 'Fernandes', 'Freitas', 'Moura', 'Cavalcanti'
        ]
        
        # Nomes de atividades fictícias
        atividades_nomes = [
            'Workshop de Tecnologia',
            'Palestra sobre Inovação',
            'Curso de Python Avançado',
            'Seminário de Engenharia',
            'Minicurso de Design Thinking',
            'Congresso Nacional',
            'Evento Acadêmico Internacional',
            'Oficina de Desenvolvimento Web',
            'Curso de Inglês Técnico',
            'Participação em Mesa Redonda',
            'Monitoria de Programação',
            'Iniciação Científica',
            'Publicação de Artigo',
            'Apresentação de TCC',
            'Curso de Gestão de Projetos',
            'Workshop de UX/UI',
            'Palestra sobre Inteligência Artificial',
            'Curso de Análise de Dados',
            'Seminário de Sustentabilidade',
            'Minicurso de Robótica',
            'Congresso Regional',
            'Evento de Empreendedorismo',
            'Oficina de Marketing Digital',
            'Curso de Espanhol',
            'Participação em Defesa de Mestrado',
            'Extensão Universitária',
            'Pesquisa de Campo',
            'Produção de Conteúdo Digital',
            'Curso de Fotografia',
            'Workshop de Comunicação',
            'Palestra sobre Liderança',
            'Curso de Excel Avançado',
            'Seminário de Direitos Humanos',
            'Minicurso de Blockchain',
            'Congresso Internacional',
            'Evento de Networking',
            'Oficina de Redação Científica',
            'Curso de Alemão Básico',
            'Participação em Banca de TCC',
            'Projeto de Extensão',
            'Estudo de Caso',
            'Produção Audiovisual',
            'Curso de Edição de Vídeo',
            'Workshop de Produtividade',
            'Palestra sobre Carreira',
            'Curso de Power BI',
            'Seminário de Ética',
            'Minicurso de Cloud Computing',
            'Congresso de Ciências',
            'Evento Cultural'
        ]
        
        descricoes = [
            'Participação como ouvinte no evento',
            'Atividade realizada com aproveitamento',
            'Curso completo com certificado',
            'Participação ativa durante todo o evento',
            'Aprendizado significativo na área',
            'Experiência enriquecedora',
            'Desenvolvimento de competências técnicas',
            'Networking e troca de experiências',
            'Atualização profissional',
            'Aprofundamento teórico e prático'
        ]
        
        total_alunos = 0
        total_atividades = 0
        tempo_inicio = time.time()
        
        # Contar total de combinações
        total_combinacoes = 0
        for curso in cursos:
            categorias_curso = list(CategoriaCurso.objects.filter(curso_semestre__curso=curso))
            if categorias_curso:
                for semestre in semestres:
                    categorias_semestre = [cc for cc in categorias_curso if cc.curso_semestre.semestre == semestre]
                    if categorias_semestre:
                        total_combinacoes += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n[PLANEJAMENTO]'))
        self.stdout.write(self.style.SUCCESS(f'  → Combinações curso/semestre: {total_combinacoes}'))
        self.stdout.write(self.style.SUCCESS(f'  → Alunos a criar: ~{total_combinacoes * 60}'))
        self.stdout.write(self.style.SUCCESS(f'  → Atividades a criar: ~{total_combinacoes * 60 * 60}'))
        
        combinacao_atual = 0
        
        # Usar uma grande transação para tudo
        with transaction.atomic():
            self.stdout.write(f'\n[PROCESSAMENTO] Iniciando inserção em lote...\n')
            
            # Para cada curso
            for idx_curso, curso in enumerate(cursos, 1):
                # Buscar todas as categorias associadas a este curso
                categorias_curso = list(CategoriaCurso.objects.filter(curso_semestre__curso=curso))
                
                if not categorias_curso:
                    continue
                
                # Para cada semestre
                for semestre in semestres:
                    # Filtrar categorias deste semestre
                    categorias_semestre = [cc for cc in categorias_curso if cc.curso_semestre.semestre == semestre]
                    
                    if not categorias_semestre:
                        continue
                    
                    combinacao_atual += 1
                    tempo_decorrido = time.time() - tempo_inicio
                    
                    self.stdout.write(f'[{combinacao_atual}/{total_combinacoes}] {curso.nome[:30]:30} | {semestre.nome} | {tempo_decorrido:.1f}s')
                    
                    # Preparar SQL em massa
                    inicio_batch = time.time()
                    
                    # 1. Criar usuários em massa com SQL puro
                    usuarios_sql = []
                    usernames_batch = []  # Agora são matrículas
                    nomes_batch = []  # Nomes completos
                    
                    for i in range(60):
                        primeiro_nome = random.choice(primeiros_nomes)
                        sobrenome = random.choice(sobrenomes)
                        nome_completo = f'{primeiro_nome} {sobrenome}'
                        # Gerar matrícula única com timestamp para evitar conflitos
                        matricula = f'{curso.nome[:3].upper()}{semestre.nome.replace(".", "")}{i+1:03d}'
                        email = f'{matricula.lower()}@example.com'
                        password = 'pbkdf2_sha256$600000$salt$hash'  # Senha dummy
                        
                        usernames_batch.append(matricula)
                        nomes_batch.append(nome_completo)
                        usuarios_sql.append(
                            f"('{matricula}', '{password}', '{email}', '', '', 0, 1, 1, datetime('now'), datetime('now'))"
                        )
                    
                    # Inserir usuários (com first_name e last_name vazios)
                    if usuarios_sql:
                        sql = f"""
                        INSERT OR IGNORE INTO auth_user 
                        (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined, last_login)
                        VALUES {','.join(usuarios_sql)}
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                            rows_affected = cursor.rowcount
                            if rows_affected > 0:
                                total_alunos += rows_affected
                    
                    # 2. Buscar IDs dos usuários criados
                    usernames_escaped = ','.join([f"'{u}'" for u in usernames_batch])
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT id, username FROM auth_user WHERE username IN ({usernames_escaped})"
                        )
                        user_ids = {row[1]: row[0] for row in cursor.fetchall()}
                    
                    # 3. Criar alunos em massa com nome e matrícula
                    alunos_sql = []
                    for idx, matricula in enumerate(usernames_batch):
                        if matricula in user_ids:
                            nome_escapado = nomes_batch[idx].replace("'", "''")
                            alunos_sql.append(
                                f"({user_ids[matricula]}, '{nome_escapado}', '{matricula}', {curso.id}, {semestre.id})"
                            )
                    
                    if alunos_sql:
                        sql = f"""
                        INSERT OR IGNORE INTO atividades_aluno 
                        (user_id, nome, matricula, curso_id, semestre_ingresso_id)
                        VALUES {','.join(alunos_sql)}
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                    
                    # 4. Buscar IDs dos alunos
                    user_ids_list = list(user_ids.values())
                    user_ids_escaped = ','.join([str(uid) for uid in user_ids_list])
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT id, user_id FROM atividades_aluno WHERE user_id IN ({user_ids_escaped})"
                        )
                        aluno_ids = {row[1]: row[0] for row in cursor.fetchall()}
                    
                    # 5. Criar atividades em massa (SUPER OTIMIZADO)
                    atividades_sql = []
                    batch_size = 500  # Criar em lotes de 500
                    
                    for username in usernames_batch:
                        if username not in user_ids or user_ids[username] not in aluno_ids:
                            continue
                        
                        aluno_id = aluno_ids[user_ids[username]]
                        
                        for j in range(30):
                            categoria = random.choice(categorias_semestre)
                            
                            # Definir datas
                            if semestre.data_inicio and semestre.data_fim:
                                data_inicio = datetime.strptime(str(semestre.data_inicio), '%Y-%m-%d')
                                data_fim = datetime.strptime(str(semestre.data_fim), '%Y-%m-%d')
                                dias_diferenca = (data_fim - data_inicio).days
                                data_atividade = data_inicio + timedelta(days=random.randint(0, max(1, dias_diferenca)))
                            else:
                                data_atividade = datetime.now()
                            
                            horas = random.randint(2, 40)
                            
                            # 70% aprovadas
                            if random.random() < 0.7:
                                if random.random() < 0.9:
                                    horas_aprovadas = random.randint(int(horas * 0.8), horas)
                                    status = 'Aprovada'
                                else:
                                    horas_aprovadas = 0
                                    status = 'Rejeitada'
                                horas_aprovadas_sql = str(horas_aprovadas)
                            else:
                                horas_aprovadas_sql = 'NULL'
                                status = 'Pendente'
                            
                            nome = random.choice(atividades_nomes).replace("'", "''")
                            descricao = random.choice(descricoes).replace("'", "''")
                            data_str = data_atividade.strftime('%Y-%m-%d')
                            
                            atividades_sql.append(
                                f"({aluno_id}, {categoria.id}, '{nome}', '{descricao}', {horas}, {horas_aprovadas_sql}, '{data_str}', NULL, '{status}')"
                            )
                            
                            # Inserir em lotes
                            if len(atividades_sql) >= batch_size:
                                sql = f"""
                                INSERT INTO atividades_atividade 
                                (aluno_id, categoria_id, nome, descricao, horas, horas_aprovadas, data, documento, status)
                                VALUES {','.join(atividades_sql)}
                                """
                                with connection.cursor() as cursor:
                                    cursor.execute(sql)
                                    total_atividades += cursor.rowcount
                                atividades_sql = []
                    
                    # Inserir atividades restantes
                    if atividades_sql:
                        sql = f"""
                        INSERT INTO atividades_atividade 
                        (aluno_id, categoria_id, nome, descricao, horas, horas_aprovadas, data, documento, status)
                        VALUES {','.join(atividades_sql)}
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                            total_atividades += cursor.rowcount
                    
                    tempo_batch = time.time() - inicio_batch
                    self.stdout.write(f'    ✓ Lote processado em {tempo_batch:.1f}s | Total: {total_alunos} alunos, {total_atividades} atividades')
                
                # Feedback a cada curso
                if idx_curso % 5 == 0:
                    self.stdout.write(self.style.SUCCESS(f'\n  → Progresso: {idx_curso}/{len(cursos)} cursos processados\n'))
        
        # Restaurar configurações SQLite
        self.stdout.write('\n[FINALIZAÇÃO] Restaurando configurações SQLite...')
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA synchronous = FULL")
            cursor.execute("PRAGMA journal_mode = DELETE")
        self.stdout.write(self.style.SUCCESS('  ✓ Configurações restauradas'))
        
        tempo_total = time.time() - tempo_inicio
        minutos = int(tempo_total // 60)
        segundos = tempo_total % 60
        
        self.stdout.write(self.style.SUCCESS(f'\n{'='*60}'))
        self.stdout.write(self.style.SUCCESS(f'✓ POPULAÇÃO MASSIVA CONCLUÍDA!'))
        self.stdout.write(self.style.SUCCESS(f'{'='*60}'))
        self.stdout.write(self.style.SUCCESS(f'  → Alunos criados: {total_alunos}'))
        self.stdout.write(self.style.SUCCESS(f'  → Atividades criadas: {total_atividades}'))
        self.stdout.write(self.style.SUCCESS(f'  → Tempo total: {minutos}min {segundos:.1f}s'))
        if tempo_total > 0:
            self.stdout.write(self.style.SUCCESS(f'  → Velocidade: {total_atividades/tempo_total:.0f} atividades/segundo'))
        self.stdout.write(self.style.SUCCESS(f'{'='*60}'))

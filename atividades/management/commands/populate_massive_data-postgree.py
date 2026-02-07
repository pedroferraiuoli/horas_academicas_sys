from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from atividades.models import Curso, CategoriaCurso, Aluno, Semestre
from datetime import datetime, timedelta
from django.db import connection, transaction
import random
import time


class Command(BaseCommand):
    help = 'Popula o sistema com dados massivos usando PostgreSQL.'

    def handle(self, *args, **options):

        tempo_inicio = time.time()

        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('POPULAÇÃO MASSIVA ULTRA-RÁPIDA (POSTGRES)'))
        self.stdout.write(self.style.WARNING('='*60))

        # Buscar cursos e semestres
        cursos = list(Curso.objects.all())
        semestres = list(Semestre.objects.all())

        if not cursos or not semestres:
            self.stdout.write(self.style.ERROR('Cursos ou semestres não encontrados.'))
            return

        primeiros_nomes = ['João','Maria','Pedro','Ana','Lucas','Juliana','Carlos','Fernanda']
        sobrenomes = ['Silva','Santos','Oliveira','Souza','Lima','Pereira','Costa','Ferreira']

        atividades_nomes = [
            'Workshop de Tecnologia',
            'Palestra sobre Inovação',
            'Curso de Python Avançado',
            'Seminário de Engenharia',
            'Congresso Nacional'
        ]

        descricoes = [
            'Participação como ouvinte',
            'Curso completo com certificado',
            'Experiência enriquecedora'
        ]

        total_alunos = 0
        total_atividades = 0

        with transaction.atomic():

            for curso in cursos:

                categorias_curso = list(
                    CategoriaCurso.objects.filter(curso_semestre__curso=curso)
                )

                if not categorias_curso:
                    continue

                for semestre in semestres:

                    categorias_semestre = [
                        cc for cc in categorias_curso
                        if cc.curso_semestre.semestre == semestre
                    ]

                    if not categorias_semestre:
                        continue

                    inicio_batch = time.time()

                    usuarios_sql = []
                    usernames_batch = []
                    nomes_batch = []

                    # ---------- USERS ----------
                    for i in range(60):

                        nome = f"{random.choice(primeiros_nomes)} {random.choice(sobrenomes)}"
                        matricula = f'{curso.nome[:3].upper()}{semestre.nome.replace(".", "")}{i+1:03d}'
                        email = f'{matricula.lower()}@example.com'

                        password = 'pbkdf2_sha256$600000$salt$hash'

                        usernames_batch.append(matricula)
                        nomes_batch.append(nome.replace("'", "''"))

                        usuarios_sql.append(
                            f"""(
                            '{matricula}',
                            '{password}',
                            '{email}',
                            '',
                            '',
                            false,
                            true,
                            true,
                            NOW(),
                            NOW()
                            )"""
                        )

                    if usuarios_sql:

                        sql = f"""
                        INSERT INTO auth_user
                        (username,password,email,first_name,last_name,
                        is_superuser,is_staff,is_active,date_joined,last_login)
                        VALUES {','.join(usuarios_sql)}
                        ON CONFLICT (username) DO NOTHING
                        """

                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                            total_alunos += cursor.rowcount

                    # Buscar ids
                    usernames_str = ",".join([f"'{u}'" for u in usernames_batch])

                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT id, username FROM auth_user WHERE username IN ({usernames_str})"
                        )
                        user_ids = {u: i for i, u in cursor.fetchall()}

                    # ---------- ALUNOS ----------
                    alunos_sql = []

                    for idx, matricula in enumerate(usernames_batch):

                        if matricula not in user_ids:
                            continue

                        alunos_sql.append(
                            f"""(
                            {user_ids[matricula]},
                            '{nomes_batch[idx]}',
                            '{matricula}',
                            {curso.id},
                            {semestre.id}
                            )"""
                        )

                    if alunos_sql:

                        sql = f"""
                        INSERT INTO atividades_aluno
                        (user_id,nome,matricula,curso_id,semestre_ingresso_id)
                        VALUES {','.join(alunos_sql)}
                        ON CONFLICT (matricula) DO NOTHING
                        """

                        with connection.cursor() as cursor:
                            cursor.execute(sql)

                    # Buscar alunos
                    ids = ",".join(str(i) for i in user_ids.values())

                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT id, user_id FROM atividades_aluno WHERE user_id IN ({ids})"
                        )
                        aluno_ids = {u: i for i, u in cursor.fetchall()}

                    # ---------- ATIVIDADES ----------
                    atividades_sql = []
                    batch_size = 1000

                    for username in usernames_batch:

                        if username not in user_ids:
                            continue

                        uid = user_ids[username]

                        if uid not in aluno_ids:
                            continue

                        aluno_id = aluno_ids[uid]

                        for _ in range(30):

                            categoria = random.choice(categorias_semestre)

                            if semestre.data_inicio and semestre.data_fim:
                                delta = (semestre.data_fim - semestre.data_inicio).days
                                data = semestre.data_inicio + timedelta(days=random.randint(0, max(1, delta)))
                            else:
                                data = datetime.now()

                            horas = random.randint(2, 40)

                            if random.random() < 0.7:
                                status = 'Aprovada'
                                horas_aprovadas = random.randint(int(horas*0.8), horas)
                            else:
                                status = 'Pendente'
                                horas_aprovadas = 'NULL'

                            nome = random.choice(atividades_nomes).replace("'", "''")
                            desc = random.choice(descricoes).replace("'", "''")

                            atividades_sql.append(
                                f"""(
                                {aluno_id},
                                {categoria.id},
                                '{nome}',
                                '{desc}',
                                {horas},
                                {horas_aprovadas},
                                '{data.strftime('%Y-%m-%d')}',
                                NULL,
                                '{status}'
                                )"""
                            )

                            if len(atividades_sql) >= batch_size:

                                sql = f"""
                                INSERT INTO atividades_atividade
                                (aluno_id,categoria_id,nome,descricao,horas,
                                horas_aprovadas,data,documento,status)
                                VALUES {','.join(atividades_sql)}
                                """

                                with connection.cursor() as cursor:
                                    cursor.execute(sql)
                                    total_atividades += cursor.rowcount

                                atividades_sql = []

                    if atividades_sql:

                        sql = f"""
                        INSERT INTO atividades_atividade
                        (aluno_id,categoria_id,nome,descricao,horas,
                        horas_aprovadas,data,documento,status)
                        VALUES {','.join(atividades_sql)}
                        """

                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                            total_atividades += cursor.rowcount

                    tempo_batch = time.time() - inicio_batch

                    self.stdout.write(
                        f'✓ {curso.nome} | {semestre.nome} → {tempo_batch:.1f}s'
                    )

        tempo_total = time.time() - tempo_inicio

        self.stdout.write(self.style.SUCCESS('\nPOPULAÇÃO FINALIZADA'))
        self.stdout.write(self.style.SUCCESS(f'Alunos: {total_alunos}'))
        self.stdout.write(self.style.SUCCESS(f'Atividades: {total_atividades}'))
        self.stdout.write(self.style.SUCCESS(f'Tempo: {tempo_total:.1f}s'))

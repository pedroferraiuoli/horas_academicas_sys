from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Prepara o projeto recém-clonado: migrações, superusuário, dados iniciais e runserver.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Executando migrate inicial...'))
        call_command('migrate')

        self.stdout.write(self.style.NOTICE('Executando makemigrations para app "atividades"...'))
        call_command('makemigrations', 'atividades')

        self.stdout.write(self.style.NOTICE('Executando migrate novamente...'))
        call_command('migrate')

        self.stdout.write(self.style.NOTICE('Criando superusuário admin:admin...'))
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superusuário admin criado.'))
        else:
            self.stdout.write(self.style.WARNING('Superusuário admin já existe.'))

        self.stdout.write(self.style.NOTICE('Populando dados iniciais...'))
        call_command('populate_initial_data')

        self.stdout.write(self.style.NOTICE('Iniciando servidor de desenvolvimento...'))
        call_command('runserver')

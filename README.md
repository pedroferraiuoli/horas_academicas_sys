# Plataforma de Controle de Atividades Complementares

Este projeto é uma plataforma web desenvolvida em Django para gestão de atividades complementares de alunos de graduação. O sistema permite o cadastro, acompanhamento e validação de atividades, com fluxos administrativos para Gestor, Coordenador e Aluno.

## Funcionalidades
- CRUD de cursos, categorias e atividades
- Dashboard com barra de progresso e alertas
- Upload de comprovantes
- Controle de horas por categoria e por curso
- Associação múltipla de categorias a cursos
- Permissões por perfil (Gestor, Coordenador, Aluno)
- Visual institucional com Bootstrap
- Redefinição de senha, alteração de e-mail
- Ativação/desativação de usuários administrativos

## Perfis de Usuário
- **Gestor:** Superadmin, gerencia todos os cursos e usuários
- **Coordenador:** Vinculado a um curso, gerencia categorias e alunos do curso
- **Aluno:** Vinculado a um curso, cadastra e acompanha suas atividades

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure o banco de dados (SQLite por padrão)
4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
5. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

## Estrutura do Projeto
- `plataforma/atividades/` - App principal com models, views, forms e templates
- `media/` - Arquivos enviados pelos usuários
- `migrations/` - Migrações do banco de dados

## Observações
- O arquivo `.gitignore` já está configurado para ignorar arquivos sensíveis e pastas de mídia/migrações
- Para produção, configure variáveis de ambiente e um banco de dados seguro

## Licença
Este projeto é distribuído sob a licença MIT.

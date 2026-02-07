# 🎓 Sistema de Gestão de Horas Acadêmicas Complementares

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![HTXM](https://img.shields.io/badge/HTMX-red)](https://www.htmx.org/)


## 📋 Sobre o Projeto

Plataforma web robusta e escalável desenvolvida em **Django** para gestão completa de atividades complementares acadêmicas. Sistema multi-tenant com controle granular de permissões, suportando dezenas de cursos e gerenciando milhares de atividades simultaneamente com alta performance.

### 🎯 Problema Resolvido

Instituições de ensino superior enfrentam desafios na validação e controle de atividades complementares dos alunos. Este sistema **automatiza e centraliza** todo o processo, reduzindo carga administrativa e garantindo conformidade com requisitos curriculares.

### 💼 Impacto de Negócio

- ⚡ **Redução** no tempo de validação de atividades
- 📊 **Dashboards em tempo real** para tomada de decisão
- 🔒 **Rastreabilidade** com sistema de logs
- 📱 **Interface responsiva**
- 🚀 **Escalável** para milhares de usuários simultâneos

---

## 🚀 Tecnologias e Arquitetura

### **Stack Principal**

- **Backend:** Django 6.0 (Python 3.12)
- **Banco de Dados:** PostgreSQL 15 (com índices otimizados)
- **Containerização:** Docker + Docker Compose
- **Web Server:** Gunicorn (produção) / Django Dev Server (desenvolvimento)
- **Frontend:** Bootstrap 5, JavaScript ES6+, HTMX
- **Cache:** Django Cache Framework
- **Storage:** Arquivos locais

### **Padrões e Boas Práticas**

- 🏗️ **Arquitetura em Camadas:** Services, Selectors, Views
- 🔐 **Segurança:** CSRF protection, autenticação baseada em sessões, validação de uploads
- 📊 **ORM Otimizado:** Queries com `select_related`, `prefetch_related`, agregações eficientes
- 🧪 **Testes:** Cobertura de testes unitários e integração
- 📝 **Logs Estruturados:** Sistema de logging com rotação automática
- 🐳 **DevOps Ready:** Docker multi-stage builds, variáveis de ambiente

---

## ✨ Funcionalidades Principais

### **Para Alunos**
- ✅ Cadastro e upload de comprovantes de atividades
- 📊 Dashboard com progresso em tempo real e controle por categoria
- 🔔 Notificações de status de validação
- 📈 Visualização de horas aprovadas vs. requeridas
- 📄 Geração de relatórios em PDF
- 📋 Listagem de atividades com filtragem dinâmica

### **Para Coordenadores**
- 🎯 Validação/rejeição de atividades do seu curso
- 👥 Gestão de alunos e categorias
- 📊 Relatórios analíticos do curso
- ⚙️ Configuração de limites de horas por categoria do seu curso
- 🔍 Filtros avançados e busca

### **Para Gestores**
- 🏢 Visão consolidada de todos os cursos
- 👤 Gestão de coordenadores e permissões
- 📈 Dashboards de números gerais
- 🗄️ Auditoria completa do sistema

### **Diferenciais Técnicos**
- 🔄 Sistema de notificações em tempo real
- 🎨 Interface moderna e responsiva (mobile-first)
- 🔐 Controle granular de permissões (RBAC)
- 📊 Queries otimizadas com índices PostgreSQL
- 🐳 Deploy simplificado com Docker
- 📝 Sistema de logs multi-nível (business, security, errors)
- ♻️ Caching inteligente para alta performance

---

## 🐳 Instalação e Execução (Docker)

### **Pré-requisitos**
- Docker 20.10+
- Docker Compose 2.0+

### **Setup Rápido**

```bash
# 1. Clone o repositório
git clone https://github.com/pedroferraiuoli/horas-academicas-sys.git
cd horas-academicas-sys

# 2. Configure variáveis de ambiente
cp .env.example .env
nano .env  # Ajuste SECRET_KEY, DB_PASSWORD, etc.

# 3. Suba os containers
docker-compose up -d --build

# 4. Execute migrações
docker-compose exec web python manage.py migrate

# 5. Popule dados iniciais (cursos, categorias, semestres)
docker-compose exec web python manage.py populate_initial_data

# 6. Crie um superusuário
docker-compose exec web python manage.py createsuperuser

# 7. Acesse a aplicação
# http://localhost:8000
```

---

## 💻 Instalação Local (Sem Docker)

```bash
# 1. Clone e entre no diretório
git clone https://github.com/pedroferraiuoli/horas-academicas-sys.git
cd horas-academicas-sys

# 2. Crie ambiente virtual
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
# Edite .env com suas configurações

# 5. Execute migrações
python manage.py migrate

# 6. Popule dados
python manage.py populate_initial_data

# 7. Crie superusuário
python manage.py createsuperuser

# 8. Execute servidor
python manage.py runserver
```

---

## 📊 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                   │
│  Templates Django + Bootstrap 5 + JavaScript + HTMX         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      CAMADA DE VIEWS                         │
│  atividade_views.py | user_views.py | dashboard_views.py    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE LÓGICA DE NEGÓCIO                │
│  services.py (write) | selectors.py (read)
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      CAMADA DE DADOS                         │
│  models.py → PostgreSQL (com índices otimizados)            │
└─────────────────────────────────────────────────────────────┘
```

### **Estrutura de Diretórios**

```
horas_academicas_sys/
├── 🐳 docker-compose.yml          # Orquestração de containers
├── 🐳 Dockerfile                  # Build de produção
├── 🐳 Dockerfile.dev              # Build de desenvolvimento
├── 📝 requirements.txt            # Dependências Python
├── ⚙️ manage.py                   # CLI do Django
│
├── 📁 plataforma/                 # Configurações do projeto
│   ├── settings.py               # Configurações centralizadas
│   ├── urls.py                   # Rotas principais
│   └── wsgi.py                   # WSGI config
│
├── 📁 atividades/                 # App principal
│   ├── 📊 models.py              # Modelos de dados
│   ├── 🎯 views/                 # Views por contexto
│   │   ├── atividade_views.py
│   │   ├── dashboard_views.py
│   │   └── user_views.py
│   ├── 🔧 services.py            # Lógica de negócio (write)
│   ├── 🔍 selectors.py           # Queries otimizadas (read)
│   ├── ✅ validators.py          # Validações customizadas
│   ├── 📝 forms.py               # Formulários
│   ├── 🎨 templates/             # Templates HTML
│   ├── 🎨 static/                # CSS, JS, imagens
│   ├── 🔄 migrations/            # Migrações do banco
│   └── 🛠️ management/commands/   # Comandos customizados
│
├── 📁 logs/                       # Logs da aplicação
├── 📁 media/                      # Uploads de usuários
└── 📁 staticfiles/                # Arquivos estáticos coletados
```

---

## 🔐 Segurança

- ✅ Proteção CSRF em todos os formulários
- ✅ Validação de tipos de arquivo em uploads
- ✅ Sanitização de inputs
- ✅ Autenticação baseada em sessões
- ✅ Controle de acesso baseado em roles (RBAC)
- ✅ Logs de segurança (tentativas de acesso não autorizado)
- ✅ Secrets gerenciados via variáveis de ambiente
- ✅ Proteção contra SQL Injection (Django ORM)
- ✅ Headers de segurança configurados

---

## 📈 Performance

### **Otimizações Implementadas**

- 🚀 **Queries Otimizadas:** `select_related`, `prefetch_related`, `only()`, `defer()`
- 📊 **Índices PostgreSQL:** Índices compostos e parciais em queries críticas
- 💾 **Caching:** Cache de queries frequentes
- 📦 **Agregações no Banco:** Uso de `annotate()` e `aggregate()`
- 🔄 **Lazy Loading:** Paginação em listagens grandes
- 📉 **Query Reduction:** Redução de N+1 queries

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Pedro** - [GitHub](https://github.com/pedroferraiuoli) | [LinkedIn](https://linkedin.com/in/pedroferraiuli)

---

## 📞 Suporte

Para dúvidas ou sugestões, abra uma [issue](https://github.com/pedroferraiuoli/horas-academicas-sys/issues).

---

## 🎓 Aprendizados e Desafios Técnicos

Este projeto demonstra competências em:

- ✅ **Desenvolvimento Full-Stack** com Django
- ✅ **Arquitetura de Software** (camadas, separação de responsabilidades)
- ✅ **Otimização de Performance** (queries, índices, caching)
- ✅ **DevOps** (Docker, containerização, CI/CD ready)
- ✅ **Banco de Dados** (modelagem, normalização, índices PostgreSQL)
- ✅ **Segurança** (RBAC, validações, proteções)
- ✅ **UI/UX** (design responsivo, acessibilidade)
- ✅ **Escalabilidade** (suporta milhares de usuários e milhões de registros)

---

⭐ **Se este projeto foi útil, considere dar uma estrela!** ⭐

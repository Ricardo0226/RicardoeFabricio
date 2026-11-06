# ClassSync — Sprint 2.5

Aplicação web Flask para organização do calendário acadêmico da turma.

## Etapas concluídas

- aplicação Flask mínima;
- rota pública `/`;
- layout Bootstrap;
- modelos relacionais com SQLAlchemy;
- persistência SQLite para desenvolvimento;
- integração inicial do FullCalendar;
- endpoint `/api/events` para os eventos do calendário;
- cadastro, edição e exclusão de eventos por líderes/administradores;
- painel protegido em `/admin`;
- testes de autorização e do ciclo CRUD da Sprint 2.4;
- validação de categoria e período dos eventos;
- páginas amigáveis para erros 404 e 500, sem exposição de detalhes internos;
- rollback explícito em falhas de persistência.

## Calendário

A interface utiliza o FullCalendar via CDN para exibir os eventos salvos no banco. A página oferece visualizações mensal, semanal e em lista, com localização em português.

O endpoint `GET /api/events` retorna os eventos no formato esperado pelo FullCalendar. Líderes e administradores podem gerenciar compromissos pelo painel `/admin`; estudantes e visitantes mantêm acesso somente à visualização pública.

## Modelos atuais

- `User`: nome, e-mail, perfil e identificador;
- `Classroom`: nome, descrição e identificador;
- `Event`: título, categoria, período, descrição e vínculo opcional com uma turma.

`Event.classroom_id` é uma chave estrangeira opcional para `Classroom`. A aplicação cria as tabelas na inicialização. O banco padrão fica em `instance/classsync.db`; a variável `DATABASE_URL` pode apontar para outro SQLite ou banco compatível.

## Execução

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python app.py
```

Acesse `http://localhost:5000`.

# ClassSync — Sprint 1

Aplicação web Flask para organização do calendário acadêmico da turma.

## Etapas concluídas

- aplicação Flask mínima;
- rota pública `/`;
- layout Bootstrap;
- modelos relacionais com SQLAlchemy;
- persistência SQLite para desenvolvimento;
- testes da página inicial, dos modelos e do relacionamento entre eventos e turmas.

## Modelos atuais

Os modelos relacionais atuais são:

- `User`: nome, e-mail, perfil e identificador;
- `Classroom`: nome, descrição e identificador;
- `Event`: título, período, descrição e vínculo opcional com uma turma.

`Event.classroom_id` é uma chave estrangeira opcional para `Classroom`. A aplicação cria as tabelas na inicialização. O banco padrão fica em `instance/classsync.db` no ambiente Flask; a variável `DATABASE_URL` pode apontar para outro SQLite ou banco compatível.

## Execução

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python app.py
```

Acesse `http://localhost:5000`.

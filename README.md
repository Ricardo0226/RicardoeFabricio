# ClassSync — Sprint 1

Aplicação web Flask para organização do calendário acadêmico da turma.

## Etapas concluídas

- aplicação Flask mínima;
- rota pública `/`;
- layout Bootstrap;
- modelos de domínio iniciais;
- testes da página inicial e dos modelos.

## Modelos atuais

A Issue #2 adiciona três modelos simples, ainda sem persistência:

- `User`: nome, e-mail, perfil e identificador;
- `Classroom`: nome, descrição e identificador;
- `Event`: título, período, descrição e vínculo opcional com uma turma.

A configuração do banco de dados será feita separadamente na Issue #3.

## Execução

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python app.py
```

Acesse `http://localhost:5000`.

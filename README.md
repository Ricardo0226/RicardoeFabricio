# ClassSync — Sprint 2.6

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

## Testes de sistema e documentação

A suíte automatizada cobre os fluxos centrais da Sprint 2: cadastro, login, logout, calendário público, autorização por papel, CRUD de eventos, validações de formulário, tratamento de erros e compatibilidade com bancos SQLite legados. O arquivo `tests/test_system_flows.py` reúne cenários ponta a ponta com visitante, estudante, líder e administrador.

Execute todos os testes com:

```bash
pytest -q
```

O resultado de cada execução deve ser registrado a partir da saída real do comando. A validação cruzada por outro integrante da equipe deve ser feita em uma execução independente; este repositório não cria evidências de revisão automaticamente.

## Calendário

A interface utiliza o FullCalendar via CDN para exibir os eventos salvos no banco. A página oferece visualizações mensal, semanal e em lista, com localização em português.

O endpoint `GET /api/events` retorna os eventos no formato esperado pelo FullCalendar. Líderes e administradores podem gerenciar compromissos pelo painel `/admin`; estudantes e visitantes mantêm acesso somente à visualização pública.

## Modelos atuais

- `User`: nome, e-mail, perfil e identificador;
- `Classroom`: nome, descrição e identificador;
- `Event`: título, categoria, período, descrição e vínculo opcional com uma turma.

`Event.classroom_id` é uma chave estrangeira opcional para `Classroom`. A aplicação cria as tabelas na inicialização e atualiza bancos SQLite legados, adicionando automaticamente a coluna `Event.category` quando ela ainda não existe. O banco padrão fica em `instance/classsync.db`; a variável `DATABASE_URL` pode apontar para outro SQLite ou banco compatível.

## Execução

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python app.py
```

Acesse `http://localhost:5000`.

### Configuração

Por padrão, a aplicação usa `sqlite:///classsync.db`, armazenado no diretório `instance/`. Para usar outro banco, defina `DATABASE_URL`; para produção, defina também `SECRET_KEY` com um valor secreto próprio:

```bash
export DATABASE_URL="sqlite:///instance/classsync.db"
export SECRET_KEY="troque-este-valor-em-producao"
python app.py
```

Não há usuários de demonstração criados automaticamente. Os testes criam dados temporários, incluindo usuários com os papéis `student`, `leader` e `admin`. Em uma instalação real, o primeiro usuário pode ser cadastrado pela tela `/register` e recebe o papel `student`; a promoção para líder ou administrador deve ser feita por uma operação administrativa controlada.

## Decisões e limitações conhecidas

- A autenticação usa sessão Flask e senhas armazenadas como hash Werkzeug; a aplicação não expõe a senha na sessão.
- `leader` e `admin` podem gerenciar eventos. Visitantes e `student` podem consultar o calendário, mas não acessam `/admin`.
- A atualização automática de schema cobre a coluna `events.category` em bancos SQLite legados. Ela não substitui uma ferramenta completa de migrações para alterações futuras.
- O calendário carrega o FullCalendar por CDN. Uma instalação sem acesso à rede pode carregar a página, mas não terá a interface interativa do calendário.
- A validação por outro integrante é uma etapa do processo de revisão e deve ser registrada no Pull Request somente depois que ocorrer de fato.

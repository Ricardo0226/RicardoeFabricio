# Sprint 2.6 — Registro de validação

## Escopo

Esta Sprint consolida os testes dos fluxos centrais da Sprint 2 e documenta as decisões e limitações atuais do ClassSync.

## Execução local do implementador

Comando:

```bash
pytest -q
```

O resultado deve ser preenchido com a saída real da execução antes da abertura ou atualização do Pull Request. Não registrar números manualmente.

## Validação cruzada

Status: **aguardando execução por integrante diferente do implementador**.

Procedimento para o revisor:

1. atualizar a branch do Pull Request;
2. criar um ambiente virtual limpo;
3. instalar `requirements.txt`;
4. executar `pytest -q`;
5. testar manualmente `/`, `/register`, `/login`, `/logout`, `/api/events` e `/admin` com visitante, estudante, líder e administrador;
6. registrar no Pull Request o comando, o resultado real, a identidade do revisor e eventuais observações.

Este arquivo é um roteiro de validação. Ele não declara que a revisão cruzada já aconteceu.

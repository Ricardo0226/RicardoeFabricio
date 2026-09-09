const diasSemana = {
  1: "Segunda-feira",
  2: "Terça-feira",
  3: "Quarta-feira",
  4: "Quinta-feira",
  5: "Sexta-feira",
};

const horarios = {
  1: "07:00 - 07:45",
  2: "07:45 - 08:30",
  3: "08:50 - 09:35",
  4: "09:35 - 10:20",
  5: "10:30 - 11:15",
  6: "11:15 - 12:00",
  7: "13:00 - 13:45",
  8: "13:45 - 14:30",
  9: "14:40 - 15:35",
  10: "15:35 - 16:20",
  11: "16:30 - 17:15",
  12: "17:15 - 18:00",
};

$(function () {
  // array global para armazenar agendamentos antes de salvar
  window.agendamentosArray = [];
  // Mudança de professor
  $("#filesA").on("change", function () {
    const matricula = $(this).val();
    const nome = $(this).find("option:selected").text();
    $("#professor-selecionado").text(nome);

    const container = $("#disciplinas-container");
    container.empty();

    fetch(`/api/disciplinas/${matricula}`)
      .then((response) => response.json())
      .then((disciplinas) => {
        disciplinas.forEach((disc) => {
          container.append(
            `<div class="card-disciplina" data-professor="${matricula}" data-disciplina="${disc.nome}">${disc.nome}</div>`
          );
        });

        $(".card-disciplina").draggable({
          helper: "clone",
          revert: "invalid",
        });
      })
      .catch((error) => console.error("Erro ao buscar disciplinas:", error));
  });

  // Configuração do Drop
  $(".agenda-cell").droppable({
    accept: ".card-disciplina",
    drop: function (event, ui) {
      const labAtual = $("#filesB").val();
      if (labAtual === "none" || !labAtual) {
        alert("Selecione um laboratório primeiro!");
        return;
      }

      const clone = ui.helper.clone();
      $(this).empty().append(clone);

      clone.draggable({
        helper: "original",
        containment: "#tabela-agenda",
        revert: "invalid",
      });

      const dia = $(this).data("dia");
      const horario = $(this).data("horario");

      const agendamento = {
        professor: clone.data("professor"),
        disciplina: clone.data("disciplina"),
        dia,
        horario,
        laboratorio: labAtual,
        dia_nome: diasSemana[dia],
        horario_legivel: horarios[horario],
      };

      // armazenar para possível envio em lote
      window.agendamentosArray.push(agendamento);
    },
  });

  // Carrega quando muda de lab
  $("#filesB").on("change", function () {
    atualizarTabelaParaLab($(this).val());
  });

  $("#limpar-agenda").on("click", function () {
    const labAtual = $("#filesB").val();
    if (!labAtual || labAtual === "none") return;
    fetch(`/api/agendamentos/${labAtual}`, { method: "DELETE" })
      .then(() => {
        atualizarTabelaParaLab(labAtual);
      })
      .catch((err) => console.error("Erro ao limpar:", err));
  });
});

async function salvarAgendamentoNoBanco(item) {
  try {
    const response = await fetch("/api/agendamentos/salvar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    });
    if (!response.ok) throw new Error("Erro ao salvar agendamento");
    console.log(
      `✔️ Salvo: ${item.disciplina} - ${item.dia_nome} (${item.horario_legivel})`
    );
  } catch (error) {
    console.error("Falha ao salvar:", error);
  }
}

// Salva todos os agendamentos que foram acumulados na página
async function salvarTodosAgendamentos() {
  if (!window.agendamentosArray || window.agendamentosArray.length === 0) {
    alert("Nenhum agendamento para salvar.");
    return;
  }

  for (const item of window.agendamentosArray) {
    await salvarAgendamentoNoBanco(item);
  }

  // Após salvar, limpa o array
  window.agendamentosArray = [];
  alert("Agendamentos salvos com sucesso.");
}

// conecta o botão SALVAR ao salvamento em lote
$(function () {
  $("#salvar-agenda").on("click", function () {
    salvarTodosAgendamentos();
  });
});

async function atualizarTabelaParaLab(lab) {
  $(".agenda-cell").empty();
  if (!lab || lab === "none") return;

  try {
    const response = await fetch(`/api/agendamentos/${lab}`);
    const agendamentos = await response.json();

    agendamentos.forEach((a) => {
      const cell = $(
        `.agenda-cell[data-dia='${a.dia}'][data-horario='${a.horario}']`
      );
      const card = $(
        `<div class="card-disciplina" data-professor="${a.professor}" data-disciplina="${a.disciplina}">${a.disciplina}</div>`
      );
      cell.append(card);
      card.draggable({
        helper: "original",
        containment: "#tabela-agenda",
        revert: "invalid",
      });
    });
  } catch (error) {
    console.error("Erro ao atualizar tabela:", error);
  }
}

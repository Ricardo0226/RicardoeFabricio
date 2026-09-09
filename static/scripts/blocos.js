for (let i = 1; i <= 12; i++) {
  document.write("<tr>");
  for (let j = 1; j <= 5; j++) {
    document.write(
      `<td class='agenda-cell' data-dia='${j}' data-horario='${i}'></td>`
    );
  }
  document.write("</tr>");
}

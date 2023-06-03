$(document).ready(function () {
  $("#tabela-livros").DataTable({
    responsive: true,
    responsive: {
      details: false,
    },
    columns: [
      null,
      null,
      { orderable: true },
      { orderable: true },
      { orderable: false, searchable: false },
    ],
    language: {
      search: "",
      searchPlaceholder: "Busque por um livro",
      zeroRecords: "Nenhum resultado encontrado",
      info: "Mostrando _START_ a _END_ de _TOTAL_ livros",
      infoEmpty: "Mostrando 0 a 0 de 0 livros",
      infoFiltered: "(filtrado de _MAX_ livros no total)",
      paginate: {
        first: "Primeira",
        last: "Última",
        next: "Próxima",
        previous: "Anterior",
      },
    },
    lengthChange: false,
    lengthMenu: [20],
    autoWidth: false,
    targets: "_all",
  });
});

function format(d) {
  // `d` is the original data object for the row
  console.log(d);
  var t = d.reviews;
  var table_str =
    '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
  t.map((r) => (table_str += "<tr>" + "<td>" + r + "</td>" + "</tr>"));
  return table_str + "</table>";
}

$(document).ready(function () {
  let table = $("#example").DataTable({
    /* responsive: {
      breakpoints: [
        { name: "bigdesktop", width: Infinity },
        { name: "meddesktop", width: 1480 },
        { name: "smalldesktop", width: 1280 },
        { name: "medium", width: 1188 },
        { name: "tabletl", width: 1024 },
        { name: "btwtabllandp", width: 848 },
        { name: "tabletp", width: 768 },
        { name: "mobilel", width: 480 },
        { name: "mobilep", width: 320 },
      ],
    }, */

    dom: "Bfrtip",
    buttons: [
      { extend: "pageLength", className: "btn btn-primary" },
     /*  {
        text: "XLSX",
        action: function (e, dt, node, config) { 
          location.href = "/api/lead/export?" + $.param(dt.ajax.params()); 
        },
      }, */
    ],
    processing: true,
    serverSide: true,
    ajax: "/api/leads",
    columns: [
      {
        className: "dt-control",
        orderable: false,
        data: null,
        defaultContent: "",
      },
      { name: "id", data: "_id.$oid", visible: false },
      { name: "name", data: "name" },
      {
        name: "email",
        data: "email",
        render: function (data, type, row) {
          return `<a href="mailto:${data}" target="_blank">${data}</a>`;
        },
      },
      { name: "address", data: "address" },
      { name: "phone", data: "phone" },
      { name: "review_score", data: "review_score" },
      { name: "total_reviews", data: "total_reviews" },
      { name: "reviews", data: "reviews", visible: false },
    ],
  });

  $("#example tbody").on("click", "td.dt-control", function () {
    var tr = $(this).closest("tr");
    var row = table.row(tr);

    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();
      tr.removeClass("shown");
    } else {
      // Open this row
      row.child(format(row.data())).show();
      tr.addClass("shown");
    }
  });
});

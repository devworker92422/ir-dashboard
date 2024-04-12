
var table;
function updateStatus(obj) {
  let id = obj.parentElement.parentElement.id;
  let value = obj.value;
  $.ajax({
    url: '/api/updateStatus',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      'id': id,
      'status': value,
    }),
    success: function (response) {
      table.draw(false);
    },
    error: function (xhr, status, error) {
      console.log(xhr.responseText);
    }
  });
}

function updateGoogleStatus(obj) {
  let id = obj.parentElement.parentElement.id;
  let value = obj.value;
  $.ajax({
    url: '/api/updateGoogleStatus',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      'id': id,
      'status': value,
    }),
    success: function (response) {
      // Handle successful response
      table.draw(false);
    },
    error: function (xhr, status, error) {
      // Handle error response
      console.log(xhr.responseText);
    }
  });
}
$(document).ready(function () {
  table = $("#example").DataTable({
    dom: "Bfrtip",
    buttons: [
      { extend: "pageLength", className: "btn bg-white" },
      {
        text: "XLSX",
        className: "btn bg-white",
        autoFilter: true,
        action: function (e, dt, node, config) {
          location.href = "/api/export?" + $.param(dt.ajax.params());
        },
      },
    ],
    paging: true,
    pageLength: 10,
    processing: true,
    serverSide: true,
    ajax: {
      url: "/api/urls",
      complete: function (response) {
        console.log(response);
        var jsonRes = response.responseJSON
        var topoffenders = jsonRes['topoffenders'];
        for (var i = 1; i < 4; i++) {
          $('#to_' + i).html('');
          if (topoffenders[i - 1]) {
            $('#to_' + i).html('<span class="text-warning mr-2"><i class="fas fa-arrow-down"></i>' + topoffenders[i - 1]['count'] + '</span><span class="text-nowrap">' + topoffenders[i - 1]['_id'] + '</span>');
          }
        }
      },
    },
    rowId: 'id',
    columns: [
      { name: "_id", data: "id", visible: false, render: function (data, type, row) { if (data) { return data } else { } } },
      { name: "date", data: "date" },
      { name: "requester_email", data: "requester_email", visible: false },
      {
        name: "client_name",
        data: "client_name",
      },
      {
        name: "client_email",
        data: "client_email",
        render: function (data, type, row) {
          return `<a href="mailto:${data}" target="_blank">${data}</a>`;
        },
      },
      {
        name: "url",
        data: "url",
        autoWidth: false,
        width: "250px",
        className: "aaa",
        render: function (data, type, row) {
          return `<a href="${data}" target="_blank">${data}</a>`;
        },
      },
      {
        name: "status",
        data: "status",
        render: function (data, type, row) {

          let role = $('#role').val();
          let live = '';
          let removed = '';
          let status_updating = '';
          let d = '';
          if (data.toString().toLowerCase() == "live") { live = 'selected'; }
          else if (data.toString().toLowerCase() == "status updating") { status_updating = "selected"; }
          else if (data.toString().toLowerCase() == "removed") { removed = "selected"; }
          else if (data.toString().toLowerCase() == "") { d = "selected"; }

          if (role < 3 & role > 0)
            return `<select class='form-control' onChange='updateStatus(this)'>
                    <option value='Live' ${live} ">Live</option>
                    <option value='Status Updating' ${status_updating}>Updating</option>
                    <option value='Removed' ${removed}>Remove</option>
                    <option value='' ${d}></option>
                  </select>`
          else
            switch (data.toString().toLowerCase()) {
              case "live":
                return `<div class='status-box live-box'>${data}</div>`;
              case "status updating":
                return `<div class='status-box updating-box'>Updating</div>`;
              case "removed":
                return `<div class='status-box removed-box'>${data}</div>`;
              default:
                return '';
            }
        },
      },
      {
        name: "google_status",
        data: "google_status",
        render: function (data, type, row) {
          let role = $('#role').val();
          let live = '';
          let removed = '';
          let status_updating = '';
          let d = '';
          if (!data) {
            data = "Status Updating";
          }
          if (data.toString().toLowerCase() == "live") { live = 'selected'; }
          else if (data.toString().toLowerCase() == "status updating") { status_updating = "selected"; }
          else if (data.toString().toLowerCase() == "removed") { removed = "selected"; }
          else if (data.toString().toLowerCase() == "") { d = "selected"; }

          if (role < 3 & role > 0)
            return `<select class='form-control' onChange='updateGoogleStatus(this)'>
                    <option value='Live' ${live}>Live</option>
                    <option value='Status Updating' ${status_updating}>Updating</option>
                    <option value='Removed' ${removed}>Remove</option>
                    <option value='' ${d}>Unknown</option>
                  </select>`
          else
            switch (data.toString().toLowerCase()) {
              case "live":
                return `<div class='status-box live-box'>${data}</div>`;
              case "status updating":
                return `<div class='status-box updating-box'>Updating</div>`;
              case "removed":
                return `<div class='status-box removed-box'>${data}</div>`;
              default:
                return '';
            }
        },
      },
      { name: "date_checked", data: "date_checked", render: function (data, type, row) { if (data) { return data; } else { return '' } } },
      { name: "submission_count", data: "submission_count", render: function (data, type, row) { if (data) { return `<div class="text-center">${data}</div>`; } else { return '1' } } },
      {
        name: "action", data: 'id', render: function (data, type, row) {
          return `<a target="_blank" href="/detail?id=${data}" class="btn">Open</a>`
        }
      }
    ],
  });
  var clients = [];
  table
    .columns()
    .flatten()
    .each(function (colIdx) {
      // Create the select list and search operation
      var select;
      switch (colIdx) {
        case 3:
        case 6:
        case 7:
          select = $(`<select class="form-control" id="sel_` + colIdx + `"/>`)
            .appendTo(table.column(colIdx).footer())
            .on("change", function () {
              console.log($(this).val());
              table.column(colIdx).search($(this).val()).draw();
            });
          break;
      }

      // Get the search data for the first column and add to the select list
      switch (colIdx) {
        case 3:
          select.append($(`<option value="">Select Profile</option>`));
          break;
        case 6:
          select.append($(`<option value="">Select Status</option>`));
          select.append($(`<option value="Live">Live</option>`));
          select.append($(`<option value="Removed">Removed</option>`));
          select.append($(`<option value="Status Updating">Status Updating</option>`));
          break;
        case 7:
          select.append($(`<option value="">Select Google Status</option>`));
          select.append($(`<option value="indexed">Indexed</option>`));
          select.append($(`<option value="Live">Live</option>`));
          select.append($(`<option value="Removed">Removed</option>`));
          break;
      }
    });

  fetch('/api/getClients',
    {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin': '*',
      }
    }).then(response => response.json()).then(res => {
      console.log(res);
      if (res['success']) {
        select = $('#sel_3');
        clients = res['results'];
        for (var i = 0; i < clients.length; i++) {
          select.append($(`<option value="` + clients[i] + `">` + clients[i] + `</option>`));
        }
      }
    });
});

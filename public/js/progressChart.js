
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
            url: "/api/progressUrl",
            complete: function (response) {
                let jsonRes = response.responseJSON;
                let requestUrl = jsonRes.recordsTotal;
                let progressUrl = jsonRes.progressUrl;
                let completeUrl = jsonRes.completeUrl;
                let top_list = "";
                let topoffenders = jsonRes['topoffenders'];
                $('#requestUrl').text(requestUrl);
                $('#progressUrl').text(progressUrl);
                $('#completeUrl').text(completeUrl);
                for (var i = 1; i < 4; i++) {
                    if (topoffenders[i - 1]) {
                        top_list += '<li>' + topoffenders[i - 1]['_id'] + '<span>' + topoffenders[i - 1]['count'] + 'links</span></li>';
                    }
                }
                $('#top-list').html(top_list);
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
});

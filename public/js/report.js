$(document).ready(function () {
    
    // let country_table_head="<th>Country</th><th>Proposals Issued</th><th>Invoice Issued</th><th>Payments Collected</th>"
    // let default_table_head="<th>Staff Email</th><th>Staff Name</th><th>Country</th><th>Proposals Issued</th><th>Invoice Issued</th><th>Payments Collected</th>"
    // let defaultMode={
    //     mode:3
    // }
    // getStaffData(defaultMode)
    // $('#country-check').change(function() {
    //     let viewMode
    //     if ($(this).is(':checked')) {
    //         $('#staff-head').html(country_table_head)
    //         $('#staff-check').prop('checked',false)
    //         viewMode={
    //             mode:1
    //         }
    //     } else {
    //         $('#staff-head').html(default_table_head)
    //         viewMode=defaultMode
    //     }
    //     getStaffData(viewMode)
    // });
    // $('#staff-check').change(function() {
    //     let viewMode
    //     if ($(this).is(':checked')) {
    //         $('#staff-head').html(default_table_head)
    //         $('#country-check').prop('checked',false)
    //         viewMode={
    //             mode:2
    //         }
    //     } else {
    //         viewMode=defaultMode
    //     }
    //     getStaffData(viewMode)
    // })
    // function getStaffData(params){
    //     $.ajax({
    //         url: '/api/getStaffData',
    //         type: 'POST',
    //         dataType: 'json',
    //         contentType: 'application/json',
    //         data:JSON.stringify(params),
    //         success: function(res) {
    //             let tableData=""
    //             res.map((item)=>{
    //                 tableData+="<tr>"
    //                 tableData+="<td>"+item._id+"</td>"
    //                 if(params.mode!=1){
    //                     tableData+="<td>"+item.name+"</td>"
    //                     tableData+="<td>"+item.region+"</td>"
    //                 }
    //                 tableData+="<td>"+item.count+"</td>"
    //                 tableData+="<td>"+12+"</td>"
    //                 tableData+="<td>"+16+"</td>"
    //                 tableData+="</tr>"
    //             })
    //             $('#staff-data').html(tableData)
    //         },
    //         error: function(xhr, status, error) {
    //           alert(error)
    //         }
    //       });
    // }

    var display = $('#display').val();
    console.log(display);
    let table = $("#tbl_staff").DataTable({
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
          ],
        
        processing: true,
        serverSide: true,
        ajax:{ url :  "/api/getStaffData",
        "data" : function(d){
            d.display = $('#display').val();
            d.dateRange = $('#staff-date-range').val();
        },
        complete: function(response){
          console.log(response);
          //response = JSON.parse(response);
          //callback(response);
          var jsonRes=response.responseJSON;
          console.log(jsonRes);
        },
        },
        columns: [
          { name: "id", data: "id", visible: false },
          { name: "country", data: "country", visible: display < 2 ? true : false },
          { name: "staff_email", data: "staff_email", visible: display > 1 ? true : false },
          { 
            name: "staff_name", 
            data: "staff_name",
            visible: display > 1 ? true : false 
            //render : function (data,type,row) {
               
            //}
          },
          {
            name: "proposals_issued",
            data: "proposals_issued",
          },
          {
            name: "invoices_issued",
            data: "invoices_issued",
          },
          {
            name: "payments_collected",
            data: "payments_collected",
            
          },
        ],
      });

    
    $('#country-check').click(function(){
        if($('#display').val() != 1){
            $('#display').val(1);
            table.columns(1).visible(true);
            table.columns(2).visible(false);
            table.columns(3).visible(false);
            table.draw();
            display = 1;

        }

    });

    $('#staff-check').click(function(){
        if($('#display').val() != 2){
            $('#display').val(2);
            table.columns(1).visible(false);
            table.columns(2).visible(true);
            table.columns(3).visible(true);
            table.draw();
            display = 2;

        }
    });

    $('#staff-date-range').change(function(){
      table.draw();
    })
});
    
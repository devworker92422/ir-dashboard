
var user_roles = ["Super Admin" , "Admin" , "Staff"]
$('#btn_add_modal').click(function(){
  $('#add_new_modal').modal();
});

$('#btn_cancel').click(function(){
  $('#add_new_modal').modal('hide');
});

$('#btn_add').click(function(){
  let email = $('#email').val();
  let name = $('#name').val();
  let role = $('#role').val();
  let region = $('#region').val();
  if(email =='' || name == '' || region == ''){
    alert('Please insert valid information and try again.');
  }
  else{
    $.ajax({
      url: '/api/addNewStaff',
      type: 'POST',
      contentType : 'application/json',
      data: JSON.stringify({
        'email' : email,
        'name' : name,
        'role' : role,
        'region' : region
      }),
      success: function(response) {
        // Handle successful response
        let data = JSON.parse(response)
        if(data['status'] == 'fail'){
          alert(data['message'])
        }
        else{
          $('#add_new_modal').modal('hide');
          table.draw(false);
        }
      },
      error: function(xhr, status, error) {
        // Handle error response
        console.log(xhr.responseText);
      }
    });
  }
})

function editStaff(obj){
  $('.btn-warning').addClass('hidden');
  $('.btn-danger').addClass('hidden');
  let action_col = obj.parentElement;
  let row = action_col.parentElement;
  let id = row.id;
  let staff_email = row.children[0].innerHTML;
  let staff_name = row.children[1].innerHTML;
  let user_role = row.children[2].innerHTML;
  let region = row.children[3].innerHTML;
  let action = action_col.innerHTML;
  ex_data = {
    'staff_email' : staff_email,
    'staff_name' : staff_name,
    'user_role' : user_role,
    'region' : region,
    'action' : action
  }
  row.children[0].innerHTML = `<input type='text' value='${staff_email}' id='edt_email'>`;
  row.children[1].innerHTML = `<input type='text' value='${staff_name}' id='edt_staffname'>`;
  let role_sel = "<select type='text' id='edt_userrole'><option value='0'>None</option>";
  for(var i=0;i<user_roles.length;i++){
    role_sel += "<option value='" + (i+1) + "'" + (user_roles[i] == user_role ? "selected" : "") +  ">" + user_roles[i] + "</option>"
  }
  role_sel += "</select>";
  row.children[2].innerHTML = role_sel;
  row.children[3].innerHTML = `<input type='text' value='${region}' id='edt_region'>`;
  row.children[4].innerHTML = `<button class="btn-success" onclick="saveStaff(this)">Save</button>
  <button class="btn-danger" onclick="cancelAction(this)">Cancel</button>`;

  }


function removeStaff(obj){
  let action_col = obj.parentElement;
  let row = action_col.parentElement;
  let id = row.id;
  //alert
  var result = confirm("Are you sure you want to remove this staff?");
  if(result){
    $.ajax({
      url: '/api/removeStaff',
      type: 'POST',
      contentType : 'application/json',
      data: JSON.stringify({
        'id' : id,
      }),
      success: function(response) {
        // Handle successful response
        table.draw(false);
        console.log(response);
      },
      error: function(xhr, status, error) {
        // Handle error response
        console.log(xhr.responseText);
      }
    });
  }

}

function saveStaff(obj){
  let action_col = obj.parentElement;
  let row = action_col.parentElement;
  let id = row.id;
  $.ajax({
    url: '/api/saveStaff',
    type: 'POST',
    data: JSON.stringify({
      'id' : id,
      'email' : $('#edt_email').val(), 
      'name' : $('#edt_staffname').val(),
      'role' : $('#edt_userrole').val(),
      'region' : $('#edt_region').val(),
    }),
    contentType : 'application/json',
    success: function(response) {
      // Handle successful response
      //console.log(response);
      table.draw(false);
    },
    error: function(xhr, status, error) {
      // Handle error response
      console.log(xhr.responseText);
    }
  });
}


function cancelAction(obj){
  let action_col = obj.parentElement;
  let row = action_col.parentElement;
  
  row.children[0].innerHTML = ex_data['staff_email'];
  row.children[1].innerHTML = ex_data['staff_name'];
  row.children[2].innerHTML = ex_data['user_role'];
  row.children[3].innerHTML = ex_data['region'];
  row.children[4].innerHTML = `<button class="btn-warning" onclick="editStaff(this)">Edit</button>
  <button class="btn-danger" onclick="removeStaff(this)">Remove</button>`;
  $('.btn-warning').removeClass('hidden');
  $('.btn-danger').removeClass('hidden');
}

var table;
var ex_data;
$(document).ready(function () {
    table = $("#tbl_staff").DataTable({
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
        ajax:{ url :  "/api/getAllStaffs",
        complete: function(response){
          console.log(response);
          //response = JSON.parse(response);
          //callback(response);
          var jsonRes=response.responseJSON;
          console.log(jsonRes);
        },
        },
        rowId : 'id',
        columns: [
          { name: "id", data: "id", visible: false },
          { name: "staff_email", data: "email", visible: true},
          { 
            name: "staff_name", 
            data: "name",
            visible: true 
            //render : function (data,type,row) {
               
            //}
          },
          {
            name: "role",
            data: "role",
            render : function(data,type,row){
              switch (data) {
                case 1:
                  return 'Super Admin';
                case 2:
                  return 'Admin';
                case 3:
                  return 'Staff';
                default:
                  return '';
              }
            }
          },
          {
            name: "region",
            data: "region",
          },
          {
            name: "action",
            render: function(data,type,row){
              return `<button class="btn-warning" onclick="editStaff(this)">Edit</button>
              <button class="btn-danger" onclick="removeStaff(this)">Remove</button>`;
            }
            
          },
        ],
      });



      
    
    
});
    
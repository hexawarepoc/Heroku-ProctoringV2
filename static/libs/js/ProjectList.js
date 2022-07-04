var count=1;
if ($("#logged_in_user_roe").val() == "") {
   location.href = "/login.html";
}
$(document).ready(function() {
$('#loader').removeClass('hidden');
fetch(URL.baseUrl + '/ProjectListData/1').then(response => response.json())
   .then((completedata) => {
      $('#loader').addClass('hidden');
      if(completedata.length >0)
      {
      AgentListData(completedata);
      }
      }).catch((err) => {
       console.log(err)
       location.href = "/Error";
      }); 
});
function AgentListData(data)
{
     var agentData=null;
     $.each(data, function (key, row) {
     var projectListData='<div class="col-xl-6 col-lg-6 col-md-6 col-sm-12 col-12">'+
      '<div class="card"><div class="card-header d-flex"><h4 class="mb-0">'+
      '<a onclick=Navigate("'+row.project_name+'")>'+row.project_name +'</a></h4>'+
      '<div class="dropdown ml-auto">'+
      '<a class="toolbar" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
      '<i class="mdi mdi-dots-vertical"></i></a>'+
      '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuLink">'+
      '<a class="dropdown-item" href="#">Action</a>'+
      '<a class="dropdown-item" href="#">Another action</a>'+
      '<a class="dropdown-item" href="#">Something else here</a></div></div></div>'+
      '<div class="card-body">'+
      '<ul class="social-sales list-group list-group-flush">'+
      '<li class="list-group-item social-sales-content pt-0 pb-0">'+
      '<div class="product-colors">'+
      '<h4>Agents</h4>'+
      '<div class="row" id="agentData'+row.project_id+'"></div>'+
      '</div></li>'+
      '<li class="list-group-item social-sales-content pt-0 pb-0">'+
      '<div class="product-colors">'+
      '<h4>Supervisors</h4>'+
      '<div class="row" id="supervisorlistData'+row.project_id+'"></div></div></div></li></ul></div></div></div>';
      $('#ESData').append(projectListData);
      $.each(row.agent, function (key,RowData){
        $('#agentData'+row.project_id).append('<div class="col-xl-1 col-lg-1 col-md-1 col-sm-12 col-12"><div class="avatarcircle1"><span class="initials">'+RowData+'</span></div></div>');
      });
      $.each(row.supervisorlist, function (key,RowData) {
        $('#supervisorlistData'+row.project_id).append('<div class="col-xl-1 col-lg-1 col-md-1 col-sm-12 col-12"><div class="avatarcircle1"><span class="initials">'+RowData+'</span></div></div>');
     });
      });
}

if ($("#logged_in_user_role").val() == "super_admin") {
  $("#ConfigurationsMenu").show();
} else {
  $("#ConfigurationsMenu").hide();
}
if ($("#logged_in_user_role").val() == "") {
  location.href = "/login.html";
}
function Navigate(project) {
  location.href = "/ProjectAgentList.html$project=" + project;
}
jQuery(function ($) {
  var path = window.location.href;
  $('.nav-link').each(function () {
     if (this.href === path) {
        $(this).addClass('active');
     }
  });
});
function LogOut() {
  $("#logged_in_user_role").val("");
  location.href = "/LogOut";
}
$('#loader').removeClass('hidden');
fetch(URL.baseUrl + '/ViolationMgmt/1').then(response => response.json())
       .then((completedata) => {
         $('#loader').addClass('hidden');
         if(completedata.length> 0 || completedata.total_rows > 0)
         {
         $.jqPaginator('#pagination1', {
            totalPages: Math.ceil(completedata.total_rows/10),         
            visiblePages:5,
            currentPage: 1,
            prev: '<li class="page-item "><span class="page-link"><a href="javascript:;">Previous</a></span></li>',
            next: '<li class="page-item"><span class="page-link"><a href="javascript:;">Next</a></span></li>',
            page: '<li class="page-item" aria-current="page" id="page{{page}}"><span class="page-link"><a href="javascript:;">{{page}}</a></span></li>',
            onPageChange: function (num, type) {
            $("#page"+num).addClass('active');  
            if(type=="change")
            {
               $('#loader').removeClass('hidden');
               fetch(URL.baseUrl + '/ViolationMgmt/'+num).then(response => response.json())
               .then((NewData) => {
                  $('#loader').addClass('hidden');
                  ViolationMgmt(NewData.data);
               }).catch((err) => {
                  location.href = "/Error";
               });
            }
            else 
            {
                 ViolationMgmt(completedata.data);
            } 
            }
         });
          }
       }).catch((err) => {
           location.href = "/Error";
   });
function ViolationMgmt(data)
{
   $("#AgentsData tr").remove();
   $.each(data, function (key, row) {
      $('#AgentsData').append('<tr><td>' + row.violation_type + '</td><td>' + row.user_name + '</td>' +
         '<td><label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" id="FP_' + row.user_id + '" type="radio" name="markas" onclick=radio_func("FP_' + row._id + '_' + row.user_id + '")>' +
         '<span class="custom-control-label">FP</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" id="ES_' + row.user_id + '" type="radio" name="markas" onclick=radio_func("ES_' + row._id + '_' + row.user_id + '")>' +
         '<span class="custom-control-label">ES</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" id="NA_' + row.user_id + '" type="radio" name="markas" onclick=radio_func("NA_' + row._id + '_' + row.user_id + '")>' +
         '<span class="custom-control-label">NA</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" id="VI_' + row.user_id + '" type="radio" name="markas" onclick=radio_func("VI_' + row._id + '_' + row.user_id + '")>' +
         '<span class="custom-control-label">VI</span></label></td>' +
         '<td><a data-toggle="collapse" data-target="#row_id' +row._id+ '" class="accordion-toggle">View  ' +
         '<i class="fa fa-fw fas fa-angle-down"></i></a></td></tr>' +
         '<tr class="p"><td colspan="6" class="hiddenRow pb-0">' +
         '<div class="accordian-body collapse p-3" id="row_id' +row._id+ '">' +
         '<div class="row"><div class="col-xl-6 col-lg-6 col-md-12 col-sm-12 col-12 col-lg-6 col-md-6 col-sm-12 col-12">' +
         '<div class="card">' +
         '<div class="card-header">' +
         '<h6 class="card-title mb-2">' + row.violation_type + '</h6>' +
         '<div class="card-body">' +
         '<img class="img-fluid" src="data:image/png;base64,' + row.violation_image + '" alt="Card image cap"></div></div></div></div>' +
         '<div class="col-xl-6 col-lg-6 col-md-12 col-sm-12 col-12 col-lg-6 col-md-6 col-sm-12 col-12">' +
         '<label>Created Date : <span>' + row.created_date + '</span></label></br>' +
         '<label>Project Name : <span>' + row.project_name + '</span> </label></br>' +
         '</div></div></div></td></tr>'
      );
   });
}
if ($("#logged_in_user_role").val() == "") {
    location.href = "/login.html";
}
if ($("#logged_in_user_role").val() == "super_admin") {
    $("#ConfigurationsMenu").show();
 } else {
    $("#ConfigurationsMenu").hide();
 }
 
 fetch(URL.baseUrl + '/GetViolation').
 then(response => response.json()).
 then((completedata) => {
    $.each(completedata, function (key, val) {
       $("#violation").append($("<option/>").val(val).text(val));
    })
}).catch((err) => {
   location.href = "/Error";
});

 $('#FormViolationPost').on('submit', function (e) {
    if ($("#logged_in_user_role").val() == "") {
       location.href = "/login.html";
    }
    $('#loader').removeClass('hidden')
    e.preventDefault();
    var violationData={};
    var data = {
       name: $('#name').val(),
       violation: $('#violation').val(),
       pageNo:1
    }
    var csrf_token = $("#csrf_token").val();
    $.ajax({
       type: "POST",
       url: URL.baseUrl + '/FilterbyViolation',
       beforeSend: function (request) {
          request.setRequestHeader("X-CSRFToken", csrf_token);
       },
       data: data,
       success: function (data) {
         violationData = JSON.parse(data);
         $('#loader').addClass('hidden');
         if(violationData.length > 0 || violationData.total_rows > 0)
         {
           $.jqPaginator('#pagination1', {
            totalPages: Math.ceil(violationData.total_rows/10),         
            visiblePages:5,
            currentPage: 1,
            prev: '<li class="page-item "><span class="page-link"><a href="javascript:;">Previous</a></span></li>',
            next: '<li class="page-item"><span class="page-link"><a href="javascript:;">Next</a></span></li>',
            page: '<li class="page-item" aria-current="page" id="page{{page}}"><span class="page-link"><a href="javascript:;">{{page}}</a></span></li>',
            onPageChange: function (num, type) {
            $("#page"+num).addClass('active');  
            if(type=="change")
            {
                $('#loader').removeClass('hidden');
                var data = {
                  name: $('#name').val(),
                  violation: $('#violation').val(),
                  pageNo:num
               }
               var csrf_token = $("#csrf_token").val();
               $.ajax({
                  type: "POST",
                  url: URL.baseUrl + '/FilterbyViolation',
                  beforeSend: function (request) {
                     request.setRequestHeader("X-CSRFToken", csrf_token);
                  },
                  data: data,
                  success: function (data) {
                  $('#loader').addClass('hidden');
                  violationData = JSON.parse(data);
                  ViolationMgmt(violationData.data);
                  }
               }).catch((err) => {
                  location.href = "/Error";
            });
            }
            else 
            {
               ViolationMgmt(violationData.data)
            } 
            }
         });
         }
         else
         {
            $("#AgentsData tr").remove();
         }
       },
       failure: function () {}
    });
    
 });
 function navigate1() {
    location.href = "/";
 }
 function navigate2() {
    location.href = "/agentdetails_home";
 }
 
 function navigate3() {
    location.href = "/onboarded_agents";
 }
 
 function navigate4() {
    location.href = "/user_management";
 }
 
 function navigate5() {
    location.href = "";
 }
 
 function navigate6() {
    location.href = "/configuration";
 }

function EsTableData() {
    if ($("#logged_in_user_role").val() == "") {
       location.href = "/login.html";
}
function GetEscalatedAgentsData(data)
{
   $("#ESData tr").remove();
   $.each(data, function (key, row) {
      $('#ESData').append('<tr data-toggle="collapse" data-target="#row_id' + row._id + '" class="accordion-toggle">' +
         '<td>' + row.violation_type + '</td>' +
         '<td>' + row.user_name + '</td>' +
         '<td><label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" disabled id="FP_' + row.user_id + '" type="radio" name="markas" onclick="radio_func("FP_' + row._id + '")>' +
         '<span class="custom-control-label">FP</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" disabled  type="radio" checked onclick=radio_func("ES_' + row._id + '")>' +
         '<span class="custom-control-label">ES</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" disabled id="NA_' + row.user_id + '" type="radio" name="markas" onclick="radio_func("NA' + row._id + '")">' +
         '<span class="custom-control-label">NA</span></label>' +
         '<label class="custom-control custom-radio custom-control-inline">' +
         '<input class="custom-control-input" disabled id="VI_' + row.user_id + '" type="radio" name="markas" onclick="radio_func("VI_' + row._id + '")"">' +
         '<span class="custom-control-label">VI</span></label></td><td>' + row.escalated_by + '</td><td>' +
         '<a data-toggle="collapse" data-target="#row_id' + row._id + '" class="accordion-toggle">View  <i class="fa fa-fw fas fa-angle-down"></i></a></td></tr>' +
         '<tr class="p"><td colspan="6" class="hiddenRow"><div class="accordian-body collapse p-3" id="row_id' + row._id + '"><div class="row">' +
         '<div class="col-xl-6 col-lg-6 col-md-12 col-sm-12 col-12 col-lg-6 col-md-6 col-sm-12 col-12"><div class="card">' +
         '<div class="card-header">' +
         '<h6 class="card-title mb-2">' + row.violation_type + '</h6>' +
         '<div class="card-body">' +
         '<img class="img-fluid" src="data:image/png;base64,' + row.violation_image + '" alt="Card image cap"></div></div></div></div>' +
         '<div class="col-xl-6 col-lg-6 col-md-12 col-sm-12 col-12 col-lg-6 col-md-6 col-sm-12 col-12">' +
         '<label>Created Date : <span>' + row.created_date + '</span></label></br>' +
         '<label>Project Name : <span>' + row.project_name + '</span> </label></br>' +
         '</div></div></div></td></tr>'
      );
   });
}
$('#loader').removeClass('hidden');
    fetch(URL.baseUrl + '/escalated_agents/1').then(response => response.json())
       .then((completedata) => {
         $('#loader').addClass('hidden');
         if(completedata.length> 0 || completedata.total_rows > 0)
         {
         $.jqPaginator('#pagination2', {
            totalPages: Math.ceil(completedata.total_rows/10),         
            visiblePages:5,
            currentPage: 1,
            prev: '<li class="page-item "><span class="page-link"><a href="javascript:;">Previous</a></span></li>',
            next: '<li class="page-item"><span class="page-link"><a href="javascript:;">Next</a></span></li>',
            page: '<li class="page-item" aria-current="page" id="page{{page}}"><span class="page-link"><a href="javascript:;">{{page}}</a></span></li>',
            onPageChange: function (num, type) {
            $("#page"+num).addClass('active');  
            if(type=="change")
            {
                $('#loader').removeClass('hidden');
                fetch(URL.baseUrl + '/escalated_agents/'+num).then(response => response.json())
               .then((NewData) => {
                  $('#loader').addClass('hidden');
                  GetEscalatedAgentsData(NewData.data);
               }).catch((err) => {
                  location.href = "/Error";
            });
            }
            else 
            {
                 GetEscalatedAgentsData(completedata.data)
            } 
            }
         });
         }
       }).catch((err) => {
          console.log(err);
       })
 }
 var statusVal = null;
function radio_func(val) {
    $('#MyModal').modal('show');
    statusVal = val;
 }
function saveStatus() {
    $('#loader').removeClass('hidden')
    $('#MyModal').modal('hide');
    const myArray = statusVal.split("_");
    var val1 = myArray[0];
    var val2 = myArray[1];
    var val3 = myArray[2];
    var Url = URL.baseUrl + "/ViolationMgmt/" + val2 + "/" + val1 + "/" + val3;
    $.get(Url, function (data) {
       $('#loader').addClass('hidden')
    });
    location.reload()
 }
 function show_image(val) {
    fetch(URL.baseUrl + '/onboarded_images/' + val).then(response => response.json()).then((completedata) => {
       let AgentImage = "";
       AgentImage = '<img src="data:image/png;base64,' + completedata.user_img + '" alt="Red dot" width="200" height="180">'
       document.getElementById(var1).innerHTML = AgentImage;
    }).catch((err) => {
      location.href = "/Error";
});
 }
 function LogOut() {
    $("#logged_in_user_role").val("");
    location.href = "/LogOut";
 }
 jQuery(function ($) {
    var path = window.location.href;
    $('.nav-link').each(function () {
       if (this.href === path) {
          $(this).addClass('active');
       }
    });
 });
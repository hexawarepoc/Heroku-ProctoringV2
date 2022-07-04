$('#loader').removeClass('hidden')
fetch(URL.baseUrl + '/UserManagement/1').then(response => response.json())
   .then((completedata) => {
      debugger;
      $('#loader').addClass('hidden');
      if(completedata.length>0 ||completedata.total_rows > 0)
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
            fetch(URL.baseUrl + '/UserManagement/'+num).then(response => response.json())
           .then((NewData) => {
            $('#loader').addClass('hidden');
            if(NewData.length>0 || NewData.total_rows > 0)
            {
              AgentsData(NewData.data);
            }
           }).catch((err) => {
             location.href = "/Error";
           });
        }
        else 
        {
             AgentsData(completedata.data)
        } 
        }
     });
   }
   }).catch((err) => {
     location.href = "/Error";
});
function AgentsData(data) {
$("#AgentsData tr").remove();
$.each(data, function (key, row) {
$('#AgentsData').append('<tr id="trcontent" onload="clickEventcards()">' +
         '<td>' + row.user_id + '</td>' +
         '<td>' + row.user_name + '</td>' +
         '<td>' + row.project_name + '</td>' +
         '<td>' + row.login_time + '</td>' +
         '<td>' + row.logout_time + '</td>' +
         '<td>' + row.session_status + '</td></tr>');
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
 if ($("#logged_in_user_role").val() == "supervisor") {
   $("#fProject").prop("disabled", true);
 }
 fetch(URL.baseUrl + '/GetProjectName').
 then(response => response.json()).
 then((completedata) => {
    $.each(completedata, function (key, val) {
       $("#fProject").append($("<option/>").val(val).text(val));
    })
});
 $('#FormUserMang').on('submit', function (e) {
    var FilterbyAgentsData={};
    $('#loader').removeClass('hidden')
    e.preventDefault();

    var data = {
       fname: $('#fname').val(),
       fProject:$('#fProject').val(),
       pageNo:1
    }
    var csrf_token = $("#csrf_token").val();
    $.ajax({
       type: "POST",
       url: URL.baseUrl + '/FilterbyAgents',
       beforeSend: function (request) {
          request.setRequestHeader("X-CSRFToken", csrf_token);
       },
       data: data,
       success: function (data) {
          $('#loader').addClass('hidden');
          var FilterbyAgentsData = JSON.parse(data);
          if(FilterbyAgentsData.length>0 ||FilterbyAgentsData.total_rows > 0)
          {
            $.jqPaginator('#pagination1', {
             totalPages: Math.ceil(FilterbyAgentsData.total_rows/10),         
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
                  fname: $('#fname').val(),
                  fProject:$('#fProject').val(),
                  pageNo:num
                }
                var csrf_token = $("#csrf_token").val();
                $.ajax({
                   type: "POST",
                   url: URL.baseUrl + '/FilterbyAgents',
                   beforeSend: function (request) {
                      request.setRequestHeader("X-CSRFToken", csrf_token);
                   },
                   data: data,
                   success: function (data) {
                   $('#loader').addClass('hidden');
                   if( data.length > 0 ||  data.total_rows > 0)
                   {
                   FilterbyAgentsData = JSON.parse(data);
                   AgentsData(FilterbyAgentsData.data);
                   }
                   }
                })
             }
             else 
             {
               AgentsData(FilterbyAgentsData.data)
             } 
             }
          });
          }
          else
          {
             $("#AgentsData tr").remove();
          }
       },
       failure: function () {
         location.href = "/Error";
       }
    });
 });
 
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
    location.href = "";
 }
 
 function navigate5() {
    location.href = "/violation_management";
 }
 
 function navigate6() {
    location.href = "/configuration";
 }
 function userLiveData(completedata) {
   $("#ESData tr").remove();
   $.each(completedata, function (key, row) {
         $('#ESData').append('<tr>' +
         '<td>' + row.user_name + '</td>' +
         '<td>' + row.project_name + '</td>' +
         '<td><span class="logged-in">●</span></td>' +
         '<td> ' + row.login_time + ' </td>' +
         '</tr>');
   });
 }
function EsTableData() {
   var user_live={};
   $('#loader').removeClass('hidden')
   fetch(URL.baseUrl + '/user_live/1').then(response => response.json())
      .then((completedata) => {
         user_live=completedata;
        $('#loader').addClass('hidden');
        if(user_live.length>0 || user_live.total_rows >0)
        {
        $.jqPaginator('#pagination2', {
           totalPages: Math.ceil(user_live.total_rows/10),         
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
               fetch(URL.baseUrl + '/user_live/'+num).then(response => response.json())
              .then((NewData) => {
                 $('#loader').addClass('hidden');
                 if(NewData.total_rows >0)
                 {
                 userLiveData(NewData.data);
                 }
              }).catch((err) => {
               location.href = "/Error";
              });
           }
           else 
           {
                 userLiveData(user_live.data)
           } 
           }
        });
      }
      }).catch((err) => {
         location.href = "/Error";
       });
}
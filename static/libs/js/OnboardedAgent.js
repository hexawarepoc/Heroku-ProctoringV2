function notify(message, type){
   $.growl({
       message: message
   },{
       type: type,
       allow_dismiss: false,
       label: 'Cancel',
       className: 'btn-xs btn-inverse',
       placement: {
           from: 'top',
           align: 'right'
       },
       delay: 4000,
       animate: {
               enter: 'animated fadeInRight',
               exit: 'animated fadeOutRight'
       },
       offset: {
           x: 30,
           y: 30
       }
   });
};
var ExcelDataList=null;
var ExcelToJSON = function() {
   this.parseExcel = function(file) {
     var reader = new FileReader();
 
     reader.onload = function(e) {
       var data = e.target.result;
       var workbook = XLSX.read(data, {
         type: 'binary'
       });
       workbook.SheetNames.forEach(function(sheetName) {
         var XL_row_object = XLSX.utils.sheet_to_row_object_array(workbook.Sheets[sheetName]);
         ExcelDataList = JSON.parse(JSON.stringify(XL_row_object));
         var files=$('#FileExcel').val();
         if (!(/\.(xlsx|xls|xlsm)$/i).test(files)) {
            $("#ErrFileExcel").text("Please upload valid excel file .xlsx, .xlsm, .xls only.");
            $("#FileExcel").val('');
            return;
         }
         $('#loader').removeClass('hidden');
         var js_data = JSON.stringify(ExcelDataList);
         var csrf_token = $("#csrf_token").val();
         $.ajax({
         type: "POST",
         url: URL.baseUrl + '/UploadExcel',
         data: js_data,
         contentType: 'application/json',
         cache: false,
         dataType : 'json',
         processData: false,
         beforeSend: function (request) {
               request.setRequestHeader("X-CSRFToken", csrf_token);
         },
        success: function (data) {
        $('#loader').addClass('hidden');
        $('#UploadExcelModal').modal('hide'); 
        notify("Excel Uploaded Successfully");
        //location.reload();
        OnboardedAgentPageLoadData();
      },
      failure: function () {
         $("#FileExcel").val('');
         $('#UploadExcelModal').modal('hide'); 
         location.href = "/Error";
      }
      });
      })
     };
     reader.onerror = function(ex) {
       console.log(ex);
     };
 
     reader.readAsBinaryString(file);
   };
 };

 function handleFileSelect(evt) {
   var files = evt.target.files; // FileList object
  var xl2json = new ExcelToJSON();
  xl2json.parseExcel(files[0]);
 }
 document.getElementById('FileExcel').addEventListener('change', handleFileSelect, false);
 OnboardedAgentPageLoadData();
function OnboardedAgentPageLoadData()
{
   $('#loader').removeClass('hidden');
   fetch(URL.baseUrl + '/OnboardedAgent/1').then(response => response.json())
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
                  fetch(URL.baseUrl + '/OnboardedAgent/'+num).then(response => response.json())
                  .then((NewData) => {
                    $('#loader').addClass('hidden');
                     OnboardedAgentData(NewData.data);
                  }).catch((err) => {
                     location.href = "/Error";
               });
               }
               else 
               {
                  OnboardedAgentData(completedata.data);
               } 
               }
            });
            }
          }).catch((err) => {
            location.href = "/Error";
   }).catch((err) => {
      location.href = "/Error";
   });
   
}
function OnboardedAgentData(data){
   $("#ESData tr").remove();
   $.each(data, function (key, row) {
      var facial_img="";
      if(row.facial_img)
      {
         facial_img="data:image/png;base64,"+row.facial_img;
      }
      else
      {
         facial_img="static\\images\\NoImage.png";
      }
      $('#ESData').append('<tr data-toggle="collapse" data-target="#' + row.user_id + '" class="accordion-toggle">' +
         '<td>' + row.user_id + '</td>' +
         '<td>' + row.user_name + '</td>' +
         '<td>' + row.onboarding_date + '</td>' +
         '<td>' + row.expiration_date + '</td>' +
         '<td><a data-toggle="collapse" data-target="#' + row.user_id + '"class="accordion-toggle">View  ' +
         '<i class="fa fa-fw fas fa-angle-down"></i></a></td>' +
         '<td>' + row.status + '</td></tr>' +
         '<tr class="p"><td colspan="6" class="hiddenRow">' +
         '<div class="accordian-body collapse p-3" id="' + row.user_id + '">' +
         '<div class="row"><div class="col-xl-6 col-lg-6 col-md-12 col-sm-12 col-12 col-lg-6 col-md-6 col-sm-12 col-12">' +
         '<div class="card"><div class="card-header"><h6 class="card-title mb-2">Face Scan</h6>' +
         '<div class="card-body"><img class="img-fluid" src='+facial_img+' alt="Card image cap">' +
         '</div></div></div></div></div></div></td></tr>');
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
 
 function LogOut() {
    $("#logged_in_user_role").val("");
    location.href = "/LogOut";
 }
 var OnboardedAgentDataVal={};
 jQuery(function ($) {
    var path = window.location.href;
    $('.nav-link').each(function () {
       if (this.href === path) {
          $(this).addClass('active');
       }
    });
    $('#FormOnboard').on('submit', function (e) {
       $('#loader').removeClass('hidden')
       e.preventDefault();
       var data = {
          fname: $('#fname').val(),
          fstatus: $('#fstatus').val(),
          pageNo:1
       }
       var csrf_token = $("#csrf_token").val();
       $.ajax({
          type: "POST",
          url: URL.baseUrl + '/FilterOnboardedAgent',
          beforeSend: function (request) {
             request.setRequestHeader("X-CSRFToken", csrf_token);
          },
          data: data,
          success: function (data) {
             OnboardedAgentDataVal = JSON.parse(data);
             $('#loader').addClass('hidden');
             if(OnboardedAgentDataVal.length > 0 || OnboardedAgentDataVal.total_rows > 0)
             {
               $.jqPaginator('#pagination1', {
                totalPages: Math.ceil(OnboardedAgentDataVal.total_rows/10),         
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
                     fstatus: $('#fstatus').val(),
                     pageNo:num
                   }
                   var csrf_token = $("#csrf_token").val();
                   $.ajax({
                      type: "POST",
                      url: URL.baseUrl + '/FilterOnboardedAgent',
                      beforeSend: function (request) {
                         request.setRequestHeader("X-CSRFToken", csrf_token);
                      },
                      data: data,
                      success: function (data) {
                      $('#loader').addClass('hidden');
                      OnboardedAgentDataVal = JSON.parse(data);
                      OnboardedAgentData(OnboardedAgentDataVal.data);
                      }
                   })
                }
                else 
                {
                  OnboardedAgentData(OnboardedAgentDataVal.data)
                } 
                }
             });
             }
             else
             {
                $("#AgentsData tr").remove();
                $("#ESData tr").remove();
             }
          },
          failure: function () {
            location.href = "/Error";
          }
       });
       
    });
 
 });
 
 function trcontent() {
 
 }
 
 function navigate1() {
    location.href = "/";
 }
 
 function navigate2() {
    location.href = "/agentdetails_home";
 }
 
 function navigate2() {
    location.href = "";
 }
 
 function navigate4() {
    location.href = "/user_management";
 }
 
 function navigate5() {
    location.href = "/violation_management";
 }
 
 function navigate6() {
    location.href = "/configuration";
 } 
function UploadFileModal() {
  $('#UploadFileModal').modal('show'); 
}
var arr = [];
$("#FileImage").change(function(){
   var input = document.getElementById('FileImage');
   var file = input.files;
   var total = file.length;
   [].forEach.call(file, function(file,index) {
      var reader = new FileReader();
      reader.onloadend = function() {
       var Image= reader.result.split(',');
       obj = {
         image:Image[1],
         emp_id:file.name.replace('.jpg', '').replace('.png', '')
       };
       arr.push(obj);
       if (index === total - 1) {
         UploadImage(arr);
       }
      }
      reader.readAsDataURL(file);
      
  });
});

function UploadImage(arr)
{  
   var files=$('#FileImage').val();
   if (!(/\.(jpg|jpeg|png)$/i).test(files)) {
      $("#ErrFileImage").text("Please upload valid image file .jpg, .jpeg, .png only.");
      $("#FileImage").val('');
      return;
   }
   if(!$("#FileExcel").val())
   {
      $("#ErrFileImage").text("Please upload excel file with agent details before uploading facial images.");
      $("#FileImage").val('');
      return;
   }
   $('#loader').removeClass('hidden');
   var js_data =JSON.stringify(arr);
   var csrf_token = $("#csrf_token").val();
   $.ajax({
     type: "POST",
     url: URL.baseUrl + '/UploadImage',
     data: js_data,
     contentType: 'application/json',
     cache: false,
     dataType : 'json',
     processData: false,
     beforeSend: function (request) {
         request.setRequestHeader("X-CSRFToken", csrf_token);
     },
     success: function (data) {
         $("#loader").addClass('hidden');
         $("#FileImage").val('');
         $("#FileExcel").val('');
         $("#UploadFileModal").modal('hide');
         $.each(data, function (key, row) {
         $('#EmpData').append('<tr>' +
            '<td>' + row + '</td>' +
            '<td>Facial data was not uploaded</td></tr>');
         });
         if(data.length > 0)
         {
         $("#UploadImgModal").modal('show'); 
         }
         else
         {
            notify("Image Uploaded Successfully");
            //location.reload();
            OnboardedAgentPageLoadData();
         }
         
     },
     failure: function () {
         $("#FileImage").val('');
         $('#UploadFileModal').modal('hide'); 
         location.href = "/Error";
      }
   });
}
function DownloadAgentTemplate()
{
   location.href = "/DownloadAgentTemplate";
}
function DownloadAgentCredentialsFile()
{
   location.href = "/DownloadAgentCredentialsFile";
}
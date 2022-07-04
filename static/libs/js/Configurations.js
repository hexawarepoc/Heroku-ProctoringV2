function Reset() {
    $('#projectName').val("");
    document.getElementById("mobile").checked = false;
    document.getElementById("book").checked = false;
    document.getElementById("multiple").checked = false;
    document.getElementById("no_person").checked = false;
 }
 jQuery(function ($) {
    var path = window.location.href;
    $('.nav-link').each(function () {
       if (this.href === path) {
          $(this).addClass('active');
       }
    });
 });
 if ($("#logged_in_user_role").val() != "super_admin") {
    location.href = "/login.html";
 } 
 $('#ConfgForm').on('submit', function (e) {
    $('#loader').removeClass('hidden')
    e.preventDefault();
    var data = {
       mobile: $('#mobile:checkbox:checked').length > 0 ? "on" : "off",
       book: $('#book:checkbox:checked').length > 0 ? "on" : "off",
       multiple: $('#multiple:checkbox:checked').length > 0 ? "on" : "off",
       no_person: $('#no_person:checkbox:checked').length > 0 ? "on" : "off",
       projectName: $('#projectName').val()
    }
    var csrf_token = $("#csrf_token").val();
    $.ajax({
       type: "POST",
       url: URL.baseUrl + '/violation_update',
       beforeSend: function (request) {
          request.setRequestHeader("X-CSRFToken", csrf_token);
       },
       data: data,
       success: function (data) {
          $('#loader').addClass('hidden')
          Reset();
          $('#MyModal').modal('show');
       },
       failure: function () {
         location.href = "/Error";
       }
    });
 });
 
 $("#projectName").change(function () {
    $('#loader').removeClass('hidden');
    fetch(URL.baseUrl + '/GetProjectByConfigurations$project=' + $("#projectName").val()).then(response => response.json())
       .then((completedata) => {
          $('#loader').addClass('hidden');
          var data = completedata.
          violation_filter;
          if (data.mobile == "on") {
             $('#mobile').prop('checked', true);
 
          } else {
             $('#mobile').prop('checked', false);
          }
          if (data.multiple_persons == "on") {
             $('#multiple').prop('checked', true);
 
          } else {
             $('#multiple').prop('checked', false);
          }
          if (data.book == "on") {
             $('#book').prop('checked', true);
 
          } else {
             $('#book').prop('checked', false);
          }
          if (data.no_person == "on") {
             $('#no_person').prop('checked', true);
 
          } else {
             $('#no_person').prop('checked', false);
          }
       }).catch((err) => {
      location.href = "/Error";
   })
 })
 function LogOut() {
    $("#logged_in_user_role").val("");
    location.href = "/LogOut";
 }
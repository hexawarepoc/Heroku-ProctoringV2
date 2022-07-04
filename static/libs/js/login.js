let formElem = document.getElementById("LoginForm");
formElem.addEventListener("submit", formSubmitHandler);

function formSubmitHandler(event) {
   event.preventDefault();
   $('#loader').removeClass('hidden')
   event.preventDefault();
   var data = {
      username: $('#username').val(),
      password: btoa($('#password').val()),
   }
   var csrf_token = $("#csrf_token").val();
   $.ajax({
      type: "POST",
      url: URL.baseUrl + '/logincheck',
      beforeSend: function (request) {
         request.setRequestHeader("X-CSRFToken", csrf_token);
      },
      data: data,
      success: function (data) {
         data = JSON.parse(data);
         $('#loader').addClass('hidden')
         if (data.Status == "Error") {
            $("#MsgText").text(data.Msg);
            $('#MyModal').modal('show');
         } else {
           // location.href = "/ProjectListData/1";
            location.href = "/index.html";
         }
      },
      failure: function () {
         location.href = "/Error";
      }
   });
}
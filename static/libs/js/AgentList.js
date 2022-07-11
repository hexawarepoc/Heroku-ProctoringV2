var flag = false;
var count=1;
if ($("#logged_in_user_role").val() == "") {
   location.href = "/login.html";
}
$('#loader').removeClass('hidden');
fetch(URL.baseUrl + '/AgentListData/1').then(response => response.json())
   .then((completedata) => {
     $('#loader').addClass('hidden');
     if(completedata.length > 0)
     {
     AgentListData(completedata);
     }
   }).catch((err) => {
      location.href = "/Error";
}).catch((err) => {
   location.href = "/Error";
});;
function AgentListData(data)
{
      $.each(data, function (key, row) {
      $('#ESData').append('<div class="col-xl-6 col-lg-6 col-md-6 col-sm-12 col-12">' +
         '<div class="card"><div class="card-body"><h5>' +
         '<span id="c3chart">' + row._id.user_name + '</span></h5> <h5><span>' + row._id.project + '</span></h5>' +
         '<div id="c3chart_gauge' + row._id.chart_name + '"></div> </div>' +
         '<div class="card-footer-item card-footer-item-bordered">' +
         '<div class="row"> <div class="col-xl-4 col-lg-4 col-md-4 col-sm-12 col-12">' +
         '<label>Total Hours</label> <h5><span>' + row.total_hours.toFixed(2) + '</span></h5> </div>' +
         '<div class="col-xl-4 col-lg-4 col-md-4 col-sm-12 col-12"> <label>Billable</label> <h5><span>' + row.billable_hours.toFixed(2) + '</span></h5></div>' +
         '<div class="col-xl-4 col-lg-4 col-md-4 col-sm-12 col-12"><label>Flags</label><h5><span>' + row.flags + '</span></h5>' +
         '</div></div></div></div></div>');
        if ($('#c3chart_gauge' + row._id.chart_name).length) {
         var chart = c3.generate({
            bindto: "#c3chart_gauge" + row._id.chart_name,
            data: {
               columns: [
                  ['data', (row.billable_hours / row.total_hours) * 100]
               ],
               type: 'gauge',
               onclick: function (d, i) {
                  console.log("onclick", d, i);
               },
               onmouseover: function (d, i) {
                  console.log("onmouseover", d, i);
               },
               onmouseout: function (d, i) {
                  console.log("onmouseout", d, i);
               },
               colors: {
                  data1: '#5969ff',
                  data2: '#ff407b',
                  data3: '#25d5f2',
                  data4: '#ffc750',
                  data5: '#2ec551',
                  data6: '#1ba3b9',

               }
            },
            gauge: {},
            size: {
               height: 320
            }
         });
      }
   })
}

$('document').ready(function () {
   if ($("#logged_in_user_role").val() == "supervisor") {
      $("#fProject").prop("disabled", true);
   }
   var date = new Date();
   var day = ("0" + date.getDate()).slice(-2);
   var monthend = ("0" + (date.getMonth() + 1)).slice(-2);
   var monthStart = ("0" + (date.getMonth())).slice(-2);
   var EndDatetoday = date.getFullYear() + "-" + (monthend) + "-" + (day);
   var StartDateToday = date.getFullYear() + "-" + (monthStart) + "-" + (day);
   document.getElementById("EndDate").defaultValue = EndDatetoday;
   document.getElementById("StartDate").defaultValue = StartDateToday;
   if ($("#logged_in_user_role").val() == "") {
      location.href = "/login.html";
   }
   if ($("#logged_in_user_role").val() == "super_admin") {
      $("#ConfigurationsMenu").show();
   } else {
      $("#ConfigurationsMenu").hide();
   }
})
jQuery(function ($) {
   var path = window.location.href;
   $('.nav-link').each(function () {
      if (this.href === path) {
         $(this).addClass('active');
      }
   });
   $('#FormAgent').on('submit', function (e) {
      $('#loader').removeClass('hidden');
      e.preventDefault();
      var StartDate = ConvertDate($('#StartDate').val());
      var EndDate = ConvertDate($('#EndDate').val());
      var data = {
         Project: $('#fProject').val(),
         fro: StartDate,
         to: EndDate
      }
      var csrf_token = $("#csrf_token").val();
      $.ajax({
         type: "POST",
         url: URL.baseUrl + '/FiltersAgentList',
         beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", csrf_token);
         },
         data: data,
         success: function (data) {
            $('#loader').addClass('hidden')
            flag = true;
            $("#ESData div").remove();
            data = JSON.parse(data);
            if(data.length > 0)
            {
            AgentListData(data);
            }
         },
         failure: function () {
            location.href = "/Error";
         }
      });
   });
   fetch(URL.baseUrl + '/GetProjectName').
   then(response => response.json()).
   then((completedata) => {
   if(completedata.length > 0)
   {
   $.each(completedata, function (key, val) {
   $("#fProject").append($("<option/>").val(val).text(val));
   })
   }
   }).catch((err) => {
      location.href = "/Error";
    });
});

function ConvertDate(userDate) {
   var date = new Date(userDate);
   var yr = date.getFullYear();
   var month = date.getMonth() + 1;
   var day = date.getDate();
   return newDate = yr + '-' + month + '-' + day;
}

function LogOut() {
   $("#logged_in_user_role").val("");
   location.href = "/LogOut";
}

$(window).scroll(function() {
   if($(window).scrollTop() == $(document).height() - $(window).height() && !flag) {
      count = count + 1;   
      $('#loader').removeClass('hidden');
      fetch(URL.baseUrl + '/AgentListData/'+count).then(response => response.json())
      .then((completedata) => {
      $('#loader').addClass('hidden');
      if(completedata.length > 0)
      {
      AgentListData(completedata);
      }
      }).catch((err) => {
         location.href = "/Error";
   });
   }
});

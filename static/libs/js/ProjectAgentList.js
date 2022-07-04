var flag = false;
if ($("#logged_in_user_role").val() == "supervisor") {
   $("#fProject").prop("disabled", true);
}
if ($("#logged_in_user_role").val() == "") {
   location.href = "/login.html";
}
var date = new Date();
var day = ("0" + date.getDate()).slice(-2);
var monthend = ("0" + (date.getMonth() + 1)).slice(-2);
var monthStart = ("0" + (date.getMonth())).slice(-2);
var EndDatetoday = date.getFullYear() + "-" + (monthend) + "-" + (day);
var StartDateToday = date.getFullYear() + "-" + (monthStart) + "-" + (day);
document.getElementById("EndDate").defaultValue = EndDatetoday;
document.getElementById("StartDate").defaultValue = StartDateToday;
if ($("#logged_in_user_role").val() == "super_admin") {
   $("#ConfigurationsMenu").show();
} else {
   $("#ConfigurationsMenu").hide();
}
jQuery(function ($) {
   var path = window.location.href;
   $('.nav-link').each(function () {
      if (this.href === path) {
         $(this).addClass('active');
      }
   });
 $('#FormAgent').on('submit', function (e) {
      $('#loader').removeClass('hidden')
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
            if(data.length >0)
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
                  '<div class="col-xl-4 col-lg-4 col-md-4 col-sm-12 col-12"><label>Flags</label><h5><span>' + row.non_billable_hours.toFixed(2) + '</span></h5>' +
                  '</div> </div> </div> </div> </div>');
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
         },
         failure: function () {
            location.href = "/Error";
         }
      });
   });
   fetch(URL.baseUrl + '/GetProjectName').
   then(response => response.json()).
   then((completedata) => {
      $.each(completedata, function (key, val) {
         $("#fProject").append($("<option/>").val(val).text(val));
      })
   }).catch((err) => {
      location.href = "/Error";
});
})

function LogOut() {
   $("#logged_in_user_role").val("");
   location.href = "/LogOut";
}

function ConvertDate(userDate) {
   var date = new Date(userDate);
   var yr = date.getFullYear();
   var month = date.getMonth() + 1;
   var day = date.getDate();
   return newDate = yr + '-' + month + '-' + day;
}
if (!flag) {
   var url = document.location.href;
   var qs = url.substring(url.indexOf('$') + 1);
   qs = qs.split('=');
   var project = qs[1];
   fetch(URL.baseUrl + '/GetNameBYProject$project=' + project).
   then(response => response.json()).
   then((completedata) => {
      $.each(completedata, function (key, val) {
         if ($('#c3chart_gauge' + val._id.chart_name).length) {
            var chart = c3.generate({
               bindto: "#c3chart_gauge" + val._id.chart_name,
               data: {
                  columns: [
                     ['data', (val.billable_hours / val.total_hours) * 100]
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
   }).catch((err) => {
      location.href = "/Error";
});
}
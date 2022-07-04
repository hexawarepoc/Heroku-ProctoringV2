if( $("#user_id").val()=="")
{
$("#btnerror").text("Back to Login");
}
else
{
 $("#btnerror").text("Back to Home");
}
function Redirect()
{
    if( $("#user_id").val()=="")
    {
        location.href = "/login.html";
    }
    else
    {
        location.href = "/index.html";
    }
}
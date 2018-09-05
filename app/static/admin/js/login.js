$( document ).ready(function() {
    var signinBtn = $('.btn-signin');
    var signinError = $('.login-error');
    
    $("form.form-signin").submit(function(e) {
        e.preventDefault(); //STOP default action
        $.ajax({
            type : "POST",
            url : $(this).attr("action"),
            data : $(this).serializeArray(),
            success: function (response) {
                window.location.href = response.next;
            },
            error: function(response) {
                signinError.html(response.responseJSON.result);
                signinError.addClass("show");
                setTimeout(function() { signinError.removeClass("show") }, 2000);
            }
        });//AJAX
        return false;
    });//form send
    
}); //doc ready

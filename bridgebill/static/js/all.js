$(document).ready(function(){
    $("#user_signup_form_minjs").validate({
        errorClass: "error",
        success: function(label) {
            label.html("&nbsp;").addClass("valid")
        },
        rules: {
            id_firstname: {
                required: true,
                minlength: 2,
            },
            id_lastname: {
                required: true,
                minlength: 2,
            },
            id_username: {
                required: true,
                minlength: 7,
                email: true, 
            },
            id_password: {
                required: true,
            },
        },
        messages: {
            id_firstname: {
                required: "&nbsp;",
                minlength: "&nbsp;",
            },
            id_lastname: {
                required: "&nbsp;",
                minlength: "&nbsp;",
            },
            id_username: {
                required: "&nbsp;",
                minlength: "&nbsp;",
                email: "&nbsp;",
            },
            id_password: {
                required: "&nbsp;",
            },
        },
    });
});

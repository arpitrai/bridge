/* Start - Validation on User Signup page */
$(document).ready(function(){
    $('#user_signup_form_minjs').validate({
        errorClass: 'error',
        success: function(label) {
            label.html('&nbsp;').addClass('valid')
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
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
            id_lastname: {
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
            id_username: {
                required: '&nbsp;',
                minlength: '&nbsp;',
                email: '&nbsp;',
            },
            id_password: {
                required: '&nbsp;',
            },
        },
    });
});
/* End - Validation on User Signup page */

/* Start - Add more friends or people on Equal Split page */
var i=0;
$(document).ready(function(){
    $('.add_friend').click(function(){
        var html_fragment_1 = '<li><input type="checkbox" checked="checked"' + 'name="people_new" class="people_new" value="people_new_' + i + '" />';
        var html_fragment_2 = '<input class="dynamic_add_in" type="text" id="id_name_' + i + '" name="name_' + i + '" />';
        var html_fragment_3 = '<input class="dynamic_add_in" type="text" id="id_email_'+ i + '" name="email_' + i + '" />';
        var html_fragment_4 = '<input class="remove_friend" type="submit" value="Remove" /></li>';
        var html_fragment = html_fragment_1 + html_fragment_2 + html_fragment_3 + html_fragment_4;
        $('ul.people li:last').after(html_fragment);
        i++;
        return false;
    });
});

$(document).ready(function(){
    $('ul.people').on('click', 'input.remove_friend', function(){
        $(this).parent().remove();
        return false;
    });
});
/* End - Add more friends or people on Equal Split page */

/* Start - To validate new name fields added on Equal Split page */
$(document).ready(function(){
    $('form#equal_split').on({
        focusin: validate_name_equal_split,
        focusout: validate_name_equal_split,
        keyup: validate_name_equal_split,
        keydown: validate_name_equal_split,
    },('input[id*=name]')
    );
});

function validate_name_equal_split(){
    $('form#equal_split').validate({ errorClass: 'error', errorElement: '', });
    $('form#equal_split input[id*=name]').each(function() {
        $(this).rules("add", {
            required: true,
            minlength: 2,
            messages: {
                required: '&nbsp',
                minlength: '&nbsp',
            },
        });
    });
};
/* End - To validate new name fields added on Equal Split page */

/* Start - To validate new email fields added on Equal Split page */
$(document).ready(function(){
    $('form#equal_split').on({
        focusin: validate_email_equal_split,
        focusout: validate_email_equal_split,
        keyup: validate_email_equal_split,
        keydown: validate_email_equal_split,
    },('input[id*=email]')
    );
});

function validate_email_equal_split(){
    $('form#equal_split').validate({ errorClass: 'error', errorElement: '', });
    $('form#equal_split input[id*=email]').each(function() {
        $(this).rules("add", {
            required: true,
            email: true,
            minlength: 7,
            messages: {
                email: '&nbsp',
                required: '&nbsp',
                minlength: '&nbsp',
            },
        });
    });
};
/* End - To validate new email fields added on Equal Split page */

/* Start - To stop the submission of any unchecked new friend name and email fields added on Equal Split page */
$(document).ready(function(){
    $('form#equal_split').on('click', ('li.last button#save'), testing);
});

function testing(event){
    $('form#equal_split input[class="people_new"]').each(function(){
        if ($(this).is(":checked")) {
            if ($(this).nextAll('input[id*=id_name_]').val().length < 2) {
                alert("What");
                $(this).nextAll('input[id*=id_name_]').addClass('error');
            };
        };
    });
    event.preventDefault();
};
/* End - To stop the submission of any unchecked new friend name and email fields added on Equal Split page */

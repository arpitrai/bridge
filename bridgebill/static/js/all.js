// Start - Validation on User Signup page 
$(document).ready(function(){
    $('#user_signup_form_minjs').validate({
        errorClass: 'error',
        success: function(label) {
            label.html('&nbsp;').addClass('valid')
        },
        rules: {
            firstname: {
                required: true,
                minlength: 2,
            },
            username: {
                required: true,
                minlength: 7,
                email: true, 
            },
            password1: {
                required: true,
            },
            password2: {
                required: true,
                equalTo: '#id_password1',
            },
        },
        messages: {
            firstname: {
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
            username: {
                required: '&nbsp;',
                minlength: '&nbsp;',
                email: '&nbsp;',
            },
            password1: {
                required: '&nbsp;',
            },
            password2: {
                required: '&nbsp;',
                equalTo: '&nbsp;',
            },
        },
    });
});
// End - Validation on User Signup page 

// Start - To stop the submission of any errors or blank fields on User Signup page 
$(document).ready(function(){
    $('form#user_signup_form_minjs li.last button#save').click(function(){
        if ($('form#user_signup_form_minjs').validate().form() === false) {
            event.preventDefault();
        };
    });
});
// End - To stop the submission of any errors or blank fields on User Signup page 

// Start - Form validation for Equal Split page 
$(document).ready(function(){
    $('form#equal_split').validate({
        errorClass: 'error',
        errorElement: 'span',
        rules: {
            date: {
                required: true,
                date: true,
            },
            description: {
                required: true,
                minlength: 2,
            },
            amount: {
                required: true,
                minlength: 1,
                digits: true,
            },
        },
        messages: {
            date: {
                required: '&nbsp',
                date: '&nbsp',
            },
            description: {
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
            amount: {
                required: '&nbsp;',
                minlength: '&nbsp;',
                digits: '&nbsp',
            },
        },
    });
});
// End - Form validation for Equal Split page 

// Start - Add more friends or people on Equal Split page 
var i=0;
$(document).ready(function(){
    $('form#equal_split button.add_friend').click(function(){
        var html_fragment_1 = '<li><input type="checkbox" checked="checked"' + 'name="people_new" class="people_new" value="people_new_' + i + '" />';
        var html_fragment_2 = '<input class="dynamic_add_in" type="text" id="id_name_' + i + '" name="name_' + i + '" placeholder="Friend Name" />';
        var html_fragment_3 = '<input class="dynamic_add_in" type="text" id="id_email_'+ i + '" name="email_' + i + '" placeholder="Friend Email" />';
        /*var html_fragment_4 = '<input class="remove_friend" type="submit" value="Remove" /></li>';*/
        /*var html_fragment = html_fragment_1 + html_fragment_2 + html_fragment_3 + html_fragment_4;*/
        var html_fragment = html_fragment_1 + html_fragment_2 + html_fragment_3;
        $('form#equal_split ul.people li:last').after(html_fragment);
        i++;
        return false;
    });
});

$(document).ready(function(){
    $('form#equal_split ul.people').on('click', 'input.remove_friend', function(){
        $(this).parent().remove();
        return false;
    });
});
// End - Add more friends or people on Equal Split page 

// Start - To validate new name fields added on Equal Split page 
$(document).ready(function(){
    $('form#equal_split').on({
        focusin: validate_name_equal_split,
        focusout: validate_name_equal_split,
        keyup: validate_name_equal_split,
        keydown: validate_name_equal_split,
    },('input[id*=id_name_]')
    );
});

function validate_name_equal_split(){
    //$('form#equal_split').validate({ errorClass: 'error', errorElement: '', });
    $('form#equal_split input[id*=id_name_]').each(function() {
        $(this).rules("add", {
            required: false,
            minlength: 2,
            messages: {
                required: '&nbsp',
                minlength: '&nbsp',
            },
        });
    });
};
// End - To validate new name fields added on Equal Split page 

// Start - To validate new email fields added on Equal Split page 
$(document).ready(function(){
    $('form#equal_split').on({
        focusin: validate_email_equal_split,
        focusout: validate_email_equal_split,
        keyup: validate_email_equal_split,
        keydown: validate_email_equal_split,
    },('input[id*=id_email_]')
    );
});

function validate_email_equal_split(){
    //$('form#equal_split').validate({ errorClass: 'error', errorElement: '', });
    $('form#equal_split input[id*=id_email_]').each(function() {
        $(this).rules("add", {
            required: false,
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
// End - To validate new email fields added on Equal Split page 

// Start - To stop the submission of any unchecked new friend name and email fields added on Equal Split page 
$(document).ready(function(){
    $('form#equal_split').on('click', ('li.last button#save'), validate_equal_split_save);
});

function validate_equal_split_save(event){
    var input_checked_counter = 0;
    $('form#equal_split input[name*=people]').each(function(){
        if ($(this).is(":checked")) {
            input_checked_counter++;
        };
    });
    if (input_checked_counter === 0) {
        $('span.friend_checked').css("visibility", "visible");
        event.preventDefault();
    }
    else {
        $('span.friend_checked').css("visibility", "hidden");
    };

    $('form#equal_split input[class="people_new"]').each(function(){
        if ($(this).is(":checked")) {
            if ($(this).nextAll('input[id*=id_name_]').val().length === 0) {
                $(this).nextAll('input[id*=id_name_]').addClass('error_2');
                event.preventDefault();
            };
            if ($(this).nextAll('input[id*=id_email_]').val().length === 0) {
                $(this).nextAll('input[id*=id_email_]').addClass('error_2');
                event.preventDefault();
            };
        };
    });

    if ($('form#equal_split').validate().form() === false) {
        alert($('form#equal_split').validate().form());
        event.preventDefault();
    };
};
// End - To stop the submission of any unchecked new friend name and email fields added on Equal Split page 

// Start - Form validation for Un-Equal Split page 
$(document).ready(function(){
    $('form#unequal_split').validate({
        errorClass: 'error',
        errorElement: 'span',
        rules: {
            date: {
                required: true,
                date: true,
            },
            description: {
                required: true,
                minlength: 2,
            },
            amount: {
                required: true,
                minlength: 1,
                digits: true,
            },
            total_people: {
                required: true,
                digits: true,
            },
        },
        messages: {
            date: {
                required: '&nbsp',
                date: '&nbsp',
            },
            description: {
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
            amount: {
                required: '&nbsp;',
                minlength: '&nbsp;',
                digits: '&nbsp',
            },
            total_people: {
                required: '&nbsp;',
                digits: '&nbsp;',
            },
        },
    });
});
// End - Form validation for Un-Equal Split page 

// Start - To calculate amount depending on user input
$(document).ready(function(){
    $('form#unequal_split').on('click', 'select[id*=id_number_of_people] option', function(event){
        var total_amount = Number($('form#unequal_split input#id_amount').val()) 
        var total_people = Number($('form#unequal_split input#id_total_people').val());
        var borrower_amount = total_amount/total_people * Number($(this).val());
        borrower_amount = Math.round(borrower_amount*100)/100;
        $(this).parent().parent().parent().find('input[id*=id_borrower_amount]').val(borrower_amount);
    });
});
// End - To calculate amount depending on user input

// Start - Add more friends or people on Un-Equal Split page 
var i=0;
$(document).ready(function(){
    $('form#unequal_split button.add_friend').click(function(){
        var html_fragment_1 = '<tr><td class="name"><input type="hidden" name="people_new" class="people_new" value="x_people_new_' + i + '" />';
        var html_fragment_2 = '<input class="dynamic_add_in" type="text" id="x_id_name_' + i + '" name="x_name_' + i + '" placeholder="Friend Name" />';
        var html_fragment_3 = '<input class="dynamic_add_in" type="text" id="x_id_email_'+ i + '" name="x_email_' + i + '" placeholder="Friend Email" /></td>';
        var html_fragment_4 = '<td class="number"><select id="x_id_number_of_people_' + i + '" name="x_number_of_people_' + i + '"><option value="0"></option><option value="1">1 person</option><option value="2">2 people</option><option value="3">3 people</option><option value="4">4 people</option><option value="5">5 people</option></select></td>'
        var html_fragment_5 = '<td class="amount"><input type="text" id="x_id_borrower_amount_' + i + '" name="x_borrower_amount_' + i + '" /></td>';
        var html_fragment_6 = '<td><input class="remove_friend" type="submit" value="Remove" /></td></tr>';
        var html_fragment = html_fragment_1 + html_fragment_2 + html_fragment_3 + html_fragment_4 + html_fragment_5 + html_fragment_6;
        $('form#unequal_split table#unequal_split_people_table tbody tr:last').after(html_fragment);
        i++;
        return false;
    });
});

$(document).ready(function(){
    $('form#unequal_split table#unequal_split_people_table').on('click', 'input.remove_friend', function(){
        $(this).parent().parent().remove();
        return false;
    });
});
// End - Add more friends or people on Un-Equal Split page 

// Start - To validate new name, email and amount fields added on Un-Equal Split page 
$(document).ready(function(){
    $('form#unequal_split').on({
        focusin: validate_unequal_split,
        focusout: validate_unequal_split,
        keyup: validate_unequal_split,
        keydown: validate_unequal_split,
    },('input[id^=x_id_name_]')
    );
});

$(document).ready(function(){
    $('form#unequal_split').on({
        focusin: validate_unequal_split,
        focusout: validate_unequal_split,
        keyup: validate_unequal_split,
        keydown: validate_unequal_split,
    },('input[id^=x_id_email_]')
    );
});

$(document).ready(function(){
    $('form#unequal_split').on({
        focusin: validate_unequal_split,
        focusout: validate_unequal_split,
        keyup: validate_unequal_split,
        keydown: validate_unequal_split,
    },('input[id^=x_id_borrower_amount_]')
    );
});

function validate_unequal_split(){
    $('form#unequal_split input[id^=x_id_name_]').each(function() {
        $(this).rules("add", {
            required: false,
            minlength: 2,
            messages: {
                required: '&nbsp',
                minlength: '&nbsp',
            },
        });
    });
    $('form#unequal_split input[id^=x_id_email_]').each(function() {
        $(this).rules("add", {
            required: false,
            email: true,
            minlength: 7,
            messages: {
                email: '&nbsp',
                required: '&nbsp',
                minlength: '&nbsp',
            },
        });
    });
    $('form#unequal_split input[id^=x_id_borrower_amount_]').each(function() {
        $(this).rules("add", {
            required: false,
            minlength: 1,
            digits: true,
            messages: {
                required: '&nbsp',
                minlength: '&nbsp',
                digits: '&nbsp',
            },
        });
    });
};
// End - To validate new name, email and amount fields added on Un-Equal Split page 

// Start - To validate amount fields for existing friends on Un-Equal Split page 
$(document).ready(function(){
    $('form#unequal_split').on({
        focusin: validate_amount_existing_unequal_split,
        focusout: validate_amount_existing_unequal_split,
        keyup: validate_amount_existing_unequal_split,
        keydown: validate_amount_existing_unequal_split,
    },('input[id^=id_borrower_amount_]')
    );
});

function validate_amount_existing_unequal_split(){
    $('form#unequal_split input[id^=id_borrower_amount_]').each(function() {
        $(this).rules("add", {
            required: false,
            minlength: 1,
            digits: true,
            messages: {
                required: '&nbsp',
                minlength: '&nbsp',
                digits: '&nbsp',
            },
        });
    });
};
// End - To validate amount fields for existing friends on Un-Equal Split page 

// Start - To stop the submission of any unchecked new friend name and email fields added on Un-Equal Split page 
$(document).ready(function(){
    $('form#unequal_split').on('click', ('li.last button#save'), validate_unequal_split_save);
});

function validate_unequal_split_save(event){
    var input_checked_counter = 0;
    $('form#unequal_split input[class=people]').each(function(){
        if ($(this).nextAll('select[id^=id_borrower]').val().length !== 0) {
            input_checked_counter++;
        };
    });
    $('form#unequal_split input[class=people_new]').each(function(){
        if ($(this).nextAll('input[id^=x_id_name]').val().length !== 0) {
            input_checked_counter++;
        };
    });
    if (input_checked_counter === 0) {
        $('span.friend_checked').css("visibility", "visible");
        event.preventDefault();
    }
    else {
        $('span.friend_checked').css("visibility", "hidden");
    };


    if ($('form#unequal_split').validate().form() === false) {
       event.preventDefault();
       return false;
    }
    else {
        var value = true;
        $('form#unequal_split input[class=people]').each(function(){
            if (($(this).nextAll('select[id^=id_borrower]').val().length === 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() === '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length !== 0)) {
                event.preventDefault();
                $(this).nextAll('select[id^=id_borrower]').addClass('error');
                $(this).parent().parent().find('select[id^=id_number_of_people]').addClass('error');
                value = false;
            };
            if (($(this).nextAll('select[id^=id_borrower]').val().length === 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() !== '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length === 0)) {
                event.preventDefault();
                $(this).nextAll('select[id^=id_borrower]').addClass('error');
                $(this).parent().parent().find('input[id^=id_borrower_amount]').addClass('error');
                value = false;
            };
            if (($(this).nextAll('select[id^=id_borrower]').val().length === 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() !== '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length !== 0)) {
                event.preventDefault();
                $(this).nextAll('select[id^=id_borrower]').addClass('error');
                value = false;
            };
            if (($(this).nextAll('select[id^=id_borrower]').val().length !== 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() === '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length === 0)) {
                event.preventDefault();
                $(this).parent().parent().find('select[id^=id_number_of_people]').addClass('error');
                $(this).parent().parent().find('input[id^=id_borrower_amount]').addClass('error');
                value = false;
            };
            if (($(this).nextAll('select[id^=id_borrower]').val().length !== 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() === '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length !== 0)) {
                event.preventDefault();
                $(this).parent().parent().find('select[id^=id_number_of_people]').addClass('error');
                value = false;
            };
            if (($(this).nextAll('select[id^=id_borrower]').val().length !== 0) && ($(this).parent().parent().find('select[id^=id_number_of_people]').val() !== '0') && ($(this).parent().parent().find('input[id^=id_borrower_amount]').val().length === 0)) {
                event.preventDefault();
                $(this).parent().parent().find('input[id^=id_borrower_amount]').addClass('error');
                value = false;
            };
        });

        $('form#unequal_split input[class=people_new]').each(function(){
            if (($(this).nextAll('input[id^=x_id_name]').val().length === 0) && ($(this).nextAll('input[id^=x_id_email]').val().length === 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length !== 0)) {
                event.preventDefault();
                $(this).nextAll('input[id^=x_id_name]').addClass('error');
                $(this).nextAll('input[id^=x_id_email]').addClass('error');
                if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                    $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                };
                value = false;
            };
            if (($(this).nextAll('input[id^=x_id_name]').val().length === 0) && ($(this).nextAll('input[id^=x_id_email]').val().length !== 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length === 0)) {
                event.preventDefault();
                $(this).nextAll('input[id^=x_id_name]').addClass('error');
                $(this).parent().parent().find('input[id^=x_id_borrower_amount]').addClass('error');
                if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                    $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                };
                value = false;
            };
            if (($(this).nextAll('input[id^=x_id_name]').val().length === 0) && ($(this).nextAll('input[id^=x_id_email]').val().length !== 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length !== 0)) {
                event.preventDefault();
                $(this).nextAll('input[id^=x_id_name]').addClass('error');
                if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                    $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                };
                value = false;
            };
             if (($(this).nextAll('input[id^=x_id_name]').val().length !== 0) && ($(this).nextAll('input[id^=x_id_email]').val().length === 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length === 0)) {
                 event.preventDefault();
                 $(this).nextAll('input[id^=x_id_email]').addClass('error');
                 $(this).parent().parent().find('input[id^=x_id_borrower_amount]').addClass('error');
                 if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                     $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                 };
                 value = false;
             };
             if (($(this).nextAll('input[id^=x_id_name]').val().length !== 0) && ($(this).nextAll('input[id^=x_id_email]').val().length === 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length !== 0)) {
                 event.preventDefault();
                 $(this).nextAll('input[id^=x_id_email]').addClass('error');
                 if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                     $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                 };
                 value = false;
             };
             if (($(this).nextAll('input[id^=x_id_name]').val().length !== 0) && ($(this).nextAll('input[id^=x_id_email]').val().length !== 0) && ($(this).parent().parent().find('input[id^=x_id_borrower_amount]').val().length === 0)) {
                 event.preventDefault();
                 $(this).parent().parent().find('input[id^=x_id_borrower_amount]').addClass('error');
                 if ($(this).parent().parent().find('select[id^=x_id_number_of_people]').val() === '0') {
                     $(this).parent().parent().find('select[id^=x_id_number_of_people]').addClass('error');
                 };
                 value = false;
             };
         });
         return value;
    };
};
// End - To stop the submission of any unchecked new friend name and email fields added on Un-Equal Split page 

// Start - Date Plugin
$(document).ready(function(){
    $('li input#id_date').datepicker({ altFormat: "yy-mm-dd" });
});
// End - Date Plugin

// Start - Validation on My Profile page 
$(document).ready(function(){
    $('#my_profile').validate({
        errorClass: 'error',
        success: function(label) {
            label.html('&nbsp;').addClass('valid')
        },
        rules: {
            first_name: {
                required: true,
                minlength: 2,
            },
        },
        messages: {
            first_name: {
                required: '&nbsp;',
                minlength: '&nbsp;',
            },
        },
    });
});
// End - Validation on My Profile page 

// Start - To stop the submission of any errors or blank fields on My Profile page 
$(document).ready(function(){
    $('form#my_profile li.last button#save').click(function(){
        if ($('form#my_profile').validate().form() === false) {
            event.preventDefault();
        };
    });
});
// End - To stop the submission of any errors or blank fields on My Profile page 

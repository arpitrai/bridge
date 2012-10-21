from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.shortcuts import render_to_response
from django.template import RequestContext
from bridgebill.models import UserProfile, UserFriend, Bill, BillDetails
from bridgebill.models import UserFriendForm, PartialBillForm
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm

from django.db.models import Max

from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from django.conf import settings
if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail, send_html_mail
else:
    from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

# Email Settings Start
account_creation_txt = get_template('email_templates/account_creation.txt')
account_creation_html = get_template('email_templates/account_creation.html')
bill_creation_txt = get_template('email_templates/bill_creation.txt')
bill_creation_html = get_template('email_templates/bill_creation.html')
payment_full_creation_txt = get_template('email_templates/payment_full_creation.txt')
payment_full_creation_html = get_template('email_templates/payment_full_creation.html')
payment_part_creation_txt = get_template('email_templates/payment_part_creation.txt')
payment_part_creation_html = get_template('email_templates/payment_part_creation.html')
# Email Settings End

"""
def login(request):
    return render_to_response('index.html', { 'request': request }, context_instance=RequestContext(request))
"""

def login_error(request):
    return render_to_response('index.html', { 'request': request }, context_instance=RequestContext(request))

def user_signup(request):
    if request.method == 'POST': 
        request_POST_modified = request.POST.copy()
        request_POST_modified['password2'] = request.POST['password1']
        user_creation_form = UserCreationForm(request_POST_modified)
        if user_creation_form.is_valid():
            username = user_creation_form.cleaned_data['username']
            password = user_creation_form.cleaned_data['password1']
            new_user = user_creation_form.save()
            new_user.email = new_user.username
            new_user.save()
            new_user = authenticate(username=username, password=password)
            login(request,new_user)
            
            # Send Email Start
            context = Context( {} )
            subject, to = 'Welcome to BridgeBill', new_user.email
            account_creation_txt_content = account_creation_txt.render(context)
            account_creation_html_content = account_creation_html.render(context)
            send_html_mail(subject, account_creation_txt_content, account_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ to ])
            # Send Email End

            user_own_friend = UserFriend(user=request.user, friend_email=request.user.email, friend_name=request.user.first_name+' '+request.user.last_name)
            user_own_friend.save()
            return HttpResponseRedirect('/home/')
        else:
            # Put in clause here when the user creation form is not valid
            pass
    else:
        user_creation_form = UserCreationForm()
        return render_to_response('user-signup.html', { 'user_creation_form': user_creation_form, 'request': request }, context_instance=RequestContext(request))

def forgot_password(request):
    if request.method == 'POST':
        pass
    else:
        forgot_password_form = PasswordResetForm()
        return render_to_response('forgot-password.html', { 'forgot_password_form': forgot_password_form, 'request': request }, context_instance=RequestContext(request))


@login_required
def home(request):
    total_borrowed_amount = 0
    total_lent_amount = 0

    """class Friend:
        pass
    friends = []
    my_friends = UserFriend.objects.filter(user=request.user).exclude(friend_email=request.user.email)
    for each_friend in my_friends:
        friend_borrower = BillDetails.objects.filter(bill__lender=request.user, borrower=each_friend, bill_cleared='N')
        friends = Friend()
        total = 0
        for each_bill in friend_borrower:
            total += each_bill.individual_amount

        friend_user = User.objects.get(email=each_friend.friend_email)
        me_borrower_object = UserFriend.objects.filter(user=friend_user, friend_email=request.user.email)
        borrowed_from_friend = BillDetails.objects.filter(bill__lender=friend_user, borrower=me_borrower_object)"""



    class Borrower:
        pass
    my_borrowers = UserFriend.objects.filter(user=request.user).exclude(friend_email=request.user.email)
    borrowers = []
    for each_borrower in my_borrowers:
        each_borrower_bills = BillDetails.objects.filter(bill__lender=request.user, borrower=each_borrower, bill_cleared='N')
        if each_borrower_bills:
            borrower = Borrower()
            total = 0
            for each_bill in each_borrower_bills:
                total += each_bill.individual_amount
            borrower.id = each_borrower.id
            borrower.name = each_borrower.friend_name
            borrower.email = each_borrower.friend_email
            borrower.amount = total
            borrowers.append(borrower)
            total_borrowed_amount += total

    class Lender:
        pass
    my_lenders = UserFriend.objects.filter(friend_email=request.user.email).exclude(user=request.user)
    lenders = []
    for each_lender in my_lenders:
        borrower = UserFriend.objects.get(user=User.objects.get(email=each_lender.user.email), friend_email=request.user.email)
        each_lender_object = User.objects.get(email=each_lender.user.email)
        each_lender_bills = BillDetails.objects.filter(bill__lender=each_lender_object, borrower=borrower, bill_cleared='N')
        if each_lender_bills: 
            lender = Lender()
            total = 0
            for each_bill in each_lender_bills:
                total += each_bill.individual_amount
            lender.id = each_lender.id
            lender.name = each_lender.user.first_name + " " + each_lender.user.last_name
            lender.email = each_lender.user.email
            try:
                lender.name = UserFriend.objects.get(user=request.user, friend_email=lender.email).friend_name
            except:
                pass
            lender.amount = total
            lenders.append(lender)
            total_lent_amount += total

    return render_to_response('home.html', { 'borrowers': borrowers, 'lenders': lenders, 'total_borrowed_amount': total_borrowed_amount, 'total_lent_amount': total_lent_amount, 'request': request }, context_instance=RequestContext(request))

@login_required
def home_details(request, person_id):
    if request.method == 'GET':
        if person_id[:2] == 'b_':
            lender_or_borrower = 'borrower'
        else:
            lender_or_borrower = 'lender'

        person_actual_id = person_id[2:]
        borrower_name = ''
        borrower_bills = []
        total_borrowed_amount = 0
        lender_name = ''
        lender_bills = []
        total_lent_amount = 0

        if lender_or_borrower == 'borrower':
            borrower = True
            borrower = UserFriend.objects.get(id=person_actual_id)
            borrower_name = borrower.friend_name
            borrower_bills = BillDetails.objects.filter(bill__lender=request.user, borrower=borrower, bill_cleared='N')
            if borrower_bills:
                total_borrowed_amount = 0
                for borrower_bill in borrower_bills:
                    total_borrowed_amount += borrower_bill.individual_amount

            borrower_email = borrower.friend_email
            try: 
                borrower_as_user = User.objects.get(email=borrower_email)
                try:
                    borrower_user_friend = UserFriend.objects.get(user=borrower_as_user, friend_email=request.user.email)
                    lender_bills = BillDetails.objects.filter(bill__lender=borrower_as_user, borrower=borrower_user_friend, bill_cleared='N')
                    if lender_bills:
                        lender = True
                        total_lent_amount = 0
                        for lender_bill in lender_bills:
                            total_lent_amount += lender_bill.individual_amount
                    else:
                        lender=False
                except:
                    lender = False
            except:
                lender = False
            return render_to_response('home-details.html', { 'borrower': borrower, 'borrower_name': borrower_name, 'borrower_bills': borrower_bills, 'total_borrowed_amount': total_borrowed_amount, 'lender': lender, 'lender_name': lender_name, 'lender_bills': lender_bills, 'total_lent_amount': total_lent_amount, 'request': request }, context_instance=RequestContext(request))

        elif lender_or_borrower == 'lender':
            lender = True
            userfriend_object = UserFriend.objects.get(id=person_actual_id)
            user_object = userfriend_object.user
            try: 
                lender_name = UserFriend.objects.get(user=request.user, friend_email=user_object.email).friend_name
            except:
                lender_name = user_object.first_name + ' ' + user_object.last_name
            lender_bills = BillDetails.objects.filter(bill__lender=user_object, borrower=userfriend_object, bill_cleared='N')
            
            total_lent_amount = 0
            for lender_bill in lender_bills:
                total_lent_amount += lender_bill.individual_amount

            borrower_email = user_object.email
            try:
                userfriend_object = UserFriend.objects.get(user=request.user, friend_email=borrower_email)
                borrower_bills = BillDetails.objects.filter(bill__lender=request.user, borrower=userfriend_object, bill_cleared='N')
                if borrower_bills:
                    borrower = True
                    total_borrowed_amount = 0
                    for borrower_bill in borrower_bills:
                        total_borrowed_amount += borrower_bill.individual_amount
                else:
                    borrower = False 
            except:
                borrower = False

            return render_to_response('home-details.html', { 'borrower': borrower, 'borrower_name': borrower_name, 'borrower_bills': borrower_bills, 'total_borrowed_amount': total_borrowed_amount, 'lender': lender, 'lender_name': lender_name, 'lender_bills': lender_bills, 'total_lent_amount': total_lent_amount, 'request': request }, context_instance=RequestContext(request))
    else:
        for i in request.POST.getlist('bill_id'):
            bill = BillDetails.objects.get(id=i)
            bill.bill_cleared = 'Y'
            bill.save()
        return HttpResponseRedirect(request.path)

@login_required
def my_friends(request, delete):
    if request.method == 'POST':
        for friend in request.POST.getlist('people'):
            user_friend = UserFriend.objects.get(user=request.user, friend_email=friend)
            user_friend.delete()
        return HttpResponseRedirect('/my-friends/')
    else: 
        my_friends = UserFriend.objects.filter(user=request.user).exclude(friend_email=request.user.email)
        if not my_friends:
            delete = False
        return render_to_response('my-friends.html', { 'my_friends': my_friends, 'delete': delete, 'request': request }, context_instance=RequestContext(request))

@login_required
def add_friends(request):
    if request.method == 'POST':
        user_friend_form = UserFriendForm(request.POST)
        if user_friend_form.is_valid():
            user_friend = UserFriend(user=request.user)
            user_friend_form = UserFriendForm(request.POST, instance=user_friend)
            user_friend_form.save()
            return HttpResponseRedirect('/my-friends/')
    else: 
        user_friend_form = UserFriendForm()
    return render_to_response('add-friends.html', { 'user_friend_form': user_friend_form, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_bill_option(request):
    if request.method == 'POST':
        if request.POST['record_bill_option'] == 'equal_split':
            return HttpResponseRedirect('/record-bill/equal-split/')
        else: 
            return HttpResponseRedirect('/record-bill/unequal-split/')
    else:
        return render_to_response('record-bill-option.html', { 'request': request }, context_instance=RequestContext(request))

@login_required
def record_bill_equal_split(request):
    if request.method == 'POST':
        bill_form = PartialBillForm(request.POST)
        if bill_form.is_valid():
            overall_bill_id = Bill.objects.aggregate(Max('overall_bill_id'))['overall_bill_id__max'] + 1
            lender = request.user
            bill = Bill(overall_bill_id=overall_bill_id, lender=lender, date=bill_form.cleaned_data['date'], description=request.POST['description'], amount=bill_form.cleaned_data['amount'])
            bill.save()
            number_of_borrowers = len(request.POST.getlist('people'))

            for borrower in request.POST.getlist('people'):
                if borrower != request.user.email:
                    borrower_object = UserFriend.objects.get(user=request.user, friend_email=borrower)
                    bill_detail = BillDetails(bill=bill, borrower=borrower_object, individual_amount=float(bill_form.cleaned_data['amount']/number_of_borrowers), bill_cleared='N')
                    bill_detail.save()

                    # Send Email Start
                    context = Context({ 'request': request, 'bill': bill, 'bill_detail': bill_detail })
                    subject = 'New Bill Recorded: ' + bill.description
                    bill_creation_txt_content = bill_creation_txt.render(context)
                    bill_creation_html_content = bill_creation_html.render(context)
                    send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ borrower ])
                    # Send Email End
                else:
                    borrower_object = UserFriend.objects.get(user=request.user, friend_email=request.user.email)
                    bill_detail = BillDetails(bill=bill, borrower=borrower_object, individual_amount=float(bill_form.cleaned_data['amount']/number_of_borrowers), bill_cleared='Y')
                    bill_detail.save()
            return HttpResponseRedirect('/who-owes-me/')
    else:
        my_friends = UserFriend.objects.filter(user=request.user)
        bill_form = PartialBillForm()
        return render_to_response('record-bill-equal-split.html', { 'my_friends': my_friends, 'bill_form': bill_form, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_bill_unequal_split(request):
    my_friends = UserFriend.objects.filter(user=request.user)
    number_of_friends = my_friends.count()
    if request.method == 'POST':
        bill_form = PartialBillForm(request.POST)
        if bill_form.is_valid():
            overall_bill_id = Bill.objects.aggregate(Max('overall_bill_id'))['overall_bill_id__max'] + 1
            lender = request.user
            bill = Bill(overall_bill_id=overall_bill_id, lender=lender, date=bill_form.cleaned_data['date'], description=request.POST['description'], amount=bill_form.cleaned_data['amount'])
            bill.save()

            for i in range(0, number_of_friends):
                borrower_counter = 'borrower_' + str(i)
                # number_of_people_counter = 'number_of_people_' + str(i)
                borrower_amount_counter = 'borrower_amount_' + str(i)
                if request.POST[borrower_amount_counter] != '':
                    if request.POST[borrower_counter] != request.user.email:
                        borrower = UserFriend.objects.get(user=request.user, friend_email=request.POST[borrower_counter])
                        bill_detail = BillDetails(bill=bill, borrower=borrower, individual_amount=float(request.POST[borrower_amount_counter]), bill_cleared='N')
                        bill_detail.save()
                        # Send Email Start
                        context = Context({ 'request': request, 'bill': bill, 'bill_detail': bill_detail })
                        subject = 'New Bill Recorded: ' + bill.description
                        bill_creation_txt_content = bill_creation_txt.render(context)
                        bill_creation_html_content = bill_creation_html.render(context)
                        send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ request.POST['borrower_counter'] ])
                        # Send Email End
                    else:
                        borrower = UserFriend.objects.get(user=request.user, friend_email=request.user.email)
                        bill_detail = BillDetails(bill=bill, borrower=borrower, individual_amount=float(request.POST[borrower_amount_counter]), bill_cleared='Y')
                        bill_detail.save()
                else:
                    continue
            return HttpResponseRedirect('/who-owes-me/')
    else: 
        bill_form = PartialBillForm()
        return render_to_response('record-bill-unequal-split.html', { 'my_friends': my_friends, 'bill_form': bill_form, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_payment_partial_form(request):
    if request.method == 'POST':
        payment_form = PartialBillForm()
        lender = User.objects.get(email=request.POST['people'])
        borrower = UserFriend.objects.get(user=lender, friend_email=request.user.email)
        bill_details = BillDetails.objects.filter(bill__lender=lender, borrower=borrower, bill_cleared='N')
        return render_to_response('record-payment.html', { 'payment_form': payment_form, 'lender': lender, 'bill_details': bill_details, 'request': request }, context_instance=RequestContext(request)) 
    else:
        my_lenders = UserFriend.objects.filter(friend_email=request.user.email).exclude(user=request.user)
        return render_to_response('record-payment-partial-form.html', { 'my_lenders': my_lenders, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_payment(request):
    if request.method == 'POST':
        payment_form = PartialBillForm(request.POST)
        lender = User.objects.get(email=request.POST['lender'])
        borrower = UserFriend.objects.get(user=lender, friend_email=request.user.email)
        bill = Bill.objects.get(overall_bill_id=request.POST['overall_bill_id'])
        if payment_form.is_valid():
            if request.POST['overall_bill_id'] != '000': 
                bill_detail = BillDetails.objects.get(bill__overall_bill_id=request.POST['overall_bill_id'], borrower=borrower)
                bill_detail.bill_cleared='Y'
                bill_detail.save()

                # Send Email Start
                context = Context({ 'request': request, 'description': request.POST['description'], 'amount': payment_form.cleaned_data['amount'] })
                subject = 'New Payment of SGD ' + str(payment_form.cleaned_data['amount']) + ' by: ' + request.user.first_name + ' ' + request.user.last_name + ' ' + '(' + request.user.email + ')'
                payment_part_creation_txt_content = payment_part_creation_txt.render(context)
                payment_part_creation_html_content = payment_part_creation_txt.render(context)
                send_html_mail(subject, payment_part_creation_txt_content, payment_part_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ lender.email ])
                # Send Email End
            else:
                bill_details = BillDetails.objects.filter(bill__lender=lender, borrower=borrower)
                for bill_detail in bill_details:
                    bill_detail.bill_cleared='Y'
                    bill_detail.save()

                # Send Email Start
                context = Context({ 'request': request, 'amount': payment_form.cleaned_data['amount'] })
                subject = 'New Payment of SGD ' + str(payment_form.cleaned_data['amount']) + ' by: ' + request.user.first_name + ' ' + request.user.last_name + ' ' + '(' + request.user.email + ')'
                payment_full_creation_txt_content = payment_full_creation_txt.render(context)
                payment_full_creation_html_content = payment_full_creation_txt.render(context)
                send_html_mail(subject, payment_full_creation_txt_content, payment_full_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ lender.email ])
                # Send Email End
            return HttpResponseRedirect('/who-i-owe/')
    else:
        HttpResponseRedirect('/record-payment/')

@login_required
def who_i_owe(request):
    borrower_objects = UserFriend.objects.filter(friend_email=request.user.email)
    my_lenders = BillDetails.objects.filter(borrower__in=borrower_objects, bill_cleared='N').exclude(bill__lender=request.user).order_by('bill__lender')
    return render_to_response('who-i-owe.html', { 'my_lenders': my_lenders, 'request': request }, context_instance=RequestContext(request))

@login_required
def who_owes_me(request):
    me_borrow_me = UserFriend.objects.get(user=request.user, friend_email=request.user.email)
    my_borrowers = BillDetails.objects.filter(bill__lender=request.user, bill_cleared='N').exclude(borrower=me_borrow_me).order_by('borrower')
    return render_to_response('who-owes-me.html', { 'my_borrowers': my_borrowers, 'request': request }, context_instance=RequestContext(request))

@login_required
def specific_bill_details(request, overall_bill_id):
    if request.method == 'POST':
        if 'mark_bill_paid' in request.POST:
            bill = Bill.objects.get(overall_bill_id=overall_bill_id)
            if 'lender_as_user_yes' in request.POST: 
                bill_details = BillDetails.objects.filter(bill=bill)
                for bill_detail in bill_details:
                    bill_detail.bill_cleared = 'Y'
                    bill_detail.save()
                return HttpResponseRedirect('/home/')
            else:
                lender_as_user = User.objects.get(email=request.POST['lender'])
                user_friend = UserFriend.objects.get(user=lender_as_user, friend_email=request.user.email)
                bill_detail = BillDetails.objects.get(bill=bill, borrower=user_friend)
                bill_detail.bill_cleared = 'Y'
                bill_detail.save()
                return HttpResponseRedirect('/home/')
        elif 'delete_bill' in request.POST:
            bill = Bill.objects.get(overall_bill_id=overall_bill_id)
            bill_details = BillDetails.objects.filter(bill=bill)
            for bill_detail in bill_details:
                bill_detail.delete()
            bill.delete()
            return HttpResponseRedirect('/who-owes-me/')
        elif 'modify_bill' in request.POST:
            modify_bill(request, overall_bill_id)
            return HttpResponseRedirect('/who-owes-me/')
    else: 
        bill = Bill.objects.get(overall_bill_id=overall_bill_id)
        if bill.lender == request.user:
            user_lender = True
        else:
            user_lender = False
        borrowers = BillDetails.objects.filter(bill=bill)
        return render_to_response('specific-bill-details.html', { 'bill': bill, 'borrowers': borrowers, 'user_lender': user_lender, 'request': request }, context_instance=RequestContext(request))

@login_required
def logout_user(request):
	logout(request)
	return HttpResponseRedirect("/") 

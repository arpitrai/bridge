from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from social_auth.models import UserSocialAuth

from django.shortcuts import render_to_response
from django.template import RequestContext
from bridgebill.models import UserProfile, UserFriend, Bill, BillDetails, Feedback
from bridgebill.models import UserFriendForm, PartialBillForm, FeedbackForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, PasswordChangeForm

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

# Start - Settings to get email templates
account_creation_txt = get_template('email_templates/account_creation.txt')
account_creation_html = get_template('email_templates/account_creation.html')
bill_creation_txt = get_template('email_templates/bill_creation.txt')
bill_creation_html = get_template('email_templates/bill_creation.html')
payment_creation_txt = get_template('email_templates/payment_creation.txt')
payment_creation_html = get_template('email_templates/payment_creation.html')
feedback_txt = get_template('email_templates/feedback.txt')
feedback_html = get_template('email_templates/feedback.html')
# End - Settings to get email templates

# Start - Common function for creating UUIDs
import uuid
def create_uuid():
    return str(uuid.uuid4())
# End - Common function for creating UUIDs

# Start - Creating unique UserProfile ID
def create_userprofile_id():
    check_counter = True
    while check_counter is True:
        userprofile_id = 'up_' + create_uuid()
        try: 
            user_profile = UserProfile.objects.get(userprofile_id=userprofile_id)
            check_counter = True
        except:
            check_counter = False
    return userprofile_id
# End - Creating unique UserProfile ID


# Start - Creating unique UserFriend ID
def create_userfriend_id():
    check_counter = True
    while check_counter is True:
        userfriend_id = 'uf_' + create_uuid()
        try: 
            user_friend = UserFriend.objects.get(userfriend_id=userfriend_id)
            check_counter = True
        except:
            check_counter = False
    return userfriend_id
# End - Creating unique UserFriend ID

def login(request):
    authentication_form = AuthenticationForm()    
    error = ''
    if request.method == 'POST':
        authentication_form = AuthenticationForm(data=request.POST)
        if authentication_form.is_valid():
            auth_login(request, authentication_form.get_user())
            try: 
                url = request.GET['next']
                return HttpResponseRedirect(url)
            except: 
                return HttpResponseRedirect('/home/')
        else:
            error = 'Invalid username or password'
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
    return render_to_response('index.html', { 'authentication_form': authentication_form, 'error': error, 'request': request }, context_instance=RequestContext(request))

def login_error(request):
    error = 'Invalid username or password'
    authentication_form = AuthenticationForm()
    return render_to_response('index.html', { 'authentication_form': authentication_form, 'error': error, 'request': request }, context_instance=RequestContext(request))

def user_signup(request):
    if request.method == 'POST': 
        user_creation_form = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            username = user_creation_form.cleaned_data['username']
            password = user_creation_form.cleaned_data['password1']
            new_user = user_creation_form.save()
            new_user.email = new_user.username
            new_user.first_name = request.POST['firstname']
            new_user.save()
        
            userprofile_id = create_userprofile_id()
            user_profile = UserProfile(userprofile_id=userprofile_id, user=new_user)
            user_profile.save()

            new_user = authenticate(username=username, password=password)
            auth_login(request, new_user)
            
            # Send Email Start
            context = Context( {} )
            subject, to = 'Welcome to BridgeBill', new_user.email
            account_creation_txt_content = account_creation_txt.render(context)
            account_creation_html_content = account_creation_html.render(context)
            send_html_mail(subject, account_creation_txt_content, account_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ to ])
            # Send Email End

            userfriend_id = create_userfriend_id()
            user_own_friend = UserFriend(userfriend_id=userfriend_id, user_profile=user_profile, friend_email=request.user.email, friend_name=request.user.first_name+' '+ request.user.last_name)
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
    userprofile_object = UserProfile.objects.get(user=request.user)
    total_borrowed_amount = 0
    total_lent_amount = 0

    class Persons:
        def __init__(self, name, total_borrowed=0, total_lent=0, total=0, total_flag='', slug=''):
            self.name = name
            self.total_borrowed = total_borrowed
            self.total_lent = total_lent
            self.total = total
            self.total_flag = total_flag
            self.slug = slug

    persons_list = []
    borrower_also_lender_list = []

    my_borrowers = UserFriend.objects.filter(user_profile=userprofile_object).exclude(friend_email=userprofile_object.user.email)
    for each_borrower in my_borrowers:
        each_borrower_bills = BillDetails.objects.filter(bill__lender=userprofile_object, borrower=each_borrower, bill_cleared='N')
        total_lent = 0
        total_borrowed = 0
        if each_borrower_bills:
            for each_bill in each_borrower_bills:
                total_borrowed += each_bill.individual_amount
            person = Persons(name=each_borrower.friend_name, total_borrowed=total_borrowed, slug=each_borrower.userfriend_id)
            try:
                borrower_as_user = UserProfile.objects.get(user__email=each_borrower.friend_email)
                try: 
                    me_as_borrower = UserFriend.objects.get(user_profile=borrower_as_user, friend_email=userprofile_object.user.email)
                    borrower_also_lender_list.append(each_borrower.friend_email)
                    each_borrower_as_lender_bills = BillDetails.objects.filter(bill__lender=borrower_as_user, borrower=me_as_borrower, bill_cleared='N')
                    if each_borrower_as_lender_bills:
                        for each_bill in each_borrower_as_lender_bills:
                            total_lent += each_bill.individual_amount
                except:
                    pass
            except:
                pass

            person.total_lent = total_lent
            person.total = person.total_borrowed - person.total_lent
            if person.total < 0:
                person.total_flag = '-ve'
                person.total *= -1
            elif person.total > 0:
                person.total_flag = '+ve'
            elif person.total == 0:
                person.total_flag = '0'
            persons_list.append(person)

    borrower_also_lender_userprofiles = []
    if borrower_also_lender_list:
        for borrower_also_lender in borrower_also_lender_list:
            borrower_also_lender_userprofile = UserProfile.objects.get(user__email=borrower_also_lender)
            borrower_also_lender_userprofiles.append(borrower_also_lender_userprofile)
    my_lenders = UserFriend.objects.filter(friend_email=userprofile_object.user.email).exclude(user_profile=userprofile_object).exclude(user_profile__in=borrower_also_lender_userprofiles)
    
    for each_lender in my_lenders:
        userprofile_lender = UserProfile.objects.get(user__email=each_lender.user_profile.user.email)
        borrower = UserFriend.objects.get(user_profile=userprofile_lender, friend_email = userprofile_object.user.email)
        each_lender_bills = BillDetails.objects.filter(bill__lender=userprofile_lender, borrower=borrower, bill_cleared='N')
        if each_lender_bills: 
            total_lent = 0
            for each_bill in each_lender_bills:
                total_lent += each_bill.individual_amount
            name = each_lender.user_profile.user.first_name + ' ' + each_lender.user_profile.user.last_name
            slug = userprofile_lender.userprofile_id
            person = Persons(name=name, total_lent=total_lent, slug=slug) 
            person.total = person.total_borrowed - person.total_lent
            if person.total < 0:
                person.total_flag = '-ve'
                person.total *= -1
            elif person.total > 0:
                person.total_flag = '+ve'
            elif person.total == 0:
                person.total_flag = '0'
            persons_list.append(person)

    return render_to_response('home.html', { 'persons_list': persons_list, 'request': request }, context_instance=RequestContext(request))

@login_required
def home_details(request, person_id):
    userprofile_object = UserProfile.objects.get(user=request.user)

    class Transactions:
        def __init__(self, date, description, individual_amount, flag, slug):
            self.date = date
            self.description = description
            self.individual_amount = individual_amount
            self.flag = flag
            self.slug = slug

    if request.method == 'GET':
        if person_id[:3] == 'uf_':
            person = 'borrower_and_lender'
        else:
            person = 'lender'

        if person == 'borrower_and_lender':
            bill_list = []
            # Start - First as borrower
            userfriend_id = person_id
            person_borrower = UserFriend.objects.get(user_profile=userprofile_object, userfriend_id=userfriend_id)
            person_name = person_borrower.friend_name
            person_borrower_bills = BillDetails.objects.filter(bill__lender=userprofile_object, borrower=person_borrower, bill_cleared='N').order_by('-bill__date')
            for each_bill in person_borrower_bills:
                transaction = Transactions(date=each_bill.bill.date, description=each_bill.bill.description, individual_amount=each_bill.individual_amount, flag='+ve', slug=each_bill.bill.overall_bill_id)
                bill_list.append(transaction)
            # End - First as borrower
            
            # Start - Second as lender
            person_email = person_borrower.friend_email
            try: 
                person_as_lender = UserProfile.objects.get(user__email=person_email)
                me_as_borrower = UserFriend.objects.get(user_profile=person_as_lender, friend_email=userprofile_object.user.email)
                person_lender_bills = BillDetails.objects.filter(bill__lender=person_as_lender, borrower=me_as_borrower, bill_cleared='N').order_by('-bill__date')
                for each_bill in person_lender_bills:
                    transaction = Transactions(date=each_bill.bill.date, description=each_bill.bill.description, individual_amount=each_bill.individual_amount, flag='-ve', slug=each_bill.bill.overall_bill_id)
                    bill_list.append(transaction)
            except:
                pass
            # End - Second as lender

            return render_to_response('home-details.html', { 'bill_list': bill_list, 'person_name': person_name, 'request': request }, context_instance=RequestContext(request))

        elif person == 'lender':
            bill_list = []
            userprofile_id = person_id
            
            person_as_lender = UserProfile.objects.get(userprofile_id=userprofile_id)
            person_name = person_as_lender.user.first_name + ' ' + person_as_lender.user.last_name
            me_as_borrower = UserFriend.objects.get(user_profile=person_as_lender, friend_email=userprofile_object.user.email)
            person_lender_bills = BillDetails.objects.filter(bill__lender=person_as_lender, borrower=me_as_borrower, bill_cleared='N').order_by('-bill__date')
            for each_bill in person_lender_bills:
                transaction = Transactions(date=each_bill.bill.date, description=each_bill.bill.description, individual_amount=each_bill.individual_amount, flag='-ve', slug=each_bill.bill.overall_bill_id)
                bill_list.append(transaction)

            return render_to_response('home-details.html', { 'bill_list': bill_list, 'person_name': person_name, 'request': request }, context_instance=RequestContext(request))

        else:
            pass




 
@login_required
def home_details1(request, person_id):
    userprofile_object = UserProfile.objects.get(user=request.user)
    if request.method == 'GET':
        if person_id[:3] == 'uf_':
            lender_or_borrower = 'borrower'
        else:
            lender_or_borrower = 'lender'

        person_actual_id = person_id[3:]
        borrower_name = ''
        borrower_bills = []
        total_borrowed_amount = 0
        lender_name = ''
        lender_bills = []
        total_lent_amount = 0

        if lender_or_borrower == 'borrower':
            borrower = True
            borrower = UserFriend.objects.get(userfriend_id=person_actual_id)
            borrower_name = borrower.friend_name
            borrower_bills = BillDetails.objects.filter(bill__lender=userprofile_object, borrower=borrower, bill_cleared='N')
            if borrower_bills:
                total_borrowed_amount = 0
                for borrower_bill in borrower_bills:
                    total_borrowed_amount += borrower_bill.individual_amount

            borrower_email = borrower.friend_email
            try: 
                borrower_as_userprofile = UserProfile.objects.get(user__email=borrower_email)
                try:
                    borrower_user_friend = UserFriend.objects.get(user_profile=borrower_as_userprofile, friend_email=userprofile_object.user.email)
                    lender_bills = BillDetails.objects.filter(bill__lender=borrower_as_userprofile, borrower=borrower_user_friend, bill_cleared='N')
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
            #userfriend_object = UserFriend.objects.get(userfriend_id=person_actual_id)
            #userprofile_object_two = userfriend_object.user_profile
            userprofile_object_two = UserProfile.objects.get(userprofile_id=person_actual_id)
            userfriend_object = UserFriend.objects.get(user_profile=userprofile_object_two, friend_email=userprofile_object.user.email)
            try: 
                lender_name = UserFriend.objects.get(user_profile=userprofile_object, friend_email=userprofile_object_two.email).friend_name
            except:
                lender_name = userprofile_object_two.user.first_name + ' ' + userprofile_object_two.user.last_name
            lender_bills = BillDetails.objects.filter(bill__lender=userprofile_object_two, borrower=userfriend_object, bill_cleared='N')
            
            total_lent_amount = 0
            for lender_bill in lender_bills:
                total_lent_amount += lender_bill.individual_amount

            borrower_email = userprofile_object_two.user.email
            try:
                userfriend_object = UserFriend.objects.get(user_profile=userprofile_object, friend_email=borrower_email)
                borrower_bills = BillDetails.objects.filter(bill__lender=userprofile_object, borrower=userfriend_object, bill_cleared='N')
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
            bill = BillDetails.objects.get(billdetail_id=i)
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
            userfriend_id = create_userfriend_id()
            user_friend = UserFriend(userfriend_id=userfriend_id, user=request.user)
            user_friend_form = UserFriendForm(request.POST, instance=user_friend)
            user_friend_form.save()
            return HttpResponseRedirect('/my-friends/')
    else: 
        user_friend_form = UserFriendForm()
    return render_to_response('add-friends.html', { 'user_friend_form': user_friend_form, 'request': request }, context_instance=RequestContext(request))

# Start - Recording Bills - Initial Option
@login_required
def record_bill_option(request):
    if request.method == 'POST':
        if request.POST['record_bill_option'] == 'equal_split':
            return HttpResponseRedirect('/record-bill/equal-split/')
        else: 
            return HttpResponseRedirect('/record-bill/unequal-split/')
    else:
        return render_to_response('record-bill-option.html', { 'request': request }, context_instance=RequestContext(request))
# End - Recording Bills - Initial Option

# Start - Creating unique overall bill ID
def create_overall_bill_id():
    check_counter = True
    while check_counter is True:
        overall_bill_id = 'ob_' + create_uuid()
        try: 
            bill = Bill.objects.get(overall_bill_id=overall_bill_id)
            check_counter = True
        except:
            check_counter = False
    return overall_bill_id
# End - Creating unique overall bill ID

# Start - Creating unique bill detail ID
def create_billdetail_id():
    check_counter = True
    while check_counter is True:
        billdetail_id = 'bd_' + create_uuid()
        try: 
            bill_detail = BillDetails.objects.get(billdetail_id=billdetail_id)
            check_counter = True
        except:
            check_counter = False
    return billdetail_id
# End - Creating unique bill detail ID

# Start - Record Bill - Equal Split
@login_required
def record_bill_equal_split(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        bill_form = PartialBillForm(request.POST)
        if bill_form.is_valid():
            overall_bill_id = create_overall_bill_id()
            lender = userprofile_object
            bill = Bill(overall_bill_id=overall_bill_id, lender=lender, date=bill_form.cleaned_data['date'], description=bill_form.cleaned_data['description'], amount=bill_form.cleaned_data['amount'])
            bill.save()
            number_of_borrowers = len(request.POST.getlist('people')) + len(request.POST.getlist('people_new'))
            individual_amount = float(bill_form.cleaned_data['amount']/number_of_borrowers)

            # For already existing friends
            if request.POST.getlist('people'):
                for borrower in request.POST.getlist('people'):
                    billdetail_id = create_billdetail_id()
                    if borrower != userprofile_object.user.email:
                        borrower_object = UserFriend.objects.get(user_profile=userprofile_object, friend_email=borrower)
                        bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower_object, individual_amount=individual_amount, bill_cleared='N')
                        bill_detail.save()
                        # Send Email Start
                        context = Context({ 'userprofile_object': userprofile_object, 'bill': bill, 'bill_detail': bill_detail })
                        subject = 'New Bill Recorded: ' + bill.description
                        bill_creation_txt_content = bill_creation_txt.render(context)
                        bill_creation_html_content = bill_creation_html.render(context)
                        send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ borrower ])
                        # Send Email End
                    else:
                        borrower_object = UserFriend.objects.get(user_profile=userprofile_object, friend_email=userprofile_object.user.email)
                        bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower_object, individual_amount=individual_amount, bill_cleared='Y')
                        bill_detail.save()
            
            # For new friends
            if request.POST.getlist('people_new'):
                for borrower in request.POST.getlist('people_new'):
                    i = borrower[11:]
                    friend_name = request.POST['name_'+str(i)]
                    friend_email = request.POST['email_'+str(i)]
                    try:
                        user_friend = UserFriend.objects.get(user_profile=userprofile_object, friend_email=friend_email)
                    except:
                        userfriend_id = create_userfriend_id()
                        user_friend = UserFriend(userfriend_id=userfriend_id, user_profile=userprofile_object, friend_name=friend_name, friend_email=friend_email)
                        user_friend.save()
                    borrower_object = user_friend
                    billdetail_id = create_billdetail_id()
                    bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower_object, individual_amount=individual_amount, bill_cleared='N')
                    bill_detail.save()

                    # Send Email Start
                    context = Context({ 'userprofile_object': userprofile_object, 'bill': bill, 'bill_detail': bill_detail })
                    subject = 'New Bill Recorded: ' + bill.description
                    bill_creation_txt_content = bill_creation_txt.render(context)
                    bill_creation_html_content = bill_creation_html.render(context)
                    send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ friend_email ])
                    # Send Email End

            return HttpResponseRedirect('/who-owes-me/')
    else:
        my_friends = UserFriend.objects.filter(user_profile=userprofile_object)
        bill_form = PartialBillForm()
        return render_to_response('record-bill-equal-split.html', { 'my_friends': my_friends, 'bill_form': bill_form, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_bill_unequal_split(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    my_friends = UserFriend.objects.filter(user_profile=userprofile_object)
    number_of_friends = my_friends.count()
    if request.method == 'POST':
        bill_form = PartialBillForm(request.POST)
        if bill_form.is_valid():
            overall_bill_id = create_overall_bill_id()
            lender = userprofile_object
            bill = Bill(overall_bill_id=overall_bill_id, lender=lender, date=bill_form.cleaned_data['date'], description=bill_form.cleaned_data['description'], amount=bill_form.cleaned_data['amount'])
            bill.save()

            # To count total people involved
            friends_total = 0
            for i in range(0, number_of_friends):
                if request.POST['borrower_'+str(i)] != '':
                    friends_total += 1
            new_friends_total = len(request.POST.getlist('people_new'))
            total_people = friends_total + new_friends_total

            # For existing friends
            for i in range(0, number_of_friends):
                borrower_counter = 'borrower_' + str(i)
                number_of_people_counter = 'number_of_people_' + str(i)
                borrower_amount_counter = 'borrower_amount_' + str(i)
                try:
                    if request.POST[borrower_counter] != '':
                        billdetail_id = create_billdetail_id()
                        if request.POST[borrower_counter] != userprofile_object.user.email:
                            borrower = UserFriend.objects.get(user_profile=userprofile_object, friend_email=request.POST[borrower_counter])
                            bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower, individual_amount=float(request.POST[borrower_amount_counter]), bill_cleared='N')
                            bill_detail.save()
                            # Send Email Start
                            context = Context({ 'userprofile_object': userprofile_object, 'bill': bill, 'bill_detail': bill_detail })
                            subject = 'New Bill Recorded: ' + bill.description
                            bill_creation_txt_content = bill_creation_txt.render(context)
                            bill_creation_html_content = bill_creation_html.render(context)
                            send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ request.POST[borrower_counter] ])
                            # Send Email End
                        else:
                            borrower = UserFriend.objects.get(user_profile=userprofile_object, friend_email=userprofile_object.user.email)
                            bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower, individual_amount=float(request.POST[borrower_amount_counter]), bill_cleared='Y')
                            bill_detail.save()
                    else:
                        continue
                except:
                    continue

            # For new friends
            if request.POST.getlist('people_new'):
                for borrower in request.POST.getlist('people_new'):
                    i = borrower[13:]
                    friend_name = request.POST['x_name_'+str(i)]
                    friend_email = request.POST['x_email_'+str(i)]
                    number_of_people = request.POST['x_number_of_people_'+str(i)]
                    borrower_amount = request.POST['x_borrower_amount_'+str(i)]
                    if friend_name and friend_email and number_of_people and borrower_amount:
                        try:
                            user_friend = UserFriend.objects.get(user_profile=userprofile_object, friend_email=friend_email)
                        except:
                            userfriend_id = create_userfriend_id()
                            user_friend = UserFriend(userfriend_id=userfriend_id, user_profile=userprofile_object, friend_name=friend_name, friend_email=friend_email)
                            user_friend.save()
                        borrower_object = user_friend
                        billdetail_id = create_billdetail_id()
                        bill_detail = BillDetails(billdetail_id=billdetail_id, bill=bill, borrower=borrower_object, individual_amount=borrower_amount, bill_cleared='N')

                        bill_detail.save()
                        
                        # Send Email Start
                        context = Context({ 'userprofile_object': userprofile_object, 'bill': bill, 'bill_detail': bill_detail })
                        subject = 'New Bill Recorded: ' + bill.description
                        bill_creation_txt_content = bill_creation_txt.render(context)
                        bill_creation_html_content = bill_creation_html.render(context)
                        send_html_mail(subject, bill_creation_txt_content, bill_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ friend_email ])
                        # Send Email End

            return HttpResponseRedirect('/who-owes-me/')
    else: 
        bill_form = PartialBillForm()
        return render_to_response('record-bill-unequal-split.html', { 'my_friends': my_friends, 'bill_form': bill_form, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_payment_partial_form(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        payment_form = PartialBillForm()
        lender = UserProfile.objects.get(user__email=request.POST['people'])
        borrower = UserFriend.objects.get(user_profile=lender, friend_email=userprofile_object.user.email)
        bill_details = BillDetails.objects.filter(bill__lender=lender, borrower=borrower, bill_cleared='N')
        all_amount = 0
        for bill_detail in bill_details:
            all_amount += bill_detail.individual_amount
        return render_to_response('record-payment.html', { 'payment_form': payment_form, 'lender': lender, 'bill_details': bill_details, 'all_amount': all_amount, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request)) 
    else:
        my_lenders_masterlist = UserFriend.objects.filter(friend_email=userprofile_object.user.email).exclude(user_profile=userprofile_object)
        class My_Lender:
            def __init__(self, name, email):
                self.name = name
                self.email = email
        my_lender_list = []
        for my_lender in my_lenders_masterlist:
            temp = 0
            my_lender_as_user = UserProfile.objects.get(user__email=my_lender.user_profile.user.email)
            me_as_userfriend = UserFriend.objects.get(user_profile=my_lender_as_user, friend_email=userprofile_object.user.email)
            bills = Bill.objects.filter(lender=my_lender_as_user)
            for bill in bills:
                bill_details = BillDetails.objects.filter(bill=bill,borrower=me_as_userfriend, bill_cleared='N')
                if bill_details:
                    temp = 1
            if temp == 1:
                lender_name = my_lender_as_user.user.first_name + ' ' + my_lender_as_user.user.last_name
                try:
                    lender_name = UserFriend.objects.get(user_profile=userprofile_object, friend_email=my_lender_as_user.user.email).friend_name
                except:
                    pass
                lender_email = my_lender_as_user.user.email
                my_lender = My_Lender(name=lender_name, email=lender_email)
                my_lender_list.append(my_lender)
        return render_to_response('record-payment-partial-form.html', { 'my_lenders': my_lender_list, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def record_payment(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        payment_form = PartialBillForm(request.POST)
        lender = UserProfile.objects.get(user__email=request.POST['lender'])
        borrower = UserFriend.objects.get(user_profile=lender, friend_email=userprofile_object.user.email)
        bill_value = 0
        if payment_form.is_valid():
            if request.POST['overall_bill_id'] != '000': 
                bill_detail = BillDetails.objects.get(bill__overall_bill_id=request.POST['overall_bill_id'], borrower=borrower)
                bill_detail.bill_cleared='Y'
                bill_detail.save()
                bill_description = bill_detail.bill.description
            else:
                bill_details = BillDetails.objects.filter(bill__lender=lender, borrower=borrower)
                for bill_detail in bill_details:
                    bill_detail.bill_cleared='Y'
                    bill_detail.save()
                    bill_value += bill_detail.individual_amount
                bill_description = 'All Bills (Total: SGD ' + str(bill_value) + ')'
            # Send Email Start
            context = Context({ 'userprofile_object': userprofile_object, 'description': bill_description })
            subject = 'New Payment by: ' + userprofile_object.user.first_name + ' ' + userprofile_object.user.last_name
            payment_creation_txt_content = payment_creation_txt.render(context)
            payment_creation_html_content = payment_creation_html.render(context)
            send_html_mail(subject, payment_creation_txt_content, payment_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ lender.user.email ])
            # Send Email End

            return HttpResponseRedirect('/who-i-owe/')
    else:
        return HttpResponseRedirect('/record-payment/')

@login_required
def who_i_owe(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    me_as_borrower = UserFriend.objects.filter(friend_email=userprofile_object.user.email)

    class My_Lender:
        def __init__(self, lender_name, bill_date, bill_description, bill_individual_amount, bill_overall_bill_id):
            self.lender_name = lender_name
            self.bill_date = bill_date
            self.bill_description = bill_description
            self.bill_individual_amount = bill_individual_amount
            self.bill_overall_bill_id = bill_overall_bill_id
    my_lender_list = []
    bill_details_my_lenders = BillDetails.objects.filter(borrower__in=me_as_borrower, bill_cleared='N').exclude(bill__lender=userprofile_object).order_by('bill__lender')
    for bill_detail in bill_details_my_lenders:
        try:
            lender_name = UserFriend.objects.get(user_profile=userprofile_object, friend_email=bill_detail.bill.lender.user.email).friend_name
        except:
            lender_name = bill_detail.bill.lender.user.first_name + ' ' + bill_detail.bill.lender.user.last_name
        bill_date = bill_detail.bill.date
        bill_description = bill_detail.bill.description
        bill_individual_amount = bill_detail.individual_amount
        bill_overall_bill_id = bill_detail.bill.overall_bill_id
        my_lender = My_Lender(lender_name=lender_name, bill_date=bill_date, bill_description=bill_description, bill_individual_amount=bill_individual_amount, bill_overall_bill_id=bill_overall_bill_id)
        my_lender_list.append(my_lender)
    return render_to_response('who-i-owe.html', { 'my_lenders': my_lender_list, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def who_owes_me(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    me_borrow_me = UserFriend.objects.get(user_profile=userprofile_object, friend_email=userprofile_object.user.email)
    my_borrowers = BillDetails.objects.filter(bill__lender=userprofile_object, bill_cleared='N').exclude(borrower=me_borrow_me).order_by('borrower')
    return render_to_response('who-owes-me.html', { 'my_borrowers': my_borrowers, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def specific_bill_details(request, overall_bill_id):
    userprofile_object = UserProfile.objects.get(user=request.user)
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
                lender_as_user = UserProfile.objects.get(user__email=request.POST['lender'])
                user_friend = UserFriend.objects.get(user_profile=lender_as_user, friend_email=userprofile_object.user.email)
                bill_detail = BillDetails.objects.get(bill=bill, borrower=user_friend)
                bill_detail.bill_cleared = 'Y'
                bill_detail.save()

                # Send Email Start
                context = Context({ 'userprofile_object': userprofile_object, 'description': bill.description })
                subject = 'New Payment by: ' + userprofile_object.user.first_name  + ' ' + userprofile_object.user.last_name
                payment_creation_txt_content = payment_creation_txt.render(context)
                payment_creation_html_content = payment_creation_html.render(context)
                send_html_mail(subject, payment_creation_txt_content, payment_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ lender_as_user.user.email ])
                # Send Email End

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
        if bill.lender == userprofile_object:
            user_lender = True
        else:
            user_lender = False
        borrowers = BillDetails.objects.filter(bill=bill)
        return render_to_response('specific-bill-details.html', { 'bill': bill, 'borrowers': borrowers, 'user_lender': user_lender, 'userprofile_object': userprofile_object, 'request': request }, context_instance=RequestContext(request))

@login_required
def my_profile(request):
    userprofile_object = UserProfile.objects.get(user=request.user)
    edit = False 
    try:
        UserSocialAuth.objects.get(user=request.user)
        user_social_auth = True
    except: 
        user_social_auth = False
    if request.method == 'POST':
        if request.POST['edit_or_save'] == 'edit':
            edit = True
            return render_to_response('my-profile.html', { 'edit': edit, 'userprofile_object': userprofile_object, 'user_social_auth': user_social_auth, 'request': request }, context_instance=RequestContext(request))
        elif request.POST['edit_or_save'] == 'save':
            request.user.first_name = request.POST['first_name']
            try: 
                request.user.last_name = request.POST['last_name']
            except:
                pass
            request.user.save()
            return render_to_response('my-profile.html', { 'userprofile_object': userprofile_object, 'user_social_auth': user_social_auth, 'request': request }, context_instance=RequestContext(request))
    return render_to_response('my-profile.html', { 'edit': edit, 'userprofile_object': userprofile_object, 'user_social_auth': user_social_auth, 'request': request }, context_instance=RequestContext(request))

@login_required
def change_password(request):
    class Error:
        pass
    error = Error()
    try:
        UserSocialAuth.objects.get(user=request.user)
        user_social_auth = True
    except: 
        user_social_auth = False
    if not user_social_auth:
        if request.method == 'POST':
            old_password = request.POST['old_password']
            new_password1 = request.POST['new_password1']
            new_password2 = request.POST['new_password2']
            if old_password and new_password1 and new_password2:
                if request.user.check_password(old_password):
                    if new_password1 == new_password2:
                        request.user.set_password(new_password1)
                        request.user.save()
                        return HttpResponseRedirect('/change-password-success/')
                    else:
                        error.new_password = 'New passwords don\'t match. Try again.'
                else: 
                    error.old_password = 'Incorrect password'
            else:
                error.old_password = 'Please enter all fields'
    return render_to_response('change-password.html', { 'user_social_auth': user_social_auth, 'error': error, 'request': request }, context_instance=RequestContext(request))

@login_required
def change_password_success(request):
    return render_to_response('change-password-success.html', { 'request': request }, context_instance=RequestContext(request))

@login_required
def logout_user(request):
	auth_logout(request)
	return HttpResponseRedirect('/') 

def feedback(request):
    feedback_form = FeedbackForm()
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback_form.save() 

            # Start - Send Email 
            name = feedback_form.cleaned_data['name']
            email = feedback_form.cleaned_data['email']
            message = feedback_form.cleaned_data['message']
            context = Context({ 'name': name, 'email': email, 'message': message })
            subject = 'New Feedback by: ' + name
            feedback_txt_content = feedback_txt.render(context)
            feedback_html_content = feedback_html.render(context)
            send_html_mail(subject, feedback_txt_content, feedback_html_content, settings.DEFAULT_FROM_EMAIL, [ 'arpitrai@bridgebill.com', 'arpitrai@gmail.com' ])
            # End - Send Email

            return HttpResponseRedirect('/feedback/confirmation')
    return render_to_response('feedback.html', { 'feedback_form': feedback_form, 'request': request }, context_instance=RequestContext(request))

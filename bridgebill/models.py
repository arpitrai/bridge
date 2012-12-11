from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserProfile(models.Model):
    userprofile_id = models.CharField(max_length=50)
    user = models.OneToOneField(User)
    currency = models.CharField(max_length=5, blank=True)

    def __unicode__(self):
        return 'User: ' + self.user.first_name + ' ' + self.user.last_name

class UserFriend(models.Model):
    userfriend_id = models.CharField(max_length=50)
    user_profile = models.ForeignKey(UserProfile)
    friend_email = models.EmailField(max_length=75)
    friend_name = models.CharField(max_length=60)
    friend_created_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return 'Lender: ' + self.user_profile.user.email + ' is a friend of Borrower: ' + self.friend_email

class UserFriendForm(ModelForm):
    class Meta:
        model = UserFriend
        fields = ('friend_name', 'friend_email')

class Bill(models.Model):
    overall_bill_id = models.CharField(max_length=50)
    lender = models.ForeignKey(UserProfile)
    date = models.DateField()
    description = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=300, blank=True)
    created_date = models.DateField(auto_now_add=True)
    
    def __unicode__(self):
        return  str(self.lender) + ' created a bill for ' + str(self.description) + ' an amount of: ' + str(self.amount)

class PartialBillForm(ModelForm):
    class Meta:
        model = Bill
        fields = ('date', 'amount', 'description', 'remarks')

BILL_CLEARED_CHOICES = (
        ('N', 'No'),
        ('Y', 'Yes'),
        )

class BillDetails(models.Model):
    billdetail_id = models.CharField(max_length=50)
    bill = models.ForeignKey(Bill)
    borrower = models.ForeignKey(UserFriend)
    individual_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_cleared = models.CharField(max_length=1, choices=BILL_CLEARED_CHOICES)
    individual_bill_created_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return str(self.bill.lender) + ' lent ' + str(self.borrower.friend_name) + ' for ' + str(self.bill.description)

class Feedback(models.Model):
    name = models.CharField(blank=True, max_length=60)
    email = models.EmailField(blank=True, max_length=75)
    message = models.TextField()
    created_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name) + '(' + str(self.email) + ')' + ' left a message'

class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback 

# Start - Signals for sending email on user registration and for adding user as own friend
from django.dispatch import receiver
from social_auth.signals import socialauth_registered

from django.conf import settings
if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail, send_html_mail
else:
    from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
account_creation_txt = get_template('email_templates/account_creation.txt')
account_creation_html = get_template('email_templates/account_creation.html')


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

def new_users_handler(sender, user, response, details, **kwargs):
    user.is_new = True

    # Start - Send Email
    context = Context( {} )
    subject, to = 'Welcome to BridgeBill', user.email
    account_creation_txt_content = account_creation_txt.render(context)
    account_creation_html_content = account_creation_html.render(context)
    send_html_mail(subject, account_creation_txt_content, account_creation_html_content, settings.DEFAULT_FROM_EMAIL, [ to ])
    # End - Send Email
    
    # Start - Add User as his own friend
    userprofile_id = create_userprofile_id()
    user_profile = UserProfile(userprofile_id=userprofile_id, user=user)
    user_profile.save()

    userfriend_id = create_userfriend_id()
    user_own_friend = UserFriend(userfriend_id=userfriend_id, user_profile=user_profile, friend_email=user.email, friend_name=user.first_name+' '+user.last_name)
    user_own_friend.save()
    # End - Add User as his own friend

    return False

socialauth_registered.connect(new_users_handler, sender=None)
# End - Signals for sending email on user registration and for adding user as own friend

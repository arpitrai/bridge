from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from bridgebill import views

# For serving static files on development environment
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.login),
    #url(r'^$', 'django.contrib.auth.views.login', { 'template_name': 'index.html' }),
    url(r'^login-error$', views.login_error),

    url(r'^home/$', views.home),
    url(r'^home/details/(?P<person_id>[a-zA-Z0-9_-]+)/$', views.home_details),
    url(r'^bill/details/(?P<overall_bill_id>[a-zA-Z0-9_-]+)/$', views.specific_bill_details),
    url(r'^user/sign-up/$', views.user_signup),
    url(r'^user/forgot-password/$', views.forgot_password),
    url(r'^my-friends/$', views.my_friends, { 'delete': False }),
    url(r'^my-friends/add-friends/$', views.add_friends),
    url(r'^my-friends/delete-friends/$', views.my_friends, { 'delete': True }),
    url(r'^record-bill/$', views.record_bill_option),
    url(r'^record-bill/equal-split/$', views.record_bill_equal_split),
    url(r'^record-bill/unequal-split/$', views.record_bill_unequal_split),
    url(r'^record-payment/$', views.record_payment_partial_form),
    url(r'^record-payment-full/$', views.record_payment),
    url(r'^who-i-owe/$', views.who_i_owe),
    url(r'^who-owes-me/$', views.who_owes_me),
    url(r'^my-profile/$', views.my_profile),
    url(r'^change-password/$', views.change_password),
    url(r'^change-password-success/$', views.change_password_success),
    url(r'^logout/$', views.logout_user),
    url(r'^about-us/$', direct_to_template, { 'template': 'about-us.html' }),
    url(r'^feedback/$',  views.feedback),
    url(r'^feedback/confirmation$', direct_to_template, { 'template': 'feedback_success.html' }),
    url(r'^contact-us/$', direct_to_template, { 'template': 'contact-us.html' }),

    url(r'', include('social_auth.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# For serving static files on development environment
urlpatterns += staticfiles_urlpatterns()

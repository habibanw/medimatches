from django.urls import path
from . import views
from .views import index, about, services, faq, profile, profile_view, create_message, message_delete, symptom_suggester
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    path('faq/', faq, name='faq'),
    path('profile/', profile_view, name='profile'),
    path('profile/messages', views.MessagesListView.as_view(), name='messages'),
    path('profile/appointments', views.AppointmentsListView.as_view(), name='appointments'),
    path('profile/messages/<int:id>/delete', views.message_delete, name='delete_message'),
    path('profile/messages/<int:id>/reply', views.reply_message, name='reply_message'),
    path('profile/messages/<int:id>/is_read', views.message_is_read, name='message_is_read'),
    path('contact/', views.contact_us, name='contact'),
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/<int:pk>', views.ProviderDetailView.as_view(), name='provider-details'),
    path('providers/<int:id>/send_message', views.create_message, name='send_message'),
    path('providers/<int:id>/schedule_appt', views.request_appointment, name='request_appointment'),
    path('appointments/appt_detail/<int:pk>', views.AppointmentDetailView.as_view(), name='appointment-details'),
    path('appointments/appt_detail/<int:pk>/appointment_status', views.appointment_status_update, name='appointment_status'),
    path('appointments/appt_detail/<int:pk>/cancel_appointment', views.cancel_appt, name='cancel_appointment'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('invalid/', views.user_login, name='invalid'),
    path('choose_role/', views.register_choose_role, name='register_choose_role'),
    path('no_provider_id/', views.no_provider_id, name='no_provider_id'),
    path('create_provider_account/', views.create_provider_account, name='create_provider_account'),
    path('create_user_account', views.create_user_account, name='create_user_account'), 
    path('check_provider_id', views.check_provider_id, name='check_provider_id'),
    path('provider_update', views.provider_update, name='provider_update'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('403/', views.provider_update, name='invalid'),
    path('user_update', views.user_update, name='user_update'),
    path('feedback', views.feedback, name='feedback'),
    path('suggest_specialist', views.symptom_suggester, name='symptpom_suggester'),
    path('reset_password',auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'),name="password_reset"),
    path('reset_password_sent',auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'),name="password_reset_confirm"),
    path('reset_password_complete',auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'),name="password_reset_complete"),
]
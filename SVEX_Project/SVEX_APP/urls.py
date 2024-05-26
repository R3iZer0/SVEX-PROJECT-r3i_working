
from django.urls import path
from . import views
from .views import EditClientProfileView
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [
    path('', views.home, name='home'),
    path('client/', views.client_home, name='client_home'),
    path('manager/', views.manager_home, name='manager_home'),
    path('login/', views.custom_login, name='custom_login'),
    path('login-new/', views.new_login, name='new_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('register/', views.register, name='register'),
    path('register-new/', views.register_new, name='register_new'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('create-support-ticket/', views.create_support_ticket, name='create_support_ticket'),
    path('ticket-created-successfully/', views.ticket_created_successfully, name='ticket_created_successfully'),
    path('edit-email/', views.change_email_address, name='change_email_address'),
    path('client-profile/', views.client_profile, name='client_profile'),
    path('update-profile/', EditClientProfileView.as_view(), name='edit_client_profile'),
    path('client_list/', views.client_list, name='client_list'),
    path('edit_client/<int:pk>/', views.edit_client_manager, name='edit_client'),
    path('edit-website/', views.edit_website, name='edit_website'),
    path('kyc_verification/', views.kyc_submit, name='kyc_verification'),
    path('kyc_status/', views.kyc_status, name='kyc_status'),
    path('my_wallets/', views.wallet_balance, name='my_wallets'),
    path('open-tickets/', views.open_ticket_list, name='open_tickets'),
    path('all-tickets/', views.all_tickets, name='all_tickets'),
    path('closed-tickets/', views.closed_tickets, name='closed_tickets'),
    path('tickets_in_progress/', views.tickets_in_progress, name='tickets_in_progress'),
    path('edit-case/<int:case_id>/', views.edit_case, name='edit_case'),
    path('my-profile/', views.my_profile_manager, name='my_profile_manager'),
    path('edit-profile/', views.edit_profile_manager, name='edit_profile'),
    path('view-kyc/', views.view_kyc, name='view_kyc'),
    path('edit-kyc/<int:kyc_id>/', views.edit_kyc, name='edit_kyc'),
    path('view-client-wallet/', views.view_client_wallet, name='view_client_wallet'),
    path('edit-client-wallet/<int:client_wallet_id>/', views.edit_client_wallet, name='edit_client_wallet'),
    path('deposit_wallet/', views.deposit_wallet, name='deposit_wallet'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),

    
    path('password-reset/', PasswordResetView.as_view(
        template_name='SVEX_APP/password_reset.html'
    ), name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='SVEX_APP/password_reset_done.html'
    ), name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='SVEX_APP/password_reset_confirm.html'
    ), name='password-reset-confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(
        template_name='SVEX_APP/password_reset_complete.html'
    ), name='password-reset-complete'),

    path('password-reset/', 
         PasswordResetView.as_view(
            template_name='SVEX_App/password_reset.html',
            html_email_template_name='SVEX_App/password_reset_email.html'
        ),
        name='password-reset'
    ),

    path('home-page', views.home_page, name='home_page'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/settings', views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/orders', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/history', views.dashboard_history, name='dashboard_history'),
    path('dashboard/staking', views.dashboard_staking, name='dashboard_staking'),
    path('dashboard/tickets', views.dashboard_support_tickets, name='dashboard_support_tickets'),
    path('get-tickets/', views.get_tickets, name='get_tickets'),
    path('faq', views.faq, name='faq'),
    path('dashboard/wallets', views.wallets_index, name='wallets_index'),
    # path('dashboard/wallets/transfer', views.wallets_transfer, name='wallets_transfer'),
    path('dashboard/wallets/withdraw', views.wallets_withdraw, name='wallets_withdraw'),
    path('dashboard/wallets/deposit', views.wallets_deposit, name='wallets_deposit'),
    path('buy-crypto', views.buy_crypto, name='buy_crypto'),
    path('markets', views.markets, name='markets'),
    path('exchange', views.exchange, name='exchange'),
    path('test', views.test, name='test'),
    path('test-2', views.test_2, name='test_2'),
    path('test-3', views.test_3, name='test_3'),
    path('change-password', views.change_password, name='change_password'),
    path('change-email', views.change_email, name='change_email'),

]

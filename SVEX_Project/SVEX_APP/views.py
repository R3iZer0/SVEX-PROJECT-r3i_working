import os

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, get_object_or_404
from .forms import KYCForm, SignUpForm, LoginForm, ClientSupportTicketForm,NewSignUpForm, CustomUserChangeForm, UpdateClientForm, Edit_Client_from_manager_Form, WebsiteForm, EditCaseForm, EditProfileManagerForm, EditKYCForm, EditClientWalletForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import KYCForm, SignUpForm, LoginForm, ClientSupportTicketForm,NewSignUpForm, CustomUserChangeForm, UpdateClientForm, Edit_Client_from_manager_Form, WebsiteForm, EditCaseForm, EditProfileManagerForm, EditKYCForm, EditClientWalletForm, WithdrawalForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .decorators import manager_required, client_required
from .models import KYC, ClientWallet, Deposit, DepositWallet, User, Case, Client , UserCredentials, Website, Withdrawal, WithdrawalMessage
from django.contrib import messages
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Sum, Subquery, OuterRef, Avg, Max, Min, Q
from django.contrib.auth.models import Group
from django.http import JsonResponse
import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.urls import resolve


# Create your views here.





############################################## Basic Views ####################################################################################################

#  Project HomePage
def home(request):
    return render(request, 'SVEX_APP/home.html')


#  Client HomePage
#@login_required(login_url='new_login')
#@client_required
def client_home(request):
    base_url = "https://api.binance.com/api/v3/ticker/24hr"
    currency_info = {
        "BTCUSDT": {"image": "BTC.png", "class_name": "Bitcoin"},
        "ETHUSDT": {"image": "ETH.png", "class_name": "Ethereum"},
        "BCHUSDT": {"image": "BCH.png", "class_name": "Bitcoin Cash"},
        "BNBUSDT": {"image": "BNB.png", "class_name": "Binance Coin"},
        "SOLUSDT": {"image": "SOL.png", "class_name": "Solana"},
        "XRPUSDT": {"image": "XRP.png", "class_name": "Ripple"},
        "LTCUSDT": {"image": "LTC.png", "class_name": "Litecoin"},
        "ADAUSDT": {"image": "ADA.png", "class_name": "Cardano"},
        "LUNAUSDT": {"image": "LUNA.png", "class_name": "Terra"},
    }
    currency_data = []

    for symbol, info in currency_info.items():
        params = {'symbol': symbol}
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            last_price = float(data['lastPrice'])
            price_change_percent = float(data['priceChangePercent'])
            image_url = f"/static/images/home-page/{info['image']}"
            class_name = info['class_name']
            price_change_percent_display = add_plus(price_change_percent)
            currency_data.append({
                'symbol': symbol,
                'last_price': last_price,
                'price_change_percent': price_change_percent,
                'price_change_percent_display': price_change_percent_display,
                'image_url': image_url,
                'class_name': class_name,
            })
        else:
            currency_data.append({'symbol': symbol, 'error': f"Error: {response.status_code}, {response.text}"})
    #get the logged in user
    user = request.user
    return render(request, 'SVEX_APP/navbar/homepage.html', {'currency_data': currency_data,'user_email':user.email})



# Manager HomePage
#@login_required(login_url='new_login')
#@manager_required
def manager_home(request):

    context = {}

    # Client Statistics
    total_clients = Client.objects.count()
    active_clients_count = 0
    phone_provided_percentage = 0
    if total_clients != 0:
        phone_provided_percentage = Client.objects.exclude(phone__isnull=True).count() / total_clients * 100

    address_provided_percentage = 0
    if total_clients != 0:
        address_provided_percentage = Client.objects.exclude(address__isnull=True).count() / total_clients * 100

    credits_summary = Client.objects.aggregate(
        average_credits=Avg('client_credits'),
        max_credits=Max('client_credits'),
        min_credits=Min('client_credits')
    )

    context.update({
        'total_clients': total_clients,
        'active_clients_count': active_clients_count,
        'phone_provided_percentage': phone_provided_percentage,
        'address_provided_percentage': address_provided_percentage,
        'credits_summary': credits_summary,

    })

    # KYC statistics
    total_kyc_pending = KYC.objects.filter(verification_status='pending').count()
    total_kyc_confirmed = KYC.objects.filter(verification_status='confirmed').count()
    total_kyc_cancelled = KYC.objects.filter(verification_status='cancelled').count()
    total_clients_with_kyc = KYC.objects.exclude(verification_status='pending').count()
    # Calculate the percentage of clients with completed KYC
    if total_clients > 0:
        percentage_clients_with_kyc = (total_clients_with_kyc / total_clients) * 100
    else:
        percentage_clients_with_kyc = 0  # Set percentage to 0 if total_clients is 0

    context.update({
        'total_kyc_pending': total_kyc_pending,
        'total_kyc_confirmed': total_kyc_confirmed,
        'total_kyc_cancelled': total_kyc_cancelled,
        'percentage_clients_with_kyc': percentage_clients_with_kyc,
    })

    # ClientWallet statistics
    total_wallets = ClientWallet.objects.count()
    total_spotbtc_balance = ClientWallet.objects.aggregate(total_spotbtc_balance=Sum('spotbtc_balance'))['total_spotbtc_balance']
    total_btc_balance = ClientWallet.objects.aggregate(total_btc_balance=Sum('btc_balance'))['total_btc_balance']
    total_eth_balance = ClientWallet.objects.aggregate(total_eth_balance=Sum('eth_balance'))['total_eth_balance']
    total_usdt_balance_erc20 = ClientWallet.objects.aggregate(total_usdt_balance_erc20=Sum('usdt_balance_erc20'))['total_usdt_balance_erc20']
    total_usd_balance_trc20 = ClientWallet.objects.aggregate(total_usd_balance_trc20=Sum('usd_balance_trc20'))['total_usd_balance_trc20']
    context.update({
        'total_wallets': total_wallets,
        'total_spotbtc_balance': total_spotbtc_balance,
        'total_btc_balance': total_btc_balance,
        'total_eth_balance': total_eth_balance,
        'total_usdt_balance_erc20': total_usdt_balance_erc20,
        'total_usd_balance_trc20': total_usd_balance_trc20,
    })

    # Case statistics
    total_cases = Case.objects.count()
    total_open_cases = Case.objects.filter(case_status='Open').count()
    total_in_progress_cases = Case.objects.filter(case_status='In Progress').count()
    total_resolved_cases = Case.objects.filter(case_status='Closed-Resolved').count()
    total_pending_cases = Case.objects.exclude(case_status='Closed-Resolved').count()
    context.update({
        'total_cases': total_cases,
        'total_open_cases': total_open_cases,
        'total_in_progress_cases': total_in_progress_cases,
        'total_resolved_cases': total_resolved_cases,
        'total_pending_cases': total_pending_cases,
    })

    # Website information
    website_info = Website.objects.first()
    context.update({'website_info': website_info})

    return render(request, 'SVEX_APP/manager_home.html', context)


# Custom Login with redirection

def custom_login(request):
    msg = None

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_manager:
                    return redirect('manager_home')  # Redirect managers to manager_home
                elif user.is_client:
                    return redirect('home_page')  # Redirect clients to client_home

                else:
                    msg = "Invalid Login Credentials"
            else:
                msg = "Incorrect username or password"
        else:
            msg = 'Form Error'
    return render(request, 'SVEX_APP/custom_login.html', {'form': form, 'msg': msg})


def new_login(request):
    msg = None
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_manager:
                    return redirect('manager_home')  # Redirect managers to manager_home
                elif user.is_client:
                    return redirect('home_page')  # Redirect clients to client_home

                else:
                    msg = "Invalid Login Credentials"
            else:
                msg = "Incorrect username or password"
        else:
            msg = 'Form Error'
    return render(request, 'SVEX_APP/auth/login.html', {'form': form, 'msg': msg})


# Logout
def custom_logout(request):
    logout(request)
    return redirect('home')











############################# Manager Dashboard ##########################################################################


# Register user from Manager

from django.contrib.auth.models import Group

#@login_required(login_url='new_login')
#@manager_required
def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Extract username and password from the form
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']

            # Save the username and password to UserCredentials model
            UserCredentials.objects.create(username=username, password=raw_password)

            user = form.save()

            # Assign the user to the appropriate group based on their attributes
            if form.cleaned_data['is_manager']:
                manager_group = Group.objects.get(name='Managers')
                user.groups.add(manager_group)
            elif form.cleaned_data['is_client']:
                client_group = Group.objects.get(name='Clients')
                user.groups.add(client_group)

            msg = 'User created successfully'
            return redirect('register')
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    return render(request, 'SVEX_APP/register.html', {'form': form, 'msg': msg})






# View Client
#@login_required(login_url='new_login')
#@manager_required
def client_list(request):
    clients = Client.objects.all()  # Retrieve all client objects
    context = {'clients': clients}  # Pass the list of clients to the template context
    return render(request, 'SVEX_APP/client_list.html', context)





# Edit client
#@login_required(login_url='new_login')
#@manager_required
def edit_client_manager(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = Edit_Client_from_manager_Form(request.POST or None, instance=client)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Client details updated successfully.')
            return redirect('client_list')  # Redirect to client list upon successful edit
        else:
            messages.error(request, 'Form has errors. Please correct them.')

    return render(request, 'SVEX_APP/edit_client_manager.html', {'form': form, 'client': client})



# Edit website details
#@login_required(login_url='new_login')
#@manager_required
def edit_website(request):
    # Retrieve the current website details from the database
    website = Website.objects.first()  # Assuming there's only one website record
    
    # If the website details exist, populate the form with the current data
    if website:
        form = WebsiteForm(request.POST or None, instance=website)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('manager_home')  # Redirect  upon successful edit
    else:
        # If no website details exist, create a new form instance
        form = WebsiteForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('manager_home')  # Redirect to view_website URL upon successful creation
    
    return render(request, 'SVEX_APP/edit_website.html', {'form': form})





# My Profile
#@login_required(login_url='new_login')
#@manager_required
def my_profile_manager(request):
    user = request.user
    return render(request, 'SVEX_APP/my_profile_manager.html', {'user': user})




#@login_required(login_url='new_login')
#@manager_required
def edit_profile_manager(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileManagerForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('my_profile_manager')  # Redirect to the profile page after saving changes
    else:
        form = EditProfileManagerForm(instance=user)
    return render(request, 'SVEX_APP/edit_profile_manager.html', {'form': form})




############################## KYC--Manager #################################################


#@login_required(login_url='new_login')
#@manager_required
def view_kyc(request):
    kyc_entries = KYC.objects.all()
    # map the kyc_entries and remove the SVEX_APP prefix from id_front and id_back
    for entry in kyc_entries:
        entry.id_front = entry.id_front.url.split('SVEX_APP')[1]
        entry.id_back = entry.id_back.url.split('SVEX_APP')[1]

    return render(request, 'SVEX_APP/view_kyc.html', {'kyc_entries': kyc_entries})


# Edit KYC
#@login_required(login_url='new_login')
#@manager_required
def edit_kyc(request, kyc_id):
    kyc_entry = get_object_or_404(KYC, pk=kyc_id)
    if request.method == 'POST':
        form = EditKYCForm(request.POST, instance=kyc_entry)
        if form.is_valid():
            form.save()
            return redirect('view_kyc')
    else:
        form = EditKYCForm(instance=kyc_entry)
    return render(request, 'SVEX_APP/edit_kyc_page.html', {'form': form, 'kyc_entry': kyc_entry})




############## Client Wallets --- Manager #################################################33




# View client wallets from manager
#@login_required(login_url='new_login')
#@manager_required
def view_client_wallet(request):
    client_wallets = ClientWallet.objects.all()
    return render(request, 'SVEX_APP/view_client_wallet.html', {'client_wallets': client_wallets})




# Edit the wallets
#@login_required(login_url='new_login')
#@manager_required
def edit_client_wallet(request, client_wallet_id):
    # Retrieve the client wallet object from the database
    client_wallet = ClientWallet.objects.get(pk=client_wallet_id)
    
    # Check if the form has been submitted
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = EditClientWalletForm(request.POST, instance=client_wallet)
        if form.is_valid():
            # Save the updated client wallet object
            form.save()
            # Redirect to the view client wallet page
            return redirect('view_client_wallet')
    else:
        # Create a form instance with the current client wallet data
        form = EditClientWalletForm(instance=client_wallet)
    
    # Render the edit client wallet template with the form and client wallet object
    return render(request, 'SVEX_APP/edit_client_wallet_page.html', {'form': form, 'client_wallet': client_wallet})


######################################### Client Side #######################################################################



# Client Sign up




def register_new(request):
    msg = None
    if request.method == 'POST':
        form = NewSignUpForm(request.POST)
        if form.is_valid():
            # Extract username and password from the form
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']
            UserCredentials.objects.create(username=username, password=raw_password)
            user = form.save()
            client_group = Group.objects.get(name='Clients')
            user.groups.add(client_group)

            msg = 'User created successfully'
            return redirect('new_login')
        else:
            msg = 'Invalid Credentials'
    else:
        form = NewSignUpForm()
    return render(request, 'SVEX_APP/auth/register.html', {'form': form, 'msg': msg})



def forgot_password(request):
    return render(request, 'SVEX_APP/auth/forgot-password.html')



# Change Email for Client
def change_email_address(request):
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('client_profile')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'SVEX_APP/edit_profile_client.html', {'form': form})



# Client Profile

def client_profile(request):
    
    user = request.user
    client = Client.objects.get(user=user)  # Retrieve the client object associated with the user
    context = {'client': client}  # Pass the client object to the template context
    return render(request, 'SVEX_APP/client_profile.html', context)





# Client to update his own data
class EditClientProfileView(View):
    def get(self, request):
        client = Client.objects.get(user=request.user)
        form = UpdateClientForm(instance=client)
        return render(request, 'SVEX_APP/update_client_profile.html', {'form': form})

    def post(self, request):
        client = Client.objects.get(user=request.user)
        form = UpdateClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('client_profile')
        else:
            messages.error(request, 'Failed to update your profile. Please check the form data.')
            return render(request, 'SVEX_APP/update_client_profile.html', {'form': form})


#kyc view
#@login_required
def kyc_submit(request):
    user = request.user

    # Check if the user has an associated KYC entry
    try:
        kyc_entry = KYC.objects.get(client=user)
        form = KYCForm(instance=kyc_entry)

        # Render the KYC form with existing data
        return render(request, 'SVEX_APP/kyc_verification.html', {'form': form})

    except KYC.DoesNotExist:
        # If the KYC entry doesn't exist, proceed with form submission
        if request.method == 'POST':
            form = KYCForm(request.POST, request.FILES)
            if form.is_valid():
                # Assign the logged-in user as the client for KYC
                kyc_instance = form.save(commit=False)
                kyc_instance.client = user
                kyc_instance.save()
                return redirect('kyc_status')  # Redirect to KYC status page or any other page

        else:
            # If it's a GET request or form is not valid, create a new form
            form = KYCForm()

        return render(request, 'SVEX_APP/kyc_verification.html', {'form': form})

#@login_required
def kyc_status(request):
    user = request.user

    # Fetch the KYC entry for the logged-in user
    kyc = KYC.objects.filter(client=user).first()

    context = {
        'kyc': kyc,
    }

    return render(request, 'SVEX_APP/kyc_status.html', context)




#Client Wallets
@login_required
def wallet_balance(request):
    user = request.user

    # Check if the user has an associated client
    if hasattr(user, 'client'):
        try:
            client_wallet = ClientWallet.objects.get(client=user)
        except ClientWallet.DoesNotExist:
            # If ClientWallet does not exist, create a new one
            client_wallet = ClientWallet.objects.create(client=user)

        context = {
            'spotbtc_balance': client_wallet.spotbtc_balance,
            'btc_balance': client_wallet.btc_balance,
            'eth_balance': client_wallet.eth_balance,
            'usdt_balance_erc20': client_wallet.usdt_balance_erc20,
            'usd_balance_trc20': client_wallet.usd_balance_trc20,
            # Add more balances here
        }

        return render(request, 'SVEX_APP/my_wallets.html', context)
    else:
        # Handle the case where the user has no associated client
        return HttpResponse("You need to create a client profile first.")



@login_required
def deposit_wallet(request):
    try:
        deposit_wallet_instance = DepositWallet.objects.get(user=request.user)
        context = {
            'deposit_wallet': deposit_wallet_instance
        }
    except DepositWallet.DoesNotExist:
        context = {}

    return render(request, 'SVEX_APP/deposit_wallet.html', context)




def withdraw(request):
    user = request.user
    client_wallet = ClientWallet.objects.get(client=user)
    withdrawal_denied_message = None

    # Check if the user is allowed to withdraw
    withdrawal_message = WithdrawalMessage.objects.filter(user=user).first()
    if withdrawal_message and not withdrawal_message.can_withdraw:
        withdrawal_denied_message = withdrawal_message.message

    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            crypto_currency = form.cleaned_data['crypto_currency']
            amount = form.cleaned_data['amount']
            wallet_withdraw = form.cleaned_data['wallet_withdraw']

            # Check if the user is allowed to withdraw
            if withdrawal_message and not withdrawal_message.can_withdraw:
                return render(request, 'SVEX_APP/withdraw_denied.html', {'message': withdrawal_message.message})

            # Check if the user has enough balance for Bitcoin (BTC)
            if crypto_currency == 'btc' and amount <= client_wallet.btc_balance:
                withdrawal = form.save(commit=False)
                withdrawal.client = user
                withdrawal.save()
                # Decrease the Bitcoin (BTC) balance
                client_wallet.btc_balance -= amount
                client_wallet.save()
                return redirect('withdrawal_success')  # Redirect to a success page

            # Check if the user has enough balance for Ethereum (ETH)
            elif crypto_currency == 'eth' and amount <= client_wallet.eth_balance:
                withdrawal = form.save(commit=False)
                withdrawal.client = user
                withdrawal.save()
                # Decrease the Ethereum (ETH) balance
                client_wallet.eth_balance -= amount
                client_wallet.save()
                return redirect('withdrawal_success')  # Redirect to a success page

            # Check if the user has enough balance for USDT ERC20
            elif crypto_currency == 'usdt_erc20' and amount <= client_wallet.usdt_balance_erc20:
                withdrawal = form.save(commit=False)
                withdrawal.client = user
                withdrawal.save()
                # Decrease the USDT ERC20 balance
                client_wallet.usdt_balance_erc20 -= amount
                client_wallet.save()
                return redirect('withdrawal_success')  # Redirect to a success page

            # Check if the user has enough balance for USDT TRC20
            elif crypto_currency == 'usd_trc20' and amount <= client_wallet.usd_balance_trc20:
                withdrawal = form.save(commit=False)
                withdrawal.client = user
                withdrawal.save()
                # Decrease the USDT TRC20 balance
                client_wallet.usd_balance_trc20 -= amount
                client_wallet.save()
                return redirect('withdrawal_success')  # Redirect to a success page

            else:
                # Display error message for insufficient balance
                form.add_error(None, 'Insufficient balance')
    else:
        form = WithdrawalForm()

    return render(request, 'SVEX_APP/withdraw.html', {'form': form, 'withdrawal_denied_message': withdrawal_denied_message})


def withdrawal_success(request):
    user = request.user
    withdrawal_message = WithdrawalMessage.objects.get(user=user)
    return render(request, 'SVEX_APP/withdrawal_success.html', {'withdrawal_message': withdrawal_message})




def transaction_history(request):
    user = request.user
    withdrawals = Withdrawal.objects.filter(client=user)
    deposits = Deposit.objects.filter(client=user)
    return render(request, 'SVEX_APP/transaction_history.html', {'withdrawals': withdrawals, 'deposits': deposits})

################################ Support Ticket #######################################################################################


#@login_required(login_url='new_login')
#@client_required
def create_support_ticket(request):
    if request.method == 'POST':
        form = ClientSupportTicketForm(request.POST)
        if form.is_valid():
            # Set the client ID (case_client) to the current user
            support_ticket = form.save(commit=False)
            support_ticket.case_client = request.user
            support_ticket.save()
            messages.success(request, 'Ticket created successfully.')
            # Redirect to the 'dashboard_support_tickets' URL after successful form submission
            return redirect('dashboard_support_tickets')
        else:
            messages.error(request, 'Please make sure all fields are filled correctly.')
            return redirect('dashboard_support_tickets')
    else:
        form = ClientSupportTicketForm()
    return render(request, 'SVEX_APP/dashboard/dashboard_support_tickets.html', {'form': form})


#@login_required(login_url='new_login')
#@client_required
def ticket_created_successfully(request):
    # Define a success message
    success_message = "Your support ticket has been created successfully. We will address it shortly."

    # Pass the success message to the template
    return render(request, 'SVEX_APP/ticket_created_successfully.html', {'success_message': success_message})
    # return render(request,'register.html', {'form': form, 'msg': msg})


# Dashboard Views
def dashboard(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard.html', {'user': request.user, 'wallet': client_wallet})


def dashboard_settings(request):
    current_path = resolve(request.path_info).url_name
    show_back_button = not current_path.endswith('dashboard')
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard_settings.html', {'show_back_button': show_back_button, 'user': request.user, 'wallet': client_wallet})


def dashboard_support_tickets(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard_support_tickets.html', {'user_email': request.user.email, 'wallet': client_wallet})


def get_tickets(request):
    query_param = request.GET.get('q')
    user_tickets = Case.objects.filter(case_client=request.user).order_by('id')

    if query_param:
        user_tickets = user_tickets.filter(
            Q(id__icontains=query_param) |
            Q(case_category__icontains=query_param) |
            Q(case_notes__icontains=query_param) |
            Q(case_status__icontains=query_param) |
            Q(case_subject__icontains=query_param)
        )

    # Pagination
    items_per_page = int(request.GET.get('items_per_page', 10))
    paginator = Paginator(user_tickets, items_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get the current page's data
    user_tickets_slice = page_obj.object_list

    tickets_data = [
        {
            'id': ticket.id,
            'subject': ticket.case_subject,
            'category': ticket.case_category,
            'status': ticket.case_status,
            'status_class': ticket.case_status.lower().replace(" ", ""),
            'notes': ticket.case_notes,
            'created_at': ticket.case_created_at,
        }
        for ticket in user_tickets_slice
    ]

    return JsonResponse({
        'tickets': tickets_data,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'total_entries': paginator.count,
        'items_per_page': items_per_page
    })

def dashboard_orders(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard_orders.html', {'user_email': request.user.email, 'wallet': client_wallet})


def dashboard_history(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard_funds_history.html', {'user_email': request.user.email, 'wallet': client_wallet})


def dashboard_staking(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/dashboard/dashboard_staking.html', {'user_email': request.user.email}, {'wallet': client_wallet})

def exchange(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/navbar/exchange.html', {'user_email': request.user.email, 'wallet': client_wallet})


def faq(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/navbar/faq.html', {'user_email': request.user.email, 'wallet': client_wallet})


def add_plus(value):
    return f"+{value}" if value >= 0 else value


def home_page(request):
    base_url = "https://api.binance.com/api/v3/ticker/24hr"
    currency_info = {
        "BTCUSDT": {"image": "BTC.png", "class_name": "Bitcoin"},
        "ETHUSDT": {"image": "ETH.png", "class_name": "Ethereum"},
        "BCHUSDT": {"image": "BCH.png", "class_name": "Bitcoin Cash"},
        "BNBUSDT": {"image": "BNB.png", "class_name": "Binance Coin"},
        "SOLUSDT": {"image": "SOL.png", "class_name": "Solana"},
        "XRPUSDT": {"image": "XRP.png", "class_name": "Ripple"},
        "LTCUSDT": {"image": "LTC.png", "class_name": "Litecoin"},
        "ADAUSDT": {"image": "ADA.png", "class_name": "Cardano"},
        "LUNAUSDT": {"image": "LUNA.png", "class_name": "Terra"},
    }
    currency_data = []

    for symbol, info in currency_info.items():
        params = {'symbol': symbol}
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            last_price = float(data['lastPrice'])
            price_change_percent = float(data['priceChangePercent'])
            image_url = f"/static/images/home-page/{info['image']}"
            class_name = info['class_name']
            price_change_percent_display = add_plus(price_change_percent)
            currency_data.append({
                'symbol': symbol,
                'last_price': last_price,
                'price_change_percent': price_change_percent,
                'price_change_percent_display': price_change_percent_display,
                'image_url': image_url,
                'class_name': class_name,
            })
        else:
            currency_data.append({'symbol': symbol, 'error': f"Error: {response.status_code}, {response.text}"})

    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/navbar/homepage.html',
                  {'currency_data': currency_data, 'user_email': request.user.email, 'wallet': client_wallet})


def wallets_index(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/wallets/index.html', {'user_email': request.user.email, 'wallet': client_wallet})


def wallets_transfer(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/wallets/transfer.html', {'user_email': request.user.email, 'wallet': client_wallet})


def wallets_withdraw(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/wallets/withdraw.html', {'user_email': request.user.email, 'wallet': client_wallet})


def wallets_deposit(request):
    client_wallet = ClientWallet.objects.get(client=request.user)
    return render(request, 'SVEX_APP/wallets/deposit.html', {'user_email': request.user.email, 'wallet': client_wallet})


#@login_required(login_url='new_login')
#@manager_required
def open_ticket_list(request):
    # Query open tickets
    open_tickets = Case.objects.filter(case_status='Open')
    return render(request, 'SVEX_APP/open_ticket_list.html', {'open_tickets': open_tickets})


#@login_required(login_url='new_login')
#@manager_required
def all_tickets(request):
    all_cases = Case.objects.all()
    return render(request, 'SVEX_APP/all_tickets.html', {'all_cases': all_cases})


def test(request):
    return render(request, 'SVEX_APP/dashboard/layout.html')


#@login_required(login_url='new_login')
#@manager_required
def closed_tickets(request):
    # Define the closed statuses
    closed_statuses = [
        'Closed-Resolved',
        'Closed-NotResolved',
        'Closed-Spam',
        'Closed-Lost',
    ]
    # Filter cases based on closed statuses
    closed_cases = Case.objects.filter(case_status__in=closed_statuses)
    # Pass the closed cases to the template
    return render(request, 'SVEX_APP/closed_tickets.html', {'closed_cases': closed_cases})


def test_2(request):
    return render(request, 'SVEX_APP/wallets/layout.html')


#@login_required(login_url='new_login')
#@manager_required
def tickets_in_progress(request):
    in_progress_cases = Case.objects.filter(case_status__in=['In Progress', 'Responded', 'Escalated', 'On Hold'])
    return render(request, 'SVEX_APP/ticket_in_progress.html', {'in_progress_cases': in_progress_cases})


def test_3(request):
    return render(request, 'SVEX_APP/auth/layout.html')


# Edit Tickets
#@login_required(login_url='new_login')
#@manager_required
def edit_case(request, case_id):
    case = get_object_or_404(Case, pk=case_id)
    if request.method == 'POST':
        form = EditCaseForm(request.POST, instance=case)
        if form.is_valid():
            form.save()
            return redirect('all_tickets')
    else:
        form = EditCaseForm(instance=case)
    return render(request, 'SVEX_APP/edit_case_manager.html', {'form': form})


def buy_crypto(request):
    return render(request, 'SVEX_APP/navbar/buy-crypto.html')


def markets(request):
    return render(request, 'SVEX_APP/navbar/markets.html')


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        repeat_password = request.POST.get('repeatPassword')
        return HttpResponse("Password changed successfully")

    return render(request, 'your_template.html')


def change_email(request):
    if request.method == 'POST':
        old_email = request.POST.get('oldEmail')
        new_email = request.POST.get('newEmail')
        return HttpResponse("Email changed successfully")

    return render(request, 'your_template.html')

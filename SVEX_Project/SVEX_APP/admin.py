from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import KYC, ClientWallet, Deposit, User, Case, Client, UserCredentials, Website,DepositWallet, Withdrawal, WithdrawalMessage
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'  # Include all fields, including password

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    list_display = ['username', 'email', 'is_manager', 'is_client', 'is_superuser']
    list_filter = ['is_manager', 'is_client', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_manager', 'is_client')}),
        ('Groups', {'fields': ('groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_manager', 'is_client')}
        ),
    )
    search_fields = ['username', 'email']
    ordering = ['username']



class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_number', 'first_name', 'last_name', 'birthdate', 'client_credits', 'phone', 'address', 'zip_code')
    search_fields = ('user__username', 'client_number')
    list_filter = ('birthdate', 'client_credits')

class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'case_category', 'client_contact_details', 'case_status', 'case_client', 'case_subject', 'case_touch', 'case_priority', 'case_created_at', 'case_updated_at')
    search_fields = ('case_number', 'client_contact_details', 'case_subject')
    list_filter = ('case_status', 'case_touch', 'case_priority')

    fieldsets = (
        ('Basic Information', {
            'fields': ('case_number', 'case_category', 'client_contact_details', 'case_status', 'case_client', 'case_subject', 'case_touch', 'case_priority')
        }),
        ('Details', {
            'fields': ('case_notes', 'case_attachment', 'related_cases', 'case_resolution_details', 'customer_feedback')
        }),
        ('Timestamps', {
            'fields': ('case_created_at', 'case_updated_at')
        }),
    )

    readonly_fields = ('case_created_at', 'case_updated_at', 'case_number')



class UserCredentialsAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'new_password') # Display the fields in the admin list view
    
    
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'support_email', 'address', 'phone', 'telegram', 'whatsapp')
    search_fields = ('name', 'address', 'phone', 'telegram', 'whatsapp')
    list_filter = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'support_email', 'description', 'address', 'phone')
        }),
        ('Contact Information', {
            'fields': ('telegram', 'whatsapp')
        }),
        ('About Us', {
            'fields': ('about_us',)
        }),
    )
    
class KYCAdmin(admin.ModelAdmin):
    list_display = ('client', 'government_name', 'last_name', 'country', 'birthdate', 'is_verified', 'verification_status')
    search_fields = ('client__username', 'government_name', 'last_name', 'country')
    list_filter = ('is_verified', 'verification_status')

    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'government_name', 'last_name', 'country', 'birthdate')
        }),
        ('Verification', {
            'fields': ('id_front', 'id_back', 'is_verified', 'verification_status')
        }),
    )
    
    
    
class ClientWalletAdmin(admin.ModelAdmin):
    list_display = ('client', 'spotbtc_balance', 'btc_balance', 'eth_balance', 'usdt_balance_erc20', 'usd_balance_trc20')
    search_fields = ('client__username',)
    list_filter = ('spotbtc_balance', 'btc_balance', 'eth_balance', 'usdt_balance_erc20', 'usd_balance_trc20')

    fieldsets = (
        ('Client Information', {
            'fields': ('client',)
        }),
        ('Balances', {
            'fields': ('spotbtc_balance', 'btc_balance', 'eth_balance', 'usdt_balance_erc20', 'usd_balance_trc20')
        }),
    )

    readonly_fields = ('client',)
    



class CustomGroupAdmin(GroupAdmin):
    list_display = ['name', 'get_users']
    filter_horizontal = ['permissions']

    def get_users(self, obj):
        return ', '.join([user.username for user in obj.user_set.all()])

    get_users.short_description = 'Users'

# Unregister the default Group admin
admin.site.unregister(Group)

# Register the Group model with your custom admin class
admin.site.register(Group, CustomGroupAdmin)



admin.site.register(User, CustomUserAdmin)

admin.site.register(Client, ClientAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(UserCredentials, UserCredentialsAdmin)
admin.site.register(Website, WebsiteAdmin)

admin.site.register(KYC, KYCAdmin)
admin.site.register(ClientWallet, ClientWalletAdmin)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('client','amount', 'crypto_currency', 'status', 'time')

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('client','amount', 'crypto_currency', 'status', 'time')

    
admin.site.register(WithdrawalMessage)
admin.site.register(DepositWallet)


from django.contrib import admin
from .models import Profile, OTPLog, Bank, Account, Wallet, Currency, Transaction

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'middle_name', 'last_name', 'phone', 'email', 'trx_pin', 'profile_pic']
    list_filter = ['created']
    search_fields = ['phone', 'email', 'full_name']


@admin.register(OTPLog)
class OTPlogAdmin(admin.ModelAdmin):
    list_display = ['otp', 'phone', 'email']
    list_filter = ['timestamp']
    search_fields = ['otp', 'phone', 'email']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    list_filter = ['created']
    search_fields = ['code']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency_code', 'balance']
    list_filter = ['created', 'updated']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_num', 'account_name', 'bank_id']
    list_filter = ['created', 'updated']
    search_fields = ['account_num', 'account_name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'receiver', 'transaction_type', 'amount']
    list_filter = ['created', 'updated']
    search_fields = ['user', 'transaction_type']


admin.site.register(Bank)

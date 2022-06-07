from django.contrib import admin
from .models import Profile, OTPLog, Bank, Account, Wallet, Currency, Transaction, SecretKey

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'trx_pin']
    list_filter = ['created', 'updated']
    search_fields = ['email', 'full_name']


@admin.register(OTPLog)
class OTPlogAdmin(admin.ModelAdmin):
    list_display = ['otp', 'email']
    list_filter = ['timestamp']
    search_fields = ['otp', 'email']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    list_filter = ['created']
    search_fields = ['code']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['email', 'currency_code', 'balance']
    list_filter = ['created', 'updated']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'account_num', 'account_name', 'bank_name']
    list_filter = ['created', 'updated']
    search_fields = ['account_num', 'account_name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['email', 'receiver_email', 'transaction_type', 'amount', 'currency_code']
    list_filter = ['created', 'updated']
    search_fields = ['user', 'transaction_type']


admin.site.register(Bank)
admin.site.register(SecretKey)

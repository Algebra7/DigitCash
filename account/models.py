from django.db import models
from django.conf import settings
from django.utils import timezone


# Create your models here.

class SecretKey(models.Model):
    key = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20)
    trx_pin = models.CharField(max_length=6, unique=True, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    @property
    def full_name(self):
        if self.middle_name:
            return "{} {} {}".format(self.first_name, self.middle_name, self.last_name)
        else:
            return "{} {}".format(self.first_name, self.last_name)

    def email(self):
        return self.user.email

    def __str__(self):
        return self.full_name


class OTPLog(models.Model):
    otp = models.CharField(max_length=8)
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = 'OTP Log'
        verbose_name_plural = 'OTP Logs'

    def __str__(self):
        return self.otp


class Bank(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    account_num = models.CharField(max_length=15)
    account_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def email(self):
        return self.user.email

    def bank_name(self):
        return self.bank.name
    
    def bank_id(self):
        return self.bank.pk

    def __str__(self):
        return self.account_num


class Currency(models.Model):
    code = models.CharField(max_length=5, unique=True, db_index=True)
    name = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return self.code


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    balance = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def email(self):
        return self.user.email

    def currency_code(self):
        return self.currency.code

    def __str__(self):
        return str(self.balance)


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Deposite', 'Deposite'),
        ('Transfer', 'Transfer'),
        ('Withdrawal', 'Withdrawal')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='receiver', blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def email(self):
        return self.user.email

    def receiver_email(self):
        if self.receiver:
            return self.receiver.email

    def currency_code(self):
        return self.currency.code

    def __str__(self):
        return str(self.amount)

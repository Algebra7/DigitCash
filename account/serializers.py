from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Profile, Bank, Account, Wallet, Currency, Transaction


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Profile
        fields = ('id', 'user', 'first_name', 'middle_name', 'last_name', 'phone', 'email', 'trx_pin', 'profile_pic')

    def create(self, validated_data):
        user = User.objects.create(**validated_data.pop("user"))
        profile = Profile.objects.create(user=user, **validated_data)
        currencies = Currency.objects.all()
        for currency in currencies:
            Wallet.objects.create(user=user, currency=currency)
        return profile


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = '__all__'
        # extra_kwargs = {'name': {'readonly_only': True}}

    
class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('id', 'account_num', 'account_name', 'bank_id')


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = ('id', 'code', 'name')


class WalletSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(many=False)

    class Meta:
        model = Wallet
        fields = ('id', 'currency', 'balance')

    
class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    receiver = UserSerializer(many=False)
    currency = CurrencySerializer(many=False)

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'receiver', 'currency', 'transaction_type', 'amount', 'created')

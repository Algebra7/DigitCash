from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Profile, Bank, Account, Wallet, Currency, Transaction


User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'full_name', 'email', 'trx_pin', 'profile_pic', 'created')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password', 'profile', 'created')
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            profile_data = validated_data.pop("profile")
            user = User.objects.create(**validated_data)
            profile = Profile.objects.create(user=user, **profile_data)
            currencies = Currency.objects.all()
            for currency in currencies:
                Wallet.objects.create(user=user, currency=currency)
            return user

        def update(self, instance, validated_data):
            profile_data = validated_data.pop('profile')
            instance.username = validated_data.get("username", instance.username)
            instance.email = validated_data.get("email", instance.email)
            instance.password = validated_data.get("password", instance.password)
            instance.first_name = validated_data.get("first_name", instance.first_name)
            instance.last_name = validated_data.get("last_name", instance.last_name)
            instance.save()

            profile = instance.profile
            profile.first_name = instance.first_name
            profile.middle_name = profile_data.get("middle_name", profile.middle_name)
            profile.last_name = instance.last_name
            profile.trx_pin = profile_data.get("trx_pin", profile.trx_pin)
            profile.save()


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = '__all__'

    
class AccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    bank = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.all())

    class Meta:
        model = Account
        fields = ('id', 'account_num', 'account_name', 'bank_name', 'email', 'bank', 'user', 'created')
        read_only_fields = ('id', 'bank_name', 'email')


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = ('id', 'code', 'name', 'created')


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    class Meta:
        model = Wallet
        fields = ('id', 'user', 'email', 'currency', 'currency_code', 'balance', 'created')
        read_only_fields = ('id', 'email', 'currency_code')

    
class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'user', 'receiver', 'email', 'receiver_email', 'currency', 'currency_code', 'amount', 'created')
        read_only_fields = ('id', 'email', 'receiver_email', 'currency_code')


    def validate(self, data):
        """
        Make sure reciever is provided for transfer transaction
        """
        if data.get('transaction_type') == "Transfer" and not data.get("receiver"):
            raise serializers.ValidationError("For transfer transaction, receiver must be provided")
        return data

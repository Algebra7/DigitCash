from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models.base import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q

from rest_framework import generics, viewsets, permissions, status, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.authtoken.models import Token

from .models import Profile, OTPLog, Bank, Account, Currency, Wallet, Transaction
from .serializers import (
    UserSerializer, ProfileSerializer, AccountSerializer, BankSerializer,
    CurrencySerializer, WalletSerializer,TransactionSerializer
)
from account.permissions import IsSecretKeyProvided
from account.paginations import CustomResultsSetPagination


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAuthenticated)
    serializer_class = UserSerializer
    pagination_class = CustomResultsSetPagination
    filterset_fields = ['username', 'email', 'first_name', 'last_name']

    queryset = User.objects.all()

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_authenticators(self):
        if self.action == 'create':
            return []
        return super().get_authenticators()

    def create(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        middle_name = request.data.get("last_name")
        trx_pin =  request.data.get("trx_pin")

        _parameters = all([username, email, password, first_name, last_name])
        if not _parameters:
            return Response({"state":"failed", "message":"Some required parameters are not provided"}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "username": request.data.get("username"),
            "password": request.data.get("password"),
            "email": request.data.get("email"),
            "first_name": request.data.get("first_name"),
            "last_name": request.data.get("last_name"),
            "profile": {
                "first_name": request.data.get("first_name"),
                "middle_name": request.data.get("middle_name"),
                "last_name": request.data.get("last_name"),
                "trx_pin": request.data.get("trx_pin"),
            }
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"state":"success", "message":"User created successfully"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        data = {
            "username": request.data.get("username", ""),
            "password": request.data.get("password", ""),
            "email": request.data.get("email", ""),
            "first_name": request.data.get("first_name", ""),
            "last_name": request.data.get("last_name", ""),
            "profile": {
                "first_name": request.data.get("first_name", ""),
                "middle_name": request.data.get("middle_name", ""),
                "last_name": request.data.get("last_name", ""),
                "trx_pin": request.data.get("trx_pin", ""),
            }
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"state":"success", "message":"User updated successfully"}, status=status.HTTP_200_OK)


class CheckUser(APIView):
    authentication_classes = ()
    permission_classes = (IsSecretKeyProvided)

    def get(self, request):
        data = request.GET
        email = data.get('email')
        if not email:
            return Response({"state":"failed", "message": "Missing parameter email address"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            return Response({"state":"success", "message":"user found successfully"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message": "user not found"}, status=status.HTTP_404_NOT_FOUND)


class SendOTP(APIView):
    authentication_classes = ()
    permission_classes = (IsSecretKeyProvided)

    def post(self, request):
        data = request.data
        email = data.get('email')
        if not email:
            return Response({"state":"failed", "message": "Email address must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_secret = os.environ['PYOTP_SECRET']
        # otp_secret = os.environ['PYOTP_SECRET']
        totp = pyotp.TOTP(otp_secret.key, interval=1)
        otp = totp.now()

        #check if an OTP related to the giving email exist, if yes delete it before creating a new one
        try:
            otp_record = OTPLog.objects.get(email=email)
            otp_record.delete()
        except ObjectDoesNotExist:
            pass
            
        otp_log = OTPLog.objects.create(otp=otp, email=email)

        if email:
            subject = "DigiCash: Sign Up Verification Code"
            message = "Here is your verification Code {}".format(otp)
            sender = "ahmadameenmuhammad@gmail.com"
            send_mail(subject, message, sender, [email])

        return Response({"state":"success", "message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOTP(APIView):
    authentication_classes = ()
    permission_classes = (IsSecretKeyProvided)
    
    def post(self, request):
        data = request.data
        email = data.get('email')
        otp = data.get('otp')
        if not (email and otp):
            return Response({"state":"failed", "message": "Email address and OTP must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        res = handle_otp(otp, email=email)
        return Response({"state":res.get("state"), "message":res.get("message")})


class BanksViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAdminUser)
    serializer_class = BankSerializer
    pagination_class = CustomResultsSetPagination
    queryset = Bank.objects.all()

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (IsSecretKeyProvided, permissions.IsAuthenticated)
        return super().get_permissions()


class CurrenciesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAdminUser)
    serializer_class = CurrencySerializer
    pagination_class = CustomResultsSetPagination
    queryset = Currency.objects.all()

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (IsSecretKeyProvided(), permissions.IsAuthenticated())
        return super().get_permissions()


class AccountsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAuthenticated)
    serializer_class = AccountSerializer
    pagination_class = CustomResultsSetPagination
    filterset_fields = ('account_num', 'account_name', 'bank', 'user')
    queryset = Account.objects.all()


class WalletView(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAdminUser)
    serializer_class = WalletSerializer
    pagination_class = CustomResultsSetPagination
    filterset_fields = ('user', 'currency')
    queryset = Wallet.objects.all()

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return (IsSecretKeyProvided(), permissions.IsAuthenticated())
        return super().get_permissions()


class TransactionView(viewsets.ModelViewSet):
    permission_classes = (IsSecretKeyProvided, permissions.IsAdminUser)
    serializer_class = TransactionSerializer
    pagination_class = CustomResultsSetPagination
    filterset_fields = ('transaction_type', 'amount', 'user', 'receiver')
    queryset = Transaction.objects.all()

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve']:
            return (IsSecretKeyProvided(), permissions.IsAuthenticated())
        return super().get_permissions()
    
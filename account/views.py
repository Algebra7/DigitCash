from django.shortcuts import render
from rest_framework import generics, viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.decorators import action, api_view
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models.base import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from .models import Profile, OTPLog, Bank, Account, Currency, Wallet, Transaction
from .serializers import UserSerializer, ProfileSerializer, AccountSerializer, BankSerializer, CurrencySerializer, WalletSerializer, TransactionSerializer
from .utils import handle_otp, is_valid_secret_key
import pyotp
import os

# Create your views here.

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def create(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "user":{
                "username": request.data.get("username"),
                "password": request.data.get("password"),
                "email": request.data.get("email"),
                "first_name": request.data.get("first_name"),
                "last_name": request.data.get("last_name")
            },
            "first_name": request.data.get("first_name"),
            "middle_name": request.data.get("middle_name"),
            "last_name": request.data.get("last_name"),
            "phone": request.data.get("phone"),
            "email": request.data.get("email"),
            "trx_pin": request.data.get("trx_pin"),
        }
        serializer = ProfileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"state":"success", "message":"User created successfully"}, status=status.HTTP_200_OK)

    def list(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        queryset = Profile.objects.get(user=user)
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            User.objects.filter(pk=Profile.objects.get(pk=pk).user.pk).update(first_name=request.data.get("first_name"), last_name=request.data.get("last_name"))
            Profile.objects.filter(pk=pk).update(first_name=request.data.get("first_name"), middle_name=request.data.get("middle_name"), last_name=request.data.get("last_name"))
            return Response({"state":"success", "message":"Basic info updated successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"state":"failed", "message":"Update fails"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckUser(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.GET
        phone = data.get('phone')
        if not phone:
            return Response({"state":"failed", "message": "Missing parameter phone number"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            profile = Profile.objects.get(phone=phone)
            return Response({"state":"success", "message":"user found successfully"}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"state":"failed", "message": "user not found"}, status=status.HTTP_404_NOT_FOUND)


class SendOTP(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        phone = data.get('phone')
        email = data.get('email')
        if not phone and not email:
            return Response({"state":"failed", "message": "Either phone or eamil one must be provided"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if phone and email:
            return Response({"state":"failed", "message": "Both phone and eamil cannot be provided at the same time"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        otp_secret = os.environ['PYOTP_SECRET']
        totp = pyotp.TOTP(otp_secret, interval=1)
        otp = totp.now()

        #check if an OTP related to the giving email exist, if yes delete it before creating a new one
        try:
            if email:
                otp_record = OTPLog.objects.get(email=email)
            if phone:
                otp_record = OTPLog.objects.get(phone=phone)
            otp_record.delete()
        except ObjectDoesNotExist:
            pass
            
        otp_log = OTPLog()
        otp_log.otp = otp
        if phone:
            otp_log.phone = phone
        if email:
            otp_log.email = email
        otp_log.save()

        if email:
            subject = "DigiCash: Sign Up Verification Code"
            message = "Here is your verification Code {}".format(otp)
            sender = "ahmadameenmuhammad@gmail.com"
            send_mail(subject, message, sender, [email])

        if phone:
            """
                Todo: handle phone number OTP sending
            """

        return Response({"state":"success", "message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOTP(APIView):
    authentication_classes = ()
    permission_classes = ()
    
    def post(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        phone = data.get('phone')
        email = data.get('email')
        otp = data.get('otp')
        if not phone and not email:
            return Response({"state":"failed", "message": "Either phone or eamil one must be provided"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if not (phone or email) or not otp:
            return Response({"state":"failed", "message": "One of the following is not provided [phone/eamil, otp]"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if phone and email:
            return Response({"state":"failed", "message": "Both phone and eamil cannot be provided at the same time"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if phone:
            res = handle_otp(otp, phone=phone)
        if email:
            res = handle_otp(otp, email=email)

        return Response({"state":res.get("state"), "message":res.get("message")})


class Login(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        phone = data.get("phone")
        email = data.get("email")
        password = data.get("password")

        if not (phone or email):
            return Response({"state":"failed", "message": "Either phone or eamil one must be provided"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if not (phone or email) or not password:
            return Response({"state":"failed", "message": "One of the following is not provided [phone/eamil, password]"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if phone and email:
            return Response({"state":"failed", "message": "Both phone and eamil cannot be provided at the same time"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            if phone:
                profile = Profile.objects.get(phone=phone)
            if email:
                profile = Profile.objects.get(email=email)
        except ObjectDoesNotExist:
            if phone:
                return Response({"state":"failed", "message":"User with phone number: {} cannot be found".format(phone)}, status=status.HTTP_404_NOT_FOUND)
            if email:
                return Response({"state":"failed", "message":"User with email: {} cannot be found".format(email)}, status=status.HTTP_404_NOT_FOUND)

        username = profile.user.username
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token = Token.objects.create(user=user)
            return Response({"auth_token": token.key, "state": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Wrong Credentials", "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class BanksViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = BankSerializer
    queryset = Bank.objects.all()

    def list(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BankSerializer(self.queryset, many=True)
        return Response(serializer.data)

class CurrenciesViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    def list(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CurrencySerializer(self.queryset, many=True)
        return Response(serializer.data)


class AccountsViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def create(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = token.user
        serializer = AccountSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # serializer.save()
            try:
                bank = Bank.objects.get(pk=data.pop('bank_id'))
                account = Account.objects.create(user=user, bank_id=bank, **data)
                return Response({"state":"success"}, status=status.HTTP_200_OK)
            except:
                return Response({"state":"failed", "message":"Account creation fails"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        token_key = request.headers.get('Token')
        token = Token.objects.get(key=token_key)
        if not token:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = token.user
        try:
            bank = Bank.objects.get(pk=request.data.pop('bank_id'))
            Account.objects.filter(pk=pk).update(user=user, bank_id=bank, **data)
            return Response({"state":"success", "message":"Basic info updated successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"state":"failed", "message":"Update fails"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def list(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        queryset = Account.objects.get(user=user)
        serializer = AccountSerializer(queryset, many=True)
        return Response(serializer.data)


class WalletView(APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = WalletSerializer

    def get(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = token.user
        user_wallets = Wallet.objects.filter(user=user)
        serializer = WalletSerializer(user_wallets)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionView(APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = TransactionSerializer

    def post(self, request):
        """
        transaction_type: 'Deposite',
        currency_code: 'usd'
        amount: '2000'
        if transaction_type == 'Transfer'
            receiver_email: 'email'
        """

        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user

        transaction_type = request.data.get('transaction_type')
        currency_code = request.data.get('currency_code')
        transaction_amount = request.data.get('amount')
        if transaction_type not in ['Deposite', 'Transfer', 'Withdrawal']:
            return Response({'state':'failed', 'message':'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)

        receiver_email = False
        receiver = False
        if transaction_type == 'Transfer':
            receiver_email = request.data.get('receiver_email')
            if not receiver_email:
                return Response({"state":"failed", "message":"Receiver email is required for transfer transaction"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                receiver = User.objects.get(email=receiver_email)
            except ObjectDoesNotExist:
                return Response({"state":"failed", "message":"Receiver cannot be found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            currency = Currency.objects.get(code=currency_code)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"Currency cannot be found using the given currency code"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "user": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            "receiver": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            } if receiver_email else None,
            "currency": currency.pk,
            "transaction_type": transaction_type,
            "amount": transaction_amount
        }
        serializer = WalletSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                # serializer.save()
                if receiver:
                    Transaction.objects.create(user=user, receiver=receiver, currency=currency, **data)
                else:
                    Transaction.objects.create(user=user, receiver=None, currency=currency, transaction_type=data.get('transaction_type'), amount=data.get('amount'))
                return Response({"state":"success"}, status=status.HTTP_200_OK)
            except Exception as ee:
                return Response({"state":"failed", "message":"Wallet creation fails"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    def get(self, request):
        if not is_valid_secret_key(request):
            return Response({'state':'failed', 'message':'Invalid secret key'}, status=status.HTTP_400_BAD_REQUEST)
        token_key = request.headers.get('Token')
        try:
            token = Token.objects.get(key=token_key)
        except ObjectDoesNotExist:
            return Response({"state":"failed", "message":"User token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        user = token.user
        user_transactions = Transaction.objects.filter(Q(user=user) | Q(receiver=user))
        serializer = TransactionSerializer(user_transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

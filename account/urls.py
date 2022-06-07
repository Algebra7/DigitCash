from django.urls import path
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from rest_framework import routers
from account import views
from .views import (
    CheckUser, SendOTP, VerifyOTP, UserViewSet, BanksViewSet, 
    AccountsViewSet, CurrenciesViewSet, WalletView, TransactionView
)

router = routers.DefaultRouter(trailing_slash=False)
router.register('api/users', UserViewSet, basename='users')
router.register('api/banks', BanksViewSet, basename='banks')
router.register('api/accounts', AccountsViewSet, basename='accounts')
router.register('api/currencies', CurrenciesViewSet, basename='currencies')
router.register('api/wallets', WalletView, basename='wallets')
router.register('api/transactions', TransactionView, basename='transactions')

urlpatterns = [
    path('api/check/user', CheckUser.as_view(), name='check_user'),
    path('api/send_otp', SendOTP.as_view(), name="send_otp"),
    path('api/verify_otp', VerifyOTP.as_view(), name='verify_otp')
]

urlpatterns += router.urls

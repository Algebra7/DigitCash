from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Currency, Wallet, Transaction
from django.contrib.auth import get_user_model


User = get_user_model()

@receiver(post_save, sender=Transaction)
def update_wallet(sender, instance, created, **kwargs):
    if created:
        transaction_type = instance.transaction_type
        transaction_amount = instance.amount
        user = instance.user
        user_wallets = Wallet.objects.filter(user=user)
        user_wallet = user_wallets.get(currency=instance.currency)
        if transaction_type == 'Transfer':
            transaction_sender = user
            transaction_receiver = instance.receiver
            sender_wallet = user_wallet
            receiver_wallets = Wallet.objects.filter(user=transaction_receiver)
            receiver_wallet = receiver_wallets.get(currency=instance.currency)
            sender_wallet.balance -= transaction_amount
            receiver_wallet.balance += transaction_amount
            sender_wallet.save()
            receiver_wallet.save()
        elif transaction_type == 'Deposite':
            user_wallet.balance += transaction_amount
            user_wallet.save()
        else:
            user_wallet.balance -= transaction_amount
            user_wallet.save()


@receiver(post_save, sender=Currency)
def handle_currency_addition(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            Wallet.objects.create(user=user, currency=instance)

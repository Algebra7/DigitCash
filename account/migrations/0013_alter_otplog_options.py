# Generated by Django 3.2.9 on 2022-01-02 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_account_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='otplog',
            options={'ordering': ('-timestamp',), 'verbose_name': 'OTPLog', 'verbose_name_plural': 'OTPLogs'},
        ),
    ]

# Generated by Django 3.2.13 on 2022-06-06 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0027_rename_bank_id_account_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='bank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.bank'),
        ),
    ]
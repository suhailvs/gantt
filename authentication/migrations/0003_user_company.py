# Generated by Django 3.1.2 on 2021-03-08 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
        ('authentication', '0002_auto_20210217_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.company'),
        ),
    ]
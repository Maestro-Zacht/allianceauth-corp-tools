# Generated by Django 3.2.5 on 2021-07-13 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corptools', '0049_alter_mailmessage_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='from_name',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='corptools.evename'),
        ),
        migrations.AddField(
            model_name='mailrecipient',
            name='recipient_name',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='corptools.evename'),
        ),
    ]

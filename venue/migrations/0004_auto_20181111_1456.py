# Generated by Django 2.1.2 on 2018-11-11 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0003_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sender',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]

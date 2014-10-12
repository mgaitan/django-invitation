# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InvitationKey',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('key', models.CharField(db_index=True, max_length=40, verbose_name='invitation key')),
                ('date_invited', models.DateTimeField(auto_now_add=True, verbose_name='date invited')),
                ('uses_left', models.IntegerField(default=1)),
                ('duration', models.IntegerField(null=True, blank=True, default=7)),
                ('recipient_email', models.EmailField(max_length=254, blank=True, default='')),
                ('recipient_first_name', models.CharField(max_length=24, blank=True, default='')),
                ('recipient_last_name', models.CharField(max_length=24, blank=True, default='')),
                ('recipient_phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True, default='')),
                ('recipient_other', models.CharField(max_length=255, blank=True, default='')),
                ('from_user', models.ForeignKey(related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
                ('registrant', models.ManyToManyField(null=True, related_name='invitations_used', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InvitationUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('invites_allocated', models.IntegerField(default=3)),
                ('invites_accepted', models.IntegerField(default=0)),
                ('inviter', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

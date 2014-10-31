# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitationkey',
            name='recipient_phone_number',
        ),
        migrations.AddField(
            model_name='invitationkey',
            name='groups',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
    ]

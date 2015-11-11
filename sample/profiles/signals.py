# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User

from djuploader.signals import uploaded_signal
import models
import uuid


def update_profile(upload, line, profile, data):
    try:
        uploaded_signal.update_instance(
            profile, line, data, excludes=['id', 'user'])
        profile.save()
    except Exception, ex:
        upload.add_error(line, ex.message)


def create_profile(upload, line, data):
    user = User.objects.filter(username=data[u'user.ユーザー名']).first()
    if not user:
        user = User.objects.create_user(
            data[u'user.ユーザー名'],
            data[u'user.メールアドレス'],
            uuid.uuid1().hex)

    profile = models.Profile(user=user)
    update_profile(upload, line, profile, data)


@receiver(uploaded_signal, sender=models.Profile)
def uploaded_profile(upload, **kwargs):
    upload.clear()          # Clear Errors
    for line, row, errors in upload.open():
        if row.get('ID', None):
            profile = models.Profile.objects.filter(id=row['ID']).first()
            if profile:
                update_profile(upload, line, profile, row)
                continue

        # IDの個人属性が見つからなかった
        create_profile(upload, line, row)

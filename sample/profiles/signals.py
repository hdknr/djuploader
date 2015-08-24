from django.dispatch import receiver
from django.contrib.auth.models import User

from djuploader.signals import uploaded
import models


@receiver(uploaded, sender=models.Profile)
def uploaded_profile(upload, **kwargs):
    for line, row, errors in upload.open():
        if row.get('ID', None):
            profile = models.Profile.objects.get(id=row['ID'])
            upload.update_instance(profile, row, excludes=['id', 'user'])
            profile.save()
        else:
            # create new Profile
            pass


@receiver(uploaded, sender=User)
def uploaded_user(upload, **kwargs):
    for line, row, errors in upload.open():
        print line, row

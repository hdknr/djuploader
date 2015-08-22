from django.dispatch import receiver
from django.contrib.auth.models import User

from djuploader.signals import uploaded
import models


@receiver(uploaded, sender=models.Profile)
def uploaded_profile(upload, **kwargs):
    print "uploaded profile", type(upload), upload.id


@receiver(uploaded, sender=User)
def uploaded_user(upload, **kwargs):
    print "uploaded user", type(upload), upload.id

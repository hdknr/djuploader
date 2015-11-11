from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
import models
from djuploader.utils import FileResponse
from djuploader.queryset import UploadQuerySet


@staff_member_required
def export_profile(request):
    response = FileResponse(filename="profile.csv")
    models.Profile.uploader.export(
        response, format="csv",
        relates=['user.username', 'user.email', ], encoding="cp932")
    return response


@staff_member_required
def export_user(request):
    response = FileResponse(filename="user.csv")
    UploadQuerySet(User).export(response, format="csv", encoding="cp932")
    return response


@staff_member_required
def export_contact(request):
    return FileResponse(filename="contact.csv").export(models.Contact)

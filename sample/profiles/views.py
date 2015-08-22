from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
import models
from djuploader.csvutils import CsvResponse, CsvQuerySet


@staff_member_required
def export_profile(request):
    response = CsvResponse(filename="profile.csv")
    models.Profile.csv.export(
        response, relates=['user.username', 'user.email', ], encoding="cp932")
    return response


@staff_member_required
def export_user(request):
    response = CsvResponse(filename="user.csv")
    CsvQuerySet(User).export(response, encoding="cp932")
    return response

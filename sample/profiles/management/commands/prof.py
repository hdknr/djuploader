# -*- coding: utf-8 -*-

from pycommand import djcommand
from profiles import models
import os


class Command(djcommand.Command):

    class ExportProfileCsv(djcommand.SubCommand):
        name = "export_profile"
        description = "export Profile"
        args = [
            (('path',), dict(nargs=1, help="export path")),
        ]

        def run(self, params, **options):
            name, ext = os.path.splitext(params.path[0])
            with open(params.path[0], 'w') as out:
                models.Profile.uploader.export(
                    out, format=ext[1:],
                    relates=['user.username', 'user.email'])

    class ExportUser(djcommand.SubCommand):
        name = "export_user"
        description = "export user"
        args = [
            (('path',), dict(nargs=1, help="export path")),
        ]

        def run(self, params, **options):
            from django.contrib.auth.models import User
            from djuploader.queryset import UploadQuerySet
            name, ext = os.path.splitext(params.path[0])
            with open(params.path[0], 'w') as out:
                UploadQuerySet(User).all().export(out, format=ext[1:])

    class RemoveMissingUploadProfile(djcommand.SubCommand):
        name = "remove_missing_upload_profile"
        description = "remove missing upload profile"

        def run(self, params, **options):
            from djuploader.models import remove_missing_files
            remove_missing_files()

    class Update(djcommand.SubCommand):
        name = "update"
        description = "update"
        args = [
            (('id',), dict(nargs=1, help="update")),
        ]

        def run(self, params, **options):
            from djuploader.models import UploadFile
            UploadFile.objects.get(id=params.id[0]).signal()

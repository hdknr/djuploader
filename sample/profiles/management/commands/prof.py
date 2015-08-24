# -*- coding: utf-8 -*-

from pycommand import djcommand
from profiles import models


class Command(djcommand.Command):

    class ExportProfile(djcommand.SubCommand):
        name = "export_profile"
        description = "export Profile"
        args = [
            (('path',), dict(nargs=1, help="export path")),
        ]

        def run(self, params, **options):
            with open(params.path[0], 'w') as out:
                models.Profile.csv.export(
                    out, relates=['user.username', 'user.email'])

    class ExportUser(djcommand.SubCommand):
        name = "export_user"
        description = "export user"
        args = [
            (('path',), dict(nargs=1, help="export path")),
        ]

        def run(self, params, **options):
            from django.contrib.auth.models import User
            from djuploader.csvutils import CsvQuerySet
            with open(params.path[0], 'w') as out:
                CsvQuerySet(User).all().export(out)

    class Update(djcommand.SubCommand):
        name = "update"
        description = "update"
        args = [
            (('id',), dict(nargs=1, help="update")),
        ]

        def run(self, params, **options):
            from djuploader.models import UploadFile
            UploadFile.objects.get(id=params.id[0]).signal()

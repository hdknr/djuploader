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
                models.Profile.csv.export(out)

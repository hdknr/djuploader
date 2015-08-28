from django.contrib import admin
from django.apps import apps
from django.utils.translation import (
    ugettext_lazy as _
)
from django.core.urlresolvers import reverse


class UploadFileAdmin(admin.ModelAdmin):
    actions = ['update_data', ]
    list_additionals = ('model_data', 'mimetype', 'error_list', )

    def update_data(self, request, queryset):
        for instance in queryset:
            instance.signal(delayed=True)

    update_data.short_description = _('Update Data')

    def model_data(self, obj):
        return u'<a href="{0}">{1}</a>'.format(
            reverse("admin:{0}_{1}_changelist".format(
                obj.content_type.app_label, obj.content_type.model)),
            obj.content_type.__unicode__(),)

    model_data.short_description = _("Model Data")
    model_data.allow_tags = True

    def error_list(self, obj):
        return u'<a href="{0}?upload__id__exact={1}">{2}</a>'.format(
            reverse("admin:{0}_{1}_changelist".format(
                obj.uploadfileerror_set.model._meta.app_label,
                obj.uploadfileerror_set.model._meta.model_name)),
            obj.id,
            obj.error_count,)

    error_list.short_description = _("Error List")
    error_list.allow_tags = True


class UploadFileErrorAdmin(admin.ModelAdmin):
    list_filter = ('upload', )
    list_excludes = ('updated_at', )


def register(app_fullname, admins, ignore_models=[]):
    app_label = app_fullname.split('.')[-2:][0]
    for n, model in apps.get_app_config(app_label).models.items():
        if model.__name__ in ignore_models:
            continue
        name = "%sAdmin" % model.__name__
        admin_class = admins.get(name, None)
        if admin_class is None:
            admin_class = type(
                "%sAdmin" % model.__name__,
                (admin.ModelAdmin,), {},
            )

        if admin_class.list_display == ('__str__',):
            excludes = getattr(admin_class, 'list_excludes', ())
            additionals = getattr(admin_class, 'list_additionals', ())
            admin_class.list_display = tuple(
                [f.name for f in model._meta.fields
                 if f.name not in excludes]) + additionals

        admin.site.register(model, admin_class)


register(__name__, globals())

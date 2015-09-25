from django.contrib import admin
from django import template, forms
from django.apps import apps
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import (
    ugettext_lazy as _
)
from django.utils.safestring import mark_safe as _S
import models


def _T(src, **ctx):
    return _S(template.Template(src).render(template.Context(ctx)))


def model_data_link(model, parent=None):
    url = reverse("admin:{0}_{1}_changelist".format(
        model._meta.app_label,
        model._meta.model_name,
    ))
    if parent:
        r = [i.field.name for i in parent._meta.related_objects
             if i.related_model == model]
        if len(r) > 0:
            url += "?{0}={1}".format(r[0], parent.id)
    # finally returns url
    return url


class UploadFileAdminForm(forms.ModelForm):

    signal_event = forms.BooleanField(
        label=_('Signal Uploaded File Event'),
        help_text=_('Signal Uploaded File Event Help'),
        required=False)

    class Meta:
        model = models.UploadFile
        exclude = []

    def modify_parent_help_text(
        self, parent=None, parent_model=None, model=None
    ):
        if parent:
            parent_model = type(parent)
            url = reverse(
                "admin:{0}_{1}_change".format(
                    parent_model._meta.app_label,
                    parent_model._meta.model_name,),
                args=(parent.id,))
            self.fields['parent_object_id'].help_text = _T(
                '''<a href="{{ u }}">{{ i }}</a>''', u=url, i=parent)

        if parent_model:
            url = reverse("admin:{0}_{1}_changelist".format(
                parent_model._meta.app_label,
                parent_model._meta.model_name,
            ))
            self.fields['parent_content_type'].help_text = _T(
                '''<a href="{{ u }}">{{ m.verbose_name }}</a>''',
                u=url, m=parent_model._meta)

        if model:
            link = model_data_link(model, parent)
            self.fields['content_type'].help_text = _T(
                '''<a href="{{ u }}">{{ m.verbose_name }}</a>''',
                u=link, m=model._meta)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', None)
        super(UploadFileAdminForm, self).__init__(*args, **kwargs)

        if self.instance.parent:
            m = self.instance.content_type and \
                self.instance.content_type.model_class()
            self.modify_parent_help_text(self.instance.parent, model=m)
        elif initial:
            ct = ContentType.objects.filter(
                id=initial.get('parent_content_type')).first()
            p = ct and ct.get_all_objects_for_this_type().filter(
                id=initial.get('parent_object_id')).first()

            c = ContentType.objects.filter(
                id=initial.get('content_type')).first()
            self.modify_parent_help_text(
                p, ct and ct.model_class(), c and c.model_class())

    def save(self, *args, **kwargs):
        instance = super(UploadFileAdminForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('signal_event', False):
            instance.signal()
        return instance


class UploadFileAdmin(admin.ModelAdmin):
    actions = ['update_data', ]
    list_additionals = ('parent', 'model_data', 'mimetype', 'error_list', )
    list_excludes = ('created_at', 'parent_content_type', 'parent_object_id',)
    form = UploadFileAdminForm

    def update_data(self, request, queryset):
        for instance in queryset:
            instance.signal()

    update_data.short_description = _('Update Data')

    def model_data(self, obj):
        model = obj.content_type.model_class()
        link = model_data_link(model, obj.parent)
        return _T('''<a href="{{ u }}">{{ m.verbose_name }}</a>''',
                  u=link, m=model._meta)

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

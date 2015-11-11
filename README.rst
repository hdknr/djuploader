====================
djuploader
====================

- Data Uploader


Reference
--------------

- setup.py: `Building and Distributing Packages with Setuptools`__
- MANIFEST.in: `Creating a Source Distribution`__
- Simplified BSD License: `2-clause license ("Simplified BSD License" or "FreeBSD License")`__ (`BSD Template`__)

__ https://pythonhosted.org/setuptools/setuptools.html
__ https://docs.python.org/2.7/distutils/sourcedist.html#source-dist
__ https://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
__ https://en.wikipedia.org/wiki/Template:BSD


Exporting Model
==================

1. `header_row` and `data_row` in a QuerySet:
--------------------------------------------------

.. code-block:: python

    from djuploader.queryset import UploadQuerySet
    from django.utils.translation import ugettext_lazy as _


    class ContactQuerySet(UploadQuerySet):
        def header_row(self, *args, **kwargs):
            ''' CSV Header '''
            return [_('Family Name'), _('First Name'), ]
    
        def data_row(self, instance):
            ''' CSV Data '''
            return [instance.family_name, instance.first_name, ]

2. bind this QuerySet as a Manager: 
--------------------------------------------------

.. code-block:: python

    class Contact(AbstractProfile):
        # ....
        objects = querysets.ContactQuerySet.as_manager()

3. FileResponse.export(model_class):
--------------------------------------------------

.. code-block:: python

    from django.contrib.admin.views.decorators import staff_member_required
    from djuploader.utils import FileResponse
    from . import models

    @staff_member_required
    def export_contact(request):
        return FileResponse(filename="contact.csv").export(models.Contact)


Importing Model
==================

1. Add `uplaoded_signal` to Model
--------------------------------------------------

.. code-block:: python

    from django.dispatch import dispatcher

    class Community(models.Model):
        uploaded_signal = dispatcher.Signal(providing_args=["instance", ])

2. Add receiver
------------------------

.. code-block:: python

    from django.dispatch import receiver
    from . import models

    @receiver(models.Community.uploaded_signal)
    def on_community_uploaded(instance, *args, **kwargs):

        for line, row, errors in instance.open(encoding='cp932'):
            if not errors:
                print "LINE=", lne, " do something with dict", row

3. Create admin link
-----------------------

- templates/admin/communities/community/change_list.html 

.. code-block:: html

    {% extends "admin/change_list.html" %}
    {% load uploadertags %}
    
    {% block object-tools-items %}
      {% get_upload_model opts.model as um %}       {# get UploadFile instance #}
      {{ block.super }}
      <li>
       <a href="{% url 'admin:djuploader_uploadfile_add' %}?upload={{ um.id }}">
            {% trans 'Import' %}{% trans 'Community' %}</a>
      </li>
    {% endblock %}
     

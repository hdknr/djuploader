from django.conf.urls import url
import views

urlpatterns = [
    url(r'^export/profile', views.export_profile,
        name="profiles_export_profile"),
    url(r'^export/user', views.export_user,
        name="profiles_export_user"),
    url(r'^export/contact', views.export_contact,
        name="profiles_export_contact"),
]

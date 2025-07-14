# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import path

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^test_project/', include('test_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path("admin/", admin.site.urls),
]

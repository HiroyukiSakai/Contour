from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'Contour.contour.views.index'),
    url(r'^tracks/(\d+)/$', 'Contour.contour.views.track'),
)

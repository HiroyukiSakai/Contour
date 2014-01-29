from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'Contour.contour.views.main_menu'),
    url(r'^main_menu/$', 'Contour.contour.views.main_menu'),
    url(r'^game/$', 'Contour.contour.views.game'),

    # url(r'^Contour/', include('Contour.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.index', name='index'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^crossdomain\.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'crossdomain.xml', 'mimetype': 'application/xml'}),
    url(r'^humans\.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    url(r'^robots\.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    url(r'^apple-touch-icon-precomposed\.png$', 'django.views.generic.simple.redirect_to', {'url': '/static/apple-touch-icon-precomposed.png'}),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
)

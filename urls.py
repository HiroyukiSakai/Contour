#   Contour  Copyright (C) 2013-2014  Hiroyuki Sakai
#
#   This file is part of Contour.
#
#   Contour is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Contour is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Contour.  If not, see <http://www.gnu.org/licenses/>.

"""The urls module maps URL patterns of requested URLs to Django views.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('Contour.contour.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

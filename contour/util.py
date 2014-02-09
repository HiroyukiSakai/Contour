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

"""A module containing helper functions.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

import re

slugify_strip_re = re.compile(r'[^\w\s-]')
slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".

    :param value: The unsanitized string.
    :type value: string.
    :returns: string -- The sanitized string.

    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(slugify_strip_re.sub('', value).strip().lower())
    return slugify_hyphenate_re.sub('-', value)

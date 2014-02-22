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

"""Forms which describe the asynchronous communication between server and client.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

from django import forms


class FinishEdgeImageForm(forms.Form):
    """Form used for the submission of drawings.

    """
    finish_edge_image = forms.BooleanField(required=True, initial=True)
    image_id = forms.IntegerField(required=True)

class RetryDrawingForm(forms.Form):
    """Form used for to retry drawings.

    """
    retry_drawing = forms.BooleanField(required=True, initial=True)

class FinishDrawingForm(forms.Form):
    """Form used for the submission of drawings.

    """
    finish_drawing = forms.BooleanField(required=True, initial=True)

class DiscardSessionForm(forms.Form):
    """Form used for the discarding of sessions.

    """
    discard_session  = forms.BooleanField(required=True, initial=True)

class SaveSessionForm(forms.Form):
    """Form used for the saving of track sessions (for highscore tracking).

    """
    name = forms.CharField(max_length=255)
    save_session  = forms.BooleanField(required=True, initial=True)

class UploadFileForm(forms.Form):
    """Form used for the upload of files.

    """
    file  = forms.FileField(required=True)
    sigma = forms.FloatField()

class SearchFlickrForm(forms.Form):
    """Form used for the submitting the Flickr search query.

    """
    query = forms.CharField(max_length=255)
    search_flickr  = forms.BooleanField(required=True, initial=True)
    sigma = forms.FloatField()

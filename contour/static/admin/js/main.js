/*
    Contour  Copyright (C) 2013-2014  Hiroyuki Sakai

    This file is part of Contour.

    Contour is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Contour is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Contour.  If not, see <http://www.gnu.org/licenses/>.
*/

if (typeof django != 'undefined' && django.jQuery != 'undefined') {
    (function($) {
        $(function() {
            $('input[name="_editedgeimage"]').click(function(event) {
                event.preventDefault();

                var id;
                var matches = window.location.href.match(/\/image\/(.*)$/);
                if (matches) {
                    id = matches[1].split("/")[0];

                    window.location.href = $(this).attr("data-url-prefix") + id + "/";
                }
            });
        });
    })(django.jQuery);
}

if (typeof $ != 'undefined') {
    $(function() {
        if (jQuery().literallycanvas) {
            // the only LC-specific thing we have to do
            $('.edit-edge-image-form .literally').literallycanvas({
                backgroundColor: 'transparent',
                imageURLPrefix: '/static/admin/vendor/literallycanvas/img',
                keyboardShortcuts: false,
                onInit: function(lc) {
                    var $literally = $('.literally');
                    $('.append-to-literally-toolbar').appendTo($literally.find('.action-buttons'));

                    $('#finish-edge-image-form').submit(function(event) {
                        event.preventDefault();

                        $(this).find('[type="submit"]').html('Saving...');

                        $.ajax({
                            type: 'POST',
                            headers: {
                                Accept: 'application/json'
                            },
                            data: {
                                csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                                finish_edge_image: true,
                                image_id: $('input[name="image_id"]').val(),
                                image:  lc.canvasWithBackground($('.separate-background-image').get(0)).toDataURL().split(',')[1],
                                type: 'base64'
                            },
                            success: function(data) {
                                location.reload();
                            }
                        });
                    });
                }
            });
        }
    });
}
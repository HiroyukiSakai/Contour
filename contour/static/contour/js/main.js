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

$(function() {
    var localStorageKey = 'drawing'

    // you may want to disable scrolling on touch devices
    $(document).bind('touchmove', function(e) {
        if (e.target === document.documentElement) {
            return e.preventDefault();
        }
    });

    $('#discard-modal').modal('show');

    $(window).resize(function() {
        $('#refresh-modal').modal('show') ;
    });

    $("[data-toggle='tooltip']").tooltip();

    $('.slider').slider();

    if (typeof clearCanvas !== 'undefined' && clearCanvas) {
        localStorage.removeItem(localStorageKey);
    }

    $('.view-main-menu #fileinput').on('change', function(evt) {
        var file = evt.target.files[0];
        if (file) {
            $('#upload-btn').css('display', 'block');
        } else {
            $('#fileinput .fileinput-preview').empty();
            $('#upload-btn').hide();
        }
    });

    $('.view-main-menu #play-modal #flickr form').submit(function(event) {
        $inputField = $('.view-main-menu #play-modal #flickr input[name="query"]');
        if (!$inputField.val()) {
            event.preventDefault();
            $inputField.parents('.form-group').addClass('has-error');
        }
    });

    $('.view-game .refresh').click(function(event) {
        event.preventDefault();
        localStorage.removeItem(localStorageKey);
        location.reload();
    });

    $('.view-completed form.form-save').submit(function(event) {
        $inputField = $('.view-completed form.form-save input[name="name"]');
        if (!$inputField.val()) {
            event.preventDefault();
            $inputField.parents('.form-group').addClass('has-error');
        }
    });

    $('.magnific-popup-container').magnificPopup({
        delegate: '.magnific-popup-item',
        type: 'image',
        gallery: {
            enabled: true
        }
    });

    if (jQuery().literallycanvas) {
        // the only LC-specific thing we have to do
        $('.view-game .literally').literallycanvas({
            backgroundColor: '#ffffff',
            imageURLPrefix: '/static/contour/vendor/literallycanvas/img',
            keyboardShortcuts: false,
            toolClasses: [LC.PencilWidget, LC.EraserWidget],
            onInit: function(lc) {
                var titleBarHeight = $('.title-bar').outerHeight();
                var toolbarHeight = $('.literally .toolbar').outerHeight();

                var widthFactor = $(window).width() / imageWidth;
                var factor = ($(window).height() - titleBarHeight - toolbarHeight) / imageHeight;
                if (widthFactor < factor)
                    factor = widthFactor

                var canvasWidth = Math.round(imageWidth * factor);
                var canvasHeight = Math.round(imageHeight * factor);

                var $literally = $('.literally');
                $literally.width(canvasWidth).height(canvasHeight + toolbarHeight);
                $literally.find('canvas').width(canvasWidth).height(canvasHeight).attr('width', canvasWidth).attr('height', canvasHeight);
                $('.append-to-literally-toolbar').appendTo($literally.find('.action-buttons'));

                if (localStorage.getItem(localStorageKey)) {
                    lc.loadSnapshotJSON(localStorage.getItem(localStorageKey));
                }
                lc.on('drawingChange', function() {
                    localStorage.setItem(localStorageKey, lc.getSnapshotJSON());
                });

                $('#finish-drawing-form').submit(function(event) {
                    event.preventDefault();

                    $('#processing-modal').modal('show');

                    $.ajax({
                        type: 'POST',
                        headers: {
                            Accept: 'application/json'
                        },
                        data: {
                            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                            finish_drawing: true,
                            image:  lc.canvasForExport().toDataURL().split(',')[1],
                            type: 'base64'
                        },
                        success: function(data) {
                            localStorage.removeItem(localStorageKey);
                            location.reload();
                        },
                    });
                });
            }
        });
    }
});

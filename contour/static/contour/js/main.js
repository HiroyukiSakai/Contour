$(function() {
    // you may want to disable scrolling on touch devices
    $(document).bind('touchmove', function(e) {
        if (e.target === document.documentElement) {
            return e.preventDefault();
        }
    });

    $(window).resize(function() {
        $('#refresh-modal').modal('show') ;
    });

    // http://davidwalsh.name/fullscreen
    // Find the right method, call on correct element
    function launchFullScreen(element) {
        if(element.requestFullScreen) {
            element.requestFullScreen();
        } else if(element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if(element.webkitRequestFullScreen) {
            element.webkitRequestFullScreen();
        }
    }

    $('#fullscreen-test').click(function() {
        launchFullScreen(document.documentElement); // any individual element
    });

    $('#discard-modal').modal('show');

    $('.view-main-menu #fileinput').on('change', function(evt) {
        var file = evt.target.files[0];
        if (file) {
            $('#upload-btn').show();
        } else {
            $('#upload-btn').hide();
        }
    });

    $('.view-game .refresh').click(function(event) {
        event.preventDefault();
        localStorage.removeItem(localStorageKey);
        location.reload();
    });

    if (jQuery().literallycanvas) {
        // the only LC-specific thing we have to do
        $('.view-game .literally').literallycanvas({
            backgroundColor: '#ffffff',
            imageURLPrefix: '/static/contour/vendor/literallycanvas/img',
            keyboardShortcuts: false,
            toolClasses: [LC.PencilWidget, LC.EraserWidget],
            onInit: function(lc) {
                var titleBarHeight = 32;
                var toolbarHeight = 31;

                var widthFactor = $(window).width() / imageWidth;
                var factor = ($(window).height() - titleBarHeight - toolbarHeight) / imageHeight;
                if (widthFactor < factor)
                    factor = widthFactor

                var canvasWidth = imageWidth * factor;
                var canvasHeight = imageHeight * factor;

                var $literally = $('.view-game .literally');
                $literally.width(canvasWidth).height(canvasHeight + toolbarHeight);
                $literally.find('canvas').width(canvasWidth).height(canvasHeight).attr('width', canvasWidth).attr('height', canvasHeight);
                $('.append-to-literally-toolbar').appendTo($literally.find('.action-buttons'));

                var localStorageKey = 'drawing'
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

$(function() {
    // you may want to disable scrolling on touch devices
    $(document).bind('touchmove', function(e) {
        if (e.target === document.documentElement) {
            return e.preventDefault();
        }
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

    $('.view-main-menu #fileinput').on('change', function(evt) {
        var file = evt.target.files[0];
        if (file) {
            $('#upload-btn').show();
        } else {
            $('#upload-btn').hide();
        }
    });

    if (jQuery().literallycanvas) {
        // the only LC-specific thing we have to do
        $('.view-game .literally').literallycanvas({
            backgroundColor: '#ffffff',
            imageURLPrefix: '/static/contour/vendor/literallycanvas/img',
            keyboardShortcuts: false
        });
    }
});

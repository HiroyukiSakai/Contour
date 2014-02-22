# Contour

Web-based drawing game.

## Known limitations

* The third party component [Literally Canvas](http://literallycanvas.com), which is used for the interactive drawing canvases, is currently not working on the standard browser on Samsung’s Android devices. The best way to play Contour on such devices is to use the Chrome web browser.
* The calculation of the score is inconsistent among different devices (e.g. computers, tablets and smartphones) since the line thickness is absolute whereas the canvas resizes relative to the viewport. This means that the score calculation is based on a thicker line on smaller devices.
* Changing images in existing tracks, for which high scores have been saved, is not recommended since the entries in the high score list are voided by this process.

## Third party technologies

### Client-side

* [HTML5 Boilerplate](http://html5boilerplate.com) v4.3.0
* [Bootstrap](http://getbootstrap.com) v3.0.3
* [Modernizr](http://modernizr.com) v2.6.2
* [Respond.js](https://github.com/scottjehl/Respond) v1.1.0
* [jQuery](http://jquery.com) v2.1.0
* [Underscore.js](http://underscorejs.org) v1.5.2
    * [Literally Canvas](http://literallycanvas.com) v0.3-rc4
* [Magnific Popup](http://dimsemenov.com/plugins/magnific-popup/) v0.9.9
* [Jasny Bootstrap](http://jasny.github.io/bootstrap/) v3.0.1-p7
* [Slider for Bootstrap](http://www.eyecon.ro/bootstrap-slider/) v2.0.0

### Server-side

* [Python](http://www.python.org) v2.7
* [NumPy](http://www.numpy.org) v1.8.0
* [SciPy](http://www.scipy.org) v0.13.1
* [scikit-image](http://www.scikit-image.org) v0.7.1
* [Django](https://www.djangoproject.com) v1.3.7
* [MySQL](http://www.mysql.com)

Contour  Copyright (C) 2013-2014  Hiroyuki Sakai

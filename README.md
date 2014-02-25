# Contour

A web-based drawing game

## Availability

* The game is currently hosted at <http://hiro.pythonanywhere.com/>.
* The source code is available at <https://github.com/HiroyukiSakai/Contour>.
* The source code documentation is available at <http://hiro.pythonanywhere.com/doc/>.
* The author is reachable at <hiroyuki.sakai@student.tuwien.ac.at>.

## Quick install

To install Contour on your server, follow these steps:

**1. Checkout the sources from the repository**

**2. Create a secret.py containing the following information:**
    
    DATABASES
    
"A dictionary containing the settings for all databases to be used with Django" (<https://docs.djangoproject.com/en/1.3/ref/settings/#databases>)
    
    ALLOWED_HOSTS

"A list of strings representing the host/domain names that this Django site can serve." (<https://docs.djangoproject.com/en/1.3/ref/settings/#allowed-hosts>)
    
    SECRET_KEY

"A secret key for this particular Django installation." (<https://docs.djangoproject.com/en/1.3/ref/settings/#secret-key>)
    
Make sure to keep this information secret.

**3. Execute the following commands from the command line:**
    
    python manage.py sql contour
    python manage.py syncdb
    
This makes sure, that the used models are reflected in the database.

**4. Create the following static aliases:**

    /static/admin/ to /usr/local/lib/python2.7/dist-packages/django/contrib/admin/media
    /static/ to Contour/static
    /media/ to Contour/media
    /favicon.ico to Contour/static/contour/favicon.ico
    /apple-touch-icon-precomposed.png to Contour/static/contour/apple-touch-icon-precomposed.png
    /robots.txt to Contour/static/contour/robots.txt
    /humans.txt to Contour/static/contour/humans.txt
    /crossdomain.xml to Contour/static/contour/crossdomain.xml
    /doc/ to Contour/_build/html

Modify the paths as needed.

**5. Execute the following command to copy the static files into the main directory for static files:**
    
    python manage.py collectstatic

Please take a look at the Django documentation for further details: <https://docs.djangoproject.com/en/1.3/>.

**Sphinx documentation**

Use the following command, if you want to create the source code documentation on your server.

    sphinx-build -b html . _build/html/

You need a working sphinx installation for this (<http://sphinx-doc.org>).

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

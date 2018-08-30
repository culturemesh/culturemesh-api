=================
Deploying the API
=================

.. _deploying-api:

We have been hosting the CultureMesh API on Bluehost on the same server as
the main CultureMesh website.  Bluehost uses Apache, so we use ``flup``
and Fast CGI in combination with a custom ``.htaccess`` file to serve the
Flask endpoints.

We specify in ``api.fcgi`` that a Python 3 binary from a dedicated
virtual environment is to be used to run the Flask application.

Here are the docs `on Flup and Fast CGI <http://flask.pocoo.org/docs/1.0/deploying/fastcgi/>`_.

Currently, there is no more action for deployment than
installing the API source on the Bluehost server, creating the
``credentials.py`` file, and letting Apache, ``flup``,
and the Python 3 binary run and serve the API Flask application.

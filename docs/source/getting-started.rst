=====================
Getting Started
=====================

.. _getting-started:

Overview
--------

The CultureMesh API is a Python Flask application.  It has no front-end and
all of its blueprints are API endpoints that return or modify
data from a MySQL database.

The API endpoints and data exchange formats are all implemented according to
`our Swagger API spec <https://codethechange.stanford.edu/>`_. We use
this file as a structured specification format -- we do not use Swagger's
code generation features.  You can visit https://editor.swagger.io/
and copy the Swagger spec file into the editor to see a nice UI for the
API methods and objects.


.. note:: We currently have no way of running the API locally.  We developed using a
  "rehearsal" database and URL endpoint.

  Generating the required infrastructure for running and testing the API locally
  without relying on a live (even if rehearsal) site is a
  great idea for future work.

Contributing
------------

.. note:: Before contributing or writing code, be sure to scan the codebase
   first.  There are certain recurring paradigms that you should follow. For
   example, we include utilities used by more than one blueprint as well
   as SQL statement helpers in `apiutils.py`, and we keep blueprint-specific
   utilities in `util.py` files in their corresponding directories.

.. note:: See section on Deployment for more information on how the API is
   is run.

All changes you make to the directory should go into a separate branch
which you push and submit a pull request for:

1. Install dependencies

.. code-block:: console

  $ cd culturemesh-api
  $ virtualenv .env
  $ pip install -r requirements.txt

2. Create a new branch

.. code-block:: console

  $ git checkout -b my-new-branch

3. Make some awesome commits

4. Push the branch:

.. code-block:: console

  $ git push -u origin my-new-branch

5. Make sure there are no merge conflicts with master
6. Submit a pull request.

  .. warning:: When opening the Pull Request choose the ``alanefl``
    base fork, not ``ericshong``'s

7. Select your reviewers

8. Wait until at least one other person submits a positive review
(or make the requested changes).  Once a positive review is submitted,
you can merge the branch yourself from the GitHub website if your reviewer
has not already done so.

9. Update your local master branch and delete the old one

.. code-block:: console

  $ git checkout master && git pull
  $ git branch -d my-new-branch

.. _secrets:

Secrets
=======

To run the API you need to write an ``api/credentials.py`` file that contains the
following contents:

.. code-block:: python

  sql = {
      'MYSQL_DATABASE_USER': '<user>',
      'MYSQL_DATABASE_PASSWORD': '<password>',
      'MYSQL_DATABASE_DB': '<db>',
      'MYSQL_DATABASE_HOST': '<db host>'
  }

  api = {
      'key': '<api key>'
  }

  host_path = {
      'image_uploads': '<path to image uploads location>'
  }

  secret_key = "<secret key for auth>"

Contact Ken if you are interested in contributing.

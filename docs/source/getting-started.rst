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

Running Locally
---------------

#. Clone the repository

    .. code-block:: console

        $ git clone https://github.com/Code-the-Change/culturemesh-api.git

#. Install python from https://python.org or via your favorite package manager

#. Install ``virtualenv``

    .. code-block:: console

      $ pip3 install virtualenv

#. If you get a note from ``pip`` about ``virtualenv`` not being in your
   ``PATH``, you need to perform this step. ``PATH`` is a variable accessible
   from any bash terminal you run, and it tells bash where to look for the
   commands you enter. It is a list of directories separated by ``:``. You can
   see yours by running ``echo $PATH``. To run ``virtualenv`` commands, you need
   to add python's packages to your ``PATH`` by editing or creating the file
   ``~/.bash_profile`` on MacOS. To that file add the following lines:

    .. code-block:: console

      PATH="<Path from pip message>:$PATH"
      export PATH

#. Then you can install dependencies into a virtual environment

    .. code-block:: console

      $ cd culturemesh-api
      $ virtualenv .env
      $ source .env/bin/activate
      $ pip install -r requirements.txt

#. Create a local testing database. If you have access to the rehearsal database
   on the server, download it through the web interface instead of creating a
   new one.

#. Install ``mysql`` and start the local server. For example, you can use
   homebrew like so:

    .. code-block:: console

        $ brew install mysql

#. The server by default has no root password, does not start automatically, and
   is only accessible over localhost. Start it, login, and create a new
   database.

    .. code-block:: console

        $ mysql.server start
        $ mysql -uroot

   This will get you into a SQL command prompt, where you should run the
   following to create the database:

    .. code-block:: mysql

        mysql> CREATE DATABASE <database_name>

    .. note:: It would be great to simulate a mysql user with limited privileges,
        but unfortunately this is more difficult to get working locally. See the
        following links for information on how to do so.

        https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql

        https://stackoverflow.com/questions/22267114/python-mysqldb-error-1045-access-denied-for-user

        https://stackoverflow.com/questions/6885164/pymysql-cant-connect-to-mysql-on-localhost

        https://stackoverflow.com/questions/6562691/python-3-2-script-to-connect-to-local-mysql-database#6562701

    Now you can load the downloaded file into the database.

    .. code-block:: mysql

        mysql> USE <database_name>;
        mysql> SOURCE <path_to_database_file>;
        mysql> SHOW TABLES;

    After the ``SHOW TABLES;`` command, you should see a bunch of tables listed.

#. Follow the instructions in :ref:`secrets` to create the credentials file.
   Fill in the database information for the root user as follows (if you left
   the root user without a password):

    .. code-block:: python

    sql = {
      'MYSQL_DATABASE_USER': 'root',
      'MYSQL_DATABASE_PASSWORD': None,
      'MYSQL_DATABASE_DB': '<database_name>',
      'MYSQL_DATABASE_HOST': 'localhost'
    }

#. Now, you can run the API locally by executing ``python run.py``. Then,
   send API requests (e.g. via Postman) to http://127.0.0.1:5000 as displayed
   in the output from running the python file.

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

====================
Guide for Developers
====================

Live Debugging
==============

The server can take a while to reflect changes, so if you want to check that the
server has registered code changes and is serving the latest version, you can
use the ``/dev/note`` endpoint. This endpoint serves the contents of
``note.txt``, which you can change to display custom text. If that new text is
displayed at that endpoint, you know the server has updated to reflect your
changes.
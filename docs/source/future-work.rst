===========
Future Work
===========

.. _future-work:

Testing
=======
There is little to no formal testing on the API.  Unit tests and integrations tests
(and a Travis build that runs them) are high priority for future work.

Network Discovery
=================
The API should provide endpoints for recommending Networks to a user.

Security
========
We use token-based authentication for some of the sensitive endpoints. This is
still not good practice -- something like Auth0 should be the end goal before
the API is used to operate on sensitive data.

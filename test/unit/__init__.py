import os
import tempfile
import pytest
from api import api

"""Initialize the testing environment

Creates an app for testing that has the database and note files replaced by
temporary files and that has the configuration flag ``TESTING`` set to ``True``.

"""

# The following function is derived from an example in the Flask documentation
# found at the following URL: http://flask.pocoo.org/docs/1.0/testing/. The
# Flask license statement has been included below as attribution.
#
# Copyright (c) 2010 by the Pallets team.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND DOCUMENTATION, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@pytest.fixture
def client():
    """Creates testing environment and app and handles cleanup

    Creates testing environment, initializes app for that environment, and then
    cleans up the environment. The environment is composed of:

        * Temporary database file
        * Temporary note file

    :return: App for testing
    """

    db_file, api.config['DATABASE'] = tempfile.mkstemp()
    note_file, api.config["NOTE_PATH"] = tempfile.mkstemp()
    api.config['TESTING'] = True
    client = api.test_client()

    #with api.app_context():
        #api.init_db()

    yield client

    os.close(db_file)
    os.unlink(api.config['DATABASE'])

    os.close(note_file)
    os.unlink(api.config["NOTE_PATH"])

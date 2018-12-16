from test.unit import client
from api import credentials
import mock


get_user_count_description = (('user_count', 8, None, 21, 21, 0, False),)


@mock.patch("api.apiutils.execute_get_one",
            return_value=((16,), get_user_count_description))
def test_get_user_count(get_one, client):
    response = client.get("/network/1/user_count",
                          query_string={"key": credentials.api["key"]})

    query = "SELECT count(*) \
             as user_count \
             from network_registration \
             where id_network=%s"
    get_one.assert_called_with(query, ('1',))
    assert response.status_code == 200
    exp = {'user_count': 16}
    assert response.json == exp

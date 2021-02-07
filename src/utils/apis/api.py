import os
from os import path
import logging
import requests
import time
from requests.exceptions import HTTPError
from ..config import Config
from .. import get_json_content, dump_json_content


DEFAULT_TIMEOUT = (15, 15)
logger = logging.getLogger(__name__)
CURRENT_PATH = path.dirname(path.abspath(__file__))


class BaseApi():
    """Base http Api class."""
    def __init__(self, host, path):
        """
        Args:
            host (str): http url host.
            path (str): http url path.

        """
        self.host = host
        self.path = path
        self.url = host + path
        self._sess = None

    @property
    def sess(self):
        if not self._sess:
            self._sess = requests.Session()
        return self._sess

    def get(self, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
        response = self.sess.get(
            self.url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def post(self, headers=None, timeout=DEFAULT_TIMEOUT, *args, **kwargs):
        response = self.sess.post(
            self.url, headers=headers, timeout=timeout, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def patch(self, id, headers=None, timeout=DEFAULT_TIMEOUT, **kwargs):
        url = path.join(self.url, str(id))
        url = self.url + '/' + str(id)
        response = self.sess.patch(
            url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def put(self, id, headers=None, timeout=DEFAULT_TIMEOUT, *args, **kwargs):
        url = path.join(self.url, str(id))
        response = self.sess.put(
            url, headers=headers, timeout=timeout, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def delete(self, id, headers=None, timeout=DEFAULT_TIMEOUT, *args, **kwargs):
        url = path.join(self.url, str(id))
        response = self.sess.delete(
            url, headers=headers, timeout=timeout, *args, **kwargs)
        response.raise_for_status()
        return response.json()


class Login(BaseApi):
    def __init__(self, host, cache_path):
        self.host = host
        self.cache_path = cache_path
        self.cache_file_dir = path.join(cache_path, 'portal.json')
        config_content = Config.instance()
        self.userName = config_content.get('API_USERNAME', 'USERNAME_NEEDED')
        self.password = config_content.get('API_PASSWORD', 'PASSWORD_NEEDED')
        super(Login, self).__init__(host=host, path='token/login')

    def token_time_expire(self, cache_time):
        # 604800 = one week
        if abs(time.time() - cache_time) >= 604800:
            return True

    def _login(self):
        params = {
            'username': self.userName,
            'password': self.password
        }
        token = self.post(data=params)['auth_token']
        data = {
            'referenceTime': time.time(),
            'token': token
        }
        os.makedirs(self.cache_path, exist_ok=True)
        dump_json_content(self.cache_file_dir, data)
        return token

    @property
    def token(self):
        if path.exists(self.cache_file_dir):
            cache_config = get_json_content(self.cache_file_dir)
            if not self.token_time_expire(cache_config.get('referenceTime', 0)):
                return cache_config['token']
        return self._login()


class Api(BaseApi):
    def __init__(self, host, target_path, cache_path='/tmp/smart_comment'):
        self.login = Login(host=host, cache_path=cache_path)
        super(Api, self).__init__(host=host, path=target_path)

    @property
    def headers(self):
        return {'Authorization': 'Token {}'.format(self.login.token)}

    def get(self, params=None):
        """
        Args:
            params: http query.

        """
        try:
            return super(Api, self).get(
                params=params, headers=self.headers)
        except HTTPError as e:
            if e.response.status_code != 401:
                raise
        except Exception as e:
            logger.error('Api.get fail {}'.format(e))

    def post(self, params=None, **kwargs):
        """
        Args:
            params: http query.

        """
        try:
            return super(Api, self).post(
                headers=self.headers, params=params, **kwargs)
        except HTTPError as e:
            if e.response.status_code != 401:
                raise
        except Exception as e:
            logger.error('Api.post fail {}'.format(e))

    def patch(self, id, params=None, json_data=None):
        """
        Args:
            id: primary id.
            params: http query.
            json_data: patch body encoded to 'application/json'.

        """
        try:
            return super(Api, self).patch(
                id=id, headers=self.headers, params=params, json=json_data)
        except HTTPError as e:
            if e.response.status_code != 401:
                raise
        except Exception as e:
            logger.error('Api.patch fail {}'.format(e))

    def put(self, id, params=None, json_data=None):
        """
        Args:
            id: primary id.
            params: http query.
            json_data: post body encoded to 'application/json'.

        """
        try:
            return super(Api, self).put(
                id=id, headers=self.headers, params=params, json=json_data)
        except HTTPError as e:
            if e.response.status_code != 401:
                raise
        except Exception as e:
            logger.error('Api.pus fail {}'.format(e))

    def delete(self, id, params=None, json_data=None):
        """
        Args:
            id: primary id.
            params: http query.
            json_data: post body encoded to 'application/json'.

        """
        try:
            return super(Api, self).delete(
                id=id, headers=self.headers, params=params, json=json_data)
        except HTTPError as e:
            if e.response.status_code != 401:
                raise
        except Exception as e:
            logger.error('Api.delete fail {}'.format(e))

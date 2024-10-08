import requests
from abc import ABC

class BaseClient(ABC):

    def __init__(self, host : str):
        assert host.find('http://')==0 or host.find('https://') == 0, 'Must include "http://" or "https://"'
        assert host[-1] != '/', 'Must not end with "/"'
        self._host = host

    @property
    def url(self):
        return f'{self._host}/'

    async def is_alive(self):
        res = requests.get(self.url)
        return res.status_code == 200
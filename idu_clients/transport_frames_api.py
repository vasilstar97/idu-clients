import requests
import pandas as pd
from typing import Literal
from .base_client import BaseClient

class TransportFramesAPI(BaseClient):
    
    async def get_accessibility_matrix(self, region_id : int, graph_type : Literal['drive', 'intermodal']) -> pd.DataFrame:
        res = requests.get(self.url + f'/api_v1/{region_id}/get_matrix', {
          'graph_type': graph_type
        })
        json = res.json()
        return pd.DataFrame(json['values'], index=json['index'], columns=json['columns'])
 
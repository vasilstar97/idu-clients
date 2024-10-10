import requests
import pandas as pd
import geopandas as gpd
from .base_client import BaseClient

CRS = 4326

class UrbanAPI(BaseClient):

    async def get_country_regions(self, country_id : int) -> pd.DataFrame:
        res = requests.get(self.url + 'api/v1/all_territories', {
            'parent_id':country_id
        })
        return gpd.GeoDataFrame.from_features(res.json()['features'], crs=CRS).set_index('territory_id', drop=True)

    async def get_countries_without_geometry(self) -> pd.DataFrame:
        res = requests.get(self.url + 'api/v1/all_territories_without_geometry')
        return pd.DataFrame(res.json()).set_index('territory_id', drop=True)

    async def get_regions(self):
        countries = await self.get_countries_without_geometry()
        countries_ids = countries.index
        countries_regions = [await self.get_country_regions(country_id) for country_id in countries_ids]
        return pd.concat(countries_regions)
    
    async def get_territory_types(self) -> pd.DataFrame:
        res = requests.get(self.url + 'api/v1/territory_types')
        return pd.DataFrame(res.json()).set_index('territory_type_id', drop=True)
    
    async def get_urban_functions(self, parent_urban_function_id : int | None = None) -> pd.DataFrame:
        res = requests.get(self.url + '/api/v1/urban_functions_by_parent', {
            'parent_id': parent_urban_function_id,
            'get_all_subtree': False
        })
        return pd.DataFrame(res.json()).set_index('urban_function_id', drop=True)
    
    async def get_service_types(self, urban_function_id : int | None = None) -> pd.DataFrame:
        res = requests.get(self.url + '/api/v1/service_types', {
            'urban_function_id' : urban_function_id
        })
        return pd.DataFrame(res.json()).set_index('service_type_id', drop=True)
    
    async def get_indicators(self, parent_indicator_id : int | None = None, territory_id : int | None = None) -> pd.DataFrame:
        res = requests.get(self.url + f'/api/v1/indicators_by_parent', {
            'parent_id' : parent_indicator_id,
            'territory_id': territory_id
        })
        return pd.DataFrame(res.json()).set_index('indicator_id', drop=True)
    
    async def get_measurement_units(self) -> pd.DataFrame:
        res = requests.get(self.url + f'/api/v1/measurement_units')
        return pd.DataFrame(res.json()).set_index('measurement_unit_id', drop=True)

    async def get_territory_capacity(self, territory_id : int, service_type_id : int):
        res = requests.get(self.url + f'/api/v1/territory/{territory_id}/services_capacity', {
            'service_type_id': service_type_id
        })
        return res.json()

    async def get_territories_capacities(self, territories_ids : list[int], service_type_id : int):
        capacities = {self.get_territory_capacity(id, service_type_id) for id in territories_ids}
        df = pd.DataFrame(data=territories_ids, columns=['territory_id'])
        df = df.set_index('territory_id', drop=True)
        df[service_type_id] = [await c for c in capacities]
        return df

    async def get_territory_normatives(self, territory_id : int):
        res = requests.get(self.url + f'/api/v1/territory/{territory_id}/normatives')
        return pd.DataFrame(res.json())

    async def get_region_territories(self, region_id : int) -> dict[int, gpd.GeoDataFrame]:
        res = requests.get(self.url + '/api/v1/all_territories', {
            'parent_id': region_id,
            'get_all_levels': True
        })
        gdf = gpd.GeoDataFrame.from_features(res.json()['features'], crs=4326)
        df = pd.json_normalize(gdf['territory_type']).rename(columns={
            'name':'territory_type_name'
        })
        gdf = pd.DataFrame.join(gdf, df).set_index('territory_id', drop=True)
        return {level:gdf[gdf['level'] == level] for level in set(gdf.level)}

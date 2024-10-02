import requests
import pandas as pd
import geopandas as gpd
from ..client import Client

CRS = 4326

class UrbanAPI(Client):

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

    async def get_region_territories(self, region_id : int) -> dict[int, gpd.GeoDataFrame]:
        res = requests.get(self.url + '/api/v1/all_territories', {
            'parent_id': region_id,
            'get_all_levels': True
        })
        gdf = gpd.GeoDataFrame.from_features(res.json()['features'], crs=4326)
        df = pd.json_normalize(gdf['territory_type']).rename(columns={
            'name':'territory_type_name'
        })
        gdf = pd.DataFrame.join(gdf, df)
        return {level:gdf[gdf['level'] == level] for level in set(gdf.level)}

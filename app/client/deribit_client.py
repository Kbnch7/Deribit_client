import aiohttp
import asyncio
from typing import Optional
from ..config import DERIBIT_API_URL

class DeribitClient:
    def __init__(self, base_url: str = DERIBIT_API_URL):
        self.base_url = base_url

    async def get_index_price(self, index_name: str) -> Optional[float]:
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": index_name}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {}).get("index_price")
                    else:
                        print(f"Error fetching price for {index_name}: {response.status}")
                        return None
            except Exception as e:
                print(f"Exception fetching price for {index_name}: {e}")
                return None

def sync_get_index_price(index_name: str) -> Optional[float]:
    client = DeribitClient()
    return asyncio.run(client.get_index_price(index_name))

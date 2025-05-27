from abc import ABC, abstractmethod

import aiohttp


class RestCountriesClientInterface(ABC):
    @abstractmethod
    async def get_country_by_code(self, code: str):
        pass


class RestCountriesClient(RestCountriesClientInterface):
    async def get_country_by_code(self, code: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://restcountries.com/v3.1/alpha/{code}") as response:
                if response.status != 200:
                    raise ValueError("Failed to fetch data from REST Countries")
                data = await response.json()
                return data[0] if data else None

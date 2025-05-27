from abc import ABC, abstractmethod

import aiohttp


class NationalizeClientInterface(ABC):
    @abstractmethod
    async def get_countries_by_name(self, name: str):
        pass


class NationalizeClient(NationalizeClientInterface):
    async def get_countries_by_name(self, name: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.nationalize.io/?name={name}") as response:
                if response.status != 200:
                    raise ValueError("Failed to fetch data from Nationalize.io")
                return await response.json()

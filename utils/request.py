import aiohttp


async def get_html(url: str):
    """ Zwraca kontent strony/html """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.text()

            await session.close()

    return result

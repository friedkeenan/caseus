import zlib
import aiohttp

from public import public

@public
def flag_url(flag_code, size):
    return f"https://www.transformice.com/images/drapeaux/{size}/{flag_code.upper()}.png"

@public
async def get_translations(language):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.transformice.com/langues/tfm-{language}.gz") as response:
            data = zlib.decompress(await response.read()).decode("utf-8")

            data = data.split("\n-\n")
            data = [line.split("=", 1) for line in data if len(line) != 0]

            return {
                pair[0]: pair[1]

                for pair in data if len(pair) > 1
            }

@public
def shaman_object_id_parts(shaman_object_id):
    if shaman_object_id > 9999:
        return (shaman_object_id - 10_000) // 10_000, (shaman_object_id - 10_000) % 10_000

    if shaman_object_id > 99:
        return shaman_object_id // 100, shaman_object_id % 100

    return shaman_object_id, 0

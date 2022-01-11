import aiohttp
import base64

BASE_URL = "https://api.github.com"


async def request(method, url, **kwargs):
    async with aiohttp.ClientSession() as session:
        r = await session.request(method, BASE_URL + url, **kwargs)
    return r


async def edit_file(repo: str, file_path: str, new_content: bytes, commit_message: str):
    url = f"/repos/{repo}/contents/{file_path}"
    content = base64.b64encode(new_content)
    b64_content = content.decode("ascii")
    r = await request("GET", url)
    await request(
        "PUT", url,
        headers={
            "Authorization": ...  # TODO: Get token from database
        },
        json={
            "message": commit_message,
            "content": b64_content,
            "sha": (await r.json())["sha"]
        }
    )

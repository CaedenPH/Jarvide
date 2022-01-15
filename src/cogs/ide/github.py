import base64

from cryptography import fernet
from decouple import config


class GitHubHTTP:
    def __init__(self, bot):
        self.bot = bot

    def get_auth(self, user_id: int):
        auth = self.bot.jarvide_api_session.get("/github", params={"userID": user_id})
        f = fernet.Fernet(config("ENCRYPTION_KEY"))
        return f.decrypt(bytes(auth))

    async def edit_file(self, user_id: int, repo: str, file_path: str, new_content: bytes, commit_message: str):
        url = f"/repos/{repo}/contents/{file_path}"
        b64_content = base64.b64encode(new_content).decode("ascii")
        r = await self.bot.request("GET", url)
        await self.bot.request(
            "PUT", url,
            headers={
                "Authorization": self.get_auth(user_id)
            },
            json={
                "message": commit_message,
                "content": b64_content,
                "sha": (await r.json())["sha"]
            }
        )

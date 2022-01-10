from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv(".env")
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUzNDczODA0NDAwNDMzNTYyNiIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiZXhwaXJhdGlvbiI6MTY0MTM0MzQwMS4wMzY2NTgsInNhbHQiOiJHNE1sRmZ6NWVWSktRZVpOdEc5UW53In0.6omMEybE1XdoYIXrvMjVicGa4A9ZF2oJYcu7aakh7Ok"
headers = {"Authorization": f"Bearer {token}"}
data = json.dumps(
    {
        "body": token,
    }
)
r = requests.post("http://127.0.0.1:5001/authenticate", data=data)
data = r.content
print(data)

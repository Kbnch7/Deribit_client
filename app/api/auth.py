from fastapi import FastAPI, Response, APIRouter
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()
auth_router = APIRouter()

CASDOOR_ENDPOINT = os.getenv("CASDOOR_ENDPOINT")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FASTAPI_CALLBACK = os.getenv("FASTAPI_CALLBACK")

@auth_router.get("/telegram/callback")
async def callback(code: str):
    token_url = f"{CASDOOR_ENDPOINT}/api/login/oauth/access_token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": FASTAPI_CALLBACK
    }

    response = requests.post(token_url, data=payload)
    res_data = response.json()
    jwt_token = res_data.get("access_token")

    if not jwt_token:
        return {"status": "error", "details": res_data}

    response = RedirectResponse(url="/")

    response.set_cookie(
        key="jwt_token", 
        value=jwt_token, 
        httponly=False, 
        samesite="lax"
    )

    return response
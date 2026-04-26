from casdoor import CasdoorSDK
from fastapi import HTTPException, Cookie
from typing import Optional

SDK = CasdoorSDK(
    endpoint="https://casdoor.your-domain.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    certificate="""-----BEGIN CERTIFICATE-----
    ...ваш сертификат из панели Casdoor...
    -----END CERTIFICATE-----""",
    org_name="your_org_name",
    application_name="your_app_name"
)

async def get_current_user(jwt_token: Optional[str] = Cookie(None)):
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Токен отсутствует")
    
    try:
        user_data = SDK.parse_jwt_token(jwt_token)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка Casdoor: {str(e)}")
import jwt
import requests
from functools import lru_cache
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config.settings import settings

security = HTTPBearer()


@lru_cache()
def get_cognito_jwks():
    url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    return requests.get(url).json()


def decode_token(token: str) -> dict:
    jwks = get_cognito_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=settings.COGNITO_CLIENT_ID,
        issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}",
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "groups": payload.get("cognito:groups", []),
            "role": _resolve_role(payload.get("cognito:groups", [])),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def _resolve_role(groups: list[str]) -> str:
    if "admins" in groups:
        return "admin"
    elif "agents" in groups:
        return "agent"
    return "customer"

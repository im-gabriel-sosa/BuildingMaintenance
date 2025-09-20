import json
import jwt
import requests

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional

from app.core.config import settings

# This dependency will check for a valid bearer token in the request header
# It's a standard FastAPI security scheme
reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


def get_current_user_id(token: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> str:
    """
    Validates the JWT token and returns the user ID (sub).
    """
    try:
        # Get the public keys from Auth0
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token.credentials).key

        # Decode and validate the JWT
        payload = jwt.decode(
            token.credentials,
            signing_key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_api_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
        # The 'sub' claim contains the user ID from Auth0
        return payload.get("sub")
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid audience"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_user_roles(token: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> List[str]:
    """
    Validates the JWT token and returns the list of user roles.
    Roles are stored in the 'permissions' claim in Auth0.
    """
    try:
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token.credentials).key

        payload = jwt.decode(
            token.credentials,
            signing_key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_api_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
        # Auth0's permissions are stored under the 'permissions' claim
        # which acts as the roles for our application
        return payload.get("permissions", [])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or retrieve roles"
        )


def check_homeowner_role(roles: List[str] = Depends(get_current_user_roles)):
    """
    Dependency that checks if the user has the 'homeowner' role.
    """
    if "homeowner" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have homeowner permissions"
        )
    return True


def check_contractor_role(roles: List[str] = Depends(get_current_user_roles)):
    """
    Dependency that checks if the user has the 'contractor' role.
    """
    if "contractor" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have contractor permissions"
        )
    return True


def check_city_role(roles: List[str] = Depends(get_current_user_roles)):
    """
    Dependency that checks if the user has the 'city' role.
    """
    if "city" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have city permissions"
        )
    return True

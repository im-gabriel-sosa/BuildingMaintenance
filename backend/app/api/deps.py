# app/api/deps.py (Debug Version)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from typing import Dict
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_jwks_client():
    try:
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        logger.debug(f"JWKS URL: {jwks_url}")
        return jwt.PyJWKClient(jwks_url)
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch JWKS: {e}"
        )


def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        logger.debug("Starting token validation...")

        # Log the token (first few characters only for security)
        token = credentials.credentials
        logger.debug(f"Token preview: {token[:50]}...")

        # Get JWKS client
        jwks_client = get_jwks_client()

        # Decode token header to inspect
        try:
            unverified_header = jwt.get_unverified_header(token)
            logger.debug(f"Token header: {unverified_header}")
        except Exception as e:
            logger.error(f"Error getting unverified header: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

        # Get signing key
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            logger.debug(f"Signing key obtained: {type(signing_key.key)}")
        except Exception as e:
            logger.error(f"Error getting signing key: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not get signing key")

        # Log settings for debugging
        logger.debug(f"AUTH0_DOMAIN: {settings.AUTH0_DOMAIN}")
        logger.debug(f"AUTH0_API_AUDIENCE: {settings.AUTH0_API_AUDIENCE}")
        logger.debug(f"AUTH0_ALGORITHMS: {settings.AUTH0_ALGORITHMS}")

        expected_issuer = f"https://{settings.AUTH0_DOMAIN}/"
        logger.debug(f"Expected issuer: {expected_issuer}")

        # Decode and validate the token (skip built-in audience verification)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[settings.AUTH0_ALGORITHMS],
            issuer=expected_issuer,
            options={"verify_aud": False}  # We'll verify audience manually below
        )

        logger.debug(f"Token payload: {payload}")

        # Validate audience
        token_audience = payload.get("aud")
        expected_audience = settings.AUTH0_API_AUDIENCE.strip()

        logger.debug(f"Token audience: {token_audience}")
        logger.debug(f"Expected audience: {expected_audience}")

        if isinstance(token_audience, str):
            if token_audience != expected_audience:
                logger.error(f"Audience mismatch: got {token_audience}, expected {expected_audience}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")
        elif isinstance(token_audience, list):
            if expected_audience not in token_audience:
                logger.error(f"Audience not in list: {expected_audience} not in {token_audience}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")
        else:
            logger.error(f"Invalid audience type: {type(token_audience)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Audience claim is missing or invalid")

        logger.debug("Token validation successful!")
        return payload

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidIssuerError as e:
        logger.error(f"Invalid issuer: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer")
    except jwt.InvalidAudienceError as e:
        logger.error(f"Invalid audience: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")
    except jwt.InvalidSignatureError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {e}")


def check_homeowner_role(payload: Dict = Depends(get_token_payload)):
    logger.debug("Checking homeowner role...")

    # Try multiple possible roles claim keys
    possible_roles_claims = [
        f"{settings.AUTH0_API_AUDIENCE}/roles",  # Using API audience as namespace
        f"https://{settings.AUTH0_DOMAIN}/roles",  # Using Auth0 domain as namespace
        "roles"  # Simple roles claim
    ]

    user_roles = []
    roles_claim_used = None

    for roles_claim in possible_roles_claims:
        if roles_claim in payload:
            user_roles = payload.get(roles_claim, [])
            roles_claim_used = roles_claim
            break

    logger.debug(f"Tried roles claim keys: {possible_roles_claims}")
    logger.debug(f"Roles claim used: {roles_claim_used}")
    logger.debug(f"User roles: {user_roles}")

    if "homeowner" not in user_roles:
        logger.error("User does not have homeowner role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required role to access this resource."
        )

    logger.debug("Homeowner role check passed!")
    return payload
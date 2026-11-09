"""Re-export auth_service from `app.core.security`."""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_current_admin_user,
    get_current_teacher_or_admin_user,
    get_current_user,
    hash_password,
    oauth2_scheme,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)

__all__ = [
    "oauth2_scheme",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "rotate_refresh_token",
    "revoke_refresh_token",
    "decode_access_token",
    "get_current_user",
    "get_current_teacher_or_admin_user",
    "get_current_admin_user",
]

from typing import Optional

from provider.provider_modules.spec_provider import spec_from_uri, spec_from_dict
from shared.models.security.user_context import UserContext


def configure_from_uri(ctx: UserContext, assistant_id: str, spec_url: str, base_uri: Optional[str] = None) -> None:
    spec: dict = spec_from_uri(spec_url, base_uri)


def configure_from_spec(ctx: UserContext, assistant_id: str, spec: dict, base_uri: Optional[str] = None) -> None:
    spec: dict = spec_from_dict(spec, base_uri)

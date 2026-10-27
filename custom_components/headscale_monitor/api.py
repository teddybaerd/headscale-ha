"""Minimal read-only client for the Headscale REST API."""
import asyncio
from urllib.parse import urlsplit

import aiohttp


class HeadscaleError(Exception):
    """Server response or connectivity error."""


class HeadscaleAuthError(HeadscaleError):
    """The API key was rejected."""


def normalize_url(url: str) -> str:
    """Accept only HTTPS origin URLs, without credentials or query parameters."""
    parsed = urlsplit(url.strip())
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or
        parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/")):
        raise ValueError("Enter an HTTPS server URL without path or credentials")
    return f"https://{parsed.netloc}".lower()


class HeadscaleClient:
    """Access the node-list endpoint; never issue modifying requests."""

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str):
        self.session = session
        self.url = normalize_url(url)
        self.api_key = api_key

    async def nodes(self) -> dict[str, dict]:
        """Fetch and validate a full snapshot of nodes."""
        try:
            async with asyncio.timeout(15):
                async with self.session.get(
                    f"{self.url}/api/v1/node",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    allow_redirects=False,
                ) as response:
                    if response.status in (401, 403):
                        raise HeadscaleAuthError("API key rejected")
                    if response.status != 200:
                        raise HeadscaleError(f"Unexpected HTTP status {response.status}")
                    data = await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise HeadscaleError("Could not retrieve Headscale nodes") from err
        if not isinstance(data, dict) or not isinstance(data.get("nodes", []), list):
            raise HeadscaleError("Invalid node response")
        nodes = data.get("nodes", [])
        if any(not isinstance(node, dict) or not node.get("id") for node in nodes):
            raise HeadscaleError("Invalid node in response")
        result = {str(node["id"]): node for node in nodes}
        if len(result) != len(nodes):
            raise HeadscaleError("Duplicate node IDs in response")
        return result

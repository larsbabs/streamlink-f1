"""
$description Official Formula 1 live streaming and video on-demand service.
$url f1tv.formula1.com
$type live, vod
$account A Formula 1 TV subscription is required
"""

import logging
import re

from streamlink.plugin import Plugin, pluginargument, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream


log = logging.getLogger(__name__)


@pluginmatcher(
    re.compile(r"https?://(?:www\.)?f1tv\.formula1\.com/"),
)
@pluginargument(
    "email",
    requires=["password"],
    metavar="EMAIL",
    help="The email address used to register with F1 TV.",
)
@pluginargument(
    "password",
    prompt="Enter F1 TV account password",
    sensitive=True,
    metavar="PASSWORD",
    help="An F1 TV account password to use with --f1tv-email.",
)
class F1TV(Plugin):
    """
    Plugin to support F1TV streaming service.
    Supports both live streams and video on demand.
    """

    _api_url = "https://f1tv.formula1.com/api"
    _login_url = "https://api.formula1.com/v2/account/subscriber/authenticate/by-password"
    _token_url = "https://f1tv.formula1.com/api/viewings"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._authed = False
        self._token = None

    def _authenticate(self):
        """
        Authenticate with F1 TV and get access token
        """
        email = self.get_option("email")
        password = self.get_option("password")

        if not email or not password:
            log.error("F1 TV requires authentication. Please provide --f1tv-email and --f1tv-password")
            return False

        log.debug(f"Attempting to login as {email}")

        # First, authenticate to get the token
        auth_data = {
            "Login": email,
            "Password": password
        }

        try:
            auth_resp = self.session.http.post(
                self._login_url,
                json=auth_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                schema=validate.Schema(
                    validate.parse_json(),
                    {
                        validate.optional("data"): {
                            validate.optional("subscriptionToken"): str,
                        },
                        validate.optional("subscriptionToken"): str,
                    },
                ),
            )

            # Try to get token from either location in response
            self._token = auth_resp.get("subscriptionToken") or auth_resp.get("data", {}).get("subscriptionToken")

            if not self._token:
                log.error("Failed to get authentication token from F1 TV")
                return False

            log.info("Successfully authenticated with F1 TV")
            self._authed = True
            return True

        except Exception as err:
            log.error(f"Authentication failed: {err}")
            return False

    def _get_content_id(self):
        """
        Extract content ID from the URL
        """
        # Get the page to find content ID
        try:
            content_data = self.session.http.get(
                self.url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                schema=validate.Schema(
                    validate.parse_html(),
                    validate.union((
                        validate.xml_xpath_string(".//script[contains(text(),'contentId')]/text()"),
                        validate.xml_xpath_string(".//meta[@property='og:url']/@content"),
                    )),
                ),
            )

            if content_data:
                # Try to extract content ID from various sources
                if isinstance(content_data, tuple):
                    script_text, og_url = content_data
                else:
                    script_text = content_data
                    og_url = None

                # Try to find content ID in script
                if script_text:
                    match = re.search(r'"contentId"\s*:\s*"?(\d+)"?', script_text)
                    if match:
                        return match.group(1)
                    match = re.search(r'contentId["\']?\s*:\s*["\']?(\d+)', script_text)
                    if match:
                        return match.group(1)

                # Try to extract from URL
                match = re.search(r'/detail/(\d+)', self.url)
                if match:
                    return match.group(1)

            return None

        except Exception as err:
            log.debug(f"Could not extract content ID: {err}")
            return None

    def _get_stream_url(self, content_id):
        """
        Get the stream URL for the content
        """
        if not self._authed and not self._authenticate():
            return None

        try:
            # Request stream URL from F1 TV API
            stream_data = self.session.http.post(
                self._token_url,
                json={
                    "content_id": content_id,
                },
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                schema=validate.Schema(
                    validate.parse_json(),
                    {
                        validate.optional("tokenised_url"): validate.url(),
                        validate.optional("url"): validate.url(),
                        validate.optional("objects"): [
                            {
                                validate.optional("tokenised_url"): validate.url(),
                                validate.optional("url"): validate.url(),
                            }
                        ],
                    },
                ),
            )

            # Try different response formats
            stream_url = (
                stream_data.get("tokenised_url") or
                stream_data.get("url") or
                (stream_data.get("objects", [{}])[0].get("tokenised_url") if stream_data.get("objects") else None) or
                (stream_data.get("objects", [{}])[0].get("url") if stream_data.get("objects") else None)
            )

            return stream_url

        except Exception as err:
            log.error(f"Failed to get stream URL: {err}")
            return None

    def _get_streams(self):
        """
        Extract streams from F1 TV
        """
        # Try to get content ID from URL
        content_id = self._get_content_id()
        
        if not content_id:
            log.error("Could not find content ID in URL")
            return

        log.debug(f"Found content ID: {content_id}")

        # Get stream URL
        stream_url = self._get_stream_url(content_id)

        if not stream_url:
            log.error("Could not get stream URL")
            return

        log.debug(f"Found stream URL: {stream_url}")

        # Parse HLS stream
        return HLSStream.parse_variant_playlist(self.session, stream_url)


__plugin__ = F1TV

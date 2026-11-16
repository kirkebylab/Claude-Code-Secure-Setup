"""Shared HTTP helper: honest identification, polite rate limits, retries, caching.

Used by verify_citations.py and fetch_fulltext.py. Not meant to be run directly.

Design notes that matter:

- The User-Agent says what this is and does not pretend to be a browser. If a site
  refuses us, that refusal is the answer; we never disguise ourselves to get past it.
- Responses are cached on disk so re-running a job does not hammer anyone's server.
- Retries cover transient failures only (429, 5xx, truncated reads). A 403 is never
  retried, because it is a decision rather than a glitch.
"""

import hashlib
import http.client
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "claude-code-secure-setup/1.0 (academic literature tooling; python-urllib)"
CACHE_DIR = os.environ.get(
    "LIT_CACHE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache"),
)
TIMEOUT = float(os.environ.get("LIT_TIMEOUT", "600"))
RETRY_STATUS = {429, 500, 502, 503, 504}

_last_call = {}


class Refused(Exception):
    """The server declined. Not an error to work around; record it and move on."""

    def __init__(self, url, code, reason=""):
        self.url, self.code, self.reason = url, code, reason
        super().__init__("%s refused: HTTP %s %s" % (urlparse_host(url), code, reason))


def urlparse_host(url):
    return urllib.parse.urlparse(url).netloc or url


def get(url, params=None, binary=False, cache=True, min_interval=0.4,
        accept=None, attempts=4):
    """Fetch a URL. Returns str (or bytes if binary=True). Raises Refused on 4xx."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)

    path = os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest()
                        + (".bin" if binary else ".txt"))
    if cache and os.path.exists(path):
        with open(path, "rb") as fh:
            data = fh.read()
        return data if binary else data.decode("utf-8", "replace")

    host = urlparse_host(url)
    wait = min_interval - (time.time() - _last_call.get(host, 0))
    if wait > 0:
        time.sleep(wait)

    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)

    data = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = response.read()
            break
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_STATUS and attempt < attempts - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise Refused(url, exc.code, exc.reason)
        except (urllib.error.URLError, http.client.IncompleteRead,
                ConnectionError, socket.timeout):
            # Small institutional servers fail transiently; one retry often wins.
            if attempt < attempts - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    _last_call[host] = time.time()

    if cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
    return data if binary else data.decode("utf-8", "replace")


def get_json(url, params=None, **kw):
    return json.loads(get(url, params, **kw))

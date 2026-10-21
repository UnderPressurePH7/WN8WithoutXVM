import json
import logging
import os
import types
import BigWorld
from wg_async import wg_async, AsyncReturn, await_callback, wg_await, delay

__all__ = [
    'logger',
    'fetch_data_with_retry',
    'cancelCallbackSafe',
    'override',
    'restore_overrides',
    'get_wn8_color',
    'get_winrate_color',
    'get_battles_color',
    'get_format_battles',
    'ANON_RATING_TOKEN',
    'ANON_ICON_PATH',
    'ANON_ICON_PANEL_SIZE',
    'get_anonymize_icon_html'
]


def cancelCallbackSafe(cbid):
    if cbid is None:
        return False
    try:
        BigWorld.cancelCallback(cbid)
        return True
    except (AttributeError, ValueError, TypeError):
        return False


logger = logging.getLogger('WN8WithoutXVM')
logger.setLevel(logging.DEBUG if os.path.isfile('.debug_mods') else logging.ERROR)

ANON_RATING_TOKEN = '__BATTLESTATS_ANON__'
ANON_ICON_PATH = 'gui/maps/icons/battlestats/anonymize.png'
ANON_ICON_IMG_PATH = 'img://' + ANON_ICON_PATH
ANON_ICON_PANEL_SIZE = 14


def get_anonymize_icon_html(size=ANON_ICON_PANEL_SIZE, vspace=-3):
    return "<img src='%s' width='%s' height='%s' vspace='%s' />" % (
        ANON_ICON_IMG_PATH, int(size), int(size), int(vspace)
    )


_overrides = []


def override(holder, name, wrapper=None, setter=None):
    if wrapper is None:
        return lambda w, s=None: override(holder, name, w, s)
    target = getattr(holder, name)
    _overrides.append((holder, name, target))
    wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
    if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
        setattr(holder, name, staticmethod(wrapped))
    elif isinstance(target, property):
        prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
        prop_setter = (lambda *a, **kw: setter(target.fset, *a, **kw)) if setter else target.fset
        setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
    else:
        setattr(holder, name, wrapped)


def restore_overrides():
    while _overrides:
        holder, name, original = _overrides.pop()
        try:
            setattr(holder, name, original)
        except Exception:
            pass


def get_wn8_color(wn8):
    if wn8 < 900:
        return "#FE0E00"  # red
    elif wn8 < 1200:
        return "#FE7903"  # orange
    elif wn8 < 1401:
        return "#F8F400"  # yellow
    elif wn8 < 1600:
        return "#A6FF4D"  # light green
    elif wn8 < 2200:
        return "#60FF00"  # green
    elif wn8 < 2800:
        return "#02C9B3"  # turquoise
    elif wn8 < 3300:
        return "#D68CFF"  # light purple
    else:
        return "#D042F3"  # purple


def get_winrate_color(winrate):
    if winrate <= 0:
        return "#FFFFFF"
    if winrate < 46.5:
        return "#FE0E00"
    elif winrate < 49.5:
        return "#FE7903"
    elif winrate < 53.0:
        return "#F8F400"
    elif winrate < 58.5:
        return "#60FF00"
    elif winrate < 64.0:
        return "#02C9B3"
    else:
        return "#D042F3"


def get_battles_color(battles):
    if battles <= 0:
        return "#FFFFFF"
    if battles < 1000:
        return "#FE7903"
    elif battles < 10000:
        return "#F8F400"
    elif battles < 50000:
        return "#60FF00"
    elif battles < 100000:
        return "#02C9B3"
    else:
        return "#D042F3"


def get_format_battles(b):
    if not b:
        return ''
    if b >= 1000000:
        return '%.1fM' % (b / 1000000.0)
    if b >= 1000:
        return '%.1fk' % (b / 1000.0)
    return str(b)


def _internal_fetch(url, headers, timeout, method, postData, callback):
    return BigWorld.fetchURL(
        url,
        callback,
        headers,
        timeout,
        method,
        postData
    )


@wg_async
def fetch_data_with_retry(url, retries=2, delay=5, headers=None, method='GET', postData='', timeout=30.0, as_json=True):
    if headers is None:
        headers = [
            ('Content-Type', 'application/json'),
            ('User-Agent', 'WoT-Stats-Client/1.0')
        ]

    try:
        retries = max(1, int(retries))
    except Exception:
        retries = 1

    lastError = None

    for attempt in range(1, retries + 1):
        try:
            logger.debug('[Fetch] Attempt %s/%s for URL: %s', attempt, retries, url)

            response = yield await_callback(_internal_fetch)(
                url,
                headers,
                timeout,
                method,
                postData
            )

            if not response:
                lastError = "Empty response object"
                logger.debug('[Fetch] Empty response on attempt %s/%s: %s', attempt, retries, url)
                if attempt < retries:
                    yield _async_sleep(delay)
                    continue
                break

            status = getattr(response, 'responseCode', None)
            try:
                status = int(status) if status is not None else None
            except Exception:
                status = None

            if status is not None and not (200 <= status < 300):
                lastError = 'HTTP {}'.format(status)
                logger.debug('[Fetch] HTTP %s on attempt %s/%s: %s', status, attempt, retries, url)
                if attempt < retries:
                    yield _async_sleep(delay)
                    continue
                break

            if hasattr(response, 'body'):
                responseBody = response.body
            elif hasattr(response, 'read'):
                responseBody = response.read()
            else:
                responseBody = str(response)

            if not responseBody:
                lastError = "Empty response body"
                logger.debug('[Fetch] Empty response body on attempt %s/%s: %s', attempt, retries, url)
                if attempt < retries:
                    yield _async_sleep(delay)
                    continue
                break

            try:
                if not as_json:
                    text = responseBody
                    if isinstance(text, bytes):
                        try:
                            text = text.decode('utf-8', 'replace')
                        except Exception:
                            text = str(text)
                    raise AsyncReturn(text)
                data = json.loads(responseBody)
                raise AsyncReturn(data)

            except (ValueError, TypeError) as e:
                lastError = "JSON decode error: {}".format(e)
                logger.debug('[Fetch] JSON decoding error on %s: %s', url, e)
                if attempt < retries:
                    yield _async_sleep(delay)
                    continue

        except AsyncReturn:
            raise

        except Exception as e:
            lastError = str(e)
            logger.debug('[Fetch] Unexpected error on attempt %s/%s for %s: %s', attempt, retries, url, e)
            if attempt < retries:
                yield _async_sleep(delay)

    logger.error('[Fetch] Failed after %s attempts for %s. Last error: %s',
                 retries, url, lastError or 'Unknown')
    raise AsyncReturn(None)


@wg_async
def _async_sleep(seconds):
    yield wg_await(delay(float(seconds)))

"""Serve uploaded media (avatars, pictures, voice notes) when DEBUG is False.

Django's built-in static() helper only works in DEBUG mode, so on Render the
files were never delivered. This view serves them and also supports HTTP Range
requests, which iPhone audio/video players require.
"""
import mimetypes
import os
import re

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotModified, StreamingHttpResponse
from django.utils._os import safe_join
from django.utils.http import http_date

CHUNK = 64 * 1024
_RANGE = re.compile(r"bytes=(\d*)-(\d*)$")


def _iter_file(path, start, length):
    with open(path, "rb") as f:
        f.seek(start)
        left = length
        while left > 0:
            data = f.read(min(CHUNK, left))
            if not data:
                break
            left -= len(data)
            yield data


def serve_media(request, path):
    try:
        full = safe_join(settings.MEDIA_ROOT, path)
    except Exception:
        raise Http404("Invalid path")
    if not os.path.isfile(full):
        raise Http404("File not found")

    size = os.path.getsize(full)
    mtime = os.path.getmtime(full)
    ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"

    headers = {
        "Accept-Ranges": "bytes",
        "Last-Modified": http_date(mtime),
        "Cache-Control": "public, max-age=3600",
    }

    start, end, status = 0, size - 1, 200
    rng = request.headers.get("Range")
    if rng:
        m = _RANGE.match(rng.strip())
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:  # suffix range: last N bytes
                start = max(size - int(m.group(2)), 0)
            end = min(end, size - 1)
            if start > end or start >= size:
                resp = HttpResponse(status=416)
                resp["Content-Range"] = f"bytes */{size}"
                return resp
            status = 206

    length = end - start + 1
    if request.method == "HEAD":
        resp = HttpResponse(status=status)
    else:
        resp = StreamingHttpResponse(_iter_file(full, start, length), status=status)
    resp["Content-Type"] = ctype
    resp["Content-Length"] = str(length)
    for k, v in headers.items():
        resp[k] = v
    if status == 206:
        resp["Content-Range"] = f"bytes {start}-{end}/{size}"
    return resp

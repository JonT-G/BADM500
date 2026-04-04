"""
Video file streaming with HTTP Range support.
This allows clicking the progress bar in the video player to jump to that part of the video,
instead of always starting from the beginning or doing nothing. 

How it works:
1. The browser sends a request with a Range header, e.g.: Range: bytes=5000000-

2. This file reads that header, opens the video file at that byte position, 
   and streams only the requested chunk back to the browser.

3. The response uses HTTP status 206 (Partial Content) instead of 200 (OK),
   and includes a Content-Range header so the browser knows where in the
   file the chunk belongs, e.g.: Content-Range: bytes 5000000-10000000/10000000
"""
import mimetypes
import os
import re

from django.http import FileResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from .models import Video


def _range_response(request, path):
    """
    Builds the correct HTTP response for a video file request.
    If the browser sent a Range header, return only that chunk (HTTP 206 request).
    If not, return the whole file (HTTP 200).
    """
    file_size = os.path.getsize(path)

    # Take the MIME type from the file extension, e.g. "video/mp4"
    # or generic binary type so the browser still receives the file if the MIME type cannot be determined.
    content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    range_header = request.META.get('HTTP_RANGE', '')

    if range_header:
        # Parse the range header. Format is always: bytes=START-END
        # END is optional — if missing, it means "to the end of the file".
        # Example: "bytes=0-" means the whole file starting from byte 0.
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)  # clamp to actual file size
            length = end - start + 1

            def file_iterator():
                """Read the file in small chunks to avoid loading it all into memory."""
                with open(path, 'rb') as f:
                    f.seek(start)           # jump to the to the clicked byte position
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(8192, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk         # yield sends one chunk at a time to the browser

            response = StreamingHttpResponse(file_iterator(), status=206, content_type=content_type)
            response['Content-Length'] = length
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            return response

    # No Range header — serve the full file normally
    response = FileResponse(open(path, 'rb'), content_type=content_type)
    response['Content-Length'] = file_size
    response['Accept-Ranges'] = 'bytes'
    return response


def stream_video(request, pk):
    """
    Entry point called by urls.py for /stream/<pk>/.
    Looks up the video, checks the file exists, then hands off to _range_response.
    """
    video = get_object_or_404(Video, pk=pk)
    path = video.file.path

    if not os.path.exists(path):
        raise Http404('Video file not found on disk.')

    return _range_response(request, path)

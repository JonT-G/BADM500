"""Video file streaming with HTTP Range support.

Allows browsers to seek within video files by supporting partial-content
(HTTP 206) responses.
"""
import mimetypes
import os
import re
from django.http import FileResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from .models import Video

def _range_response(request, path):
    """Serve a file with HTTP Range support for video seeking."""
    size = os.path.getsize(path)
    content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    range_header = request.META.get('HTTP_RANGE', '')

    if range_header:
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else size - 1
            end = min(end, size - 1)
            length = end - start + 1

            def file_iterator():
                with open(path, 'rb') as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(8192, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            resp = StreamingHttpResponse(
                file_iterator(), status=206, content_type=content_type,
            )
            resp['Content-Length'] = length
            resp['Content-Range'] = f'bytes {start}-{end}/{size}'
            resp['Accept-Ranges'] = 'bytes'
            return resp

    resp = FileResponse(open(path, 'rb'), content_type=content_type)
    resp['Content-Length'] = size
    resp['Accept-Ranges'] = 'bytes'
    return resp

def stream_video(request, pk):
    """Serve a video file with HTTP Range support for proper seeking."""
    video = get_object_or_404(Video, pk=pk)
    path = video.file.path
    if not os.path.exists(path):
        raise Http404('Video file not found')
    return _range_response(request, path)

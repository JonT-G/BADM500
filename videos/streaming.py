"""
Video file streaming with HTTP Range support.
Allows user to watch videos without downloading the whole file first.
It sends video in chunks bytes and if you click ahead it will request the amount of bytes needed to play from that point.
"""
import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Video

CONTENT_TYPE = 'video/mp4'  # only MP4 is supported

def _range_response(request, path):
    """
    If the browser sent a Range header, return only that chunk (HTTP 206).
    If not, return the whole file (HTTP 200).
    """
    file_size = os.path.getsize(path)
    range_header = request.META.get('HTTP_RANGE', '')

    f = open(path, 'rb') # open in read and binary mode 

    if range_header:
        # Range header: "bytes=12345-67890" or "bytes=12345-" (till end of file)
        start, _, end = range_header.replace('bytes=', '').partition('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        end = min(end, file_size - 1)   # clamp to end of file if the client request more bytes than the file has left
        length = end - start + 1

        f.seek(start)                   # move file pointer to the start byte
        response = FileResponse(f, content_type=CONTENT_TYPE, status=206)
        response['Content-Length'] = length    
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}' 
    else:
        # No Range header, so just serve the full file
        response = FileResponse(f, content_type=CONTENT_TYPE)
        response['Content-Length'] = file_size

    response['Accept-Ranges'] = 'bytes'  # if you skip ahead in video, browser will request additional bytes
    return response


def stream_video(request, pk):
    """
    Looks up the video, checks the file exists, then gives to _range_response.
    So find video with id=5 in database if found begin _range_response and if not raise error.
    """
    video = get_object_or_404(Video, pk=pk)
    path = video.file.path
    if not os.path.exists(path):
        raise Http404('Video file not found.')
    return _range_response(request, path)

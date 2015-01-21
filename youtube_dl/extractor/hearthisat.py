# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_urllib_request
from ..utils import (
    str_to_int,
    urlencode_postdata,
)


class HearThisAtIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?hearthis\.at/(?P<artist>[^/]+)/(?P<title>[A-Za-z0-9\-]+)/?$'
    _PLAYLIST_URL = 'https://hearthis.at/playlist.php'
    _TEST = {
        'url': 'https://hearthis.at/moofi/dr-kreep',
        'md5': 'd594c573227a89f4256f0b03e68c80cc',
        'info_dict': {
            'id': '150939',
            'ext': 'mp3',
            'title': 'Moofi - Dr. Kreep',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1421564134,
            'description': 'Creepy Patch. Mutable Instruments Braids Vowel + Formant Mode.',
            'upload_date': '20150118',
            'comment_count': int,
            'view_count': int,
            'like_count': int,
            'duration': 71,
            'categories': ['Experimental'],
        }
    }

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        display_id = '{artist:s} - {title:s}'.format(**m.groupdict())

        webpage = self._download_webpage(url, display_id)
        track_id = self._search_regex(
            r'intTrackId\s*=\s*(\d+)', webpage, 'track ID')

        payload = urlencode_postdata({'tracks[]': track_id})
        req = compat_urllib_request.Request(self._PLAYLIST_URL, payload)
        req.add_header('Content-type', 'application/x-www-form-urlencoded')

        track = self._download_json(req, track_id, 'Downloading playlist')[0]
        title = '{artist:s} - {title:s}'.format(**track)

        categories = None
        if track.get('category'):
            categories = [track['category']]

        description = self._og_search_description(webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        meta_span = r'<span[^>]+class="%s".*?</i>([^<]+)</span>'
        view_count = str_to_int(self._search_regex(
            meta_span % 'plays_count', webpage, 'view count', fatal=False))
        like_count = str_to_int(self._search_regex(
            meta_span % 'likes_count', webpage, 'like count', fatal=False))
        comment_count = str_to_int(self._search_regex(
            meta_span % 'comment_count', webpage, 'comment count', fatal=False))
        duration = str_to_int(self._search_regex(
            r'data-length="(\d+)', webpage, 'duration', fatal=False))
        timestamp = str_to_int(self._search_regex(
            r'<span[^>]+class="calctime"[^>]+data-time="(\d+)', webpage, 'timestamp', fatal=False))

        track_url = self._search_regex(
            r'<a[^>]+data-mp3="([^"]+)"', webpage, 'track URL')

        formats = [{
            'format_id': 'mp3',
            'url': track_url,
            'vcodec': 'none',
        }]

        return {
            'id': track_id,
            'display-id': display_id,
            'title': title,
            'formats': formats,
            'thumbnail': thumbnail,
            'description': description,
            'duration': duration,
            'timestamp': timestamp,
            'view_count': view_count,
            'comment_count': comment_count,
            'like_count': like_count,
            'categories': categories,
        }
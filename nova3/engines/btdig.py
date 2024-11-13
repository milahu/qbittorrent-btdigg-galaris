# VERSION: 1.1
#
# LICENSING INFORMATION
# This is free and unencumbered software released into the public domain.
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# For more information, please refer to <https://unlicense.org>

import sys
import os
import urllib.parse
import urllib.request
import re
import math
import time
import gzip
from io import BytesIO
from novaprinter import prettyPrinter
import urllib.parse

debug = bool(os.environ.get("DEBUG_NOVA3_ENGINES_BTDIG"))

class btdig(object):
    url = 'https://www.btdig.com'
    name = 'btdig'
    supported_categories = {'all': '0'}
    def search(self, what, cat='all'): 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
            'Sec-GPC': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers'
        }

        url = f"{self.url}/search?q={what.replace(' ', '+')}&order=0"

        if debug:
            print(f"fetching {url}", file=sys.stderr)

        response = retrieve_url(url)

        if len(response) == 0:
            if debug:
                print("error: empty response", file=sys.stderr)
            return

        if debug:
            response_path = "response.html"
            print(f"writing {response_path}", file=sys.stderr)
            with open(response_path, "w") as f:
                f.write(response)

        results_match = re.search(r'<span style="color:rgb\(100, 100, 100\);padding:2px 10px">(\d+) results found', response)
        if results_match:
            total_results = int(results_match.group(1))
            total_pages = math.ceil(total_results / 10)
        else:
            total_pages = 1 # assuming single page

        self.parse_page(response)

        for page in range(1, total_pages):
            time.sleep(1)  # Sleep for 1 second between requests
            url = f"{self.url}/search?q={what.replace(' ', '+')}&p={page}&order=0"
            response = self.get_response(urllib.request.Request(url, headers=headers))
            self.parse_page(response)

    def get_response(self, req):
        try:
            with urllib.request.urlopen(req) as response:
                if response.info().get('Content-Encoding') == 'gzip':
                    gzip_file = gzip.GzipFile(fileobj=BytesIO(response.read()))
                    return gzip_file.read().decode('utf-8', errors='ignore')
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return ""

    def parse_page(self, html_content):
        result_blocks = re.finditer(r'<div class="one_result".*?(?=<div class="one_result"|$)', html_content, re.DOTALL)
        
        for block in result_blocks:
            result = {}
            block_content = block.group(0)
            
            magnet_match = re.search(r'<a href="(magnet:\?xt=urn:btih:[^"]+)"', block_content)
            name_match = re.search(r'<div class="torrent_name".*?><a.*?>(.*?)</a>', block_content, re.DOTALL)
            size_match = re.search(r'<span class="torrent_size"[^>]*>(.*?)</span>', block_content)
            
            desc_link_match = re.search(r'<div class="torrent_name".*?><a href="([^"]+)"', block_content, re.DOTALL) # could implement retrieving further info on torrent later
            
            if magnet_match and name_match and size_match and desc_link_match:
                result['link'] = magnet_match.group(1)
                result['name'] = re.sub(r'<.*?>', '', name_match.group(1)).strip()
                result['size'] = size_match.group(1).strip().replace('&nbsp;', ' ')
                result['desc_link'] = desc_link_match.group(1)
                result['engine_url'] = self.url
                result['seeds'] = '-1'
                result['leech'] = '-1'
                prettyPrinter(result)



# https://github.com/nklido/qBittorrent_search_engines
# helpers.py

#VERSION: 1.43

# Author:
#  Christophe DUMEZ (chris@qbittorrent.org)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import gzip
import html.entities
import io
import os
import re
import socket
import socks
import tempfile
import urllib.error
import urllib.parse
import urllib.request

# Some sites blocks default python User-agent
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
headers = {'User-Agent': user_agent}
# SOCKS5 Proxy support
if "sock_proxy" in os.environ and len(os.environ["sock_proxy"].strip()) > 0:
    proxy_str = os.environ["sock_proxy"].strip()
    m = re.match(r"^(?:(?P<username>[^:]+):(?P<password>[^@]+)@)?(?P<host>[^:]+):(?P<port>\w+)$",
                 proxy_str)
    if m is not None:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, m.group('host'),
                              int(m.group('port')), True, m.group('username'), m.group('password'))
        socket.socket = socks.socksocket


def htmlentitydecode(s):
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in html.entities.name2codepoint:
            return chr(html.entities.name2codepoint[entity])
        return " "  # Unknown entity: We replace with a space.
    t = re.sub('&(%s);' % '|'.join(html.entities.name2codepoint), entity2char, s)

    # Then convert numerical entities (such as &#233;)
    t = re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), t)

    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(r'&#x(\w+);', lambda x: chr(int(x.group(1), 16)), t)


def retrieve_url(url):
    """ Return the content of the url page as a string """
    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as exc:
        print(f"Connection error: HTTP {exc.status} {exc.reason}")
        return ""
    except urllib.error.URLError as exc:
        print(f"Connection error: {type(exc).__name__} {exc}")
        return ""
    dat = response.read()
    # Check if it is gzipped
    if dat[:2] == b'\x1f\x8b':
        # Data is gzip encoded, decode it
        compressedstream = io.BytesIO(dat)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        extracted_data = gzipper.read()
        dat = extracted_data
    info = response.info()
    charset = 'utf-8'
    try:
        ignore, charset = info['Content-Type'].split('charset=')
    except Exception:
        pass
    dat = dat.decode(charset, 'replace')
    dat = htmlentitydecode(dat)
    # return dat.encode('utf-8', 'replace')
    return dat


def download_file(url, referer=None):
    """ Download file at url and write it to a file, return the path to the file and the url """
    file, path = tempfile.mkstemp()
    file = os.fdopen(file, "wb")
    # Download url
    req = urllib.request.Request(url, headers=headers)
    if referer is not None:
        req.add_header('referer', referer)
    response = urllib.request.urlopen(req)
    dat = response.read()
    # Check if it is gzipped
    if dat[:2] == b'\x1f\x8b':
        # Data is gzip encoded, decode it
        compressedstream = io.BytesIO(dat)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        extracted_data = gzipper.read()
        dat = extracted_data

    # Write it to a file
    file.write(dat)
    file.close()
    # return file path
    return (path + " " + url)

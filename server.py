#!/usr/bin/env python3

# Copyright 2019 Penn Mackintosh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging, json, os, shutil, time, requests, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from wsgiref.handlers import format_date_time
from urllib.parse import urlsplit, urlunsplit


def genurl(base, obj, host=None):
    if isinstance(base, bytes):
        base = base.decode('utf-8')
    parts = list(urlsplit(base))
    parts[0] = 'http'
    if host:
        parts[1] = host
    parts[2] = parts[2].rsplit('/',1)[0] + '/' + obj # Replace the last element of the path with the wanted one
    parts[3] = ''
    parts[4] = ''
    logging.debug('generated url %s', parts)
    return urlunsplit(parts)

s = requests.Session()

class Handler(BaseHTTPRequestHandler):
    def send_headers(self, length):

        logging.debug('sending response length %d', length)

        self.send_response(200)
        self.send_header('Content-Length', length)
        self.send_header('Connection', 'keep-alive')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('X-frame-options', 'SAMEORIGIN')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Server', 'elb')

    def send_resp(self, resp):
        self.send_headers(len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def do_GET(self):
        logging.debug("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        if self.path.rsplit('/',1)[1] == 'filelist.xml':
            logging.info('Serving filelist')
            self.send_resp(self.server.filelist)
        elif self.path[:4] == '/TDS':
            logging.info("Serving data...")
            # Forward the request.
            r = requests.Request('GET', 'http://update.hicloud.com:8180'+self.path, headers={}).prepare()
            r.headers = dict(self.headers) # We want EXACTLY the same headers.
            resp = s.send(r, stream=True)
            logging.debug("request sent!")
            logging.debug(resp.headers)
            self.send_response(resp.status_code)
            for h in resp.headers:
                logging.debug('%s: %s', h, resp.headers[h])
                self.send_header(h, resp.headers[h])
            self.end_headers()
            logging.debug("forwarded headers done")
            shutil.copyfileobj(resp.raw, self.wfile)
            logging.debug("forwarded data!")
        else:
            logging.error('Invalid path for GET %s', self.path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        data = json.loads(post_data)

        if self.path == '/sp_ard_common/v2/UpdateReport.action':
            logging.info("UpdateReport ignored.")
            self.send_response(404)
#            self.server.stop = True
        elif self.path == '/sp_ard_common/v2/Check.action?latest=true':
            logging.info("Check.action called, sending package...")
            try:
                data['rules']
            except KeyError:
                logging.error("data has no rules")
                return

            if data['rules']['PackageType'][:4] != 'full':
                logging.error("PackageType was invalid, should begin 'full' but was '%s'", data['rules']['PackageType'])
                return
            resp = json.dumps({'status':'0', 'components': [{'name':'testpackage','version':'TESTPACKAGE','versionID':'999999999','description':'a test update','createTime':'2050-12-30T23:59:59+0000','url':genurl(self.server.url, '', 'query.hicloud.com').rsplit('/',2)[0]+'/'}]})
            self.send_resp(resp.encode('utf-8'))
        else:
            logging.error("Unknown POST Path: %s", self.path)

def run(server_class=ThreadingHTTPServer, handler_class=Handler, port=80):
    logging.basicConfig(level=logging.DEBUG, datefmt='')
    server_address = ('query.hicloud.com', port)
    try:
        httpd = server_class(server_address, handler_class)
    except PermissionError:
        logging.error("This script must be run as root/admin to access port 80.")
        raise
    except OSError as e:
        if e.errno == 99:
            logging.error("You must enable hotspot and change your hosts file.")
        elif e.errno == 13:
            logging.error("This script must be run as root/admin to access port 80.")
        raise
    httpd.url = sys.argv[1] if len(sys.argv) > 1 else input('Please enter the filelist URL: ')
    if urlsplit(httpd.url)[1] != 'update.hicloud.com:8180':
        logging.error('invalid url %s', urlsplit(httpd.url)[1])
        sys.exit(1)
    if httpd.url.rsplit('/',1)[1] != 'filelist.xml':
        logging.error('invalid url %s', httpd.url.rsplit('/',1)[1])
        sys.exit(1)
    httpd.filelist = s.get(httpd.url).text.encode('utf-8')
    logging.debug(httpd.filelist)
    logging.info('Starting server...\n')
    print(genurl(httpd.url, '', 'query.hicloud.com').rsplit('/',2)[0]+'/')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')

if __name__ == '__main__':
    run()


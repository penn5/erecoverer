#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging, json, os, shutil, time, requests
from wsgiref.handlers import format_date_time

s = requests.Session()

class Handler(BaseHTTPRequestHandler):
    def send_headers(self, length, allow_range=False):

        print(length)

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
        if self.path == '/TDS/data/files/p3/s15/G2918/g1647/v220916/f1//full/filelist.xml':
            logging.info('Serving filelist')
            resp = open(os.path.join('files', 'filelist.xml'), 'rb').read()
            self.send_resp(resp)
        elif self.path[:4] == '/TDS':
            logging.info("redir")
            # Forward the request.
            r = requests.Request('GET', 'http://update.hicloud.com:8180'+self.path, headers={}).prepare()
            r.headers = dict(self.headers) # We want EXACTLY the same headers.
            resp = s.send(r, stream=True)
            logging.info("request sent!")
            logging.info(resp.headers)
            self.send_response(resp.status_code)
            for h in resp.headers:
                logging.debug('%s: %s', h, resp.headers[h])
                self.send_header(h, resp.headers[h])
            self.end_headers()
            logging.info("forwarded headers done")
            shutil.copyfileobj(resp.raw, self.wfile)
            logging.info("forwarded data!")
        else:
            logging.error('Invalid path for GET %s', self.path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        data = json.loads(post_data)

        if self.path == '/sp_ard_common/v2/UpdateReport.action':
            logging.info("UpdateReport")
            self.send_response(404)
#            self.server.stop = True
        elif self.path == '/sp_ard_common/v2/Check.action?latest=true':
            logging.info("Check.action")
            try:
                data['rules']
            except KeyError:
                logging.error("data has no rules")
                return

            if data['rules']['PackageType'][:4] != 'full':
                logging.error("PackageType was invalid, should begin with 'full' but was '%s'", data['rules']['PackageType'][:4])
                return

            resp = json.dumps({'status':'0', 'components': [{'name':'testpackage','version':'TESTPACKAGE','versionID':'999999999','description':'a test update','createTime':'2050-12-30T23:59:59+0000','url':'http://query.hicloud.com/TDS/data/files/p3/s15/G2918/g1647/v220916/f1/'}]})
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
    logging.info('Starting httpd...\n')
    httpd.stop = False
    while not httpd.stop:
        try:
            httpd.handle_request()
            print("command done")
        except KeyboardInterrupt:
            httpd.stop = True
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    run()


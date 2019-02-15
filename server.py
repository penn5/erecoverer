#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging, json, os, shutil

class Handler(BaseHTTPRequestHandler):
    def send_headers(self, length):
        self.send_response(200)

        self.send_header('Content-Length', length)
        self.send_header('Connection', 'keep-alive')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('X-frame-options', 'SAMEORIGIN')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Server', 'elb')
        self.end_headers()

    def send_resp(self, resp):
        self.send_headers(len(resp))
        self.wfile.write(resp)

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        if self.path == '/dload//full/filelist.xml':
            logging.info('Serving filelist')
            resp = open('filelist.xml', 'rb').read()
            self.send_resp(resp)
        elif self.path[:12] == '/dload/full/':
            logging.info('Serving package %s', self.path[12:])
            self.send_headers(os.path.getsize(os.path.join('files', self.path[12:]))) #Get file size and send
            shutil.copyfileobj(open(os.path.join('files', self.path[12:]), 'rb')) #Copy the entire file
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

            resp = json.dumps({'status':'0', 'components': [{'name':'testpackage','version':'TESTPACKAGE','versionID':'999999999','description':'a test update','createTime':'2050-12-30T23:59:59+0000','url':'http://query.hicloud.com/dload/'}]})
            self.send_resp(resp.encode('utf-8'))
        else:
            logging.error("Unknown POST Path: %s", self.path)

def run(server_class=HTTPServer, handler_class=Handler, port=80):
    logging.basicConfig(level=logging.INFO, datefmt='')
    server_address = ('query.hicloud.com', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    run()


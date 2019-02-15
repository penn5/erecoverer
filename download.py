#!/usr/bin/env python3

import requests, os, shutil
from lxml import etree
from urllib.parse import urlsplit, urlunsplit

def genurl(base, obj):
    parts = list(urlsplit(base))
    parts[0] = 'http'
    parts[2] = parts[2].rsplit('/',1)[0] + '/' + obj # Replace the last element of the path with the wanted one
    parts[3] = ''
    parts[4] = ''
    return urlunsplit(parts)

def download(url, out):
    with requests.get(url, stream=True) as r:
        with open(os.path.join('files', out), 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def main():
    url = input('Please enter changelog or filelist URL: ')

    tree = etree.parse(genurl(url, 'filelist.xml'))
    packages = tree.xpath('/root/vendorInfo')

    for package in packages:
        path = package.get('package')
        if package.get('subpath'):
            path = package.get('subpath')+'/'+path
            os.makedirs(os.path.join('files', package.get('subpath')), exist_ok=True)
        print(path)
        print(genurl(url, path))
        download(genurl(url, path), path)
#    print(etree.tostring(tree))

if __name__ == '__main__':
    main()

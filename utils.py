import os
import re
import urllib
import time

DOCUMENT_ROOT = ''


NCPU = 1


CONTENT_TYPES = {
    None: 'text/plain',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash'
}


def get_ncpu():
    global NCPU
    return NCPU


def set_ncpu(count):
    global NCPU
    NCPU = count


def set_document_root(root_dir):
    global DOCUMENT_ROOT
    if os.path.exists(root_dir):
        if os.path.isdir(root_dir):
            DOCUMENT_ROOT = root_dir
        else:
            raise OSError
        print DOCUMENT_ROOT
    else:
        raise OSError


def recieve_data(conn):
    data = ""
    new_data = True
    while b"\r\n" not in data and new_data:
        new_data = conn.recv(1024)
        if new_data:
            data += new_data
        else:
            break
    return data


def request_parser(request):
    udata = request.decode('utf8')
    pattern = '(GET|HEAD|POST)\s(/.+)\sHTTP/([.0-9]+)'
    result = re.findall(pattern, udata)

    if result.__len__() != 1:
        return None, None, None
    method = result[0][0]
    path = result[0][1]
    version = result[0][2]
    print method
    print path
    path = urllib.unquote(path)
    return method, path, version


def find_file(file_path):
    full_path = DOCUMENT_ROOT + file_path
    print full_path
    # type_res = ''

    if len(re.findall(r'\.\w+$', full_path)) == 0:
        full_path += '/index.html'

    try:
        if '..' in full_path:
            raise IOError
        # type_res = urllib.urlopen(full_path).info().type
        my_file = open(full_path, 'r')
        my_string = my_file.read()
        my_file.close()
        status = '200 OK'
    except IOError:
        status = '403 forbidden'
        my_string = status
    return {'status': status, 'file': my_string}


def make_40x_response_header(response):
    header = 'HTTP/1.1 {0}\r\nServer: {1}\r\n'.format(response, "AS Server")
    return header


def determinate_content_type(path):
    pattern = r'\.([\w]{1,5})$'
    type_ = re.search(pattern, path)
    if type_:
        try:
            return CONTENT_TYPES[type_.group(0)]
        except KeyError:
            return CONTENT_TYPES[None]
    else:
        return CONTENT_TYPES['.html']


def get_date():
    timestamp = time.time()
    return time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime(timestamp))

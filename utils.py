import os
import urllib
import time


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
    request = urllib.unquote(request)

    strings_of_req = request.split('\r')
    request = strings_of_req[0].split(' ')
    method = request[0]

    if method != 'GET' and method != 'HEAD':
        return None, None, None

    path = ' '.join([item for item in request[1:len(request) - 1]])
    new_path = path.split('/')
    query_string = new_path[len(new_path)-1].split('?')
    if len(query_string) > 1:
        index_q = path.rindex(query_string[1])
        path = path[:index_q - 1]
    index_v = request[len(request) - 1].find('/')
    if index_v != -1:
        version = request[len(request) - 1][index_v + 1:]

    print "***************************"
    print 'Method: ' + method
    print 'Path: ' + path
    print 'Version: ' + version

    return method, path, version


def find_file(path):
    type_res = 'text/html'

    try:
        path = check_path(path)
        elements = path.split("/")
        if ".." in elements:
            raise IOError
        type_res = urllib.urlopen(path).info().type
        my_file = open(path, 'r')
        my_string = my_file.read()
        my_file.close()
        status = '200 OK'
    except IOError:
        status = '404 not found'
        my_string = status
    except OSError:
        status = '403 forbidden'
        my_string = status
    return {'status': status, 'file': my_string, 'type_res': type_res}


def make_40x_response_header(response):
    header = 'HTTP/1.1 {0}\r\nServer: {1}\r\n'.format(response, "AS Server")
    return header


def get_date():
    timestamp = time.time()
    return time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime(timestamp))


def check_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            path += '/index.html'
            if not os.path.isfile(path):
                raise OSError
        else:
            return path
    else:
        raise IOError
    return path

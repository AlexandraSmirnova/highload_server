import os
import re
import urllib

DOCUMENT_ROOT = ''


def set_document_root(root_dir):
    """

    :param root_dir:
    """
    global DOCUMENT_ROOT
    if os.path.exists(root_dir):
        if os.path.isdir(root_dir):
            DOCUMENT_ROOT = root_dir
        else:
            raise OSError
        print DOCUMENT_ROOT
    else:
        raise OSError


def request_parser(request):
    udata = request.decode('utf8')
    pattern = '(GET|HEAD)\s(/.+)\sHTTP'
    result = re.findall(pattern, udata)

    if result.__len__() != 1:
        return None, None
    method = result[0][0]
    path = result[0][1]
    print method
    print path
    path = urllib.unquote(path)
    return method, path


def find_file(file_path):
    if file_path is None:
        file_path = '/'
    full_path = DOCUMENT_ROOT + file_path
    print full_path
    type_res = ''

    if len(re.findall(r'\.\w+$', full_path)) == 0:
        full_path += '/index.html'

    try:
        if '..' in full_path:
            raise IOError
        type_res = urllib.urlopen(full_path).info().type
        my_file = open(full_path, 'r')
        my_string = my_file.read()
        my_file.close()
        status = '200 OK'
    except IOError:
        my_string = "404 - Sorry we can't find your file"
        status = '404 NOT FOUND'
    return {'status': status, 'file': my_string, 'type_res': type_res}

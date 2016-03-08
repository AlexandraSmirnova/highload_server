import sys
import asyncore
import socket
from utils import *


class Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(1024)
        if data:
            method, path, version = request_parser(data)
            response = find_file(path)
            length = response['file'].__len__()
            print length

            #http_v = 'HTTP/{0} {1}'.format(version, response['status'])
            #length_data = 'Content-Length: {}\r\n'.format(length)
            #content_type = 'Content-Type: {} \r'.format(response['type_res'])

            self.send('HTTP/{0} {1}\r\n'.format(version, response['status']))
            self.send('Content-Length: {}\r\n'.format(length))
            self.send('Content-Type: ' + response['type_res'] + ' \r\n')
            #self.send('\n'.join([http_v, content_type]))
            self.send('\n')
            self.send(response['file'])
            self.close()


class Server(asyncore.dispatcher):
    def __init__(self, host=None, port=0xB00B):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = Handler(sock)

    def handle_error(self):
        print 'Server error: %s' % sys.exc_value
        sys.exit(1)

    def handle_expt(self):
        print 'client dropped connection'
        self.close()

    def close(self):
        asyncore.dispatcher.close(self)


def main():
    try:
        _r_flag = False
        _c_flag = False
        for param in sys.argv:
            if _r_flag:
                set_document_root(param)
            if param == '-r':
                _r_flag = True
            if param == '-c':
                _c_flag = True

        print _c_flag
        print 'For server stopping press Ctrl^C '
        server = Server('127.0.0.1', 8000)
        asyncore.loop(0.1, True)
    except KeyboardInterrupt:
        print '\nBye :-*'
        sys.exit(0)


if __name__ == '__main__':
    main()

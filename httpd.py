import sys
import asyncore
import socket
import re
import urllib

DOCUMENT_ROOT = sys.argv[2]


class Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            udata = data.decode('utf8')
            result = re.findall(r'GET\s(/.+)\sHTTP', udata)
            result = urllib.unquote(str(result))
            response = self.find_file(result)

            self.send('HTTP/1.0 ' + response['status'] + '\n')
            self.send('Content-Type: ' + response['type_res'] + ' \n')
            self.send('\n')
            self.send(response['file'])
            self.close()

    def find_file(self, file_path):
        full_path = DOCUMENT_ROOT + file_path[3: len(file_path) - 2]
        type_res = ''

        if len(re.findall(r'\.\w+$', full_path)) == 0:
            full_path += '/index.html'

        try:
            type_res = urllib.urlopen(full_path).info().type
            my_file = open(full_path, 'r')
            my_string = my_file.read()
            my_file.close()
            status = '200 OK'
        except IOError:
            my_string = "404 - Sorry we can't find your file"
            status = '404 NOT FOUND'
        return {'status': status, 'file': my_string, 'type_res': type_res}


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
        print 'For server stopping press Ctrl^C '
        server = Server('127.0.0.1', 8080)
        asyncore.loop(0.1, True)
    except KeyboardInterrupt:
        print '\nBye :-*'
        sys.exit(0)


if __name__ == '__main__':
    main()

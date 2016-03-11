import sys
import asyncore
import socket
import threading
from utils import *

from multiprocessing import freeze_support, Process


class Handler(asyncore.dispatcher_with_send):
    def handle_read(self):

        data = recieve_data(self)
        method, path, version = request_parser(data)

        if not method or not path or not version or method == 'POST':
            print 'none'
            self.send(make_40x_response_header("405 Bad Gateway"))
        else:
            response = find_file(path)
            if response['status'] != '200 OK':
                self.send(make_40x_response_header(response['status']))
            length = response['file'].__len__()
            type_res = determinate_content_type(path)
            print type_res

            header = ''
            header += 'HTTP/{0} {1}\r\n'.format(version, response['status'])
            header += 'Content-Length: {}\r\n'.format(length)
            header += 'Date: {}\r\n'.format(get_date())
            header += 'Server: {}\r\n'.format("AS Server")
            header += 'Content-Type: {}\r\n'.format(type_res)

            print header
            self.send(header)
            self.send('\r\n')

            if method == 'GET':
                self.sendall(response['file'])
        self.close()


class Server(asyncore.dispatcher):
    def __init__(self, host=None, port=0xB00B):
        print("Server init")
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)

    def handle_accept(self):
        # print __name__
        if hasattr( os, 'getppid' ):  # only available on Unix
            print( '{0}:\tPID={1} PPID={2}'.format("Process", os.getpid(), os.getppid() ) )
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


class AsyncEventLoop(threading.Thread):
    def run(self):
        asyncore.loop()


if __name__ == '__main__':
    try:
        _r_flag = False
        _c_flag = False
        for param in sys.argv:
            if _r_flag:
                set_document_root(param)
                _r_flag = False
            elif _c_flag:
                try:
                    set_ncpu(int(param))
                except Exception as e:
                    print "-c parameter should be int"
                    raise Exception
                _c_flag = False
            elif param == '-r':
                _r_flag = True
            elif param == '-c':
                _c_flag = True

        print 'Server started.. '
        freeze_support()
        server = Server('127.0.0.1', 8000)
        process_list = []
        for index in range(0, get_ncpu()):
            print index
            process_list.append(Process(target=asyncore.loop, args=(0.1, True)))
            print process_list[index]
        for index in range(0, get_ncpu()):
            process_list[index].start()
        for index in range(0, get_ncpu()):
            process_list[index].join()

            # asyncore.loop(0.1, True)
            # evLoop = AsyncEventLoop()
            # evLoop.start()
    except KeyboardInterrupt:
        print '\nBye :-*'
        sys.exit(0)

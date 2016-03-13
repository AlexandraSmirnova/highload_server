import sys
import asyncore
import socket
from utils import *

from multiprocessing import freeze_support, Process


# This class for storing information about ncpu
class Info(object):
    def __init__(self, ncpu=1):
        self.ncpu = ncpu

    def get_ncpu(self):
        return self.ncpu

    def set_ncpu(self, count):
        self.ncpu = count


class Handler(asyncore.dispatcher_with_send):
    def __init__(self, sock, base_dir=''):
        self.base_dir = base_dir
        asyncore.dispatcher_with_send.__init__(self, sock)

    def handle_read(self):
        data = recieve_data(self)
        method, path, version = request_parser(data)

        if not method or not path or not version:
            self.send(make_40x_response_header("405 Bad Gateway"))
        else:
            response = find_file(self.base_dir + path)
            if response['status'] != '200 OK':
                self.send(make_40x_response_header(response['status']))
            else:
                length = len(response['file'])

                header = ''
                header += 'HTTP/{0} {1}\r\n'.format(version, response['status'])
                header += 'Content-Length: {}\r\n'.format(length)
                header += 'Date: {}\r\n'.format(get_date())
                header += 'Server: {}\r\n'.format("AS Server")
                header += 'Content-Type: {}\r\n'.format(response['type_res'])

                print header
                self.send(header)
                self.send('\r\n')

                if method == 'GET':
                    self.sendall(response['file'])
        self.close()


class Server(asyncore.dispatcher):
    def __init__(self, host=None, port=0xB00B, base_dir=''):
        asyncore.dispatcher.__init__(self)
        try:
            self.check_document_root(base_dir)
            self.base_dir = base_dir
        except OSError:
            print 'Directory is not correct'
            exit()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)

    def handle_accept(self):
        if hasattr(os, 'getppid'):  # only available on Unix
            print('{0}:\tPID={1} PPID={2}'.format("Process", os.getpid(), os.getppid()))
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = Handler(sock, self.base_dir)

    def handle_error(self):
        print 'Server error: %s' % sys.exc_value
        sys.exit(1)

    def handle_expt(self):
        print 'client dropped connection'
        self.close()

    def close(self):
        asyncore.dispatcher.close(self)

    @staticmethod
    def check_document_root(base_dir):
        if os.path.exists(base_dir):
            if os.path.isdir(base_dir):
                return True
            else:
                raise OSError
        else:
            raise OSError


if __name__ == '__main__':
    info = Info()
    _r_flag = False
    _c_flag = False
    root_dir = ''
    try:
        for param in sys.argv:
            if _r_flag:
                root_dir = param
                _r_flag = False
            elif _c_flag:
                try:
                    info.set_ncpu(int(param))
                except Exception as e:
                    print "-c parameter should be int"
                    raise Exception
                _c_flag = False
            elif param == '-r':
                _r_flag = True
            elif param == '-c':
                _c_flag = True

        freeze_support()
        server = Server('127.0.0.1', 8000, root_dir)
        # creating processes
        process_list = []
        for index in range(0, info.get_ncpu()):
            process_list.append(Process(target=asyncore.loop, args=(0.1, True)))
        for index in range(0, info.get_ncpu()):
            process_list[index].start()
        for index in range(0, info.get_ncpu()):
            process_list[index].join()

    except KeyboardInterrupt:
        print '\nBye :-*'
        sys.exit(0)

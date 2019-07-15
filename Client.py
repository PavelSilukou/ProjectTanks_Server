import socket
import threading
import Queue

server_ip = "localhost"
server_port = 10000

recv_queue = Queue.Queue()
send_queue = Queue.Queue()

class ClientControllerThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.off_event = threading.Event()
        
    def run(self):
        while not self.off_event.isSet():
            self.enterCommand()

    def enterCommand(self):
        command = raw_input(">> ")

        if command == "RUN":
            self.run_client()
        elif command == "STOP":
            self.stop_client()
        elif command == "SEND":
            self.send_client()
        elif command == "OFF":
            self.off_client()

    def run_client(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, server_port))
        self.client_send_thr = ClientSendThread(self.sock)
        self.client_send_thr.start()
        self.client_recv_thr = ClientReceiveThread(self.sock)
        self.client_recv_thr.start()

    def stop_client(self):
        self.client_send_thr.join()
        self.client_recv_thr.join()
        self.sock.close()

    def send_client(self):
        message = raw_input("Enter: ")
        send_queue.put(message)

    def off_client(self):
        self.off_event.set()

class ClientSendThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.sock = sock

    def run(self):
        while not self.stop_event.isSet():
            if not send_queue.empty():
                self.sock.send(send_queue.get())
                send_queue.task_done()

    def join(self):
        self.stop_event.set()

class ClientReceiveThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.sock = sock

    def run(self):
        
        while not self.stop_event.isSet():
            global recv_queue
            message = self.sock.recv(128)
            print message
            recv_queue.put(message)

    def join(self):
        self.stop_event.set()

def main():
    client_controller_thr = ClientControllerThread()
    client_controller_thr.start()

if __name__ == "__main__":
    main()

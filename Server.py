import socket
import threading
import Queue
import select

import configreader
import serverstate
import gamemanager

config = configreader.ConfigReader()
server_state = serverstate.ServerState()

process_client_thr_list = list()

class ClientMessage():

    def __init__(self, connection, number, message):
        self.connection = connection
        self.client_number = number
        self.message = message

class ServerControllerThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.off_event = threading.Event()

    def run(self):
        while not self.off_event.isSet():
            self.enterCommand()

    def enterCommand(self):
        command = raw_input(">> ")

        if command == "RUN":
            self.run_server()
        elif command == "STOP":
            self.stop_server()
        elif command == "OFF":
            self.off_server()

    def stop_server(self):
        
        server_state.stop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config.server_ip, config.server_port))

        global process_client_thr_list
        for client_thr in process_client_thr_list:
            client_thr.join()
        del process_client_thr_list[:]
        
        print "!! Server is stopped."

    def run_server(self):

        config.get("serverconfig.ini")

        server_accept_thr = ServerAcceptConnection()
        server_accept_thr.start()

        server_state.run()
        print "!! Server is running."

    def off_server(self):
        self.off_event.set()
        if server_state.is_run():
            self.stop_server()
        print "!! Server is switched off."

class ProcessClientMessage(threading.Thread):

    def __init__(self, connection, message, game_manager):
        threading.Thread.__init__(self)
        self.connection = connection
        self.message = message
        self.game_manager = game_manager

    def run(self):
        splitted_message = self.message.split(' ')
        result = self.game_manager.run_function(splitted_message[0], splitted_message[1:])
        try:
            self.connection.send(result)
        except socket.error:
            return

class ProcessClientThread(threading.Thread):

    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.connection = connection
        self.eoc_message = "!eoc!"
        self.game_manager = gamemanager.GameManager()

    def run(self):
        while not self.stop_event.isSet():
            ready_to_read, ready_to_write, in_error = select.select([self.connection, ], [], [] , 5)

            for s in ready_to_read:

                try:
                    recv_message = self.connection.recv(128)
                except socket.error:
                    return

                process_client_message_thr = ProcessClientMessage(self.connection, recv_message, self.game_manager)
                process_client_message_thr.start()

                if recv_message == self.eoc_message:
                    #process eoc
                    self.join()
                    break

    def join(self):
        self.stop_event.set()

class ServerAcceptConnection(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = None

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((config.server_ip, config.server_port))
        self.sock.listen(1)

        while True:
            connection, client_address = self.sock.accept()

            if server_state.is_stop():
                break

            process_client_thr = ProcessClientThread(connection)
            process_client_thr_list.append(process_client_thr)
            process_client_thr.start()

        self.sock.close()

def main():
    server_controller_thr = ServerControllerThread()
    server_controller_thr.start()

if __name__ == "__main__":
    main()

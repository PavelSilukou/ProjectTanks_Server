class ServerState():

    def __init__(self):
        self.current_state = None
        self.states = ["RUN", "STOP"]

    def run(self):
        self.current_state = self.states[0]

    def is_run(self):
        return self.current_state == self.states[0]

    def stop(self):
        self.current_state = self.states[1]

    def is_stop(self):
        return self.current_state == self.states[1]

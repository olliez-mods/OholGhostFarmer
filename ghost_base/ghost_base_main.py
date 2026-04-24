from events import Events_Handler, Run, RunChild

class GhostBaseRun(RunChild):
    def start(self):
        print("Starting Ghost Base Run sorry")

    def tick(self):
        pass
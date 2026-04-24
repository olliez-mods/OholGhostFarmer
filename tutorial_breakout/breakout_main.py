from events import Events_Handler, Run, RunChild

class BreakoutRun(RunChild):
    def start(self):
        print("Starting Breakout Run")

    def tick(self):
        pass
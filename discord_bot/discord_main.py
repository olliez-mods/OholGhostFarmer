from events import Events_Handler, Run, RunChild

class DiscordRun(RunChild):
    def start(self):
        print("Starting Discord Run")

    def tick(self):
        pass
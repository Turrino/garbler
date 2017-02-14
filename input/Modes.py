import random


class Modes:
    def __init__(self, mode):
        modes = {"auto": self.auto, "console": self.console, "api": self.api}
        self.mode = modes[mode]

    def choose(self, options):
        return self.mode(options)

    @staticmethod
    def auto(options):
        return options[random.randrange(0,len(options))]["to"]

    @staticmethod
    def console(options):
        # todo ConsoleChosinator
        return None

    @staticmethod
    def api(options):

        return None

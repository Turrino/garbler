import random

# todo class ConsoleChosinator:

# todo class ApiChosinator:


class AutoChosinator:
    @staticmethod
    def choose(options):
        return options[random.randrange(0,len(options))]["to"]


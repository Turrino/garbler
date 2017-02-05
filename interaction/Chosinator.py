import random


class Auto:
    @staticmethod
    def choose(options):
        return options[random.randrange(0,len(options))]["to"]

# todo class ConsoleChosinator:
# todo class ApiChosinator:
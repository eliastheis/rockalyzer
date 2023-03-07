from json import load as json_load
from pprint import pprint

from console_colors import *
from Game import Game


class Replayer:

    def __init__(self, file_name):

        self.file_name = file_name
        print(HEADER + f'[+] Start Replaying "{self.file_name}"' + ENDC)

        # load json content
        with open(self.file_name, 'r') as f:
            self.json_content = json_load(f)
        
        # prepare game object
        self.game = Game()
            

    def replay(self):
        pass



if __name__ == '__main__':
    replayer = Replayer('replays/replay.json')
    replayer.replay()
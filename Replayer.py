from json import load as json_load
from pprint import pprint
from time import perf_counter
from matplotlib import pyplot as plt

from console_colors import *
from constants import *
from Game import Game
from Action import Action


class Replayer:

    def __init__(self, file_name, render=True):

        self.file_name = file_name
        self.render = render
        print(HEADER + f'[+] Start Replaying "{self.file_name}"' + ENDC)

        # load json content
        with open(self.file_name, 'r') as f:
            self.json_content = json_load(f)
        self.object_lookup = self.json_content['objects']
        self.name_lookup = self.json_content['names']

        # prepare game object
        self.game = Game(len(self.json_content['network_frames']['frames']), self.object_lookup, self.name_lookup, self.json_content['debug_info'], self.render)
    
        # print simple header
        self.print_header_info()

        # load actions
        Action.set_values(self.json_content['objects'])
    

    def print_header_info(self):

        prop = self.json_content['properties']
        replay_name = prop['ReplayName']
        date = prop['Date']
        team_size = prop['TeamSize']
        fps = prop['RecordFPS']


        # GENERAL STATS
        print(HEADER + f'\n=== {replay_name} ===' + ENDC)
        print(OKGREEN + f' {team_size}v{team_size} on {date} ({len(self.json_content["network_frames"]["frames"])} frames)' + ENDC)


        # PLAYER STATS
        print(HEADER + '\n=== Players ===' + ENDC)
        team0 = []
        team1 = []
        for player in prop['PlayerStats']:
            name = player['Name']
            b_bot = player['bBot']
            platform = 'BOT' if b_bot else player['Platform']['value'].replace('OnlinePlatform_', '')
            team = player['Team']
            score = player['Score']
            goals = player['Goals']
            assists = player['Assists']
            saves = player['Saves']
            shots = player['Shots']
            temp = {'name': name, 'platform': platform, 'score': score, 'goals': goals, 'assists': assists, 'saves': saves, 'shots': shots}
            if team == 0:
                team0.append(temp)
            else:
                team1.append(temp)
        longest_name = max(len(player['name']) for player in team0 + team1)
        tabs = '\t' * (longest_name // 4 + 1)
        print(OKGREEN + f' Team\t\tName\t\tScore\tGoals\tAssists\tSaves\tShots')
        print(OKRED, end='')
        for player in team1:
            print(f' ORANGE\t\t"{player["name"]}"\t{player["score"]}\t{player["goals"]}\t{player["assists"]}\t{player["saves"]}\t{player["shots"]}')
        print(OKCYAN, end='')
        for player in team0:
            print(f' BLUE\t\t"{player["name"]}"\t{player["score"]}\t{player["goals"]}\t{player["assists"]}\t{player["saves"]}\t{player["shots"]}')
        print(ENDC, end='')


        # EVENTS
        print(HEADER + '\n=== Events ===' + ENDC)
        for tick_mark in self.json_content['tick_marks']:

            frame = tick_mark['frame']
            description = tick_mark['description']
            elapsed_time = self.json_content['network_frames']['frames'][frame]['time']
            team = 0 if 'Team0' in description else 1
            description = description.replace('Team0', '').replace('Team1', '')

            if team == 1:
                print(OKRED, end='')
            else:
                print(OKCYAN, end='')
            print(f' {elapsed_time // 60:02.0f}:{elapsed_time % 60:02.0f} {description}' + ENDC)
            

    def replay(self):

        start_time = perf_counter()
        
        frames = self.json_content['network_frames']['frames']
        for i, frame in enumerate(frames):

            # update game
            self.game.update(i, frame)

            # render game
            if self.render:
                self.game.render()
        
        diff = perf_counter() - start_time
        print(HEADER + f'\n[+] Finished Replaying "{self.file_name}" in {diff:.3f} seconds' + ENDC)
        
    
    def get_stats(self):
        return self.game.get_stats(self.json_content['properties'])


if __name__ == '__main__':

    # load replay file
    replayer = Replayer('replays/replay.json', render=False)

    # replay
    replayer.replay()

    # get and print stats
    stats = replayer.get_stats()
    print(HEADER + '\n=== Stats ===' + ENDC)
    for key in stats:
        print(OKGREEN + f' {key}: \t{str(stats[key])[:50]}' + ENDC)

    print(OKGREEN + '\nGoals:' + ENDC)
    pprint(stats['goals'])

    print(OKGREEN + 'Players:' + ENDC)
    pprint(stats['players'])

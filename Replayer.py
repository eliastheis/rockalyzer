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
    
        # print simple header
        self.print_sime_stats()
    

    def print_sime_stats(self):

        prop = self.json_content['properties']
        replay_name = prop['ReplayName']
        date = prop['Date']
        team_size = prop['TeamSize']
        fps = prop['RecordFPS']


        # GENERAL STATS
        print(HEADER + f'\n=== {replay_name} ===' + ENDC)
        print(OKGREEN + f' {team_size}v{team_size} on {date}' + ENDC)


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
        for player in team0:
            print(f' ORANGE\t\t"{player["name"]}"\t{player["score"]}\t{player["goals"]}\t{player["assists"]}\t{player["saves"]}\t{player["shots"]}')
        print(OKCYAN, end='')
        for player in team1:
            print(f' BLUE\t\t"{player["name"]}"\t{player["score"]}\t{player["goals"]}\t{player["assists"]}\t{player["saves"]}\t{player["shots"]}')
        print(ENDC, end='')


        # EVENTS
        print(HEADER + '\n=== Events ===' + ENDC)
        for tick_mark in self.json_content['tick_marks']:

            frame = tick_mark['frame']
            description = tick_mark['description']
            elapsed_time = frame / fps
            team = 0 if 'Team0' in description else 1
            description = description.replace('Team0', '').replace('Team1', '')

            if team == 0:
                print(OKRED, end='')
            else:
                print(OKCYAN, end='')
            print(f' {elapsed_time // 60:02.0f}:{elapsed_time % 60:02.0f} {description}' + ENDC)
            

    def replay(self):
        pass



if __name__ == '__main__':
    replayer = Replayer('replays/replay.json')
    replayer.replay()
from pprint import pprint
from json import dump as json_dump
from matplotlib import pyplot as plt
import numpy as np
import math

from console_colors import *
from constants import *
from Action import Action


class Game:

    def __init__(self, num_frames, object_lookup, name_lookup, debug_info, render):
        self.num_frames = num_frames
        self.object_lookup = object_lookup
        self.name_lookup = name_lookup
        self.debug_info = debug_info
        self.b_render = render
        self.time = 0.0
        self.current_fps = 0.0
        self.actors = {}

        # state stuff
        self.player_car_pairs = None
        self.ball_id = None
        self.last_shot = None
        self.last_goal = None

        # render stuff
        if self.b_render:
            plt.style.use('dark_background')
            plt.ion()
            # set size of plot
            plt.figure(figsize=(10, 10))
        
        # prepare snapshot
        self.prepare_snapshot()


###############
# ACTOR STUFF #
###############


    def update(self, frame_index, frame):

        # update time and fps
        self.time = frame['time']
        delta = frame['delta']
        self.current_fps = 0 if delta == 0 else 1 / delta

        # next: handle new_actors, deleted_actors and updated_actors
        # first we handle deleted_actors, because actor_id's are reused

        # deleted actors
        self.delete_actors(frame['deleted_actors'])
        
        # new actors
        self.add_actors(frame['new_actors'])
        
        # updated actors
        event_goal, event_hit_ball = self.update_actors(frame['updated_actors'], frame_index)

        # handle all events
        if event_goal:
            self.handle_goal(frame_index)
        if event_hit_ball:
            self.handle_hit_ball(frame_index)

        # find objects
        self.player_car_pairs = self.get_player_car_pairs()
        self.ball_id = self.get_ball()
    
        # calculate stuff
        self.calculate_stuff(frame_index)

        # snapshot values
        self.snapshot_values(frame_index)

        #if frame_index == 300:
        #    self.dump_actors_into_json()


    def delete_actors(self, actors):
        for actor in actors:
            actor_id = actor
            # TODO: handle parent-objects
            del self.actors[actor_id]


    def add_actors(self, actors):
        for actor in actors:
            actor_id = actor['actor_id']
            object_id = actor['object_id']

            # add list of parent-object_ids
            actor['parent_ids'] = []

            # add readable object_name
            actor['object_name'] = self.object_lookup[object_id]
            actor['name_id_name'] = self.name_lookup[actor['name_id']]

            if object_id == Action.Archetypes_GameEvent_GameEvent_Soccar:
                actor['frames_with_event'] = [] # temporary

            if 'initial_trajectory' in actor:
                # we take the position and rotation from the initial_trajectory and add it to the actor
                initial_trajectory = actor['initial_trajectory']
                actor = actor | initial_trajectory
                del actor['initial_trajectory']
                
            self.actors[actor_id] = actor


    def update_actors(self, actors, frame_index):

        # events
        event_goal = False
        event_hit_ball = False

        for actor in actors:
            actor_id = actor['actor_id']
            object_name = self.object_lookup[actor['object_id']]

            match actor['object_id']:

                case Action.Engine_Actor_RemoteRole:
                    self.actors[actor_id]['remote_role'] = actor['attribute']['Enum']
                
                case Action.Engine_Actor_DrawScale:
                    self.actors[actor_id]['draw_scale'] = actor['attribute']['Float']

                case Action.TAGame_CarComponent_TA_Vehicle:
                    # add actor_id to list of parent-objects
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                    
                case Action.TAGame_CarComponent_TA_ReplicatedActive:
                    self.actors[actor_id]['active'] = actor['attribute']['Byte']

                case Action.TAGame_CarComponent_Boost_TA_ReplicatedBoostAmount:
                    self.actors[actor_id]['boost'] = actor['attribute']['Byte']
                
                case Action.TAGame_GameEvent_TA_ReplicatedRoundCountDownNumber:
                    self.actors[actor_id]['round_countdown'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_ReplicatedGameStateTimeRemaining:
                    self.actors[actor_id]['time_remaining'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_ReplicatedStateName:
                    self.actors[actor_id]['stateName'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_BotSkill:
                    self.actors[actor_id]['bot_skill'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_bHasLeaveMatchPenalty:
                    self.actors[actor_id]['has_leave_match_penalty'] = actor['attribute']['Boolean']
                
                case Action.TAGame_GameEvent_Team_TA_MaxTeamSize:
                    self.actors[actor_id]['max_team_size'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_Soccar_TA_RoundNum:
                    self.actors[actor_id]['current_round'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_Soccar_TA_bBallHasBeenHit:
                    # this event is not triggered when the ball is hit, but when the ball is hit at kickoff
                    # and at some random times
                    self.actors[actor_id]['ball_has_been_hit'] = actor['attribute']['Boolean']
                
                case Action.TAGame_GameEvent_Soccar_TA_SecondsRemaining:
                    self.actors[actor_id]['seconds_remaining'] = actor['attribute']['Int']
                
                case Action.Engine_Pawn_PlayerReplicationInfo:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_RBActor_TA_ReplicatedRBState:
                    # if the new linear_velocity is None then we do not update the linear_velocity
                    if actor['attribute']['RigidBody']['linear_velocity'] is None:
                        del actor['attribute']['RigidBody']['linear_velocity']
                    self.actors[actor_id].update(actor['attribute']['RigidBody'])

                case Action.TAGame_Vehicle_TA_ReplicatedSteer:
                    self.actors[actor_id]['steer'] = actor['attribute']['Byte']
                
                case Action.TAGame_Vehicle_TA_ReplicatedThrottle:
                    self.actors[actor_id]['throttle'] = actor['attribute']['Byte']
                
                case Action.TAGame_Vehicle_TA_bReplicatedHandbrake:
                    self.actors[actor_id]['handbrake'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Vehicle_TA_bDriving:
                    self.actors[actor_id]['driving'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Car_TA_RumblePickups:
                    # IGNORE Rumble stuff
                    pass
            
                case Action.TAGame_Car_TA_TeamPaint:
                    self.actors[actor_id]['team_paint'] = actor['attribute']['TeamPaint']
                    self.actors[actor_id]['team'] = actor['attribute']['TeamPaint']['team']
                
                case Action.TAGame_CameraSettingsActor_TA_CameraYaw:
                    self.actors[actor_id]['camera_yaw'] = actor['attribute']['Byte']
                
                case Action.TAGame_CameraSettingsActor_TA_CameraPitch:
                    self.actors[actor_id]['camera_pitch'] = actor['attribute']['Byte']
                
                case Action.TAGame_CameraSettingsActor_TA_bMouseCameraToggleEnabled:
                    self.actors[actor_id]['camera_toggle'] = actor['attribute']['Boolean']
                
                case Action.TAGame_CameraSettingsActor_TA_bUsingSwivel:
                    self.actors[actor_id]['using_swivel'] = actor['attribute']['Boolean']
                
                case Action.TAGame_CameraSettingsActor_TA_bUsingBehindView:
                    self.actors[actor_id]['using_behind_view'] = actor['attribute']['Boolean']
                
                case Action.TAGame_CameraSettingsActor_TA_ProfileSettings:
                    self.actors[actor_id]['camera_settings'] = actor['attribute']['CamSettings']
                
                case Action.TAGame_CameraSettingsActor_TA_bUsingSecondaryCamera:
                    self.actors[actor_id]['using_ball_cam'] = actor['attribute']['Boolean']
                
                case Action.Engine_PlayerReplicationInfo_UniqueId:
                    self.actors[actor_id]['unique_id'] = actor['attribute']['UniqueId']
                    # check for MMR in debug_info
                    remote_id = self.actors[actor_id]['unique_id']['remote_id']
                    id = None
                    if 'Epic' in remote_id:
                        id = remote_id['Epic']
                    elif 'Steam' in remote_id:
                        id = remote_id['Steam']
                    elif 'PlayStation' in remote_id:
                        id = remote_id['PlayStation']['online_id']
                    if id:
                        for info in self.debug_info:
                            if id in info['user']:
                                self.actors[actor_id]['mmr'] = info['text']
                    else:
                        print(WARNING, 'Unknown remote_id type: ' + str(remote_id) + ENDC)
                        exit()
                
                case Action.Engine_PlayerReplicationInfo_Team:
                    self.actors[actor_id]['team'] = actor['attribute']['ActiveActor']['actor']
                
                case Action.Engine_PlayerReplicationInfo_PlayerID:
                    self.actors[actor_id]['player_id'] = actor['attribute']['Int']
                
                case Action.Engine_PlayerReplicationInfo_PlayerName:
                    self.actors[actor_id]['player_name'] = actor['attribute']['String']
                
                case Action.Engine_PlayerReplicationInfo_Ping:
                    self.actors[actor_id]['ping'] = actor['attribute']['Byte']
                
                case Action.TAGame_PRI_TA_CurrentVoiceRoom:
                    self.actors[actor_id]['current_voice_room'] = actor['attribute']['String']
                
                case Action.TAGame_PRI_TA_SpectatorShortcut:
                    self.actors[actor_id]['spectator_shortcut'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_SteeringSensitivity:
                    self.actors[actor_id]['steering_sensitivity'] = actor['attribute']['Float']
                
                case Action.TAGame_PRI_TA_Title:
                    self.actors[actor_id]['title'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_PartyLeader:
                    self.actors[actor_id]['party_leader_id'] = actor['attribute']['PartyLeader']
               
                case Action.TAGame_PRI_TA_ClientLoadoutsOnline:
                    self.actors[actor_id]['loadout_online'] = actor['attribute']['LoadoutsOnline']
                
                case Action.TAGame_PRI_TA_ClientLoadouts:
                    self.actors[actor_id]['team_loadout'] = actor['attribute']['TeamLoadout']
                
                case Action.TAGame_PRI_TA_ReplicatedGameEvent:
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    self.actors[other_actor_id]['frames_with_event'].append(frame_index)
                
                case Action.TAGame_PRI_TA_PlayerHistoryValid:
                    self.actors[actor_id]['player_history_valid'] = actor['attribute']['Boolean']
                
                case Action.TAGame_PRI_TA_MatchScore:
                    self.actors[actor_id]['score'] = actor['attribute']['Int']
                
                case Action.TAGame_Ball_TA_HitTeamNum:
                    event_hit_ball = True
                    print(actor['attribute']['Byte'], end=' ')
                    self.actors[actor_id]['hit_team_num'] = actor['attribute']['Byte']
                
                case Action.TAGame_CarComponent_Dodge_TA_DodgeTorque:
                    self.actors[actor_id]['location'] = actor['attribute']['Location']
                
                case Action.Engine_GameReplicationInfo_ServerName:
                    self.actors[actor_id]['server'] = actor['attribute']['String']
                
                case Action.ProjectX_GRI_X_MatchGuid:
                    self.actors[actor_id]['match_guid'] = actor['attribute']['String']
                
                case Action.ProjectX_GRI_X_bGameStarted:
                    self.actors[actor_id]['game_started'] = actor['attribute']['Boolean']
                
                case Action.ProjectX_GRI_X_GameServerID:
                    self.actors[actor_id]['server_id'] = actor['attribute']['String']

                case Action.ProjectX_GRI_X_Reservations:
                    self.actors[actor_id]['reservation'] = actor['attribute']['Reservation']
                
                case Action.ProjectX_GRI_X_ReplicatedServerRegion:
                    self.actors[actor_id]['region'] = actor['attribute']['String']

                case Action.ProjectX_GRI_X_ReplicatedGamePlaylist:
                    self.actors[actor_id]['game_playlist'] = actor['attribute']['Int']
                
                case Action.TAGame_Team_TA_GameEvent:
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    self.actors[other_actor_id]['frames_with_event'].append(frame_index)
                
                case Action.TAGame_VehiclePickup_TA_NewReplicatedPickupData:
                    instigator_id = actor['attribute']['PickupNew']['instigator']
                    if instigator_id is not None: # for whatever reason, instigator_id can be None
                        if instigator_id != -1: # for whatever reason, instigator_id can be -1
                            if 'boost_pickups' not in self.actors[instigator_id]:
                                self.actors[instigator_id]['boost_pickups'] = []
                            picked_up = actor['attribute']['PickupNew']['picked_up']
                            boost_actor_id = actor['actor_id']
                            data = {'picked_up': picked_up, 'frame_index': self.time, 'boost_actor_id': boost_actor_id}
                            self.actors[instigator_id]['boost_pickups'].append(data)

                case Action.TAGame_PRI_TA_PersistentCamera:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_CameraSettingsActor_TA_PRI:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_Ball_TA_GameEvent:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_PRI_TA_MatchGoals:
                    event_goal = True
                    self.actors[actor_id]['match_goals'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_MatchAssists:
                    self.actors[actor_id]['match_assists'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_MatchSaves:
                    self.actors[actor_id]['match_saves'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_MatchShots:
                    self.actors[actor_id]['match_shots'] = actor['attribute']['Int']
                
                case Action.Engine_PlayerReplicationInfo_Score:
                    self.actors[actor_id]['score'] = actor['attribute']['Int']
                
                case Action.Engine_TeamInfo_Score:
                    self.actors[actor_id]['score'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_bCanVoteToForfeit:
                    self.actors[actor_id]['can_vote_to_forfeit'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Car_TA_ReplicatedDemolishGoalExplosion:
                    self.actors[actor_id]['demolish_fx'] = actor['attribute']['DemolishFx']
                
                case Action.TAGame_GameEvent_Soccar_TA_ReplicatedScoredOnTeam:
                    self.actors[actor_id]['scored_on_team'] = actor['attribute']['Byte']
                
                case Action.Engine_Actor_bCollideActors:
                    self.actors[actor_id]['collide_actors'] = actor['attribute']['Boolean']
                
                case Action.Engine_Actor_bBlockActors:
                    self.actors[actor_id]['block_actors'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Ball_TA_ReplicatedExplosionDataExtended:
                    self.actors[actor_id]['extended_explosion'] = actor['attribute']['ExtendedExplosion']
                
                case Action.Engine_Actor_bHidden:
                    self.actors[actor_id]['hidden'] = actor['attribute']['Boolean']
                
                case Action.TAGame_PRI_TA_bReady:
                    self.actors[actor_id]['ready'] = actor['attribute']['Boolean']

                case Action.TAGame_PRI_TA_ReplicatedWorstNetQualityBeyondLatency:
                    self.actors[actor_id]['worst_net_quality_beyond_latency'] = actor['attribute']['Byte']
                
                case Action.TAGame_CarComponent_FlipCar_TA_FlipCarTime:
                    self.actors[actor_id]['flip_car_time'] = actor['attribute']['Float']
                
                case Action.TAGame_GameEvent_Soccar_TA_MaxScore:
                    self.actors[actor_id]['max_score'] = actor['attribute']['Int']
                
                case Action.TAGame_Team_TA_ClubColors:
                    self.actors[actor_id]['club_colors'] = actor['attribute']['ClubColors']

                case Action.TAGame_Car_TA_ClubColors:
                    self.actors[actor_id]['club_colors'] = actor['attribute']['ClubColors']
                
                case Action.ProjectX_GRI_X_ReplicatedGameMutatorIndex:
                    self.actors[actor_id]['game_mutator_index'] = actor['attribute']['Int']
                
                case Action.TAGame_GameEvent_TA_MatchTypeClass:
                    # pretty weird event
                    pass
            
                case Action.Engine_GameReplicationInfo_GameClass:
                    # pretty weird event
                    pass
            
                case Action.TAGame_GameEvent_Soccar_TA_ReplicatedStatEvent:
                    # pretty weird event
                    pass
            
                case _:

                    target_id = actor_id
                    target_object_name = object_name
                    event_name = self.object_lookup[actor['object_id']]
                    is_refernce = 'ActiveActor' in actor['attribute']
                    is_valid_reference = False
                    reference_id = None
                    if is_refernce:
                        reference_id = actor['attribute']['ActiveActor']['actor']
                        is_valid_reference = reference_id in self.actors
                        if is_valid_reference:
                            reference_object_name = self.object_lookup[self.actors[reference_id]['object_id']]
                    
                    print()
                    print(OKRED + f'\nUpdate Actor {actor_id} ({target_object_name}) with event {event_name}' + ENDC)

                    print(OKGREEN + f'TARGET ACTOR:' + ENDC)
                    pprint(self.actors[target_id])

                    print(OKGREEN + f'TARGET EVENT:' + ENDC)
                    pprint(actor)

                    if is_valid_reference:
                        print(OKBLUE + f'Reference {reference_id} ({reference_object_name})' + ENDC)
                        pprint(self.actors[reference_id])
                    else:
                        print(WARNING + f'Reference {reference_id} (INVALID)' + ENDC)
        
        return event_goal, event_hit_ball


###############
# VALUE STUFF #
###############


    def calculate_stuff(self, frame_index):

        # calculate car speed
        for player, car in self.player_car_pairs:
            if 'linear_velocity' in self.actors[car]:
                linear_velocity = self.actors[car]['linear_velocity']
                if linear_velocity is not None:
                    speed = (linear_velocity['x'] ** 2 + linear_velocity['y'] ** 2 + linear_velocity['z'] ** 2) ** 0.5
                    self.actors[car]['speed'] = speed
            else:
                self.actors[car]['speed'] = -1.0
        
        # calculate ball speed
        if 'linear_velocity' in self.actors[self.ball_id]:
            linear_velocity = self.actors[self.ball_id]['linear_velocity']
            if linear_velocity is not None:
                speed = (linear_velocity['x'] ** 2 + linear_velocity['y'] ** 2 + linear_velocity['z'] ** 2) ** 0.5
                self.actors[self.ball_id]['speed'] = speed
            else:
                self.actors[self.ball_id]['speed'] = -1.0
        else:
            self.actors[self.ball_id]['speed'] = -1.0


    def prepare_snapshot(self):
        
        self.hist_ball_speed = np.full(self.num_frames, -1.0, dtype=np.float32)
        self.hist_player_speeds = {}


    def snapshot_values(self, frame_index):
        
        # ball speed
        self.hist_ball_speed[frame_index] = self.actors[self.get_ball()]['speed']

        # player speeds
        for player, car in self.player_car_pairs:
            player_name = self.actors[player]['player_name']
            if player_name not in self.hist_player_speeds:
                self.hist_player_speeds[player_name] = np.full(self.num_frames, -1.0, dtype=np.float32)
            self.hist_player_speeds[player_name][frame_index] = self.actors[car]['speed']


################
# RENDER STUFF #
################


    def render_map(self):
        # team orange
        plt.plot([MAP_SIDE_WALL_X, MAP_SIDE_WALL_X], [0, MAP_WALL_DISTANCE_Y-MAP_CORNER_SIZE], color='orange') # wall
        plt.plot([MAP_SIDE_WALL_X, MAP_SIDE_WALL_X-MAP_CORNER_SIZE], [MAP_WALL_DISTANCE_Y-MAP_CORNER_SIZE, MAP_WALL_DISTANCE_Y], color='orange') # angle
        plt.plot([MAP_SIDE_WALL_X-MAP_CORNER_SIZE, MAP_HALF_GOAL_WIDTH], [MAP_WALL_DISTANCE_Y, MAP_WALL_DISTANCE_Y], color='orange') # back wall
        plt.plot([MAP_HALF_GOAL_WIDTH, MAP_HALF_GOAL_WIDTH], [MAP_WALL_DISTANCE_Y, MAP_WALL_DISTANCE_Y+MAP_GOAL_DEPTH], color='orange') # goal
        plt.plot([MAP_HALF_GOAL_WIDTH, -MAP_HALF_GOAL_WIDTH], [MAP_WALL_DISTANCE_Y+MAP_GOAL_DEPTH, MAP_WALL_DISTANCE_Y+MAP_GOAL_DEPTH], color='orange') # goal
        plt.plot([-MAP_HALF_GOAL_WIDTH, -MAP_HALF_GOAL_WIDTH], [MAP_WALL_DISTANCE_Y, MAP_WALL_DISTANCE_Y+MAP_GOAL_DEPTH], color='orange') # goal
        plt.plot([-MAP_SIDE_WALL_X+MAP_CORNER_SIZE, -MAP_HALF_GOAL_WIDTH], [MAP_WALL_DISTANCE_Y, MAP_WALL_DISTANCE_Y], color='orange') # back wall
        plt.plot([-MAP_SIDE_WALL_X, -MAP_SIDE_WALL_X+MAP_CORNER_SIZE], [MAP_WALL_DISTANCE_Y-MAP_CORNER_SIZE, MAP_WALL_DISTANCE_Y], color='orange') # angle
        plt.plot([-MAP_SIDE_WALL_X, -MAP_SIDE_WALL_X], [MAP_WALL_DISTANCE_Y-MAP_CORNER_SIZE, 0], color='orange') # wall
        # team blue (inverted y)
        plt.plot([MAP_SIDE_WALL_X, MAP_SIDE_WALL_X], [0, -MAP_WALL_DISTANCE_Y+MAP_CORNER_SIZE], color='blue') # wall
        plt.plot([MAP_SIDE_WALL_X, MAP_SIDE_WALL_X-MAP_CORNER_SIZE], [-MAP_WALL_DISTANCE_Y+MAP_CORNER_SIZE, -MAP_WALL_DISTANCE_Y], color='blue') # angle
        plt.plot([MAP_SIDE_WALL_X-MAP_CORNER_SIZE, MAP_HALF_GOAL_WIDTH], [-MAP_WALL_DISTANCE_Y, -MAP_WALL_DISTANCE_Y], color='blue') # back wall
        plt.plot([MAP_HALF_GOAL_WIDTH, MAP_HALF_GOAL_WIDTH], [-MAP_WALL_DISTANCE_Y, -MAP_WALL_DISTANCE_Y-MAP_GOAL_DEPTH], color='blue') # goal
        plt.plot([MAP_HALF_GOAL_WIDTH, -MAP_HALF_GOAL_WIDTH], [-MAP_WALL_DISTANCE_Y-MAP_GOAL_DEPTH, -MAP_WALL_DISTANCE_Y-MAP_GOAL_DEPTH], color='blue') # goal
        plt.plot([-MAP_HALF_GOAL_WIDTH, -MAP_HALF_GOAL_WIDTH], [-MAP_WALL_DISTANCE_Y, -MAP_WALL_DISTANCE_Y-MAP_GOAL_DEPTH], color='blue') # goal
        plt.plot([-MAP_SIDE_WALL_X+MAP_CORNER_SIZE, -MAP_HALF_GOAL_WIDTH], [-MAP_WALL_DISTANCE_Y, -MAP_WALL_DISTANCE_Y], color='blue') # back wall
        plt.plot([-MAP_SIDE_WALL_X, -MAP_SIDE_WALL_X+MAP_CORNER_SIZE], [-MAP_WALL_DISTANCE_Y+MAP_CORNER_SIZE, -MAP_WALL_DISTANCE_Y], color='blue') # angle
        plt.plot([-MAP_SIDE_WALL_X, -MAP_SIDE_WALL_X], [-MAP_WALL_DISTANCE_Y+MAP_CORNER_SIZE, 0], color='blue') # wall

        # render middle line
        plt.plot([MAP_SIDE_WALL_X, -MAP_SIDE_WALL_X], [0, 0], color='gray', linewidth=0.5)

        # render outer bounds for better visualization
        plt.scatter([MAP_OUTER_BOUND, MAP_OUTER_BOUND, -MAP_OUTER_BOUND, -MAP_OUTER_BOUND],
                    [MAP_OUTER_BOUND, -MAP_OUTER_BOUND, MAP_OUTER_BOUND, -MAP_OUTER_BOUND],
                    color='white', s=0.01)


    def render_current_frame(self, pause_time=99999):
        # update player, cars and ball for render
        self.player_car_pairs = self.get_player_car_pairs()
        self.ball_id = self.get_ball()
        plt.style.use('dark_background')
        plt.figure(figsize=(10, 10))
        plt.ion()
        self.render()
        plt.pause(pause_time)


    def render(self):
        # check if rendering is enabled
        plt.clf()

        # render map
        self.render_map()

        # render boost pads
        for location in BOOST_LOCATIONS:
            plt.scatter(location[0], location[1], color='yellow', s=0.5)

        # render players
        for player, car in self.player_car_pairs:
            player_name = 'unkown player' if 'player_name' not in self.actors[player] else self.actors[player]['player_name']
            #player_name = self.actors[player]['player_name']
            x = self.actors[car]['location']['x']
            y = self.actors[car]['location']['y']
            plt.scatter(x, y, label=player_name)

        # render ball
        ball = self.get_ball()
        if ball is not None:
            x = self.actors[ball]['location']['x']
            y = self.actors[ball]['location']['y']
            plt.scatter(x, y, label='ball', color='red')

        plt.title(round(self.time))
        plt.legend()
        plt.pause(0.0001)


####################
# HELPER FUNCTIONS #
####################


    def dump_actors_into_json(self):
        with open('json_dumps/actors.json', 'w') as f:
            json_dump(self.actors, f, indent=4)
            print(OKBLUE + 'Dumped actors in actors.json' + ENDC)
            exit(0)


    def get_player_car_pairs(self):
        player_car_pairs = []

        # get all actor_ids from objects with object_id 264
        players = [actor_id for actor_id, actor in self.actors.items() if actor['object_id'] == Action.TAGame_Default__PRI_TA]

        for player in players:
            
            # get all children of the player (car)
            car = [actor_id for actor_id, actor in self.actors.items() if player in actor['parent_ids'] and actor['object_id'] == Action.Archetypes_Car_Car_Default]
            if len(car) == 0:
                pass
            elif len(car) == 1:
                car = car[0]
                player_car_pairs.append((player, car))
            else:
                # if there are more than one car, the player was probably demoed
                # the last car is the one that is used
                car = car[-1]
                player_car_pairs.append((player, car))
        return player_car_pairs


    def get_ball(self):

        # get all actor_ids from objects with object_id 264
        ball = [actor_id for actor_id, actor in self.actors.items() if actor['object_id'] == Action.Archetypes_Ball_Ball_Default]

        if len(ball) == 0:
            return None
        elif len(ball) == 1:
            return ball[0]
        else:
            print(WARNING + 'There are more than one ball' + ENDC)
            return ball[-1]
    
    
    def get_children(self, actor_id):
        return [actor_id for actor_id, actor in self.actors.items() if actor_id in actor['parent_ids']]


    def handle_goal(self, frame_index):
        # check if goal was scored
        ball_id = self.get_ball()
        # 1. ball is in goal
        if abs(self.actors[ball_id]['location']['y']) < MAP_WALL_DISTANCE_Y:
            return
            
        # 2. last goal was more than 3 seconds ago
        if self.last_goal is not None and frame_index - self.last_goal < 3*30:
            return

        # set last goal to current frame
        self.last_goal = frame_index

        # calculate ball speed
        linear_velocity = self.actors[ball_id]['linear_velocity']
        if linear_velocity is None:
            print(WARNING + 'Ball has no linear velocity' + ENDC)
            exit()
        ball_speed_squared = linear_velocity['x']**2 + linear_velocity['y']**2 + linear_velocity['z']**2
        ball_speed = math.sqrt(ball_speed_squared)

        speed_kmh = round(ball_speed * UU_TO_KMH_FACTOR, 2)
        print(OKGREEN + f'GOAL! Ball speed: {speed_kmh} km/h' + ENDC)


    def handle_hit_ball(self, frame_index):
        player, car, distance_squared = self.get_nearest_car_to_ball()
        player_name = self.actors[player]['player_name']
        print(OKGREEN + f'Player {player_name} hit the ball' + ENDC)


    def get_nearest_car_to_ball(self):
        # returns tuple (player_id, car_id, distance_squared)
        ball_location = self.actors[self.ball_id]['location']
        ball_x, ball_y, ball_z = ball_location['x'], ball_location['y'], ball_location['z']
        player_distances = []
        for player, car in self.player_car_pairs:
            car_location = self.actors[car]['location']
            car_x, car_y, car_z = car_location['x'], car_location['y'], car_location['z']
            # we do not need the actual distance, but the squared distance is faster to calculate
            distance_squared = (car_x-ball_x)**2 + (car_y-ball_y)**2 + (car_z-ball_z)**2
            player_distances.append((player, car, distance_squared))
        # sort by distance
        player_distances.sort(key=lambda x: x[2])
        return player_distances[0]


    def get_current_shot(self):
        # returns dict with all information about the current shot
        player_id, car_id, _ = self.get_nearest_car_to_ball()
        if 'player_name' not in self.actors[player_id]:
            return None
        player_name = self.actors[player_id]['player_name']
        car_location = self.actors[car_id]['location']
        car_x, car_y, car_z = car_location['x'], car_location['y'], car_location['z']
        ball_location = self.actors[self.ball_id]['location']
        ball_x, ball_y, ball_z = ball_location['x'], ball_location['y'], ball_location['z']
        shot = {
            'player_id': player_id,
            'player_name': player_name,
            'car_id': car_id, 'car_x': car_x, 'car_y': car_y, 'car_z': car_z,
            'ball_id': self.ball_id, 'ball_x': ball_x, 'ball_y': ball_y, 'ball_z': ball_z,
            'time': self.time
        }
        return shot


#########
# STATS #
#########


    def get_stats(self):
        stats = {}
        
        stats['ball_speed'] = self.hist_ball_speed
        stats['player_speeds'] = self.hist_player_speeds
        
        return stats

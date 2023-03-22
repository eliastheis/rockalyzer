from pprint import pprint
from json import dump as json_dump
from matplotlib import pyplot as plt

from console_colors import *
from Action import Action


class Game:

    def __init__(self, object_lookup, name_lookup, debug_info, render):
        self.object_lookup = object_lookup
        self.name_lookup = name_lookup
        self.debug_info = debug_info
        self.b_render = render
        self.time = 0.0
        self.current_fps = 0.0
        self.actors = {}
        self.max_x = 4085.92
        self.max_y = 5981.23
        plt.style.use('dark_background')
        plt.ion()


    def update(self, frame_index, frame):

        # update time and fps
        self.time = frame['time']
        delta = frame['delta']
        self.current_fps = 0 if delta == 0 else 1 / delta

        # next: handle new_actors, deleted_actors and updated_actors
        # first we handle deleted_actors, because actor_id's are reused
        #if len(frame['new_actors']) + len(frame['deleted_actors']) + len(frame['updated_actors']) == 0:
        #    print(OKBLUE + 'No actors in this frame' + ENDC)

        # deleted actors
        self.delete_actors(frame['deleted_actors'])
        
        # new actors
        self.add_actors(frame['new_actors'])
        
        # updated actors
        self.update_actors(frame['updated_actors'], frame_index)

        '''if frame_index == 1800:
            # dump actors in json file
            with open('json_dumps/actors_new.json', 'w') as f:
                json_dump(self.actors, f, indent=4)
            print(OKBLUE + 'Dumped actors in actors.json' + ENDC)
            exit(0)'''
    

    def get_players(self):

        ret = []

        # get all actor_ids from objects with object_id 264
        players = [actor_id for actor_id, actor in self.actors.items() if actor['object_id'] == Action.TAGame_Default__PRI_TA]

        for player in players:
            
            # get all children of the player (car)
            car = [actor_id for actor_id, actor in self.actors.items() if player in actor['parent_ids'] and actor['object_id'] == Action.Archetypes_Car_Car_Default]
            if len(car) == 0:
                pass
            elif len(car) == 1:
                car = car[0]
                ret.append((player, car))
            else:
                # if there are more than one car, the player was probably demoed
                # the last car is the one that is used
                car = car[-1]
                ret.append((player, car))
        return ret


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


    def render(self):
        # check if rendering is enabled
        if not self.b_render:
            return
        plt.clf()

        # render players
        players = self.get_players()
        for player in players:
            player_name = self.actors[player[0]]['player_name']
            x = self.actors[player[1]]['location']['x']
            y = self.actors[player[1]]['location']['y']
            plt.scatter(x, y, label=player_name)
            plt.scatter([self.max_x, self.max_x, -self.max_x, -self.max_x], [self.max_y, -self.max_y, self.max_y, -self.max_y], color='white')


        # render ball
        ball = self.get_ball()
        if ball is not None:
            x = self.actors[ball]['location']['x']
            y = self.actors[ball]['location']['y']
            plt.scatter(x, y, label='ball', color='red')

        plt.title(round(self.time))
        plt.legend()
        plt.pause(0.0001)


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

            match object_id:

                case Action.Archetypes_GameEvent_GameEvent_Soccar:

                    actor['frames_with_event'] = []

                case 41 | 43 | 47 | 143 | 264 | 285 | 288 | 291: # Archetypes.Car.Car_Default
                    # we take the position and rotation from the initial_trajectory and add it to the actor
                    initial_trajectory = actor['initial_trajectory']
                    actor = actor | initial_trajectory
                    del actor['initial_trajectory']
                
            self.actors[actor_id] = actor


    def update_actors(self, actors, frame_index):
        for actor in actors:
            actor_id = actor['actor_id']
            object_name = self.object_lookup[actor['object_id']]

            match actor['object_id']:

                case Action.Engine_Actor_RemoteRole:
                    self.actors[actor_id]['remote_role'] = actor['attribute']['Enum']
                
                case Action.Engine_Actor_DrawScale:
                    self.actors[actor_id]['draw_scale'] = actor['attribute']['Float']

                case Action.TAGame_CarComponent_TA_Vehicle:
                    '''print(WARNING, self.object_lookup[self.actors[actor_id]['object_id']], end=' --> ')
                    correspondig_id = actor['attribute']['ActiveActor']['actor']
                    print(self.object_lookup[correspondig_id])
                    print(OKGREEN, ' BASE:' + ENDC)
                    pprint(self.actors[actor_id])
                    print(OKGREEN, ' parent:' + ENDC)
                    pprint(self.actors[correspondig_id])
                    print(OKGREEN, ' ACTOR:' + ENDC)
                    pprint(actor)'''
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
                    self.actors[actor_id]['ball_has_been_hit'] = actor['attribute']['Boolean']
                
                case Action.TAGame_GameEvent_Soccar_TA_SecondsRemaining:
                    self.actors[actor_id]['seconds_remaining'] = actor['attribute']['Int']
                
                case Action.Engine_Pawn_PlayerReplicationInfo:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                    '''print(OKCYAN + f'Update Actor {actor_id} ({object_name} ({actor["object_id"]}))' + ENDC)
                    pprint(self.actors[actor_id])
                    print()
                    pprint(actor['attribute'])
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    #pprint(self.actors[other_actor_id])
                    exit()'''
                
                case Action.TAGame_RBActor_TA_ReplicatedRBState:
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
                    self.actors[actor_id]['secondary_camera'] = actor['attribute']['Boolean']
                
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
                    self.actors[actor_id]['current_pickup'] = actor['attribute']['PickupNew'] | {'frame_index': self.time}
                
                case Action.TAGame_PRI_TA_PersistentCamera:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_CameraSettingsActor_TA_PRI:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_Ball_TA_GameEvent:
                    self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_PRI_TA_MatchGoals:
                    self.actors[actor_id]['match_goals'] = actor['attribute']['Int']
                
                case Action.TAGame_PRI_TA_MatchGoals:
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

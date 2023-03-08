from pprint import pprint
from console_colors import *
from json import dump as json_dump

class Game:

    def __init__(self, object_lookup, debug_info):
        self.object_lookup = object_lookup
        self.debug_info = debug_info
        self.time = 0.0
        self.current_fps = 0.0
        self.actors = {}


    def update(self, frame_index, frame):

        # update time and fps
        self.time = frame['time']
        delta = frame['delta']
        self.current_fps = 0 if delta == 0 else 1 / delta

        # next: handle new_actors, deleted_actors and updated_actors
        # first we handle deleted_actors, because actor_id's are reused
        if len(frame['new_actors']) + len(frame['deleted_actors']) + len(frame['updated_actors']) == 0:
            print(OKBLUE + 'No actors in this frame' + ENDC)

        # deleted actors
        self.delete_actors(frame['deleted_actors'])
        
        # new actors
        self.add_actors(frame['new_actors'])
        
        # updated actors
        self.update_actors(frame['updated_actors'], frame_index)

        if frame_index == 1800:
            # dump actors in json file
            with open('actors.json', 'w') as f:
                json_dump(self.actors, f, indent=4)
            print(OKBLUE + 'Dumped actors in actors.json' + ENDC)
            exit(0)
        

    

    def render(self):
        pass
    

    def delete_actors(self, actors):
        for actor in actors:
            actor_id = actor
            # TODO: handle super-objects
            del self.actors[actor_id]


    def add_actors(self, actors):
        for actor in actors:
            actor_id = actor['actor_id']
            object_id = actor['object_id']

            # add list of super-object_ids
            actor['super_ids'] = []

            match object_id:

                case 91: # Archetypes.GameEvent.GameEvent_Soccar

                    actor['frames_with_event'] = []

                case 143 | 264 | 285: # Archetypes.Car.Car_Default
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

                

                case 16: # Engine.Actor:RemoteRole
                    self.actors[actor_id]['remote_role'] = actor['attribute']['Enum']
                
                case 18: # Engine.Actor:DrawScale
                    self.actors[actor_id]['draw_scale'] = actor['attribute']['Float']

                case 23: # TAGame.CarComponent_TA:Vehicle
                    '''print(WARNING, self.object_lookup[self.actors[actor_id]['object_id']], end=' --> ')
                    correspondig_id = actor['attribute']['ActiveActor']['actor']
                    print(self.object_lookup[correspondig_id])
                    print(OKGREEN, ' BASE:' + ENDC)
                    pprint(self.actors[actor_id])
                    print(OKGREEN, ' SUPER:' + ENDC)
                    pprint(self.actors[correspondig_id])
                    print(OKGREEN, ' ACTOR:' + ENDC)
                    pprint(actor)'''
                    # add actor_id to list of super-objects
                    self.actors[actor_id]['super_ids'].append(actor['attribute']['ActiveActor']['actor'])
                    
                case 24: # TAGame.CarComponent_TA:ReplicatedActive
                    self.actors[actor_id]['active'] = actor['attribute']['Byte']

                case 28: # TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount
                    self.actors[actor_id]['boost'] = actor['attribute']['Byte']
                
                case 86: # TAGame.GameEvent_Soccar_TA:SecondsRemaining
                    self.actors[actor_id]['seconds_remaining'] = actor['attribute']['Int']
                
                case 116: # TAGame.RBActor_TA:ReplicatedRBState (ReplicatedRigidBodyState)
                    self.actors[actor_id].update(actor['attribute']['RigidBody'])

                case 123: # TAGame.Vehicle_TA:ReplicatedSteer
                    self.actors[actor_id]['steer'] = actor['attribute']['Byte']
                
                case 124: # TAGame.Vehicle_TA:ReplicatedThrottle
                    self.actors[actor_id]['throttle'] = actor['attribute']['Byte']
                
                case 126: # TAGame.Vehicle_TA:bReplicatedHandbrake
                    self.actors[actor_id]['handbrake'] = actor['attribute']['Boolean']
                
                case 127: # TAGame.Vehicle_TA:bDriving
                    self.actors[actor_id]['driving'] = actor['attribute']['Boolean']
                
                case 138: # TAGame.Car_TA:TeamPaint
                    self.actors[actor_id]['team_paint'] = actor['attribute']['TeamPaint']
                
                case 148: # TAGame.CameraSettingsActor_TA:CameraYaw
                    self.actors[actor_id]['camera_yaw'] = actor['attribute']['Byte']
                
                case 149: # TAGame.CameraSettingsActor_TA:CameraPitch
                    self.actors[actor_id]['camera_pitch'] = actor['attribute']['Byte']
                
                case 152: # TAGame.CameraSettingsActor_TA:bMouseCameraToggleEnabled
                    self.actors[actor_id]['camera_toggle'] = actor['attribute']['Boolean']
                
                case 153: # TAGame.CameraSettingsActor_TA:bUsingSwivel
                    self.actors[actor_id]['using_swivel'] = actor['attribute']['Boolean']
                
                case 157: # TAGame.CameraSettingsActor_TA:ProfileSettings
                    self.actors[actor_id]['camera_settings'] = actor['attribute']['CamSettings']
                
                case 156: # TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera
                    self.actors[actor_id]['secondary_camera'] = actor['attribute']['Boolean']
                
                case 172: # Engine.PlayerReplicationInfo:UniqueId
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
                
                case 183: # Engine.PlayerReplicationInfo:Team
                    self.actors[actor_id]['team'] = actor['attribute']['ActiveActor']['actor']
                
                case 184: # Engine.PlayerReplicationInfo:PlayerID
                    self.actors[actor_id]['player_id'] = actor['attribute']['Int']
                
                case 185: # Engine.PlayerReplicationInfo:PlayerName
                    self.actors[actor_id]['player_name'] = actor['attribute']['String']
                
                case 186: # Engine.PlayerReplicationInfo:Ping
                    self.actors[actor_id]['ping'] = actor['attribute']['Byte']
                
                case 193: # TAGame.PRI_TA:CurrentVoiceRoom
                    self.actors[actor_id]['current_voice_room'] = actor['attribute']['String']
                
                case 197: # TAGame.PRI_TA:SpectatorShortcut
                    self.actors[actor_id]['spectator_shortcut'] = actor['attribute']['Int']
                
                case 205: # TAGame.PRI_TA:SteeringSensitivity
                    self.actors[actor_id]['steering_sensitivity'] = actor['attribute']['Float']
                
                case 207: # TAGame.PRI_TA:Title
                    self.actors[actor_id]['title'] = actor['attribute']['Int']
                
                case 208: # TAGame.PRI_TA:PartyLeader
                    self.actors[actor_id]['party_leader_id'] = actor['attribute']['PartyLeader']
               
                case 214: # TAGame.PRI_TA:ClientLoadoutsOnline
                    self.actors[actor_id]['loadout_online'] = actor['attribute']['LoadoutsOnline']
                
                case 215: # TAGame.PRI_TA:ClientLoadouts
                    self.actors[actor_id]['team_loadout'] = actor['attribute']['TeamLoadout']
                
                case 218: # TAGame.PRI_TA:ReplicatedGameEvent
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    self.actors[other_actor_id]['frames_with_event'].append(frame_index)
                
                case 220: # TAGame.PRI_TA:PlayerHistoryValid
                    self.actors[actor_id]['player_history_valid'] = actor['attribute']['Boolean']
                
                case 234: # TAGame.PRI_TA:MatchScore
                    self.actors[actor_id]['score'] = actor['attribute']['Int']
                
                case 273: # TAGame.Ball_TA:HitTeamNum
                    self.actors[actor_id]['hit_team_num'] = actor['attribute']['Byte']
                
                case 289: # TAGame.CarComponent_Dodge_TA:DodgeTorque
                    self.actors[actor_id]['location'] = actor['attribute']['Location']
                
                case 293: # Engine.GameReplicationInfo:ServerName
                    self.actors[actor_id]['server'] = actor['attribute']['String']
                
                case 304: # ProjectX.GRI_X:MatchGuid
                    self.actors[actor_id]['match_guid'] = actor['attribute']['String']
                
                case 305: # ProjectX.GRI_X:bGameStarted
                    self.actors[actor_id]['game_started'] = actor['attribute']['Boolean']
                
                case 306: # ProjectX.GRI_X:GameServerID
                    self.actors[actor_id]['server_id'] = actor['attribute']['String']

                case 307: # ProjectX.GRI_X:Reservations
                    self.actors[actor_id]['reservation'] = actor['attribute']['Reservation']

                case 310: # ProjectX.GRI_X:ReplicatedGamePlaylist
                    self.actors[actor_id]['game_playlist'] = actor['attribute']['Int']
                
                case 323: # TAGame.Team_TA:GameEvent
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    self.actors[other_actor_id]['frames_with_event'].append(frame_index)
                
                case 346: # TAGame.VehiclePickup_TA:NewReplicatedPickupData
                    self.actors[actor_id]['current_pickup'] = actor['attribute']['PickupNew'] | {'frame_index': self.time}
            
                
                case _:

                    pass

                    
                    # this prints any other action that is not handled above
                    print(OKCYAN + f'Update Actor {actor_id} ({object_name} ({actor["object_id"]}))' + ENDC)
                    pprint(self.actors[actor_id])
                    print()
                    pprint(actor['attribute'])
from pprint import pprint
from json import dump as json_dump
from matplotlib import pyplot as plt
import numpy as np
import math

from console_colors import *
from constants import *
from Action import Action


class Game:

    def __init__(self, num_frames, object_lookup, name_lookup, debug_info, render, properties, debug_print=False):
        self.num_frames = num_frames
        self.object_lookup = object_lookup
        self.name_lookup = name_lookup
        self.debug_info = debug_info
        self.b_render = render
        self.time = 0.0
        self.current_fps = 0.0
        self.actors = {}
        self.debug_print = debug_print
        self.properties = properties
        self.map_name = properties['MapName']

        # state stuff
        self.player_car_pairs = None
        self.ball_id = None
        self.seconds_remaining = 300
        self.frame_index = 0

        # render stuff
        if self.b_render:
            plt.style.use('dark_background')
            plt.ion()
            # set size of plot
            plt.figure(figsize=(10, 10))
        
        # prepare snapshot
        self.prepare_snapshot()

    
    def dispose(self):
        if self.b_render:
            plt.close()
        del self.actors
        del self.player_car_pairs
        del self.ball_id
        del self.seconds_remaining
        del self.frame_index
        del self.time
        del self.current_fps
        del self.debug_print
        del self.b_render
        del self.debug_info
        del self.name_lookup
        del self.object_lookup
        del self.num_frames


###############
# ACTOR STUFF #
###############


    def update(self, frame_index, frame):

        # update time and fps
        self.time = frame['time']
        delta = frame['delta']
        self.current_fps = 0 if delta == 0 else 1 / delta
        self.frame_index = frame_index

        # next: handle new_actors, deleted_actors and updated_actors
        # first we handle deleted_actors, because actor_id's are reused

        # deleted actors
        self.delete_actors(frame['deleted_actors'])
        
        # new actors
        self.add_actors(frame['new_actors'])
        
        # updated actors
        event_goal = self.update_actors(frame['updated_actors'], frame_index)

        # handle all events
        if event_goal:
            self.handle_goal(frame_index)

        # find objects
        self.player_car_pairs = self.get_player_car_pairs()
        self.ball_id = self.get_ball()
    
        # calculate stuff
        self.calculate_stuff(frame_index)

        # snapshot values
        self.snapshot_values(frame_index)

        # check for events
        self.check_for_events(frame_index)

        #if frame_index == 4900: # (first goal)
        #    self.dump_actors_into_json()
        #    exit()


    def delete_actors(self, actors):
        for actor in actors:
            actor_id = actor
            object_name = self.actors[actor_id]['object_name']
            if self.debug_print:
                print(f'[-] Deleting {object_name} ({actor_id})')
            # TODO: handle parent-objects
            # without handling the parent-objects, the could a reference to a deleted object
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

            if 'initial_trajectory' in actor:
                # we take the position and rotation from the initial_trajectory and add it to the actor
                initial_trajectory = actor['initial_trajectory']
                actor = actor | initial_trajectory
                del actor['initial_trajectory']
                
            self.actors[actor_id] = actor


    def update_actors(self, actors, frame_index):

        # events
        event_goal = False

        for actor in actors:
            actor_id = actor['actor_id']
            object_name = self.object_lookup[actor['object_id']]

            match actor['object_id']:

                case Action.Engine_Actor_RemoteRole:
                    self.actors[actor_id]['remote_role'] = actor['attribute']['Enum']
                
                case Action.Engine_Actor_DrawScale:
                    self.actors[actor_id]['draw_scale'] = actor['attribute']['Float']

                case Action.TAGame_CarComponent_TA_Vehicle:
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
                    self.seconds_remaining = actor['attribute']['Int']
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
                    elif 'PsyNet' in remote_id:
                        id = remote_id['PsyNet']['online_id']
                    elif 'Xbox' in remote_id:
                        id = remote_id['Xbox']
                    if id:
                        for info in self.debug_info:
                            if id in info['user']:
                                self.actors[actor_id]['mmr'] = info['text']
                    else:
                        print(WARNING, 'Unknown remote_id type ', ENDC,  str(remote_id))
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
                    if other_actor_id != -1:
                        if 'frames_with_event' not in self.actors[other_actor_id]:
                            self.actors[other_actor_id]['frames_with_event'] = []
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
                    if 'QWord' in actor['attribute']:
                        self.actors[actor_id]['server_id'] = actor['attribute']['QWord']
                    elif 'String' in actor['attribute']:
                        self.actors[actor_id]['server_id'] = actor['attribute']['String']
                    else:
                        print(WARNING, 'Unknown GameServerID type (should be String or QWord)', ENDC, str(actor['attribute']))
                        exit()

                case Action.ProjectX_GRI_X_Reservations:
                    self.actors[actor_id]['reservation'] = actor['attribute']['Reservation']
                
                case Action.ProjectX_GRI_X_ReplicatedServerRegion:
                    self.actors[actor_id]['region'] = actor['attribute']['String']

                case Action.ProjectX_GRI_X_ReplicatedGamePlaylist:
                    self.actors[actor_id]['game_playlist'] = actor['attribute']['Int']
                
                case Action.TAGame_Team_TA_GameEvent:
                    other_actor_id = actor['attribute']['ActiveActor']['actor']
                    if 'frames_with_event' not in self.actors[other_actor_id]:
                        self.actors[other_actor_id]['frames_with_event'] = []
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
                    if actor['attribute']['Boolean'] != True:
                        print(WARNING + 'Actor ' + str(actor_id) + ' is not hidden' + ENDC)
                        exit()
                    self.actors[actor_id]['hidden_since_frame'] = frame_index
                
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
                
                case Action.TAGame_CarComponent_FlipCar_TA_bFlipRight:
                    self.actors[actor_id]['flip_right'] = actor['attribute']['Boolean']
                
                case Action.TAGame_PRI_TA_bIsDistracted:
                    self.actors[actor_id]['is_distracted'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Team_TA_Difficulty:
                    self.actors[actor_id]['difficulty'] = actor['attribute']['Int']
                
                case Action.TAGame_Team_TA_CustomTeamName:
                    self.actors[actor_id]['custom_team_name'] = actor['attribute']['String']
                
                case Action.ProjectX_GRI_X_MatchGUID:
                    self.actors[actor_id]['match_guid'] = actor['attribute']['String']
                
                case Action.TAGame_GameEvent_Soccar_TA_SeriesLength:
                    self.actors[actor_id]['series_length'] = actor['attribute']['Int']
                
                case Action.TAGame_CarComponent_Dodge_TA_DodgeImpulse:
                    self.actors[actor_id]['dodge_impulse_location'] = actor['attribute']['Location']

                case Action.Engine_PlayerReplicationInfo_RemoteUserData:
                    self.actors[actor_id]['remote_user_data'] = actor['attribute']['String']
                
                case Action.TAGame_GameEvent_Soccar_TA_bOverTime:
                    if actor['attribute']['Boolean']:
                        self.actors[actor_id]['over_time_at_frame'] = frame_index
                        print('Overtime!' + ENDC)
                    else:
                        print(WARNING + 'Actor ' + str(actor_id) + ' is not in overtime' + ENDC)
                        exit()
                
                case Action.TAGame_GameEvent_Soccar_TA_bClubMatch:
                    self.actors[actor_id]['club_match'] = actor['attribute']['Boolean']
                
                case Action.TAGame_Team_TA_ClubID:
                    self.actors[actor_id]['club_id'] = actor['attribute']['Int64']
                
                case Action.Engine_PlayerReplicationInfo_bBot:
                    self.actors[actor_id]['is_bot'] = actor['attribute']['Boolean']
                
                case Action.TAGame_PRI_TA_BotProductName:
                    self.actors[actor_id]['bot_product_name'] = actor['attribute']['Int']

                case Action.TAGame_PRI_TA_ClubID:
                    self.actors[actor_id]['club_id'] = actor['attribute']['Int64']
                
                case Action.TAGame_GameEvent_Team_TA_bForfeit:
                    if actor['attribute']['Boolean']:
                        self.actors[actor_id]['forfeit_at_frame'] = frame_index
                    else:
                        print(WARNING + 'Actor ' + str(actor_id) + ' did not forfeit' + ENDC)
                        exit()
                
                case Action.TAGame_PRI_TA_PlayerHistoryKey:
                    self.actors[actor_id]['player_history_key'] = actor['attribute']['PlayerHistoryKey']
                
                case Action.Engine_PlayerReplicationInfo_bTimedOut:
                    if actor['attribute']['Boolean']:
                        self.actors[actor_id]['timed_out_at_frame'] = frame_index
                    else:
                        print(WARNING + 'Actor ' + str(actor_id) + ' did not time out' + ENDC)
                        exit()
                
                case Action.Engine_ReplicatedActor_ORS_ReplicatedOwner:
                    if 'ActiveActor' not in actor['attribute']:
                        print(WARNING, 'Unknown Replicated Owner (should be ActiveActor)', ENDC, str(actor['attribute']))
                        exit()
                    else:
                        self.actors[actor_id]['parent_ids'].append(actor['attribute']['ActiveActor']['actor'])
                
                case Action.TAGame_MaxTimeWarningData_TA_EndGameWarningEpochTime:
                    #print(WARNING + 'End game warning at frame ' + str(frame_index) + ENDC)
                    self.actors[actor_id]['end_game_warning_epoch_time'] = actor['attribute']['Int64']
                
                case Action.TAGame_MaxTimeWarningData_TA_EndGameEpochTime:
                    self.actors[actor_id]['end_game_epoch_time'] = actor['attribute']['Int64']
                
                case Action.TAGame_Ball_TA_ReplicatedWorldBounceScale:
                    self.actors[actor_id]['world_bounce_scale'] = actor['attribute']['Float']
                
                case Action.TAGame_PRI_TA_bIsInSplitScreen:
                    self.actors[actor_id]['is_in_split_screen'] = actor['attribute']['Boolean']
                
                case Action.TAGame_RBActor_TA_bReplayActor:
                    self.actors[actor_id]['is_replay_actor'] = actor['attribute']['Boolean']
                
                case Action.TAGame_GameEvent_Soccar_TA_bUnlimitedTime:
                    if not actor['attribute']['Boolean']:
                        print(WARNING + 'Actor ' + str(actor_id) + ' is not in unlimited time' + ENDC)
                        exit()
                    self.actors[actor_id]['unlimited_time'] = actor['attribute']['Boolean']
                
                case Action.TAGame_CarComponent_Boost_TA_UnlimitedBoostRefCount:
                    self.actors[actor_id]['unlimited_boost_ref_count'] = actor['attribute']['Int']
                
                case Action.TAGame_VehiclePickup_TA_bNoPickup:
                    self.actors[actor_id]['no_pickup'] = actor['attribute']['Boolean']
                
                case Action.TAGame_PRI_TA_PawnType:
                    self.actors[actor_id]['pawn_type'] = actor['attribute']['Byte']

                case Action.TAGame_CarComponent_Boost_TA_RechargeDelay:
                    self.actors[actor_id]['recharge_delay'] = actor['attribute']['Float']

                case Action.TAGame_CarComponent_Boost_TA_RechargeRate:
                    self.actors[actor_id]['recharge_rate'] = actor['attribute']['Float']

                case Action.TAGame_BreakOutActor_Platform_TA_DamageState:
                    self.actors[actor_id]['damage_state'] = actor['attribute']['DamageState']
                
                case Action.TAGame_Ball_Breakout_TA_LastTeamTouch:
                    self.actors[actor_id]['last_team_touch'] = actor['attribute']['Byte']

                case Action.TAGame_PRI_TA_MatchBreakoutDamage:
                    self.actors[actor_id]['match_breakout_damage'] = actor['attribute']['Int']

                case Action.TAGame_Ball_Breakout_TA_AppliedDamage:
                    self.actors[actor_id]['applied_damage'] = actor['attribute']['AppliedDamage']
                
                case Action.TAGame_Ball_Breakout_TA_DamageIndex:
                    self.actors[actor_id]['damage_index'] = actor['attribute']['Int']

                case Action.TAGame_PRI_TA_bUsingItems:
                    self.actors[actor_id]['using_items'] = actor['attribute']['Boolean']

                case Action.TAGame_RumblePickups_TA_ConcurrentItemCount:
                    self.actors[actor_id]['concurrent_item_count'] = actor['attribute']['Int']
                
                case Action.TAGame_RumblePickups_TA_PickupInfo:
                    pickup_info = actor['attribute']['PickupInfo']
                    # IGNORE Rumble stuff
                
                case Action.TAGame_CarComponent_TA_ReplicatedActivityTime:
                    # probably Rumble stuff
                    self.actors[actor_id]['replicated_activity_time'] = actor['attribute']['Float']
                
                case Action.TAGame_SpecialPickup_Targeted_TA_Targeted:
                    # IGNORE Rumble stuff
                    pass
            
                case Action.TAGame_SpecialPickup_BallFreeze_TA_RepOrigSpeed:
                    # IGNORE Rumble stuff
                    pass

                case Action.TAGame_Car_TA_AddedCarForceMultiplier:
                    # IGNORE Rumble stuff
                    pass
            
                case Action.TAGame_Car_TA_AddedBallForceMultiplier:
                    # IGNORE Rumble stuff
                    pass
            
                case Action.TAGame_Car_TA_AddedBallForceMultiplier:
                    # IGNORE Rumble stuff
                    pass

                case Action.TAGame_GameEvent_TA_MatchTypeClass:
                    # pretty weird event
                    pass
            
                case Action.Engine_GameReplicationInfo_GameClass:
                    # pretty weird event
                    pass
            
                case Action.TAGame_GameEvent_Soccar_TA_ReplicatedStatEvent:
                    # pretty weird event
                    pass

                case Action.TAGame_GameEvent_Soccar_TA_SubRulesArchetype:
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
                    
                    exit()
        
        return event_goal


###############
# VALUE STUFF #
###############


    def calculate_stuff(self, frame_index):

        # calculate ball speed (stored in self.hist_ball_speed)
        speed = -1.0
        if self.ball_id is not None and 'linear_velocity' in self.actors[self.ball_id]:
            linear_velocity = self.actors[self.ball_id]['linear_velocity']
            if linear_velocity is not None:
                speed = (linear_velocity['x'] ** 2 + linear_velocity['y'] ** 2 + linear_velocity['z'] ** 2) ** 0.5
                self.actors[self.ball_id]['speed'] = speed
        
        # calculate angle of ball velocity (only x and y; stored in hist_ball_angles)
        angle = 0.0
        if self.ball_id is not None and 'linear_velocity' in self.actors[self.ball_id]:
            linear_velocity = self.actors[self.ball_id]['linear_velocity']
            if linear_velocity is not None:
                angle = math.atan2(linear_velocity['y'], linear_velocity['x'])
                self.actors[self.ball_id]['angle'] = angle

        # calculate car speeds (stored in self.hist_player_speeds)
        for player, car in self.player_car_pairs:
            if 'linear_velocity' in self.actors[car]:
                linear_velocity = self.actors[car]['linear_velocity']
                if linear_velocity is not None:
                    speed = (linear_velocity['x'] ** 2 + linear_velocity['y'] ** 2 + linear_velocity['z'] ** 2) ** 0.5
                    self.actors[car]['speed'] = speed
            else:
                self.actors[car]['speed'] = -1.0
        
        # calculate distance between ball and cars (stored in self.hist_player_ball_distances)
        some_big_number = 999999.0
        if self.ball_id is None:
            ball_location = {'x': some_big_number, 'y': some_big_number, 'z': some_big_number}
        else:
            ball_location = self.actors[self.ball_id]['location']
        for player, car in self.player_car_pairs:
            car_location = self.actors[car]['location']
            car_x, car_y, car_z = car_location['x'], car_location['y'], car_location['z']
            distance = some_big_number
            if ball_location is not None and car_location is not None:
                distance = ((ball_location['x'] - car_x) ** 2 + (ball_location['y'] - car_y) ** 2 + (ball_location['z'] - car_z) ** 2) ** 0.5
            self.actors[car]['distance_to_ball'] = distance
        
        
    def check_for_events(self, frame_index):
        # check for collisions between ball and cars
        # rules for collisions:
        # 1.    change in ball speed is greater than <BALL_HIT_BALL_SPEED>
        #   OR
        #       change in vector of ball velocity is greater than <BALL_HIT_BALL_ANGLE_CHANGE_THRESHOLD>
        # 2. distance between ball and car is less than <BALL_HIT_CAR_TO_BALL_DISTANCE>
        # 3. car is not demolished
        # since the change of ball speed is lagged by 1 frame, we need to check the previous frame
        if frame_index > 0:
            if self.hist_ball_speed_abs_diff[frame_index] >= BALL_HIT_BALL_SPEED or \
                self.hist_ball_linear_velocities_diff_len[frame_index] >= BALL_HIT_BALL_ANGLE_CHANGE_THRESHOLD:
                player_car_dist_tuples = []
                for player, car in self.player_car_pairs:
                    player_name = self.actors[player]['player_name']
                    if self.hist_player_ball_distances[player_name][frame_index] <= BALL_HIT_CAR_TO_BALL_DISTANCE:
                        # we have potential collision
                        # lastly, we check if the car is not demolished
                        if 'hidden_since_frame' not in self.actors[car]:
                            player_car_dist_tuples.append((player_name, player, car, self.hist_player_ball_distances[player_name][frame_index]))
                if len(player_car_dist_tuples) > 0:
                    # sort by distance
                    player_car_dist_tuples.sort(key=lambda x: x[3])
                    player_name, player, car, _ = player_car_dist_tuples[0]
                    self.handle_ball_hit(player_name, player, car, frame_index)
                              

    def prepare_snapshot(self):

        self.hist_seconds_remaining = np.full(self.num_frames, -1.0, dtype=np.int32)

        self.shots = []
        self.goals = []

        self.hist_ball_speed = np.full(self.num_frames, -1.0, dtype=np.float32)
        self.hist_ball_speed_abs_diff = np.full(self.num_frames, -1.0, dtype=np.float32)
        self.hist_ball_angles = np.full(self.num_frames, 0.0, dtype=np.float32)
        self.hist_player_speeds = {}
        self.hist_player_lineear_velocities = {}
        self.hist_player_ball_distances = {}
        self.hist_ball_linear_velocities = np.full((self.num_frames, 3), -1.0, dtype=np.float32)
        self.hist_ball_linear_velocities_diff_len = np.full(self.num_frames, -1.0, dtype=np.float32)
        self.hist_ping = {}
        

    def snapshot_values(self, frame_index):

        # seconds remaining
        self.hist_seconds_remaining[frame_index] = self.seconds_remaining

        # ping
        for player, _ in self.player_car_pairs:
            player_name = self.actors[player]['player_name']
            ping = -1
            if player_name not in self.hist_ping:
                self.hist_ping[player_name] = np.full(self.num_frames, -1.0, dtype=np.int32)
            if 'ping' in self.actors[player]:
                ping = self.actors[player]['ping']
            self.hist_ping[player_name][frame_index] = ping

        # ball speed
        if self.ball_id is not None and 'speed' in self.actors[self.ball_id]:
            self.hist_ball_speed[frame_index] = self.actors[self.get_ball()]['speed']
        if frame_index > 0:
            self.hist_ball_speed_abs_diff[frame_index] = abs(self.hist_ball_speed[frame_index] - self.hist_ball_speed[frame_index-1])

        # ball angle
        if self.ball_id is not None and 'angle' in self.actors[self.ball_id]:
            self.hist_ball_angles[frame_index] = self.actors[self.get_ball()]['angle']

        # ball linear velocity
        if self.ball_id is not None and 'linear_velocity' in self.actors[self.ball_id]:
            linear_velocity = self.actors[self.ball_id]['linear_velocity']
            if linear_velocity is not None:
                self.hist_ball_linear_velocities[frame_index, 0] = linear_velocity['x']
                self.hist_ball_linear_velocities[frame_index, 1] = linear_velocity['y']
                self.hist_ball_linear_velocities[frame_index, 2] = linear_velocity['z']
                self.hist_ball_linear_velocities_diff_len[frame_index] = np.linalg.norm(self.hist_ball_linear_velocities[frame_index] - self.hist_ball_linear_velocities[frame_index-1])

        # player linear velocities
        for player, car in self.player_car_pairs:
            player_name = self.actors[player]['player_name']
            if player_name not in self.hist_player_lineear_velocities:
                self.hist_player_lineear_velocities[player_name] = np.full((self.num_frames, 3), -1.0, dtype=np.float32)
            if 'linear_velocity' in self.actors[car]:
                linear_velocity = self.actors[car]['linear_velocity']
                if linear_velocity is not None:
                    self.hist_player_lineear_velocities[player_name][frame_index, 0] = linear_velocity['x']
                    self.hist_player_lineear_velocities[player_name][frame_index, 1] = linear_velocity['y']
                    self.hist_player_lineear_velocities[player_name][frame_index, 2] = linear_velocity['z']                

        # player speeds
        for player, car in self.player_car_pairs:
            player_name = self.actors[player]['player_name']
            if player_name not in self.hist_player_speeds:
                self.hist_player_speeds[player_name] = np.full(self.num_frames, -1.0, dtype=np.float32)
            self.hist_player_speeds[player_name][frame_index] = self.actors[car]['speed']
        
        # player to ball distances
        for player, car in self.player_car_pairs:
            player_name = self.actors[player]['player_name']
            if player_name not in self.hist_player_ball_distances:
                self.hist_player_ball_distances[player_name] = np.full(self.num_frames, -1.0, dtype=np.float32)
            self.hist_player_ball_distances[player_name][frame_index] = self.actors[car]['distance_to_ball']
        

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

        plt.title(self.seconds_to_timestamp(self.seconds_remaining) + ' - ' + str(round(self.time, 3)))
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
        ball_types = [
            Action.Archetypes_Ball_Ball_Default,
            Action.Archetypes_GameEvent_GameEvent_Basketball,
            Action.Archetypes_GameEvent_GameEvent_Hockey,
        ]
        ball = [actor_id for actor_id, actor in self.actors.items() if actor['object_id'] in ball_types]

        if len(ball) == 0:
            return None
        elif len(ball) == 1:
            return ball[0]
        else:
            print(WARNING + 'There is more than one ball' + ENDC)
            for b in ball:
                pprint(self.actors[b])
                print()
            exit()
            return ball[-1]
    
    
    def get_children(self, actor_id):
        return [actor_id for actor_id, actor in self.actors.items() if actor_id in actor['parent_ids']]


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


    def seconds_to_timestamp(self, seconds_remaining):
        # returns timestamp in format 'mm:ss'
        minutes = int(seconds_remaining // 60)
        seconds = int(seconds_remaining % 60)
        return f'{minutes:02d}:{seconds:02d}'


    def get_ping_metrics(self, player_name):
        # return min, avgerage and max ping, while skipping ping values of -1
        pings = [ping for ping in self.hist_ping[player_name] if ping != -1]
        if len(pings) == 0:
            return -1.0, -1.0, -1.0
        return min(pings), sum(pings)/len(pings), max(pings)


    def remove_false_goals(self, header_goals):
        # this function removes false goals from the list of goals
        # to do that, it iterates over the list of goals and checks if there is a corresponding
        # goal in the header_goals list. If there is, the goal is kept, otherwise it is removed.

        goal_indices_to_remove = []
        for i, goal in enumerate(self.goals):
            frame_index = goal['frame_index']
            found = False
            for header_goal in header_goals:
                # we allow a small margin of error of 10 frames
                if abs(header_goal['frame'] - frame_index) < 10:
                    found = True
                    break
            if not found:
                if self.debug_print:
                    print(f'Removing goal at frame {frame_index}')
                goal_indices_to_remove.append(i)

        # remove goals from the list of goals in reverse order to avoid index errors
        for i in reversed(goal_indices_to_remove):
            self.goals.pop(i)

        # lastly, we check if the number of goals in the header_goals list
        # is the same as the number of goals in the self.goals list
        if len(header_goals) != len(self.goals):
            print(WARNING + 'The number of goals in the header_goals list does not match the number of goals in the self.goals list' + ENDC)
            print(f'header_goals: {len(header_goals)}')
            print(f'self.goals: {len(self.goals)}')
            exit()


#################
# EVENT HANDLER #
#################


    def is_goal(self, frame_index):

        ball_id = self.get_ball()

        # 1. last goal was more than 3 seconds ago
        if len(self.goals) > 0 and frame_index - self.goals[-1]['frame_index'] < 3*30:
            return False

        # 2. ball is in goal
        # we have to distinguish between soccer and hoops
        if 'hoops' not in self.map_name.lower():
            # the check is designed in such a way that sometimes more goals are detected than there actually are
            # Later, the false goals can filtered out again relatively easily.
            # The other way around is much more difficult.
            ball_y = self.actors[ball_id]['location']['y']
            if abs(ball_y) < MAP_WALL_DISTANCE_Y:
                return False
        else:
            # hoops
            return True
    
        return True


    def handle_goal(self, frame_index):

        # check if goal was scored
        ball_id = self.get_ball()

        if not self.is_goal(frame_index):
            return
    
        # if for whatever reason the ball does not have a linear_velocity,
        # we look back in history until we find a frame where the ball had a linear_velocity
        if 'linear_velocity' not in self.actors[ball_id]:
            found = False
            for i in range(0, 3*30):
                tmp_vel = self.hist_ball_linear_velocities[frame_index-i]
                print(tmp_vel)
                if tmp_vel[0] != -1.0 and tmp_vel[1] != -1.0 and tmp_vel[2] != -1.0:
                    found = True
                    print('found', i)
                    self.actors[ball_id]['linear_velocity'] = {'x': tmp_vel[0], 'y': tmp_vel[1], 'z': tmp_vel[2]}
                    break
            if not found:
                # to avoid errors, we set the linear_velocity to 0
                self.actors[ball_id]['linear_velocity'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    
        # at this point we know that a goal was scored!
        goal = {'frame_index': frame_index, 'time': self.time}
        linear_velocity = self.actors[ball_id]['linear_velocity']
        ball_speed = math.sqrt(linear_velocity['x']**2 + linear_velocity['y']**2 + linear_velocity['z']**2)
        goal['ball_speed'] = ball_speed

        speed_kmh = round(ball_speed * UU_TO_KMH_FACTOR, 2)
        if self.actors[ball_id]['location']['y'] > 0:
            print(OKBLUE + f'Team BLUE scoread a GOAL! Ball speed: {speed_kmh} km/h' + ENDC)
            goal['team_scorer'] = '0'
        else:
            print(OKRED + f'Team ORANGE scoread a GOAL! Ball speed: {speed_kmh} km/h' + ENDC)
            goal['team_scorer'] = '1'
        
        self.goals.append(goal)


    def handle_ball_hit(self, player_name, player, car, frame_index):
        # check if event is a duplicate (shot should at least be 15 frames apart)
        if len(self.shots) > 0 and \
            frame_index - self.shots[-1]['frame_index'] < 15 and \
            self.shots[-1]['player_id'] == player:
            return
    
        # check if ball is sleeping
        if 'sleeping' in self.actors[self.ball_id] and self.actors[self.ball_id]['sleeping']:
            return
    
        shot = {'frame_index': frame_index, 'time': self.time}
        shot['player_id'] = player
        shot['player_name'] = player_name
        shot['car_id'] = car
        shot['car_location'] = self.actors[car]['location']
        shot['car_linear_velocity'] = self.actors[car]['linear_velocity']
        shot['ball_id'] = self.ball_id
        shot['ball_location'] = self.actors[self.ball_id]['location']
        shot['ball_linear_velocity'] = self.actors[self.ball_id]['linear_velocity']
        self.shots.append(shot)
        print(OKGREEN + f'Player {player_name} hit the ball' + ENDC)


#########
# STATS #
#########


    def get_stats(self, properties):

        # prepare stats dict
        stats = {}

        # general stuff
        stats['datetime'] = properties['Date']
        stats['team_size'] = properties['TeamSize']
        stats['scores'] = {}
        stats['scores']['Blue'] = 0 if 'Team0Score' not in properties else properties['Team0Score']
        stats['scores']['Orange'] = 0 if 'Team1Score' not in properties else properties['Team1Score']
        stats['replay_name'] = None if 'replay_name' not in properties else properties['ReplayName']
        stats['replay_id'] = properties['Id']
        stats['map_name'] = properties['MapName']
        stats['num_frames'] = properties['NumFrames']
        
        # players
        stats['players'] = []
        player_stats = properties['PlayerStats']
        for player_id, car_id in self.player_car_pairs:

            player = {}
            player['player_name'] = self.actors[player_id]['player_name'] 

            # try to extract player stats from header
            player_stat = [p for p in player_stats if p['Name'] == self.actors[player_id]['player_name']]
            if len(player_stat) > 0:
                player_stat = player_stat[0]
                # general stuff
                
                player['team'] = 'Blue' if player_stat['Team'] == 0 else 'Orange'
                player['is_bot'] = player_stat['bBot']
                match_values = {}    
                match_values['shots'] = player_stat['Shots']
                match_values['goals'] = player_stat['Goals']
                match_values['saves'] = player_stat['Saves']
                match_values['assists'] = player_stat['Assists']
                match_values['score'] = player_stat['Score']
                player['match_values'] = match_values

            # if not available, use data from replay
            else:

                player_object = self.actors[player_id]
                car_object = self.actors[car_id]

                player['team'] = 'Blue' if car_object['team_paint']['team'] == 0 else 'Orange'
                player['is_bot'] = True if 'is_bot' in player_object else False
                match_values = {}
                values = ['match_shots', 'match_goals', 'match_saves', 'match_assists', 'match_score']
                for value in values:
                    if value in player_object:
                        match_values[value.split('_')[1]] = player_object[value]
                    else:
                        match_values[value.split('_')[1]] = 0
                player['match_values'] = match_values
            
            # if player is NO BOT:
            if not player['is_bot']:

                # ping
                min_, avg_, max_ = self.get_ping_metrics(player['player_name'])
                player['ping'] = {'min': min_, 'avg': avg_, 'max': max_}

                # platform
                if 'unique_id' not in self.actors[player_id]:
                    player['platform'] = None
                    player['platform_id'] = None
                else:
                    player['platform'] = list(self.actors[player_id]['unique_id']['remote_id'])[0]
                    match player['platform']:
                        case 'Epic':
                            player['platform_id'] = self.actors[player_id]['unique_id']['remote_id'][player['platform']]
                        case 'Xbox':
                            player['platform_id'] = self.actors[player_id]['unique_id']['remote_id'][player['platform']]
                        case 'PlayStation':
                            player['platform_id'] = self.actors[player_id]['unique_id']['remote_id'][player['platform']]['online_id']
                
                # things that might not be set
                unkown_keys = ['mmr', 'title']
                for key in unkown_keys:
                    if key in self.actors[player_id]:
                        player[key] = self.actors[player_id][key]
                    else:
                        player[key] = None
            
            stats['players'].append(player)
        
        if 'Goals' not in properties:
            properties['Goals'] = []
            print(WARNING + 'No goals in header' + ENDC)

        # GOALS
        # check if number of goals in properties is the same as in the goals list
        if len(self.goals) != len(properties['Goals']):
            if len(properties['Goals']) > len(self.goals):
                print(WARNING + 'More goals in header than in replay' + ENDC)
                print(len(properties['Goals']), len(self.goals))
                pprint(properties['Goals'])
                print()
                pprint(self.goals)
                exit()
            self.remove_false_goals(properties['Goals'])

        stats['goals'] = []
        for i in range(len(self.goals)):
            goal = {}
            goal['frame_index'] = self.goals[i]['frame_index']
            goal['player_name'] = properties['Goals'][i]['PlayerName']
            goal['team'] = 'Blue' if properties['Goals'][i]['PlayerTeam'] == 0 else 'Orange'
            goal['ball_speed_kmh'] = self.goals[i]['ball_speed'] * UU_TO_KMH_FACTOR
            goal['timestamp'] = self.seconds_to_timestamp(self.hist_seconds_remaining[goal['frame_index']])
            stats['goals'].append(goal)
            
        # debug stuff
        stats['debug'] = {}
        stats['debug']['ball_speed'] = self.hist_ball_speed
        stats['debug']['ball_angle'] = self.hist_ball_angles
        stats['debug']['ball_linear_velocity'] = self.hist_ball_linear_velocities
        stats['debug']['ball_linear_velocity_diff_len'] = self.hist_ball_linear_velocities_diff_len
        stats['debug']['player_speeds'] = self.hist_player_speeds
        stats['debug']['player_distances'] = self.hist_player_ball_distances

        # goals and shots
        stats['shots'] = self.shots

        return stats

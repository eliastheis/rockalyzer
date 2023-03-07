from pprint import pprint
from console_colors import *

class Game:

    def __init__(self, object_lookup):
        self.object_lookup = object_lookup
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
        self.update_actors(frame['updated_actors'])
        

    

    def render(self):
        pass
    

    def delete_actors(self, actors):
        for actor in actors:
            actor_id = actor
            del self.actors[actor_id]


    def add_actors(self, actors):
        for actor in actors:
            actor_id = actor['actor_id']
            object_id = actor['object_id']

            match object_id:

                case 143: # Archetypes.Car.Car_Default
                    # we take the position and rotation from the initial_trajectory and add it to the actor
                    initial_trajectory = actor['initial_trajectory']
                    actor = actor | initial_trajectory
                    del actor['initial_trajectory']

            self.actors[actor_id] = actor


    def update_actors(self, actors):
        for actor in actors:
            actor_id = actor['actor_id']
            object_name = self.object_lookup[actor['object_id']]


            match actor['object_id']:

                case 116: # TAGame.RBActor_TA:ReplicatedRBState (ReplicatedRigidBodyState)
                    rigid_body_state = actor['attribute']['RigidBody']
                    #for key in rigid_body_state:
                    #    self.actors[actor_id][key] = rigid_body_state[key]
                    self.actors[actor_id].update(rigid_body_state)

                case 16: # Engine.Actor:RemoteRole
                    self.actors[actor_id]['remote_role'] = actor['attribute']['Enum']

                case 24: # TAGame.CarComponent_TA:ReplicatedActive
                    self.actors[actor_id]['active'] = actor['attribute']['Byte']

                case 28: # TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount
                    self.actors[actor_id]['boost'] = actor['attribute']['Byte']
                
                case 86: # TAGame.GameEvent_Soccar_TA:SecondsRemaining
                    self.actors[actor_id]['seconds_remaining'] = actor['attribute']['Int']

                case 123: # TAGame.Vehicle_TA:ReplicatedSteer
                    self.actors[actor_id]['steer'] = actor['attribute']['Byte']
                
                case 124: # TAGame.Vehicle_TA:ReplicatedThrottle
                    self.actors[actor_id]['throttle'] = actor['attribute']['Byte']
                
                case 126: # TAGame.Vehicle_TA:bReplicatedHandbrake
                    self.actors[actor_id]['handbranke'] = actor['attribute']['Boolean']
                
                case 156: # TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera
                    self.actors[actor_id]['secondary_camera'] = actor['attribute']['Boolean']
                
                case 186: # Engine.PlayerReplicationInfo:Ping
                    self.actors[actor_id]['ping'] = actor['attribute']['Byte']
                
                case 234: # TAGame.PRI_TA:MatchScore
                    self.actors[actor_id]['score'] = actor['attribute']['Int']
                
                case _:


                    # this prints any other action that is not handled above
                    print(OKCYAN + f'Update Actor {actor_id} ({object_name} ({actor["object_id"]}))' + ENDC)
                    pprint(self.actors[actor_id])
                    print()
                    print(' ' + str(actor['attribute']))
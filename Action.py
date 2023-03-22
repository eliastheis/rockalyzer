class Action:

    Engine_Actor_RemoteRole = -1
    Engine_Actor_DrawScale = -1
    TAGame_CarComponent_TA_Vehicle = -1
    TAGame_CarComponent_TA_ReplicatedActive = -1
    TAGame_CarComponent_Boost_TA_ReplicatedBoostAmount = -1
    TAGame_GameEvent_TA_ReplicatedRoundCountDownNumber = -1
    TAGame_GameEvent_TA_ReplicatedGameStateTimeRemaining = -1
    TAGame_GameEvent_TA_ReplicatedStateName = -1
    TAGame_GameEvent_TA_BotSkill = -1
    TAGame_GameEvent_TA_bHasLeaveMatchPenalty = -1
    TAGame_GameEvent_Team_TA_MaxTeamSize = -1
    TAGame_GameEvent_Soccar_TA_RoundNum = -1
    TAGame_GameEvent_Soccar_TA_bBallHasBeenHit = -1
    TAGame_GameEvent_Soccar_TA_SecondsRemaining = -1
    Engine_Pawn_PlayerReplicationInfo = -1
    TAGame_RBActor_TA_ReplicatedRBState = -1
    TAGame_Vehicle_TA_ReplicatedSteer = -1
    TAGame_Vehicle_TA_ReplicatedThrottle = -1
    TAGame_Vehicle_TA_bReplicatedHandbrake = -1
    TAGame_Vehicle_TA_bDriving = -1
    TAGame_Car_TA_RumblePickups = -1
    TAGame_Car_TA_TeamPaint = -1
    TAGame_CameraSettingsActor_TA_CameraYaw = -1
    TAGame_CameraSettingsActor_TA_CameraPitch = -1
    TAGame_CameraSettingsActor_TA_bMouseCameraToggleEnabled = -1
    TAGame_CameraSettingsActor_TA_bUsingSwivel = -1
    TAGame_CameraSettingsActor_TA_bUsingBehindView = -1
    TAGame_CameraSettingsActor_TA_ProfileSettings = -1
    TAGame_CameraSettingsActor_TA_bUsingSecondaryCamera = -1
    Engine_PlayerReplicationInfo_UniqueId = -1
    Engine_PlayerReplicationInfo_Team = -1
    Engine_PlayerReplicationInfo_PlayerID = -1
    Engine_PlayerReplicationInfo_PlayerName = -1
    Engine_PlayerReplicationInfo_Ping = -1
    TAGame_PRI_TA_CurrentVoiceRoom = -1
    TAGame_PRI_TA_SpectatorShortcut = -1
    TAGame_PRI_TA_SteeringSensitivity = -1
    TAGame_PRI_TA_Title = -1
    TAGame_PRI_TA_PartyLeader = -1
    TAGame_PRI_TA_ClientLoadoutsOnline = -1
    TAGame_PRI_TA_ClientLoadouts = -1
    TAGame_PRI_TA_ReplicatedGameEvent = -1
    TAGame_PRI_TA_PlayerHistoryValid = -1
    TAGame_PRI_TA_MatchScore = -1
    TAGame_Ball_TA_HitTeamNum = -1
    TAGame_CarComponent_Dodge_TA_DodgeTorque = -1
    Engine_GameReplicationInfo_ServerName = -1
    ProjectX_GRI_X_MatchGuid = -1
    ProjectX_GRI_X_bGameStarted = -1
    ProjectX_GRI_X_GameServerID = -1
    ProjectX_GRI_X_Reservations = -1
    ProjectX_GRI_X_ReplicatedServerRegion = -1
    ProjectX_GRI_X_ReplicatedGamePlaylist = -1
    TAGame_Team_TA_GameEvent = -1
    TAGame_VehiclePickup_TA_NewReplicatedPickupData = -1
    Archetypes_Car_Car_Default = -1 # car
    TAGame_Default__PRI_TA = -1 # player
    TAGame_PRI_TA_PersistentCamera = -1
    TAGame_CameraSettingsActor_TA_PRI = -1
    TAGame_Ball_TA_GameEvent = -1


    @staticmethod
    def set_values(objects):
        for i, obj in enumerate(objects):
            match obj:
                case 'Engine.Actor:RemoteRole':
                    Action.Engine_Actor_RemoteRole = i
                case 'Engine.Actor:DrawScale':
                    Action.Engine_Actor_DrawScale = i
                case 'TAGame.CarComponent_TA:Vehicle':
                    Action.TAGame_CarComponent_TA_Vehicle = i
                case 'TAGame.CarComponent_TA:ReplicatedActive':
                    Action.TAGame_CarComponent_TA_ReplicatedActive = i
                case 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount':
                    Action.TAGame_CarComponent_Boost_TA_ReplicatedBoostAmount = i
                case 'TAGame.GameEvent_TA:ReplicatedRoundCountDownNumber':
                    Action.TAGame_GameEvent_TA_ReplicatedRoundCountDownNumber = i
                case 'TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining':
                    Action.TAGame_GameEvent_TA_ReplicatedGameStateTimeRemaining = i
                case 'TAGame.GameEvent_TA:ReplicatedStateName':
                    Action.TAGame_GameEvent_TA_ReplicatedStateName = i
                case 'TAGame.GameEvent_TA:BotSkill':
                    Action.TAGame_GameEvent_TA_BotSkill = i
                case 'TAGame.GameEvent_TA:bHasLeaveMatchPenalty':
                    Action.TAGame_GameEvent_TA_bHasLeaveMatchPenalty = i
                case 'TAGame.GameEvent_Team_TA:MaxTeamSize':
                    Action.TAGame_GameEvent_Team_TA_MaxTeamSize = i
                case 'TAGame.GameEvent_Soccar_TA:RoundNum':
                    Action.TAGame_GameEvent_Soccar_TA_RoundNum = i
                case 'TAGame.GameEvent_Soccar_TA:bBallHasBeenHit':
                    Action.TAGame_GameEvent_Soccar_TA_bBallHasBeenHit = i
                case 'TAGame.GameEvent_Soccar_TA:SecondsRemaining':
                    Action.TAGame_GameEvent_Soccar_TA_SecondsRemaining = i
                case 'Engine.Pawn:PlayerReplicationInfo':
                    Action.Engine_Pawn_PlayerReplicationInfo = i
                case 'TAGame.RBActor_TA:ReplicatedRBState':
                    Action.TAGame_RBActor_TA_ReplicatedRBState = i
                case 'TAGame.Vehicle_TA:ReplicatedSteer':
                    Action.TAGame_Vehicle_TA_ReplicatedSteer = i
                case 'TAGame.Vehicle_TA:ReplicatedThrottle':
                    Action.TAGame_Vehicle_TA_ReplicatedThrottle = i
                case 'TAGame.Vehicle_TA:bReplicatedHandbrake':
                    Action.TAGame_Vehicle_TA_bReplicatedHandbrake = i
                case 'TAGame.Vehicle_TA:bDriving':
                    Action.TAGame_Vehicle_TA_bDriving = i
                case 'TAGame.Car_TA:RumblePickups':
                    Action.TAGame_Car_TA_RumblePickups = i
                case 'TAGame.Car_TA:TeamPaint':
                    Action.TAGame_Car_TA_TeamPaint = i
                case 'TAGame.CameraSettingsActor_TA:CameraYaw':
                    Action.TAGame_CameraSettingsActor_TA_CameraYaw = i
                case 'TAGame.CameraSettingsActor_TA:CameraPitch':
                    Action.TAGame_CameraSettingsActor_TA_CameraPitch = i
                case 'TAGame.CameraSettingsActor_TA:bMouseCameraToggleEnabled':
                    Action.TAGame_CameraSettingsActor_TA_bMouseCameraToggleEnabled = i
                case 'TAGame.CameraSettingsActor_TA:bUsingSwivel':
                    Action.TAGame_CameraSettingsActor_TA_bUsingSwivel = i
                case 'TAGame.CameraSettingsActor_TA:bUsingBehindView':
                    Action.TAGame_CameraSettingsActor_TA_bUsingBehindView = i
                case 'TAGame.CameraSettingsActor_TA:ProfileSettings':
                    Action.TAGame_CameraSettingsActor_TA_ProfileSettings = i
                case 'TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera':
                    Action.TAGame_CameraSettingsActor_TA_bUsingSecondaryCamera = i
                case 'Engine.PlayerReplicationInfo:UniqueId':
                    Action.Engine_PlayerReplicationInfo_UniqueId = i
                case 'Engine.PlayerReplicationInfo:Team':
                    Action.Engine_PlayerReplicationInfo_Team = i
                case 'Engine.PlayerReplicationInfo:PlayerID':
                    Action.Engine_PlayerReplicationInfo_PlayerID = i
                case 'Engine.PlayerReplicationInfo:PlayerName':
                    Action.Engine_PlayerReplicationInfo_PlayerName = i
                case 'Engine.PlayerReplicationInfo:Ping':
                    Action.Engine_PlayerReplicationInfo_Ping = i
                case 'TAGame.PRI_TA:CurrentVoiceRoom':
                    Action.TAGame_PRI_TA_CurrentVoiceRoom = i
                case 'TAGame.PRI_TA:SpectatorShortcut':
                    Action.TAGame_PRI_TA_SpectatorShortcut = i
                case 'TAGame.PRI_TA:SteeringSensitivity':
                    Action.TAGame_PRI_TA_SteeringSensitivity = i
                case 'TAGame.PRI_TA:Title':
                    Action.TAGame_PRI_TA_Title = i
                case 'TAGame.PRI_TA:PartyLeader':
                    Action.TAGame_PRI_TA_PartyLeader = i
                case 'TAGame.PRI_TA:ClientLoadoutsOnline':
                    Action.TAGame_PRI_TA_ClientLoadoutsOnline = i
                case 'TAGame.PRI_TA:ClientLoadouts':
                    Action.TAGame_PRI_TA_ClientLoadouts = i
                case 'TAGame.PRI_TA:ReplicatedGameEvent':
                    Action.TAGame_PRI_TA_ReplicatedGameEvent = i
                case 'TAGame.PRI_TA:PlayerHistoryValid':
                    Action.TAGame_PRI_TA_PlayerHistoryValid = i
                case 'TAGame.PRI_TA:MatchScore':
                    Action.TAGame_PRI_TA_MatchScore = i
                case 'TAGame.Ball_TA:HitTeamNum':
                    Action.TAGame_Ball_TA_HitTeamNum = i
                case 'TAGame.CarComponent_Dodge_TA:DodgeTorque':
                    Action.TAGame_CarComponent_Dodge_TA_DodgeTorque = i
                case 'Engine.GameReplicationInfo:ServerName':
                    Action.Engine_GameReplicationInfo_ServerName = i
                case 'ProjectX.GRI_X:MatchGuid':
                    Action.ProjectX_GRI_X_MatchGuid = i
                case 'ProjectX.GRI_X:bGameStarted':
                    Action.ProjectX_GRI_X_bGameStarted = i
                case 'ProjectX.GRI_X:GameServerID':
                    Action.ProjectX_GRI_X_GameServerID = i
                case 'ProjectX.GRI_X:Reservations':
                    Action.ProjectX_GRI_X_Reservations = i
                case 'ProjectX.GRI_X:ReplicatedServerRegion':
                    Action.ProjectX_GRI_X_ReplicatedServerRegion = i
                case 'ProjectX.GRI_X:ReplicatedGamePlaylist':
                    Action.ProjectX_GRI_X_ReplicatedGamePlaylist = i
                case 'TAGame.Team_TA:GameEvent':
                    Action.TAGame_Team_TA_GameEvent = i
                case 'TAGame.VehiclePickup_TA:NewReplicatedPickupData':
                    Action.TAGame_VehiclePickup_TA_NewReplicatedPickupData = i
                case 'Archetypes.Car.Car_Default':
                    Action.Archetypes_Car_Car_Default = i
                case 'TAGame.Default__PRI_TA':
                    Action.TAGame_Default__PRI_TA = i
                case 'Archetypes.GameEvent.GameEvent_Soccar':
                    Action.Archetypes_GameEvent_GameEvent_Soccar = i
                case 'TAGame.PRI_TA:PersistentCamera':
                    Action.TAGame_PRI_TA_PersistentCamera = i
                case 'TAGame.CameraSettingsActor_TA:PRI':
                    Action.TAGame_CameraSettingsActor_TA_PRI = i
                case 'TAGame.Ball_TA:GameEvent':
                    Action.TAGame_Ball_TA_GameEvent = i

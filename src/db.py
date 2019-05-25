from src.models import ProfileModel, MissionModel, WaypointModel, db
from src.objects import MSN, Wp
from src.logger import get_logger
from LatLon23 import LatLon, Latitude, Longitude


class DatabaseInterface:
    def __init__(self, db_name):
        self.logger = get_logger("db")
        db.init(db_name)
        db.connect()
        db.create_tables([ProfileModel, MissionModel, WaypointModel])
        self.logger.debug("Connected to database")

    def get_profile(self, profilename):
        profile = ProfileModel.get(ProfileModel.name == profilename)
        msns = [MSN(LatLon(Latitude(mission.latitude), Longitude(mission.longitude)),
                    elevation=mission.elevation, name=mission.name) for mission in profile.missions]

        wps = [Wp(LatLon(Latitude(waypoint.latitude), Longitude(waypoint.longitude)),
                  elevation=waypoint.elevation, name=waypoint.name) for waypoint in profile.waypoints]

        self.logger.debug(f"Fetched {profilename} from DB, with {len(msns)} missions and {len(wps)} waypoints")
        return msns, wps

    def save_profile(self, profileinstance):
        missionmodel_instances = list()
        waypointmodel_instances = list()

        profile, _ = ProfileModel.get_or_create(name=profileinstance.profilename, aircraft=profileinstance.aircraft)
        for mission in profile.missions:
            mission.delete_instance()

        for waypoint in profile.waypoints:
            waypoint.delete_instance()

        self.logger.debug(f"Attempting to save profile {profileinstance.profilename}")
        for mission in profileinstance.missions:
            missionmodel_instance = MissionModel.create(name=mission.name,
                                                        latitude=mission.position.lat.decimal_degree,
                                                        longitude=mission.position.lon.decimal_degree,
                                                        elevation=mission.elevation,
                                                        number=mission.number,
                                                        profile=profile)
            missionmodel_instances.append(missionmodel_instance)

        for waypoint in profileinstance.waypoints:
            waypointmodel_instance = WaypointModel.create(name=waypoint.name,
                                                          latitude=waypoint.position.lat.decimal_degree,
                                                          longitude=waypoint.position.lon.decimal_degree,
                                                          elevation=waypoint.elevation,
                                                          profile=profile)
            waypointmodel_instances.append(waypointmodel_instance)

    @staticmethod
    def delete_profile(profilename):
        profile = ProfileModel.get(name=profilename)
        for mission in profile.missions:
            mission.delete_instance()

        for waypoint in profile.waypoints:
            waypoint.delete_instance()

        profile.delete_instance()

    @staticmethod
    def get_profile_names():
        return [profile.name for profile in ProfileModel.select()]

    @staticmethod
    def close():
        db.close()

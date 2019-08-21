import uuid
import xmltodict
import ast
import json

from ServerHandlers import ControlServerHandler
from fs import open_fs

class deGardenaWebservice:
    def __init__(self, fileSystem, controlServer):
        self.fileSystem = fileSystem
        self.controlServer = controlServer
        self.gatewayId = self.__get_gatewayId()
        self.mapping = self.__readMapping()
    
    def __get_gatewayId(self):
        gatewayId = None
        for gwId_dir in self.fileSystem.listdir("/gateway/"):
            gatewayId = gwId_dir
        return gatewayId
    
    def __dir_name(self, full_dir):
        return full_dir.split("/")[-1]

    def __getXmlDict(self, path):
        return xmltodict.parse(self.fileSystem.readtext(path))
    
    def __readMapping(self):
        map = []
        mapFs = open_fs('./deGardenServer/mapping/')
        for map_file in mapFs.listdir("/"):
            map_obj = open(map_file, 'r')
            entry = json.load(map_obj)
            map.append(entry)
        return map

            


    def auth_token(self, username, password):
        token = {
            "data": {
                "id": str(uuid.uuid4()),
                "type": "token",
                "attributes": {
                    "expires_in": 863999,
                    "refresh_token": str(uuid.uuid4()),
                    "provider": "husqvarna",
                    "user_id": str(uuid.uuid4()),
                    "scope": "iam:read iam:write"
                }
            }
        }
        return token
    def session(self, username, password):
        token = { "sessions": {
                "token": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4())
        } }
        return token

    def location(self, locationId):
        location = {
            "id": locationId,
            "name": "deGarden",
            "authorized_at": "TODO", #2019-05-11T21:24:48.429Z
            "authorized_user_ids": [],
            "device_flashing": {},
            "devices": self.__device_ids(),
            "geo_position": {
                "latitude": 48.3568,
                "longitude": 9.9444913,
                "address": "Hans-Lorenser-Straße 40, Deutschland", #Gardena HQ
                "gateway_time_zone": "Europe/Berlin",
                "gateway_time_zone_offset": 7200000,
                "id": self.gatewayId,
                "sunrise": "05:21",
                "sunset": "21:39",
                "time_zone": "Europe/Berlin",
                "time_zone_offset": 7200000
            },
            "zones": []
        }
        return location

    def locations(self):
        locations = []
        locations.append(self.location(self.gatewayId))
        return { "locations": locations }

    def __device_ids(self):
        devices = []
        for id_dir in self.fileSystem.listdir("/network/{}/device/".format(self.gatewayId)):
            devices.append(id_dir)
        return devices

    def device(self, deviceId):
        path = "/network/{}/device/{}/data.xml".format(self.gatewayId, deviceId)
        deviceInfo = self.__getXmlDict(path)["device"]

        device = {
            "id": deviceId,
            "name": deviceInfo["name"],
            "description": None,
            "category": "",
            "abilities": self.services(deviceId),
            "configuration_synchronized": True,
            "configuration_synchronized_v2": {
                "value": True,
                "timestamp": "" #2019-05-11T21:24:49.031Z
            },
            "configuration_update": {
                "status": "synchronized",
                "timestamp": "" #2019-05-11T21:24:49.031Z
            },
            "constraints": [],
            "device_state": "ok",
            "property_constraints": [],
            "scheduled_events": [],
            "scheduling_wizard_mowing": None,
            "settings": [],
            "status_report_history": [],
            "zones": []
        }
        return device

    def devices(self):
        devices = []
        for id in self.__device_ids():
            devices.append(self.device(id))
        return { "devices": devices }

    def __properties_device_info(self, deviceId):
        deviceXml = self.__getXmlDict("/network/{}/device/{}/data.xml".format(self.gatewayId, deviceId))["device"]
        properties = []

        for name, value in deviceXml.items():
            if name[0] != "@":
                prop = self.__fill_property(
                    deviceId,  #hack
                    name,
                    value,
                    False
                )
                properties.append(prop)
        return properties

    def __fill_service(self, serviceId, name, type, properties):
        service = {
            "id": serviceId, 
            "name": name,
            "type": type,
            "properties": properties
        }
        return service

    def __fill_property(self, propertyId, name, value, writable):
        #realVal = value
        try:
            value = ast.literal_eval(value) #convert number strings to ints/floats
        except:
            pass

        prop = {
                "id": propertyId,
                "name": name,
                "value": value,
                #"valueUntouched": realVal, #just for testing
                "writeable": writable,
                "supported_values": []
        }
        return prop
    
    def __property(self, deviceId, propertyId):
        path = "/network/{}/device/{}/service/{}/".format(self.gatewayId, deviceId, propertyId)
        service = self.__getXmlDict(path + "data.xml")["service"]

        valueId = self.fileSystem.listdir(path+"value/")[0] #May multiple values (type Report / Control)
        value = self.__getXmlDict(path+"value/"+valueId+"/data.xml")["value"]

        prop = self.__fill_property(propertyId, service["name"], value["data"], ("w" in service["permission"]))
        return prop

    def services(self, deviceId):    
        services = []
        services.append(
            self.__fill_service(deviceId, #hack
                "device_info", "device_info", 
                self.__properties_device_info(deviceId)
            )
        )
        properties = []

        for id_dir in self.fileSystem.listdir("/network/{}/device/{}/service/".format(self.gatewayId, deviceId)):
            properties.append(self.__property(deviceId, id_dir))

        #TODO: Filter properties and group them into the right services +rename
        services.append(self.__fill_service(
            deviceId,
            "all",
            "all",
            properties
        ))

        return services
        
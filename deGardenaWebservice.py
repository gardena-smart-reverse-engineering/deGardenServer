import uuid

class deGardenaWebservice:
    def __init__(self, fileSystem):
        self.fileSystem = fileSystem
        self.gatewayId = self.__get_gatewayId()
    
    def __get_gatewayId(self):
        gatewayId = None
        for gwId_dir in self.fileSystem.listdir("/gateway/"):
            gatewayId = gwId_dir
        return gatewayId
    
    def __dir_name(self, full_dir):
        return full_dir.split("/")[-1]

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

    def device(self, deviceId):
        device = {
            "id": deviceId,
            "name": "TODO",
            "description": "TODO",
            "category": "",
            "configuration_synchronized": True,
            "configuration_synchronized_v2": {
                "value": True,
                "timestamp": ""
            },
            "abilities": self.services(deviceId),
            "scheduled_events": [],
            "settings": []
        }
        return device

    def devices(self):
        devices = []
        for id_dir in self.fileSystem.listdir("/network/{}/device/".format(self.gatewayId)):
            devices.append(self.device(id_dir))
        return { "devices": devices }

    def service(self, deviceId, serviceId):
        
        service = {
            "id": serviceId,
            "name": "TODO",
            "type": "TODO",
            "properties": [{
                "id": "f9667bc2-b5e2-11e5-b6a5-100000000000",
                "name": "TODO",
                "value": "TODO",
                "writeable": False,
                "supported_values": []
            }]
        }
        return service

    def __service_device_info(self, deviceId):
        #deviceXml = self.fileSystem.readtext("/network/{}/device/{}/data.xml".format(self.gatewayId, deviceId))
        service = {
            "id": deviceId, #hack
            "name": "device_info",
            "type": "device_info",
            "properties": [{
                "id": deviceId, #hack
                "name": "TODO",
                "value": "TODO",
                "writeable": False,
                "supported_values": [] #tags from deviceXml
            }]
        }
        return service
    
    def services(self, deviceId):    
        services = []
        services.append(self.__service_device_info(deviceId))
        for id_dir in self.fileSystem.listdir("/network/{}/device/{}/service/".format(self.gatewayId, deviceId)):
            services.append(self.service(deviceId, id_dir))
        return services
        
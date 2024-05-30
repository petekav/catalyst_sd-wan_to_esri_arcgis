print("\nPull router status from Catalyst SD-WAN Manager (via REST API) and publish as MQTT, to be consumed by ESRI Velocity.")
print("By Pete Kavanagh - pkavanag@cisco.com\n")

# Import required libraries etc.
import os
import json
import urllib3
import paho.mqtt.client as paho
from classes import Csm, MqttBroker

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Open up login.json file in the env folder (N.B. not synced via Git!)
script_dir = os.path.dirname(__file__)
rel_path = "../env/login.json"
abs_file_path = os.path.join(script_dir, rel_path)
#print(abs_file_path)
with open(abs_file_path) as file:
    target = json.load(file)


# Extract url, username and password from JSON, and make available as variables, by creating objects from the classes
mycsm = Csm(target["csm"]["url"],target["csm"]["username"],target["csm"]["password"])
#print(mycsm)
mymqttbroker = MqttBroker(target["mqttbroker"]["url"],target["mqttbroker"]["port"],target["mqttbroker"]["tls"],target["mqttbroker"]["username"],target["mqttbroker"]["password"])
#print(mymqttbroker)


# Setup MQTT
mqttclient = paho.Client(client_id="Data from Catalyst SD-WAN into ESRI map", userdata=None, protocol=paho.MQTTv5)
#print(mymqttbroker.tls)
if (mymqttbroker.tls == True) :
    mqttclient.tls_set()

mqttclient.username_pw_set(mymqttbroker.username, mymqttbroker.password)
mqttclient.connect(mymqttbroker.url, int(mymqttbroker.port))
#print(mqttclient.is_connected())

# Start Catalyst SD-WAN SDK session, inc. Personality to allowing filtering down to WAN Edge role.
from catalystwan.session import create_manager_session
from catalystwan.utils.personality import Personality
from catalystwan.utils.reachability import Reachability
from catalystwan.utils.dashboard import HealthColor
with create_manager_session(url=mycsm.url, username=mycsm.username, password=mycsm.password) as session:
    alldevices = session.api.dashboard.get_devices_health()
    routers = alldevices.devices.filter(personality=Personality.EDGE)
    router_counter = 0
    reachable_router_counter = 0
    healthy_router_counter = 0
    processed_routers = {}
    for router in routers:
        print(router)
        router_name = router.name
        router_reachable = False
        router_health = ""
        router_latitude = 0.0
        router_longitude = 0.0
        #print(type(router_latitude))
        # If router is reachable by CSM then set this flag
        if (router.reachability == Reachability.REACHABLE):
            reachable_router_counter += 1
            router_reachable = True
        
        # Set value for health colour
        if (router.health == HealthColor.GREEN):
            healthy_router_counter += 1
            router_health = "Green"
        elif (router.health == HealthColor.YELLOW):
            router_health = "Yellow"
        elif (router.health == HealthColor.RED):
            router_health = "Red"
        else:
            router_health = "Error getting router health"
            print(f"ERROR: Router {router.name} did not return a valid health colour!")
        
        router_counter += 1
        processed_routers.update()

        # Set Lat/Lon
        router_latitude = router.latitude
        router_longitude = router.longitude
        print(f"Lat: {router_latitude}, Long: {router_longitude}\n")

        # Add all the info together and publish to MQTT broker
        processed_router = dict(name = router_name, reachable = router_reachable, health = router_health, latitude = router_latitude, longitude = router_longitude)
        print(processed_router)
        mqttclient.publish("catalystsdwanmanager/"+mycsm.url, payload=json.dumps(processed_router), qos=1)

    print(f"\n{router_counter} routers in total, of which {reachable_router_counter} are reachable.")
    #print(alldevices.devices.filter(personality=Personality.EDGE))
    #print(routers.total_devices)
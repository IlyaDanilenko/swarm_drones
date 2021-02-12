import subprocess


networksNames = ["Geoscan-Orange", "Geoscan-White", "Geoscan-Blue"]
# subprocess.call("echo connect", shell=True)

def connectToWifi(networkId):
    global networksNames
    print("connecting to ", networkId)
    subprocess.Popen(["sh","bashscrpt/enableNetworkManager.sh"],stdout=subprocess.PIPE).communicate()
    subprocess.Popen("nmcli device wifi connect \"{}\" password geoscan123 name \"{}\"".format(networksNames[networkId],networksNames[networkId]), shell=True).communicate()

def enableHotspot():
    subprocess.call("sh bashscrpt/enableNetworkManagerHotspot.sh", shell=True)

for i in networksNames:
    print(i)

print("connect to white")
connectToWifi(1)
# print("start enable hotspot script")
# enableHotspot()


# Creation date : 23/07/22
# Project : Client SNMP - IPMI
# Application for retrieve SNMP data by oids, and data from IPMI sensors
# Last update : 17/08/22

import subprocess
import json
import requests
from pysnmp.entity.rfc3413.oneliner import cmdgen
import sys

# Variable declaration
snmp_data = []
ipmi_data = []
error_data = []

choice = int(input("If you want modify the conf.json , press 1, else, press other number : "))
if choice == 1:
    # Json config by user inputs
    new_ip_snmp = input("Input SNMP host : ")
    new_community = input("Input SNMP community name : ")
    new_port = input("Input SNMP port : ")
    new_oid = input("Input OID for send data : ")
    new_ip_ipmi = input("Input IPMI host : ")
    new_user = input("Input user name : ")
    new_password = input("Input user password : ")
    new_metric1 = input("Input metric1 , choose your parameter 1 : ")
    new_metric2 = input("Input metric2 , choose your parameter 2 : ")

    # Update conf.json with inputs
    with open('conf.json', 'r+') as f:
        data = json.load(f)
        data["SNMP"]["srv1"]["ip"] = new_ip_snmp
        data["SNMP"]["srv1"]["port"] = new_port
        data["SNMP"]["srv1"]["community"] = new_community
        data["SNMP"]["srv1"]["metrics"]["metric1"] = new_oid
        data["IPMI"]["srv1"]["ip"] = new_ip_ipmi
        data["IPMI"]["srv1"]["user"] = new_user
        data["IPMI"]["srv1"]["password"] = new_password
        data["IPMI"]["srv1"]["metrics"]["metric1"] = new_metric1
        data["IPMI"]["srv1"]["metrics"]["metric2"] = new_metric2

        # Add new datas to conf.json and delete initials datas
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        print("The configuration file was modified correctly.")
else:
    print("The configuration file was not modified")


# Request SNMP allowing connection to the server's SNMP
# Retrieves the values of the oids chosen in the conf.json
def snmp_request(server_name, ip, port, community, oid, metric_name):
    auth = cmdgen.CommunityData(community)
    cmd = cmdgen.CommandGenerator()
    error_indication, error_status, error_index, var_binds = cmd.getCmd(
        auth,
        cmdgen.UdpTransportTarget((ip, port)),
        *[cmdgen.MibVariable(oid)],
        lookupMib=False
    )
    if error_indication:
        return error_data.append({"server_name": server_name, "error_reason": error_indication})
    else:
        for oid, val in var_binds:
            # Display the error when the OID registered in the conf.json does not exist in the system
            if val.prettyPrint() == "No Such Object currently exists at this OID":
                error_data.append({"server_name": server_name, "protocol": "SNMP",
                                   "error_reason": f"OID {oid.prettyPrint()} does not exists."})
            else:
                return {"server_name": server_name, "name": metric_name,
                        "oid": str(oid.prettyPrint()).rstrip().replace("\n", " ").replace("\r", " "),
                        "value": str(val.prettyPrint()).rstrip().replace("\n", " ").replace("\r", " ")}


# IPMI request allowing connection to the IPMI port of the server
# Get the sensors/metrics chosen in the conf.json
def ipmi_request(server_name, ip, user, password, metrics):
    pipe = subprocess.Popen([f"ipmitool -I lanplus -H {ip} -U {user} -P {password} sdr elist full"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    output, error = pipe.communicate()
    if error:
        error_data.append({"server_name": server_name, "protocol": "IPMI", "error_reason": error.decode("utf-8")})
    else:
        data = []
        ipmi_metrics = list(metrics.values())
        for metric in ipmi_metrics:
            # Check each line of the list and select those that match the sensor from the json conf
            for line in output.splitlines():
                if metric in line.decode("utf-8").rstrip():
                    # Add the data in the variable data
                    data.append(
                        {"server_name": server_name, "name": list(metrics.keys())[list(metrics.values()).index(metric)],
                         "value": line.decode("utf-8").rstrip().replace("\n", " ").replace("\r", " ")})
        return data


# Loading the "conf.json" configuration file
file = open("conf.json", "r")
dictionary = json.load(file)

# Host Recovery
snmp_host = list(dictionary["SNMP"].keys())
ipmi_host = list(dictionary["IPMI"].keys())

# For each SNMP host
for host in snmp_host:
    # Exception handling
    if "ip" not in dictionary["SNMP"][host]:
        sys.exit(f"Key 'ip' for host {host} does not exist. Please enter it correctly.")
    if "port" not in dictionary["SNMP"][host]:
        sys.exit(f"Key 'port' for host {host} does not exist. Please enter it correctly.")
    if "community" not in dictionary["SNMP"][host]:
        sys.exit(f"Key 'community' for host {host} does not exist. Please enter it correctly.")
    # Retrieval of SNMP oids and addition to the snmp_data variable
    if "metrics" in dictionary["SNMP"][host]:
        for oid in list(dictionary["SNMP"][host]["metrics"].values()):
            data = snmp_request(host, dictionary["SNMP"][host]["ip"], dictionary["SNMP"][host]["port"],
                                dictionary["SNMP"][host]["community"], oid,
                                list(dictionary["SNMP"][host]["metrics"].keys())[
                                    list(dictionary["SNMP"][host]["metrics"].values()).index(str(oid))])
            if data:
                snmp_data.append(data)
    else:
        sys.exit(f"Key for 'metrics' for host {host} does not exist. Please enter it correctly.")

# For each IPMI host
for host in ipmi_host:
    # Exception handling
    if "ip" not in dictionary["IPMI"][host]:
        sys.exit(f"Key 'ip' for host {host} does not exist. Please enter it correctly.")
    if "user" not in dictionary["IPMI"][host]:
        sys.exit(f"Key 'user' for host {host} does not exist. Please enter it correctly.")
    if "password" not in dictionary["IPMI"][host]:
        sys.exit(f"Key 'password' for host {host} does not exist. Please enter it correctly.")
    # Recovery of IPMI sensors and addition in the variable ipmi_data
    if "metrics" in dictionary["IPMI"][host]:
        data = ipmi_request(host, dictionary["IPMI"][host]["ip"], dictionary["IPMI"][host]["user"],
                            dictionary["IPMI"][host]["password"],
                            dictionary["IPMI"][host]["metrics"])
        if data:
            for item in data:
                ipmi_data.append(item)
    else:
        sys.exit(f"Key 'metrics' for host {host} does not exist. Please enter it correctly.")

# Display of results in json format
if snmp_data:
    print("snmp_data : \n")
    for item in snmp_data:
        print(json.dumps(item))
if ipmi_data:
    print("\n ipmi_data : \n")
    for item in ipmi_data:
        print(json.dumps(item))
if error_data:
    print("\n error_data : \n")
    print(error_data)

data = {}
if snmp_data:
    data["SNMP"] = snmp_data
if ipmi_data:
    data["IPMI"] = ipmi_data

# Request to send data to php api
resp = requests.post('http://localhost/api/apiSnmpIpmi.php', data=json.dumps(data))
print(resp.content)
print(resp.status_code)

# END

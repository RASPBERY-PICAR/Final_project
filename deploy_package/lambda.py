import json
import logging
import sys
import numpy as np
import pandas as pd
import greengrasssdk
# Create random name
import random
import string

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# SDK Client
client = greengrasssdk.client("iot-data")

MAX_NUM_CARPORT = 100
PUBLIC_CARPORT = 80
# init as free
carport_array = np.zeros(MAX_NUM_CARPORT, dtype=np.int8)
next_free_array = (i+1 for i in range(MAX_NUM_CARPORT))
# next_private_free = 0
next_public_free = 0
num_occupied = 0

dataset = pd.DataFrame(
    columns=["vehicle_id", "user_id", "user_name", "veh_type", "veh_state", "registered_carport_id"])
# "veh_type": 1 registered, 2 temporary(guest)
# "veh_state": >=0: occupied carport id,
user_set = {}


def generate_user(id):
    if id not in user_set.keys():
        user_set[id] = ''.join(
            [random.choice(string.ascii_letters + string.digits) for n in range(4)])


def generate_vehicle(id):
    veh_dic = {}
    veh_dic["vehicle_id"] = ''.join(
        [random.choice(string.ascii_letters + string.digits) for n in range(5)])
    if id not in user_set.keys():
        generate_user(id)
    veh_dic["user_id"] = id
    veh_dic["user_name"] = user_set[id]
    veh_dic["veh_type"] = 1
    veh_dic["veh_state"] = -1
    veh_dic["registered_carport_id"] = random.choice(range(PUBLIC_CARPORT))
    return veh_dic


def assign_carport(veh_type, veh_id):
    global num_occupied, carport_array, next_free_array, next_public_free
    assign_id = 0
    if num_occupied >= MAX_NUM_CARPORT:
        return -1
    if veh_type == 1:  # has registered carport
        filtered_df = dataset[dataset.vehicle_id == veh_id]
        # print(filtered_df)
        veh_dic = {}
        veh_dic = filtered_df.to_dict(orient="list")
#         print(veh_dic)
        assign_id_list = veh_dic["registered_carport_id"]
        for assign_id in assign_id_list:
            if carport_array[assign_id] == 0:
                num_occupied += 1
                carport_array[assign_id] = 1
                dataset.loc[dataset.vehicle_id ==
                            veh_id, "veh_state"] = assign_id
                return assign_id
    # not get the registered carport or guest car
    assign_id = next_public_free
    carport_array[next_public_free] = veh_type  # assign to a guest car
    next_public_free = next_free_array[assign_id]
    num_occupied += 1
    dataset.loc[dataset.vehicle_id == veh_id, "veh_state"] = assign_id
    return assign_id


def unassign_carport(carport_id):
    global num_occupied, carport_array, next_free_array, next_public_free
    if carport_array[carport_id] == 0:
        return -1
    if carport_id >= PUBLIC_CARPORT:
        next_free_array[carport_id] = next_public_free
        next_public_free = carport_id
    carport_array[carport_id] = 0
    dataset.loc[dataset.veh_state == carport_id, "veh_state"] = -1
    num_occupied -= 1
    return 0


# init data(10 vehicles)
dataset.drop(dataset.index, inplace=True)
for i in range(10):
    dic = generate_vehicle(i)
#     print(dic)
    dataset = dataset.append(dic, ignore_index=True)
    assign_carport(1, dic["vehicle_id"])
#     print(dataset.head())


def lambda_handler(event, context):
    global carport_array, dataset
    # controller
    if event["device"] == "controller":
        message = {"device": "cloud",
                   "behavior": "re_enter", "detail": "none"}
        veh_id = event["detail"]
        filtered_df = dataset[dataset.vehicle_id == veh_id]
        # print(filtered_df)
        veh_dic = {}
        veh_dic = filtered_df.to_dict(orient="list")
        if veh_dic["veh_state"][0] >= 0:
            # quit
            message["behavior"] = "re_quit"
            ret = unassign_carport(veh_dic["veh_state"][0])
            if ret < 0:
                # error
                message["detail"] = "error"
            else:
                message["detail"] = str(veh_dic["veh_state"][0])
        else:
            # enter
            assign_id = assign_carport(veh_dic["veh_type"][0], veh_id)
            if assign_id < 0:
                # error
                message["detail"] = "error"
            else:
                message["detail"] = str(assign_id)

        client.publish(topic="controller", qos=0, payload=json.dumps(message))
        client.publish(topic="log", qos=0, payload=json.dumps(message))
    # user side
    else:
        if event["behavior"] == "query":
            message = {"device": "cloud",
                       "behavior": "re_query", "detail": "none"}
            free_list = []
            occupied_list = []
            df1 = dataset[dataset.user_id == event["device"]]
            carport_id_list = df1["registered_carport_id"].to_list()
            for port in carport_id_list:
                if carport_array[port] == 0:
                    free_list.append(port)
                else:
                    occupied_list.append(port)
            for port in range(PUBLIC_CARPORT, MAX_NUM_CARPORT):
                if carport_array[port] == 0:
                    free_list.append(port)
                else:
                    occupied_list.append(port)
            message["detail"] = {"free_list": free_list,
                                 "occupied_list": occupied_list}
            client.publish(topic=event["device"],
                           qos=0, payload=json.dumps(message))
        return
        # if __name__ == "__main__":
        #     test_data = pd.read_csv(
        #         "/Users/skymac/Desktop/CS437/Lab4/deploy_package/data2/vehicle0.csv")
        #     for i in range(2):
        #         lambda_handler(test_data.loc[i].to_dict(), None)
        #         # print(test_data.loc[i].to_dict())
        #         # print(lambda_handler(test_data.loc[i].to_dict()))

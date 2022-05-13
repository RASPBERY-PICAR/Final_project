import json
import logging
import sys
# import pandas as pd
import greengrasssdk

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# SDK Client
client = greengrasssdk.client("iot-data")

# # Counter
# my_counter = 0

# global dict to store the current max CO2 value of every vehicle
dict_CO2_MAX = {}


def lambda_handler(event, context):
    global dict_CO2_MAX
    # TODO1: Get your data
    veh_id = event["vehicle_id"]
    timestep = int(event["timestep_time"])
    ved_co2 = event["vehicle_CO2"]

    # init data
    if (timestep == -1):
        dict_CO2_MAX[veh_id] = ved_co2
        return
    # if data > 0, Send the results to IOT analytics for aggregation
    if (ved_co2 > 0):
        client.publish(
            topic='CO2_analysis',
            qos=0,
            payload=json.dumps(
                {"vehicle_ID": veh_id, "time_step": timestep, "CO2": ved_co2})
        )

    # TODO2: Calculate max CO2 emission
    # if we have the record of id in dict, and current co2 < recorded MAX, do nothing
    if (veh_id in dict_CO2_MAX) and (ved_co2 < dict_CO2_MAX[veh_id]):
        return

    # else, update record and publish
    dict_CO2_MAX[veh_id] = ved_co2
    print({"vehicle_ID": veh_id, "time_step": timestep, "CO2_MAX": ved_co2})
    # TODO3: Return the result
    # Send response back to device
    client.publish(
        topic=veh_id,
        qos=0,
        payload=json.dumps(
            {"vehicle_ID": veh_id, "time_step": timestep, "CO2_MAX": ved_co2})
    )
    # Send the results(max values) to IOT core
    client.publish(
        topic='CO2_MAX',
        qos=1,
        payload=json.dumps(
            {"vehicle_ID": veh_id, "time_step": timestep, "CO2_MAX": ved_co2})
    )

    # client.publish(
    #     topic="hello/world/counter",
    #     payload=json.dumps(
    #         {"message": "Hello world! Sent from Greengrass Core.  Invocation Count: {}".format(
    #             my_counter)}
    #     ),
    # )
    # my_counter += 1

    return


# if __name__ == "__main__":
#     test_data = pd.read_csv(
#         "/Users/skymac/Desktop/CS437/Lab4/deploy_package/data2/vehicle0.csv")
#     for i in range(2):
#         lambda_handler(test_data.loc[i].to_dict(), None)
#         # print(test_data.loc[i].to_dict())
#         # print(lambda_handler(test_data.loc[i].to_dict()))

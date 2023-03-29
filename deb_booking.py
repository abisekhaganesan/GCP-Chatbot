from google.cloud import datastore
import json
from google.oauth2 import service_account
from datetime import datetime,timedelta,date

import time
import pandas as pd

# Added Cors Configuration
cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

# Client Intialization via credentials.json
def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    #return datastore.Client(project=project_id, credentials=credentials)
    return datastore.Client(credentials=credentials)
    
# Function call to query Particular range of data from database
def chatbot_agent_booking(request):
    client = create_client("irrchatbotagent1-ufnp")
    query = client.query(kind="booking")
    l = query.fetch()
    l_data = list(l)


# GET request API Handle
    # get_data = request.get_json()
    # get_data=json.loads(request.args.get("filterdata"))
    get_data = request.args.get("data")
    # return (json.dumps({"status":"get_data",
    # "result":get_data}),cors_header)


    output_list = []
    output = {}


# Filtering data according to the Range
    # if get_data is not None and get_data != {}:
    if get_data is not None and len(get_data) != 0:
        get_data = json.loads(get_data.replace("\'", ''))
        status = get_data.get("status")
        input_request = get_data.get("result") 

# Filtering data with from/to API request in 'date'column from the datastore 
        if status == 'filter_from_to':
            # i_data = []
            for full_data in l_data:
                full_data_date = pd.to_datetime(full_data['date'],format="%d/%m/%Y")
                for data_from_request in input_request:
                    req_from_date = pd.to_datetime(data_from_request['from'],format="%d/%m/%Y")
                    req_to_date = pd.to_datetime(data_from_request['to'],format="%d/%m/%Y")
                    if full_data_date >= req_from_date and full_data_date <= req_to_date:
                        output_list.append(full_data)
            output = output_list
            return (json.dumps({"status":"filter_from_to",
            "result":output}),cors_header)
        
        # else:
        #     return (json.dumps({"status":" need param-filter_from_to",
        #     "result":"Status not equal to filter_from_to"}),cors_header)

# To update visited column on the datastore
        elif status == 'visited':
            output_list=[]
            for full_data in l_data:
                full_data_booking_id = full_data.get("booking_id")
                full_data_visited = full_data.get("visited")
                for i in input_request:
                    i_booking_id = i.get("booking_id")
                    i_visited = i.get("visited")
                    if full_data_booking_id == i_booking_id and full_data_visited != i_visited:
                        # print(full_data)
                        key_id_entity = int(full_data.key.id)
                        key = client.key("booking", key_id_entity)
                        visited_entity = client.get(key)
                        # print("existing data : ", visited_entity)
                        visited_entity['visited'] = i_visited
                        client.put(visited_entity)
                        output_list = visited_entity
                        return (json.dumps({"status":"visited",
                        "result":"visited Updated"}),cors_header)

        # elif status == 'visited':
        #     for full_data in l_data:
        #         full_data_booking_id = full_data.get("booking_id")
        #         full_data_visited = full_data.get("visited")
        #         # return (json.dumps({"status":"visited",
        #         # "result":full_data}),cors_header)
        #         for i in input_request:
        #             i_booking_id = i.get("booking_id")
        #             i_visited = i.get("visited")
        #             if full_data_booking_id == i_booking_id and full_data_visited != i_visited:
        #                 key_id_entity = int(full_data.key.id)
        #                 key = client.key("appointment", key_id_entity)
        #                 visited_entity = client.get(key)
        #                 visited_entity['visited'] = i_visited
        #                 client.put(visited_entity)
        #                 return (json.dumps({"status":"visited",
        #                 "result":" visited Update to: " +i_visited}),cors_header)
                #     else:
                #         return (json.dumps({"status":"visited",
                #         "result":"visited status already updated to:" +i_visited}),cors_header)
                # break
        # else:
        #     return (json.dumps({"status":"Request",
        #     "result":"Request does not match"}),cors_header)

        # elif status == 'filter_full_data':
        #     for data_from_db in l_data:
        #         data_from_db_bk_id = data_from_db.get('booking_id')# bk_id
        #         data_from_db_date = data_from_db.get('date')
        #         data_from_db_day = data_from_db.get('day')
        #         data_from_db_fin = data_from_db.get('fin')
        #         data_from_db_name = data_from_db.get('name')
        #         data_from_db_phone_no = data_from_db.get('phone_no')
        #         data_from_db_time = data_from_db.get('time')
        #         data_from_db_ttl_tag = data_from_db.get('ttl_tag')

        #         for data_from_request in input_request:
        #             req_bk_id = data_from_request.get('booking_id')
        #             req_date = data_from_request.get('date')
        #             req_day = data_from_request.get('day')
        #             req_fin = data_from_request.get('fin')
        #             req_name = data_from_request.get('name')
        #             req_phone_no = data_from_request.get('phone_no')
        #             req_time = data_from_request.get('time')
        #             req_ttl_tag = data_from_request.get('ttl_tag')

        #             if data_from_db_bk_id == req_bk_id or data_from_db_date == req_date or data_from_db_day == req_day or data_from_db_fin == req_fin or data_from_db_name == req_name or data_from_db_phone_no == req_phone_no or data_from_db_time == req_time or data_from_db_ttl_tag == req_ttl_tag:
        #                 output_list.append(data_from_db)
        #                 output = output_list
        #     return (json.dumps({"status":"data_from_db",
        #     "result":output}),cors_header)
    else:
        # today = date.today()
        # curr_date = today.strftime('%d/%m/%Y')
        # # to_date = today + datetime.timedelta(days=14)
        # # curr_date_to = to_date.strftime('%d/%m/%Y')
       

        # to_date = today + timedelta(days=14)
        # curr_date_to = to_date.strftime('%d/%m/%Y')
        # data={"status": "filter_from_to", "result": [{"from":""+curr_date+"","to":""+curr_date_to+""}]}
        # chatbot_agent_booking(data)

        return (json.dumps({'status':'full_data',
        'result': l_data}),cors_header)

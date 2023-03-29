from google.cloud import datastore
import json
from google.oauth2 import service_account
import pandas as pd

#Added Cors Configuration
cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

#Client Intialization via credentials.json
def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return datastore.Client(credentials=credentials)


#Function call to query Particular range of data from database
def chatbot_agent_slots(request):
    ##Client Init
    client = create_client("irrchatbotagent1-ufnp")
    ##Query Database for full range
    query_slots = client.query(kind="slots")
    slots_fulldata = query_slots.fetch()
    slots_fulldata_list = list(slots_fulldata)


  ##GET request API Handle
    get_api_data = request.args.get("data")
    # get_api_data = json.loads(get_data.replace("\'", ''))

  #Filtering data according to the Range
    if get_api_data != None and get_api_data != "" and get_api_data != "{}":
        get_api_data = json.loads(get_api_data.replace("\'", ''))
        status = get_api_data.get("status")
        input_request = get_api_data.get("result")
        # filtered_data = []

        ####### Filtered Slot Dates to show on chatbot #######
        if status == 'slot_filter_weekend':
            i_date = []
            for i in slots_fulldata_list:
                i_date_ts = pd.to_datetime(i['date'],format="%d/%m/%Y")
                for date in input_request:
                    req_from = pd.to_datetime(date['from'],format="%d/%m/%Y")
                    req_to = pd.to_datetime(date['to'],format="%d/%m/%Y")
                    if (i_date_ts >= req_from) & (i_date_ts <= req_to) & (i['available_slots'] != '0'):
                        i_date.append(i)
            return (json.dumps({"status":"slot_filter_weekend",
            "output":i_date}),cors_header)

        ######### Portal Filter ##########
        elif status == 'portal_filter_from_to':
            filter_data = []
            for full_data in slots_fulldata_list:
                full_data_date = pd.to_datetime(full_data['date'],format="%d/%m/%Y")
                for data_from_request in input_request:
                    req_from_date = pd.to_datetime(data_from_request['from'],format="%d/%m/%Y")
                    req_to_date = pd.to_datetime(data_from_request['to'],format="%d/%m/%Y")
                    if full_data_date >= req_from_date and full_data_date <= req_to_date:
                        filter_data.append(full_data)
            output = filter_data
            return (json.dumps({"status":"portal_filter_from_to",
            "output":output}),cors_header)

        ######### new slot adding ##########
        elif status == 'new_slot_adding':
            for i in input_request:
                req_date = pd.to_datetime(i['date'],format="%d/%m/%Y")
                req_slot_time = i.get('slot_time')
                # print(req_date,req_slot_time)
            for full_data in slots_fulldata_list:
                full_date = pd.to_datetime(full_data['date'],format="%d/%m/%Y")
                full_slot_time = full_data['slot_time']
                if req_date == full_date and req_slot_time == full_slot_time:
                    # print('match')
                    return (json.dumps({'status':'slot already exists'}),cors_header)
                    break
            else:
                # print('not match')
                day_name = req_date.day_name()
                reserved_slots = '0'
                available_slots = '20'
                req_date_str = req_date.strftime("%d/%m/%Y")
                # print(req_date_str,day_name,req_date)
                if day_name == 'Sunday' or day_name == 'Saturday':
                    if req_date_str != '' and req_slot_time != '' and day_name != '' and reserved_slots != '' and available_slots != '':
                        slot_add = {'date':req_date_str,'day':day_name,'slot_time':req_slot_time,'reserved_slots':reserved_slots,'available_slots':available_slots}
                        complete_key = client.key("slots")
                        task = datastore.Entity(key=complete_key)
                        task.update(slot_add)
                        client.put(task)
                        # print('slot added')
                        return (json.dumps({'status':'slot added'}),cors_header)
                else:
                    # print('only weekend slot can be added')
                    return (json.dumps({'status':'only weekend slot can be added'}),cors_header)

        ####### Reserved slot Date #######
        elif status == 'reserve_data':
            for data in slots_fulldata_list:
                for i in input_request:
                    req_date = i['date']
                    req_slot = i['slot_time']
                    slot_time_date_for_output = req_date + " " + req_slot
                    if req_date in data.values() and req_slot in data.values():
                        key_id_entity = int(data.key.id)
                        reserve_key = client.key("slots", key_id_entity)
                        reserve_entity = client.get(reserve_key)
                        if str(int(data['available_slots'])) != '0':
                            sub_data_slot = str(int(data['available_slots'])-1)
                            add_data_slot = str(int(data['reserved_slots'])+1)
                            reserve_entity.update({
                                "available_slots":sub_data_slot,
                                "reserved_slots":add_data_slot
                                })
                            client.put(reserve_entity)
                            return (json.dumps({'status':'reserved_slots_are_updated'}),cors_header)
                        else:
                            return (json.dumps({"Slot Not Available for requested date": slot_time_date_for_output}),cors_header)

        ######## Cancelled slot Dates ########
        else:
            for data in slots_fulldata_list:
                for i in input_request:
                    req_date = i['date']
                    req_slot = i['slot_time']
                    slot_time_date_for_output = req_date + " " + req_slot
                    if req_date in data.values() and req_slot in data.values():
                        key_id_entity = int(data.key.id)
                        key = client.key("slots", key_id_entity)
                        cancel_entity = client.get(key)
                        sub_data_slot = str(int(data['available_slots'])+1)
                        add_data_slot = str(int(data['reserved_slots'])-1)
                        if int(data['reserved_slots']) > 0 and int(data['reserved_slots']) <= 20:
                            cancel_entity.update({
                                "available_slots":sub_data_slot,
                                "reserved_slots":add_data_slot
                                })
                            client.put(cancel_entity)
                            return (json.dumps({'status':'canceled_slots_are_updated'}),cors_header)
                        else:
                            return (json.dumps({"Slot Not Available for cancel": slot_time_date_for_output}),cors_header)

    ####### This statement will simply displays full slot data from the datastore #####                        
    else:
        return (json.dumps({"status":"full_data",
        "output":slots_fulldata_list}),cors_header)
from google.cloud import datastore
import json
from google.oauth2 import service_account
from flask import Flask
from flask_cors import CORS,cross_origin

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return datastore.Client(credentials=credentials)

def chatbot_booking_cancellation(request):
    client = create_client("dev-irrchatbotagent-lard") 

    query_booking = client.query(kind="booking")
    l_book = query_booking.fetch()
    booking_full_data = list(l_book) 

    query_slot = client.query(kind="slots")
    l_slot = query_slot.fetch()
    slot_full_data = list(l_slot)
        
    get_api_data = request.args.get("data")
    if get_api_data != None and get_api_data != "" and get_api_data != "{}":
        get_api_data = json.loads(get_api_data.replace("\'", ''))
        status = get_api_data.get("status")
        input_request = get_api_data.get("result")
        
        if status == 'check_booking_id':
            for req_data in input_request:
                req_booking_id = req_data.get('booking_id')
                id_filter = query_booking.add_filter("booking_id","=",req_booking_id).fetch()
                id_data = list(id_filter)
                if not id_data:
                    return (json.dumps({'status':'booking_id_not_exist'}),cors_header)
                else:
                    for i in id_data:
                        id_phone_no = i.get('phone_no')
                    return (json.dumps({'status':'booking_id_exist','phone_no':id_phone_no}),cors_header)

        elif status == 'view_booking_id':
            for req_data in input_request:
                req_booking_id = req_data.get('booking_id')
                id_filter = query_booking.add_filter("booking_id","=",req_booking_id).fetch()
                id_data = list(id_filter)
                id_data_json = json.dumps(id_data)
                id_data_json = json.loads(id_data_json.replace("\'", ''))
                if not id_data:
                    return (json.dumps({'status':'view_booking_id_not_exist'}),cors_header)
                else:
                    return (json.dumps({"status":"view_booking_id","output":id_data_json}),cors_header)

        elif status == 'reschedule_view_booking_id':
            for req_data in input_request:
                req_booking_id = req_data.get('booking_id')
                id_filter = query_booking.add_filter("booking_id","=",req_booking_id).fetch()
                id_data = list(id_filter)
                if not id_data:
                    return (json.dumps({'status':'reschedule_view_booking_id_not_exist'}),cors_header)
                else:
                    return (json.dumps({"status":"reschedule_view_booking_id","output":id_data}),cors_header)
        
        elif status == "cancel_booking_id":
            for req_data in input_request:
                req_booking_id = req_data.get('booking_id')
                id_filter = query_booking.add_filter("booking_id","=",req_booking_id).fetch()
                id_data = list(id_filter)
                if not id_data:
                    return (json.dumps({'status':'No data found'}),cors_header)
                else:
                    for i in id_data:
                        book_id = i.get('booking_id')
                        book_date = i.get('date')
                        book_time = i.get('time')
                        if book_id == req_booking_id:
                            key_id_entity = int(i.key.id)
                            delete_key = client.key("booking", key_id_entity)
                            client.delete(delete_key)
                    for slot_data in slot_full_data:
                        slot_date = slot_data.get('date')
                        slot_time = slot_data.get('slot_time')
                        if (book_date == slot_date) and (book_time == slot_time):
                            key_id_entity = int(slot_data.key.id)
                            key = client.key("slots", key_id_entity)
                            cancel_entity = client.get(key)
                            sub_data_slot = str(int(slot_data['available_slots'])+1)
                            add_data_slot = str(int(slot_data['reserved_slots'])-1)
                            if int(slot_data['reserved_slots']) > 0 and int(slot_data['reserved_slots']) <= 20:
                                cancel_entity.update({
                                    "available_slots":sub_data_slot,
                                    "reserved_slots":add_data_slot
                                    })
                                client.put(cancel_entity)
                                return (json.dumps({'status':'cancellation successfully updated'}),cors_header)
    else:
        return (json.dumps({'status':'improper/empty request'}),cors_header)


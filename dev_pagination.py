from google.cloud import datastore
import json
from google.oauth2 import service_account
from datetime import datetime,timedelta,date

import time
import pandas as pd
# from flask import Flask
#from flask_cors import CORS,cross_origin


#app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }
def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return datastore.Client(credentials=credentials)

def pagination_function(request):
    #request = json.loads(request1.args.get("data"))
    client = create_client("dev-irrchatbotagent-lard") 
    query = client.query(kind="booking")
    l = query.fetch()
    booking_full_data = list(l)
    booking_new_data = json.dumps(sorted(booking_full_data,key=lambda k :  (k['date'],k['time'])))
    output_list =[]
    output = {}
    full_data_date='no value'
    
    data_new =json.loads(booking_new_data)
    data_len =len(data_new)
    
    get_api = request.args.get("data")
    if get_api is not None and len(get_api) != 0:
        get_api_json = json.loads(get_api.replace("\'", ''))
        status = get_api_json.get("status")
        input_request = get_api_json.get("result")
      

        if status == 'pagination':
            for i in input_request:
                page = i.get("page")
                limit = i.get("limit")
                page =int(page)
                limit = int(limit)
                page_size = (page * limit) 
                from_date = i.get('from')
                to_date =i.get('to')
               
                if data_len > page_size:

                    if (from_date != "" and to_date != ""):
                        req_from_date = pd.to_datetime(from_date,format="%d/%m/%Y")
                        req_to_date = pd.to_datetime(to_date,format="%d/%m/%Y")
                        for full_data in data_new:
                            full_data_date = pd.to_datetime(full_data['date'],format="%d/%m/%Y")
                            if full_data_date >= req_from_date and full_data_date <= req_to_date:
                                output_list.append(full_data)
                        output = output_list
                    else:
                        output=data_new                      
                 

                    if page ==0:
                        start=0
                        a=[output[start:limit]]
                        return (json.dumps({'status':'data','result': a}),cors_header)

                    else:
                        start=page*limit
                        a=[output[start:(limit+start)]]
                        return (json.dumps({'status':'data','result': a}),cors_header)
                else:
                    return (json.dumps({'status':'page limit exeeds'}),cors_header)













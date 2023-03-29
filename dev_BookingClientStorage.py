from google.cloud import datastore
import json
from google.oauth2 import service_account
from flask import Flask
from flask_cors import CORS,cross_origin

app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

@app.route("/hello_world")
def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return datastore.Client(credentials=credentials)


def chatbot_storing_values_datastore(request1):
    
    # nottrue = "false data"
    # request=request.get_json() 
    # if (len(request)) == 0:
    #     return nottrue
   
    # else:
    try:
        request = json.loads(request1.args.get("data"))
        if(request.get("fin")!=''and request.get("name")!='' and request.get("phone_no")!='' and request.get("date")!='' and request.get("day")!=''
        and request.get("time")!='' and request.get("ttl_tag")!='' and request.get("booking_id")!=''):
            
            cur_client = create_client("irrchatbotagent1-ufnp")

            client = cur_client

            complete_key = client.key("booking")

            task = datastore.Entity(key=complete_key)
        
            task.update(request)

            client.put(task)

            return (json.dumps({'status':'stored'}),cors_header)
            
        else:
            
            return (json.dumps({'status':'improper_data'}),cors_header)
    except:
        return (json.dumps({'status':'fail'}),cors_header)
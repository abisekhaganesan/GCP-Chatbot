from google.cloud import datastore
import json
from google.oauth2 import service_account
from flask import Flask
from flask_cors import CORS,cross_origin

#app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

# @app.route("/hello_world")
def create_client(project_id):
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return datastore.Client(credentials=credentials)

def chatbot_fin_check(request):
    #request = json.loads(request1.args.get("data"))
    client = create_client("dev-irrchatbotagent-lard") 
    query = client.query(kind="booking")
    l = query.fetch()
    get_api_data = request.args.get("data")
    if get_api_data != None and get_api_data != "" and get_api_data != "{}":
        get_api_data_json = json.loads(get_api_data.replace("\'", ''))
        status = get_api_data_json.get("status")
        input_request = get_api_data_json.get("data") 
        
        if status == 'check_fin':
            for req_data in input_request:
                req_data_fin = req_data.get('fin')
            for full_data in l:
                full_data_fin = full_data.get('fin')
                full_data_ttl =full_data.get('ttl_tag')               

                if full_data_fin == req_data_fin:
                    ttl=full_data_ttl
                    return (json.dumps({'status':'fin_exist','ttl':ttl}),cors_header)
                        #return ("fin exist")
                    # else:
            return (json.dumps({'status':'fin_not_exist'}),cors_header)
                    #     #return ("fin not exist")
        # else :
        #     return (json.dumps({'status':'fin not exist'}),cors_header)
    else:
        return (json.dumps({'status':'request_empty'}),cors_header)
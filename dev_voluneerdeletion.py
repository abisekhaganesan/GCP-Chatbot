from google.cloud import datastore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import auth, credentials
import json
from datetime import datetime
import pandas as pd


# Added Cors Configuration
cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

# Function call 
def chatbot_volunteer_TTL(request):
    get_data = request.args.get("data")
    if get_data is None or get_data == "" or get_data == "{}":

        # Client Intialization via credentials.json
        datastore_credentials = service_account.Credentials.from_service_account_file("datastore_credentials.json")
        project_id = 'dev-irrchatbotagent-lard'

        # Set up Datastore and Cloud Storage clients
        datastore_client = datastore.Client(project=project_id, credentials=datastore_credentials)
        
        # firebase cred
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)

        # Get today's date
        today = datetime.today()
        curr_date = today.strftime('%d/%m/%Y')
        curr_date = pd.to_datetime(curr_date,format="%d/%m/%Y")

        query = datastore_client.query(kind='volunteer')
        results = query.fetch()
        full_list_data = list(results)

        for entity in full_list_data:
            approved_date_str = entity['approved_date']
            if approved_date_str:
                approved_date = pd.to_datetime(approved_date_str, format='%d/%m/%Y', dayfirst=True)            
                email = entity.get('email')
                if approved_date < curr_date:
                    # print(entity)
                    user=auth.get_user_by_email(email)
                    # print(user)
                    auth.delete_user(user.uid)

                    key_id_entity = int(entity.key.id)
                    # print(key_id_entity)
                    delete_key = datastore_client.key("volunteer", key_id_entity)
                    # print(delete_key)
                    datastore_client.delete(delete_key)
                    return (json.dumps({"status":"Data deleted from firebase and datastore"}),cors_header)
                else:
                    return (json.dumps({"status":"No record found"}),cors_header)
            else:
                return (json.dumps({"status":"No record found"}),cors_header)


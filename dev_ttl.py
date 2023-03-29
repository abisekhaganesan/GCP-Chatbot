from google.cloud import datastore
from google.cloud import storage
from google.oauth2 import service_account
import datetime
import pandas as pd
import json

# Added Cors Configuration
cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

# Function call 
def chatbot_TTL_booking(request):
    get_data = request.args.get("data")
    if get_data is None or get_data == "" or get_data == "{}":

        # Client Intialization via credentials.json
        credentials = service_account.Credentials.from_service_account_file("credentials.json")
        project_id = 'dev-irrchatbotagent-lard'

        # Set up Datastore and Cloud Storage clients
        storage_client = storage.Client(project=project_id, credentials=credentials)
        datastore_client = datastore.Client(project=project_id, credentials=credentials)

        # Set up Cloud Storage bucket and CSV file name
        bucket_name = 'irr-backup-files'
        now = datetime.datetime.now()
        formatted_date = now.strftime("%d/%m/%Y-%H:%M:%S")
        file_name = 'IRR-Chatbot_booking_backup-{}.csv'.format(formatted_date.replace('/', '-'))
        # file_name = 'IRR-Chatbot_booking_backup-{}.csv'.format(formatted_date)
        
        # file_name = 'IRR-Chatbot_booking_backup-{}.csv'.format(datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S'))
        
        # file_name = 'IRR-Chatbot_booking_backup-{}.csv'.format(datetime.now().strftime('%d/%m/%Y-%H:%M:%S'))

        # Define CSV header row
        header = 'fin,phone_no,date,time,day,booking_id,ttl_tag,visited,name\n'

        # Query Datastore for all entities of kind 'booking'
        query = datastore_client.query(kind='booking')
        results = query.fetch()

        # Get today's date
        today = datetime.datetime.today().date()
        curr_date = today.strftime('%d/%m/%Y')
        curr_date = pd.to_datetime(curr_date,format="%d/%m/%Y")

        # Build data string from entities with matching ttl_tag
        data = header
        data_exists = False # flag to check if any matching data exists
        for entity in results:
            full_data_ttl_tag = pd.to_datetime(entity['ttl_tag'],format="%d/%m/%Y")
            
            # Only add entity data to the data string if the full_data_ttl_tag matches today's date
            if full_data_ttl_tag == curr_date:
                data_exists = True # matching data exists
                fin = entity.get('fin', 'N/A')
                phone_no = entity.get('phone_no', 'N/A')
                date = entity.get('date', 'N/A')
                time = entity.get('time', 'N/A')
                day = entity.get('day', 'N/A')
                booking_id = entity.get('booking_id', 'N/A')
                ttl_tag = entity.get('ttl_tag', 'N/A')
                visited = entity.get('visited', 'N/A')
                name = entity.get('name', 'N/A')

                # Add entity data to the data string
                data += f"{fin},{phone_no},{date},{time},{day},{booking_id},{ttl_tag},{visited},{name}\n"

                # Write data to Cloud Storage
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(file_name)
                blob.upload_from_string(data)
                
                # Delete data from Datastore
                key_id_entity = int(entity.key.id)
                print(key_id_entity)
                delete_key = datastore_client.key("booking", key_id_entity)
                print(delete_key)
                datastore_client.delete(delete_key)

        if not data_exists:
            # No matching data found
            return (json.dumps({"status":"Data not exists"}), cors_header)
            
        return (json.dumps({"status":"Data Stored and Cleared"}), cors_header)
    else:
        return (json.dumps({"error":"Invalid data parameter"}), cors_header, 400)
from google.cloud import datastore
import json
from google.oauth2 import service_account

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }


def create_client(project_id):
  credentials = service_account.Credentials.from_service_account_file("credentials.json")
  #return datastore.Client(project=project_id, credentials=credentials)
  return datastore.Client(credentials=credentials)

def chatbot_agent_volunteer(request):
  client = create_client("irrchatbotagent1-ufnp ")
  query_vol = client.query(kind="volunteer")
  volunteer_full_data = query_vol.fetch()
  full_list_data = list(volunteer_full_data)
 
  query_slot = client.query(kind="slots")
  slot_full_data = query_slot.fetch()
  slot_list_data = list(slot_full_data)

  ##GET request API Handle
  get_api_data = request.args.get("data")
  
  # volunteer datastore manipulations function
  if get_api_data != None and get_api_data != "" and get_api_data != "{}":
    get_api_data = json.loads(get_api_data.replace("\'", ''))
    status = get_api_data.get("status")
    input_request = get_api_data.get("result")

    if status == 'update_data':
      for req_data in input_request:
          req_email_data = req_data.get('email')
          req_approved_data = req_data.get('approved_status')
          req_person_data = req_data.get('person')
          req_approved_date = req_data.get('approved_date')
          req_approved_slot = req_data.get('approved_slot')
      for i in full_list_data:
          full_email_data = i.get('email')
          full_approved_data = i.get('approved_status')
          full_person_data = i.get('person')
          full_approved_date = i.get('approved_date')
          full_approved_slot = i.get('approved_slot')
          if full_email_data == req_email_data:
              key_id_entity = int(i.key.id)
              update_key = client.key("volunteer", key_id_entity)
              update_entity = client.get(update_key)
              if full_approved_data != req_approved_data:
                  req_approved = req_data['approved_status']
                  update_entity.update({"approved_status":req_approved})
                  req_person = req_data['person']
                  update_entity.update({"person":req_person})
                  req_approved_date = req_data['approved_date']
                  update_entity.update({"approved_date":req_approved_date})
                  req_approved_slot = req_data['approved_slot']
                  update_entity.update({"approved_slot":req_approved_slot})
                  client.put(update_entity)
                  return (json.dumps({"status":"approved_status updated"}),cors_header)
    
    elif status == 'delete_data':
      for req_data in input_request:
          req_email_data = req_data.get('email')
      for i in full_list_data:
          full_email_data = i.get('email')
          if full_email_data == req_email_data:
              key_id_entity = int(i.key.id)
              delete_key = client.key("volunteer", key_id_entity)
              client.delete(delete_key)
              return (json.dumps({"status":"data deleted"}),cors_header)

    elif status == 'not_approved_full_data':
      i_data = []
      for i in full_list_data:
          full_approved_data = i.get('approved_status')
          if full_approved_data == 'not approved':
            i_data.append(i)
      return (json.dumps({"status":"volunteer not approved full data",
      "output":i_data}),cors_header) 

    elif status == 'approved_full_data':
      i_data = []
      for i in full_list_data:
        full_approved_data = i.get('approved_status')
        if full_approved_data == 'approved':
          i_data.append(i)
      return (json.dumps({"status":"volunteer approved full data",
      "output":i_data}),cors_header)

    elif status == 'role_fetch':
      for req_data in input_request:
          req_email_data = req_data.get('email')
          email_filter = query_vol.add_filter("email","=",req_email_data).fetch()
          email_data = list(email_filter)
          if not email_data:
            return (json.dumps({'status':'email not found'}),cors_header)
          else:
              for i in email_data:
                return (json.dumps({'status':'full_data',
                'output':{'role':i.get('person'),'name':i.get('volunteer_name'),'phone':i.get('phone_no')} }),cors_header)
    
    elif status == 'delete_volunteer_slot':
      for req_data in input_request:
          req_date = req_data.get('date')
          req_slot = req_data.get('slot')
      for vol_data in full_list_data:
          vol_requested_date = vol_data.get('requested_date')
          vol_requested_slot = vol_data.get('requested_slot')
          if (req_date == vol_requested_date and req_slot == vol_requested_slot):
              vol_key_id_entity = int(vol_data.key.id)
              vol_delete_key = client.key("volunteer", vol_key_id_entity)
              client.delete(vol_delete_key)

      for i in slot_list_data:
          slot_date_data = i.get('date')
          slot_time_data = i.get('slot_time')
          if (req_date == slot_date_data and req_slot == slot_time_data):
              slot_key_id_entity = int(i.key.id)
              slot_delete_key = client.key("slots", slot_key_id_entity)
              client.delete(slot_delete_key)
              return (json.dumps({"status":"data deleted"}),cors_header)
      return (json.dumps({"status":"data invalid"}),cors_header)

    else:
      if (get_api_data.get("email")!=''and get_api_data.get("volunteer_name")!='' and get_api_data.get("phone_no")!='' and get_api_data.get("approved_status")!='', get_api_data.get("requested_date")!='', get_api_data.get("requested_slot")!=''):
        complete_key = client.key("volunteer")
        task = datastore.Entity(key=complete_key)
        task.update(get_api_data)
        client.put(task)   
        return (json.dumps({"status":"data added to the database"}),cors_header)
      else:
        return (json.dumps({'status':'improper data'}),cors_header)
      
  else:
    return (json.dumps({'status':'full_data',
    'output': full_list_data}),cors_header)
    # return (json.dumps({"status":"invalid request"}),cors_header)

# def hello_world(request):
#   client = create_client("irrchatbotagent1-ufnp")
#   query = client.query(kind="volunteer")
#   l = query.fetch()
#   l_data = list(l)
#   # return (json.dumps({"status":"full_data", "output":l_data}),cors_header)
#   get_data = request.get_json()
#   if len(get_data) != 0:
#     status = 'volunteer_info'
#     input_request = get_data.get("result")
#     if status == 'volunteer_info':
#       for data in l_data:
#         # return(json.dumps({'status':'data',
#         #     'result':data}),cors_header) #-- full data
#         for i in input_request:
#           # return(json.dumps({'status':'get_data input_request',
#           # 'result':i}),cors_header) #-- req data
#           req_email = i['email']
#           # return(json.dumps({'status':'req_email value',
#           # 'result':req_email}),cors_header) #-- req email value
#           req_password = i['password']
#           # return(json.dumps({'status':'req_password value',
#           # 'result':req_password}),cors_header) #-- req password value
#           req_person = i['person']
#           # return(json.dumps({'status':'req_person value',
#           # 'result':req_person}),cors_header) #-- req person value          
#           req_volunteer_name = i['volunteer_name']
#           # return(json.dumps({'status':'req_volunteer_name value',
#           # 'result':req_volunteer_name}),cors_header) #-- req volunteer name value    
#           if req_email in data.values() and req_password in data.values() and req_person in data.values() and req_volunteer_name in data.values():
#             return(json.dumps({'status':'login_info',
#             'result':'match success'}),cors_header)
#           else:
#             return(json.dumps({'status':'login_info',
#             'result':'match unsuccess'}),cors_header)
#   else:
#     return(json.dumps({'status':'req_empty'
#     }),cors_header)

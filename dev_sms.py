import os
from twilio.rest import Client
import json

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }


def send_sms(request):
  account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
  auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

  # Your Twilio phone number
  from_number = os.environ.get("TWILIO_PHONE_NUMBER")

  # get_api = {'status':'sms','result':[{'phone_no':'+919003430809','body':'hello'}]}
  get_api_data = request.args.get("data")
  if get_api_data != None and get_api_data != "" and get_api_data != "{}":
    # return (json.dumps({'status':get_api_data}),cors_header)
    get_api_data = json.loads(get_api_data.replace("\'", ''))
    status = get_api_data.get("status")
    input_request = get_api_data.get("result")

    if status == 'sms':
      for i in input_request:
        to_number = i.get('phone_no')
        body = i.get('body')
      client = Client(account_sid, auth_token)
      message = client.messages.create(
        to=to_number,
        from_=from_number,
        body=body
        )
      return (json.dumps({'status':'sms sent'}),cors_header)

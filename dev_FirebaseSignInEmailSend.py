import firebase_admin
from firebase_admin import credentials, auth
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import smtplib
import json

cors_header={
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
    }

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

def mailsend_and_firebase_signin(request):
  get_api_data = request.args.get("data")
  if get_api_data != None and get_api_data != "" and get_api_data != "{}":
    get_api_data = json.loads(get_api_data.replace("\'", ''))
    status = get_api_data.get("status")
    input_request = get_api_data.get("result")

    sender_address = 'luzyphillip@gmail.com'
    sender_pass = 'kkuvavvjdgxfjuqn'

    if status == "cred_send":
      # data = {"status":"cred_send","result":[{"email":"xxxxxxx@gmail.com"}]}
      letters = string.ascii_lowercase
      result_str = ''.join(random.choice(letters) for i in range(8))
      for i in input_request:
          receiver_address = i.get('email')

      user = auth.list_users()
      all_user = []
      for i in user.iterate_all():
          all_user.append(i.email)

      if receiver_address in all_user:
          return (json.dumps({'status': 'Email already exists'}), cors_header)
      else:
      # Create a new user with email and password
        user = auth.create_user(
          email=receiver_address,
          password=result_str
          )
        user_list = auth.list_users()
        all_user_email = []
        for i in user_list.iterate_all():
          all_user_email.append(i.email)
        if receiver_address in all_user_email:
          subject ='IRR web Portal Access'
          mail_content = 'Your Login credential for IRR web Portal, Email id: '+ receiver_address+' , Password: '+result_str

          message = MIMEMultipart()
          message['From'] = sender_address
          message['To'] = receiver_address
          message['Subject'] = subject  #The subject line
          message.attach(MIMEText(mail_content, 'plain'))

          session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
          session.starttls() #enable security
          session.login(sender_address, sender_pass) #login with mail_id and password
          text = message.as_string()
          session.sendmail(sender_address, receiver_address, text)
          session.quit()
          
          return (json.dumps({'status': 'User ID created in firebase and credentials email sent'}), cors_header)
        else:
          return (json.dumps({'status': 'Email is not properly stored in firebase'}), cors_header)

    elif status == "sign_in":
      # data={"status":"sign_in","result":[{"email":"xxxxxxxx@gmail.com","password":"xxxxxxxxxx"}]}
      for i in input_request:
          receiver_address = i.get('email')
          receiver_pass = i.get('password')
      user = auth.get_user_by_email(receiver_address)
      auth.verify_password(receiver_pass, user.password_hash)
      id_token = user.id_token
      return (json.dumps({'status': 'user signed in sucessfully','id_token':id_token}), cors_header)

    elif status == "delete_user":
      # data={"status":"delete_user","result":[{"uid":"5N93uz48a6QcNbzmCiOBZpvlvHj2"}]}
      for i in input_request:
        email = i.get('email')
        # Parse request data
        # uid = i.get('uid')
        # Delete a user by their uid
        user=auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        return (json.dumps({'status':'User deleted with UID ','output':email}),cors_header)
  else:
    return (json.dumps({'status':'Empty request'}),cors_header)
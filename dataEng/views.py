from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from base.models import *
import logging
import json
from datetime import datetime, time
from dateutil.parser import parse

def cleanEmailData(request):
    eds_instances = EmailUsage.objects.all()
    data_dict = {}
    count = 0
    for instance in eds_instances:
        raw_string_data = instance.email_log['list'][0]['messages'].split("\n")
        cleaned_data = ""
        isNewDict = False
        for line in raw_string_data:
            try:
                if isNewDict:
                    cleaned_data = cleaned_data + line
                if line[0] == "{":
                    isNewDict = True
                    cleaned_data = cleaned_data + line
                if line[0] == "}":
                    isNewDict = False
                    obj = json.loads(cleaned_data)
                    if instance.userId in data_dict.keys():
                        data_dict[instance.userId].append(obj)
                    else:
                        data_dict[instance.userId] = [obj] 
                    cleaned_data = ""
            except IndexError:
                continue
    
    # Removing duplicates and error objects
    for key, emails_list in data_dict.items():
        seen = []
        for index, obj in enumerate(emails_list):
            if obj not in seen:
                if 'error' not in obj.keys():
                    seen.append(obj)
        if (len(seen) != len(data_dict[key])):
            data_dict[key] = seen

    
    processed_data_dict = {}
        
    for key,emails_list in data_dict.items():
        isSent = True
        morning_sent_count = 0
        night_sent_count = 0
        processed_data_dict[key] = {"latest_sent_email": 0, 'earliest_sent_email': 0,'num_of_sent_emails': 0, 'num_emails_uber':0, 'num_emails_uber.com':0,'morning_sent_count':0, 'night_sent_count':0,'emails_sent_saturday':0 , 'emails_sent_sunday':0 ,'emails_sent_monday':0 ,'emails_sent_tuesday':0 ,'emails_sent_wednesday':0 ,'emails_sent_thursday':0 ,'emails_sent_friday':0 , 'total_words_in_subject': 0, 'distinct_receivers': set()}
        for index, email_body in enumerate(emails_list):
            if 'SENT' in email_body['labelIds']:
                for header_dict in email_body['payload']['headers']:
                    
                    if header_dict['name'] == 'Date':
                        # Morning sent
                        # date_time_obj = datetime.strptime(str(header_dict['value'])[:31], "%a, %d %b %Y %H:%M:%S %z")
                        date_time_obj = parse(str(header_dict['value']))
                        morning_start_time = time(0,0,0)
                        morning_end_time = time(6,0,0)
                        night_start_time = time(18,0,0)
                        night_end_time  = time(23, 59, 59)
                        if date_time_obj.time() >= morning_start_time and date_time_obj.time() <= morning_end_time:
                            morning_sent_count = morning_sent_count + 1
                        if date_time_obj.time() >= night_start_time and date_time_obj.time() <= night_end_time:
                            night_sent_count = night_sent_count + 1
                        if date_time_obj.strftime("%A") == "Saturday":
                            processed_data_dict[key]['emails_sent_saturday'] = processed_data_dict[key]['emails_sent_saturday'] + 1
                        if date_time_obj.strftime("%A") == "Sunday":
                            processed_data_dict[key]['emails_sent_sunday'] = processed_data_dict[key]['emails_sent_sunday'] + 1
                        if date_time_obj.strftime("%A") == "Monday":
                            processed_data_dict[key]['emails_sent_monday'] = processed_data_dict[key]['emails_sent_monday'] + 1
                        if date_time_obj.strftime("%A") == "Tuesday":
                            processed_data_dict[key]['emails_sent_tuesday'] = processed_data_dict[key]['emails_sent_tuesday'] + 1
                        if date_time_obj.strftime("%A") == "Wednesday":
                            processed_data_dict[key]['emails_sent_wednesday'] = processed_data_dict[key]['emails_sent_wednesday'] + 1
                        if date_time_obj.strftime("%A") == "Thursday":
                            processed_data_dict[key]['emails_sent_thursday'] = processed_data_dict[key]['emails_sent_thursday'] + 1
                        if date_time_obj.strftime("%A") == "Friday":
                            processed_data_dict[key]['emails_sent_friday'] = processed_data_dict[key]['emails_sent_friday'] + 1
                        
                        # Latest sent date
                        if index == 0:
                            processed_data_dict[key]['latest_sent_email']= header_dict['value']
                        
                    # Distinct Receivers
                    if header_dict['name'] == 'To':
                        processed_data_dict[key]['distinct_receivers'].add(header_dict['value'])
                    
                    # Subject line
                    if header_dict['name'] == 'Subject':
                        processed_data_dict[key]['total_words_in_subject'] = processed_data_dict[key]['total_words_in_subject']  + len(header_dict['value'].split()) 
          
            elif isSent:
                isSent = False
                # Sent mails counters
                processed_data_dict[key]['morning_sent_count'] = morning_sent_count
                processed_data_dict[key]['night_sent_count'] = night_sent_count

                # Total sent mails
                processed_data_dict[key]['num_of_sent_emails'] = index
                for header_dict in emails_list[index-1]['payload']['headers']:
                    # Earliest sent date
                    if header_dict['name'] == 'Date':
                        processed_data_dict[key]['earliest_sent_email']=header_dict['value']

            if 'INBOX' in email_body['labelIds']:
                for header_dict in emails_list[index]['payload']['headers']:
                    # Checking for Mails from Uber
                    if header_dict['name'] == 'Subject':
                        if header_dict['value'].lower().find("uber.com") != -1:
                            processed_data_dict[key]['num_emails_uber.com'] = processed_data_dict[key]['num_emails_uber.com'] + 1
                        elif header_dict['value'].lower().find("uber") != -1:
                            processed_data_dict[key]['num_emails_uber'] = processed_data_dict[key]['num_emails_uber'] + 1
            

    for k, v in processed_data_dict.items():
        if v['num_emails_uber.com'] != 0:
            logging.critical(k)
            logging.critical(v)
            logging.critical("------------------------")
    
    # jsonString = json.dumps(data_dict)
    # jsonFile = open("email_data.json", "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()
    return HttpResponse("done")


def cleanCallLog(request):
    md_instances = DeepSocial.objects.all()
    md_data = {}
    for instance in md_instances:
        md_data[instance.userId]= {'callLog' : instance.call_log['list']}
    
    processed_md_dict = {}
    for key,call_list in md_data.items():
        for call in call_list:
            logging.critical(call)
        

    return HttpResponse("done")


from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from base.models import *
import logging
import json
from datetime import datetime

def cleanEmailData(request):
    eds_instances = EmailUsage.objects.all()
    data_dict = {}
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

    logging.critical(data_dict.keys())   
    for emails_list in data_dict.values():
        for index, email in enumerate(emails_list):
            if (index == 0 or index == len(email)-1) and (email["labelIds"][0]=="SENT"):
                for json_obj in (email['payload']['headers']):
                    if json_obj["name"] == "Date":
                        format_string = "%a, %d %b %Y %H:%M:%S %z"
                        # Use strptime() to parse the string and convert it to a datetime object
                        date_object = datetime.strptime(json_obj['value'], format_string)
                        if index == 0:
                            latest_email_sent_date = date_object
                        else:
                            earliest_email_sent_date = date_object

            #logging.critical(latest_email_sent_date)
            #logging.critical(earliest_email_sent_date)

    # jsonString = json.dumps(data_dict)
    # jsonFile = open("email_data.json", "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()
    return HttpResponse("done")



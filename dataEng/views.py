from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from base.models import *
import logging
import json
from datetime import datetime, time, date
from dateutil.parser import parse
from dataEng.utils import *
import statistics


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

    for key, emails_list in data_dict.items():
        isSent = True
        morning_sent_count = 0
        night_sent_count = 0
        processed_data_dict[key] = {"latest_sent_email": 0, 'earliest_sent_email': 0, 'num_of_sent_emails': 0, 'num_emails_uber': 0, 'num_emails_uber.com': 0, 'morning_sent_count': 0, 'night_sent_count': 0, 'emails_sent_saturday': 0,
                                    'emails_sent_sunday': 0, 'emails_sent_monday': 0, 'emails_sent_tuesday': 0, 'emails_sent_wednesday': 0, 'emails_sent_thursday': 0, 'emails_sent_friday': 0, 'total_words_in_subject': 0, 'distinct_receivers': set()}
        for index, email_body in enumerate(emails_list):
            if 'SENT' in email_body['labelIds']:
                for header_dict in email_body['payload']['headers']:

                    if header_dict['name'] == 'Date':
                        # Morning sent
                        # date_time_obj = datetime.strptime(str(header_dict['value'])[:31], "%a, %d %b %Y %H:%M:%S %z")
                        date_time_obj = parse(str(header_dict['value']))
                        morning_start_time = time(0, 0, 0)
                        morning_end_time = time(6, 0, 0)
                        night_start_time = time(18, 0, 0)
                        night_end_time = time(23, 59, 59)
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
                            processed_data_dict[key]['latest_sent_email'] = header_dict['value']

                    # Distinct Receivers
                    if header_dict['name'] == 'To':
                        processed_data_dict[key]['distinct_receivers'].add(
                            header_dict['value'])

                    # Subject line
                    if header_dict['name'] == 'Subject':
                        processed_data_dict[key]['total_words_in_subject'] = processed_data_dict[key]['total_words_in_subject'] + len(
                            header_dict['value'].split())

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
                        processed_data_dict[key]['earliest_sent_email'] = header_dict['value']

            if 'INBOX' in email_body['labelIds']:
                for header_dict in emails_list[index]['payload']['headers']:
                    # Checking for Mails from Uber
                    if header_dict['name'] == 'Subject':
                        if header_dict['value'].lower().find("uber.com") != -1:
                            processed_data_dict[key]['num_emails_uber.com'] = processed_data_dict[key]['num_emails_uber.com'] + 1
                        elif header_dict['value'].lower().find("uber") != -1:
                            processed_data_dict[key]['num_emails_uber'] = processed_data_dict[key]['num_emails_uber'] + 1

    # for k, v in processed_data_dict.items():
    #     logging.critical(k)
    #     logging.critical(v)
    #     logging.critical("------------------------")

    # jsonString = json.dumps(data_dict)
    # jsonFile = open("email_data.json", "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()
    return HttpResponse("done")


def cleanCallLog(request):
    clds_instances = DeepSocial.objects.all()
    processed_clds_data = {}

    for clds_instance in clds_instances:
        # Removing data before 2021
        truncated_call_log = []
        for call_log in clds_instance.call_log['list']:
            default_earliest_date = datetime(2020, 12, 31)
            if parse(call_log['date']) > default_earliest_date:
                truncated_call_log.append(call_log)
        # Removing duplicates
        clds_instance.call_log['list'] = truncated_call_log

        processed_clds_data[clds_instance.userId] = clds_instance.call_log
    logging.critical(len(processed_clds_data))

    for userId, list in processed_clds_data.items():
        outgoing_calls = []
        incoming_calls = []
        missed_calls = []

        # Calculating Per day No. of persons called
        total_calls = len(list['list'])
        per_day_no_of_persons_called = total_calls / \
            getDaysBetween(list['list'][0]['date'], list['list'][-1]['date'])
        processed_clds_data[userId]['per_day_no_of_persons_called'] = per_day_no_of_persons_called
        logging.critical(getDaysBetween(
            list['list'][0]['date'], list['list'][-1]['date']))
        # Seperating call logs based on type
        for obj in list['list']:
            if str(obj['call_type']) == "CallType.outgoing":
                outgoing_calls.append(obj)
            elif str(obj['call_type']) == "CallType.incoming":
                incoming_calls.append(obj)
            elif str(obj['call_type']) == "CallType.rejected" or str(obj['call_type']) == "CallType.missed":
                missed_calls.append(obj)

        processed_clds_data[userId]['call_logs'] = [
            outgoing_calls, incoming_calls, missed_calls]

    for userId, list in processed_clds_data.items():
        # Calculating Per day Total Duration of Incoming calls
        duration = 0.0
        days_between = getDaysBetween(
            list['call_logs'][1][0]['date'], list['call_logs'][1][-1]['date'])

        for i in range(2):
            duration = 0.0
            days_between = getDaysBetween(
                list['call_logs'][1][0]['date'], list['call_logs'][1][-1]['date'])
            for call_log in (list['call_logs'][i]):
                duration = float(
                    call_log['duration']) + duration
            if i == 0:
                processed_clds_data[userId]['per_day_total_duration_outgoing_calls'] = duration/days_between
            elif i == 1:
                processed_clds_data[userId]['per_day_total_duration_incoming_calls'] = duration/days_between
        # removing original combined list of calls
        del list['list']
        # Creating contact list for each type of call
        processed_clds_data[userId]['contacts_list'] = [createContactsList(
            list['call_logs'][0]), createContactsList(list['call_logs'][1]), createContactsList(list['call_logs'][2])]

    for userId, list in processed_clds_data.items():
        pday_pperson_avg_no_incoming_calls = []
        pday_pperson_avg_no_outgoing_calls = []
        pday_pperson_avg_no_missed_calls = []
        if (userId == 'samriaadiba1234@gmail.com'):

            for contact in set(list['contacts_list'][0]):
                # last_date = get_last_date(contact,list['call_logs'][0])
                last_date = date(1990, 1, 1)
                first_date = date.today()
                count = 0
                for call in list['call_logs'][0]:
                    date_time_obj = parse(call['date']).date()
                    if (call['number'] == contact):
                        count = count + 1
                        if (last_date < date_time_obj):
                            last_date = date_time_obj
                        if (first_date > date_time_obj):
                            first_date = date_time_obj
                # logging.critical(last_date)
                # logging.critical(first_date)
                # logging.critical(count)
                try:
                    pday_pperson_avg_no_outgoing_calls.append(
                        count/getDaysBetween(str(last_date), str(first_date)))
                except ZeroDivisionError:
                    pday_pperson_avg_no_outgoing_calls.append(count)

            processed_clds_data[userId]['Per day Per person Avg No. of Outgoing calls'] = pday_pperson_avg_no_outgoing_calls

        else:
            break

    logging.critical(processed_clds_data['samriaadiba1234@gmail.com']
                     ['Per day Per person Avg No. of Outgoing calls'])

    return HttpResponse(processed_clds_data['samriaadiba1234@gmail.com']['Per day Per person Avg No. of Outgoing calls'])

# Social Foot Print ----------------------------------------------------------------------------------------------------------------------------------------
def cleanAppList(request):
    al_instances = SocialFp.objects.all()
    al_data = {}

    for al_instance in al_instances:
        for app_log in al_instance.app_list['list']:
            al_data[al_instance.userId] = al_instance.app_list

    finsavy_list = ['com.bKash.customerapp', 'com.konasl.nagad', 'com.expertoption', 'com.ibbl.cellfin',  'com.binance.dev', 
                    'com.dbbl.nexus.pay', 'com.thecitybank.citytouch', 'eraapps.bankasia.bdinternetbanking.apps', 'com.desco.ssl',
                      'com.coinbase.android', 'com.cibl.eblsky', 'com.fsiblbd.fsiblcloud', 'com.mtb.mobilebanking']
    
    travel_list = ['com.webparkit.railsheba', 'com.airbnb.android', 'com.gozayaan.app', 'net.sharetrip', 'com.obhai', 'com.booking', 
                   'com.shohoz.rides', 'com.shohoz.bus.android', 'com.shohoz.dtrainpwa', 'com.ubercab', 'com.pathao.user']
    
    ecom_list = ['com.daraz.android', 'com.bikroy', 'com.alibaba.intl.android.apps.poseidon', 'com.rokomari', 'com.amazon.mShop.android.shopping', 
                 'com.swap.swap_ecommerce', 'bd.com.evaly.evalyshop',  'com.pickaboo.app', 'com.flipkart.android', 'com.gorillamove']
    
    processed_al_data = {}
    
    for userId, list in al_data.items():
        processed_al_data[userId] = {"num_of_finsavy_apps":0 ,"isFinsavyApp":False , "num_of_travel_apps":0 , "isTravelApp":False , "num_of_ecom_apps":0 , "isEcomApp":False }
        for apps in list['list']:
            if(apps['appName'] in finsavy_list):
                processed_al_data[userId]['num_of_finsavy_apps'] = processed_al_data[userId]['num_of_finsavy_apps'] + 1
                processed_al_data[userId]['isFinsavyApp'] = True
            if(apps['appName'] in travel_list):
                processed_al_data[userId]['num_of_travel_apps'] = processed_al_data[userId]['num_of_travel_apps'] + 1
                processed_al_data[userId]['isTravelApp'] = True
            if(apps['appName'] in ecom_list):
                processed_al_data[userId]['num_of_ecom_apps'] = processed_al_data[userId]['num_of_ecom_apps'] + 1
                processed_al_data[userId]['isEcomApp'] = True

    return HttpResponse('yes i m done')

# Mobile Foot Print ----------------------------------------------------------------------------------------------------------------------------------------
def cleanMobileFp(request):
    mfp_instances = MobileFp.objects.all()
    mfp_data = {}

    for mfp_instance in mfp_instances:
        mfp_data[mfp_instance.userId] = {"no_contacts":mfp_instance.no_contacts,"no_sms":mfp_instance.no_sms}
    
# Getting number of calls ----------------------------------------------------------
    clds_instances = DeepSocial.objects.all()

    for clds_instance in clds_instances:
        # Removing data before 2021
        truncated_call_log = []
        for call_log in clds_instance.call_log['list']:
            default_earliest_date = datetime(2020, 12, 31)
            if parse(call_log['date']) > default_earliest_date:
                truncated_call_log.append(call_log)
        # Removing duplicates
        clds_instance.call_log['list'] = truncated_call_log

        mfp_data[clds_instance.userId]["num_of_calls"] = len(clds_instance.call_log['list'])

# Getting number of apps ----------------------------------------------------------
    al_instances = SocialFp.objects.all()

    for al_instance in al_instances:
        mfp_data[al_instance.userId]["num_of_apps"] = len(al_instance.app_list['list'])

    logging.critical(mfp_data)
    return HttpResponse('$')

# Survey Cleaning and getting necessary data ----------------------------------------------------------------------------------------------------------------------------------------

def cleanSurvey(request):
    survey1_instances = Survey.objects.all()
    survey2_instances = Survey2.objects.all()

    demographic_data = {}
    psychometric_data = {}

    for s1_instance in survey1_instances:
        time_list = []
        for answer in s1_instance.answers['results']:
            if(answer['id']['id'] != "321"):

                if(answer['id']['id'] == "p1"):
                    psychometric_data[s1_instance.userId] = {"no_references":answer['results'][0]['result']['value']}


                if(answer['id']['id'] == "p2"):
                    if int(answer['results'][0]['result']['value']) > 1:
                        psychometric_data[s1_instance.userId]['other_banks'] = True
                    else:
                        psychometric_data[s1_instance.userId]['other_banks'] = False

                if(answer['id']['id'] == "p3"):
                    psychometric_data[s1_instance.userId]['product_applicant_would_like_to_have_in_12months'] = answer['results'][0]['result']

                if(answer['id']['id'] == "p4"):
                    psychometric_data[s1_instance.userId]['money_now_later_3months'] = answer['results'][0]['result']['text']


                if(answer['id']['id'] == "p5"):
                    psychometric_data[s1_instance.userId]['money_now_later_6months'] = answer['results'][0]['result']['text']


                if(answer['id']['id'] == "d21"):
                    demographic_data[s1_instance.userId] = {"salary":answer['results'][0]['result']}


                if(answer['id']['id'] == "d22"):
                    demographic_data[s1_instance.userId]['age'] = answer['results'][0]['result']


                if(answer['id']['id'] == "d23"):
                    demographic_data[s1_instance.userId]['sex'] = answer['results'][0]['result']['value']


                if(answer['id']['id'] == "d23"):
                    demographic_data[s1_instance.userId]['sex'] = answer['results'][0]['result']['value']


                if(answer['id']['id'] == "d24"):
                    demographic_data[s1_instance.userId]['highschool_dummy'] = True
                    demographic_data[s1_instance.userId]['highschool_name'] = answer['results'][0]['result']['value']


                if(answer['id']['id'] == "d25"):
                    demographic_data[s1_instance.userId]['college_dummy'] = True

                if(answer['id']['id'] == "p6"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p7"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p8"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p9"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p10"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p11"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p12"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p13"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())


                if(answer['id']['id'] == "p14"):
                    delta = parse(answer['results'][0]['endDate'])-parse(answer['results'][0]['startDate'])
                    time_list.append(delta.total_seconds())
        try:
            if(len(time_list)==0):
                psychometric_data[s1_instance.userId] = {'median_time_taken_expressing_agreement' : 0}
            else:
                psychometric_data[s1_instance.userId]['median_time_taken_expressing_agreement'] = statistics.median(time_list)
        except KeyError:
            psychometric_data[s1_instance.userId] = {'median_time_taken_expressing_agreement' : 0}
        

    for s2_instance in survey2_instances:
        try:
            psychometric_data[s2_instance.userId]['type_of_player'] = s2_instance.qp3
        except KeyError:
             psychometric_data[s2_instance.userId] = {'type_of_player':s2_instance.qp3}

        try:
            measure = (s2_instance.qp7["Home"] + s2_instance.qp7["Health"] )/( s2_instance.qp7["vacation"] + s2_instance.qp7["Entertainment"])
        except ZeroDivisionError:
            measure = s2_instance.qp7["Home"] + s2_instance.qp7["Health"]
        psychometric_data[s2_instance.userId]['measure_of_moderation'] = measure


# juthiahamed19@gmail.com'
    return HttpResponse('$')
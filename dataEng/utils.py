from dateutil.parser import parse


def createContactsList(processed_dict_value):
    contacts_list = []
    for call_log_obj in processed_dict_value:
        contacts_list.append(call_log_obj['number'])

    return contacts_list


def getDaysBetween(last_date, first_date):
    latest_call_date = parse(last_date)
    earliest_call_date = parse(first_date)
    days_between = (latest_call_date - earliest_call_date).days
    return days_between

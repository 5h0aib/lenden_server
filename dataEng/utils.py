def createContactsList(processed_dict_value):
    contacts_list = []
    for call_log_obj in processed_dict_value:
        contacts_list.append(call_log_obj['number'])

    return contacts_list

# def get_last_date(contact , list):
#     for call in list:

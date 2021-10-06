from dataholders.SeriesDataHolder import SeriesDataHolder


def build_param_dataholders(msgs_recipes):
    dh_by_name = {}
    dh_by_type = {}
    for topic_rec in msgs_recipes:
        for msg_rec in topic_rec['messages']:  # TODO: kiszervezni

            new_dh = SeriesDataHolder(msg_rec['name'], msg_rec['fields'], 1)

            dh_by_name[msg_rec['name']] = new_dh
            dh_by_type[msg_rec['type']] = new_dh

    return dh_by_name,dh_by_type
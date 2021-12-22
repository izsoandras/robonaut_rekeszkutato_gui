import yaml
from my_gui.plotting.PlotsFrame import PlotsFrame
from clients.mqtt.listeners.DatabaseSaveListener import DatabbaseSaveListener
from dataholders.SeriesDataHolder import SeriesDataHolder
from dataholders.FixedDataholder import FixedDataholder


def build_plot_env_from_file(mqtt_data_path, msg_recipes_path, plot_recipes_path, db_proxy, parent, *args, **kwargs):
    with open(msg_recipes_path) as file:
        topic_rec = yaml.safe_load(file)[1]  # TODO: rendesen megvizsgalni mit kell menetni

    with open(plot_recipes_path) as file:
        plot_rec = yaml.safe_load(file)

    with open(mqtt_data_path) as file:
        mqtt_data = yaml.safe_load(file)

    dh_by_type = {}
    dh_by_name = {}
    for msg in topic_rec['messages']:  # TODO: kiszervezni
        new_dh = SeriesDataHolder(msg['name'], msg['fields'], plot_rec['sample_num'])
        dh_by_name[msg['name']] = new_dh
        dh_by_type[msg['type']] = new_dh

    listener = DatabbaseSaveListener(db_proxy, topic_rec['messages'], 'RKI gui tel', mqtt_data['broker'],
                                     topic_rec['name'], mqtt_data['user'], mqtt_data['pwd'], dh_by_type)

    frame = PlotsFrame(dh_by_name, plot_rec, parent, *args, **kwargs)

    return listener, frame


def build_dataholders(msgs_reicpes, plots_recipe=None):
    if plots_recipe is None:
        plots_recipe = {
            'plots': []
        }

    dh_by_name = {}
    dh_by_type = {}
    for topic_rec in msgs_reicpes:
        for msg_rec in topic_rec['messages']:  # TODO: kiszervezni
            dh_type = find_plot_type(msg_rec['name'], plots_recipe['plots'])  # TODO: kiszervezni

            if dh_type == 'series' or dh_type == 'spec' or dh_type == 'spec_bin':
                new_dh = SeriesDataHolder(msg_rec['name'], msg_rec['fields'], plots_recipe['sample_num'])
            elif dh_type == 'bar' or dh_type == 'compass':
                new_dh = FixedDataholder(msg_rec['name'], msg_rec['fields'], 1)
            else:
                raise ValueError(f'Wrong value as plot type for {msg_rec["name"]}')

            dh_by_name[msg_rec['name']] = new_dh
            dh_by_type[msg_rec['type']] = new_dh

    return dh_by_name, dh_by_type


def find_plot_type(name, plots):
    for plot in plots:
        for line in plot['lines']:  # TODO: kiszervezni
            if line['message'] == name:  # TODO: kiszervezni
                return plot['type']  # TODO: kiszervezni

    return 'series'  # TODO: kiszervezni

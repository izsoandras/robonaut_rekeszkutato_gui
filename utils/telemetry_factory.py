import yaml
from my_gui.plotting.PlotsFrame import PlotsFrame
from my_mqtt.listeners.DatabaseSaveListener import DatabbaseSaveListener
from dataholders.SeriesDataHolder import SeriesDataHolder
from dataholders.FixedDataholder import FixedDataholder


def build_plot_env_from_file(mqtt_data_path, msg_recipes_path, plot_recipes_path, db_proxy, parent, *args, **kwargs):
    with open(msg_recipes_path) as file:
        msg_rec = yaml.safe_load(file)[1] # TODO: rendesen megvizsgalni mit kell menetni

    with open(plot_recipes_path) as file:
        plot_rec = yaml.safe_load(file)

    with open(mqtt_data_path) as file:
        mqtt_data = yaml.safe_load(file)

    dh_by_type = {}
    dh_by_name = {}
    for msg in msg_rec['messages']:  # TODO: kiszervezni
        new_dh = SeriesDataHolder(msg['name'], msg['fields'], plot_rec['sample_num'])
        dh_by_name[msg['name']] = new_dh
        dh_by_type[msg['type']] = new_dh

    listener = DatabbaseSaveListener(db_proxy, msg_rec['messages'], 'RKI gui tel', mqtt_data['broker'], msg_rec['name'], mqtt_data['user'], mqtt_data['pwd'], dh_by_type)

    frame = PlotsFrame(dh_by_name, plot_rec, parent, *args, **kwargs)

    return listener, frame


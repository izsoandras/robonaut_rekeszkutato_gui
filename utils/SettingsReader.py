import yaml
import yaml.scanner
import logging

# TODO: outsource
defaults = {
    'proto': {
        'proto': 'mqtt',
        'broker': 'localhost',
        'user': None,
        'pwd': None
    },
    'topics': [],
    'database': {
        'dbhost': 'localhost',
        'dbname': 'test',
        'measurement_prefix': ''
    },
    'plotting': {
        'sample_num': 50,
        'update_period': 200,
        'layout': [3, 3],
        'plots': []
    },
    'lines': []
}

# TODO: outsource
comp_fields = {
    'topic': ['name', 'messages'],
    'msgs': ['name', 'type', 'format','fields'],
    'plot': ['lines'],
    'line': ['message', 'field']
}

opt_fields = {
    'topic': [],
    'msgs': ['factors'],
    'plot': ['title', 'type', 'ylim', 'bins', 'sample_num', 'isRad', 'theta_dir', 'flipud', 'fliplr'],
    'line': ['legend']
}


class SettingsReader:
    def __init__(self, msgs_path=None, plots_path=None, proto_path=None, db_path=None):
        if msgs_path is not None:
            self.msgs_path = msgs_path
        else:
            self.msgs_path = './settings/msgs.yaml'  # TODO: remove literal

        if plots_path is not None:
            self.plots_path = plots_path
        else:
            self.plots_path = './settings/plots.yaml'  # TODO: remove literal

        if proto_path is not None:
            self.proto_path = proto_path
        else:
            self.proto_path = './settings/proto.yaml'  # TODO: remove literal

        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = './settings/database.yaml'  # TODO: remove literal


        self.errors = []
        self.severe = []
        self.logger = logging.getLogger('RKID.SettingsReader')

        self.topic_recs = None
        self.proto_data = None
        self.plots_rec = None
        self.db_data = None

    def read_data(self):

        try:
            with open(self.proto_path) as file:
                proto_data = yaml.safe_load(file)

            self.proto_data = self.check_full_default(proto_data, defaults['proto'], 'PROTO')
        except FileNotFoundError:
            # self.logger.warning(f'MQTT data settings not found at: {self.mqtt_path},\nusing default values')
            self.log_file_not_found('MQTT data', self.mqtt_path)
            self.proto_data = defaults['mqtt']  # TODO: remove literal
        except yaml.scanner.ScannerError as se:
            self.proto_data = defaults['mqtt']
            self.logger.error(str(se))

        try:
            with open(self.msgs_path) as file:
                topic_recs = yaml.safe_load(file)

            self.topic_recs = self.check_nested_lists(topic_recs, [['messages']], ['topic', 'msgs'],
                                                      ['topic', 'message'])  # TODO: remove literal
        except FileNotFoundError:
            self.topic_recs = defaults['topics']  # TODO: remove literal
            self.log_file_not_found('Msgs', self.msgs_path)
        except yaml.scanner.ScannerError as se:
            self.topic_recs = defaults['topics']
            self.logger.error(str(se))

        try:
            with open(self.plots_path) as file:
                plots_rec = yaml.safe_load(file)

            plots_rec = self.check_full_default(plots_rec, defaults['plotting'], 'plotting')  # TODO: remove literal
            plots_rec['plots'] = self.check_nested_lists(plots_rec['plots'], [['lines']], ['plot', 'line'],
                                                         ['plot', 'line'])  # TODO: remove literal

            self.plots_rec = plots_rec
        except FileNotFoundError:
            self.plots_rec = defaults['plotting']  # TODO: remove literal
            self.log_file_not_found('Plots', self.plots_path)
        except yaml.scanner.ScannerError as se:
            self.plots_rec = defaults['plotting']
            self.logger.error(str(se))

        try:
            with open(self.db_path) as file:
                db_data = yaml.safe_load(file)

            self.db_data = self.check_full_default(db_data, defaults['database'], 'Database')
        except FileNotFoundError:
            self.db_data = defaults['database']  # TODO: remove literal
            self.log_file_not_found('Database', self.db_path)
        except yaml.scanner.ScannerError as se:
            self.db_data = defaults['database']
            self.logger.error(str(se))

        return self.topic_recs, self.plots_rec, self.proto_data, self.db_data

    def check_nested_lists(self, outmost_list: list, keys, fields_keys, whats):
        recs_passed = []
        for idx, recipe in enumerate(outmost_list):
            id = self.name_or_idx(recipe, idx)
            for key in recipe.keys():
                if key not in comp_fields[fields_keys[0]] and key not in opt_fields[fields_keys[0]]:  # TODO: remove literal
                    self.logger.warning(f'{str.capitalize(whats[0])} {id} has unnecessary key: {key}')

            comp_not_incl = [key for key in comp_fields[fields_keys[0]] if key not in recipe.keys()]
            if comp_not_incl:
                self.log_comp_key_miss(whats[0], {id}, comp_not_incl)
                is_passed = False
            else:
                is_passed = True

            sublists_passed = []
            if len(keys) > 0:
                if type(keys[0]) is not list:
                    keys[0] = [keys[0]]

                for key in keys[0]:
                    if key in recipe.keys():
                        thiskey_passed = self.check_nested_lists(recipe[key], keys[1:], fields_keys[1:], whats[1:])

                        sublists_passed.append(thiskey_passed)
                    else:
                        sublists_passed.append([])



            # msgs_passed = []
            # if 'messages' not in comp_not_incl:  # TODO: remove literal
            #     for msg_idx, msg_rec in enumerate(recipe['messages']):  # TODO: remove literal
            #         msg_id = self.name_or_idx(msg_rec, msg_idx)
            #         for msg_key in msg_rec.keys():
            #             if msg_key not in comp_fields['msgs'] and msg_key not in opt_fields['msgs']:
            #                 self.logger.warning(f'Message {msg_id} has unnecessary key {msg_key}')
            #
            #         msg_comp_not_incl = [key not in recipe.keys for key in comp_fields['msgs']]
            #         if msg_comp_not_incl:
            #             self.log_comp_key_miss('Message', msg_id, msg_comp_not_incl, 'topic', id)
            #         else:
            #             msgs_passed.append(msg_rec)

            if is_passed:
                if len(keys) > 0:
                    for key, passed_list in zip(keys[0], sublists_passed):
                        recipe[key] = passed_list

                recs_passed.append(recipe)

        return recs_passed

    def name_or_idx(self, dic: dict, idx):
        if 'name' in dic.keys():
            return dic['name']
        else:
            return f'no{idx}'

    # def check_mqtt(self, mqtt_data: dict):
    #     for key in defaults['mqtt'].keys():
    #         if key not in mqtt_data.keys():
    #             self.logger.warning(f'MQTT settings file does not have key: {key}. Using default value instead.')
    #             mqtt_data[key] = defaults['mqtt'][key]
    #
    #     if len(mqtt_data.keys()) > len(defaults['mqtt'].keys()):
    #         self.logger.warning(
    #             f'MQTT settings file has unnecessary keys. Only the following keys should be contained: {str(defaults["mqtt"].keys())}')
    #
    #     self.mqtt_data = mqtt_data

    def check_full_default(self, read, default, what):
        for key in default.keys():
            if key not in read.keys():
                self.logger.warning(f'{what} settings file does not have key: {key}. Using default value instead.')
                read[key] = default[key]

        if len(read.keys()) > len(default.keys()):
            self.logger.warning(
                f'{what} settings file has unnecessary keys. Only the following keys should be contained: {str(default.keys())}')

        return read

    def log_file_not_found(self, what, where):
        err_str = f'{what} settings file not found at: {where}'
        self.severe.append(err_str)
        self.logger.error(err_str)

    def log_comp_key_miss(self, what, which, keys, in_what=None, in_which=None):
        in_str = f' in {in_what} {in_which}' if in_what is not None and in_which is not None else ''
        err_msg = f'{str.capitalize(what)} {which}{in_str} does not contain compulsory keys {str(keys)}'
        self.logger.error(err_msg)
        self.errors.append(err_msg)


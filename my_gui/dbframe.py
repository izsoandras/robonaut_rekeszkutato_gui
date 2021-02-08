import tkinter
from tkinter import filedialog
import csv
import logging


class DBframe(tkinter.Frame):
    def __init__(self, parent, influxDB, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.logger = logging.getLogger('robotlog')

        self.database = influxDB

        self.lb_dropdown = tkinter.Label(self, text='Select measurement:')
        self.lb_dropdown.pack(side=tkinter.LEFT)

        choices = self.get_measurements()
        if not choices:
            choices = 'No measurement yet'

        self.dropdown_var = tkinter.StringVar(self)
        self.dropdown_var.set("option1")
        self.dropdown = tkinter.OptionMenu(self, self.dropdown_var, *choices)
        self.dropdown.configure(width=40)
        self.dropdown.pack(side=tkinter.LEFT)

        self.fr_buttons = tkinter.Frame(self)
        self.btn_load = tkinter.Button(master=self.fr_buttons, text="Load", command=self.load_measurement)
        self.btn_export = tkinter.Button(master=self.fr_buttons, text="Export", command=self.export_measurement)
        self.btn_delete = tkinter.Button(master=self.fr_buttons, text="Delete", command=self.delete_measurement)
        self.btn_load.pack()
        self.btn_export.pack()
        self.btn_delete.pack()

        self.fr_buttons.pack(side=tkinter.LEFT)

    def get_measurements(self):
        measurements = self.database.get_list_measurements()
        names = []
        for measurement in measurements:
            names.append(measurement['name'])

        return names

    def update_dropdown(self):
        # Reset var and delete all old options
        self.dropdown_var.set('')
        self.dropdown['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to var)
        measurements = self.get_measurements()

        if not measurements:
            measurements = ['No measurements yet']
            self.btn_delete.configure(state='disabled')
            self.btn_export.configure(state='disabled')
            self.btn_load.configure(state='disabled')
        else:
            self.btn_delete.configure(state='normal')
            self.btn_export.configure(state='normal')
            self.btn_load.configure(state='normal')

        for measurement in measurements:
            self.dropdown['menu'].add_command(label=measurement, command=tkinter._setit(self.dropdown_var, measurement))

        self.dropdown_var.set(measurements[0])

        self.logger.debug('Dropdown updated')

    def export_measurement(self):
        f = filedialog.asksaveasfilename(title="Export measurement", filetypes=(("CSV files", "*.csv"),))
        if f is None:
            return

        string = 'SELECT * FROM '+'"'+self.dropdown_var.get()+'"'    # TODO: bind_params

        query_set = self.database.query(string)
        raw_data = query_set.get_points()

        first = next(raw_data)
        print(query_set.items())
        with open(f, 'w', newline='') as export_file:
            writer = csv.DictWriter(export_file, first.keys())
            writer.writeheader()
            writer.writerow(first)
            for data in raw_data:
                writer.writerow(data)

        self.logger.info('Measurements saved: '+self.dropdown_var.get())

    def delete_measurement(self):
        self.database.drop_measurement(self.dropdown_var.get())

        self.logger.warning('Measurement deleted" '+self.dropdown_var.get())

        self.update_dropdown()

    def load_measurement(self):
        raise NotImplementedError


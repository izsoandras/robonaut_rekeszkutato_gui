import tkinter
from tkinter import filedialog
import utils.db_exporters
import logging
import utils.InfluxDBproxy


class DBExportFrame(tkinter.Frame):
    def __init__(self, parent, dbproxy: utils.InfluxDBproxy.InfluxDBproxy, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.dbproxy = dbproxy

        self.logger = logging.getLogger('RKID.DBExport')

        self.lb_dropdown = tkinter.Label(self, text='Select measurement:')
        self.lb_dropdown.pack(side=tkinter.LEFT)

        self.dropdown_var = tkinter.StringVar(self)
        self.dropdown_var.set("No measurement yet")
        self.dropdown = tkinter.OptionMenu(self, self.dropdown_var, "No measurement yet")
        self.dropdown.configure(width=40)
        self.dropdown.pack(side=tkinter.LEFT)

        self.fr_buttons = tkinter.Frame(self)
        self.btn_update = tkinter.Button(master=self.fr_buttons, text="Update list", command=self.on_btn_update)
        self.btn_export = tkinter.Button(master=self.fr_buttons, text="Export", command=self.on_btn_export)
        self.btn_delete = tkinter.Button(master=self.fr_buttons, text="Delete", command=self.on_btn_delete)

        self.update_dropdown()

        self.btn_update.pack()
        self.btn_export.pack()
        self.btn_delete.pack()

        self.fr_buttons.pack(side=tkinter.LEFT)

    def update_dropdown(self):

        # Insert list of new options (tk._setit hooks them up to var)
        try:
            measurements = self.dbproxy.get_list_measurements()
        except ConnectionError:
            self.logger.debug("DB not connected, couldn't update dropwodn!")
            return

        # Reset var and delete all old options
        self.dropdown_var.set('')
        self.dropdown['menu'].delete(0, 'end')

        if not measurements:
            measurements = ['No measurements yet']
            self.btn_delete.configure(state='disabled')
            self.btn_export.configure(state='disabled')
        else:
            self.btn_delete.configure(state='normal')
            self.btn_export.configure(state='normal')

        for measurement in measurements:
            self.dropdown['menu'].add_command(label=measurement,
                                              command=tkinter._setit(self.dropdown_var, measurement))

        self.dropdown_var.set(measurements[0])

        self.logger.debug('Dropdown updated')

    def on_btn_export(self):
        f = filedialog.asksaveasfilename(title="Export measurement", filetypes=(("CSV files", "*.csv"),))

        if f is None:
            return

        # TODO: background thread
        self.logger.debug(f'Sending query for measurements {self.dropdown_var.get()}')
        query_set = self.dbproxy.get_measurement(self.dropdown_var.get())
        self.logger.info(f'Exporting {self.dropdown_var.get()}')
        utils.db_exporters.influx2csv(query_set, f)
        self.logger.info(f'Export {self.dropdown_var.get()} complete!')

    def on_btn_delete(self):
        self.dbproxy.delete_measurement(self.dropdown_var.get())
        self.update_dropdown()

    # TODO: nice, scheduled update of the view, also with disable/enable buttons in form of on_connected and on_disconnected
    def on_btn_update(self):
        self.update_dropdown()


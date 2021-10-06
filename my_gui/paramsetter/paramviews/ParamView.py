import abc
import tkinter
import logging


class ParamView(metaclass=abc.ABCMeta, tkinter.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.name = name
        self.logger = logging.getLogger('paramview_' + name)

        self.lb_name = tkinter.Label(self, text=self.name)
        self.lb_name.pack(side=tkinter.LEFT)

        # https://stackoverflow.com/questions/55184324/why-is-calling-register-required-for-tkinter-input-validation/55231273#55231273
        vcmd = self.register(self.validate_input)
        self.tb_set_value = tkinter.Entry(self, width=8, justify='right')
        self.tb_set_value.config(validate='key', validatecommand=(vcmd, '%P'))
        self.tb_set_value.pack(side=tkinter.LEFT)

        self.stvar_current = tkinter.StringVar()
        self.tb_current_value = tkinter.Entry(self, state='readonly',
                                              textvariable=self.stvar_current,
                                              width=8, justify='left')
        self.tb_current_value.pack(side=tkinter.LEFT)

    @abc.abstractmethod
    def validate_input(self, input_value: str):
        pass

    # TODO: make thread safe (it is accessed through multiple threads)
    def get_new_value(self):
        return self.tb_set_value.get()

    def get_current_value(self):
        return self.stvar_current.get()

    def set_view(self, value):
        self.stvar_current.set(str(value))

import tkinter
import logging


class IsConnectedView(tkinter.Frame):
    def __init__(self, parent, name, is_conn_subject, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.logger = logging.getLogger(f'RKID.ConnView{name}')
        self.name = name
        self.subject = is_conn_subject

        self.ivar_rbvar = tkinter.IntVar()
        self.ivar_rbvar.set(0)
        self.lb_name = tkinter.Label(self, text=self.name)
        self.rb_isConn = tkinter.Radiobutton(self, variable=self.ivar_rbvar, value=1,selectcolor='red',command=self.command)
        self.lb_name.pack(side=tkinter.LEFT)
        self.rb_isConn.pack(side=tkinter.LEFT)

    def update_view(self):
        if self.subject.isConnected:
            self.rb_isConn.configure(selectcolor='green')
        else:
            self.rb_isConn.configure(selectcolor='red')

    def command(self):
        self.ivar_rbvar.set(0)
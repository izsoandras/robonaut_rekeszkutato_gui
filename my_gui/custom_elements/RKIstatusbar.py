import tkinter
import logging
from .IsConnectedView import IsConnectedView


class RKIstatusbar(tkinter.Frame):
    def __init__(self, parent, client, db_proxy, pinger, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.logger = logging.getLogger('RKID.RKIstatusbar')
        self.client = client
        self.db_proxy = db_proxy
        self.pinger = pinger

        self.conn_views = []
        subjects = [client, db_proxy, pinger]
        names = ['Broker:', ' Database:', ' Robot:']

        for s in zip(subjects,names):
            cv = IsConnectedView(self, s[1], s[0])
            cv.pack(side=tkinter.LEFT)
            self.conn_views.append(cv)

        self.update_cycle()

    def update_cycle(self):
        self.update_view()
        self.master.after(500, self.update_cycle)

    def update_view(self):
        for cv in self.conn_views:
            cv.update_view()

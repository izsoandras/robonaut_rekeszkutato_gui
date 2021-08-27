import logging
import logging.handlers
import tkinter
import queue


class ScreenLogger(tkinter.Frame):
    def __init__(self, parent, visible_line_num=10, max_line_num=100, update_ms=200, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.max_line_num = max_line_num
        self.line_num = 0
        self.update_ms = update_ms

        self.msg_queue = queue.Queue()

        self.logHandler = logging.handlers.QueueHandler(self.msg_queue)

        self.tb_logfield = tkinter.Text(self, height=visible_line_num, state=tkinter.DISABLED)
        self.sb_logscroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tb_logfield.yview)

        self.tb_logfield.configure(yscrollcommand=self.sb_logscroll.set)

        self.sb_logscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tb_logfield.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.master.after(update_ms, self.update_screen)

    def update_screen(self):
        self.tb_logfield.config(state=tkinter.NORMAL)
        while not self.msg_queue.empty():
            new_msg = self.msg_queue.get()

            self.tb_logfield.insert(tkinter.END, '\n' + new_msg)

        self.line_num = int(self.tb_logfield.index(tkinter.END).split('.')[0]) - 1
        if self.line_num >= self.max_line_num:
            self.tb_logfield.delete('1.0', f'{1 + (self.line_num - self.max_line_num)}.0')

        self.keep_end_visible_if_needed()

        self.tb_logfield.config(state=tkinter.DISABLED)
        self.master.after(self.update_ms, self.update_screen)

    def keep_end_visible_if_needed(self):
        if self.sb_logscroll.get()[1] > (self.line_num - 2) / self.line_num:
            self.tb_logfield.see(tkinter.END)
            return True
        else:
            return False

    def set_visible_line_number(self, visible_line_num: int):
        self.tb_logfield.configure(height=visible_line_num)

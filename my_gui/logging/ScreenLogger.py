import logging
import logging.handlers
import tkinter
import queue


class ScreenLogger(tkinter.Frame):
    def __init__(self, parent, level=logging.INFO, fmt=None, visible_line_num=10, max_line_num=100, update_ms=200, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.logger = logging.getLogger(__name__)

        self.max_line_num = max_line_num
        self.line_num = 0
        self.update_ms = update_ms

        self.msg_queue = queue.Queue()

        self.logHandler = logging.handlers.QueueHandler(self.msg_queue)
        self.logHandler.setLevel(level)
        if fmt is None:
            fmt = '%(levelname)s-%(name)s: %(message)s'

        self.logHandler.setFormatter(logging.Formatter(fmt))

        self.tb_logfield = tkinter.Text(self, height=visible_line_num, state=tkinter.DISABLED)
        self.sb_logscroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tb_logfield.yview)

        self.tb_logfield.configure(yscrollcommand=self.sb_logscroll.set)

        self.fr_level_select = tkinter.Frame(self)
        self.lb_level = tkinter.Label(self.fr_level_select, text='Log view level:')
        self.ddvar_level = tkinter.StringVar(self)
        choices = ["Debug", "Info", "Warning", "Error", "Severe", "Critical"]
        self.dd_level = tkinter.OptionMenu(self.fr_level_select, self.ddvar_level, *choices, command=self.on_level_selection_changed)
        self.dd_level.config(width=10)
        self.ddvar_level.set(choices[1])

        self.lb_level.pack(side=tkinter.LEFT)
        self.dd_level.pack(side=tkinter.LEFT)
        self.fr_level_select.pack(side=tkinter.TOP)

        self.sb_logscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tb_logfield.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.master.after(update_ms, self.update_screen)

    def update_screen(self):
        self.tb_logfield.config(state=tkinter.NORMAL)
        while not self.msg_queue.empty():
            new_log = self.msg_queue.get()

            self.tb_logfield.insert(tkinter.END, '\n' + new_log.msg)

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
        self.logger.debug(f'Changed visible line number to: {visible_line_num}')

    def on_level_selection_changed(self, new_val):
        if new_val == "Debug":
            new_lvl = logging.DEBUG
        elif new_val == "Info":
            new_lvl = logging.INFO
        elif new_val == "Warning":
            new_lvl = logging.WARNING
        elif new_val == "Error":
            new_lvl = logging.ERROR
        elif new_val == "Critical":
            new_lvl = logging.CRITICAL
        else:
            self.logger.error(f'Wrong level {new_val}')
            return

        self.logHandler.setLevel(new_lvl)



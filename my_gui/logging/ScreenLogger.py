import logging
import logging.handlers
import tkinter
import queue
import tkinter.font
import numpy


class ScreenLogger(tkinter.Frame):
    def __init__(self, parent, app_level=logging.INFO, robot_level=logging.DEBUG, fmt=None, visible_line_num=10, max_line_num=100, update_ms=200, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.logger = logging.getLogger(__name__)

        self.max_line_num = max_line_num
        self.line_num = 0
        self.update_ms = update_ms

        self.msg_queue = queue.Queue()

        self.appLogHandler = logging.handlers.QueueHandler(self.msg_queue)
        self.appLogHandler.setLevel(app_level)

        self.robotLogHandler = logging.handlers.QueueHandler(self.msg_queue)
        self.robotLogHandler.setLevel(robot_level)

        if fmt is None:
            fmt = '%(asctime)s-%(levelname)s-%(name)s>\t%(message)s'

        date_fmt = '%H:%M:%S'

        formatter = logging.Formatter(fmt, date_fmt)
        self.appLogHandler.setFormatter(formatter)
        self.robotLogHandler.setFormatter(formatter)

        self.tb_logfield = tkinter.Text(self, height=visible_line_num, state=tkinter.DISABLED)
        self.sb_logscroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tb_logfield.yview)

        self.tb_logfield.configure(yscrollcommand=self.sb_logscroll.set)

        self.fr_level_select = tkinter.Frame(self)
        self.lb_app_level = tkinter.Label(self.fr_level_select, text='Log view app level:')
        self.ddvar_app_level = tkinter.StringVar(self)
        choices = ["Debug", "Info", "Warning", "Error", "Critical"]
        self.dd_app_level = tkinter.OptionMenu(self.fr_level_select, self.ddvar_app_level, *choices, command=self.on_app_level_selection_changed)
        self.dd_app_level.config(width=10)
        self.ddvar_app_level.set(choices[1])    # TODO: change to given parameter
        self.lb_robot_level = tkinter.Label(self.fr_level_select, text='Log view robot level:')
        self.ddvar_robot_level = tkinter.StringVar(self)
        self.dd_robot_level = tkinter.OptionMenu(self.fr_level_select, self.ddvar_robot_level, *choices, command=self.on_robot_level_selection_changed)
        self.ddvar_robot_level.set(choices[0])    # TODO: change to given parameter
        self.btn_section_break = tkinter.Button(self.fr_level_select, text="Section break", command=self.on_btn_section_break)

        self.lb_app_level.pack(side=tkinter.LEFT)
        self.dd_app_level.pack(side=tkinter.LEFT)
        self.lb_robot_level.pack(side=tkinter.LEFT)
        self.dd_robot_level.pack(side=tkinter.LEFT)
        self.btn_section_break.pack(side=tkinter.LEFT)
        self.fr_level_select.pack(side=tkinter.TOP)

        self.sb_logscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tb_logfield.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.master.after(update_ms, self.update_screen)

    def update_screen(self):
        lines = []
        while not self.msg_queue.empty():
            new_log = self.msg_queue.get()
            lines.append(new_log.msg)

        self.push_to_screen(lines)

        self.master.after(self.update_ms, self.update_screen)

    def push_to_screen(self, lines):
        try:
            iter(lines)
        except TypeError:
            lines = [lines]

        if lines:
            self.tb_logfield.config(state=tkinter.NORMAL)

            self.tb_logfield.insert(tkinter.END, '\n' + "\n".join(lines))

            self.line_num = int(self.tb_logfield.index(tkinter.END).split('.')[0]) - 1
            if self.line_num >= self.max_line_num:
                self.tb_logfield.delete('1.0', f'{1 + (self.line_num - self.max_line_num)}.0')

            self.keep_end_visible_if_needed()

            self.tb_logfield.config(state=tkinter.DISABLED)

    def keep_end_visible_if_needed(self):
        if self.sb_logscroll.get()[1] > (self.line_num - 2) / self.line_num:
            self.tb_logfield.see(tkinter.END)
            return True
        else:
            return False

    def set_visible_line_number(self, visible_line_num: int):
        self.tb_logfield.configure(height=visible_line_num)
        self.logger.debug(f'Changed visible line number to: {visible_line_num}')

    def on_btn_section_break(self):
        tb_w = self.tb_logfield.winfo_width()
        tb_font = tkinter.font.nametofont(self.tb_logfield["font"])
        font_w = tb_font.measure("-")
        separator_row = "-" * int(numpy.floor(tb_w/font_w)-1)
        self.push_to_screen([separator_row])

    def on_app_level_selection_changed(self, new_val):
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

        self.appLogHandler.setLevel(new_lvl)

    def on_robot_level_selection_changed(self, new_val):
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

        self.robotLogHandler.setLevel(new_lvl)



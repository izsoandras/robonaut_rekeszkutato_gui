import tkinter as tk
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt
import my_mqtt.navigation
import my_mqtt.commands
import my_mqtt.telemetry
import multiprocessing
from queue import Queue


class SkillCourseFrame(tk.Frame):
    def __init__(self, parent, image_path, points, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.VIEW_UPDATE_PERIOD = 200 # [ms]

        self.mqtt_client = mqtt.Client(my_mqtt.COURSE_POS_NAME)
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.username_pw_set(my_mqtt.USER_NAME, my_mqtt.PASSWORD)
        self.mqtt_client.connect(my_mqtt.HOST_NAME)
        self.mqtt_client.subscribe(my_mqtt.COURSE_POS_TOPIC)
        self.mqtt_client.subscribe(my_mqtt.TELEMETRY_TOPIC)
        self.mqtt_client.loop_start()

        self.queue = Queue()
        self.speed_queue = Queue()

        self.pos_marker_rad = 10
        self.pos_marker_poscolor = 'IndianRed1'
        self.pos_marker_negcolor = 'RoyalBlue1'
        self.pos_marker_tag = 'pos'
        self.pos_sign_tag = 'pos_sign'
        self.last_gate_marker_rad = 13
        self.last_gate_marker_color = 'gray60'
        self.last_gate_marker_tag = 'last_gate'
        self.goal_marker_rad = 16
        self.goal_marker_color = 'gold'
        self.goal_marker_tag = 'goal'
        self.points = points
        self.nav_data = {
            'position': 0,
            'next_goal': 0,
            'last_gate': 0,
            'orient': 1,
            'dir':1
        }

        # Create canvas with the image
        self.image_path = image_path
        self.base_img = Image.open(image_path)
        self.base_width, self.base_height = self.base_img.size
        self.canvas_img = ImageTk.PhotoImage(self.base_img)
        self.canvas = tk.Canvas(self, width=self.canvas_img.width(), bg='#f0f0f0', height=self.canvas_img.height(),
                                scrollregion=(0, 0, self.canvas_img.width(), self.canvas_img.height()))

        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_img)

        self.speed_text = self.canvas.create_text(200,40,text='Speed: 0', font='Arial 26 bold')
        self.is_resized = True
        self.resized_img = self.base_img
        self.ratio = 1
        self.prev_ratio = 1
        self.resize_process = multiprocessing.Process()

        x0 = 10
        y0 = 10
        delta_x = 18
        delta_y = 1.2*delta_x
        hor_space = 10
        vert_space = 20
        line_width = 6
        self.dir_selected_color = 'green3'
        self.dir_non_color = 'red'
        self.dir_view = [None]*6
        self.dir_view[1] = self.canvas.create_line(x0, y0, x0 + delta_x, y0+delta_y, width=line_width, fill=self.dir_non_color, capstyle=tk.ROUND)
        self.dir_view[3] = self.canvas.create_line(x0+delta_x+hor_space, y0, x0+delta_x+hor_space, y0+delta_y, width=line_width, fill=self.dir_selected_color, capstyle=tk.ROUND)
        self.dir_view[5] = self.canvas.create_line(x0+2*delta_x+2*hor_space, y0, x0+delta_x+2*hor_space, y0+delta_y, width=line_width, fill=self.dir_non_color, capstyle=tk.ROUND)

        self.dir_view[0] = self.canvas.create_line(x0+delta_x, y0+delta_y+vert_space, x0, y0+vert_space+2*delta_y, width=line_width, fill=self.dir_non_color, capstyle=tk.ROUND)
        self.dir_view[2] = self.canvas.create_line(x0+delta_x+hor_space, y0+delta_y+vert_space, x0+delta_x+hor_space, y0+vert_space+2*delta_y, width=line_width,
                                fill=self.dir_non_color, capstyle=tk.ROUND)
        self.dir_view[4] = self.canvas.create_line(x0 + delta_x + 2 * hor_space, y0+delta_y+vert_space, x0 + 2 * delta_x + 2 * hor_space, y0+vert_space+2*delta_y,
                                width=line_width, fill=self.dir_non_color, capstyle=tk.ROUND)

        r = 17
        self.dir_sign_marker = self.canvas.create_oval(x0 + delta_x + hor_space - r,
                                y0 + delta_y + vert_space * 0.54 - r,
                                x0 + delta_x + hor_space + r,
                                y0 + delta_y + vert_space * 0.54 + r, fill=self.pos_marker_poscolor)
        self.dir_sign_text = self.canvas.create_text(x0+delta_x+hor_space, y0+delta_y+vert_space*0.54, text='+', font='Arial 22 bold')

        # Create goal marker
        self.canvas.create_oval(self.points[0][0] - self.goal_marker_rad, self.points[0][1] - self.goal_marker_rad,
                                self.points[0][0] + self.goal_marker_rad, self.points[0][1] + self.goal_marker_rad,
                                fill=self.goal_marker_color, tags=self.goal_marker_tag)
        # Create last gate marker
        self.canvas.create_oval(self.points[0][0] - self.last_gate_marker_rad,
                                self.points[0][1] - self.last_gate_marker_rad,
                                self.points[0][0] + self.last_gate_marker_rad,
                                self.points[0][1] + self.last_gate_marker_rad,
                                fill=self.last_gate_marker_color, tags=self.last_gate_marker_tag)
        # Create position marker
        self.pos_marker = self.canvas.create_oval(self.points[0][0] - self.pos_marker_rad,
                                                  self.points[0][1] - self.pos_marker_rad,
                                                  self.points[0][0] + self.pos_marker_rad,
                                                  self.points[0][1] + self.pos_marker_rad,
                                                  fill=self.pos_marker_poscolor, tags=self.pos_marker_tag)
        # Create orient sign text
        self.pos_marker_sign_text = self.canvas.create_text(self.points[0][0], self.points[0][1], text='+', font='Arial 22 bold', tag='pos_sign')

        # Add scroll function
        # self.sb_canvasscrolly = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        # # self.sb_canvasscrollx = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        # # self.canvas.configure(yscrollcommand=self.sb_canvasscrolly.set, xscrollcommand=self.sb_canvasscrollx.set)
        # self.canvas.configure(yscrollcommand=self.sb_canvasscrolly.set)

        # Build GUI
        # self.sb_canvasscrolly.pack(side=tk.RIGHT, fill=tk.Y)
        # self.sb_canvasscrollx.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.NW)

        self.bind('<Configure>', self.resizer)

        self.master.after(self.VIEW_UPDATE_PERIOD, self.update_vew)

    def on_message(self, client, userdata, message):
        if message.topic == my_mqtt.COURSE_POS_TOPIC:
            navi_dict = my_mqtt.navigation.decode_navigation(message.payload)
            self.queue.put(navi_dict)
        elif message.topic == my_mqtt.TELEMETRY_TOPIC:
            if message.payload[1] == my_mqtt.telemetry.SPEEDCTRL_TYPE:
                speed_dict = my_mqtt.telemetry.decode_telemetry(message.payload)
                self.speed_queue.put(int(speed_dict['data']['speed_setp']))

    def resizer(self, e):
        width_rat = e.width/self.base_width
        height_rat = e.height/self.base_height

        self.ratio = min(width_rat, height_rat)

        # self.canvas.delete("all")

        # if self.resize_process is not None and self.resize_process.is_alive():
        #     self.resize_process.kill()

        self.resized_img = ImageTk.PhotoImage(
            self.base_img.resize((int(self.ratio * self.base_width), int(self.ratio * self.base_height)), Image.ANTIALIAS))

        self.canvas.itemconfigure( self.image_id, image=self.resized_img)
        self.canvas_img = self.resized_img
        self.redraw(self.nav_data)

    def resize_worker(self, rat):

        self.resized_img = ImageTk.PhotoImage(
            self.base_img.resize((int(rat * self.base_width), int(rat * self.base_height)), Image.ANTIALIAS))

        self.ratio = rat

    def update_vew(self):
        new_data = None
        while not self.queue.empty():
            new_data = self.queue.get()

        if new_data is not None:
            self.nav_data = new_data['data']
            self.redraw(new_data['data'])

        new_speed = None
        while not self.speed_queue.empty():
            new_speed = self.speed_queue.get()

        if new_speed is not None:
            self.canvas.itemconfigure(self.speed_text, text=f'Speed: {new_speed}')

        # if self.ratio != self.prev_ratio:
        #     self.ratio = self.prev_ratio
        #     self.resized_img = ImageTk.PhotoImage(
        #         self.base_img.resize((int(self.ratio * self.base_width), int(self.ratio * self.base_height)),
        #                              Image.NEAREST))
        #
        #     self.canvas.itemconfigure(self.image_id, image=self.resized_img)
        #     self.canvas_img = self.resized_img

        self.master.after(self.VIEW_UPDATE_PERIOD, self.update_vew)

    def redraw(self, navi_data):
        pos_idx = navi_data['position']
        goal_idx = navi_data['next_goal']
        last_gate_idx = navi_data['last_gate']

        pos_last = self.canvas.coords(self.pos_marker)  # (x0, y0, x1, y1) tuple

        self.move_obj([self.ratio * i for i in self.points[pos_idx]], self.ratio * self.pos_marker_rad, self.pos_marker_tag)
        self.move_obj([self.ratio * i for i in self.points[goal_idx]], self.ratio * self.goal_marker_rad, self.goal_marker_tag)
        self.move_obj([self.ratio * i for i in self.points[last_gate_idx]], self.ratio * self.last_gate_marker_rad, self.last_gate_marker_tag)

        pos_new = self.canvas.coords(self.pos_marker)  # (x0, y0, x1, y1) tuple

        if navi_data['orient'] > 0:
            pos_color = self.pos_marker_poscolor
            pos_sign_text = '+'
        else:
            pos_color = self.pos_marker_negcolor
            pos_sign_text = '-'

        self.canvas.itemconfigure(self.pos_marker, fill=pos_color)
        self.canvas.itemconfigure(self.pos_marker_sign_text, text=pos_sign_text)

        self.canvas.move(self.pos_marker_sign_text, pos_new[0] - pos_last[0], pos_new[1] - pos_last[1])

        direction = navi_data['dir']

        if direction > 0:
            dir_color = self.pos_marker_poscolor
            dir_sign_text = '+'
        else:
            dir_color = self.pos_marker_negcolor
            dir_sign_text = '-'

        self.canvas.itemconfigure(self.dir_sign_marker, fill=dir_color)
        self.canvas.itemconfigure(self.dir_sign_text, text=dir_sign_text)

        sel_idx = abs(direction) - 1
        for idx, line in enumerate(self.dir_view):
            if idx == sel_idx:
                self.canvas.itemconfigure(line, fill=self.dir_selected_color)
            else:
                self.canvas.itemconfigure(line, fill=self.dir_non_color)

    def move_obj(self, center, radius, tag):
        x0 = center[0] - radius
        y0 = center[1] - radius
        x1 = center[0] + radius
        y1 = center[1] + radius
        self.canvas.coords(tag, x0, y0, x1, y1)

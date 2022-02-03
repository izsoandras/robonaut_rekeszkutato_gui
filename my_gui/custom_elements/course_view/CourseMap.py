import tkinter
from PIL import ImageTk, Image, ImageOps
import json
import math
import logging
from clients.mqtt.listeners import ParamListener
from dataholders import DataHolder
import numpy as np

CAR_IMG = 0
DIR_SW_IMG = 1
EXIT_IMG = 2
LANE_LEFT_IMG = 3
LANE_RIGHT_IMG = 4
LEFT_IMG = 5
RIGHT_IMG = 6
MIDDLE_IMG = 7
STOP_IMG = 8
LINE_IMG = 9

MANEUVER_FOLLOW_LEFT = 0
MANEUVER_FOLLOW_MIDDLE = 1
MANEUVER_FOLLOW_RIGHT = 2
MANEUVER_TURN = 3
MANEUVER_TURN_FOLLOW_LEFT = 4
MANEUVER_TURN_FOLLOW_MIDDLE = 5
MANEUVER_TURN_FOLLOW_RIGHT = 6
MANEUVER_EXIT_THROUGH = 7
MANEUVER_LANE_SW_LEFT = 8
MANEUVER_LANE_SW_RIGHT = 9
MANEUVER_STOP = 10

NAVI_EVENT_CROSSING_FRONT = 0
NAVI_EVENT_CROSSING_REAR = 1
NAVI_EVENT_CROSSING_LEFT = 2
NAVI_EVENT_EXIT_LEFT = 3
NAVI_EVENT_START_ROUTE = 4
NAVI_EVENT_TURN_COMPLETE = 5
NAVI_EVENT_DEAD_END = 6
NAVI_EVENT_INVALID = 7


class CourseMap(tkinter.Frame):
    def __init__(self, parent, client: ParamListener, id, dataholder: DataHolder, assets_path='./assets/map', *args,
                 **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.logger = logging.getLogger('RKID.CourseView')

        self.client = client
        self.id = id
        self.dataholder = dataholder
        self.car_state = {
            'current node': 0,
            'goal node': 0,
            'node_dir': 1,
            'orientation': 1,
            'direction': 1,
            'event': None,
            'maneuver': MANEUVER_STOP
        }

        with open(assets_path + '/course.json') as node_file:
            self.node_info = json.load(node_file)

        self.ratio = 1
        self.base_img = Image.open(assets_path + '/course.png')
        self.base_width, self.base_height = self.base_img.size
        self.canvas_img = ImageTk.PhotoImage(self.base_img)
        self.canvas = tkinter.Canvas(self, width=self.canvas_img.width(), bg='#f0f0f0', height=self.canvas_img.height())
        self.image_id = self.canvas.create_image(0, 0, anchor=tkinter.NW, image=self.canvas_img)
        self.is_resized = True
        self.resized_img = self.canvas_img

        figs_paths = ['car_car.png', 'car_dir_sw.png', 'car_exit.png', 'car_lane_left.png', 'car_lane_right.png',
                      'car_left.png', 'car_right.png', 'car_middle.png', 'car_STOP.png', 'car_line_sensor.png']
        self.car_ratio = self.node_info['car_rat']
        self.fig_imgs = []
        self.fig_imgs_resiz = []
        for fig_path in figs_paths:
            img = Image.open(assets_path + '/figs/' + fig_path).convert('RGBA')
            self.fig_imgs.append(
                img.resize((int(self.car_ratio * img.width), int(self.car_ratio * img.height)), Image.ANTIALIAS))
            self.fig_imgs_resiz.append(self.fig_imgs[-1])

        self.car_base_width, self.car_base_height = self.fig_imgs[0].size
        self.car_img = ImageTk.PhotoImage(self.fig_imgs_resiz[CAR_IMG])
        self.car_img_id = self.canvas.create_image((100, 50), image=self.car_img)

        self.disabled_gui = [{'idx': None, 'tag': None} for i in range(0, 4)]
        self.goal_gui = {'idx': None, 'tag': None}
        self.goal_car = {'idx': None, 'tag': None}
        self.disabled_car = [{'idx': None, 'tag': None} for i in range(0, 4)]
        self.marker_rad = self.fig_imgs_resiz[0].height * self.car_ratio

        self.send_btn = tkinter.Button(self.canvas, text="Send", bg='RoyalBlue1', activebackground='navy',
                                       command=self.on_btn_send_click)
        # self.send_btn.pack(side=tkinter.RIGHT, anchor=tkinter.SE)
        self.send_btn.place(x=self.canvas_img.width(),
                            y=self.canvas_img.height(),
                            width=self.canvas_img.width() / 8, height=self.canvas_img.height() / 12, anchor=tkinter.SE)

        self.random_btn = tkinter.Button(self.canvas, text="Randomize", bg='lime green',
                                         activebackground='forest green',
                                         command=self.on_btn_random_click)
        self.random_btn.place(x=self.canvas_img.width() - self.canvas_img.width() / 8,
                              y=self.canvas_img.height(),
                              width=self.canvas_img.width() / 8, height=self.canvas_img.height() / 12,
                              anchor=tkinter.SE)

        self.canvas.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH, anchor=tkinter.NW)
        self.bind('<Configure>', self.on_resize)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self._invalid = True
        self.continous_update()

    def invalidate(self):
        self._invalid = True

    def redraw(self):
        self._invalid = False

        for d in self.disabled_car:
            self._draw_marker(d, 'IndianRed4', False)

        for d in self.disabled_gui:
            self._draw_marker(d, 'IndianRed1')

        self._draw_marker(self.goal_car, 'DarkGoldenrod3', False)
        self._draw_marker(self.goal_gui, 'gold')

        self.update_car()

        self.send_btn.place(x=self.canvas_img.width(),
                            y=self.canvas_img.height(),
                            width=self.canvas_img.width() / 8, height=self.canvas_img.height() / 12, anchor=tkinter.SE)

        self.random_btn.place(x=self.canvas_img.width() - self.canvas_img.width() / 8,
                            y=self.canvas_img.height(),
                            width=self.canvas_img.width() / 8, height=self.canvas_img.height() / 12, anchor=tkinter.SE)

    def _draw_marker(self, marker, color, filled=True):
        if marker['tag'] is not None:
            self.canvas.delete(marker['tag'])
            marker['tag'] = None

        if marker['idx'] is not None:
            x_c = self.node_info["coords"][marker['idx']][0]
            y_c = self.node_info["coords"][marker['idx']][1]

            if filled:
                marker["tag"] = self.canvas.create_oval(self.ratio * (x_c - self.marker_rad),
                                                        self.ratio * (y_c - self.marker_rad),
                                                        self.ratio * (x_c + self.marker_rad),
                                                        self.ratio * (y_c + self.marker_rad),
                                                        fill=color)
            else:
                marker["tag"] = self.car_goal_marker = self.canvas.create_oval(self.ratio * (x_c - self.marker_rad),
                                                                               self.ratio * (y_c - self.marker_rad),
                                                                               self.ratio * (x_c + self.marker_rad),
                                                                               self.ratio * (y_c + self.marker_rad),
                                                                               fill=None, outline=color,
                                                                               width=self.ratio * self.marker_rad)

    def on_resize(self, event):
        width_rat = event.width / self.base_width
        height_rat = event.height / self.base_height

        self.ratio = min(width_rat, height_rat)

        # self.canvas.delete("all")

        # if self.resize_process is not None and self.resize_process.is_alive():
        #     self.resize_process.kill()

        self.resized_img = ImageTk.PhotoImage(
            self.base_img.resize((int(self.ratio * self.base_width), int(self.ratio * self.base_height)),
                                 Image.ANTIALIAS))

        self.canvas.itemconfigure(self.image_id, image=self.resized_img)
        self.canvas_img = self.resized_img

        for idx, fig_base in enumerate(self.fig_imgs):
            self.fig_imgs_resiz[idx] = fig_base.resize(
                (int(self.ratio * self.car_base_width), int(self.ratio * self.car_base_height)),
                Image.ANTIALIAS)

        self._invalid = True
        pass

    def make_car(self, car_ori, car_dir, maneuver):
        img = Image.new('RGBA', ((int(self.ratio * self.car_base_width), int(self.ratio * self.car_base_height))),
                        (0, 0, 0, 0))

        if car_dir * car_ori > 0:
            new_img = ImageOps.mirror(self.fig_imgs_resiz[LINE_IMG])
        else:
            new_img = self.fig_imgs_resiz[LINE_IMG]

        img.paste(new_img, (0, 0), new_img)

        if car_ori > 0:
            new_img = self.fig_imgs_resiz[CAR_IMG].rotate(180)
        else:
            new_img = self.fig_imgs_resiz[CAR_IMG]

        img.paste(new_img, (0, 0), new_img)

        new_img = None
        if maneuver == MANEUVER_STOP:
            new_img = self.fig_imgs_resiz[STOP_IMG]
        elif maneuver == MANEUVER_LANE_SW_LEFT:
            new_img = self.fig_imgs_resiz[LANE_LEFT_IMG]
        elif maneuver == MANEUVER_LANE_SW_RIGHT:
            new_img = ImageOps.mirror(self.fig_imgs_resiz[LANE_RIGHT_IMG])
        else:
            if maneuver == MANEUVER_EXIT_THROUGH:
                new_img = ImageOps.mirror(self.fig_imgs_resiz[EXIT_IMG])
            elif maneuver == MANEUVER_FOLLOW_MIDDLE:
                new_img = ImageOps.mirror(self.fig_imgs_resiz[MIDDLE_IMG])
            elif maneuver == MANEUVER_FOLLOW_LEFT:
                new_img = ImageOps.mirror(self.fig_imgs_resiz[RIGHT_IMG])
            elif maneuver == MANEUVER_FOLLOW_RIGHT:
                new_img = ImageOps.mirror(self.fig_imgs_resiz[LEFT_IMG])
            elif maneuver == MANEUVER_TURN_FOLLOW_MIDDLE:
                new_img = self.fig_imgs_resiz[MIDDLE_IMG]
            elif maneuver == MANEUVER_TURN_FOLLOW_LEFT:
                new_img = self.fig_imgs_resiz[LEFT_IMG]
            elif maneuver == MANEUVER_TURN_FOLLOW_RIGHT:
                new_img = self.fig_imgs_resiz[LEFT_IMG]

            if new_img is not None and car_ori * car_dir < 0:
                new_img = new_img.rotate(180)

        if new_img is not None:
            img.paste(new_img, (0, 0), new_img)

        if maneuver in [MANEUVER_TURN, MANEUVER_TURN_FOLLOW_LEFT, MANEUVER_TURN_FOLLOW_MIDDLE,
                        MANEUVER_TURN_FOLLOW_RIGHT]:
            new_img = self.fig_imgs_resiz[DIR_SW_IMG]
            img.paste(new_img, (0, 0), new_img)

        return img

    def put_car(self, car_img, node_idx, node_dir):
        if node_idx > len(self.node_info["name"]):
            node_idx = -1

        angle = math.atan2(self.node_info["dirs"][node_idx][1], self.node_info["dirs"][node_idx][0])
        self.car_img = ImageTk.PhotoImage(car_img.rotate(math.degrees(angle), expand=True))
        self.canvas.itemconfigure(self.car_img_id, image=self.car_img)
        x_basic_offs = self.car_ratio * (350 - 600 / 2)
        y_basic_offs = self.car_ratio * (162 - 324 / 2)

        car_center = [node_dir * (x_basic_offs * math.cos(angle) - y_basic_offs * math.sin(angle)),
                      node_dir * (x_basic_offs * math.sin(angle) + y_basic_offs * math.cos(angle))]

        x0 = int(self.ratio * (self.node_info["coords"][node_idx][0] - car_center[0]))
        y0 = int(self.ratio * (self.node_info["coords"][node_idx][1] + car_center[1]))

        self.canvas.coords(self.car_img_id, x0, y0)
        self.canvas.tag_raise(self.car_img)
        pass

    def update_car(self):
        img = self.make_car(self.car_state['orientation'], self.car_state['direction'], self.car_state['maneuver'])
        self.put_car(img, self.car_state['current node'], self.car_state['node_dir'])

    def node_name2idx(self, name):
        if not type(name) is str:
            name = chr(name)

        name = name.upper()
        name = ord(name)

        if not name == ord(' '):
            idx = 1 + name - ord('A')
        else:
            idx = None

        return idx

    def update_view(self):
        if self.dataholder.hasNew:
            data = self.dataholder.getData()
            for key in data.keys():
                self.car_state[key] = data[key][-1]

            for i, c_int in enumerate(
                    [self.car_state['disabled1'], self.car_state['disabled2'], self.car_state['disabled3'],
                     self.car_state['disabled4']]):
                self.disabled_car[i]['idx'] = self.node_name2idx(c_int)

            self.goal_car['idx'] = self.car_state['goal node']

            self.invalidate()
            # if self.car_state['event'] == NAVI_EVENT_CROSSING_FRONT:
            #     msg = 'NAVI_EVENT_CROSSING_FRONT'
            # elif self.car_state['event'] == NAVI_EVENT_CROSSING_REAR:
            #     msg = 'NAVI_EVENT_CROSSING_REAR'
            # elif self.car_state['event'] == NAVI_EVENT_CROSSING_LEFT:
            #     msg = 'NAVI_EVENT_CROSSING_LEFT'
            # elif self.car_state['event'] == NAVI_EVENT_START_ROUTE:
            #     msg = 'NAVI_EVENT_START_ROUTE'
            # elif self.car_state['event'] == NAVI_EVENT_EXIT_LEFT:
            #     msg = 'NAVI_EVENT_EXIT_LEFT'
            # elif self.car_state['event'] == NAVI_EVENT_DEAD_END:
            #     msg = 'NAVI_EVENT_DEAD_END'
            # elif self.car_state['event'] == NAVI_EVENT_INVALID:
            #     msg = 'NAVI_EVENT_INVALID'
            # else:
            #     msg = 'Unknown navigation event!'
            #
            # self.logger.debug(msg)

        if self._invalid:
            self.redraw()
        pass

    def on_left_click(self, event):
        self.logger.debug("Ouch, left click")

        for idx, crd in enumerate(self.node_info["coords"]):
            crd = [c * self.ratio for c in crd]
            if math.dist(crd, [event.x, event.y]) < self.ratio * 40:
                if not self.node_info['name'][idx].strip():
                    self.logger.warning(f"Node {idx} has no name, so it can't be goal!")
                    return

                for d in self.disabled_gui:
                    if d['idx'] == idx:
                        self.logger.warning(f'Node {idx} is disabled! Cannot be goal!')
                        return

                if self.goal_gui['idx'] == idx:
                    self.goal_gui['idx'] = None
                else:
                    self.goal_gui['idx'] = idx

                self.invalidate()

        pass

    def on_right_click(self, event):
        self.logger.debug("Why you poke me??")

        for idx, crd in enumerate(self.node_info["coords"]):
            crd = [c * self.ratio for c in crd]
            if math.dist(crd, [event.x, event.y]) < self.ratio * 40:
                if not self.node_info['name'][idx].strip():
                    self.logger.warning(f"Node {idx} has no name, so it can't be disabled!")
                    return

                if idx == self.goal_gui['idx']:
                    self.logger.warning(f"Node {idx} is the goal node! Cannot be disabled!")
                    return

                deleted = False
                for d in self.disabled_gui:
                    if d['idx'] == idx:
                        d['idx'] = None
                        deleted = True
                        break

                if not deleted:
                    added = False
                    for d in self.disabled_gui:
                        if d['idx'] is None:
                            d['idx'] = idx
                            added = True
                            break

                    if not added:
                        self.logger.warning("Maximum number of disabled nodes reached! Remove before adding new ones!")

                self.invalidate()
                break

        pass

    def continous_update(self):
        self.update_view()
        self.master.after(20, self.continous_update)

    def on_btn_send_click(self):
        if self.goal_gui['idx'] is None:
            self.logger.warning("No goal is given! Cannot send message!")
            return

        msg = self.node_info['name'][self.goal_gui['idx']]

        for d in self.disabled_gui:
            if d['idx'] is not None and self.node_info['name'][d['idx']] is not None:
                msg = msg + str(self.node_info['name'][d['idx']]).lower()

        msg = msg + '\n'

        self.client.send_message(self.id, {'msg': msg})

        pass

    def on_btn_random_click(self):
        disabled_num = np.random.randint(0, 5)

        goal_idx = np.random.randint(1, 16)

        self.goal_gui['idx'] = goal_idx

        disabled_idxs = []
        while len(disabled_idxs) < disabled_num:
            next_rnd = np.random.randint(1, 16)
            if next_rnd != goal_idx and next_rnd not in disabled_idxs:
                disabled_idxs.append(next_rnd)

        for i, idx in enumerate(disabled_idxs):
            self.disabled_gui[i]['idx'] = idx

        for i in range(disabled_num, 4):
            self.disabled_gui[i]['idx'] = None

        self.logger.debug(f"New Random goal: {goal_idx}, disableds: {disabled_idxs}")
        self.invalidate()
        self.on_btn_send_click()

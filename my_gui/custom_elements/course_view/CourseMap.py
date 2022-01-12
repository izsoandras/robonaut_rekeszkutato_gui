import tkinter
from PIL import ImageTk, Image, ImageOps
import json
import math
import logging
from clients.mqtt.listeners import ParamListener
from dataholders import DataHolder

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
MANEUVER_TURN_FOLLOW_LEFT = 3
MANEUVER_TURN_FOLLOW_MIDDLE = 4
MANEUVER_TURN_FOLLOW_RIGHT = 5
MANEUVER_EXIT_THROUGH = 6
MANEUVER_LANE_SW_LEFT = 7
MANEUVER_LANE_SW_RIGHT = 8
MANEUVER_STOP = 9

NAVI_EVENT_CROSSING_FRONT = 0
NAVI_EVENT_CROSSING_REAR = 1
NAVI_EVENT_CROSSING_LEFT = 2
NAVI_EVENT_EXIT_LEFT = 3
NAVI_EVENT_START_ROUTE = 4
NAVI_EVENT_INVALID = 5


class CourseMap(tkinter.Frame):
    def __init__(self, parent, client: ParamListener, id, dataholder: DataHolder, assets_path='./assets/map', *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.logger = logging.getLogger('RKID.CourseView')

        self.client = client
        self.id = id
        self.dataholder = dataholder
        self.car_state = {
            'current node': 0,
            'goal node': 16,
            'node_dir': 1,
            'orientation': 1,
            'direction': 1,
            'event': None,
            'maneuver': MANEUVER_STOP
        }

        with open(assets_path+'/course.json') as node_file:
            self.node_info = json.load(node_file)

        self.ratio = 1
        self.base_img = Image.open(assets_path+'/course.png')
        self.base_width, self.base_height = self.base_img.size
        self.canvas_img = ImageTk.PhotoImage(self.base_img)
        self.canvas = tkinter.Canvas(self, width=self.canvas_img.width(), bg='#f0f0f0', height=self.canvas_img.height())
        self.image_id = self.canvas.create_image(0, 0, anchor=tkinter.NW, image=self.canvas_img)
        self.is_resized = True
        self.resized_img = self.canvas_img

        figs_paths = ['car_car.png', 'car_dir_sw.png', 'car_exit.png', 'car_lane_left.png', 'car_lane_right.png', 'car_left.png', 'car_right.png', 'car_middle.png', 'car_STOP.png', 'car_line_sensor.png']
        self.car_ratio = 1.5/5
        self.fig_imgs = []
        self.fig_imgs_resiz = []
        for fig_path in figs_paths:
            img = Image.open(assets_path+'/figs/'+fig_path).convert('RGBA')
            self.fig_imgs.append(img.resize((int(self.car_ratio*img.width), int(self.car_ratio*img.height)), Image.ANTIALIAS))
            self.fig_imgs_resiz.append(self.fig_imgs[-1])

        self.car_base_width, self.car_base_height = self.fig_imgs[0].size
        self.car_img = ImageTk.PhotoImage(self.fig_imgs_resiz[CAR_IMG])
        self.car_img_id = self.canvas.create_image((100, 50), image=self.car_img)

        self.disabled = []
        self.goal = {'idx': None, 'tag': None}
        self.marker_rad = 20

        self.send_btn = tkinter.Button(self.canvas, text="Send", bg='RoyalBlue1', activebackground='navy', command=self.on_btn_send_click)
        # self.send_btn.pack(side=tkinter.RIGHT, anchor=tkinter.SE)
        self.send_btn.place(x=self.canvas_img.width(),
                            y=self.canvas_img.height()-10,
                            width=self.canvas_img.width()/8, height=self.canvas_img.height()/12, anchor=tkinter.SE)

        self.car_goal_marker = None

        self.canvas.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH, anchor=tkinter.NW)
        self.bind('<Configure>', self.on_resize)
        self.canvas.bind("<Button-1>",self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self._invalid = True
        self.continous_update()


    def invalidate(self):
        self._invalid = True

    def redraw(self):
        self._invalid = False
        self.update_car()

        for d in self.disabled:
            self._draw_marker(d, 'IndianRed1')

        self.disabled = [d for d in self.disabled if d['idx'] is not None]

        self._draw_marker(self.goal, 'gold')

        if self.car_goal_marker is not None:
            self.canvas.delete(self.car_goal_marker)

        if self.car_state['goal node'] is not None:
            g_x = self.node_info['coords'][self.car_state['goal node']][0]
            g_y = self.node_info['coords'][self.car_state['goal node']][1]
            self.car_goal_marker = self.canvas.create_oval(self.ratio * (g_x - self.marker_rad),
                                                   self.ratio * (g_y - self.marker_rad),
                                                   self.ratio * (g_x + self.marker_rad),
                                                   self.ratio * (g_y + self.marker_rad),
                                                   fill=None, outline='DarkGoldenrod3', width=self.ratio*10)

        self.send_btn.place(x=self.canvas_img.width(),
                            y=self.canvas_img.height() - 10,
                            width=self.canvas_img.width() / 8, height=self.canvas_img.height() / 12, anchor=tkinter.SE)



    def _draw_marker(self, marker, color):
        if marker['tag'] is not None:
            self.canvas.delete(marker['tag'])
            marker['tag'] = None

        if marker['idx'] is not None:
            x_c = self.node_info["coords"][marker['idx']][0]
            y_c = self.node_info["coords"][marker['idx']][1]

            marker["tag"] = self.canvas.create_oval(self.ratio * (x_c - self.marker_rad),
                                               self.ratio * (y_c - self.marker_rad),
                                               self.ratio * (x_c + self.marker_rad),
                                               self.ratio * (y_c + self.marker_rad),
                                               fill=color)

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
            self.fig_imgs_resiz[idx] = fig_base.resize((int(self.ratio * self.car_base_width), int(self.ratio * self.car_base_height)),
                                Image.ANTIALIAS)

        self._invalid = True
        pass

    def make_car(self, car_ori, car_dir, maneuver):
        img = Image.new('RGBA', ((int(self.ratio * self.car_base_width), int(self.ratio * self.car_base_height))), (0,0,0,0))

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

        if maneuver == MANEUVER_STOP:
            new_img = self.fig_imgs_resiz[STOP_IMG]
        elif maneuver == MANEUVER_LANE_SW_LEFT:
            new_img = self.fig_imgs_resiz[LANE_LEFT_IMG]
        elif maneuver == MANEUVER_LANE_SW_RIGHT:
            new_img = ImageOps.mirror(self.fig_imgs_resiz[LANE_RIGHT_IMG])
        else:
            if maneuver == MANEUVER_EXIT_THROUGH:
                if car_ori * car_dir > 0:
                    new_img = ImageOps.mirror(self.fig_imgs_resiz[EXIT_IMG])
                else:
                    new_img = self.fig_imgs_resiz[EXIT_IMG]
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

            if car_ori * car_dir < 0:
                new_img = new_img.rotate(180)

        img.paste(new_img, (0, 0), new_img)

        if maneuver in [MANEUVER_TURN_FOLLOW_LEFT, MANEUVER_TURN_FOLLOW_MIDDLE, MANEUVER_TURN_FOLLOW_RIGHT]:
            new_img = self.fig_imgs_resiz[DIR_SW_IMG]

        img.paste(new_img, (0, 0), new_img)

        return img

    def put_car(self, car_img, node_idx, node_dir):
        angle = math.atan2(self.node_info["dirs"][node_idx][1], self.node_info["dirs"][node_idx][0])
        self.car_img = ImageTk.PhotoImage(car_img.rotate(math.degrees(angle), expand=True))
        self.canvas.itemconfigure(self.car_img_id, image=self.car_img)
        x_basic_offs = self.car_ratio * (350 - 600/2)
        y_basic_offs = self.car_ratio * (162 - 324/2)

        car_center = [node_dir * (x_basic_offs * math.cos(angle) - y_basic_offs * math.sin(angle)),
                      node_dir * (x_basic_offs * math.sin(angle) + y_basic_offs * math.cos(angle))]

        x0 = int(self.ratio * (self.node_info["coords"][node_idx][0] - car_center[0]))
        y0 = int(self.ratio * (self.node_info["coords"][node_idx][1] + car_center[1]))

        self.canvas.coords(self.car_img_id, x0, y0)
        pass

    def update_car(self):
        img = self.make_car(self.car_state['orientation'], self.car_state['direction'], self.car_state['maneuver'])
        self.put_car(img, self.car_state['current node'], self.car_state['node_dir'])

    def update_view(self):
        if self.dataholder.hasNew:
            self.car_state = self.dataholder.getData()[-1]
            self.invalidate()
            if self.car_state['event'] == NAVI_EVENT_CROSSING_FRONT:
                msg = 'NAVI_EVENT_CROSSING_FRONT'
            elif self.car_state['event'] == NAVI_EVENT_CROSSING_REAR:
                msg = 'NAVI_EVENT_CROSSING_REAR'
            elif self.car_state['event'] == NAVI_EVENT_CROSSING_LEFT:
                msg = 'NAVI_EVENT_CROSSING_LEFT'
            elif self.car_state['event'] == NAVI_EVENT_START_ROUTE:
                msg = 'NAVI_EVENT_START_ROUTE'
            elif self.car_state['event'] == NAVI_EVENT_EXIT_LEFT:
                msg = 'NAVI_EVENT_EXIT_LEFT'
            elif self.car_state['event'] == NAVI_EVENT_INVALID:
                msg = 'NAVI_EVENT_INVALID'
            else:
                msg = 'Unknown navigation event!'

            self.logger.info(msg)

        if self._invalid:
            self.redraw()
        pass

    def on_left_click(self, event):
        self.logger.debug("Ouch, left click")

        for idx, crd in enumerate(self.node_info["coords"]):
            crd = [c * self.ratio for c in crd]
            if math.dist(crd, [event.x, event.y]) < self.ratio * 40:
                for d in self.disabled:
                    if d['idx'] == idx:
                        self.logger.warning('This node is disabled! Cannot be goal!')
                        return

                if self.goal['idx'] == idx:
                    self.goal['idx'] = None
                else:
                    self.goal['idx'] = idx

                self.invalidate()

        pass

    def on_right_click(self, event):
        self.logger.debug("Why you poke me??")

        for idx, crd in enumerate(self.node_info["coords"]):
            crd = [c*self.ratio for c in crd]
            if math.dist(crd, [event.x, event.y]) < self.ratio * 40:
                if idx == self.goal['idx']:
                    self.logger.warning("This node is the goal node! Cannot be disabled!")
                    return

                deleted = False
                for d in self.disabled:
                    if d['idx'] == idx:
                        d['idx'] = None
                        deleted = True
                        break

                if not deleted:
                    if len(self.disabled) < 4:
                        self.disabled.append({
                            "idx": idx,
                            "tag": None
                        })
                    else:
                        self.logger.warning("Maximum number of disabled nodes reached! Remove before adding new ones!")

                self.invalidate()
                break

        pass

    def continous_update(self):
        self.update_view()
        self.master.after(20, self.continous_update)

    def on_btn_send_click(self):
        if self.goal['idx'] is None:
            self.logger.warning("No goal is given! Cannot send message!")
            return

        msg = self.node_info['name'][self.goal['idx']]

        for d in self.disabled:
            if self.node_info['name'][d['idx']] is not None:
                msg = msg + self.node_info['name'][d['idx']]

        msg = msg + '\n'

        self.client.send_message(self.id, {'msg': msg})

        pass

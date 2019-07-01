import random
import numpy as np
import tkinter as tk
import tkinter.font as tkf
from get_dubins import dubins
from PIL import Image, ImageTk


# shift the window to screen_center
def center_window(win, width=None, height=None):
    screenwidth = win.winfo_screenwidth()
    screenheight = win.winfo_screenheight()
    if width is None:
        width, height = get_window_size(win)[:2]
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/3)
    win.geometry(size)


# get the size of window
def get_window_size(win, update=True):
    if update:
        win.update()
    return win.winfo_width(), win.winfo_height(), win.winfo_x(), win.winfo_y()


# resize the image
def resize_img(img, w_box, h_box, keep_ratio=True):
    temp_width, temp_height = img.size
    width, height = w_box, h_box
    if keep_ratio:
        if temp_width > temp_height:
            width = w_box
            height = int(h_box * (1.0 * temp_height / temp_width))
        if temp_height >= temp_width:
            height = h_box
            width = int(w_box * (1.0 * temp_width / temp_height))
    img1 = img.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(img1)


# get the component based on input image
def image_label(frame, img, width, height, keep_ratio=True):
    if isinstance(img, str):
        _img = Image.open(img)
    else:
        _img = img
    lbl_image = tk.Label(frame, width=width, height=height)
    tk_img = resize_img(_img, width, height, keep_ratio)
    lbl_image.image = tk_img
    lbl_image.config(image=tk_img)
    return lbl_image


# set font
def _font(font='微软雅黑', size=12, bold=tkf.NORMAL):
    ft = tkf.Font(family=font, size=size, weight=bold)
    return ft


# sample font
def _ft(size=12, bold=False):
    if bold:
        return _font(size=size, bold=tkf.BOLD)
    else:
        return _font(size=size, bold=tkf.NORMAL)


def h_separator(parent, height=2):  # height 单位为像素值
    # 水平分割线, 水平填充
    tk.Frame(parent, height=height, bg='white smoke').pack(fill=tk.X)


def v_separator(parent, width, bg='white smoke'):  # width 单位为像素值
    # 垂直分割线 , fill=tk.Y, 但如何定位不确定，直接返回对象，由容器决定
    frame = tk.Frame(parent, width=width, bg=bg)
    return frame


class UavGroup(object):
    def __init__(self, size, mission, plane):
        self.mission = mission
        self.plane = plane
        self.angles = [10 * i for i in range(36)]  # candidates
        self.approach_angle = []  # in action
        self.size = size
        self.limit_angles = []  # in action
        self.population = []  # in action
        self.target_coord = []  # coordinates of targets
        self.target_number = []  # in action
        self.mission_type = []  # in action
        self.uav = []  # in action
        self.uav_number = []  # candidates
        self.uav_type = []  # candidates
        self.type_uav = []  # in action
        self.payload = []  # in action
        self.mission_payload = []  # candidates
        self.limit_r = []  # candidates
        self.start_angle = []  # candidates
        self.start_position = []  # candidates
        self.get_mission()  # information of target
        self.get_population()

    def get_mission(self):
        # print('TARGET NUMBER & MISSION TYPE & TARGET COORDINATES: ')
        for ele in self.mission:
            s = ele.split()
            for i in range(1, len(s) - 4):
                self.target_number.append(s[0])
                self.mission_type.append(s[i])
            self.target_coord.append((float(s[-4]), float(s[-3])))
            self.limit_angles.append((float(s[-2]), float(s[-1])))

    def get_population(self):
        self.get_uav()
        for i in range(self.size):
            self.uav, self.approach_angle = [], []
            for j in range(len(self.mission_type)):
                while True:
                    temp = random.sample(self.uav_number, 1)[0]
                    if self.uav_type[temp - 1] == 'V' or self.uav_type[temp - 1] == self.mission_type[j]:
                        break
                self.uav.append(temp)
            self.payload = [self.mission_payload[ele - 1] for ele in self.uav]
            for p in range(len(self.target_number)):
                temp_minimum = float(self.limit_angles[int(self.target_number[p]) - 1][0])
                temp_maximum = float(self.limit_angles[int(self.target_number[p]) - 1][1])
                index = random.sample([q for q in range(int((temp_maximum - temp_minimum) // 10))], 1)[0]
                temp_angle = temp_minimum + index * 10
                self.approach_angle.append(temp_angle)
            # self.approach_angle = random.sample(self.angles, len(self.target_number))
            self.type_uav = [self.uav_type[ele - 1] for ele in self.uav]
            temp = [self.target_number, self.mission_type, self.uav, self.approach_angle, self.payload, self.type_uav]
            self.population.append(np.array(temp))

    def get_uav(self):
        # print('UAV NUMBER & TYPE & PAYLOAD & LIMIT RADIUS & POSITION & ANGLE: ')
        for ele in self.plane:
            s = ele.split()
            self.uav_number.append(int(s[0]))
            self.uav_type.append(s[1])
            self.mission_payload.append(float(s[2]))
            self.limit_r.append(float(s[3]))
            self.start_position.append((float(s[4]), float(s[5])))
            self.start_angle.append(int(s[-1]))


class GA(UavGroup):
    def __init__(self, size, epoch, mission, plane, text, f, inherit_rate=0.3, mutation_rate=1.0):
        super().__init__(size, mission, plane)
        self.best = None
        self.acc = []
        self.cost = []
        self.epoch = epoch
        self.inherit_rate = inherit_rate
        self.mutation_rate = mutation_rate
        self.epoch_count = 0
        self.text = text
        self.f = f
        self.fun()

    @staticmethod
    def get_para(char):
        if char == 'C':
            return 1.2
        elif char == 'A':
            return 1.0
        return 1.5

    @staticmethod
    def show(mat):
        token = ['TARGET NUMBER', 'MISSION TYPE', 'UAV NUMBER', 'ANGLES', 'PAYLOAD', 'UAV TYPE']
        for i in range(mat.shape[0]):
            print(token[i] + ' ' * (16 - len(token[i])) + ': ', mat[i])

    def fun(self):
        token = ['TARGET NUMBER', 'MISSION TYPE', 'UAV NUMBER', 'ANGLES', 'PAYLOAD', 'UAV TYPE']
        self.text.delete(0.0, tk.END)
        print('epoch ' + str(self.epoch_count) + ' : ', end='')
        self.cost, index, self.epoch_count = [], 0, self.epoch_count + 1
        for ele in self.population:
            total = 0
            for i in range(ele.shape[1]):
                uav_number = int(ele[2, i]) - 1
                total += self.get_para(ele[-1, i]) * float(ele[4, i]) * self.get_length(
                             uav_number, self.target_coord[int(ele[0, i]) - 1][0],
                             self.target_coord[int(ele[0, i]) - 1][1], self.limit_r[int(ele[2, i]) - 1],
                             float(ele[3, i]))
            self.cost.append((index, total))
            index += 1
        self.cost = sorted(self.cost, key=lambda x: x[-1])
        self.best = (self.population[self.cost[0][0]], self.cost[0][-1])
        print('%.4f' % self.best[-1])
        string = 'epoch ' + str(self.epoch_count) + ' : ' + str(self.best[-1]) + '\n\n'
        self.text.insert(tk.END, string)
        for p in range(self.best[0].shape[0]):
            temp_str = token[p] + ' ' * (16 - len(token[p])) + ': ' + str(self.best[0][p, :]) + '\n'
            self.text.insert(tk.END, temp_str)
        self.f.update()

    def get_length(self, index, a, b, r, theta):
        return dubins([float(self.start_position[index][0]), float(self.start_position[index][1]),
                       self.start_angle[index]], [a, b, theta], r)

    def get_next_generation(self):
        for i in range(int(self.size * (1 - self.inherit_rate))):
            self.population[self.cost[-i-1][0]] = self.get_gene()
        self.mutation()
        self.fun()

    def mutation(self):
        if random.uniform(0, 1) <= self.mutation_rate:
            col = self.population[0].shape[1]
            for index in range(len(self.population)):
                if index != self.cost[0][0]:
                    for ele in range(col):
                        self.mutation_change(index, ele)

    def mutation_change(self, index, point):
        while True:
            if self.population[index][1, point] != 'V':
                temp = random.sample(self.uav_number, 1)[0]
                if (self.population[index][1, point] == self.uav_type[temp - 1] and self.uav_type[temp - 1] !=
                        self.population[index][-1, point]) or self.uav_type[temp - 1] == 'V':
                    self.population[index][2, point] = temp
                    self.population[index][4, point] = self.mission_payload[temp - 1]
                    self.population[index][5, point] = self.uav_type[temp - 1]
                    self.population[index][3, point] = self.greedy_angle(index, point)
                    break
            else:
                while True:
                    temp = random.sample(self.uav_number, 1)[0]
                    if self.uav_type[temp - 1] == 'V':
                        break
                self.population[index][2, point] = temp
                self.population[index][4, point] = self.mission_payload[temp - 1]
                self.population[index][5, point] = self.uav_type[temp - 1]
                self.population[index][3, point] = self.greedy_angle(index, point)
                break

    def greedy_angle(self, index, point):
        cost = []
        minimum = float(self.limit_angles[int(self.population[index][0, point]) - 1][0])
        maximum = float(self.limit_angles[int(self.population[index][0, point]) - 1][1])
        for ele in self.angles:
            if minimum <= ele <= maximum:
                total, temp_index = 0, int(self.population[index][2, point]) - 1
                angle = float(self.population[index][4, point])
                total += self.get_para(self.population[index][-1, point]) * angle * self.get_length(
                    temp_index, self.target_coord[int(self.population[index][0, point]) - 1][0],
                    self.target_coord[int(self.population[index][0, point]) - 1][1],
                    self.limit_r[int(self.population[index][2, point]) - 1], ele)
                cost.append((ele, total))
            cost = sorted(cost, key=lambda x: x[-1])
        return cost[0][0]

    # cross operation
    def get_gene(self):
        p1, p2 = self.population[self.get_index()].copy(), self.population[self.get_index()].copy()
        point = random.randint(0, self.population[0].shape[1] - 1)
        p1[:, point:], p2[:, point:] = p2[:, point:], p1[:, point:]
        return p1

    # roulette
    def get_index(self):
        self.acc, add = [], 0
        for ele in self.cost:
            add += ele[-1]
            self.acc.append(add)
        self.acc = [ele / add for ele in self.acc]
        temp = random.uniform(0, 1)
        for i in range(len(self.acc)):
            if temp <= self.acc[i]:
                return i

    def run(self):
        token = ['TARGET NUMBER', 'MISSION TYPE', 'UAV NUMBER', 'ANGLES', 'PAYLOAD', 'UAV TYPE']
        for i in range(self.epoch):
            self.get_next_generation()
        print('BEST SOLUTION AFTER ' + str(self.epoch) + ' EPOCHS :  ', self.best[-1])
        for i in range(self.best[0].shape[0]):
            print(token[i] + ' ' * (16 - len(token[i])) + ': ', self.best[0][i])


class UAV(object):
    def __init__(self):
        self.size = 10
        self.epochs = 30
        self.inherit = 0.2
        self.mutation = 0.8
        self.first = []
        self.second = []


class Window(object):
    def __init__(self, parent=None):
        self.inf = UAV()
        self.root = tk.Tk()
        self.parent = parent
        self.root.geometry('1200x800')
        center_window(self.root)
        self.root.title('遗传算法')
        self.root.iconbitmap('xjtu.ico')
        self.root.grab_set()
        self.body()

    def body(self):
        self.title(self.root).pack(fill=tk.X)
        self.main(self.root).pack(expand=tk.YES, fill=tk.BOTH)
        self.bottom(self.root).pack(fill=tk.X)

    @staticmethod
    def title(parent):
        def label(temp_frame, text, size, bold=False):
            return tk.Label(temp_frame, text=text, bg='black', fg='white', height=2, font=_ft(size, bold))
        frame = tk.Frame(parent, bg='black')
        label(frame, 'SEAD协同任务分配系统', 16, True).pack(side=tk.LEFT, padx=10)
        image_label(frame, 'cv.png', 60, 60, False).pack(side=tk.RIGHT)
        return frame

    @staticmethod
    def bottom(parent):
        frame = tk.Frame(parent, height=10, bg='white smoke')
        frame.propagate(True)
        return frame

    def main(self, parent):
        frame = tk.Frame(parent, bg='white smoke')
        self.main_top(frame).pack(fill=tk.X, padx=30, pady=15)
        self.main_left(frame).pack(side=tk.LEFT, fill=tk.Y, padx=30)
        v_separator(frame, 30).pack(side=tk.RIGHT, fill=tk.Y)
        self.main_right(frame).pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)
        return frame

    def main_top(self, parent):
        frame = tk.Frame(parent, bg='white', height=150)
        image_label(frame, 'gene.jpg', width=240, height=120, keep_ratio=False).pack(side=tk.LEFT, padx=10, pady=10)
        self.main_top_middle(frame).pack(side=tk.LEFT)
        frame.propagate(False)
        return frame

    def main_top_middle(self, parent):
        str1 = '参考文献：基于SEAD任务特性约束的协同任务分配方法---吴蔚楠，关英姿，郭继峰，崔乃刚'
        str2 = '说明：为了加快收敛速度，在变异过程中采用了贪心算法，并且上一代的最优个体直接进入下一代'

        def label(temp_frame, text):
            return tk.Label(temp_frame, bg='white', fg='gray', text=text, font=_ft(12))
        frame = tk.Frame(parent, bg='white')
        self.main_top_middle_top(frame).pack(anchor=tk.NW)
        label(frame, str1).pack(anchor=tk.W, padx=10, pady=2)
        label(frame, str2).pack(anchor=tk.W, padx=10)
        return frame

    @staticmethod
    def main_top_middle_top(parent):
        def label(temp_frame, text, size=12, bold=True, fg='blue'):
            return tk.Label(temp_frame, text=text, bg='white', fg=fg, font=_ft(size, bold))
        frame = tk.Frame(parent, bg='white')
        label(frame, '基于遗传算法的任务调配', 20, True, 'black').pack(side=tk.LEFT, padx=10)
        return frame

    @staticmethod
    def main_left(parent):
        def label(temp_frame, text, size=10, bold=False, bg='white'):
            return tk.Label(temp_frame, text=text, bg=bg, font=_ft(size, bold))
        frame = tk.Frame(parent, width=180, bg='white')
        label(frame, '模型内容', 12, True).pack(anchor=tk.W, padx=20, pady=10)
        label(frame, '任务背景').pack(anchor=tk.W, padx=40, pady=5)
        label(frame, '论文详解').pack(anchor=tk.W, padx=40, pady=5)
        f1 = tk.Frame(frame, bg='white smoke')
        v_separator(f1, width=5, bg='blue').pack(side=tk.LEFT, fill=tk.Y)
        label(frame, '模型说明').pack(anchor=tk.W, padx=40, pady=5)
        label(f1, '遗传算法', bg='white smoke').pack(side=tk.LEFT, anchor=tk.W, padx=35, pady=5)
        f1.pack(fill=tk.X)
        label(frame, '模型总结').pack(anchor=tk.W, padx=40, pady=5)
        h_separator(frame, 10)
        label(frame, '数据中心', 12, True).pack(anchor=tk.W, padx=20, pady=10)
        label(frame, '测试样例').pack(anchor=tk.W, padx=40, pady=5)
        label(frame, '创建数据').pack(anchor=tk.W, padx=40, pady=5)
        frame.propagate(False)
        return frame

    def main_right(self, parent):
        def label(temp_frame, text, size=10, bold=False, fg='black'):
            return tk.Label(temp_frame, text=text, bg='white', fg=fg, font=_ft(size, bold))

        def space(n):
            return int(n) * ' '
        frame = tk.Frame(parent, width=200, bg='white')
        label(frame, '创建模型', 12, True).pack(anchor=tk.W, padx=20, pady=5)
        h_separator(frame)

        f_remind = tk.Frame(frame, bg='white')
        text_remind = tk.Text(f_remind, width=160, height=2, fg='red')
        text_remind.pack(side=tk.LEFT)
        initial_str = space(40) + '系统提醒 ： 无事件'
        text_remind.insert(tk.END, initial_str)
        f_remind.pack(fill=tk.X)

        f0 = tk.Frame(frame, bg='white')
        label(f0, space(8) + '模型类别：').pack(side=tk.LEFT, pady=5)
        label(f0, '遗传算法').pack(side=tk.LEFT, padx=20)
        f0.pack(fill=tk.X)

        f1 = tk.Frame(frame, bg='white')
        label(f1, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f1, '遗传概率   ：').pack(side=tk.LEFT)
        get_inf1 = tk.Entry(f1, bg='white', font=_ft(10), width=15, show=None)

        def get_first():
            temp1 = get_inf1.get().strip().split()
            if temp1 and 0 < float(temp1[0]) < 1:
                self.inf.inherit = float(temp1[0])
                str_first = space(40) + '系统提醒 ： 输入遗传概率为' + str(temp1[0])
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_first)
            else:
                str_first = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_first)
        get_inf1.pack(side=tk.LEFT, padx=20)
        tk.Button(f1, text='确认', width=20, height=1, command=get_first).pack(side=tk.LEFT, padx=20)
        f1.pack(fill=tk.X)

        f2 = tk.Frame(frame, bg='white')
        label(f2, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f2, '变异概率   ：').pack(side=tk.LEFT)
        get_inf2 = tk.Entry(f2, bg='white', font=_ft(10), width=15, show=None)

        def get_second():
            temp2 = get_inf2.get().strip().split()
            if temp2 and 0 < float(temp2[0]) < 1:
                self.inf.mutation = float(temp2[0])
                str_second = space(40) + '系统提醒 ： 输入变异概率为' + str(temp2[0])
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_second)
            else:
                str_second = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_second)
        get_inf2.pack(side=tk.LEFT, padx=20)
        tk.Button(f2, text='确认', width=20, height=1, command=get_second).pack(side=tk.LEFT, padx=20)
        f2.pack(fill=tk.X)

        f3 = tk.Frame(frame, bg='white')
        label(f3, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f3, '每代个体数：').pack(side=tk.LEFT)
        get_inf3 = tk.Entry(f3, bg='white', font=_ft(10), width=15, show=None)

        def get_third():
            temp3 = get_inf3.get().strip().split()
            if temp3:
                self.inf.size = int(temp3[0])
                str_third = space(40) + '系统提醒 ： 每代个体数为' + str(temp3[0])
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_third)
            else:
                str_third = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_third)
        get_inf3.pack(side=tk.LEFT, padx=20)
        tk.Button(f3, text='确认', width=20, height=1, command=get_third).pack(side=tk.LEFT, padx=20)
        f3.pack(fill=tk.X)

        f4 = tk.Frame(frame, bg='white')
        label(f4, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f4, '迭代总次数：').pack(side=tk.LEFT)
        get_inf4 = tk.Entry(f4, bg='white', font=_ft(10), width=15, show=None)

        def get_forth():
            temp4 = get_inf4.get().strip().split()
            if temp4:
                self.inf.epochs = int(temp4[0])
                str_forth = space(40) + '系统提醒 ： 迭代总次数为' + str(temp4[0])
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_forth)
            else:
                str_forth = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_forth)
        get_inf4.pack(side=tk.LEFT, padx=20)
        tk.Button(f4, text='确认', width=20, height=1, command=get_forth).pack(side=tk.LEFT, padx=20)
        f4.pack(fill=tk.X)

        f5 = tk.Frame(frame, bg='white')
        label(f5, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f5, '目标编号 && 任务类型 && 坐标位置 && 末端角度限制：').pack(side=tk.LEFT)
        get_inf5 = tk.Entry(f5, bg='white', font=_ft(10), width=15)

        def get_fifth():
            temp5 = get_inf5.get().strip()
            if temp5:
                self.inf.first.append(temp5)
                str_fifth = space(28) + '目标信息 ：目标编号 && 任务类型 && 坐标位置 && 末端角度限制 ：' + temp5
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_fifth)
            else:
                str_fifth = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_fifth)
        get_inf5.pack(side=tk.LEFT, padx=20)
        tk.Button(f5, text='确认', width=20, height=1, command=get_fifth).pack(side=tk.LEFT, padx=20)

        def del_fifth():
            if len(self.inf.first):
                temp_fifth = self.inf.first.pop()
                str_temp_fifth = space(40) + '系统提醒 ： 删除数据 ' + temp_fifth
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_temp_fifth)
            else:
                str_temp_fifth = space(40) + '系统提醒 ： 无目标数据'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_temp_fifth)
        tk.Button(f5, text='清除上一条', width=20, height=1, command=del_fifth).pack(side=tk.LEFT, padx=20)
        f5.pack(fill=tk.X)

        f6 = tk.Frame(frame, bg='white')
        label(f6, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f6, '飞机编号及类型&&任务载荷&&转弯半径&&位置及角度：').pack(side=tk.LEFT)
        get_inf6 = tk.Entry(f6, bg='white', font=_ft(10), width=15)

        def get_sixth():
            temp6 = get_inf6.get().strip()
            if temp6:
                self.inf.second.append(temp6)
                str_sixth = space(26) + 'UAV信息 ： 飞机编号 && 类型 && 任务载荷 && 转弯半径 && 位置及角度 ：' + temp6
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_sixth)
            else:
                str_sixth = space(40) + '系统提醒 ： 请输入'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_sixth)
        get_inf6.pack(side=tk.LEFT, padx=20)
        tk.Button(f6, text='确认', width=20, height=1, command=get_sixth).pack(side=tk.LEFT, padx=20)

        def del_sixth():
            if len(self.inf.second):
                temp_sixth = self.inf.second.pop()
                str_temp_sixth = space(40) + '系统提醒 ： 删除数据 ' + temp_sixth
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_temp_sixth)
            else:
                str_temp_sixth = space(40) + '系统提醒 ： 无UAV数据'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_temp_sixth)
        tk.Button(f6, text='清除上一条', width=20, height=1, command=del_sixth).pack(side=tk.LEFT, padx=20)
        f6.pack(fill=tk.X)

        f7 = tk.Frame(frame, bg='white')
        label(f7, space(5) + '*', fg='red').pack(side=tk.LEFT, pady=5)
        label(f7, '清除数据：').pack(side=tk.LEFT)

        def clear():
            self.inf.first, self.inf.second = [], []
            str_del = space(40) + '系统提醒 ： 所有数据已清除'
            text_remind.delete(0.0, tk.END)
            text_remind.insert(tk.END, str_del)
        tk.Button(f7, text='清除全部', width=20, height=1, command=clear).pack(side=tk.LEFT, padx=20)
        f7.pack(fill=tk.X)

        f8 = tk.Frame(frame, bg='white')
        label(f8, space(5) + '*', fg='red').pack(side=tk.LEFT, anchor=tk.N, pady=5)
        label(f8, '开始计算：').pack(side=tk.LEFT, anchor=tk.N, pady=5)

        def start():
            if len(self.inf.first) and len(self.inf.second):
                str_start = space(40) + '系统提醒 ： 正在计算......'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_start)
                ga = GA(self.inf.size, self.inf.epochs, self.inf.first,
                        self.inf.second, text_show, f8, self.inf.inherit, self.inf.mutation)
                ga.run()
                str_end = space(40) + '系统提醒 ： 无事件'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_end)
            else:
                str_start = space(40) + '系统提醒 ： 数据无效'
                text_remind.delete(0.0, tk.END)
                text_remind.insert(tk.END, str_start)
        text_show = tk.Text(f8, width=60, height=10)
        f8.update()
        tk.Button(f8, text='开始', width=20, height=1, command=start).pack(side=tk.LEFT, padx=20)
        text_show.pack(side=tk.LEFT)
        f8.pack(fill=tk.X)
        return frame


if __name__ == '__main__':
    w = Window()
    w.root.mainloop()

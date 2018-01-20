import random
import math
from time import strftime

import wx

START = 200
CIRCLE_GAP = 25
WIDTH = 800
HEIGHT = 600
PI = 3.1415
SMALL_CIRCLE_PEN_WIDTH = 2
BIG_CIRCLE_PEN_WIDTH = 6
WINDOW_CENTER = [WIDTH // 2, HEIGHT // 2]


class ClockFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetSize((WIDTH, HEIGHT))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(1000)
        self.Show(True)

        self.circle_radius = [200, 180, 155, 135, 110, 90, 65]
        self.used_angles = []
        self.ellipses = []

    def on_paint(self, _):
        canvas = wx.BufferedPaintDC(self)
        self.draw(canvas)

    def on_timer(self, _=None):
        canvas = wx.BufferedDC(wx.ClientDC(self))
        self.draw(canvas)

    def draw(self, canvas):
        canvas.SetBackground(wx.Brush(self.GetBackgroundColour()))
        canvas.Clear()

        self.used_angles = []

        self.draw_circles(canvas)
        canvas.SetPen(wx.Pen(wx.BLACK, 3))
        self.draw_gallifreyan(canvas)

    def draw_circles(self, canvas):
        for i, radius in enumerate(self.circle_radius):
            stroke_size = 2
            if i % 2 == 0 and i != 0 and i != len(self.circle_radius) - 1:
                stroke_size = 4
            elif i % 2 == 0 and i == len(self.circle_radius) - 1:
                stroke_size = 8
            canvas.SetPen(wx.Pen(wx.BLACK, stroke_size))
            canvas.DrawCircle((WIDTH // 2, HEIGHT // 2), radius)

    def draw_gallifreyan(self, canvas):
        tf = strftime("%H:%M:%S")
        self.draw_time(canvas, tf)

        t = tf.replace(":", "")
        lines = []
        for i, digit in enumerate(t):
            lines = self.advance_all_lines(lines, i)
            digit = self.draw_circle_if_digit_gr_five(canvas, int(digit), i)

            for j in range(digit):
                try:
                    start, end = self.get_extended_lines_start_and_end(canvas, lines[j])
                except IndexError:
                    start, end = self.get_new_lines_start_and_end(i)
                    lines.append([start, end, i])
                canvas.DrawLine(*start, *end)

    def draw_time(self, canvas, tf):
        canvas.SetFont(wx.Font(30, wx.SWISS, wx.NORMAL, wx.NORMAL))
        tw, th = canvas.GetTextExtent(tf)
        canvas.DrawText(tf, WIDTH//2-tw/2, 40)

    def advance_all_lines(self, lines, i):
        for j, line in enumerate(lines):
            neu_start = lines[j][1]
            direction = [neu_start[i] - WINDOW_CENTER[i] for i in range(len(neu_start))]
            ratio = self.circle_radius[i + 1] / self.circle_radius[i]
            end_of_line = [WINDOW_CENTER[i] + ratio * direction[i] for i in range(len(neu_start))]

            lines[j] = [neu_start, end_of_line, i]
        return lines

    def draw_circle_if_digit_gr_five(self, canvas, digit, i):
        if digit > 5:
            circle_center, diameter = self.get_five_as_circle(self.circle_radius[i], self.circle_radius[i + 1])
            canvas.DrawCircle(*circle_center, diameter)
            return digit - 5
        return digit

    def get_five_as_circle(self, diameter_left, diameter_right):
        window_center = [WIDTH // 2, HEIGHT // 2]
        stuetz = self.get_random_point_on_circle(diameter_left)
        direction = [window_center[i] - stuetz[i] for i in range(len(stuetz))]
        circle_center = [stuetz[i] + (1 - diameter_right / diameter_left) / 2 * direction[i] for i in
                         range(len(stuetz))]

        return circle_center, (diameter_right - diameter_left) / 2

    def get_extended_lines_start_and_end(self, canvas, line):
        neu_start = line[0]
        end_of_line = line[1]

        return neu_start, end_of_line

    def get_new_lines_start_and_end(self, i):
        point_on_circle = self.get_random_point_on_circle(self.circle_radius[i])
        direction = [point_on_circle[i] - WINDOW_CENTER[i] for i in range(len(point_on_circle))]

        start_of_line = [WINDOW_CENTER[i] + 1.0 * direction[i] for i in range(len(point_on_circle))]
        ratio = self.circle_radius[i+1]/self.circle_radius[i]
        end_of_line = [WINDOW_CENTER[i] + ratio * direction[i] for i in range(len(point_on_circle))]

        return start_of_line, end_of_line

    def get_random_point_on_circle(self, diameter):
        angle = self.get_angle()
        if self.used_angles:
            while min([abs(k - angle) for k in self.used_angles]) < .5:
                angle = self.get_angle()
        self.used_angles.append(angle)

        return int(math.cos(angle) * diameter + WIDTH // 2), int(math.sin(angle) * diameter + HEIGHT // 2)

    def get_angle(self):
        return random.random() * PI * 2


if __name__ == "__main__":
    app = wx.App(False)
    frame = ClockFrame(None, wx.ID_ANY, "Gallifreyan Clock")
    app.MainLoop()

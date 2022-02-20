import os
import shutil
from glob import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import colorsys
from scipy.interpolate import interp1d


class axiom():

    def __init__(self):
        self.stats_SPL = {}
        self.me = os.getcwd()
        self.stats_dir = os.path.join(self.me, "STATS")


    ### Load .JSON SPL stats from STATS and save to SPL dictionary
    def load_stats(self):
        master = {}
        to_search = self.stats_dir+"/*/*"
        dirs = glob(to_search, recursive = True)
        target = os.path.join(dirs[0], os.listdir(dirs[0])[0])
        with open(target) as json_file:
            data = json.load(json_file)
            bin_length = len(data['SPL']["data"])
        for dir in dirs:
            room = dir.split(os.sep)[-2]
            master[room] = {"target": [0]*bin_length, "masks": [0]*bin_length}
        for dir in dirs:
            room = dir.split(os.sep)[-2]
            type = dir.split(os.sep)[-1]
            for file in os.listdir(dir):
                filename = os.fsdecode(file)
                target = os.path.join(dir, filename)
                with open(target) as json_file:
                    data = json.load(json_file)
                    for i, point in enumerate(master[room][type]):
                        master[room][type][i] += 10**(data["SPL"]["data"][i]/20)
            for i, point in enumerate(master[room][type]):
                num = round(20*np.log10(point+0.0000001), 2)
                if num > 0:
                    master[room][type][i] = num
                else:
                    master[room][type][i] = 0
        self.stats_SPL = master


    ### plot frequency distribution of targets and masks of rooms
    def plot_tar_mask(self, rooms):
        x = [125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        for room in rooms:
            a = self.stats_SPL[room]["target"][:8]
            b = self.stats_SPL[room]["masks"][:8]
            plt.plot(x, a, label = f"{room} target")
            plt.plot(x, b, label = f"{room} masks")
        plt.ylim([60,125])
        plt.title(f"{room} target vs mask frequency distribution")
        plt.legend()
        plt.show()


    ### plot a-weighted totals of targets and masks of rooms
    def plot_totals(self, rooms):
        bars = []
        heights = []
        colours = []
        for room in rooms:
            target = self.stats_SPL[room]["target"][-1]
            masks_sum = self.stats_SPL[room]["masks"][-1]
            spl_to_hue = interp1d([0,130],[230,0])
            m_hue = spl_to_hue(masks_sum)
            t_hue = spl_to_hue(target)
            m_rgb = colorsys.hsv_to_rgb(m_hue/100,1,1)
            t_rgb = colorsys.hsv_to_rgb(t_hue/100,1,1)
            heights.append(masks_sum)
            heights.append(target)
            bars.append(f"{room} mask")
            bars.append( f"{room} target")
            colours.append(m_rgb)
            colours.append(t_rgb)
        plt.bar(bars, heights, color=colours)
        plt.title("dB SPL comparison")
        plt.show()


    ### plot differences of target - masks_total for rooms
    def plot_difs(self, rooms):
        bars = []
        heights = []
        colours = []
        for room in rooms:
            dif = self.stats_SPL[room]["target"][-1] - self.stats_SPL[room]["masks"][-1]
            spl_to_hue = interp1d([-130,130],[0,230])
            hue = spl_to_hue(dif)
            rgb = colorsys.hsv_to_rgb(hue/100,1,1)
            heights.append(dif)
            bars.append(f"{room} dif")
            colours.append(rgb)
        plt.bar(bars, heights, color=colours)
        plt.title("dB SPL target above masks")
        plt.show()


cap = axiom()
cap.load_stats()

cap.plot_tar_mask(["room_1", "room_2"])
cap.plot_totals(["room_1", "room_2"])
cap.plot_difs(["room_1", "room_2"])
from cgi import test
from dataclasses import replace
from fileinput import filename
import os
from posixpath import split
import shutil
import json

# pyautogui

me = os.getcwd()

class walle():

    def __init__(self, me):
        self.me = me
        self.out = os.path.join(me, "SORTED")
        self.dump = os.path.join(me, "DUMP")
        self.ins = os.path.join(me, "INS")
        self.stats = os.path.join(me, "STATS")
        self.from_CATT = os.path.join(me, "OUT")
        self.project = ""
        self.m_dict = {}
        self.stat_dict = {}
        self.room_dict = {}


    ### make function to copy all the .SIM files to DUMP
    def move_SIM(self):
        for file in os.listdir(self.from_CATT):
            filename = os.fsdecode(file)
            if filename.split(".")[1] == "SIM":
                target_file = os.path.join(self.from_CATT, filename)
                shutil.copy(target_file, os.path.join(self.me, self.dump))


    ### create a dictionary of all [sample names: file names]
    def load_dict(self):
        for file in os.listdir(self.dump):
            filename = os.fsdecode(file)
            if len(self.project) == 0:
                self.project = filename.split("_A0")[0]
            sample = filename.replace(self.project+"_", "")
            if "_L.SIM" in sample:
                s_name = sample.replace("_L.SIM", "")
                self.m_dict[s_name] = [None, None]
                self.m_dict[s_name][0] = filename
            elif "_R.SIM" in sample:
                s_name = s_name.replace("_R.SIM", "")
                self.m_dict[s_name][1] = filename


    ### create a dictionary of all .txt files for stats [sample names: file names]
    def load_dict_stats(self):
        for file in os.listdir(self.from_CATT):
            filename  = os.fsdecode(file)
            check = filename.replace(self.project+"_", "")
            if ".TXT" in check:
                check = check.replace(".TXT", "")
                for room in self.room_dict:
                    for type in self.room_dict[room]:
                        if check in self.room_dict[room][type]:
                            self.stat_dict[check] = filename


    ### create a dictionary of all rooms: [ targets: [], masks: [] ] names from Blender
    def load_ins(self):
        for file in os.listdir(self.ins):
            filename = os.fsdecode(file)
            room = filename.split(".")[0]
            self.room_dict[room] = {"target": [], "masks": []}

            with open(os.path.join(self.ins, file)) as f:
                lines = []
                for line in f:
                    lines.append(line.strip())
                self.room_dict[room]["target"] = [lines[0]]
                self.room_dict[room]["masks"] = lines[2:]


    ### make directories for all rooms specified in INS dictionary, params for STATS and SIM dirs
    def make_room_dirs(self, sub_dir):
        for room in self.room_dict:
            room_dir = os.path.join(sub_dir, room)
            if os.path.exists(room_dir):
                pass
            else:
                os.mkdir(room_dir)
                os.mkdir(os.path.join(room_dir, "target"))
                os.mkdir(os.path.join(room_dir, "masks"))


    ### move targets .SIM
    def move_targets(self):
        for room in self.room_dict:
            target_file_names = self.get_files(self.room_dict[room]["target"])
            if target_file_names != None:
                for pair in target_file_names:
                    for channel in pair:
                        target_file = os.path.join(self.dump, channel)
                        shutil.copy(target_file, os.path.join(os.path.join(self.out, room), "target"))
            else:
                print(f"Couldn't find all target {room}")


    ### move masks .SIM
    def move_masks(self):
        for room in self.room_dict:
            target_file_names = self.get_files(self.room_dict[room]["masks"])
            if target_file_names != None:
                for pair in target_file_names:
                    for channel in pair:
                        target_file = os.path.join(self.dump, channel)
                        shutil.copy(target_file, os.path.join(os.path.join(self.out, room), "masks"))
            else:
                print(f"Couldnt find all masks {room}")


    ### gets the file name of the requested sample, returns None if not found
    def get_files(self, samples):
        output = []
        try:
            for f in samples:
                output.append(self.m_dict[f])
            return output
        except KeyError:
            print(f"ERR: No such file! {f}")
            return None


    ### create JSON file in STATS directories from raw data
    def create_stats(self):
        for room in self.room_dict:
            for type in self.room_dict[room]:
                for name in self.room_dict[room][type]:
                    if name != "None":
                        with open( os.path.join(self.from_CATT, self.stat_dict[name])) as f:
                            glob = []
                            for line in f:
                                glob.append(line)
                            parsed = self.stats_parser(glob)
                            location = os.path.join(self.stats, room)
                            location = os.path.join(location, type)
                            json_file = os.path.join(location, f'{name}.json')
                            with open(json_file, 'w') as outfile:
                                json.dump(parsed, outfile)


    ### takes raw txt data and returns dict for C-80, RT, T-30, SPL
    def stats_parser(self, raw):
        results_dict = {"C-80":{"unit": "", "data": []}, "RT'":{"unit": "", "data": []}, "T-30":{"unit": "", "data": []}, "SPL":{"unit": "", "data": []}}
        interest = ["C-80", "RT'", "T-30", "SPL"]
        for i, line in enumerate(raw):
            if any(key in line for key in interest):
                r_type, r_data, r_unit = self.clean_up(line)
                results_dict[r_type]["data"] = r_data
                results_dict[r_type]["unit"] = r_unit
        return results_dict


    ### takes raw line and returns reading_type, reading_data, reading_unit
    def clean_up(self, line):
        for i in range(5):
            line = line.replace("  ", " ")
            line = line.replace("\t", " ")
        splitted_line = line.split(' ')
        reading_type = splitted_line[0]
        reading_unit = splitted_line[-1]
        reading_data = splitted_line[2:-1]
        for i, point in enumerate(reading_data):
            if point == "---":
                reading_data[i] = 0
            if point == '"---"':
                reading_data[i] = 0
        return reading_type.replace('"', ''), [float(i) for i in reading_data], reading_unit.replace('"', '').strip()


cube = walle(me)

### Move .SIM to DUMP
cube.move_SIM()

### Load sample names, instructions, make SIM directories
cube.load_dict()
cube.load_ins()
cube.make_room_dirs(cube.out)

### Move .SIM from DUMP to respective directories
cube.move_targets()
cube.move_masks()

### Load stats from raw CATT output
cube.load_dict_stats()

### Make directories for stats
cube.make_room_dirs(cube.stats)

### Create JSON stats in respective directories
cube.create_stats()


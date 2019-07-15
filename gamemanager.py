import random
import ConfigParser
import copy

from dbmanager import DBManager
from xml.dom.minidom import parseString
import gamelogicsettings as GameLogicSettings

class GameManager():

    def __init__(self):
        self.function_dict = {
                            self.choose_map_random: "choose_map_random",
                            1: "no"
                            }
        self.db = DBManager()
        self.map_manager = MapManager(self.db)

    def find_function(self, function_name):
        for func, func_name in self.function_dict.iteritems():
            if func_name == function_name:
                return func

    def run_function(self, function_name, function_param):
        func = self.find_function(function_name)
        return func(function_param)
    
    def choose_map_random(self, params):
        map_name = self.map_manager.choose_map_random()
        return "choose_map_random " + map_name

class MapManager():

    def __init__(self, db):
        self.height = None
        self.width = None
        self.map_name = None
        self.hex_map = list()
        self.hex_path_data = list()
        self.current_path = PathData()
        self.db = db

    def choose_map_random(self):
        map_list = self.db.select_all_maps()
        chosen_map = random.choice(map_list)
        self.map_name = chosen_map

        data = self.db.select_map_data(chosen_map)
        self.height = data[1]
        self.width = data[2]

        self.generate_hex_map()
        
        self.link_hex_map()
        
        self.add_obstacles(data[3])

        self.generate_hex_path_data()

        return chosen_map

    def generate_hex_map(self):
        for i in range(self.width):
            col = None
            if i % 2 == 0:
                col = [Hex(i, j) for j in range(self.height)]
            else:
                col = [Hex(i, j) for j in range(self.height-1)]
            self.hex_map.append(col)

    def link_hex_map(self):
        for i in range(len(self.hex_map)):
            for j in range(len(self.hex_map[i])):
                h = self.hex_map[i][j]

                for index in range(6):
                    if i % 2 != 0:
                        if index == 0 and i > 0:
                            h.neighbors[index] = self.hex_map[i-1][j]
                        if index == 1 and i > 0:
                            h.neighbors[index] = self.hex_map[i-1][j+1]
                        if index == 2 and j < len(self.hex_map[i])-1:
                            h.neighbors[index] = self.hex_map[i][j+1]
                        if index == 3 and i < len(self.hex_map)-1:
                            h.neighbors[index] = self.hex_map[i+1][j+1]
                        if index == 4 and i < len(self.hex_map)-1:
                            h.neighbors[index] = self.hex_map[i+1][j]
                        if index == 5 and j > 0:
                            h.neighbors[index] = self.hex_map[i][j-1]
                    else:
                        if index == 0 and i > 0 and j > 0:
                            h.neighbors[index] = self.hex_map[i-1][j-1]
                        if index == 1 and i > 0 and j < len(self.hex_map[i])-1:
                            h.neighbors[index] = self.hex_map[i-1][j]
                        if index == 2 and j < len(self.hex_map[i])-1:
                            h.neighbors[index] = self.hex_map[i][j+1]
                        if index == 3 and i < len(self.hex_map)-1 and j < len(self.hex_map[i])-1:
                            h.neighbors[index] = self.hex_map[i+1][j]
                        if index == 4 and i < len(self.hex_map)-1 and j > 0:
                            h.neighbors[index] = self.hex_map[i+1][j-1]
                        if index == 5 and j > 0:
                            h.neighbors[index] = self.hex_map[i][j-1]

    def add_obstacles(self, xml):
        root = parseString(xml)
        elements = root.getElementsByTagName("Hex")
        for elem in elements:
            x = int(elem.getAttribute("x"))
            y = int(elem.getAttribute("y"))
            elem_data = elem.childNodes[0].data
            split_elem_data = elem_data.split(',')
            is_move = int(split_elem_data[0])
            is_shoot = int(split_elem_data[1])
            self.hex_map[x][y].set_obstacles(is_move, is_shoot)

    def generate_hex_path_data(self):
        for i in range(len(self.hex_map)):
            col = None
            if i % 2 == 0:
                col = [HexPathData() for j in range(self.height)]
            else:
                col = [HexPathData() for j in range(self.height-1)]
            self.hex_path_data.append(col)

    def new_round(self):
        self.reset_hex_path_data()

    def reset_hex_path_data(self):
        for i in range(len(self.hex_map)):
            for j in range(len(self.hex_map[i])):
                del self.hex_path_data[i][j].main_path[:]
                del self.hex_path_data[i][j].reserve_path[:]
                self.hex_path_data[i][j].distance = -1

    def find_available_path_forward(self, x, y, index_start_direction, points_move):

        if points_move == 0:
            return

        hex_data = self.hex_path_data[x][y]
        hex_data.main_path = list()
        hex_data.main_path.append(self.hex_map[x][y])
        hex_data.distance = 0

        neighbors = self.hex_map[x][y].neighbors

        for i in range(6):
            if neighbors[i] != None:
                self.calculate_available_path_forward(neighbors[i].x, neighbors[i].y, hex_data.main_path, hex_data.distance, index_start_direction, i, points_move)


    def calculate_available_path_forward(self, x, y, way, current_distance, index_start_direction, index_end_direction, points_move):

        if self.hex_map[x][y].is_move == False:
            return

        rotates = abs(index_end_direction - index_start_direction)
        if rotates > 3:
            rotates = 6 - rotates

        distance = GameLogicSettings.tank_forward_move_point + rotates * GameLogicSettings.tank_rotate_move_point
        if current_distance + distance > points_move:
            return

        hex_data = self.hex_path_data[x][y]

        if hex_data.distance != -1 and hex_data.distance < (current_distance + distance):
            return
        
        #new_way = copy.deepcopy(way)
        new_way = copy.copy(way)
        new_way.append(self.hex_map[x][y])
                       
        if hex_data.distance == (current_distance + distance):
            hex_data.reserve_path = new_way
        else:
            hex_data.main_path = new_way

        hex_data.distance = current_distance + distance

        neighbors = self.hex_map[x][y].neighbors

        for i in range(6):
            if neighbors[i] != None:
                self.calculate_available_path_forward(neighbors[i].x, neighbors[i].y, hex_data.main_path, hex_data.distance, index_end_direction, i, points_move)

    def find_available_path_backward(self, x, y, index_start_direction, points_move):

        if points_move == 0:
            return

        hex_data = self.hex_path_data[x][y]
        hex_data.main_path = list()
        hex_data.main_path.append(self.hex_map[x][y])
        hex_data.distance = 0

        neighbors = self.hex_map[x][y].neighbors

        for i in range(6):
            if neighbors[i] != None:
                self.calculate_available_path_backward(neighbors[i].x, neighbors[i].y, hex_data.main_path, hex_data.distance, index_start_direction, i, points_move)


    def calculate_available_path_backward(self, x, y, way, current_distance, index_start_direction, index_end_direction, points_move):

        if self.hex_map[x][y].is_move == False:
            return

        rotates = abs(index_end_direction - index_start_direction)
        if rotates > 3:
            rotates = 6 - rotates

        distance = GameLogicSettings.tank_backward_move_point + rotates * GameLogicSettings.tank_rotate_move_point
        if current_distance + distance > points_move:
            return

        hex_data = self.hex_path_data[x][y]

        if hex_data.distance != -1 and hex_data.distance < (current_distance + distance):
            return
        
        new_way = copy.deepcopy(way)
        new_way.append(self.hex_map[x][y])
                       
        if hex_data.distance == (current_distance + distance):
            hex_data.reserve_path = new_way
        else:
            hex_data.main_path = new_way

        hex_data.distance = current_distance + distance

        neighbors = self.hex_map[x][y].neighbors

        for i in range(6):
            if neighbors[i] != None:
                self.calculate_available_path_backward(neighbors[i].x, neighbors[i].y, hex_data.main_path, hex_data.distance, index_end_direction, i, points_move)

    def reset_move_path(self):
        if self.current_path.distance == -1:
            return
        else:
            self.current_path = PathData()

    def find_move_path_forward(self, x, y, index_end_direction, points_move):

        self.reset_move_path()

        if self.hex_path_data[x][y].distance == -1:
            return

        if self.hex_path_data[x][y].distance == 0:
            return

        if len(self.hex_path_data[x][y].reserve_path) != 0:

            main_path = self.hex_path_data[x][y].main_path
            reserve_path = self.hex_path_data[x][y].reserve_path

            main_path_distance = self.calculate_move_path_distance(x, y, main_path, index_end_direction)
            reserve_path_distance = self.calculate_move_path_distance(x, y, reserve_path, index_end_direction)

            if main_path_distance >= reserve_path_distance:
                #self.current_path.path = copy.deepcopy(main_path)
                self.current_path.path = main_path
                self.current_path.distance = main_path_distance
            else:
                #self.current_path.path = copy.deepcopy(reserve_path)
                self.current_path.path = reserve_path
                self.current_path.distance = reserve_path_distance
        else:
            self.current_path.path = copy.deepcopy(self.hex_path_data[x][y].main_path)
            self.current_path.distance = self.calculate_move_path_distance(x, y, self.hex_path_data[x][y].main_path, index_end_direction)

    def calculate_move_path_distance(self, x, y, path, index_end_direction):

        penultimate_hex = path[-2]
        target_hex_neighbors = self.hex_map[x][y].neighbors

        neighbor_index = 0
        for i in range(6):
            if target_hex_neighbors[i] == penultimate_hex:
                neighbor_index = i
                break

        index_start_direction = neighbor_index + 3
        if index_start_direction > 5:
            index_start_direction -= 6

        rotates = abs(index_end_direction - index_start_direction)
        if rotates > 3:
            rotates = 6 - rotates

        distance = rotates * GameLogicSettings.tank_rotate_move_point + self.hex_path_data[x][y].distance

        return distance
        
class Hex():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = [None] * 6
        #self.neighbors_l2 = list()
        self.is_move = 1
        self.is_shoot = 1

    def set_obstacles(self, is_move, is_shoot):
        self.is_move = is_move
        self.is_shoot = is_shoot

class HexPathData():

    def __init__(self):
        self.main_path = list()
        self.reserve_path = list()
        self.distance = None

class PathData():

    def __init__(self):
        self.path = list()
        self.distance = -1

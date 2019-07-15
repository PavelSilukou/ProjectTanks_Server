import sqlite3
from xml.dom.minidom import parseString

class DBManager():

    def __init__(self):
        self.connection = None
        self.cursor = None

    def set_connection(self):
        self.connection = sqlite3.connect("project_tanks_DB.db")
        self.cursor = self.connection.cursor()

    def select_all_maps(self):
        self.set_connection()
        self.cursor.execute("SELECT MapName FROM Map")
        result = self.cursor.fetchall()
        all_maps = list()
        for map_data in result:
            all_maps.append(map_data[0])
        self.connection.close()
        return all_maps

    def select_map_data(self, map_name):
        self.set_connection()
        self.cursor.execute("SELECT * FROM Map WHERE MapName='{0}'".format(map_name))
        result = self.cursor.fetchall()
        self.connection.close()
        return result[0]

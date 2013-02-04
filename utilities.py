#License Information:
#--------------------------------------
#
#Copyright (C) 2013  Alimohammad Rabbani
#
#DigTheMail is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#DigTheMail is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with DigTheMail. If not, see <http://www.gnu.org/licenses/>.


import threading
import logging
import os


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
#            logging.debug('Running: %s', self.active)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
#            logging.debug('Running: %s', self.active)

class FileOperations(object):
    @staticmethod
    def create_directory(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

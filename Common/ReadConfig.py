#!/usr/bin/env python
import ConfigParser,os

DEBUG_MODULE = "[Common]"
DEBUG_SCRIPT = "[ReadConfig]"
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

def ReadConfig():
    #------------------------
    # Read configuration file
    #------------------------
    config = ConfigParser.ConfigParser()
    home_directory = os.path.expanduser('~')
    #print DEBUG_HEADER, home_directory
    config.read(home_directory + '/.fireantenv')
    #print DEBUG_HEADER, config
    path = config.get('directory','path')
    #print DEBUG_HEADER, path
    config.read(path + '/Config/FireantNode.conf')
    print DEBUG_HEADER, "Read FireantNode.conf"
    print DEBUG_HEADER, config
    return config

#ReadConfig()

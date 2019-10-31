# NOTE: before running this module, lines 89 - 227 (end) of model.py needs to be commented

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

import configparser

from model import EvolutionaryModel

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']
n_agents = int(CONFIG_MODEL['total_agents'])
grid_height = int(CONFIG_MODEL['grid_height'])
grid_width = int(CONFIG_MODEL['grid_width'])


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 #  "Color": "red",
                 "r": 0.5}

    if agent.strategy == 'hawk':
        portrayal["Color"] = "red"
    elif agent.strategy == 'dove':
        portrayal["Color"] = "yellow"
    elif agent.strategy == 'possessor':
        portrayal["Color"] = "blue"
    elif agent.strategy == 'trader':
        portrayal["Color"] = "green"

    return portrayal


grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)
server = ModularServer(EvolutionaryModel,
                       [grid],
                       "Evolutionary Model",
                       {"N": n_agents, "width": grid_width, "height": grid_height})
server.port = 8521  # The default
server.launch()

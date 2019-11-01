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
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 0,
                 "w": 0.8,
                 "h": 0.8}

    if agent.strategy == 'hawk':
        portrayal["Color"] = "#1f77b4"
    elif agent.strategy == 'dove':
        portrayal["Color"] = "#ff7e0e"
    elif agent.strategy == 'possessor':
        portrayal["Color"] = "#2ca02c"
    elif agent.strategy == 'trader':
        portrayal["Color"] = "#d62728"
    elif agent.strategy == 'traderToM0':
        portrayal["Color"] = "#9467bd"
    elif agent.strategy == 'traderToM1':
        portrayal["Color"] = "#8c564b"

    return portrayal


grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)
server = ModularServer(EvolutionaryModel,
                       [grid],
                       "Evolutionary Model",
                       {"N": n_agents, "width": grid_width, "height": grid_height})
server.port = 8521  # The default
server.launch()

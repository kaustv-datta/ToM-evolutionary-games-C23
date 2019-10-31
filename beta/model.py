from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from agent import EvolutionaryAgent
import strategies
import random
import matplotlib.pyplot as plt
import numpy as np
import configparser
import io
import math
import os
import pandas as pd
from functools import reduce

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']
CONFIG_RESULTS = CONFIG['results']
WEALTH_TYPE = CONFIG_MODEL['initial_wealth_type']
FIXED_WEALTH_VALUE = int(CONFIG_MODEL['fixed_wealth_value'])
FIXED_PROPERTY_VALUE = int(CONFIG_MODEL['fixed_property_value'])
strategyList = CONFIG_MODEL['active_strategies'].split(',')


# Main model which controls the agents
class EvolutionaryModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        """Contructor function

        Arguments:
            N {integer} -- Number of initial agents in the model
            width {integer} -- Model grid width
            height {integer} -- Model grid height
        """
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)  # True -> toroid
        self.schedule = RandomActivation(self)
        self.latest_id = N-1

        # Create agents based on population percentage from config file
        AGENT_ID = 0
        for strategy in strategies.strategyList:
            percent_agent = float(
                CONFIG_MODEL[strategy + '_population_percent'])
            num_strategy_agents = math.floor(percent_agent * self.num_agents)

            for i in range(num_strategy_agents):
                evolutionaryStrategy = strategy
                # Initial Wealth is set from config - to a random number OR fixed amount
                if WEALTH_TYPE == 'fixed':
                    initialWealth = FIXED_WEALTH_VALUE
                else:
                    initialWealth = random.randrange(int(CONFIG_MODEL['initial_wealth_range_lower']), int(
                        CONFIG_MODEL['initial_wealth_range_upper']))
                a = EvolutionaryAgent(
                    AGENT_ID, self, evolutionaryStrategy, initialWealth, 0)
                self.schedule.add(a)
                AGENT_ID += 1

                # Add the agent to a random grid cell
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(a, (x, y))

        # Make percentage of agents property owners
        num_owners = round(
            (int(CONFIG_MODEL['percentage_of_owners']) / 100) * len(self.schedule.agents))
        owner_agents = random.sample(self.schedule.agents, num_owners)
        # Assign property to the agents that are chosen to be owners
        for agent in owner_agents:
            agent.assignPropertyToAgent()

    def step(self):
        """Steps to take at each tick of the model
        """
        self.schedule.step()
        # Natural selection
        strategies.naturalSelection(self)


n_steps = int(CONFIG_MODEL['steps'])
n_agents = int(CONFIG_MODEL['total_agents'])
grid_height = int(CONFIG_MODEL['grid_height'])
grid_width = int(CONFIG_MODEL['grid_width'])

# Repeat entire simluation based on config file
num_simulations = int(CONFIG_RESULTS['total_runs'])
working_directory = os.getcwd()
output_folder = os.path.join(
    working_directory, CONFIG_RESULTS['output_folder'])
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

output_df = pd.DataFrame(
    columns=['run', 'step', 'strategy', 'wealth', 'population'])

for sim_run in range(num_simulations):
    # EvolutionaryModel(N, width, height)
    model = EvolutionaryModel(n_agents, grid_width, grid_height)
    all_wealth = []
    all_strategies = []
    all_hawks = []
    all_doves = []
    all_traders = []
    all_possessors = []

    n_hawks = []
    n_doves = []
    n_possessors = []
    n_traders = []
    n_nonTraders = []

    for i in range(n_steps):
        model.step()
        # create statistics
        number_hawks = 0
        number_doves = 0
        number_traders = 0
        number_nonTraders = 0
        number_trader = 0
        number_possessor = 0
        for agent in model.schedule.agents:
            if agent.strategy == "hawk":
                number_hawks += 1
            elif agent.strategy == "dove":
                number_doves += 1
            elif agent.strategy == "trader":
                number_trader += 1
            else:
                number_possessor += 1

            if agent.strategy != 'trader':
                number_nonTraders += 1

        n_doves.append(number_doves)
        n_hawks.append(number_hawks)
        n_traders.append(number_trader)
        n_possessors.append(number_possessor)
        n_nonTraders.append(number_nonTraders)

        for strategy in strategyList:
            strategy_agents = list(
                filter(lambda agent: agent.strategy == strategy, model.schedule.agents))
            population = len(strategy_agents)
            wealth = sum(agent.getTotalWealth() for agent in strategy_agents)
            output_df = output_df.append(pd.Series(
                [sim_run, i, strategy, wealth, population], index=output_df.columns), ignore_index=True)

    # Store the results
    for agent in model.schedule.agents:
        all_wealth.append(agent.wealth + agent.owner)
        all_strategies.append(agent.strategy)
        if agent.strategy == "hawk":
            all_hawks.append(agent.wealth + agent.owner)
        elif agent.strategy == "dove":
            all_doves.append(agent.wealth + agent.owner)
        elif agent.strategy == "trader":
            all_traders.append(agent.wealth + agent.owner)
        else:
            all_possessors.append(agent.wealth + agent.owner)

output_df.to_csv(output_folder + '/simulation_results.csv', index=False)

# Create aggregated plots
grouped_data = output_df.groupby(['step', 'strategy'])
grouped_data_dict = {}
for strategy in strategyList:
    population_key = 'population_' + strategy
    wealth_key = 'wealth_' + strategy
    grouped_data_dict[population_key] = []
    grouped_data_dict[wealth_key] = []

for step in range(n_steps):
    for strategy in strategyList:
        grouped_data_dict['population_' + strategy].append(
            grouped_data.get_group((step, strategy))['population'].mean())
        grouped_data_dict['wealth_' + strategy].append(
            grouped_data.get_group((step, strategy))['wealth'].mean())

# 1. Strategy population over time
plt.figure()
for strategy in strategyList:
    plt.plot(grouped_data_dict['population_' + strategy], label=(strategy))
plt.ylabel('Population')
plt.xlabel('Simulation Steps')
plt.title("Strategy population at each step")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder,  'aggregated_population_plot.png'))
plt.close()

# 2. Strategy wealth over time
plt.figure()
for strategy in strategyList:
    plt.plot(grouped_data_dict['wealth_' + strategy], label=(strategy))
plt.ylabel('Wealth')
plt.xlabel('Simulation Steps')
plt.title("Strategy wealth accumulated at each step")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder,  'aggregated_wealth_plot.png'))
plt.close()

# 3. Population histogram
final_populations = []
final_strategies = []
for strategy in strategyList:
    final_strategies.append(strategy)
    final_populations.append(grouped_data.get_group(
        (n_steps - 1, strategy))['population'].mean())
y_pos = np.arange(len(final_strategies))
plt.figure()
plt.bar(y_pos, final_populations, align='center', alpha=0.5)
plt.xticks(y_pos, final_strategies)
plt.ylabel('Population')
plt.xlabel('Strategies')
plt.title('Population composition - end of simulation')
plt.tight_layout()
plt.savefig(os.path.join(output_folder,  'aggregated_histogram_plot.png'))
plt.close()


# Visualize agents in the model
# def agent_portrayal(agent):
#     portrayal = {"Shape": "circle",
#                  "Color": "red",
#                  "Filled": "true",
#                  "Layer": 0,
#                  "r": 0.5}
#     return portrayal

# grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)
# server = ModularServer(EvolutionaryModel,
#                        [grid],
#                        "Evolutionary Model",
#                        {"N": n_agents, "width": grid_width, "height": grid_height})
# server.port = 8521 # The default
# server.launch()
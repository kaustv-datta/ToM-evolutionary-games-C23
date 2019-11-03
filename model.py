from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from agent import EvolutionaryAgent
import strategies
import random
import configparser
import math

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']
WEALTH_TYPE = CONFIG_MODEL['initial_wealth_type']
FIXED_WEALTH_VALUE = int(CONFIG_MODEL['fixed_wealth_value'])
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
        self.running = True

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

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import EvolutionaryAgent
import strategies
import random
import matplotlib.pyplot as plt
import configparser
import io
import math
import os

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']
CONFIG_RESULTS = CONFIG['results']
WEALTH_TYPE = CONFIG_MODEL['initial_wealth_type']
FIXED_WEALTH_VALUE = int(CONFIG_MODEL['fixed_wealth_value'])
FIXED_PROPERTY_VALUE = int(CONFIG_MODEL['fixed_property_value'])


# Main model which controls the agents
class EvolutionaryModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height, step_cost, die_value, reproduce_value):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.step_cost = step_cost
        self.die_value = die_value
        self.reproduce_value = reproduce_value
        self.schedule = RandomActivation(self)
        self.latest_id = N-1

        # Create agents based on population percentage from config file
        AGENT_ID = 0
        for strategy in strategies.strategyList:
            percent_agent = float(CONFIG_MODEL[strategy + '_population_percent'])
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
        # Property value is set from config file
        for agent in owner_agents:
            current_wealth = agent.wealth
            if WEALTH_TYPE == 'fixed':
                updated_wealth = current_wealth
                updated_owner = FIXED_PROPERTY_VALUE
            else:
                updated_wealth = round(0.2 * current_wealth)
                updated_owner = round(0.8 * current_wealth)
            agent.updateAgentResource(updated_wealth, updated_owner)

    def step(self):
        self.schedule.step()
        # Natural selection
        strategies.naturalSelection(self)


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
n_steps = int(CONFIG_MODEL['steps'])
n_agents = int(CONFIG_MODEL['total_agents'])

# Repeat entire simluation based on config file
num_simulations = int(CONFIG_RESULTS['total_runs'])
working_directory = os.getcwd()
output_folder = os.path.join(working_directory, CONFIG_RESULTS['output_folder'])
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

for sim_run in range(num_simulations):
    # EvolutionaryModel(N, width, height, step_cost, die_value, reproduce_value)
    model = EvolutionaryModel(n_agents, 10, 10, 2, 0, 10)

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


    # for agent in model.schedule.agents:
    #     print("I'm a " + agent.strategy + " and I have " +
    #           str(agent.wealth) + "and I own" + str(agent.owner))

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


    # shows a histogram of the total number of hawks and doves
    plt.hist((all_strategies))
    plt.title("Total number of each remaining strategy")
    # plt.show()
    plt.savefig(os.path.join(output_folder, 'run_' + str(sim_run) + '_plot1.png'))
    plt.close()

    # shows a histogram of the wealth of hawks and doves
    plt.hist((all_hawks, all_doves, all_traders, all_possessors),
            label=('Hawks', 'Doves', 'Traders', 'Possessors'))
    plt.title("Histogram of the wealth each strategy")
    plt.legend()
    # plt.show()
    plt.savefig(os.path.join(output_folder,  'run_' + str(sim_run) + '_plot2.png'))
    plt.close()

    plt.plot(n_hawks, label=('Hawks'))
    plt.plot(n_doves, label=('Doves'))
    plt.plot(n_traders, label=('Traders'))
    plt.plot(n_possessors, label=('Possessors'))
    plt.title("Plot of number of hawks and doves at each step")
    plt.legend()
    # plt.show()
    plt.savefig(os.path.join(output_folder,  'run_' + str(sim_run) + '_plot3.png'))
    plt.close()

    plt.plot(n_traders, label=('Traders'))
    plt.plot(n_nonTraders, label=('Non-Traders'))
    plt.title("Plot of number of traders and non-traders at each step")
    plt.legend()
    # plt.show()
    plt.savefig(os.path.join(output_folder,  'run_' + str(sim_run) + '_plot4.png'))
    plt.close()

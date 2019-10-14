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

        # Create agents
        for i in range(self.num_agents):
            evolutionaryStrategy = random.choice(strategies.strategyList)
            # Initial Wealth is set to a random number between 1 and 15
            initialWealth = random.randrange(1, 16, 1)
            # 50 % are owners
            owner = 0
            if random.randrange(1, 101, 1) <= int(CONFIG_MODEL['percentage_of_owners']):
                owner = round(0.8 * initialWealth)
                initialWealth = round(0.2 * initialWealth)
            a = EvolutionaryAgent(i, self, evolutionaryStrategy, initialWealth, owner)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        # Natural selection
        strategies.naturalSelection(self)


# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']

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


for agent in model.schedule.agents:
    print("I'm a " + agent.strategy + " and I have " + str(agent.wealth) + "and I own" + str(agent.owner))

# Store the results
for agent in model.schedule.agents:
    all_wealth.append(agent.wealth)
    all_strategies.append(agent.strategy)
    if agent.strategy == "hawk":
        all_hawks.append(agent.wealth)
    elif agent.strategy == "dove":
        all_doves.append(agent.wealth)
    elif agent.strategy == "trader":
        all_traders.append(agent.wealth)
    else:
        all_possessors.append(agent.wealth)


# shows a histogram of the total number of hawks and doves
plt.hist((all_strategies))
plt.title("Total number of each remaining strategy")
plt.show()

# shows a histogram of the wealth of hawks and doves
plt.hist((all_hawks, all_doves, all_traders, all_possessors), label=('Hawks', 'Doves', 'Traders', 'Possessors'))
plt.title("Histogram of the wealth each strategy")
plt.legend()
plt.show()

plt.plot(n_hawks, label=('Hawks'))
plt.plot(n_doves, label=('Doves'))
plt.plot(n_traders, label=('Traders'))
plt.plot(n_possessors, label=('Possessors'))
plt.title("Plot of number of hawks and doves at each step")
plt.legend()
plt.show()

plt.plot(n_traders, label=('Traders'))
plt.plot(n_nonTraders, label=('Non-Traders'))
plt.title("Plot of number of traders and non-traders at each step")
plt.legend()
plt.show()

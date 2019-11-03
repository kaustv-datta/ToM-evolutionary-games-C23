import configparser
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from model import EvolutionaryModel

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']
CONFIG_RESULTS = CONFIG['results']

n_steps = int(CONFIG_MODEL['steps'])
n_agents = int(CONFIG_MODEL['total_agents'])
grid_height = int(CONFIG_MODEL['grid_height'])
grid_width = int(CONFIG_MODEL['grid_width'])
strategyList = CONFIG_MODEL['active_strategies'].split(',')

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
    model = EvolutionaryModel(n_agents, grid_width, grid_height)

    for i in range(n_steps):
        model.step()
        
        # create statistics
        for strategy in strategyList:
            strategy_agents = list(
                filter(lambda agent: agent.strategy == strategy, model.schedule.agents))
            population = len(strategy_agents)
            wealth = sum(agent.getTotalWealth() for agent in strategy_agents)
            output_df = output_df.append(pd.Series(
                [sim_run, i, strategy, wealth, population], index=output_df.columns), ignore_index=True)

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
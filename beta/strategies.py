import random
import statistics
import math
import configparser
import io
import os

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read('./config/config.ini')
CONFIG_MODEL = CONFIG['model']

# List of available strategies
strategyList = CONFIG_MODEL['active_strategies'].split(',')


# Type of game
ACTIVE_GAME_TYPE = CONFIG_MODEL['game_type']


# Hawk-Dove OR Dove-Hawk
def emulateHawkDoveStrategy(hawk, dove):
    # hawk gains resource
    if dove.owner > 0:
        hawk.owner = dove.owner
        dove.owner = 0
    hawk.saySomething('I am hawk. I gained ' + str(hawk.owner))
    # dove loses resource
    dove.saySomething('I am dove. I lost')


# Hawk-Hawk
def emulateHawkHawkStrategy(hawkO, hawkNO):
    owner = hawkO.owner
    h = getFightCost(owner)
    # if wealth/2 > h its the prisoners dilemma, otherwise its the chicken game
    # one of both will win/be the Hawk while the other looses/be the dove
    player = [hawkO, hawkNO]
    winner = random.choice(player)
    player.remove(winner)
    looser = player[0]
    if owner / 2 > h:
        # prisoners dilemma:  both keep the hawk strategy, one will gain (V-h),
        # the other will (loose -h)
        winner.wealth -= h
        winner.owner = owner
        looser.wealth -= h
        looser.owner = 0
    else:
        # chicken game: one chooses Hawk (winner) and the other one Dove
        # (looser)
        winner.saySomething("We will play the Chicken Game. I am Hawk " +
                            str(winner.unique_id) +
                            " and I fight, while Hawk " +
                            str(looser.unique_id) +
                            " behaves as a dove")
        emulateHawkDoveStrategy(winner, looser)


# Dove-Dove
def emulateDoveDoveStrategy(doveO, doveNO):
    owner = doveO.owner
    player = [doveO, doveNO]
    # random dove retreats
    winner = random.choice(player)
    player.remove(winner)
    looser = player[0]
    # the winner takes it all
    winner.owner = owner
    looser.owner = 0
    winner.saySomething('I am dove ' +
                        str(winner.unique_id) +
                        '. I gained ' +
                        str(owner))
    # the other dove doesn't gain anything
    looser.saySomething('I am dove ' + str(looser.unique_id) + ". I retreated")

# Traders


def emulateTradersStrategy(owner, intruder):
    # intruder values the property V = 0.8 * intruder.wealth
    # owner values the property v = owner.owner
    # owner sells the property for x = (V + v) / 2
    x = round((0.8 * intruder.wealth + owner.owner) / 2)
    owner.owner = 0
    owner.wealth += x
    intruder.owner = x
    intruder.wealth -= x
    owner.saySomething('We are trading')


# Get cost of interaction or fight
def getFightCost(V):
    h = 0
    if ACTIVE_GAME_TYPE == 'prisoners-dilema':
        h = round(random.uniform(0, V/2))
    elif ACTIVE_GAME_TYPE == 'chicken-game':
        h = round(random.uniform(V/2, V))
    return h


# Kill agents with bad performing strategies and replicate the good strategies
def naturalSelection(model):
    all_agents = model.schedule.agents
    agent_wealths = [agent.owner + agent.wealth for agent in all_agents]
    average_wealth = statistics.mean(agent_wealths)

    for strategy in strategyList:
        # get fresh list of agents after each iteration
        all_agents = model.schedule.agents
        strategy_specific_agents = [
            agent for agent in all_agents if agent.strategy == strategy]
        if len(strategy_specific_agents) == 0:
            continue
        strategy_specific_wealth = [
            agent.wealth + agent.owner for agent in strategy_specific_agents]
        strategy_average_wealth = statistics.mean(strategy_specific_wealth)

        # If this is a loosing strategy - kill weakest agents using this strategy
        # No. of agents to kill is proportional to how less the average
        # strategy wealth is below the overall average wealth
        if average_wealth > strategy_average_wealth:
            percentage_to_kill = (
                average_wealth - strategy_average_wealth) / average_wealth
            num_agents_to_kill = math.floor(
                percentage_to_kill * len(strategy_specific_agents))
            agents_to_kill = sorted(strategy_specific_agents, key=lambda agent: agent.wealth + agent.owner)[
                :num_agents_to_kill]
            for agent in agents_to_kill:
                agent.die()

    for strategy in strategyList:
        # get fresh list of agents after each iteration
        all_agents = model.schedule.agents
        strategy_specific_agents = [
            agent for agent in all_agents if agent.strategy == strategy]
        if len(strategy_specific_agents) == 0:
            continue
        strategy_specific_wealth = [
            agent.wealth + agent.owner for agent in strategy_specific_agents]
        strategy_average_wealth = statistics.mean(strategy_specific_wealth)

        # If this is a winning strategy - replicate more agents with this strategy
        # No. of repliactions is proportional to how high the average strategy
        # wealth is above the overall average wealth
        if strategy_average_wealth > average_wealth:
            percentage_to_replicate = (
                strategy_average_wealth - average_wealth) / average_wealth
            num_agents_to_replicate = math.floor(
                percentage_to_replicate * len(strategy_specific_agents))
            agents_to_replicate = random.sample(
                strategy_specific_agents, num_agents_to_replicate)
            for agent in agents_to_replicate:
                agent.reproduce()

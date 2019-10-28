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
PROPERTY_INFLATION_PRICE = float(CONFIG_MODEL['property_buy_price_percentage'])

# List of available strategies
strategyList = CONFIG_MODEL['active_strategies'].split(',')

# Type of game
ACTIVE_GAME_TYPE = CONFIG_MODEL['game_type']


def emulateHawkDoveStrategy(hawk, dove):
    """Hawk-Dove OR Dove-Hawk strategy

    Arguments:
        hawk {Agent} -- the hawkish agent
        dove {Agent} -- the dove agent
    """
    # hawk gains resource
    if dove.owner > 0:
        hawk.owner = dove.owner
        dove.owner = 0
    hawk.saySomething('I am hawk. I gained ' + str(hawk.owner))
    # dove loses resource
    dove.saySomething('I am dove. I lost')


def emulateHawkHawkStrategy(hawkO, hawkNO):
    """Hawk-Hawk strategy

    Arguments:
        hawkO {Agent} -- Hawk Owner Agent
        hawkNO {Agent} -- Hawk Intruder Agent
    """
    owner = hawkO.owner
    h = getFightCost(owner)

    # if wealth/2 > h its the prisoners dilemma, otherwise its the chicken game
    # one of both will win while the other looses
    player = [hawkO, hawkNO]
    winner = random.choice(player)
    player.remove(winner)
    looser = player[0]
    # the winner is the (new) owner
    # the looser is no owner (anymore)
    # both have fighting costs that diminishes their wealth by h
    winner.wealth -= h
    winner.owner = owner
    looser.wealth -= h
    looser.owner = 0

    # Die if wealth is negative
    if looser.wealth < 0:
        looser.die()
    if winner.wealth < 0:
        winner.die()


def emulateDoveDoveStrategy(doveO, doveNO):
    """Dove-Dove strategy

    Arguments:
        doveO {Agent} -- Dove Owner Agent
        doveNO {Agent} -- Dove Intruder Agent
    """
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


def emulateTradersStrategy(owner, intruder):
    """Trading strategy

    Arguments:
        owner {Agent} -- Trader Owner Agent
        intruder {Agent} -- Trader Intruder Agent
    """
    estimated_buying_price = owner.owner + \
        (PROPERTY_INFLATION_PRICE * owner.owner)
    x = owner.owner + round((estimated_buying_price - owner.owner) / 2)
    owner.owner = 0
    owner.wealth += x
    intruder.owner = x
    intruder.wealth -= x
    owner.saySomething('We are trading')


# Trader vs Trader with ToM0 or ToM1
def emulateTraderToMStrategy(owner, intruder):
    # intruder values the property V = 0.8 * intruder.wealth
    # owner values the property v = owner.owner
    # owner sells the property for x = (V + v) / 4
    # x = round((0.8 * intruder.wealth + owner.owner) / 2)
    v = owner.owner
    estimated_buying_price = v + (PROPERTY_INFLATION_PRICE * v)
    x = round((estimated_buying_price - v) / 4)
    owner.owner = 0
    owner.wealth += v + x
    intruder.owner = v + 3 * x
    intruder.wealth -= v + 3 * x
    owner.saySomething('We are trading')


# Trader with ToM0 or ToM1 vs Trader
def emulateToMTraderStrategy(owner, intruder):
    # intruder values the property V = 0.8 * intruder.wealth
    # owner values the property v = owner.owner
    # owner sells the property for x = (V + v) / 4
    # x = round((0.8 * intruder.wealth + owner.owner) / 2)
    v = owner.owner
    estimated_buying_price = v + (PROPERTY_INFLATION_PRICE * v)
    x = round((estimated_buying_price - v) / 4)

    owner.owner = 0
    owner.wealth += v + 3 * x
    intruder.owner = v + x
    intruder.wealth -= v + x

    owner.saySomething('We are trading')


# Trader with ToM0 or ToM1 vs Trader with ToM0 or ToM1
def emulateToMToMStrategy(owner, intruder):
    # v = owner.owner
    # estimated_buying_price = v + (PROPERTY_INFLATION_PRICE * v)
    #print("initial property owner:", owner.owner, "\t \t initial wealth owner:", owner.wealth)
    #print("initial property intruder:", intruder.owner, "\t \t initial wealth intruder:", intruder.wealth)
    p = owner.ToMAgent.play(intruder.ToMAgent)
    if p != None:
        x = p * intruder.wealth
        #print("excess paied:",x)

        owner.owner = 0
        owner.wealth += x
        intruder.owner = x
        intruder.wealth -= x

        #print("final property owner:", owner.owner, "\t \tfinal wealth owner:", owner.wealth)
        #print("final property intruder:", intruder.owner, "\t \tfinal wealth intruder:", intruder.wealth)
        #print("____________________________________________________________________________________")


# Get cost of interaction or fight
def getFightCost(V):
    """Get cost of interaction or fight

    Arguments:
        V {integer} -- Value of property being fought

    Returns:
        integer -- cost of the fight
    """
    h = 0
    if ACTIVE_GAME_TYPE == 'prisoners-dilema':
        h = round(random.uniform(0, V / 2))
    elif ACTIVE_GAME_TYPE == 'chicken-game':
        h = round(random.uniform(V/2, V))
    elif ACTIVE_GAME_TYPE == 'no-predefined-game-type':
        h = round(random.uniform(0, V))
    return h


def naturalSelection(model):
    """Kill agents with bad performing strategies and replicate the good strategies

    Arguments:
        model {Model} -- Mesa model object
    """
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
        # No. of replications is proportional to how high the average strategy
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

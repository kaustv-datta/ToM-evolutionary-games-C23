import random
import statistics
import math

# List of available strategies
strategyList = ['hawk', 'dove']

# Hawk-Dove OR Dove-Hawk
def emulateHawkDoveStrategy(hawk, dove, wealth):
    # hawk gains resource
    hawk.wealth += wealth
    hawk.saySomething('I am hawk. I gained ' + str(wealth))
    # dove loses resource
    dove.saySomething('I am dove. I lost')


# Hawk-Hawk
def emulateHawkHawkStrategy(hawk1, hawk2, wealth):
    # every fight costs the hawk a random number between 1 and 7
    h = random.randrange(1, 8, 1)
    # if wealth/2 > h its the prisoners dilemma, otherwise its the chicken game
    # one of both will win/be the Hawk while the other looses/be the dove
    player = [hawk1, hawk2]
    winner = random.choice(player)
    player.remove(winner)
    looser = player[0]
    if wealth / 2 > h:
        # prisoners dilemma:  both keep the hawk strategy, one will gain (V-h),
        # the other will (loose -h)
        winner.wealth += wealth - h
        looser.wealth -= h
    else:
        # chicken game: one chooses Hawk (winner) and the other one Dove
        # (looser)
        winner.saySomething("We will play the Chicken Game. I am Hawk " +
                            str(winner.unique_id) +
                            " and I fight, while Hawk " +
                            str(looser.unique_id) +
                            " behaves as a dove")
        emulateHawkDoveStrategy(winner, looser, wealth)


# Dove-Dove
def emulateDoveDoveStrategy(dove1, dove2, wealth):
    player = [dove1, dove2]
    # random dove retreats
    winner = random.choice(player)
    player.remove(winner)
    looser = player[0]
    # the winner takes it all
    winner.wealth += wealth
    winner.saySomething('I am dove ' +
                        str(winner.unique_id) +
                        '. I gained ' +
                        str(wealth))
    # the other dove doesn't gain anything
    looser.saySomething('I am dove ' + str(looser.unique_id) + ". I retreated")


# Kill agents with bad performing strategies and replicate the good strategies
def naturalSelection(model):
    all_agents = model.schedule.agents
    agent_wealths = [agent.wealth for agent in all_agents]
    average_wealth = statistics.mean(agent_wealths)

    for strategy in strategyList:
        # get fresh list of agents after each iteration
        all_agents = model.schedule.agents
        strategy_specific_agents = [
            agent for agent in all_agents if agent.strategy == strategy]
        if len(strategy_specific_agents) == 0:
            continue
        strategy_specific_wealth = [
            agent.wealth for agent in strategy_specific_agents]
        strategy_average_wealth = statistics.mean(strategy_specific_wealth)

        # If this is a loosing strategy - kill some agents using this strategy
        # No. of agents to kill is proportional to how less the average
        # strategy wealth is below the overall average wealth
        if average_wealth > strategy_average_wealth:
            print('------LOSING----' + strategy)
            percentage_to_kill = (
                average_wealth - strategy_average_wealth) / average_wealth
            num_agents_to_kill = math.ceil(
                percentage_to_kill * len(strategy_specific_agents))
            agents_to_kill = random.sample(
                strategy_specific_agents, num_agents_to_kill)
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
            agent.wealth for agent in strategy_specific_agents]
        strategy_average_wealth = statistics.mean(strategy_specific_wealth)

        # If this is a winning strategy - replicate the strategy accross the population
        # No. of repliactions is proportional to how high the average strategy
        # wealth is above the overall average wealth
        if strategy_average_wealth > average_wealth:
            print('------WINNING----' + strategy)
            percentage_to_replicate = (
                strategy_average_wealth - average_wealth) / average_wealth
            num_agents_to_replicate = math.ceil(
                percentage_to_replicate * len(all_agents))
            agents_to_replicate = random.sample(
                all_agents, num_agents_to_replicate)
            for agent in agents_to_replicate:
                agent.strategy = strategy

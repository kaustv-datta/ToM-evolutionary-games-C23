import random
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
    if wealth/2 > h:
        # prisoners dilemma:  both keep the hawk strategy, one will gain (V-h), the other will (loose -h)
        winner.wealth += wealth - h
        looser.wealth -= h
    else:
        # chicken game: one chooses Hawk (winner) and the other one Dove (looser)
        winner.saySomething("We will play the Chicken Game. I am Hawk " + str(winner.unique_id) +
                            " and I fight, while Hawk " + str(looser.unique_id) + " behaves as a dove")
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
    winner.saySomething('I am dove ' + str(winner.unique_id) + '. I gained ' + str(wealth))
    # the other dove doesn't gain anything
    looser.saySomething('I am dove ' + str(looser.unique_id) + ". I retreated")


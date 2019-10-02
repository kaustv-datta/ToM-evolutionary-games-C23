import random
strategyList = ['hawk','dove']

# Hawk-Dove OR Dove-Hawk
def emulateHawkDoveStrategy(hawk, dove, wealth):
    # hawk gains resource
    hawk.wealth += wealth
    hawk.saySomething('I am hawk. I gained ' + str(wealth))
    # dove loses resource
    dove.saySomething('I am dove. I lost')

# Hawk-Hawk
def emulateHawkHawkStrategy(hawk1, hawk2, wealth):
    # every fight costs the hawk a random number between 1 and 15
    h = random.randrange(1, 16, 1)
    # hawk loses resource
    hawk1.wealth += wealth/2 - h
    hawk1.saySomething('I am hawk1. I gained ' + str(wealth/2 - h))
    # hawk loses resource
    hawk2.wealth += wealth/2 - h
    hawk2.saySomething('I am hawk2. I gained ' + str(wealth/2 - h))

# Dove-Dove
def emulateDoveDoveStrategy(dove1, dove2, wealth):
    # random dove retreats
    winner = random.choice([dove1, dove2])
    # the winner takes it all
    winner.wealth += wealth
    winner.saySomething('I am dove ' + str(winner.unique_id) + '. I gained ' + str(wealth))
    # the other dove doesn't gain anything
    if winner.unique_id == dove1.unique_id:
        dove2.saySomething('I am ' + str(dove2.unique_id) + ". I retreated")
    else:
        dove1.saySomething('I am ' + str(dove1.unique_id) + ". I retreated")

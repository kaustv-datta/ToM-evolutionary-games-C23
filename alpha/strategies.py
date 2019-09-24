strategyList = ['hawk','dove']

# Hawk-Dove OR Dove-Hawk
def emulateHawkDoveStrategy(hawk, dove):
    # hawk gains resource
    hawk.saySomething('I am hawk. I gain resource')
    # dove loses resourse
    dove.saySomething('I am dove. I lose resource')

# Hawk-Hawk
def emulateHawkHawkStrategy(hawk1, hawk2):
    # hawk loses resource
    hawk1.saySomething('I am hawk1. I lose resource')
    # hawk loses resource
    hawk2.saySomething('I am hawk2. I lose resource')

# Dove-Dove
def emulateDoveDoveStrategy(dove1, dove2):
    # dove might gain or lose resource
    dove1.saySomething('I am dove1. I might gain or lose resource')
    # dove might gain or lose resource
    dove2.saySomething('I am dove1. I might gain or lose resource')

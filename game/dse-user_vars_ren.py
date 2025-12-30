# This is where play-defined varables like stats and events go.

_tmp = __import__("dse-core_objects_ren")
globals().update(vars(_tmp))

"""renpy
init python:
"""

register_stat("Strength", "strength", 10, 100)
register_stat("Intelligence", "intelligence", 10, 100)
register_stat("Relaxation", "relaxation", hidden=True)
register_stat("Glasses Girl", "glasses", 0, 100, hidden=True, relationship=True)
register_stat("Sporty Girl", "sporty", 0, 100, hidden=True, relationship=True)

dp_period("Morning", "morning_act")
dp_choice("Attend Class", "class")
dp_choice("Cut Class", "cut")

# This is an example of an event that should only show up under special circumstances
dp_choice("Fly to the Moon", "fly", show="strength >= 100 and intelligence >= 100")

dp_period("Afternoon", "afternoon_act")
dp_choice("Study", "study")
dp_choice("Hang Out", "hang")

dp_period("Evening", "evening_act")
dp_choice("Exercise", "exercise")
dp_choice("Play Games", "play")
dp_choice("Call Friend", "call")

# First up, we define some simple events for the various actions, that
# are run only if no higher-priority event is about to occur.

event("class", "act == 'class'", event.only(), priority=200, title="_class")
event("class_bad", "act == 'class'", priority=210, title="_class")
event("cut1", "act == 'cut'", event.choose_one('cut'), priority=200, title="_cut1",
      changes=["intelligence -= 10", "relaxation += 10"])
event("cut2", "act == 'cut'", event.choose_one('cut'), priority=200, title="_cut2",
      changes=["relaxation += 10"])
event("fly", "act == 'fly'", event.solo(), priority=200, title="Flying Away!")
event("study", "act == 'study'", event.solo(), priority=200, title="_study",
      changes=["intelligence += 10", "relaxation -= 10"])
event("hang", "act == 'hang'", event.solo(), priority=200, title="_hang",
      changes=["relaxation += 10"])
event("exercise", "act == 'exercise'", event.solo(), priority=200, title="_exercise",
      changes=["strength += 10", "relaxation -= 10"])
event("play", "act == 'play'", event.solo(), priority=200, title="_play",
      changes=["strength -= 10", "relaxation += 10"])
event("chat", "act == 'call'", event.solo(), priority=200, title="_chat")


# This is an introduction event, that runs once when we first go
# to class. 
event("introduction", "act == 'class'", event.once(), event.only(), hintable=True,
        children=[
            None, # this is here so simulator knows it's possible to not progress to child event
            event("_introduction_focus", 
                  "False", # event is only triggered by manually adding it to event queue
                  changes=["glasses += 10", "intelligence += 5"]
                  )
        ])

# These are the events with glasses girl.
#
# The glasses girl is studying in the library, but we do not
# talk to her.
event("gg_studying",
        # This takes place when the action is 'study'.
        "act == 'study'",
        # This will only take place if no higher-priority
        # event will occur.
        event.solo(),
        # This takes place at least one day after seeing the
        # introduction event.
        event.depends("introduction"),
        # This takes priority over the study event.
        priority=190,
        title="Studying (Glasses Girl)",
        changes=["intelligence += 10", "relaxation -= 10"]
      )

# She asks to borrow our pen. 
event("borrow_pen",
        # This takes place when we go to study, and we have an int
        # >= 50. 
        "act == 'study' and intelligence >= 50",
        # It runs only once.
        event.once(),
        # It requires the introduction event to have run at least
        # one day before.
        event.depends("introduction"),
        hintable=True,
        changes=["glasses += 30"]
    )

# After the pen, she smiles when she sees us.
event("gg_smiling", "act == 'study'",
        event.solo(), event.depends("borrow_pen"),
        priority = 180, title="Smiling",
        changes=["if glasses < 50: glasses += 5", "intelligence += 10", "relaxation -= 10"]
    )

# The bookslide.
event("bookslide", "act == 'study' and intelligence == 100",
        event.once(), event.depends("borrow_pen"), hintable=True,
        changes=["glasses = 70"], skip_period=1,
    )

# She makes us cookies.
event("cookies", "act == 'study'",
        event.once(), event.depends("bookslide"), hintable=True,
        changes=["glasses=100"]
      )

# Her solo ending.
event("gg_confess", "act == 'class'",
        event.once(), event.depends("cookies"), hintable=True, title="Glasses Girl Confession", terminal=True)

# Here are Sporty Girl's events that happen during the exercise act.
event("catchme", "act == 'exercise'",
        event.depends('introduction'), event.once(), title="Catch Me!", changes=["sporty = 30"])
event("cantcatchme", "act == 'exercise'",
        event.depends('catchme'), event.solo(), priority=190, title="Can't Catch Me!",
        changes=["if sporty < 50: sporty += 5", "strength += 10", "relaxation -= 10"]
      )
event("caughtme", "act == 'exercise' and strength >= 50",
        event.depends('catchme'), event.once(), title="Caught Me!", hintable=True,
        changes=["if sporty < 70: sporty += 10", "strength += 10", "relaxation -= 10"]
      )
event("together", "act == 'exercise' and strength >= 50",
        event.depends('caughtme'), event.solo(), priority=180, hintable=True,
        changes=["if sporty < 70: sporty += 5", "strength += 10"]
      )
event("apart", "act == 'exercise' and strength < 50",
        event.depends('caughtme'), event.solo(), priority=180,
      changes=["if sporty < 70: sporty += 10", "strength += 10", "relaxation -= 10"]
      )
event("pothole", "act == 'exercise' and strength >= 100",
        event.depends('caughtme'), event.once(), hintable=True,
        changes=["sporty = 100"], skip_period=1
      )
event("dontsee", "act == 'exercise'",
        event.depends('pothole'), event.solo(), priority=170, title="Alone...")
event("sg_confess", "act == 'class'",
        event.depends('dontsee'), event.once(), hintable=True, title="Sporty Girl Confession", terminal=True)

# Relaxed ending with no girls happens if we max out our hidden relaxation stat.
event("relaxed_ending", "act=='hang' and relaxation >= 100", event.once(), hintable=True, terminal=True)

# Ending with both girls only happens if we have seen both of their final events
# This needs to be higher-priority than either girl's ending.    
event('both_confess', 'act == "class"',
        event.depends("dontsee"), event.depends("cookies"),
        event.once(), priority = 50, hintable=True, title="Double Confession!",
        terminal=True
      )

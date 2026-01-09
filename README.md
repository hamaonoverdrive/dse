# dse: Rougelike Fork
Dating Sim Engine for Ren'Py
The Dating Sim Engine (DSE) is a framework for writing games based on events that are triggered by statistics. It comprises a number of independent modules that can be combined to create games. 

## Features of this fork
- Core renpy files updated to modern versions.
- Additional "Relationship status" screen that displays scores with love interests.
- Optional "Hardcore" mode, which disables saves and stores all user data in persistent variables.
- Random events for each day are rolled at the start of the day, instead of right before they occur.
- Because events for a day are pre-determined, "hintable" events will be highlighted on the scheduler.
- An event viewer menu, which allows the player to revisit any scene that they have already seen. **Note: This uses the renpy replay function and may lead to undesired behavior if contents of events are conditioned on player stats**. There may be a patch to address this in the future.
- And last, but certainly not least: an included [gameplay simulator](game/dse-simulator.ipynb) which can predict player stat values and endings under different play strategies.

# Key usage notes
- For hardcore mode to work, **all** variables that store user states need to be declared with `register_stat()`
- Most user variables (ie: event objects, period and act definitions) should be placed in `game/dse-user_vars_ren.py`
- Labels and script for each of these events are in `game/dse-events.rpy`
- `label start:` and the core day loop are in `game/dse-schedule.rpy`

# Known Issues
These are being discovered as I develop Bloodsport Duel SiMulator, and will be fixed once that gamejam is done.
[ ] All hardcore values need to be initialized before first day, otherwise quitting on a new save will be unloadable
[ ] Event viewer label needs to be manually marked as seen to guarantee that it works
[ ] Need to block rollback between event calls in the event viewer in order to prevent rollback from causing crash

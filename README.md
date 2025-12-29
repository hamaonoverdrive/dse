# dse: Rougelike Fork
Dating Sim Engine for Ren'Py
The Dating Sim Engine (DSE) is a framework for writing games based on events that are triggered by statistics. It comprises a number of independent modules that can be combined to create games. 

## Development goals for this fork
- [x] Update core renpy files to modern versions
- [x] "Relationship status" screen that shows selected stats
- [x] Optional "Hardcore" mode, which disables saves and stores all user data in persistent variables
- [x] ~~Optional "Quick" mode, which skips already-seen events faster than renpy text skip~~ Decided to cut this, would be very tedious to implement 'short' versions of events for this mode
- [x] Allow specified random events to be rolled before player makes schedule selection, and display "hints" for the respective activities
- [x] Event viewer menu, which allows the player to revisit any scene that they have already seen. **Note: This uses the renpy replay function and may lead to undesired behavior if contents of events are conditioned on player stats**. There may be a patch to address this in the future.
- [ ] **Stretch goal**: refactor some objects into `_ren.py` files and write a framework to simulate playthroughs and predict player stat gain under different play strategies.

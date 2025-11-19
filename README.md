# dse
Dating Sim Engine for Ren'Py
The Dating Sim Engine (DSE) is a framework for writing games based on events that are triggered by statistics. It comprises a number of independent modules that can be combined to create games. 

## Development goals for this fork
- [x] Update core renpy files to modern versions
- [ ] "Relationship status" screen that shows selected stats
- [ ] Optional "Hardcore" mode, which disables saves and stores all user data in persistent variables
- [ ] Optional "Quick" mode, which skips already-seen events faster than renpy text skip
- [ ] Allow specified random events to be rolled before player makes schedule selection, and display "hints" for the respective activities
- [ ] Event viewer menu, which allows the player to revisit any scene that they have already seen
- [ ] **Stretch goal**: refactor some objects into `_ren.py` files and write a framework to simulate playthroughs and predict player stat gain under different play strategies.

# hardcore.rpy
# Manages variables that need to be read from or to persistent variables for hardcore mode

init -200 python:
    def set_hardcore(boolean):
        persistent.hardcore = boolean

    def update_persistent(label, jumped):
        # ignore labels that start with underscores or are on our banned list
        # also only save when we aren't in a call to avoid stack issues
        banned = ["main_menu_screen", "save_screen"]
        event_names = [x.name for x in all_events]
        banned.extend(event_names)

        if label not in banned and label[0] != "_":
            persistent.hardcore_label = label
            for stat in persistent.hardcore_tracked_stats:
                if hasattr(store, stat):
                    persistent.hardcore_stat_values[stat] = getattr(store, stat)
            renpy.save_persistent()

    def __init_hardcore():
        # other engine variables that we need to be sure get crammed in our hardcore store
        keywords = ["day", "events_executed", "events_executed_yesterday"]
        for word in keywords:
            persistent.hardcore_tracked_stats.add(word)
        # just change this from the default (save) because that breaks hardcore mode
        setattr(store, "_game_menu_screen", "preferences")

    config.start_callbacks.append(__init_hardcore)
    config.label_callbacks.append(update_persistent)

    if persistent.hardcore == None:
        persistent.hardcore = False

    if persistent.hardcore_tracked_stats == None:
        persistent.hardcore_tracked_stats = set()

    if persistent.hardcore_stat_values == None:
        persistent.hardcore_stat_values = {}

label _hardcore_check:
    if not persistent.hardcore:
        jump _ask_hardcore
    else:
        if persistent.hardcore_label is not None:
            python:
                for stat in persistent.hardcore_tracked_stats:
                    setattr(store, stat, persistent.hardcore_stat_values[stat])
                renpy.jump(persistent.hardcore_label)
        else:
            jump _ask_hardcore

label _ask_hardcore:
    menu:
        "Would you like to start the game in Hardcore mode? This setting cannot be changed again until a new game is started."
        "Yes":
            $ persistent.hardcore = True
            jump start
        "No":
            $ persistent.hardcore = False
            jump start

label _restart_hardcore:
    python:
        persistent.hardcore_label = None
        persistent.hardcore_stat_values = {}
        renpy.full_restart()


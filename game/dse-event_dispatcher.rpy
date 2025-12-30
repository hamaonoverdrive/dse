# The Ren'Py/DSE event dispatcher. This file contains the code that
# actually supports the running of events. Specifically, it contains
# code that determines which events are available, which events can
# run, and to actually run the events that should be run during a
# given period.

# This isn't really intended to be user-changable.

init -100 python:

    def __events_init():
        store.events_executed = { }
        store.events_executed_yesterday = { }

    config.start_callbacks.append(__events_init)

# This should called at the end of a (game) day, to let things
# like depends_yesterday to work.
label events_end_day:

    $ skip_periods = 0

    python hide:

        # We can't skip between days.
        skip_periods = 0

        for k in events_executed:
            events_executed_yesterday[k] = True

    return
    
# This is called once per period, to determine, and then execute, the
# events that should be run for that period. 
label events_run_period:

    while not check_skip_period() and events:

        $ _event = events.pop(0)
        $ events_executed[_event] = True

        # event titles starting with _ are ignored
        $ title = event_name_to_obj(_event).title
        if title[0] != "_":
            $ narrator.add_history(kind="adv", who="Event:", what=title)
            show screen event_popup(title)

        if persistent.hardcore:
            $ renpy.block_rollback()
        $ renpy.call(_event)

        $ e = event_name_to_obj(_event)

        # kill game if event is terminal!
        if e.terminal:
            $ persistent.hardcore_label = None
            $ renpy.full_restart()

        python:
            for ch in e.changes:
                exec(ch) 
                # I hate this so much but can't think of an easier way to do it

        # apply period skips
        $ skip_period = e.skip_period

        # force save if this is hardcore
        if persistent.hardcore:
            $ update_persistent(None, False)
        hide screen event_popup

    return

""" DEPRECATED!
Don't use the following over setting skip_period in the event declaration
Jumping to these may cause issues with not applying changed stats!

# If this is jumped to, it will end the current period immediately,
# and return control to the main program.
label events_end_period:

    $ skip_periods = 1
    return

# If this is jumped to, it will end the current period and skip
# the next period. Use this if, say, the user goes on a date that
# takes up two time slots.
label events_skip_period:

    $ skip_periods = 2
    return

"""

# used for the event viewer to handle events with children
label _view_event:

    while events:
        $ _event = events.pop(0)
        $ renpy.call(_event)

    $ renpy.end_replay()
        
init 100:
    python hide:
        # Sort all events on priority.
        all_events.sort(key=lambda i : i.priority)

    python hide:

        for i in all_events:
            if not renpy.has_label(i.name):
                raise Exception("'%s' is defined as an event somewhere in the game, but no label named '%s' was defined anywhere." % (i.name, i.name))
    
screen event_popup(title):

    zorder 190

    tag event_popup

    frame:
        style_prefix 'dse_event_popup'
        ## The transform that makes it pop out
        at event_popout()
        has hbox
        vbox:
            text title

    # timer 5.0 action [Hide("dse_event_popup"), Hide()]

transform event_popout():
    ## The `on show` event occurs when the screen is first shown.
    on show:
        ## Align it off-screen at the left. Note that no y information is
        ## given, as that is handled on the popup screen.
        xpos 0.0 xanchor 1.0
        ## Ease it on-screen
        easein_back 0.25 xpos 0.0 xanchor 0.0
    ## The `on hide, replaced` event occurs when the screen is hidden.
    on hide, replaced:
        ## Ease it off-screen again.
        easeout_back 0.25 xpos 0.0 xanchor 1.0

init -100 python:
    # viewable: whether an event can be seen in the viewer
    def event_is_viewable(e):
        # just gonna go through and eliminate reasons why an event may not be eligible one by one
        if e.title is None:
            return False

        if e.title[0] == "_":
            return False

        if e.is_child:
            return False

        return True

    # revisitable: whether a player has fully seen an event
    def event_is_revisitable(e, checking_child=False):

        if not checking_child and not event_is_viewable(e):
            return False

        if not renpy.seen_label(e.name):
            return False

        for child in e.children:
            if child is not None and not event_is_revisitable(child, True):
                return False
        return True

label _view_event(e):
    python:
        renpy.block_rollback()
        # first we dump everything that matters into temp vars so we don't disturb a current run
        _tempstore = {}
        for stat in persistent.hardcore_tracked_stats:
            _tempstore[stat] = getattr(store, stat)
        events = [e.name]

    while events:
        $ _event = events.pop(0)
        $ renpy.call(_event)

    python:
        renpy.block_rollback()
        # restore everything back to the store
        for stat in persistent.hardcore_tracked_stats:
            setattr(store, stat, _tempstore[stat])
        renpy.call_in_new_context("_game_menu", _game_menu_screen="viewer")
    return

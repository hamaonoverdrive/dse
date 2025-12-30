# These are core dse objects that have been partitioned off to allow for simulation
# of playthroughs in a non-renpy python session.

# code here will be executed by python interpreter, but not renpy.

import random
events_executed = {}
events_executed_yesterday = {}
events = [] # queue of upcoming event names
periods = {}
period_order = []
act = ""


class S:
    pass


store = S()
stats = {}


class __Stat(object):

    def __init__(self, name, default, max):
        self.name = name
        self.default = default
        self.max = max


def register_stat(name, var, default=0, max=100, hidden=False, relationship=False):
    global store
    global stats

    stats[var] = __Stat(name, default, max)
    setattr(store, var, default)

def reset():
    global events_executed
    global events_executed_yesterday
    global store
    global stats

    events_executed = {}
    events_executed_yesterday = {}
    for name, stat in stats.items():
        setattr(store, name, stat.default)

class Period(object):
    def __init__(self, name, var):
        self.name = name
        self.var = var
        self.acts = []

        global period_order
        period_order.append(self)


def dp_period(name, var):
    global periods
    periods[name] = Period(name, var)

def dp_choice(name, value=object(), enable="True", show="True"):
    global period_order
    if len(period_order) == 0:
        raise Exception("Choices must be a part of a defined period.")

    if value is object():
        value = name

    period_order[-1].acts.append((name, value, enable, show))


class EventDispatchSimulator(object):
    def __init__(self):
        self.rolled_events = None

        # Sort all events on priority.
        # kind of a weird place to put this but it's in a weird place in event_dispatcher too.
        global all_events
        all_events.sort(key=lambda i : i.priority)

    def start_day(self):
        self.rolled_events = EventChecker.getAllValid()
        global skip_periods
        skip_periods = 0

        global events_executed
        global events_executed_yesterday
        for k in events_executed:
            events_executed_yesterday[k] = True

        return self.rolled_events

    def get_choices(self):
        # need to find what acts are even valud, then return those keys from self.rolled_events
        possible_acts = { }
        # key: period
        # value: list with acts

        # cram everything from our fake store into locals so that eval will work properly
        global store
        global stats
        for var in stats.keys():
            locals()[var] = getattr(store, var)

        global period_order
        for period in period_order:

            possible_acts[period.name] = []

            for name, curr_val, enable, should_show in period.acts:
                if eval(enable) and eval(should_show):
                    possible_acts[period.name].append(curr_val)

        return possible_acts

    def run_day(self, acts, child_acts={}):
        # acts is expected to be dict with
        # key: period name
        # value: selected action

        # child_acts is dict with
        # key: event name
        # value: index of child event to take, if not None

        global periods
        global events
        global events_executed

        # cram everything from our fake store into locals so that stat changes will work properly
        global store
        global stats
        global skip_period
        for var in stats.keys():
            locals()[var] = getattr(store, var)

        for period in periods:
            act = acts[period]
            events = self.rolled_events[act]
            while not check_skip_period() and events:
                _event = events.pop(0)
                events_executed[_event] = True

                e = event_name_to_obj(_event)
                for change in e.changes:
                    exec(change)

                # nromalize stats
                for var, stat in stats.items():
                    v = locals()[var]
                    if v > stat.max:
                        locals()[var] = stat.max
                    if v < 0:
                        locals()[var] = 0

                # if this event is an ending, report back with the name of the ending
                if e.terminal:
                    return _event

                skip_periods = e.skip_period

                if _event in child_acts.keys():
                    events.insert(0, event_name_to_obj(_event).children[child_acts[_event]])

        # dump local changes back into store
        for var in stats.keys():
            setattr(store, var, locals()[var])

        return False


"""renpy
init -100 python:
"""


# A list of all of the events that the system knowns about,
# it's filtered to determine which events should run when.
all_events = [ ]

# The base class for events. When constructed, an event
# automatically adds itself to all_events.
#
# The first parameter for this is a unique name for the event,
# which is also used as the label that is called when the
# event executes.
#
# All other parameters are expressions. These expressions can
# be either strings, or objects having an eval method. Many
# interesting objects are given below.
#
# Keyword arguments are also kept on the object. Currently,
# there is one useful keyword argument, priority. This
# controls the order in which events are in the event list.
# (Events with lower priority number are evaluated first. If a
# priority is not specified, it's 100.)
class event(object):

    def __repr__(self):
        return '<event ' + self.name + '>'

    def __init__(self, name, *args, **kwargs):

        self.name = name

        exprs = [ ]

        for i in args:
            if isinstance(i, str):
                exprs.append(event.evaluate(i))
            else:
                exprs.append(i)

        self.exprs = exprs

        self.priority = kwargs.get('priority', 100)
        self.hintable = kwargs.get("hintable", False)
        self.children = kwargs.get("children", [ ])
        self.changes = kwargs.get("changes", [ ])
        self.terminal = kwargs.get("terminal", False)
        self.skip_period = kwargs.get("skip_period", 0) # only used in simulator
        self.is_child = False

        self.title = kwargs.get("title", None)
        if self.title is None:
            # if name starts with an underscore that means it's one we want to mark as hidden
            if self.name[0] != "_":
                self.title = self.name.replace("_"," ").title()
            else:
                self.title = self.name

        for child in self.children:
            if child is not None:
                child.is_child = True

        global all_events
        all_events.append(self)

    # Checks to see if this event is valid. It's called with
    # a list of events that have already checked out to be
    # True, and returns True if this event checks out.
    def check(self, valid):

        global act
        for i in self.exprs:
            if not i.eval(self.name, valid):
                return False

        return True

    def properties(self):

        rv = { }

        for i in self.exprs:
            rv.update(i.properties())

        return rv

    # The following two methods are used for the event viewer
    # viewable: whether an event can be seen in the viewer
    def is_viewable(self):
        if self.title is None:
            return False

        if self.title[0] == "_":
            return False

        if self.is_child:
            return False

        return True

    # visitable: whether a player has fully seen an event
    def is_visitable(self, checking_child=False):
        # function will crash outside of renpy, so let's just short it
        if "renpy" not in globals():
            return False

        if not checking_child and not self.is_viewable():
            return False

        if not renpy.seen_label(self.name):
            return False

        for child in self.children:
            if child is not None and not child.is_visitable(True):
                return False
        return True


    # The base class for all of the event checks given below.
    class event_check(object):

        def properties(self):
            return { }

        def __invert__(self):
            return event.false(self)

        def __and__(self, other):
            return event.and_op(self, other)

        def __or__(self, other):
            return event.or_op(self, other)


    # This evaluates the expression given as an argument, and the
    # returns true if it evaluates to true.
    class evaluate(event_check):

        def __init__(self, expr):
            self.expr = expr

        def eval(self, name, valid):
            global act
            if "renpy" not in globals():
                global store
                global stats
                for var in stats.keys():
                    locals()[var] = getattr(store, var)
            return eval(self.expr)

    # If present as a condition to an event, an object of this
    # type ensures that the event will only execute once.
    class once(event_check):
        def eval(self, name, valid):
            global events_executed
            return name not in events_executed

    # Returns True if no event of higher priority can execute,
    # and false otherwise. In general, solo events should be
    # the lowest priority, and are run if nothing else is.
    class solo(event_check):
        def eval(self, name, valid):

            # True if valid is empty.
            return not valid

    # Returns True if no event of higher priority can execute.
    # This also prevents other events from executing.
    class only(solo):

        def properties(self):
            return dict(only=True)


    # Returns True if the given events have happend already,
    # at any time in the game. False if at least one hasn't
    # happened yet.
    class happened(event_check):
        def __init__(self, *events):
            self.events = events

        def eval(self, name, valid):
            global events_executed
            for i in self.events:
                if i not in events_executed:
                    return False

            return True

    # Returns True probability of the time, where probability
    # is a number between 0 and 1.
    class random(event_check):

        def __init__(self, probability):
            self.probability = probability

        def eval(self, name, valid):
            # don't use the rollback-honoring random if we're not in renpy
            if "renpy" in globals():
                return renpy.random.random() <= self.probability
            else:
                return random.random() <= self.probability

    # Chooses only one from the group.
    class choose_one(event_check):

        def __init__(self, group, group_count=1):
            self.group = group
            self.group_count = group_count

        def eval(self, name, valid):
            return True

        def properties(self):
            return dict(group=self.group,
                        group_count=self.group_count)


    # Evaluates its argument, and returns true if it is false
    # and vice-versa.
    class false(event_check):
        def __init__(self, cond):
            self.cond = cond

        def eval(self, name, valid):
            global act
            return not self.cond.eval(name, valid)

    # Handles the and operator.
    class and_op(event_check):

        def __init__(self, *args):
            self.args = args

        def eval(self, name, valid):
            global act
            for i in self.args:
                if not i.eval(name, valid):
                    return False
            return True

    # Handles the or operator.
    class or_op(event_check):

        def __init__(self, *args):
            self.args = args

        def eval(self, name, valid):
            global act
            for i in self.args:
                if i.eval(name, valid):
                    return True
            return False

    # Returns True if all of the events given as arguments have
    # happened yesterday or earlier, or False otherwise.
    class depends(event_check):
        def __init__(self, *events):
            self.events = events

        def eval(self, name, valid):
            for i in self.events:
                if i not in events_executed_yesterday:
                    return False

            return True

# The number of periods to skip.
skip_periods = 0


# This returns True if the current period should be skipped,
# or False if the current period should execute. If it returns
# True, it decrements skip_periods.
def check_skip_period():

    global skip_periods

    if skip_periods:
        skip_periods -= 1
        return True
    else:
        return False


def event_name_to_obj(name):
    global all_events
    for e in all_events:
        if e.name == name:
            return e
    return None


class EventChecker:

    def setActVars(selected_act):
        global act
        global events
        global rolled_events
        act = selected_act
        events = rolled_events[act]

    def getAllValid():
        global periods
        global act

        # save whatever act is so we can restore it later
        # (just assume it's there if we're not in renpy)
        if "renpy" not in globals() or hasattr(store, "act"):
            old_act = act
        else:
            old_act = None
        results = { }

        for p in periods.values():
            for a in p.acts:
                act = a[1]
                results[act] = EventChecker.getValid()

        if old_act is not None:
            act = old_act
        return results

    def getValid():
        global all_events

        events = [ ]

        eobjs = [ ]
        egroups = { }
        eingroup = { }

        for i in all_events:
            if not i.check(eobjs):
                continue

            eobjs.append(i)

            props = i.properties()

            if 'group' in props:
                group = props['group']
                count = props['group_count']

                egroups.setdefault(group, [ ]).extend([ i ] * count)
                eingroup[i] = group

            if 'only' in props:
                break

        echosen = { }

        for k in egroups:
            if "renpy" in globals():
                echosen[k] = renpy.random.choice(egroups[k])
            else:
                echosen[k] = random.choice(egroups[k])

        for i in eobjs:

            if i in eingroup and echosen[eingroup[i]] is not i:
                continue

            events.append(i.name)

        return events

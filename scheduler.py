import time as time


def now():
    # returns time now in milliseconds
    return int(time.time() * 1000)


class Scheduler:
    """
    A class that manages the timing of user events in a loop, e.g a game loop.
    Example:
    ==========================================================================
    s = Scheduler()
    #....

    # loop
    while True:
        #....
        s.update((
            (predelay1, condition1, postdelay1, func1, args_tuple1, kwargs_dict1),
        
            (predelay2, condition2, postdelay2, func2, args_tuple2, kwargs_dict2),
                 
            (predelay3, condition3, postdelay3, func3, args_tuple3, kwargs_dict3),
            
            ......
        )
        #... other code that also include break out of while at some point
    ==========================================================================
    
    Each tuple argument above is an "event".
    
    Events are run consecutively.

    For each event:
        the boolean condition is checked after the predelay
        when condition is true, the func(*args_tuple, **kwarg_dict) is run after the postdelay
        
    Notes:
        Delays are in milliseconds.
        
        The update method returns immediately if the current delay has not timed out
        i.e. it does not keep control waiting for the delay.

        Variables in the condition as well the args_tuple, kwargs_dict are 
        refreshed each update call. 
        
        What happens in the user funcs is out of the control of scheduler. 
        The passed funcs are called at the appropriate times and then they have
        control; if you want the game loop o keep updating at a certain rate, 
        it's up to you to make sure that the funcs allow this.
        
        If a func takes no args, pass () for the args_tuple.
        If a func take only one arg, pass (single_arg,) for the args_tuple.
        If a func takes no kwargs, pass {} for args_dict
    """

    def __init__(self, verbose=False):
        self._verbose = verbose
        self._event_num = -1  # number of current event
        self._predelay_finished = False
        self._postdelay_finished = False
        self._condition_met = False
        self._is_last = False  # becomes true when on last event
        self._all_finished = False  # becomes true when finished all events

    def update(self, *params):
        """
        Public method to update schedule.
        Keeps track of whether event delay has time-out and if so
        runs the user function for that event, passing the 'current' value
        of the args and kwargs for that function.
        Here 'current' means as of last update call.
        """
        if not params or self._all_finished:
            return True
        self._update(*params)
        return False

    def _update(self, *params):
        """
        private update method
        """
        if self._event_num == -1:
            # This is first call, so start predelay
            self._start_time = now()
            self._predelay, self._postdelay, self._func = self._get_next(*params)
            if self._verbose:
                print("\nFirst event started...")

        if not self._predelay_finished and now() - self._start_time >= self._predelay:
            if self._verbose:
                print(
                    f"\nEvent {self._event_num+1} pre-delay of {self._predelay} ms finished...."
                )
            # current predelay has finished
            self._predelay_finished = True

        if self._predelay_finished and not self._condition_met:
            # get most up to date version of condition
            self._condition = self._get_condition(*params)

        if self._predelay_finished and not self._condition_met and self._condition:
            if self._verbose:
                print(f"\nEvent {self._event_num+1} condition met....")
            # start postdelay
            self._start_time = now()
            self._condition_met = True

        if (
            self._predelay_finished
            and self._condition_met
            and not self._postdelay_finished
            and now() - self._start_time >= self._postdelay
        ):
            if self._verbose:
                print(
                    f"\nEvent {self._event_num+1} post-delay of {self._postdelay} ms finished...."
                )
            # current postdelay has finished
            self._postdelay_finished = True
            # refresh args
            args, kwargs = self._get_args_kwargs(*params)
            self._func(*args, **kwargs)  # call user function
            if self._is_last:
                if self._verbose:
                    print("\nAll events finished.")
                self._all_finished = True
                return
            # start processing next event
            if self._verbose:
                print("\nFetching next event...")
            self._start_time = now()
            self._predelay_finished = False
            self._postdelay_finished = False
            self._condition_met = False
            self._predelay, self._postdelay, self._func = self._get_next(*params)

    def _get_args_kwargs(self, *params):
        """
        Returns as a tuple the arg and kwargs for the current function
        """
        event_info = params[self._event_num]
        return event_info[4], event_info[5]

    def _get_condition(self, *params):
        event_info = params[self._event_num]
        return event_info[1]

    def _get_next(self, *params):
        """
        Returns as a tuple the delay and function for the next event
        and increments the event number.
        params tuple is (predelay, condition, postdelay, func, args_tuple, kwargs_dict)
        """
        self._event_num += 1
        event_info = params[self._event_num]
        if self._event_num == len(params) - 1:
            self._is_last = True
        return event_info[0], event_info[2], event_info[3]


def main():
    import random

    def has_collided(obj1, obj2, _time=None):
        # Clever collision code...
        # .....
        # Here we will just return True with a probablity of 1%
        if random.randrange(100) == 0:
            if _time is not None:
                print(f"debug: time = {_time} ms, {obj1} collided with {obj2}")
            return True
        return False

    def start_pickup_animation(obj1, obj2, _time=None):
        if _time is not None:
            print(
                f"debug: time = {_time} ms, starting animation of {obj1} picking up {obj2}"
            )
        # this would decrement number of coins and increment player health

    def start_fadeaway_animation(obj, _time=None):
        if _time is not None:
            print(f"debug: time = {_time} ms, starting disappear animation of {obj}")

    def update_hud(level, health_delta=0, coins_delta=0, _time=None):
        if _time is not None:
            print(
                f"debug: time = {_time} ms, updating_hud, level = {level}, health delta = {health_delta}, coins delta = {coins_delta}"
            )

    def show_message(loc, msg, msg_id, _time=None):
        if _time is not None:
            print(
                f"debug: time = {_time} ms, showing mesage '{msg}' with id {msg_id} at location {loc}"
            )

    def delete_message(msg_id, _time=None):
        if _time is not None:
            print(f"debug: time = {_time} ms, delete message with id {msg_id}")

    coin_pickup_scheduler = Scheduler(verbose=False)
    coin_value = 100
    hud_hidden = False
    msgs_hidden = False
    level = 1
    start_time = now()
    fps = 60
    has_finished = False
    run_time = 10_000  # 10 sec
    
    while now() - start_time < run_time:
        if random.randrange(100) == 0:
            # just a way of simulating level number increasing
            level += 1
        if not has_finished:
            has_finished = coin_pickup_scheduler.update(
                # (predelay, condition, postdelay, function, args_tuple, kwargs_dict),
                (
                    0,
                    has_collided("player", "coin", _time=now() - start_time),
                    0,
                    start_pickup_animation,
                    ("player", "coin"),
                    dict(_time=now() - start_time),
                ),
                (
                    250,
                    True,
                    0,
                    start_fadeaway_animation,
                    ("coin",),
                    dict(_time=now() - start_time),
                ),
                (
                    0,
                    not hud_hidden,
                    0,
                    update_hud,
                    (level,),
                    dict(
                        health_delta=level * coin_value,
                        coins_delta=-1,
                        _time=now() - start_time,
                    ),
                ),
                (
                    0,
                    not msgs_hidden,
                    0,
                    show_message,
                    ((100, 100),),
                    dict(msg_id="coin_pickup", msg="Coin Collected", _time=now() - start_time),
                ),
                (
                    2000,
                    not msgs_hidden,
                    0,
                    delete_message,
                    (),
                    dict(msg_id="coin_pickup", _time=now() - start_time),
                ),
            )
            if has_finished:
                print(f"\ndebug: time = {now()-start_time} ms, finished")
        time.sleep(1 / fps)  # simulate frame tick


if __name__ == "__main__":
    main()

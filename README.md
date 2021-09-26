# scheduler.py
A module that manages the timing of user events in a loop, e.g a game loop.

## Installation
Requires python 3.

Just download ```scheduler.py``` and copy it to your working directory.

## Usage

### Generic

```python

# generic usage
s = Scheduler()

# loop
while True:
    #....
    s.update(
    	    (predelay1, condition1, postdelay1, func1, args_tuple1, kwargs_dict1),
            (predelay2, condition2, postdelay2, func2, args_tuple2, kwargs_dict2),               
            (predelay3, condition3, postdelay3, func3, args_tuple3, kwargs_dict3),
            # as many events as you need   
        )
        #... other code that also include break out of while at some point

"""
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
```

### concrete example (scheduleing events for a coin pickup in a game)

```python

import random
import time
from scheduler import Scheduler, now

"""
In this example we use scheduler to schedule the following events in game loop
 (pseudo code):

wait 0 ms
if player collided with coin:
    wait 0 ms
    start pickup animiation
    
    wait 250 ms
    if True:
        wait 0 ms
        start coin disappearing animation
        
        wait 0 ms
        if HUD is not hidden:
            wait 0 ms
            update HUD
            
            wait 0 ms
            if messages not hidden:
                wait 0 ms
                show coin pick up message
            
                wait 2000 ms:
                    if messages not hidden:
                        wait 0 ms
                        delete previous message
    
"""

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


coin_pickup_scheduler = Scheduler(verbose=True)
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
    
print("\nfinished")

```


## License
[MIT](https://choosealicense.com/licenses/mit/)

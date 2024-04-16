from wayfire.ipc import sock
from random import randint, choice

# scale, expo, showdesktop, switcherview, cube,  autororate
plugin = choice(["scale", "expo", "showdesktop", "switcherview", "cube", "autororate", None])
while True:
    try:
        number_of_views = randint(1, 20)
        number_of_executions = randint(10, 100)
        random_time_to_wait = randint(20, 400)
        sock.test_wayfire(
            number_of_views, number_of_executions, random_time_to_wait, plugin
        )
    except:
        continue

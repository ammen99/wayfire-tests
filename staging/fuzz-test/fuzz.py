from random import randint, choice
from fuzzy import TestWayfire

test = TestWayfire()

# scale, expo, switcherview, cube
# plugin = choice(["scale", "expo", "switcherview", "cube", None])
plugin = choice(["expo", "scale", None])
while True:
    try:
        number_of_views = randint(1, 20)
        number_of_executions = randint(10, 100)
        random_time_to_wait = randint(1, 400)
        test.test_wayfire(
            number_of_views, number_of_executions, random_time_to_wait, plugin
        )
    except Exception as e:
        print(e)
        continue

from celery.result import AsyncResult, GroupResult
from nextstep.tasks import *

"""call tasks:
1. delay
2. apply_async: can add additional params
3. directly __call__ normal function
"""
add.delay(2, 2)

add.apply_async((2, 2))
# add.apply_async((2, 2), queue="lopri", countdown=10)

add(2, 2)


"""Canvas
1. signature
2. s

"""
add_s = add.signature((2, 2), countdown=10)
add_s = add.s(2, 2)

# partial paramertes
add_s = add.signature((2, ), countdown=10)
add_s = add.s(2)

"""Canvas Primitives
1. group
2. chain
3. chord
4. map
5. starmap
6. chunks
"""

# group
# send a list of tasks in parallel, not one task only
# return result list format in order
from celery import group


g = group(add.s(i, i) for i in range(10))
group_result: GroupResult = g()
print(group_result.get())

# chain
# the previous result pass to the next result
from celery import chain
c = chain(add.s(4, 4) | mul(8))
chain_result: AsyncResult = c()
print(chain_result.get())

# chain shortcuts
(add.s(4, 4) | mul(8))().get()


# chord
# group then

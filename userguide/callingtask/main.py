from userguide.task.tasks import *


r = test_link.apply_async((2, 2), link=test_link.s(16))
# get first task result
r.get()  # 4
# get children task result
r.children()[0].get()  # 20


r = test_on_message.apply_async((1, 1))
print(r.get(on_message=on_message))


r = test_retry_policy.delay()

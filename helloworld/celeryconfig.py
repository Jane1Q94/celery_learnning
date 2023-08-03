broker_url = 'redis://localhost'
result_backend = 'redis://localhost'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utc = True

# 路由
# task_routes = {
#     "tasks.add": "low-priority"
# }

# 限流
# task_annotations = {
#     "tasks.add": {
#         "rate_limit": "1/m"
#     }
# }

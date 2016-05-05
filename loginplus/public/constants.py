# This is the constants variable defination file.
# Created by shaomingwu@inspur.com

QUEUE_WORKER = "queue_worker"       # The queue name for backend worker.

# Both the worker pragrame and WEB view share the queue of rpc type, I mean that:
# 1, For each worker, report the result to the backend server through RPC.
# 2, For WEB view, querying the result from backend server through RPC too.
QUEUE_RPC = "queue_rpc"             # The queue name for rpc.

# define the field of one task.
TASK_STATE = "task_state"
TASK_COMMENT = "task_comment"

# define the task state: just like an enum.
TASK_STATE_UNKNOWN, TASK_STATE_PROCESSING, TASK_STATE_DONE, TASK_STATE_ERROR = range(4)
import os
import sys

# Ensure the current directory is in the path so we can import 'app'
sys.path.append(os.getcwd())

from rq import SimpleWorker, Queue
from app.redis_client import get_redis_connection
from dotenv import load_dotenv
import os

load_dotenv()

# macOS specific hack to avoid fork safety issues with some libraries
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

listen = ['default']

if __name__ == '__main__':
    try:
        conn = get_redis_connection()
        # Explicitly pass connection to Queues
        queues = [Queue(name, connection=conn) for name in listen]
        
        # Use SimpleWorker to avoid fork() issues on macOS, passing connection explicitly
        worker = SimpleWorker(queues, connection=conn)
        print(f"🚀 Worker started (Simple/No-Fork). Listening on queues: {', '.join(listen)}")
        worker.work()
    except Exception as e:
        print(f"❌ Worker failed to start: {e}")

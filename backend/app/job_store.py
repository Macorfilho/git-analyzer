from rq.job import Job
from app.redis_client import get_redis_connection
from rq.exceptions import NoSuchJobError

class JobStore:
    """
    Simple abstraction to track and retrieve job statuses.
    Relies on Redis/RQ as the backing store.
    """
    def __init__(self):
        self.connection = get_redis_connection()

    def get_job(self, job_id: str):
        try:
            return Job.fetch(job_id, connection=self.connection)
        except NoSuchJobError:
            return None

    def get_status(self, job_id: str):
        job = self.get_job(job_id)
        if not job:
            return "unknown"
        
        status = job.get_status()
        # Map RQ statuses to our API statuses if needed, or return as is.
        # RQ statuses: queued, started, finished, failed, deferred, scheduled
        return status

    def get_result(self, job_id: str):
        job = self.get_job(job_id)
        if not job:
            return None
        return job.result

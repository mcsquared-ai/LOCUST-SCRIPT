"""Tasks related to querying the RAG system."""
import json
from locust import task, TaskSet

class QueryTasks(TaskSet):
    @task(4)
    def check_job_status(self):
        """Check the status of a processing job"""
        if not self.user.job_id:
            return

        with self.client.get(f"/api/jobs/{self.user.job_id}",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get job status: {response.text}")

    @task(3)
    def query_instance(self):
        """Query the RAG instance"""
        if not self.user.instance_id:
            return

        payload = {
            "instance_ids": [self.user.instance_id],
            "query": "What were the key revenue drivers in Q3?",
            "top_k": 5
        }
        with self.client.put("/api/instances",
                           data=json.dumps(payload),
                           headers={"Content-Type": "application/json"},
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Query failed: {response.text}")

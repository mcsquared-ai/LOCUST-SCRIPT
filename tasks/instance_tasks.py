"""Tasks related to RAG instance management."""
import json
import time
from locust import task, TaskSet

from config import USER_ID

class InstanceTasks(TaskSet):
    def on_start(self):
        """Initialize by creating an instance"""
        self.create_instance()

    @task(1)
    def create_instance(self):
        """Create a new RAG instance"""
        payload = {
            "name": f"Load Test Instance {time.time()}",
            "description": "Testing RAG API with Locust",
            "user_id": USER_ID,
            "instance_metadata": {"project": "Locust Test", "client": "Test Client"}
        }
        with self.client.post("/api/instances/create-only",
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            if response.status_code == 200:
                self.user.instance_id = response.json().get("instance", {}).get("id")
                print(f"Created instance: {self.user.instance_id}")
                response.success()
            else:
                response.failure(f"Failed to create instance: {response.text}")

    @task(2)
    def list_instance_files(self):
        """List files in the instance"""
        if not self.user.instance_id:
            return

        with self.client.get(f"/api/instances/{self.user.instance_id}",
                           catch_response=True) as response:
            if response.status_code == 200:
                files = response.json().get("files", [])
                if files:
                    self.user.file_id = files[0].get("file_id")
                response.success()
            else:
                response.failure(f"Failed to list files: {response.text}")

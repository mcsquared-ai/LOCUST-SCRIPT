from locust import HttpUser, task, between
import json

USER_ID = "user-abc-123"

class SAMRAGUser(HttpUser):
    host = "https://api-rag.dev.stagwellmarketingcloud.io"  # Base URL of SAM_RAG API
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    instance_id = None
    job_id = None

    @task
    def create_instance(self):
        """Create a new RAG instance"""
        payload = {
            "name": "Load Test Instance",
            "description": "Testing RAG API with Locust",
            "user_id": USER_ID,
            "instance_metadata": {"project": "Locust Test", "client": "Test Client"}
        }
        response = self.client.post("/api/instances/create-only", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.instance_id = data["instance"]["id"]
            print(f"Instance created: {self.instance_id}")

    @task
    def generate_signed_urls(self):
        """Generate presigned URLs for file uploads"""
        if not self.instance_id:
            return
        payload = {
            "files": [
                {"filename": "report_q3_2024.pdf", "content_type": "application/pdf", "size_bytes": 1048576},
                {"filename": "supplementary_data.csv", "content_type": "text/csv", "size_bytes": 524288}
            ],
            "expiration_minutes": 15
        }
        self.client.post(f"/api/instances/{self.instance_id}/upload/signed-urls", json=payload)

    @task
    def query_instance(self):
        """Query the RAG instance"""
        if not self.instance_id:
            return
        payload = {
            "instance_ids": [self.instance_id],
            "query": "What were the key revenue drivers in Q3?",
            "top_k": 5
        }
        response = self.client.put("/api/instances", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Query response: {data.get('ai_response', '')}")

    @task
    def check_job_status(self):
        """Optional: Check background job status"""
        if not self.job_id:
            return
        self.client.get(f"/api/jobs/{self.job_id}")

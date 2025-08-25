from locust import HttpUser, task, between
import json
import time

USER_ID = "user-abc-123"

class SAMRAGUser(HttpUser):
    host = "https://api-rag.dev.stagwellmarketingcloud.io"  # Add your API base URL here
    wait_time = between(1, 3)
    instance_id = None
    job_id = None
    gcs_uri = None
    file_id = None

    def on_start(self):
        """Initialize user by creating an instance"""
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
                self.instance_id = response.json().get("instance", {}).get("id")
                print(f"Created instance: {self.instance_id}")
                response.success()
            else:
                response.failure(f"Failed to create instance: {response.text}")

    @task(2)
    def get_upload_urls(self):
        """Get signed URLs for file upload"""
        if not self.instance_id:
            return

        payload = {
            "files": [{
                "filename": "test_document.pdf",
                "content_type": "application/pdf",
                "size_bytes": 1048576
            }],
            "expiration_minutes": 15
        }
        with self.client.post(f"/api/instances/{self.instance_id}/upload/signed-urls",
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data["upload_urls"]:
                    self.gcs_uri = data["upload_urls"][0]["gcs_path"]
                response.success()
            else:
                response.failure(f"Failed to get upload URLs: {response.text}")

    @task(3)
    def confirm_upload(self):
        """Confirm file upload and start processing"""
        if not self.instance_id or not self.gcs_uri:
            return

        payload = {
            "uploaded_files": [{
                "filename": "test_document.pdf",
                "gcs_uri": f"gs://bucket/{self.gcs_uri}",
                "size_bytes": 1048576,
                "content_type": "application/pdf"
            }]
        }
        with self.client.post(f"/api/instances/{self.instance_id}/upload/confirm",
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            if response.status_code == 200:
                self.job_id = response.json().get("job_id")
                response.success()
            else:
                response.failure(f"Failed to confirm upload: {response.text}")

    @task(4)
    def check_job_status(self):
        """Check the status of a processing job"""
        if not self.job_id:
            return

        with self.client.get(f"/api/jobs/{self.job_id}",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get job status: {response.text}")

    @task(5)
    def list_instance_files(self):
        """List files in the instance"""
        if not self.instance_id:
            return

        with self.client.get(f"/api/instances/{self.instance_id}",
                           catch_response=True) as response:
            if response.status_code == 200:
                files = response.json().get("files", [])
                if files:
                    self.file_id = files[0].get("file_id")
                response.success()
            else:
                response.failure(f"Failed to list files: {response.text}")

    @task(6)
    def query_instance(self):
        """Query the RAG instance"""
        if not self.instance_id:
            return

        payload = {
            "instance_ids": [self.instance_id],
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

    @task(7)
    def delete_files(self):
        """Delete files from the instance"""
        if not self.instance_id or not self.file_id:
            return

        payload = {
            "file_ids": [self.file_id]
        }
        with self.client.delete(f"/api/instances/{self.instance_id}/files",
                              data=json.dumps(payload),
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to delete files: {response.text}")

"""Tasks related to file operations."""
import json
from locust import task, TaskSet

from config import TEST_FILE_NAME, TEST_FILE_TYPE, TEST_FILE_SIZE

class FileTasks(TaskSet):
    @task(2)
    def get_upload_urls(self):
        """Get signed URLs for file upload"""
        if not self.user.instance_id:
            return

        payload = {
            "files": [{
                "filename": TEST_FILE_NAME,
                "content_type": TEST_FILE_TYPE,
                "size_bytes": TEST_FILE_SIZE
            }],
            "expiration_minutes": 15
        }
        with self.client.post(f"/api/instances/{self.user.instance_id}/upload/signed-urls",
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data["upload_urls"]:
                    self.user.gcs_uri = data["upload_urls"][0]["gcs_path"]
                response.success()
            else:
                response.failure(f"Failed to get upload URLs: {response.text}")

    @task(3)
    def confirm_upload(self):
        """Confirm file upload and start processing"""
        if not self.user.instance_id or not self.user.gcs_uri:
            return

        payload = {
            "uploaded_files": [{
                "filename": TEST_FILE_NAME,
                "gcs_uri": f"gs://bucket/{self.user.gcs_uri}",
                "size_bytes": TEST_FILE_SIZE,
                "content_type": TEST_FILE_TYPE
            }]
        }
        with self.client.post(f"/api/instances/{self.user.instance_id}/upload/confirm",
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            if response.status_code == 200:
                self.user.job_id = response.json().get("job_id")
                response.success()
            else:
                response.failure(f"Failed to confirm upload: {response.text}")

    @task(1)
    def delete_files(self):
        """Delete files from the instance"""
        if not self.user.instance_id or not self.user.file_id:
            return

        payload = {
            "file_ids": [self.user.file_id]
        }
        with self.client.delete(f"/api/instances/{self.user.instance_id}/files",
                              data=json.dumps(payload),
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to delete files: {response.text}")

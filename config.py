"""Configuration settings for the load test."""

# API Configuration
API_HOST = "https://api-rag.dev.stagwellmarketingcloud.io"
USER_ID = "user-abc-123"

# Test Configuration
WAIT_TIME_MIN = 1  # minimum wait time between tasks
WAIT_TIME_MAX = 3  # maximum wait time between tasks

# File Upload Configuration
TEST_FILE_SIZE = 1048576  # 1MB
TEST_FILE_NAME = "test_document.pdf"
TEST_FILE_TYPE = "application/pdf"

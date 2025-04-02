from fastapi import HTTPException, status
import os
import logging
from dotenv import load_dotenv
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Environment variables loaded in auth module")

# Service-specific configuration
SERVICES = ["openai", "gemini", "grok"]
USER_EMAIL = "ansh.riyal@gmail.com"  # Your email

class ServiceCredentials(BaseModel):
    api_key: str
    is_valid: bool = False

# Data storage
SERVICE_CREDENTIALS_FILE = "data/service_credentials.json"

def load_data(file_path: str) -> dict:
    """Load data from JSON file"""
    logger.debug(f"Loading data from {file_path}")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            logger.debug(f"Data loaded successfully from {file_path}")
            return data
    logger.debug(f"No existing data found at {file_path}, returning empty dict")
    return {}

def save_data(file_path: str, data: dict):
    """Save data to JSON file"""
    logger.debug(f"Saving data to {file_path}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f)
    logger.debug(f"Data saved successfully to {file_path}")

class Auth:
    def __init__(self):
        logger.info("Initializing Auth service")
        self.service_credentials = load_data(SERVICE_CREDENTIALS_FILE)
        logger.debug(f"Loaded credentials for {len(self.service_credentials)} services")

    def save_service_credentials(self, service: str, api_key: str):
        """Save API key for a service"""
        logger.info(f"Saving {service} API key")
        if service not in SERVICES:
            logger.error(f"Invalid service: {service}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service: {service}"
            )

        self.service_credentials[service] = {
            "api_key": api_key,
            "is_valid": False  # Will be validated when used
        }
        save_data(SERVICE_CREDENTIALS_FILE, self.service_credentials)
        logger.debug(f"{service} API key saved successfully")

    def get_service_credentials(self, service: str) -> Optional[Dict]:
        """Get API key for a service"""
        logger.debug(f"Retrieving {service} API key")
        return self.service_credentials.get(service)

    def get_all_credentials(self) -> Dict:
        """Get all service credentials"""
        return self.service_credentials 
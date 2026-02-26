"""
Firebase Firestore client for state management and real-time data.
Handles all database operations with proper error handling and retry logic.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from config import config

class FirebaseClient:
    """Firestore client wrapper with retry logic and error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client: Optional[firestore.Client] = None
        self._initialize()
        
    def _initialize(self) -> None:
        """Initialize Firestore client with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client = config.initialize_firebase()
                self.logger.info("Firebase Firestore client initialized successfully")
                return
            except Exception as e:
                self.logger.warning(f"Firebase initialization attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error("All Firebase initialization attempts failed")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
                
    def _safe_operation(self, operation, *args, **kwargs):
        """Wrapper for safe Firestore operations with retry logic"""
        if not self.client:
            raise ConnectionError("Firestore client not initialized")
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Firestore operation failed (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.5 * (attempt +
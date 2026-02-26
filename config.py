"""
Configuration management for the Autonomous Evolutionary Trading Platform.
Centralizes all environment variables, API keys, and system parameters with validation.
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

@dataclass
class TradingConfig:
    """Configuration for trading parameters"""
    initial_capital: float = 10000.0
    max_position_size: float = 0.1  # 10% of capital
    max_drawdown: float = 0.2  # 20% max drawdown
    risk_per_trade: float = 0.02  # 2% risk per trade
    min_confidence: float = 0.65  # Minimum confidence threshold
    cooloff_period: int = 60  # Seconds between trades
    
@dataclass
class EvolutionConfig:
    """Configuration for evolutionary algorithm"""
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.15
    crossover_rate: float = 0.7
    elite_size: int = 5
    tournament_size: int = 3
    
@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str
    credentials_path: str
    
class ConfigManager:
    """Manages system configuration with validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._validate_environment()
        
        # Trading Configuration
        self.trading = TradingConfig()
        
        # Evolution Configuration
        self.evolution = EvolutionConfig()
        
        # Firebase Configuration
        self.firebase = FirebaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
        )
        
        # Exchange Configuration
        self.exchanges = {
            'binance': {
                'api_key': os.getenv("BINANCE_API_KEY", ""),
                'secret': os.getenv("BINANCE_API_SECRET", ""),
                'testnet': os.getenv("BINANCE_TESTNET", "true").lower() == "true"
            },
            'coinbase': {
                'api_key': os.getenv("COINBASE_API_KEY", ""),
                'secret': os.getenv("COINBASE_API_SECRET", "")
            }
        }
        
        # Data Configuration
        self.data = {
            'cache_ttl': 300,  # 5 minutes cache TTL
            'retry_attempts': 3,
            'timeout': 30
        }
        
    def _validate_environment(self) -> None:
        """Validate required environment variables"""
        required_vars = ['FIREBASE_PROJECT_ID']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            error_msg = f"Missing required environment variables: {missing}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Validate file exists for Firebase credentials
        creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
        if not os.path.exists(creds_path):
            self.logger.warning(f"Firebase credentials file not found at {creds_path}")
            
    def initialize_firebase(self) -> firestore.Client:
        """Initialize Firebase Firestore client"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.firebase.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': self.firebase.project_id
                })
            return firestore.client()
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
            
    def get_exchange_config(self, exchange_name: str) -> Dict[str, Any]:
        """Get configuration for specific exchange"""
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not configured")
        return self.exchanges[exchange_name]
    
# Global configuration instance
config = ConfigManager()
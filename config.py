import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values"""
    pass


class Config:
    """
    Configuration manager for loading and accessing application settings.
    Singleton pattern ensures only one instance exists.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, env_path: Optional[str] = None):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize configuration from environment files.
        
        Args:
            env_path: Optional custom path to .env file. 
                     Defaults to '.env' in project root if not specified.
        """
        # Only initialize once
        if self._initialized:
            return
            
        # Determine which .env file to load
        if env_path:
            env_file = Path(env_path)
            if not env_file.exists():
                raise ConfigurationError(
                    f"Environment file not found: {env_path}\n"
                    f"Please check the file path or create the file."
                )
            load_dotenv(env_file, override=False)
        else:
            # Load from project root .env file by default
            # Assumes config.py is in a subdirectory (e.g., /src or /config)
            root_env = Path(__file__).parent.parent / '.env'
            if root_env.exists():
                load_dotenv(root_env, override=False)
            else:
                # Try current directory as fallback
                current_env = Path('.env')
                if current_env.exists():
                    load_dotenv(current_env, override=False)
        
        # Cache configuration values for better performance
        self._cache = {}
        
        # Validate required configuration
        self._validate()
        self._initialized = True
    
    def _validate(self) -> None:
        """Validate that all required configuration values are present and valid"""
        required_keys = {
            'GOOGLE_CLOUD_PROJECT': 'Google Cloud Project ID',
            'GOOGLE_CLOUD_LOCATION': 'Google Cloud Location',
            'GOOGLE_GENAI_USE_VERTEXAI': 'Vertex AI usage flag'
        }
        
        missing = []
        invalid = []
        
        for key, description in required_keys.items():
            value = os.getenv(key)
            if not value:
                missing.append(f"  - {description} ({key})")
            elif key in ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_CLOUD_LOCATION']:
                if not value.strip():
                    invalid.append(f"  - {description} ({key}) cannot be empty")
        
        # Provide comprehensive error message
        if missing or invalid:
            error_parts = ["Configuration errors found:"]
            if missing:
                error_parts.append("\nMissing required values:")
                error_parts.extend(missing)
            if invalid:
                error_parts.append("\nInvalid values:")
                error_parts.extend(invalid)
            error_parts.append("\nPlease set these in your .env file or environment variables.")
            raise ConfigurationError('\n'.join(error_parts))
    
    @property
    def google_cloud_project(self) -> str:
        """Get Google Cloud Project ID"""
        return os.getenv('GOOGLE_CLOUD_PROJECT', '')
    
    @property
    def google_cloud_location(self) -> str:
        """Get Google Cloud Location"""
        return os.getenv('GOOGLE_CLOUD_LOCATION', '')
    
    @property
    def use_vertex_ai(self) -> bool:
        """Get Vertex AI usage flag"""
        value = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '0')
        return value.lower() in ('1', 'true', 'yes', 'on')
    
    @property
    def google_application_credentials(self) -> str:
        """Get path to Google Application Credentials JSON file"""
        return os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    
    
    @property
    def mongodb_url(self) -> Optional[str]:
        """Get MongoDB connection URL"""
        return os.getenv('MONGODB_URL')
    
    @property
    def mongodb_database(self) -> Optional[str]:
        """Get MongoDB database name"""
        return os.getenv('MONGODB_DATABASE')
    
    @property
    def mongodb_collection(self) -> Optional[str]:
        """Get MongoDB collection name"""
        return os.getenv('MONGODB_COLLECTION')
    
    @property
    def mongodb_configured(self) -> bool:
        """Check if MongoDB is fully configured"""
        return all([self.mongodb_url, self.mongodb_database, self.mongodb_collection])
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key name
            default: Default value if key not found
            required: If True, raises error when key is missing
            
        Returns:
            Configuration value
            
        Raises:
            ConfigurationError: If required key is missing
        """
        # Use cache for better performance
        if key in self._cache:
            return self._cache[key]
            
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ConfigurationError(
                f"Missing required configuration key: {key}\n"
                f"Please set this value in your .env file or environment variables."
            )
        
        # Cache the value
        if value is not None:
            self._cache[key] = value
        
        return value
    
    def reload(self, env_path: Optional[str] = None) -> None:
        """
        Reload configuration from environment files.
        Useful for testing or when config changes.
        
        Args:
            env_path: Optional custom path to .env file
        """
        self._cache.clear()
        self._initialized = False
        self.__init__(env_path)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"Config(project={self.google_cloud_project}, "
            f"location={self.google_cloud_location}, "
            f"vertex_ai={self.use_vertex_ai})"
        )


# Lazy loading: only create instance when accessed
_config_instance = None

def get_config(env_path: Optional[str] = None) -> Config:
    """
    Get or create the global configuration instance.
    
    Args:
        env_path: Optional custom path to .env file
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(env_path)
    return _config_instance


# Global config instance for backward compatibility
config = Config()
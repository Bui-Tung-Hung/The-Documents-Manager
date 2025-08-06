"""
Custom exceptions for the application
"""

class ConfigurationError(Exception):
    """Raised when there's a configuration error"""
    pass

class ProviderError(Exception):
    """Raised when there's an error with a provider"""
    pass

class VectorDBError(ProviderError):
    """Raised when there's an error with vector database operations"""
    pass

class EmbeddingError(ProviderError):
    """Raised when there's an error with embedding operations"""
    pass

class SearchError(Exception):
    """Raised when there's an error during search operations"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

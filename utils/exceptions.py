"""Custom exception classes."""


class ConvertKeylogAppError(Exception):
    """Base exception class for ConvertKeylogApp."""
    pass


class ConversionError(ConvertKeylogAppError):
    """Exception raised during conversion process."""
    pass


class ValidationError(ConvertKeylogAppError):
    """Exception raised during data validation."""
    pass


class FileProcessingError(ConvertKeylogAppError):
    """Exception raised during file processing."""
    pass


class ConfigurationError(ConvertKeylogAppError):
    """Exception raised for configuration issues."""
    pass


class UnsupportedFormatError(ConvertKeylogAppError):
    """Exception raised for unsupported file formats."""
    pass


class InvalidInputError(ConvertKeylogAppError):
    """Exception raised for invalid input data."""
    pass


class ProcessingTimeoutError(ConvertKeylogAppError):
    """Exception raised when processing times out."""
    pass

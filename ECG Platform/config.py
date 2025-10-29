"""
Configuration management for ECG2Signal.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Settings can be overridden via environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "ECG2Signal"
    env: Literal["development", "production", "testing"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = True

    # Model Paths
    model_dir: Path = Path("./models")
    unet_model_path: Path = Path("./models/unet_weights.onnx")
    ocr_model_path: Path = Path("./models/ocr_transformer.onnx")
    layout_model_path: Path = Path("./models/layout_cnn.onnx")

    # Processing Configuration
    default_sample_rate: int = 500
    default_paper_speed: float = 25.0  # mm/s
    default_gain: float = 10.0  # mm/mV
    max_image_size: int = 4096
    batch_size: int = 8
    num_workers: int = 4

    # Quality Thresholds
    min_snr: float = 10.0
    max_baseline_drift: float = 0.2
    min_coverage: float = 0.8

    # Export Configuration
    default_export_format: str = "wfdb"
    export_dir: Path = Path("./outputs")

    # Cache Configuration
    enable_cache: bool = True
    cache_dir: Path = Path("./cache")
    cache_max_size_gb: float = 10.0

    # Security
    api_key: str | None = None
    cors_origins: list[str] = ["*"]
    max_upload_size_mb: int = 50

    # Training Configuration
    wandb_api_key: str | None = None
    tensorboard_log_dir: Path = Path("./logs/tensorboard")
    checkpoint_dir: Path = Path("./checkpoints")

    # Database
    database_url: str = "sqlite:///./ecg2signal.db"

    # Privacy
    anonymize_exports: bool = False
    audit_logging: bool = True
    retain_input_images: bool = False

    # Performance
    use_gpu: bool = True
    gpu_device: int = 0
    onnx_optimization_level: int = 3
    parallel_inference: bool = True

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.model_dir,
            self.export_dir,
            self.cache_dir,
            self.tensorboard_log_dir,
            self.checkpoint_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


def get_settings() -> Settings:
    """
    Get application settings instance.

    Returns:
        Settings instance with loaded configuration
    """
    settings = Settings()
    settings.create_directories()
    return settings

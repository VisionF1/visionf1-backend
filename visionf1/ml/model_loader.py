"""
Downloads serialized ML artifacts from Cloudinary on startup.
"""
import logging
from pathlib import Path
import httpx
import os

logger = logging.getLogger(__name__)

class ModelLoader:
    """Downloads and caches ML model files from Cloudinary."""
    
    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        if not self.cloud_name:
            raise ValueError("CLOUDINARY_CLOUD_NAME environment variable not set")
    
    def _build_url(self, public_id: str) -> str:
        """
        Build URL for Cloudinary raw files.
        
        Args:
            public_id: e.g., "models/portable_xgb.json"
        
        Returns:
            Full Cloudinary URL
        """
        # For raw files (not images), we use the /raw/upload/ endpoint
        return f"https://res.cloudinary.com/{self.cloud_name}/raw/upload/{public_id}"
    
    def _download_file(self, public_id: str, filename: str) -> Path:
        """
        Downloads from Cloudinary using public_id.
        
        Args:
            public_id: Cloudinary public_id (e.g., "models/portable_xgb.json")
            filename: Local filename to save
        """
        local_path = self.cache_dir / filename
        
        if local_path.exists():
            logger.info(f"Using cached: {filename}")
            return local_path
        
        url = self._build_url(public_id)
        logger.info(f"⬇Downloading {filename} from {url}")
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url)
                response.raise_for_status()
                local_path.write_bytes(response.content)
            
            logger.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
            return local_path
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error downloading {filename}: {e.response.status_code}")
            logger.error(f"   URL attempted: {url}")
            raise
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            raise
    
    def download_all_artifacts(self) -> dict[str, Path]:
        """
        Downloads all required ML artifacts from Cloudinary.
        
        Returns:
            Dictionary mapping artifact names to local paths
        """
        artifacts = {
            "model": ("portable_xgb.json", "portable_xgb.json"),
            "history_store": ("history_store.pkl", "history_store.pkl"),
            "feature_names": ("/feature_names.pkl", "feature_names.pkl"),
        }
        
        paths = {}
        for key, (public_id, filename) in artifacts.items():
            paths[key] = self._download_file(public_id, filename)
        
        logger.info(f"All artifacts ready in: {self.cache_dir}")
        return paths
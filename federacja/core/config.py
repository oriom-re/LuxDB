
"""
⚙️ Federation Configuration - Konfiguracja Federacji
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

@dataclass
class FederationConfig:
    """Konfiguracja Federacji"""
    kernel_name: str = "FederationKernel"
    kernel_version: str = "1.0.0"
    kernel_description: str = "Kernel Federacji"
    kernel_author: str = "Wilson"
    kernel_license: str = "MIT"
    kernel_dependencies: List[str] = field(default_factory=list)
    manifest_path: Path = field(default_factory=lambda: Path("federacja/manifests/manifest.yaml"))
    logger: Dict[str, Any] = field(default_factory=lambda: {'level': 'INFO', 'format': 'console'})
    
    @classmethod
    def from_manifest(cls, manifest_path: Path) -> 'FederationConfig':
        """Tworzy konfigurację z pliku manifestu"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return cls(
                kernel_name=data.get('kernel', {}).get('name', 'FederationKernel'),
                kernel_version=data.get('kernel', {}).get('version', '1.0.0'),
                kernel_description=data.get('kernel', {}).get('description', 'Kernel Federacji'),
                kernel_author=data.get('kernel', {}).get('author', 'Wilson'),
                kernel_license=data.get('kernel', {}).get('license', 'MIT'),
                kernel_dependencies=data.get('kernel', {}).get('dependencies', []),
                manifest_path=manifest_path,
                logger=data.get('logger', {'level': 'INFO', 'format': 'console'})
            )
        except Exception as e:
            print(f"⚠️ Błąd podczas ładowania manifestu: {e}")
            return cls(manifest_path=manifest_path)

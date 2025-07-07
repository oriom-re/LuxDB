
#!/usr/bin/env python3
"""
🔮 Start AstralKernel - Punkt wejścia dla kernela opartego na AstralEngine

Łączy potęgę LuxDB v2 z architekturą Federacji
"""

import asyncio
from pathlib import Path
from federacja.core.astral_kernel import AstralKernel
from federacja.core.config import FederationConfig

async def main():
    print("🔮 Uruchamianie AstralKernel - Fuzja Federacji z LuxDB v2...")
    
    # Konfiguracja dla AstralKernel
    config = FederationConfig(
        kernel_name="AstralKernel",
        kernel_version="2.0.0",
        kernel_description="Kernel Federacji oparty na AstralEngine",
        kernel_author="Wilson",
        kernel_license="MIT",
        kernel_dependencies=["luxdb_v2"],
        manifest_path=Path("federacja/manifests/manifest.yaml"),
        logger={'level': 'INFO', 'format': 'console'}
    )

    # Utwórz i uruchom AstralKernel
    kernel = AstralKernel(config)

    try:
        await kernel.start()
    except KeyboardInterrupt:
        print("\n⭐ Zatrzymywanie AstralKernel...")
        await kernel.stop()
        print("✨ AstralKernel zatrzymany - transcendencja zakończona")

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
from pathlib import Path
from federacja.core.kernel import FederationKernel
from federacja.core.config import FederationConfig

async def main():
    # Konfiguracja kernela
    config = FederationConfig(
        kernel_name="FederationKernel",
        kernel_version="1.0.0",
        kernel_description="Kernel Federacji",
        kernel_author="Wilson",
        kernel_license="MIT",
        kernel_dependencies=["test"],
        manifest_path=Path("federacja/manifests/manifest.yaml"),
        logger={'level': 'INFO', 'format': 'console'}
    )

    # Uruchom kernel
    kernel = FederationKernel(config)

    try:
        await kernel.start()
    except KeyboardInterrupt:
        print("\n⭐ Zatrzymywanie kernela...")
        await kernel.stop()
        print("✨ Kernel zatrzymany")

if __name__ == "__main__":
    asyncio.run(main())

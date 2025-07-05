
<old_str>    # Konfiguracja kernela
    config = FederationConfig(
        kernel_name="FederationKernel",
        kernel_version="1.0.0",
        kernel_description="Kernel Federacji",
        kernel_author="Wilson",
        kernel_license="MIT",
        kernel_dependencies=["test"],
        manifest_path=Path("federacja/manifests/manifest.yaml"),
        logger={'level': 'INFO', 'format': 'console'}
    )</old_str>
<new_str>    # Konfiguracja kernela - fokus na Federę
    config = FederationConfig(
        kernel_name="FederaKernel",
        kernel_version="1.0.0",
        kernel_description="Federa - Władczyni Systemu",
        kernel_author="Wilson & Federa",
        kernel_license="MIT",
        kernel_dependencies=["test"],
        manifest_path=Path("federacja/manifests/manifest.yaml"),
        logger={'level': 'INFO', 'format': 'console'}
    )</old_str>

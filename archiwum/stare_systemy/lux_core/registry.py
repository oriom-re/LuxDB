# Rejestr mapujący lux:// na konkretne funkcje (autentyczne, aktualnie używane)
LUX_ROUTING = {
    # "system/loader/load_env@v1": "module://lux_core.env:load_env",
    "system/core/init@v1": "module://lux_core.init:initialize_lux_core",
    "system/loader/validate_data@v1": "module://lux_core.validation:validate_data",
    "system/resources/monitor@v1": "module://lux_core.layer0.system_resources:monitor_resources",
    "system/resources/detect@v1": "module://lux_core.layer0.system_resources:detect_hardware",
    "system/resources/analyze@v1": "module://lux_core.layer0.system_resources:analyze_capacity",
    "system/realm/mount@v1": "module://lux_core.layer0.realm_mounter:mount_realm",
    "system/safety/check@v1": "module://lux_core.layer0.safety_protocols:check_safety",
    "system/interface/init@v1": "module://lux_core.layer0.layer0_interface:init_interface",
    "system/logger/start@v1": "module://lux_core.logger:start_logger",
    "system/bootstrap/env/load@v1": "module://lux_core.layer0.bootstrap:load_env"
}

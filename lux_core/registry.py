# Rejestr mapujący lux:// na konkretne funkcje (autentyczne, aktualnie używane)
LUX_ROUTING = {
    "system/loader/load_env@v1": "module://lux_core.env:load_env",
    "system/loader/validate_data@v1": "module://lux_core.validation:validate_data",
    "system/resources/monitor@v1": "module://lux_core.layer0.system_resources:monitor_resources",
    "system/realm/mount@v1": "module://lux_core.layer0.realm_mounter:mount_realm",
    "system/safety/check@v1": "module://lux_core.layer0.safety_protocols:check_safety",
    "system/interface/init@v1": "module://lux_core.layer0.layer0_interface:init_interface",
    "system/logger/start@v1": "module://lux_core.logger:start_logger"
}

default_app_config = 'dashboard.inventory.apps.InventoryConfig'

class CameraState:
    DISABLED = 0
    ENABLED = 1
    CHOICES = (
        (DISABLED, 'Disabled'),
        (ENABLED, 'Enabled'),
    )        

class RecorderMethod:
    VLC = 1
    VLC_SNAP = 2
    HTTP_GET = 3
    CHOICES = (
        (VLC, 'VideoLAN'),
        (VLC_SNAP, 'VideoLAN Snapshot'),
        (HTTP_GET, 'HTTP Get'),
    )        


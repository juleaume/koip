import storage
import supervisor

storage.disable_usb_drive()
supervisor.runtime.autoreload = False
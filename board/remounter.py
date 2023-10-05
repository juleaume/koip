import storage

storage.remount("/", readonly=False)
with open("boot.py", "a") as b:
    b.write("\nstorage.enable_usb_drive()\n")
# Recovery and Rollback

[简体中文](RECOVERY.md) | **English** | [Project overview](../README.en.md)

This public package contains no personal device backups or flashable images.

For kernel recovery, use your own original images and restore the correct partitions and slots. `boot` and `init_boot` serve different roles: never guess the restore target. Do not relock the bootloader on a device running a modified or cross-region system.

The privacy example's `restore.sh` removes only the firewall rules/chains named by this module and restores Analytics/MSA to their default states. That is appropriate only if their original states were the defaults. Devices with manually enabled/disabled packages or different user configurations must restore their actual backed-up states instead.

Disabling a Magisk module does not automatically undo package disabling performed through PackageManager. Explicitly execute the reviewed recovery steps before managing or removing the module. Do not flush every iptables rule as a rollback shortcut.

The recovery script is a reference implementation and is not guaranteed to work on every ROM. Validate it first on a test device with console access and offline recovery options.

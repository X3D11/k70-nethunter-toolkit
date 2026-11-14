# Build and Validation Workflow

[简体中文](BUILD.md) | **English** | [Project overview](../README.md)

This public package is not a complete, reproducible kernel build environment. It excludes device configurations, vendor ABI captures, module-signing keys, complete toolchains, firmware, kernel source trees, and final images.

1. Back up your own boot-related partitions, such as `boot`, `init_boot`, and `vendor_boot`, and device-unique partitions such as `modemst1`, `modemst2`, `fsg`, `fsc`, and `persist`. Confirm which partitions actually exist on your device. Read each at least twice, compare sizes and hashes, and protect the backups offline.
2. Record the system version, active slot, update/snapshot merge status, and exact GKI source version. The experiment used Android Common Kernel commit `f4321180a3973d19b626b3eef51871199e4e1fac`; do not assume it matches another system build.
3. Build a baseline first. Preserve critical layouts, CFI, and signature protection, then add features individually. The experiment used Clang/LLVM 14 and a separate pahole 1.24 installation; these versions are not universal requirements.
4. Capture vendor module imports from your device and compare them against independently built export CRCs. Explain BTF layout changes individually. Assigning an expected CRC to an importing module does not independently prove header ABI compatibility.
5. Repack using the boot image format appropriate for the device. Check the header, architecture, size, and partition capacity. Read the checking tools' source for their exact input formats.
6. Temporarily boot before persistent installation. Check the display, cameras, modem, audio, Wi-Fi, root access, SELinux, loaded modules, and error logs before deciding whether to write an image persistently.
7. Validate USB wireless functionality with real hardware. Successful driver loading establishes module registration only.

No flashing commands are provided here. The operator must determine the correct action using their own device information and recovery options. Do not remove thermal protection, force-unload permanent modules, or disable SELinux to conceal compatibility problems.

# Redmi K70 NetHunter Adaptation and Privacy Toolkit

[简体中文](README.zh-CN.md) | **English**

Experimental notes and supporting source code for running Android-based NetHunter on the Redmi K70 (`vermeer`). This project provides tools for checking GKI/vendor module compatibility, launching Kali in a private mount namespace, and implementing reversible privacy controls.

**This is a source and methodology toolkit, not an official NetHunter device-support announcement or a universal flashing package.** It contains no flashable kernels, vendor modules, firmware, or APKs. Never flash another device's images onto your phone.

## Test environment and observed results

- Device: a China-market Redmi K70 running Global HyperOS, Android 16, and a 5.15.194-series GKI kernel.
- Android is retained; NetHunter runs through Magisk root and a Kali ARM64 chroot.
- The experimental kernel adds SysV IPC, IPC namespaces, USB Bluetooth support, and related functionality while retaining CFI and module signature protection.
- Vendor module symbol CRCs, critical structure layouts, and boot image structure were checked before temporary boot testing and persistent installation.
- On the tested device, all 406 original modules and 17 additional USB wireless driver/dependency modules loaded successfully. These counts depend on the system build and are not universal acceptance criteria.
- The Kali shell entry point and a temporary local Xfce/VNC desktop startup test passed. No desktop credentials are included.
- External USB wireless adapters were not tested with physical hardware. Reception, transmission, monitor mode, injection, and compatibility with specific adapters are therefore not guaranteed.

These observations apply only to the tested device and build. They do not establish compatibility with other ROMs, OTA versions, or hardware combinations.

## Repository layout

```text
src/chroot-launcher.c       Chroot launcher using a private mount namespace
tools/                     ELF module ABI, BTF, and boot image checks
examples/privacy/          Per-UID firewall and recovery reference scripts
docs/BUILD.en.md           Build/validation workflow and missing dependencies
docs/PRIVACY.en.md         Publication scope and audit limitations
docs/RECOVERY.en.md        Recovery and rollback guidance
```

## Prerequisites

You should understand ADB, Fastboot, Linux, Android partitions, and root access. Boot image operations require an unlocked bootloader and verified, recoverable backups of your own device.

Use source code, configuration, original images, and slot information that match your exact device and system version. These device-specific inputs are not included. Passing CRC, layout, and image structure checks does not replace temporary boot testing on real hardware.

## Analysis tool examples

The included Python tools primarily use the standard library. Check each script's source for its required inputs and dependencies before running it.

```bash
python tools/inspect-module.py /path/to/example.ko
python tools/compare-module-abi.py /path/to/Module.symvers /path/to/example.abi.json --output report.json
python tools/verify-boot-candidate.py /path/to/stock-boot.img /path/to/candidate-boot.img /path/to/Image boot-report.json
```

`src/chroot-launcher.c` currently uses the fixed experimental rootfs path `/data/local/codex-nethunter/kali-arm64`. Change the `root` path in the source for your environment, then compile with a toolchain targeting the device architecture. Do not overwrite an existing environment blindly.

The launcher creates a private mount namespace and checks mount propagation before preparing device nodes, proc, and devpts and entering the chroot. Its proc mount is read-only, so software that requires writing to proc may not work. **It isolates mount propagation, not networking, processes, or the entire Android security boundary.**

## Privacy control examples

The experimental approach targets Analytics, MSA, and GuardProvider: the first two can be reversibly disabled, while GuardProvider's outbound connectivity is restricted by its independently owned UID without removing its local components.

The example scripts are **not a complete installable Magisk module**. Before integrating them, supply module metadata, back up the real starting state, and review all behavior for your device.

The firewall script checks that GuardProvider does not share its UID with another package, then creates dedicated IPv4/IPv6 chains. It retains loopback traffic and does not flush unrelated firewall rules. It blocks traffic belonging to that UID; it does not guarantee coverage of proxy services running under other UIDs or every embedded system SDK.

**The recovery script assumes Analytics and MSA originally had the default enabled state (`0`).** If that is not true on your device, save and restore the actual original states instead. Restricting GuardProvider networking affects cloud antivirus queries and online virus-definition updates. Thermal management, SELinux, SecurityCenter, and modem partitions are not disabling targets in this example.

The test network had no IPv6 default route. IPv6 rule installation was checked, but real IPv6 outbound connectivity was not tested.

## Important limitations

- The presence of code, permissions, domain strings, or kernel modules alone does not prove actual recording, surveillance, or uploading.
- A Global ROM is not necessarily free of telemetry. Findings about one component cannot be generalized to all versions.
- This toolkit does not include lock-screen, payment integrity, or device-attestation bypasses.
- It does not automatically flash images, delete system components, or upload logs.
- Recheck the kernel, module ABI, application UIDs, and firewall rules after OTA updates.

## Privacy and publication

This repository was prepared from an explicit allowlist of reviewed source files and newly written documentation. It excludes partition backups, accounts, device identifiers, databases, logs, screenshots, raw forensic output, private signing keys, APKs, rootfs archives, images, and firmware.

**Upload only the prepared release directory or the extracted release ZIP, never the original working directory.** Before opening an issue, remove serial numbers, IMEIs, MAC/IP addresses, account information, call records, and access tokens from any attachments or output.

Additional documentation:

- [Build and validation](docs/BUILD.en.md)
- [Privacy and audit scope](docs/PRIVACY.en.md)
- [Recovery and rollback](docs/RECOVERY.en.md)

## Upstream projects and licensing

- [Kali NetHunter](https://www.kali.org/docs/nethunter/)
- [Android Common Kernel](https://android.googlesource.com/kernel/common/)
- [MiCode kernel sources](https://github.com/MiCode/Xiaomi_Kernel_OpenSource)
- [Magisk](https://github.com/topjohnwu/Magisk)
- [Android DEX format](https://source.android.com/docs/core/runtime/dex-format)

The original helper source code and documentation published here are licensed under MIT. Upstream kernels, third-party patches, and binaries are not redistributed in this repository and remain subject to their respective licenses. If you redistribute a kernel or vendor module, independently verify the relevant licensing, source-distribution obligations, and redistribution permissions.

This project is not officially affiliated with Xiaomi, Kali, Google, or Magisk.

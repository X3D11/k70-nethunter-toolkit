# Privacy Protection and Audit Scope

[简体中文](PRIVACY.md) | **English** | [Project overview](../README.en.md)

Publication uses an explicit file allowlist rather than uploading the original workspace after deleting a few sensitive files. The original Git history, partition images, device databases, logs, personal directories, attachments, accounts, tokens, keys, third-party APK/rootfs archives, and vendor binaries are excluded.

Android package names, standard device paths, and kernel versions appearing in the public scripts are technical configuration, not personal device identifiers. The SHA256 manifest covers only the files in this public package.

Failure to find a named class or database is not proof that all telemetry is absent. A static string match is not evidence of execution either. An audit should distinguish code capabilities, activation conditions, actual execution, and actual transmitted content. Obtain appropriate authorization before collecting real communications, and minimize what is collected.

Even when source files contain no private data, running the tools may produce output containing device information. Keep generated output out of the repository by default; review it before sharing separately.

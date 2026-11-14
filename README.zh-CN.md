# Redmi K70 NetHunter 适配与隐私控制工具集

**简体中文** | [English](README.md)

面向 Redmi K70（`vermeer`）的 Android NetHunter 实验记录与辅助源码。项目整理了 GKI 内核与厂商模块兼容性检查、隔离 Kali chroot 启动，以及可恢复隐私控制的实现示例。

**这是源码与方法工具集，不是官方 NetHunter 设备支持声明，也不是通用一键刷机包。** 发布包不包含可直接刷写的内核、厂商模块、固件或 APK。请勿把其他设备的镜像用于自己的手机。

## 测试背景与已完成工作

- 设备：Redmi K70，原国行设备，运行 Global HyperOS；Android 16、5.15.194 系列 GKI。
- 保留 Android，通过 Magisk Root 和 Kali ARM64 chroot 运行 NetHunter。
- 实验内核加入 SysV IPC、IPC namespace、USB Bluetooth 等支持；保留 CFI 和模块签名保护。
- 核验厂商模块导入符号 CRC、关键结构体布局、启动镜像结构后，先临时启动，再进行持久安装。
- 单台设备验证中，原有 406 个模块与 17 个新增 USB 无线驱动依赖模块成功加载。数量随系统版本变化，不是通用验收标准。
- Kali 终端入口及临时本机 Xfce/VNC 桌面启动测试通过。本仓库不附带桌面登录凭据。
- 外接无线网卡未做硬件实测，因此不保证监听、注入、收发或所有适配器功能。

以上仅代表特定设备和构建上的观察，不构成对其他 ROM、OTA 或硬件组合的兼容性保证。

## 目录

```text
src/chroot-launcher.c       私有挂载命名空间内的 chroot 启动器
tools/                     ELF 模块 ABI、BTF 和 boot 镜像检查工具
examples/privacy/          针对单一应用 UID 的防火墙及恢复参考脚本
docs/BUILD.md              构建与验证流程、缺失依赖说明
docs/PRIVACY.md            发布范围、隐私保护和审计边界
docs/RECOVERY.md           回滚与恢复说明
```

## 使用前提

需要熟悉 ADB、Fastboot、Linux、Android 分区和 Root 权限。涉及启动镜像的操作要求设备已解锁 Bootloader，并已保存本机可恢复备份。

必须使用匹配自己设备、系统版本和当前槽位的源代码、配置与原始镜像。本仓库没有提供这些设备专属文件。CRC、布局和镜像结构检查通过，也不能替代实机临时启动验证。

## 分析工具示例

工具主要使用 Python 标准库。BTF 分析相关脚本可能调用外部工具，运行前检查其参数和依赖。

```bash
python tools/inspect-module.py /path/to/example.ko
python tools/compare-module-abi.py /path/to/Module.symvers /path/to/example.abi.json --output report.json
python tools/verify-boot-candidate.py /path/to/stock-boot.img /path/to/candidate-boot.img /path/to/Image boot-report.json
```

`src/chroot-launcher.c` 当前使用固定的实验 rootfs 路径 `/data/local/codex-nethunter/kali-arm64`。移植前修改源码中的 root 路径，再用目标架构工具链编译；不要直接覆盖已有环境。它会创建私有挂载命名空间并核查传播属性，在该环境中挂载设备、proc 和 devpts，随后进入 chroot。proc 为只读，部分依赖写入 proc 的程序不适用。它隔离挂载传播，不隔离网络、进程或整个 Android 安全边界。

## 隐私控制示例

实验方案针对 Analytics、MSA 与 GuardProvider：前两者可恢复停用；GuardProvider 按独立 UID 限制外联，保留应用本地组件。示例脚本不构成完整可安装 Magisk 模块，需自行制作模块元数据、备份状态并审核后集成。

脚本会确认 GuardProvider UID 不与其他包共享，再建立独立 IPv4/IPv6 链；保留回环，不清空其他防火墙规则。它阻断的是该 UID 的外联，不保证覆盖其他进程代理联网或所有系统 SDK。

**恢复脚本有明确前提：Analytics/MSA 的原始状态均为默认状态（0）。** 其他设备应先保存真实状态并修改恢复逻辑，不能照搬。云查毒与在线病毒库更新会受联网限制影响。温控、SELinux、安全中心和基带不属于本示例的停用目标。

测试环境没有 IPv6 默认路由：IPv6 规则安装已检查，但没有完成 IPv6 实际外联验证。

## 重要限制

- 代码、权限、域名字符串或模块存在，不能单独证明实际录制、监控或上传行为。
- Global ROM 不等于没有遥测；对某个组件的检查结果不能推广到所有版本。
- 不包含绕过锁屏、支付完整性校验或设备认证的功能。
- 不包含自动刷入、自动删除系统组件或自动上传日志的操作。
- OTA 后应重新核验内核、模块 ABI、UID 和防火墙规则。

## 隐私与发布

本仓库采用白名单打包，仅发布少量审核后的源码和重新撰写的说明。设备分区备份、账号、设备标识、数据库、日志、截图、原始审计输出、签名私钥、APK、rootfs、镜像和固件均未纳入。

**请上传本发布目录或 ZIP 解压后的内容，不要上传原始工作目录。** 提交 issue 时请先删去序列号、IMEI、MAC、IP、账号、通话记录和访问令牌。

## 上游与许可

- [Kali NetHunter](https://www.kali.org/docs/nethunter/)
- [Android Common Kernel](https://android.googlesource.com/kernel/common/)
- [MiCode 内核源码](https://github.com/MiCode/Xiaomi_Kernel_OpenSource)
- [Magisk](https://github.com/topjohnwu/Magisk)
- [Android DEX 格式](https://source.android.com/docs/core/runtime/dex-format)

本仓库发布的原创辅助源码和文档使用 MIT 许可。没有重新分发上游内核、第三方补丁或二进制；其许可由各上游项目决定。重新发布内核或厂商模块时，必须单独确认源码提供义务、许可和再分发权限。本项目与 Xiaomi、Kali、Google 或 Magisk 项目没有官方从属关系。

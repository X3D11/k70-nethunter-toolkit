#!/system/bin/sh
MODDIR=${0%/*}
umask 077
mkdir -p /data/adb/codex_privacy_state
/system/bin/sh "$MODDIR/firewall.sh" > /data/adb/codex_privacy_state/early-service.log 2>&1

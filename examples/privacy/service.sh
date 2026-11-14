#!/system/bin/sh
MODDIR=${0%/*}
umask 077
exec > /data/adb/codex_privacy_state/late-service.log 2>&1
while [ "$(getprop sys.boot_completed)" != 1 ]; do sleep 3; done
/system/bin/sh "$MODDIR/firewall.sh"

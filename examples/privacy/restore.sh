#!/system/bin/sh
set -eu
MODDIR=${0%/*}
state=/data/adb/codex_privacy_state
chain=codex_gp_out
# Disable automatic reapplication first. Only this task's chains are removed.
touch "$MODDIR/disable"
uid=$(cat "$state/guard-uid" 2>/dev/null || true)
case "$uid" in ''|*[!0-9]*) echo 'No valid recorded UID; inspect rules manually'; exit 1;; esac
for tool in /system/bin/iptables /system/bin/ip6tables; do
    while "$tool" -w 2 -C OUTPUT -m owner --uid-owner "$uid" -j "$chain" 2>/dev/null; do
        "$tool" -w 2 -D OUTPUT -m owner --uid-owner "$uid" -j "$chain"
    done
    if "$tool" -w 2 -S "$chain" >/dev/null 2>&1; then
        "$tool" -w 2 -F "$chain"
        "$tool" -w 2 -X "$chain"
    fi
done
# Original enabled state for these two packages was verified as default (0).
pm default-state --user 0 com.miui.analytics
pm default-state --user 0 com.miui.msa.global
echo 'Restored original package states and removed task firewall rules.'

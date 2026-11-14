#!/system/bin/sh
set -eu
MODDIR=${0%/*}
state=/data/adb/codex_privacy_state
chain=codex_gp_out
mkdir -p "$state"
chmod 0700 "$state"
uid=$(awk '$1=="com.miui.guardprovider" {print $2}' /data/system/packages.list)
case "$uid" in ''|*[!0-9]*) echo 'No valid GuardProvider UID'; exit 1;; esac
[ "$uid" -ge 10000 ] && [ "$uid" -lt 20000 ]
names=$(awk -v id="$uid" '$2==id {print $1}' /data/system/packages.list)
old=$(cat "$state/guard-uid" 2>/dev/null || true)
remove_jump() {
    id=$1
    case "$id" in ''|*[!0-9]*) return;; esac
    for tool in /system/bin/iptables /system/bin/ip6tables; do
        while "$tool" -w 2 -C OUTPUT -m owner --uid-owner "$id" -j "$chain" 2>/dev/null; do
            "$tool" -w 2 -D OUTPUT -m owner --uid-owner "$id" -j "$chain"
        done
    done
}
if [ "$names" != com.miui.guardprovider ]; then
    remove_jump "$old"
    echo 'UID is shared: refused broad network blocking'
    exit 1
fi
if [ -n "$old" ] && [ "$old" != "$uid" ]; then remove_jump "$old"; fi
for tool in /system/bin/iptables /system/bin/ip6tables; do
    case "$tool" in *ip6tables) loopback=::1/128;; *) loopback=127.0.0.0/8;; esac
    "$tool" -w 2 -N "$chain" 2>/dev/null || "$tool" -w 2 -S "$chain" >/dev/null
    "$tool" -w 2 -C "$chain" -d "$loopback" -j RETURN 2>/dev/null || "$tool" -w 2 -A "$chain" -d "$loopback" -j RETURN
    "$tool" -w 2 -C "$chain" -j REJECT 2>/dev/null || "$tool" -w 2 -A "$chain" -j REJECT
    "$tool" -w 2 -C OUTPUT -m owner --uid-owner "$uid" -j "$chain" 2>/dev/null || "$tool" -w 2 -I OUTPUT 1 -m owner --uid-owner "$uid" -j "$chain"
done
echo "$uid" > "$state/guard-uid"
chmod 0600 "$state/guard-uid"
echo "GuardProvider UID $uid IPv4/IPv6 egress blocked; loopback retained."

#!/usr/bin/env bash
set -euo pipefail

source /opt/hades/bin/functions.sh

print_usage() {
	msg "\
Usage: $0 [-h] [--help]

Update unbound's trust anchor with

Options:
  -h --help             Print this message"
}

readonly DNS_ROOT_KEY_FILE="/usr/share/dns/root.key"
readonly ROOT_TRUST_ANCHOR_FILE="/var/lib/hades/auth-dns/root.key"

main() {
	if (( $# > 0 )); then
		print_usage
		case "$1" in
			-h|--help) exit "$EX_OK";;
			*)         exit "$EX_USAGE";;
		esac
	fi
	load_config
	if [[ ! -f "$DNS_ROOT_KEY_FILE" ]]; then
		error "Error: DNS root key file $DNS_ROOT_KEY_FILE missing. Install the dns-root-data package."
		exit 2
	fi
	if [[ "$DNS_ROOT_KEY_FILE" -nt "$ROOT_TRUST_ANCHOR_FILE" ]]; then
		if [[ -f "$ROOT_TRUST_ANCHOR_FILE" ]]; then
			msg "Updating $ROOT_TRUST_ANCHOR_FILE with newer $DNS_ROOT_KEY_FILE."
		else
			msg "Missing $ROOT_TRUST_ANCHOR_FILE. Copying from $DNS_ROOT_KEY_FILE."
		fi
		install --mode=0644 --owner="$HADES_UNBOUND_USER" --group="$HADES_UNBOUND_GROUP" "$DNS_ROOT_KEY_FILE" "$ROOT_TRUST_ANCHOR_FILE"
	fi
	/usr/sbin/unbound-anchor -a "$ROOT_TRUST_ANCHOR_FILE" || :
}

main "$@"

#!/usr/bin/env bash
# capture_attack.sh
# Usage: sudo ./capture_attack.sh <LABEL> <OUTPUT_DIR>
# Example: sudo ./capture_attack.sh WirePatrol /mnt/SDD128GB/tshark_data/log/pcaps

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <LABEL> <OUTPUT_DIR>"
  exit 1
fi

LABEL="$1"
OUTPUT_DIR="$2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PCAP_FILE="${OUTPUT_DIR}/${LABEL}_${TIMESTAMP}.json"
INTERFACE="eth0"    # adjust if your public interface is named differently

# Make sure output dir exists
mkdir -p "$OUTPUT_DIR"

echo ">> Starting capture for '${LABEL}'"
echo "   Interface: $INTERFACE"
echo "   Writing to: $PCAP_FILE"
echo ">> Press Ctrl-C to stop capture and save."

# Run tshark with a capture filter; needs root (or dumpcap privileges)
tshark -i "$INTERFACE" \
	   -T json > "$PCAP_FILE"

echo ">> Capture complete. Saved to $PCAP_FILE"

chown 1001:1001 "$PCAP_FILE"
echo ">> Changed owner of $PCAP_FILE to UID=1001 and GID=1001"
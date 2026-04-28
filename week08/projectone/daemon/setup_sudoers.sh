#!/usr/bin/env bash
# Grant the current user passwordless sudo rights for shutdown, poweroff, and reboot.
#
# Why this is needed:
#   The daemon calls `systemctl reboot` / `systemctl poweroff` directly (no sudo needed
#   when running as root under systemd). However, if you ever call these commands from
#   a non-root script or want to test them manually as the `pi` user, sudo would normally
#   prompt for a password — which is impossible in an automated/headless context.
#   This script adds entries to /etc/sudoers.d/ to allow passwordless execution.
#
# Usage: sudo bash setup_sudoers.sh
set -euo pipefail

# Must be run as root to write to /etc/sudoers.d/
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash setup_sudoers.sh"
    exit 1
fi

# Determine the real user (SUDO_USER is set when invoked via sudo; fall back to current user)
CURRENT_USER="${SUDO_USER:-}"
if [ -z "$CURRENT_USER" ]; then
    CURRENT_USER="$(id -un)"
fi

# Write one sudoers file per command — granular files are easier to audit and remove
echo "$CURRENT_USER ALL=(root) NOPASSWD: /sbin/shutdown"  > /etc/sudoers.d/project_one_shutdown
echo "$CURRENT_USER ALL=(root) NOPASSWD: /sbin/poweroff"  > /etc/sudoers.d/project_one_poweroff
echo "$CURRENT_USER ALL=(root) NOPASSWD: /sbin/reboot"    > /etc/sudoers.d/project_one_reboot

# sudoers files must be read-only and not world-readable
chmod 440 /etc/sudoers.d/project_one_shutdown
chmod 440 /etc/sudoers.d/project_one_poweroff
chmod 440 /etc/sudoers.d/project_one_reboot

# Validate the entire sudoers configuration before we finish — catches any syntax errors
visudo -c && echo "Sudoers configured for $CURRENT_USER"

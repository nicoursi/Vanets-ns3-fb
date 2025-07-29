#!/bin/bash

# === Info Message ===
echo "This script ensures your environment is set up to source the custom .bashrc from:"
echo "  ~/storage/Vanets-ns3-fb/build-env/.bashrc"
echo
echo "If the line isn't already in ~/.bash_profile, it will be prepended automatically."
echo
echo "To add or modify aliases, edit the following file:"
echo "  ~/storage/Vanets-ns3-fb/build-env/.bashrc"
echo "You can add lines like: alias ll='ls -lah'"
echo

# === Logic ===
BASH_PROFILE="$HOME/.bash_profile"
LINE='[[ -f ~/storage/Vanets-ns3-fb/build-env/.bashrc ]] && source ~/storage/Vanets-ns3-fb/build-env/.bashrc'

# Check if the line is already present
if ! grep -Fxq "$LINE" "$BASH_PROFILE"; then
    # Prepend the line to .bash_profile
    tmpfile=$(mktemp)
    echo "$LINE" > "$tmpfile"
    cat "$BASH_PROFILE" >> "$tmpfile"
    mv "$tmpfile" "$BASH_PROFILE"
    echo "✅ Line added to $BASH_PROFILE"
else
    echo "ℹ️  Line already exists in $BASH_PROFILE — nothing changed."
fi

#!/bin/bash
### Find the actual project root
CURRENT_DIR="$(pwd)"
PROJECT_ROOT=""
while [[ "$CURRENT_DIR" != "/" ]]; do
 if [[ -d "$CURRENT_DIR/ns-3" ]]; then
     PROJECT_ROOT="$CURRENT_DIR"
     break
 fi
 CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

if [[ -z "$PROJECT_ROOT" ]]; then
 echo "ERROR: Could not find project root (looking for ns-3/)">&2
 echo "Searched from: $(pwd)">&2
 exit 1
fi
export PROJECT_ROOT

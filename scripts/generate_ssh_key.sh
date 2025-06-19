#!/bin/bash
# generate_ssh_key.sh
# Safely generate a new SSH key with prudent options and guidance.

set -e

# Prompt for email/comment
read -p "Enter your email for the SSH key comment: " EMAIL

# Prompt for key type
read -p "Choose key type (ed25519/rsa) [ed25519]: " KEYTYPE
KEYTYPE=${KEYTYPE:-ed25519}

# Prompt for key filename
read -p "Enter a filename for your new SSH key [~/.ssh/id_${KEYTYPE}]: " KEYFILE
KEYFILE=${KEYFILE:-~/.ssh/id_${KEYTYPE}}

# Prompt for passphrase
read -s -p "Enter a passphrase (leave blank for none): " PASSPHRASE

echo

# Generate the key
if [ "$KEYTYPE" = "rsa" ]; then
  ssh-keygen -t rsa -b 4096 -C "$EMAIL" -f "$KEYFILE" ${PASSPHRASE:+-N "$PASSPHRASE"}
else
  ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEYFILE" ${PASSPHRASE:+-N "$PASSPHRASE"}
fi

# Show the public key
echo
cat "${KEYFILE}.pub"
echo

echo "Your new SSH key has been generated."
echo "Add the public key above to your GitHub, server, or service as needed."
echo "Private key: $KEYFILE"
echo "Public key: ${KEYFILE}.pub"

# Offer to copy public key to clipboard (if xclip or pbcopy is available)
if command -v xclip &> /dev/null; then
  cat "${KEYFILE}.pub" | xclip -selection clipboard
  echo "(Public key copied to clipboard with xclip.)"
elif command -v pbcopy &> /dev/null; then
  cat "${KEYFILE}.pub" | pbcopy
  echo "(Public key copied to clipboard with pbcopy.)"
else
  echo "(Install xclip or pbcopy to enable clipboard copy.)"
fi

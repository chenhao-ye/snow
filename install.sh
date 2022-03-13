#!/bin/bash

pip3 install -r requirements.txt
rm -rf "$HOME/.snow"
cp -rf . "$HOME/.snow"

# shellcheck disable=SC2016
echo 'Install SNOW to $HOME/.snow successfully'
# shellcheck disable=SC2016
echo 'To use SNOW, make sure "$HOME/.snow/bin" is in the $PATH:'
echo "    echo 'export PATH=\"\$PATH:\$HOME/.snow/bin\"' >> ~/.bashrc # OR ~/.zshrc"

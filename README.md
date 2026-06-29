# Configurations of my system

These are most configration files I use on my computers

## MacOS setup

Basic setup

```zsh
touch $HOME/.hushlogin                                                          # Hide last login message
xcodebuild -runFirstLaunch                                                      # Ensure Xcode
defaults write com.apple.dock autohide-delay -float 0                           # Quick Dock
defaults write com.apple.dock autohide-time-modifier -float 0.05                #   "
killall Dock                                                                    #   "
defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true        # Don't write stores (.DS_Stores) on external USB
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true    #               "                 on network shares
sudo mdutil -i off -d /Volumes/Delt                                             # Do not index this volume
sudo mdutil -i off -d /Volumes/Ekstern                                          #               "
```

Use Touch ID with `sudo`

```zsh
echo "auth sufficient pam_tid.so" | sudo tee /etc/pam.d/sudo_local > /dev/null
```

Finder

```zsh
defaults write com.apple.finder DisableAllAnimations -bool true
defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"
```

SSH key creation

```zsh
ssh-keygen -o -a 1024 -t ed25519 -C "${HOST/.local}"            # Generate a keypair
ssh-copy-id -i $HOME/.ssh/id_ed25519.pub user@remote-host       # Copy public key to remote host
eval $(ssh-agent)                                               # Set up the SSH agent
ssh-add --apple-use-keychain $HOME/.ssh/id_ed25519              # Add the key and store passphrase into keychain
```

If copying the public key to clipboard is required

```zsh
pbcopy < $HOME/.ssh/id_ed25519.pub
```

Automatic use of the keys for remote host (eg. GitHub)

```zsh
install -m 600 /dev/null $HOME/.ssh/config
nano $HOME/.ssh/config
```

and edit matching the relevant host
```
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

Global git set up

```zsh
mkdir -p $HOME/.config/git
touch $HOME/.config/git/config
touch $HOME/.config/git/gitignore
git config --global user.name "$(id -F)"
git config --global user.email "$(osascript -e 'tell application "Contacts" to get value of email 1 of my card')"
git config --global core.editor zed
git config --global init.defaultBranch development
git config --global gpg.format ssh
git config --global user.signingKey $HOME/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true
git config --global core.excludesFile $HOME/.config/git/gitignore
```

```zsh
nano $HOME/.config/git/gitignore
```

And a suggestion for gitignore

```
.*
zig-cache/
zig-out/
/release/
/debug/
/build/
/build-*/
/docgen_tmp/
/__pycache__/
puzzle_input
```

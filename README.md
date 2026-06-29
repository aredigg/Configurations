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

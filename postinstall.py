from installer import (
    exec,
    get_input_or_default,
    DEFAULT_GITHUB_EMAIL,
    DEFAULT_GITHUB_USERNAME,
    AURS,
)


if __name__ == "__main__":
    github_username = get_input_or_default(
        f"Enter github username: [{DEFAULT_GITHUB_USERNAME}] ", DEFAULT_GITHUB_USERNAME
    )

    github_email = get_input_or_default(
        f"Enter github email: [{DEFAULT_GITHUB_EMAIL}] ", DEFAULT_GITHUB_EMAIL
    )

    exec(
        f"mkdir -p ~/.config/kitty && cp dotfiles/kitty.conf ~/.config/kitty/kitty.conf",
        f'sed "s/GITHUB_EMAIL/{github_email}/; s/GITHUB_USERNAME/{github_username}/" dotfiles/.gitconfig > ~/.gitconfig',
        f"git clone https://aur.archlinux.org/yay-bin.git $HOME/Downloads/yay-bin",
        f"cd $HOME/Downloads/yay-bin && makepkg -si",
        f"yay -S {' '.join(AURS)}",
        f"cd ~/Downloads/rogstrix-arch",
        f"rm -rf $HOME/Downloads/yay-bin",
        f'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
        f"git clone https://github.com/zsh-users/zsh-autosuggestions ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-autosuggestions",
        f"git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-syntax-highlighting",
        f'ssh-keygen -t ed25519 -C "{github_email}" && eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519',
        f"lookandfeeltool -a org.kde.breezedark.desktop",
        f"/usr/lib/plasma-changeicons Papirus-Dark",
        f"cp dotfiles/.zshrc ~/.zshrc",
        f"mkdir -p ~/.ssh && cp dotfiles/.sshconfig ~/.ssh/config",
    )

    if input("Installation complete. reboot? (y/n) [n] ") == "y":
        exec("reboot")

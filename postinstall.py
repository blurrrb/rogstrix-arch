from installer import exec, get_input_or_default, DEFAULT_GITHUB_EMAIL, AURS


def main():

    github_email = get_input_or_default(
        f"Enter github email: [{DEFAULT_GITHUB_EMAIL}] ", DEFAULT_GITHUB_EMAIL
    )
    exec(
        f"git clone https://aur.archlinux.org/yay-bin.git $HOME/Downloads/yay-bin",
        f"cd $HOME/Downloads/yay-bin && makepkg -si",
        f"yay -S {' '.join(AURS)}",
        f'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
        f"git clone https://github.com/zsh-users/zsh-autosuggestions ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-autosuggestions",
        f"git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-syntax-highlighting",
        f'ssh-keygen -t ed25519 -C "{github_email}" && eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519',
        f"cd ~ && rm -rf $HOME/Downloads/yay-bin",
        f"lookandfeeltool -a org.kde.breezedark.desktop",
        f"/usr/lib/plasma-changeicons Papirus-Dark",
    )

    if input("Installation complete. reboot? (y/n) [n] ") == "y":
        exec("reboot")


if __name__ == "__main__":
    main()

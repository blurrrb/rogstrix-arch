from os import system as shell

# DEFAULTS
DEFAULT_USERNAME = "blrb"
DEFAULT_HOSTNAME = "rogstrix"
DEFAULT_DRIVE = "/dev/sda"

DEFAULT_GITHUB_USERNAME = "blurrrb"
DEFAULT_GITHUB_EMAIL = ""

DEFAULT_MIRROR = (
    "Server = https://mirrors.piconets.webwerks.in/archlinux-mirror/$repo/os/$arch"
)

# PACKAGES
PKGS = [
    # bootloader
    "grub",
    "efibootmgr",
    # intel
    "intel-ucode",
    "mesa mesa-utils",
    # nvidia
    "nvidia-lts",
    "nvidia-settings",
    "nvidia-utils",
    "nvidia-prime",
    # display manager
    "xorg-server",
    "plasma",
    "networkmanager",
    # applications
    "firefox",
    "chromium",
    "vim",
    "dolphin",
    "kitty",
    "spectacle",
    "shotwell",
    "ark",
    "kate",
    "okular",
    "libreoffice-fresh",
    "vlc",
    "transmission-qt",
    "papirus-icon-theme",
    "adobe-source-code-pro-fonts",
    # utils
    "packagekit-qt5",
    "sudo",
    "reflector",
    "man",
    # development
    "git",
    "base-devel",
    "rust",
    "go",
    "python3",
    "python-pip",
    "nodejs-lts-gallium",
    "npm",
    "zsh",
    "docker",
    # printing
    "cups",
    "cups-pdf",
    "simple-scan",
    # virtual machine
    "libvirt",
    "iptables-nft",
    "dnsmasq",
    "dmidecode",
    "bridge-utils",
    "openbsd-netcat",
    "edk2-ovmf",
    "virt-manager",
    # extras
    "networkmanager-openconnect",
    "stoken",
]

AURS = [
    "epson-inkjet-printer-escpr",
    "visual-studio-code-bin",
    "yay-bin",
    "slack-desktop",
    "discord",
    "zoom",
    "authy",
]

# helpers


def get_input_or_default(message, default):
    inp = input(message)
    return inp if len(inp) > 0 else default


def exec_arch_chroot(user, *commands):
    payload = "\n".join(commands)
    print(payload)
    shell(f"arch-chroot /mnt su {user} bash -c '{payload}'")


def exec(*commands):
    payload = "\n".join(commands)
    print(payload)
    shell(f"bash -c '{payload}'")


def main():
    user = get_input_or_default(
        f"Enter username: [{DEFAULT_USERNAME}] ", DEFAULT_USERNAME
    )

    hostname = get_input_or_default(
        f"Enter hostname: [{DEFAULT_HOSTNAME}] ", DEFAULT_HOSTNAME
    )

    github_username = get_input_or_default(
        f"Enter github username: [{DEFAULT_GITHUB_USERNAME}] ", DEFAULT_GITHUB_USERNAME
    )

    github_email = get_input_or_default(
        f"Enter github email: [{DEFAULT_GITHUB_EMAIL}] ", DEFAULT_GITHUB_EMAIL
    )

    exec("fdisk -l")
    drive = get_input_or_default(f"Enter drive: [{DEFAULT_DRIVE}] ", DEFAULT_DRIVE)

    exec(
        f"systemctl stop reflector",
        f"echo '{DEFAULT_MIRROR}' > /etc/pacman.d/mirrorlist && cat /etc/pacman.d/mirrorlist",
        f"timedatectl set-ntp true",
        f"umount /mnt/boot",
        f"umount /mnt",
        f"parted {drive} mklabel gpt",
        f'parted {drive} mkpart "boot" fat32 1Mib 512Mib set 1 esp on',
        f'parted {drive} mkpart "root" ext4 512MiB 100%',
        f"mkfs.ext4 {drive}2",
        f"mkfs.fat -F 32 {drive}1",
        f"mount {drive}2 /mnt",
        f"mkdir /mnt/boot",
        f"mount {drive}1 /mnt/boot",
        f"pacstrap -i /mnt base linux-lts linux-lts-headers linux-firmware",
        f"genfstab -U /mnt >> /mnt/etc/fstab",
    )

    print("phase 1")

    exec_arch_chroot(
        "root",
        f"echo '{DEFAULT_MIRROR}' > /etc/pacman.d/mirrorlist && cat /etc/pacman.d/mirrorlist",
        f'pacman -S {" ".join(PKGS)}',
        f"ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime",
        f"hwclock --systohc",
        f'echo "en_US.UTF-8 UTF-8" > /etc/locale.gen',
        f"locale-gen",
        f'echo "LANG=en_US.UTF-8" > /etc/locale.conf',
        f"echo {hostname} >> /etc/hostname",
        f"mkinitcpio -P",
        f"grub-install --target=x86_64-efi --efi-directory=/boot/ --bootloader-id=GRUB && grub-mkconfig -o /boot/grub/grub.cfg",
        f'sed -i "s/^#\s*\(%wheel\s*ALL=(ALL)\s*NOPASSWD:\s*ALL\)/\\1/" /etc/sudoers',
        f"useradd -m {user}",
        f"usermod -aG wheel,libvirt,docker {user}",
        f'echo "Enter root password:" && passwd',
        f'echo "Enter {user} password:" && passwd {user}',
        f"systemctl enable NetworkManager",
        f"systemctl enable sddm",
        f"systemctl enable libvirtd && virsh net-autostart default",
        f"systemctl enable docker",
    )

    exec(
        f"mkdir -p /mnt/etc/sddm.conf.d && cp dotfiles/kde_settings.conf /mnt/etc/sddm.conf.d/kde_settings.conf",
        "echo done",
        f"sed 's/GITHUB_EMAIL/{github_email}/; s/GITHUB_USERNAME/{github_username}/' dotfiles/.gitconfig > /mnt/home/{user}/.gitconfig",
        "echo done",
        f"cp dotfiles/.zshrc /mnt/home/{user}/.zshrc",
        "echo done",
        f"mkdir -p /mnt/home/{user}/.ssh && cp dotfiles/.sshconfig /mnt/home/{user}/.ssh/config",
        "echo done",
        f"mkdir -p /mnt/home/{user}/.config/kitty && cp dotfiles/kitty.conf /mnt/home/{user}/.config/kitty/kitty.conf",
        "echo done",
    )

    exec_arch_chroot(
        user,
        f"git clone https://aur.archlinux.org/yay-bin.git $HOME/yay-bin",
        f"cd $HOME/yay-bin makepkg -si",
        f"yay -S {AURS}",
        f'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
        f"git clone https://github.com/zsh-users/zsh-autosuggestions ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-autosuggestions",
        f"git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${{ZSH_CUSTOM:-~/.oh-my-zsh/custom}}/plugins/zsh-syntax-highlighting",
        f'ssh-keygen -t ed25519 -C "{github_email}" && eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519',
    )

    if input("Installation complete. reboot? (y/n) [n] ") == "y":
        exec("umount /mnt/boot", "umount /mnt", "reboot")


if __name__ == "__main__":
    main()

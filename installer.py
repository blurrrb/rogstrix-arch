from os import system as shell

# DEFAULTS
DEFAULT_USERNAME = "blrb"
DEFAULT_HOSTNAME = "rogstrix"
DEFAULT_DRIVE = "/dev/sda"

DEFAULT_GITHUB_USERNAME = "blurrrb"
DEFAULT_GITHUB_EMAIL = ""

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
    "qemu",
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
]

# helpers


def get_input_or_default(message, default):
    inp = input(message)
    return inp if len(inp) > 0 else default


def exec_arch_chroot(user, *commands):
    payload = "\n".join(commands)
    shell(f"arch-chroot /mnt su {user} bash -c '{payload}'")


def exec(*commands):
    payload = "\n".join(commands)
    shell(f"bash -c '{payload}'")


if __name__ == "__main__":
    user = get_input_or_default(
        f"Enter username: [{DEFAULT_USERNAME}] ", DEFAULT_USERNAME
    )

    hostname = get_input_or_default(
        f"Enter hostname: [{DEFAULT_HOSTNAME}] ", DEFAULT_HOSTNAME
    )

    exec("fdisk -l")
    drive = get_input_or_default(f"Enter drive: [{DEFAULT_DRIVE}] ", DEFAULT_DRIVE)

    exec(
        f"systemctl stop reflector",
        f"cp dotfiles/mirrorlist /etc/pacman.d/mirrorlist && cat /etc/pacman.d/mirrorlist",
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

    exec_arch_chroot(
        "root",
        f"ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime",
        f"hwclock --systohc",
        f'echo "en_US.UTF-8 UTF-8" > /etc/locale.gen',
        f"locale-gen",
        f'echo "LANG=en_US.UTF-8" > /etc/locale.conf',
        f"echo {hostname} >> /etc/hostname",
        f"mkinitcpio -P",
        f'pacman -S {" ".join(PKGS)}',
        f"grub-install --target=x86_64-efi --efi-directory=/boot/ --bootloader-id=GRUB && grub-mkconfig -o /boot/grub/grub.cfg",
        f'sed -i "s/# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/%wheel ALL=(ALL:ALL) NOPASSWD: ALL/" /etc/sudoers',
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
        f"mkdir -p /mnt/etc/sddm.conf.d && cp dotfiles/kde_settings.conf /mnt/etc/sddm.conf.d/kde_settings.conf"
    )

    if input("Installation complete. reboot? (y/n) [n] ") == "y":
        exec("umount /mnt/boot", "umount /mnt", "reboot")

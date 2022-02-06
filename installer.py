from os import system as shell

# DEFAULTS
DEFAULT_USERNAME = 'blrb'
DEFAULT_HOSTNAME = 'rogstrix'
DEFAULT_DRIVE = '/dev/sda'

DEFAULT_GITHUB_USERNAME = 'blurrrb'

# PACKAGES
PKGS_BOOTLOADER = [
    'grub',
    'efibootmgr'
]

PKGS_INTEL = [
    'intel-ucode',
    'mesa mesa-utils'
]
PKGS_NVIDIA = [
    'nvidia-lts',
    'nvidia-settings',
    'nvidia-utils',
    'nvidia-prime'
]
PKGS_DISPLAY_MANAGER = [
    'xorg-server',
    'plasma',
    'networkmanager'
]
PKGS_APPS = [
    'firefox',
    'vim',
    'dolphin',
    'konsole',
    'spectacle',
    'shotwell',
    'ark',
    'kate',
    'okular',
    'libreoffice-fresh',
    'vlc',
    'transmission-qt',
    'papirus-icon-theme',
    'adobe-source-code-pro-fonts'
]
PKGS_UTILS = [
    'packagekit-qt5',
    'sudo',
    'reflector'
]
PKGS_DEVEL = [
    'git',
    'base-devel',
    'rust',
    'go',
    'python3',
    'python-pip',
    'nodejs-lts-gallium',
    'npm',
    'zsh',
    'docker'
]
PKGS_PRINTING = [
    'cups',
    'cups-pdf',
    'simple-scan'
]
PKGS_VM = [
    'libvirt',
    'iptables-nft',
    'dnsmasq',
    'dmidecode',
    'bridge-utils',
    'openbsd-netcat',
    'edk2-ovmf',
    'virsh',
    'virt-manager'
]
PKGS_EXTRA = [
    'networkmanager-openconnect',
    'stoken'
]

PKGS = PKGS_BOOTLOADER + PKGS_INTEL + PKGS_NVIDIA + PKGS_DISPLAY_MANAGER + \
    PKGS_APPS + PKGS_DEVEL + PKGS_PRINTING + PKGS_VM + PKGS_EXTRA

AURS = [
    'epson-inkjet-printer-escpr',
    'visual-studio-code-bin',
    'yay-bin',
    'slack-desktop',
    'discord',
    'zoom',
    'authy'
]

# helpers


def get_input_or_default(message, default):
    inp = input(message)
    return inp if len(inp) > 0 else default


def exec_arch_chroot(user, commands):
    payload = '\n'.join(commands)
    shell(f'arch-chroot -u {user} /mnt bash -c \'{payload}\'')


def exec(commands):
    payload = '\n'.join(commands)
    shell(f'bash -c \'{payload}\'')


def main():
    user = get_input_or_default(
        f'Enter username: [{DEFAULT_USERNAME}] ', DEFAULT_USERNAME)
    hostname = get_input_or_default(
        f'Enter hostname: [{DEFAULT_HOSTNAME}] ', DEFAULT_HOSTNAME)

    github_username = get_input_or_default(
        f'Enter github username:[{DEFAULT_GITHUB_USERNAME}] ', DEFAULT_GITHUB_USERNAME)
    
    github_email = input('Enter github email: ')

    shell('fdisk -l')
    drive = get_input_or_default(
        f'Enter drive: [{DEFAULT_DRIVE}]', DEFAULT_DRIVE)

    exec([
        f'systemctl stop reflector',
        f'reflector --save /etc/pacman.d/mirrorlist --country India --protocol https --sort rate',
        f'cat /etc/pacman.d/mirrorlist',
        f'timedatectl set-ntp true',
        f'parted {drive} mklabel gpt',
        f'parted {drive} mkpart "EFI-System-Partition" fat32 1Mib 512Mib set 1 esp on',
        f'parted {drive} mkpart "Linux-Partition" ext4 512MiB 100%',
        f'mkfs.ext4 {drive}2',
        f'mkfs.fat -F 32 {drive}1',
        f'mount {drive}2 /mnt',
        f'mkdir /mnt/boot',
        f'mount {drive}1 /mnt/boot',
        f'pacstrap -i /mnt base linux-lts linux-lts-headers linux-firmware',
        f'genfstab -U /mnt >> /mnt/etc/fstab'
    ])

    exec_arch_chroot('root', [
        f'pacman -S {" ".join(PKGS)}',
        f'ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime',
        f'hwclock --systohc',
        f'echo \'en_US.UTF-8 UTF-8\' > /etc/locale.gen',
        f'locale-gen',
        f'echo \'LANG=en_US.UTF-8\' > /etc/locale.conf',
        f'echo {hostname} >> /etc/hostname',
        f'mkinitcpio -P',
        f'grub-install --target=x86_64-efi --efi-directory=/boot/ --bootloader-id=GRUB && grub-mkconfig -o /boot/grub/grub.cfg',
        f'sed -i \'s/^#\s*\(%wheel\s*ALL=(ALL)\s*NOPASSWD:\s*ALL\)/\\1/\' /etc/sudoers',
        f'usermod -m -G wheel,libvirt,docker {user}',
        f'echo \'Enter root password:\' && passwd',
        f'echo \'Enter {user} password:\' && passwd {user}',
        f'systemctl enable NetworkManager',
        f'systemctl enable sddm',
        f'systemctl enable libvirtd',
        f'systemctl enable docker',
        f'reflector --save /etc/pacman.d/mirrorlist --country India --protocol https --sort rate'
    ])

    exec_arch_chroot(user, [
        f'git config --global user.name {github_username}',
        f'git config --global user.email {github_email}',
        f'git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin'
        f'cd /tmp/yay-bin && makepkg -si'
        f'yay -S {AURS}'
    ])

    # shell('umount /mnt/boot && umount /mnt')


if __name__ == '__main__':
    main()

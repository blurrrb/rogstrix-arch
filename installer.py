from os import system as shell

# DEFAULTS
DEFAULT_USERNAME = 'blrb'
DEFAULT_HOSTNAME = 'rogstrix'
DEFAULT_DRIVE = '/dev/sda'

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


def arch_chroot(user):
    commands = []

    def chroot_shell(cmd):
        commands.append(cmd)

    def execute():
        payload = '\n'.join(commands)
        shell(f'arch-chroot -u {user} /mnt bash -c \'{payload}\'')

    return chroot_shell, execute


def main():
    user = get_input_or_default(
        f'Enter username: [{DEFAULT_USERNAME}]', DEFAULT_USERNAME)
    hostname = get_input_or_default(
        f'Enter hostname: [{DEFAULT_HOSTNAME}]', DEFAULT_HOSTNAME)

    shell('fdisk -l')
    drive = get_input_or_default(
        f'Enter drive: [{DEFAULT_DRIVE}]', DEFAULT_DRIVE)

    shell('systemctl stop reflector')
    shell('reflector --save /etc/pacman.d/mirrorlist --country India --protocol https --sort rate && cat /etc/pacman.d/mirrorlist')

    shell('timedatectl set-ntp true')

    shell(
        f'''parted {drive} << EOF
        mklabel gpt
        mkpart "EFI System Partition" fat32 1Mib 512Mib set 1 esp on
        mkpart "Linux Partition" ext4 512MiB 100 %
        EOF
        mount {drive}2 /mnt
        mkdir /mnt/boot
        mount {drive}1 /mnt/boot''')

    shell('pacstrap -i /mnt base linux-lts linux-lts-headers linux-firmware')
    shell('genfstab -U /mnt >> /mnt/etc/fstab')

    # chroot as root
    root_chroot_shell, root_chroot_execute = arch_chroot('root')

    root_chroot_shell(f'pacman -S {PKGS}')
    root_chroot_shell('ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime')
    root_chroot_shell('hwclock --systohc')
    root_chroot_shell('echo \'en_US.UTF-8 UTF-8\' > /etc/locale.gen')
    root_chroot_shell('locale-gen')
    root_chroot_shell('echo \'LANG=en_US.UTF-8\' > /etc/locale.conf')
    root_chroot_shell(f'echo {hostname} >> /etc/hostname')
    root_chroot_shell('mkinitcpio -P')

    root_chroot_shell(
        'grub-install --target=x86_64-efi --efi-directory=/boot/ --bootloader-id=GRUB && grub-mkconfig -o /boot/grub/grub.cfg')

    root_chroot_shell(
        'sed -i \'s/^#\s*\(%wheel\s*ALL=(ALL)\s*NOPASSWD:\s*ALL\)/\1/\' /etc/sudoers')
    root_chroot_shell(f'usermod -m -G wheel,libvirt,docker {user}')

    root_chroot_shell('echo \'Enter root password:\' && passwd')
    root_chroot_shell(f'echo \'Enter {user} password:\' && passwd {user}')
    root_chroot_shell('systemctl enable NetworkManager')
    root_chroot_shell('systemctl enable sddm')
    root_chroot_shell('systemctl enable libvirtd')
    root_chroot_shell('systemctl enable docker')

    root_chroot_shell('reflector --save /etc/pacman.d/mirrorlist --country India --protocol https --sort rate')

    root_chroot_execute()

    user_chroot_shell, user_chroot_execute = arch_chroot(user)

    user_chroot_shell('git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin')
    user_chroot_shell('cd /tmp/yay-bin && makepkg -si')
    user_chroot_shell(f'yay -S {AURS}')

    user_chroot_execute()

    shell('umount /mnt/boot && umount /mnt')

    
if __name__ == '__main__':
    main()

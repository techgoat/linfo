"""Static distro databases and lookup helpers.

Desktop/server facts live in DISTRO_DATA. Embedded / IoT oriented facts live
in EMBEDDED_DISTRO_DATA. Lookups are name-normalized (case/space tolerant).
"""

from __future__ import annotations

# Curated list of popular distros for the random feature
RANDOM_DISTROS: list[tuple[str, str]] = [
    ("Ubuntu", "x86_64"),
    ("Fedora", "x86_64"),
    ("Debian", "x86_64"),
    ("Arch Linux", "x86_64"),
    ("Linux Mint", "x86_64"),
    ("Pop!_OS", "x86_64"),
    ("openSUSE Tumbleweed", "x86_64"),
    ("NixOS", "x86_64"),
    ("Kali Linux", "x86_64"),
    ("AlmaLinux", "x86_64"),
    ("Rocky Linux", "x86_64"),
    ("Parrot Security", "x86_64"),
]

# Random pool when --embedded is set and no --distro is given
RANDOM_EMBEDDED_DISTROS: list[tuple[str, str]] = [
    ("Alpine Linux", "x86_64"),
    ("OpenWrt", "aarch64"),
    ("Yocto Project", "armv7"),
    ("Buildroot", "aarch64"),
    ("BusyBox", "x86_64"),
    ("Raspberry Pi OS Lite", "aarch64"),
    ("balenaOS", "aarch64"),
]

# Static data for fastfetch-style output + download links + ASCII (inspired by neofetch)
# Keys are normalized (lowercase, no spaces/punctuation)
DISTRO_DATA: dict[str, dict[str, str]] = {
    "ubuntu": {
        "display_name": "Ubuntu",
        "ascii_logo": r"""
               _
           ---(_)
         /        \\
        |   Ubuntu |
         \\        /
           `-----'
""",
        "color": "bright_red",
        "pkg_manager": "APT / dpkg + Snap",
        "default_desktop": "GNOME (default)",
        "official_site": "https://ubuntu.com",
        "download_url": "https://ubuntu.com/download/desktop",
        "release_model": "Point releases + LTS (2y/5y+)",
    },
    "fedora": {
        "display_name": "Fedora",
        "ascii_logo": r"""
      _____
     /     \\
    /   o   \\
   (    ---   )
    \\         /
     \\_______/
""",
        "color": "bright_blue",
        "pkg_manager": "DNF / RPM + Flatpak",
        "default_desktop": "GNOME (Workstation)",
        "official_site": "https://fedoraproject.org",
        "download_url": "https://fedoraproject.org/workstation/download/",
        "release_model": "6-month rapid releases",
    },
    "debian": {
        "display_name": "Debian",
        "ascii_logo": r"""
      .-.
     /   \\
    |  o  |
     \\   /
      '-'
""",
        "color": "red",
        "pkg_manager": "APT / dpkg",
        "default_desktop": "GNOME (varies by spin)",
        "official_site": "https://www.debian.org",
        "download_url": "https://www.debian.org/distrib/",
        "release_model": "Stable ~2 years, very conservative",
    },
    "archlinux": {
        "display_name": "Arch Linux",
        "ascii_logo": r"""
     .--.
    |o_o |
    |:_/ |
   //   \ \\
  (|     | )
 /'\_   _/`\
\___)=(___/
""",
        "color": "bright_cyan",
        "pkg_manager": "Pacman + AUR helpers",
        "default_desktop": "None (user chosen)",
        "official_site": "https://archlinux.org",
        "download_url": "https://archlinux.org/download/",
        "release_model": "Rolling release",
    },
    "linuxmint": {
        "display_name": "Linux Mint",
        "ascii_logo": r"""
      .--.
     /    \\
    | Mint |
     \\    /
      '--'
""",
        "color": "bright_green",
        "pkg_manager": "APT + Flatpak + AppImage",
        "default_desktop": "Cinnamon (default)",
        "official_site": "https://linuxmint.com",
        "download_url": "https://linuxmint.com/download.php",
        "release_model": "Based on Ubuntu LTS, 5y support",
    },
    "popos": {
        "display_name": "Pop!_OS",
        "ascii_logo": r"""
   ______
  /      \\
 |  Pop!  |
  \\______/
""",
        "color": "bright_magenta",
        "pkg_manager": "APT + Flatpak + AppImage",
        "default_desktop": "COSMIC (or GNOME)",
        "official_site": "https://pop.system76.com",
        "download_url": "https://pop.system76.com/",
        "release_model": "Ubuntu-based, 2 releases/year",
    },
    "opensusetumbleweed": {
        "display_name": "openSUSE Tumbleweed",
        "ascii_logo": r"""
    ____
   /    \\
  | open |
   \\____/
""",
        "color": "bright_yellow",
        "pkg_manager": "Zypper / RPM + transactional",
        "default_desktop": "KDE Plasma or GNOME",
        "official_site": "https://www.opensuse.org",
        "download_url": "https://get.opensuse.org/",
        "release_model": "Rolling release (Tumbleweed)",
    },
    "nixos": {
        "display_name": "NixOS",
        "ascii_logo": r"""
   ___
  /   \\
 | Nix |
  \\___/
""",
        "color": "bright_blue",
        "pkg_manager": "Nix (declarative)",
        "default_desktop": "Various (user configured)",
        "official_site": "https://nixos.org",
        "download_url": "https://nixos.org/download/",
        "release_model": "Rolling + declarative generations",
    },
    "kalilinux": {
        "display_name": "Kali Linux",
        "ascii_logo": r"""
   .--.
  /    \\
 | Kali |
  \\    /
   '--'
""",
        "color": "bright_red",
        "pkg_manager": "APT + custom repos",
        "default_desktop": "Xfce (default), GNOME, etc.",
        "official_site": "https://www.kali.org",
        "download_url": "https://www.kali.org/get-kali/",
        "release_model": "Rolling (Debian-based)",
    },
    "almalinux": {
        "display_name": "AlmaLinux",
        "ascii_logo": r"""
   ____
  /    \\
 | Alma |
  \\____/
""",
        "color": "bright_green",
        "pkg_manager": "DNF / RPM",
        "default_desktop": "GNOME (varies)",
        "official_site": "https://almalinux.org",
        "download_url": "https://almalinux.org/get-almalinux/",
        "release_model": "RHEL clone, 10y support",
    },
    "rockylinux": {
        "display_name": "Rocky Linux",
        "ascii_logo": r"""
   ____
  /    \\
 |Rocky|
  \\____/
""",
        "color": "bright_green",
        "pkg_manager": "DNF / RPM",
        "default_desktop": "GNOME (varies)",
        "official_site": "https://rockylinux.org",
        "download_url": "https://rockylinux.org/download",
        "release_model": "RHEL clone, community driven",
    },
    "parrotsecurity": {
        "display_name": "Parrot Security",
        "ascii_logo": r"""
   ____
  /    \\
 |Parrot|
  \\____/
""",
        "color": "bright_blue",
        "pkg_manager": "APT (Debian + Parrot repos)",
        "default_desktop": "MATE (customized)",
        "official_site": "https://parrotsec.org",
        "download_url": "https://parrotsec.org/download/",
        "release_model": "Rolling (Debian-based)",
    },
}

# Embedded / IoT / appliance oriented facts (used with --embedded)
EMBEDDED_DISTRO_DATA: dict[str, dict[str, str]] = {
    "alpinelinux": {
        "display_name": "Alpine Linux",
        "ascii_logo": r"""
   /\\
  /  \\
 / /\ \\
/ ____ \\
\/    \/
""",
        "color": "bright_blue",
        "pkg_manager": "apk",
        "default_desktop": "None (headless typical)",
        "official_site": "https://alpinelinux.org",
        "download_url": "https://alpinelinux.org/downloads/",
        "release_model": "Stable + edge (musl, busybox userland)",
        "build_system": "Native packages (abuild); often base for containers",
        "typical_footprint": "~5–130 MB images common",
        "init_system": "OpenRC",
        "update_mechanism": "apk upgrade; A/B optional in appliances",
        "common_targets": "Containers, routers, SBCs, minimal VMs",
    },
    "alpine": {
        "display_name": "Alpine Linux",
        "ascii_logo": r"""
   /\\
  /  \\
 / /\ \\
/ ____ \\
\/    \/
""",
        "color": "bright_blue",
        "pkg_manager": "apk",
        "default_desktop": "None (headless typical)",
        "official_site": "https://alpinelinux.org",
        "download_url": "https://alpinelinux.org/downloads/",
        "release_model": "Stable + edge (musl, busybox userland)",
        "build_system": "Native packages (abuild); often base for containers",
        "typical_footprint": "~5–130 MB images common",
        "init_system": "OpenRC",
        "update_mechanism": "apk upgrade; A/B optional in appliances",
        "common_targets": "Containers, routers, SBCs, minimal VMs",
    },
    "openwrt": {
        "display_name": "OpenWrt",
        "ascii_logo": r"""
  .--.
 / OO \\
| Open |
 \\__/
""",
        "color": "bright_cyan",
        "pkg_manager": "opkg (or apk on newer branches)",
        "default_desktop": "LuCI web UI (no desktop)",
        "official_site": "https://openwrt.org",
        "download_url": "https://openwrt.org/downloads",
        "release_model": "Stable releases + snapshots",
        "build_system": "OpenWrt build system (image builder / SDK)",
        "typical_footprint": "Often <16–128 MB flash targets",
        "init_system": "procd / busybox init",
        "update_mechanism": "sysupgrade; opkg for packages",
        "common_targets": "Wi-Fi routers, gateways, APs, IoT edge",
    },
    "yoctoproject": {
        "display_name": "Yocto Project",
        "ascii_logo": r"""
  Yocto
  =====
  layers
""",
        "color": "bright_yellow",
        "pkg_manager": "rpm/deb/ipk (image-defined)",
        "default_desktop": "Image-defined (often headless)",
        "official_site": "https://www.yoctoproject.org",
        "download_url": "https://www.yoctoproject.org/software-overview/",
        "release_model": "Named releases (LTS available); layer-based",
        "build_system": "OpenEmbedded / BitBake (Yocto)",
        "typical_footprint": "Custom; from tiny to full desktop",
        "init_system": "systemd or sysvinit (recipe choice)",
        "update_mechanism": "swupdate, RAUC, OSTree, custom",
        "common_targets": "Industrial, automotive, appliances, custom BSPs",
    },
    "yocto": {
        "display_name": "Yocto Project",
        "ascii_logo": r"""
  Yocto
  =====
  layers
""",
        "color": "bright_yellow",
        "pkg_manager": "rpm/deb/ipk (image-defined)",
        "default_desktop": "Image-defined (often headless)",
        "official_site": "https://www.yoctoproject.org",
        "download_url": "https://www.yoctoproject.org/software-overview/",
        "release_model": "Named releases (LTS available); layer-based",
        "build_system": "OpenEmbedded / BitBake (Yocto)",
        "typical_footprint": "Custom; from tiny to full desktop",
        "init_system": "systemd or sysvinit (recipe choice)",
        "update_mechanism": "swupdate, RAUC, OSTree, custom",
        "common_targets": "Industrial, automotive, appliances, custom BSPs",
    },
    "buildroot": {
        "display_name": "Buildroot",
        "ascii_logo": r"""
  Build
  root
""",
        "color": "bright_green",
        "pkg_manager": "None in image (rebuild to change)",
        "default_desktop": "Optional; often none",
        "official_site": "https://buildroot.org",
        "download_url": "https://buildroot.org/downloads/",
        "release_model": "Stable releases + git master",
        "build_system": "Buildroot (kconfig + Makefile)",
        "typical_footprint": "Often multi-MB rootfs; very flexible",
        "init_system": "BusyBox init / systemd / others",
        "update_mechanism": "Full image reflash or custom",
        "common_targets": "Embedded boards, appliances, learning BSPs",
    },
    "busybox": {
        "display_name": "BusyBox",
        "ascii_logo": r"""
  Busy
  Box
""",
        "color": "bright_white",
        "pkg_manager": "N/A (multi-call binary in rootfs)",
        "default_desktop": "None",
        "official_site": "https://busybox.net",
        "download_url": "https://busybox.net/downloads/",
        "release_model": "Upstream releases; embedded in many systems",
        "build_system": "BusyBox config + host toolchain / Buildroot / Yocto",
        "typical_footprint": "Hundreds of KB for core userland",
        "init_system": "BusyBox init (common)",
        "update_mechanism": "Depends on integrating distro/image",
        "common_targets": "Minimal rootfs, recovery, IoT, initramfs",
    },
    "raspberrypioslite": {
        "display_name": "Raspberry Pi OS Lite",
        "ascii_logo": r"""
   .~~.
  / Pi \\
  \\____/
""",
        "color": "bright_red",
        "pkg_manager": "APT / dpkg",
        "default_desktop": "None (Lite)",
        "official_site": "https://www.raspberrypi.com/software/",
        "download_url": "https://www.raspberrypi.com/software/operating-systems/",
        "release_model": "Debian-based images for Pi hardware",
        "build_system": "Raspberry Pi OS images (Debian derivative)",
        "typical_footprint": "Lite image smaller than desktop; SD-card focused",
        "init_system": "systemd",
        "update_mechanism": "apt upgrade; rpi-update (careful)",
        "common_targets": "Raspberry Pi SBCs, kiosks, sensors, education",
    },
    "raspberrypios": {
        "display_name": "Raspberry Pi OS Lite",
        "ascii_logo": r"""
   .~~.
  / Pi \\
  \\____/
""",
        "color": "bright_red",
        "pkg_manager": "APT / dpkg",
        "default_desktop": "None (Lite context)",
        "official_site": "https://www.raspberrypi.com/software/",
        "download_url": "https://www.raspberrypi.com/software/operating-systems/",
        "release_model": "Debian-based images for Pi hardware",
        "build_system": "Raspberry Pi OS images (Debian derivative)",
        "typical_footprint": "Lite image smaller than desktop; SD-card focused",
        "init_system": "systemd",
        "update_mechanism": "apt upgrade; rpi-update (careful)",
        "common_targets": "Raspberry Pi SBCs, kiosks, sensors, education",
    },
    "balenaos": {
        "display_name": "balenaOS",
        "ascii_logo": r"""
  balena
  =====
""",
        "color": "bright_blue",
        "pkg_manager": "Host is minimal; apps via containers",
        "default_desktop": "None (fleet device OS)",
        "official_site": "https://www.balena.io/os/",
        "download_url": "https://www.balena.io/os/",
        "release_model": "Yocto-based host OS; rolling host updates",
        "build_system": "Yocto-based balenaOS host + Docker/balenaEngine",
        "typical_footprint": "Host + container workloads",
        "init_system": "systemd (host)",
        "update_mechanism": "Host OTA + container releases",
        "common_targets": "IoT fleets, digital signage, industrial edge",
    },
}


def normalize_distro_name(name: str) -> str:
    """Normalize distro name for lookup in static databases."""
    return (
        name.lower()
        .replace(" ", "")
        .replace("!", "")
        .replace("_", "")
        .replace("-", "")
        .replace(".", "")
    )


def get_distro_data(distro_name: str, *, embedded: bool = False) -> dict[str, str] | None:
    """Return static data for a distro (case/space tolerant).

    When ``embedded`` is True, prefer ``EMBEDDED_DISTRO_DATA``. If the name is
    not there, fall back to desktop ``DISTRO_DATA`` so known distros still
    render something useful.
    """
    key = normalize_distro_name(distro_name)
    if embedded:
        data = EMBEDDED_DISTRO_DATA.get(key)
        if data is not None:
            return data
        return DISTRO_DATA.get(key)
    return DISTRO_DATA.get(key)

#!/usr/bin/env python3
"""
Programmatic usage example for linfo components.

Note: The primary interface is the CLI (`linfo` command).
This shows how the core dataclasses can be used directly (e.g. in other tools or tests).
"""

from linfo.main import Distro, DistroRenderer, get_distro_data

def main():
    print("=== Using Distro dataclass ===")
    d = Distro.from_name("Ubuntu")
    print(f"Distro: {d.name} ({d.arch})")
    print(f"Download: {d.data.get('download_url') if d.data else 'N/A'}")
    print(f"Package manager: {d.data.get('pkg_manager') if d.data else 'N/A'}")

    print("\n=== Rendering fetch style (simulates --style fetch) ===")
    renderer = DistroRenderer(style="fetch", brief=False)
    # In real use the 2nd arg would be the LLM response; here it's a placeholder
    renderer.render(d, "This would be the detailed LLM narrative for Ubuntu...")

    print("\n=== Brief mode for unknown distro (simulates --brief on Parrot Security) ===")
    d2 = Distro(name="Parrot Security", arch="x86_64", data=get_distro_data("Parrot Security"))
    renderer_brief = DistroRenderer(brief=True)
    renderer_brief.render(d2, "Concise LLM summary for Parrot Security (security-focused Debian derivative)...")

    print("\n=== Direct data lookup ===")
    data = get_distro_data("Arch Linux")
    if data:
        print(f"Arch official site: {data['official_site']}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Programmatic usage example for linfo components.

Note: The primary interface is the CLI (`linfo` command).
This shows how the core dataclasses can be used directly (e.g. in other tools or tests).
"""

from linfo import Distro, DistroRenderer, get_distro_data
from linfo.output import build_result_payload


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

    print("\n=== Brief mode for unknown distro (simulates --brief on MysteryOS) ===")
    d2 = Distro(name="MysteryOS", arch="x86_64", data=None)
    renderer_brief = DistroRenderer(brief=True)
    renderer_brief.render(d2, "Concise LLM summary for MysteryOS...")

    print("\n=== Embedded profile ===")
    emb = Distro.from_name("OpenWrt", embedded=True)
    print(f"Build system: {emb.data.get('build_system') if emb.data else 'N/A'}")
    DistroRenderer(brief=True, embedded=True).render(emb, None)

    print("\n=== JSON payload shape (no network) ===")
    payload = build_result_payload(
        d, response="...", style="fetch", brief=True, embedded=False
    )
    print(f"Keys: {sorted(payload.keys())}")

    print("\n=== Direct data lookup ===")
    data = get_distro_data("Arch Linux")
    if data:
        print(f"Arch official site: {data['official_site']}")


if __name__ == "__main__":
    main()

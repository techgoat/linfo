# Usage & Examples

See the main `README.md` (project root) for quick start.

## Common Patterns

```bash
# Random (fetch style by default)
linfo

# Brief for any distro (works even if not in built-in DB)
linfo --distro "Parrot Security" --brief

# Explicit style + level
linfo --distro Fedora --style markdown --level intermediate --topics "package management,security"

# Embedded / IoT profile
linfo --distro OpenWrt --embedded --brief
linfo --embedded   # random from embedded pool

# JSON for scripts
linfo --distro Ubuntu --brief --json
linfo --distro Alpine --embedded --json | jq '.static_data'

# Verbose (shows internal logs on console; always written to logs/)
linfo -v --distro Arch
```

See `examples/` for more (shell scripts, etc.).

## Programmatic Use (Advanced)

You can import parts of the library (though the primary interface is the CLI):

```python
from linfo import Distro, DistroRenderer, get_distro_data
# or: from linfo.main import Distro, DistroRenderer, get_distro_data

d = Distro.from_name("Ubuntu")
print(d.data["download_url"])

renderer = DistroRenderer(style="fetch", brief=True)
renderer.render(d, "optional llm blurb")

emb = Distro.from_name("OpenWrt", embedded=True)
print(emb.data.get("build_system"))
```

Full details in the [API Reference](api.md).

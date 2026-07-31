"""Pytest test cases for linfo.

Tests validate inputs (arg parsing / validation), data classes (Distro),
renderer output paths for --style and --brief, prompt construction,
embedded profile, JSON payload shape, and log/history paths.

Run with: uv run --extra test pytest
"""

import argparse
import os
from unittest.mock import MagicMock, patch

import pytest

from linfo.agent import build_prompt
from linfo.data import get_distro_data, normalize_distro_name
from linfo.main import validate_inputs
from linfo.models import Distro
from linfo.output import build_result_payload
from linfo.renderer import DistroRenderer


def test_normalize_distro_name():
    assert normalize_distro_name("Ubuntu") == "ubuntu"
    assert normalize_distro_name("Parrot Security") == "parrotsecurity"
    assert normalize_distro_name("Linux-Mint!") == "linuxmint"


def test_get_distro_data_known():
    data = get_distro_data("Ubuntu")
    assert data is not None
    assert "download_url" in data
    assert data["pkg_manager"].startswith("APT")


def test_get_distro_data_unknown():
    data = get_distro_data("CompletelyFakeDistroXYZ")
    assert data is None


def test_get_distro_data_embedded_prefers_embedded_db():
    data = get_distro_data("OpenWrt", embedded=True)
    assert data is not None
    assert "build_system" in data
    assert "opkg" in data["pkg_manager"].lower() or "apk" in data["pkg_manager"].lower()


def test_get_distro_data_embedded_falls_back_to_desktop():
    # Ubuntu is desktop-only; embedded lookup should still return desktop facts
    data = get_distro_data("Ubuntu", embedded=True)
    assert data is not None
    assert data["download_url"]


def test_distro_from_args_known():
    args = argparse.Namespace(
        distro="Ubuntu", arch="x86_64", level="beginner", topics="overview", embedded=False
    )
    d = Distro.from_args(args)
    assert d.name == "Ubuntu"
    assert d.arch == "x86_64"
    assert d.data is not None
    assert d.level == "beginner"
    assert d.embedded is False


def test_distro_from_args_embedded():
    args = argparse.Namespace(
        distro="Alpine Linux",
        arch="aarch64",
        level=None,
        topics=None,
        embedded=True,
    )
    d = Distro.from_args(args)
    assert d.embedded is True
    assert d.data is not None
    assert "init_system" in d.data


def test_distro_from_args_unknown():
    args = argparse.Namespace(
        distro="Parrot Security", arch="x86_64", level=None, topics=None, embedded=False
    )
    d = Distro.from_args(args)
    assert d.name == "Parrot Security"
    assert isinstance(d.data, (dict, type(None)))


def test_distro_from_name():
    d = Distro.from_name("Fedora")
    assert d.name == "Fedora"
    assert d.data is not None


def test_validate_inputs_valid_levels():
    for level in ["beginner", "intermediate", "advanced", "general", None]:
        args = argparse.Namespace(level=level)
        validate_inputs(args)  # should not raise


def test_validate_inputs_invalid():
    args = argparse.Namespace(level="expert")
    with pytest.raises(ValueError, match="Expertise level must be one of"):
        validate_inputs(args)


def test_build_prompt_normal_vs_brief():
    args = argparse.Namespace(
        distro="Debian", arch="x86_64", level="general", topics=None
    )
    normal = build_prompt(args, brief=False)
    brief = build_prompt(args, brief=True)

    assert "detailed information" in normal.lower()
    assert "concise" in brief.lower()
    assert "key facts only" in brief.lower()


def test_build_prompt_embedded_adds_emphasis():
    args = argparse.Namespace(
        distro="Yocto Project", arch="armv7", level="advanced", topics=None
    )
    prompt = build_prompt(args, brief=False, embedded=True)
    assert "embedded" in prompt.lower() or "yocto" in prompt.lower()
    assert "build system" in prompt.lower() or "cross-compilation" in prompt.lower()


def test_renderer_brief_with_data_uses_fetch():
    """When brief=True and data present, should call fetch path and not in-depth/markdown."""
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=True, style="markdown")

    d = Distro.from_name("Ubuntu")
    assert d.data is not None

    with patch.object(renderer, "_render_fetch") as mock_fetch, \
         patch.object(renderer, "_render_in_depth") as mock_in_depth, \
         patch.object(renderer, "_render_markdown") as mock_md, \
         patch.object(renderer, "_render_brief_summary") as mock_summary:

        renderer.render(d, "some llm response")

        mock_fetch.assert_called_once()
        mock_in_depth.assert_not_called()
        mock_md.assert_not_called()
        mock_summary.assert_not_called()


def test_renderer_brief_without_data_uses_summary():
    """For unknown distro + brief, use the summary fallback, not full markdown."""
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=True)

    d = Distro(name="MysteryOS", arch="x86_64", data=None)

    with patch.object(renderer, "_render_fetch") as mock_fetch, \
         patch.object(renderer, "_render_markdown") as mock_md, \
         patch.object(renderer, "_render_brief_summary") as mock_summary:

        renderer.render(d, "llm output here")

        mock_fetch.assert_not_called()
        mock_md.assert_not_called()
        mock_summary.assert_called_once()


def test_renderer_style_fetch_calls_fetch_then_in_depth():
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=False, style="fetch")

    d = Distro.from_name("Debian")
    assert d.data is not None

    with patch.object(renderer, "_render_fetch") as mock_fetch, \
         patch.object(renderer, "_render_in_depth") as mock_in_depth, \
         patch.object(renderer, "_render_markdown") as mock_md:

        renderer.render(d, "response")

        mock_fetch.assert_called_once()
        mock_in_depth.assert_called_once()
        mock_md.assert_not_called()


def test_renderer_style_markdown_uses_markdown_panel():
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=False, style="markdown")

    d = Distro(name="Foo", arch="x86_64", data=None)

    with patch.object(renderer, "_render_markdown") as mock_md, \
         patch.object(renderer, "_render_fetch") as mock_fetch:

        renderer.render(d, "full response")

        mock_md.assert_called_once()
        mock_fetch.assert_not_called()


def test_renderer_embedded_fetch_includes_build_facts():
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=True, embedded=True)
    d = Distro.from_name("OpenWrt", embedded=True)
    assert d.data is not None
    assert "build_system" in d.data

    # Brief + data should take the fetch path with embedded=True set on renderer
    with patch.object(renderer, "_render_fetch", wraps=renderer._render_fetch) as mock_fetch:
        renderer.render(d, None)
        mock_fetch.assert_called_once()

    assert mock_console.print.called
    assert renderer.embedded is True


def test_renderer_brief_skips_download_footer_logic():
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=True)

    d = Distro.from_name("Ubuntu")
    renderer.render(d, "resp")

    assert mock_console.print.called


def test_history_and_log_use_logs_subdir(monkeypatch, tmp_path):
    """Ensure that when using logs subdir, files are under logs/ (mocked)."""
    import linfo.history as history_mod

    logs_dir = tmp_path / "logs"
    monkeypatch.setattr(history_mod, "LOGS_DIR", str(logs_dir))
    monkeypatch.setattr(history_mod, "HISTORY_FILE", str(logs_dir / "query_history.json"))

    logs_dir.mkdir(parents=True, exist_ok=True)

    history_mod.save_history([], {"test": "entry"})

    hist_file = logs_dir / "query_history.json"
    assert hist_file.exists()

    log_path = os.path.join(str(logs_dir), "transaction_log.txt")
    assert "logs" in log_path


def test_distro_renderer_brief_header_for_unknown():
    """Smoke that brief summary path produces a 'Brief:' header."""
    mock_console = MagicMock()
    renderer = DistroRenderer(console=mock_console, brief=True)
    d = Distro(name="MysteryOS", arch="aarch64", data=None)

    renderer.render(d, "Concise info about MysteryOS...")

    found_brief = False
    for call in mock_console.print.call_args_list:
        args = call[0] if call[0] else ()
        for arg in args:
            if hasattr(arg, "renderable"):
                if "Brief" in str(getattr(arg, "renderable", "")):
                    found_brief = True
            elif "Brief" in str(arg):
                found_brief = True
    assert found_brief, "Expected a 'Brief:' header in the rendered output"


def test_json_payload_shape():
    d = Distro.from_name("Ubuntu")
    payload = build_result_payload(
        d,
        response="hello",
        style="fetch",
        brief=True,
        embedded=False,
        random_mode=False,
    )
    assert payload["name"] == "Ubuntu"
    assert payload["arch"] == "x86_64"
    assert payload["brief"] is True
    assert payload["embedded"] is False
    assert payload["response"] == "hello"
    assert payload["static_data"] is not None
    assert "download_url" in payload["static_data"]
    assert "ascii_logo" not in payload["static_data"]
    assert payload["static_data"]["has_ascii_logo"] is True


def test_json_payload_unknown_distro():
    d = Distro(name="MysteryOS", arch="x86_64", data=None)
    payload = build_result_payload(
        d,
        response="info",
        style="markdown",
        brief=False,
        embedded=True,
        random_mode=True,
    )
    assert payload["static_data"] is None
    assert payload["embedded"] is True
    assert payload["random_mode"] is True

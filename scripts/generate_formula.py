#!/usr/bin/env python3
"""Generate the millyagent Homebrew formula from published release metadata.

The input may be a local ``package-metadata.json`` file or an absolute HTTPS
URL.  The script intentionally only writes the formula requested by the
caller; it does not publish a release, create a GitHub release, or infer
checksums from an asset.  Run it only after the release assets and metadata
are public.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

_MAX_METADATA_BYTES = 1024 * 1024
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[.-][0-9A-Za-z.-]+)?$")
_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
_ARCHITECTURES = ("arm64", "x64")


class MetadataError(ValueError):
    """The metadata cannot safely describe a Homebrew binary release."""


def _read_metadata(source: str) -> Mapping[str, Any]:
    """Read a metadata object from a local path or an HTTPS URL."""

    if source.lower().startswith(("http://", "https://")):
        parsed = urlsplit(source)
        if (
            parsed.scheme.lower() != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise MetadataError(
                "metadata URL must be an absolute HTTPS URL without credentials "
                "or query"
            )
        request = Request(source, headers={"User-Agent": "millyagent-homebrew-tap"})
        with urlopen(request, timeout=30) as response:  # noqa: S310 - HTTPS checked above
            raw = response.read(_MAX_METADATA_BYTES + 1)
        if len(raw) > _MAX_METADATA_BYTES:
            raise MetadataError("metadata document is larger than 1 MiB")
    else:
        path = Path(source).expanduser()
        if not path.is_file():
            raise MetadataError(f"metadata file does not exist: {path}")
        if path.stat().st_size > _MAX_METADATA_BYTES:
            raise MetadataError("metadata document is larger than 1 MiB")
        raw = path.read_bytes()

    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MetadataError("metadata must be valid UTF-8 JSON") from exc
    if not isinstance(value, Mapping):
        raise MetadataError("metadata root must be a JSON object")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MetadataError(f"{label} must be a non-empty string")
    return value


def _version(metadata: Mapping[str, Any]) -> str:
    version = _string(metadata.get("version"), "metadata version")
    if not _VERSION_RE.fullmatch(version):
        raise MetadataError(
            "metadata version is not a supported release version: "
            f"{version!r}"
        )
    return version


def _asset(
    homebrew: Mapping[str, Any], architecture: str
) -> dict[str, str]:
    value = homebrew.get(architecture)
    if not isinstance(value, Mapping):
        raise MetadataError(f"homebrew.{architecture} must be an object")

    url = _string(value.get("url"), f"homebrew.{architecture}.url")
    parsed = urlsplit(url)
    if (
        parsed.scheme.lower() != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise MetadataError(
            f"homebrew.{architecture}.url must be an absolute HTTPS URL "
            "without credentials, query, or fragment"
        )
    filename = parsed.path.rsplit("/", 1)[-1]
    if not _FILENAME_RE.fullmatch(filename):
        raise MetadataError(
            f"homebrew.{architecture}.url must end in a safe asset filename"
        )

    declared_filename = value.get("file")
    if declared_filename is not None:
        declared_filename = _string(
            declared_filename, f"homebrew.{architecture}.file"
        )
        if declared_filename != filename:
            raise MetadataError(
                f"homebrew.{architecture}.file does not match the URL filename"
            )

    digest = _string(value.get("sha256"), f"homebrew.{architecture}.sha256")
    if not _SHA256_RE.fullmatch(digest):
        raise MetadataError(
            f"homebrew.{architecture}.sha256 must be exactly 64 hexadecimal characters"
        )

    return {"url": url, "sha256": digest.lower(), "file": filename}


def _validated_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    if metadata.get("name") != "millyagent":
        raise MetadataError("metadata name must be 'millyagent'")
    version = _version(metadata)
    homebrew = metadata.get("homebrew")
    if not isinstance(homebrew, Mapping):
        raise MetadataError("metadata homebrew value must be an object")
    if homebrew.get("version") != version:
        raise MetadataError("homebrew.version must match metadata.version")

    assets = {
        architecture: _asset(homebrew, architecture)
        for architecture in _ARCHITECTURES
    }
    return {"version": version, "assets": assets}


def _ruby_string(value: str) -> str:
    """Return a deterministic double-quoted Ruby string literal."""

    return json.dumps(value, ensure_ascii=False)


def render_formula(metadata: Mapping[str, Any]) -> str:
    """Render a deterministic formula from already validated metadata."""

    validated = _validated_metadata(metadata)
    version = validated["version"]
    arm64 = validated["assets"]["arm64"]
    x64 = validated["assets"]["x64"]

    header = (
        "# Generated by scripts/generate_formula.py from published "
        "package metadata.\n"
        "# Do not edit manually; regenerate after a release asset or checksum "
        "changes.\n"
    )
    environment_line = (
        '    environment_variables MILLYAGENT_HOME: "#{Dir.home}/.millyagent", '
        'MILLYAGENT_SCOPE: "user"\n'
    )
    return header + f'''class Millyagent < Formula
  desc "millychat local agent for MCP tools"
  homepage "https://millychat.com"
  license "Apache-2.0"
  version {_ruby_string(version)}

  on_arm do
    url {_ruby_string(arm64["url"])}, using: :nounzip
    sha256 {_ruby_string(arm64["sha256"])}
  end

  on_intel do
    url {_ruby_string(x64["url"])}, using: :nounzip
    sha256 {_ruby_string(x64["sha256"])}
  end

  def install
    if Hardware::CPU.arm?
      bin.install {_ruby_string(arm64["file"])} => "millyagent"
    else
      bin.install {_ruby_string(x64["file"])} => "millyagent"
    end
  end

  service do
    run [opt_bin/"millyagent", "serve"]
{environment_line}    keep_alive true
    run_at_load true
  end

  def caveats
    <<~EOS
      millyagent is an unsigned binary distributed from the
      millychat-ai/homebrew-millyagent tap. This is a third-party tap, not
      Homebrew core or cask.

      Complete first-run setup:
        millyagent setup

      Start the per-user service explicitly:
        brew services start millyagent

      This formula never starts a service automatically. The standalone HTTPS
      installer accepts --no-autostart to skip service registration and
      immediate start; --no-autostart is an installer option, not a
      millyagent setup option.
    EOS
  end
end
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "metadata",
        help="local package-metadata.json path or absolute HTTPS metadata URL",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("Formula/millyagent.rb"),
        help="formula output path (default: Formula/millyagent.rb)",
    )
    args = parser.parse_args(argv)

    try:
        metadata = _read_metadata(args.metadata)
        formula = render_formula(metadata)
        output = args.output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(formula, encoding="utf-8", newline="\n")
    except (MetadataError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

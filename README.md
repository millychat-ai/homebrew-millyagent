# homebrew-millyagent

Homebrew tap for [millyagent](https://millychat.com), the millychat local
agent. This repository is the standalone tap `millychat-ai/homebrew-millyagent`;
it is not Homebrew core or cask.

## Release status

The tap is bootstrapped before the public v0.22.3 release. The macOS arm64
and x64 assets, their SHA-256 digests, and the versioned
`package-metadata.json` are not public yet, so `Formula/millyagent.rb` is
intentionally **not present**. `Formula/.gitkeep` preserves the safe formula
directory without publishing a formula with guessed URLs or checksums.

After the release publishes the metadata and both macOS assets, generate the
formula from the release-owned metadata. Do not hand-edit URLs or SHA-256
digests:

```sh
# Local metadata handoff:
python3 scripts/generate_formula.py \
  /path/to/package-metadata.json \
  --output Formula/millyagent.rb

# Or read the public versioned metadata URL:
python3 scripts/generate_formula.py \
  https://millychat.com/downloads/millyagent/0.22.3/package-metadata.json \
  --output Formula/millyagent.rb
```

The generator accepts only a local JSON file or an absolute HTTPS URL. It
requires the metadata to identify `millyagent`, checks that the top-level and
Homebrew versions agree, and validates both `homebrew.arm64` and
`homebrew.x64` URLs and 64-character hexadecimal SHA-256 values. It derives
the downloaded filename from each URL and emits the same formula for the same
metadata every time.

Before committing a generated formula, inspect it and run the checks available
on a macOS machine with Homebrew:

```sh
ruby -c Formula/millyagent.rb
brew style Formula/millyagent.rb
brew audit --new-formula Formula/millyagent.rb
```

The repository workflow is path-gated and remains skipped while the formula is
absent. Homebrew style and audit are therefore a post-release macOS gate, not a
claim that this bootstrap commit has a publishable formula.

## Install after a release

The official tap formula command is:

```sh
brew install millychat-ai/millyagent/millyagent && millyagent setup && brew services start millyagent
```

`brew install` does not run setup or start a service as a side effect. The
explicit `millyagent setup` step selects and snapshots the user's configured
sources. The explicit `brew services start millyagent` step starts the
per-user service. To install and complete setup without starting the service,
stop after the second command:

```sh
brew install millychat-ai/millyagent/millyagent && millyagent setup
```

The formula's service runs `millyagent serve` with:

```text
MILLYAGENT_HOME=#{Dir.home}/.millyagent
MILLYAGENT_SCOPE=user
```

It requests keep-alive and run-at-load behavior, but the tap does not
implicitly start it. `post_install` is deliberately not used for setup or
service registration.

The standalone HTTPS installer (not Homebrew) accepts `--no-autostart`; that
flag skips service registration and immediate start. It is an installer flag,
not a `millyagent setup` option. The Homebrew flow above has no automatic-start
flag because it never starts a service until `brew services start` is run.

## Trust and packaging scope

The formula installs an **unsigned binary** from the public millychat release
assets. This tap is maintained under the `millychat-ai` organization and is a
third-party tap, not an official Homebrew core/cask submission. Users should
review release metadata and the generated formula before installation.

This repository only prepares the tap contract. It does not create or tag the
millyagent release, publish release assets, or submit anything to Homebrew
core/cask.

# Generated from published package metadata by scripts/generate_formula.py.
# Current Homebrew Formula DSL keeps stable URL declarations at formula scope.
# Do not edit URLs or checksums manually; regenerate after release metadata changes.
class Millyagent < Formula
  desc "Local agent for millychat MCP tools"
  homepage "https://millychat.com"
  version "0.22.5"
  license "Apache-2.0"
  if OS.mac? && Hardware::CPU.arm?
    url "https://millychat.com/downloads/millyagent/0.22.5/millyagent-0.22.5-macos-arm64", using: :nounzip
    sha256 "a8dbe87ea0d1b3077f1731cbd8f4ffd9502d061beaa64d3ef9b75c03df253d64"
  elsif OS.mac? && Hardware::CPU.intel?
    url "https://millychat.com/downloads/millyagent/0.22.5/millyagent-0.22.5-macos-x64", using: :nounzip
    sha256 "f8ae64b2cf6209ef235d1ceb58697c0d5d2d88ada015a00a6b8c353afb587cca"
  end

  def install
    if Hardware::CPU.arm?
      bin.install "millyagent-0.22.5-macos-arm64" => "millyagent"
    else
      bin.install "millyagent-0.22.5-macos-x64" => "millyagent"
    end
  end

  service do
    run [opt_bin/"millyagent", "serve"]
    environment_variables MILLYAGENT_HOME: "#{Dir.home}/.millyagent", MILLYAGENT_SCOPE: "user"
    keep_alive true
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

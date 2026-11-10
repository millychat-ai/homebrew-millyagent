# Generated from published package metadata by scripts/generate_formula.py.
# Current Homebrew Formula DSL keeps stable URL declarations at formula scope.
# Do not edit URLs or checksums manually; regenerate after release metadata changes.
class Millyagent < Formula
  desc "Local agent for millychat MCP tools"
  homepage "https://millychat.com"
  version "0.22.4"
  license "Apache-2.0"
  if OS.mac? && Hardware::CPU.arm?
    url "https://millychat.com/downloads/millyagent/0.22.4/millyagent-0.22.4-macos-arm64", using: :nounzip
    sha256 "436a5cc543de88203e03098c17dc91572e40bef7c25337812b24266655574256"
  elsif OS.mac? && Hardware::CPU.intel?
    url "https://millychat.com/downloads/millyagent/0.22.4/millyagent-0.22.4-macos-x64", using: :nounzip
    sha256 "39001247c2b032fd1e95814a579a841a60602cbc96a8f1521b4cf1bc005b10ad"
  end

  def install
    if Hardware::CPU.arm?
      bin.install "millyagent-0.22.4-macos-arm64" => "millyagent"
    else
      bin.install "millyagent-0.22.4-macos-x64" => "millyagent"
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

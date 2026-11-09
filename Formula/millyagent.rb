# Generated from published package metadata by scripts/generate_formula.py.
# Current Homebrew Formula DSL keeps stable URL declarations at formula scope.
# Do not edit URLs or checksums manually; regenerate after release metadata changes.
class Millyagent < Formula
  desc "Local agent for millychat MCP tools"
  homepage "https://millychat.com"
  version "0.22.3"
  license "Apache-2.0"
  if OS.mac? && Hardware::CPU.arm?
    url "https://millychat.com/downloads/millyagent/0.22.3/millyagent-0.22.3-macos-arm64", using: :nounzip
    sha256 "a7167359fb20fdab5999efedd0f0a7f8337e14c09002da1f002e84022e8978b0"
  elsif OS.mac? && Hardware::CPU.intel?
    url "https://millychat.com/downloads/millyagent/0.22.3/millyagent-0.22.3-macos-x64", using: :nounzip
    sha256 "6ef151bdeb8c26b64896bbd8f4655da8de12a9344c9254c0d5826c627f82d42c"
  end

  def install
    if Hardware::CPU.arm?
      bin.install "millyagent-0.22.3-macos-arm64" => "millyagent"
    else
      bin.install "millyagent-0.22.3-macos-x64" => "millyagent"
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

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECONCILER = ROOT / ".github" / "scripts" / "reconcile-release.sh"


class ReconcileReleaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

        self.root = Path(self.temporary_directory.name)
        self.repository = self.root / "repository"
        self.remote = self.root / "remote.git"
        self.bin_directory = self.root / "bin"
        self.release_state = self.root / "release.json"
        self.release_count = self.root / "release-count"

        (self.repository / ".github" / "scripts").mkdir(parents=True)
        (self.repository / "filabridge").mkdir()
        self.bin_directory.mkdir()

        shutil.copy2(
            RECONCILER,
            self.repository / ".github" / "scripts" / RECONCILER.name,
        )
        (self.repository / "filabridge" / "config.yaml").write_text(
            'name: FilaBridge\nversion: "1.3.0"\n', encoding="utf-8"
        )
        (self.repository / "README.md").write_text("# Test\n", encoding="utf-8")

        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "tag.gpgsign", "false")
        self.git("add", ".")
        self.git("commit", "-m", "Create App")
        self.version_commit = self.git("rev-parse", "HEAD").stdout.strip()

        self.run_command("git", "init", "--bare", str(self.remote), cwd=self.root)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "--set-upstream", "origin", "main")

        fake_gh = self.bin_directory / "gh"
        fake_gh.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -Eeuo pipefail

                case "${1:-} ${2:-}" in
                  "release view")
                    if [[ ! -f "${FAKE_RELEASE_STATE}" ]]; then
                      exit 1
                    fi
                    cat "${FAKE_RELEASE_STATE}"
                    ;;
                  "release create")
                    count=0
                    if [[ -f "${FAKE_RELEASE_COUNT}" ]]; then
                      count="$(cat "${FAKE_RELEASE_COUNT}")"
                    fi
                    printf '%s\n' "$((count + 1))" >"${FAKE_RELEASE_COUNT}"
                    printf '%s\n' '{"isDraft":false,"isPrerelease":false,"tagName":"v1.3.0","url":"https://example.invalid/release"}' >"${FAKE_RELEASE_STATE}"
                    ;;
                  "api repos/sargonas/filabridge/releases/tags/v1.3.0")
                    printf '%s\n' 'https://github.com/sargonas/filabridge/releases/tag/v1.3.0'
                    ;;
                  *)
                    printf 'Unexpected gh invocation: %s\n' "$*" >&2
                    exit 2
                    ;;
                esac
                """
            ),
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)

        self.environment = os.environ.copy()
        self.environment.update(
            {
                "FAKE_RELEASE_COUNT": str(self.release_count),
                "FAKE_RELEASE_STATE": str(self.release_state),
                "GITHUB_REPOSITORY": "example/ha-filabridge",
                "PATH": f"{self.bin_directory}:{self.environment['PATH']}",
            }
        )

    def run_command(
        self,
        *command: str,
        cwd: Path | None = None,
        check: bool = True,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=cwd or self.repository,
            check=check,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return self.run_command("git", *arguments)

    def reconcile(self, version: str = "1.3.0") -> subprocess.CompletedProcess[str]:
        return self.run_command(
            "bash",
            ".github/scripts/reconcile-release.sh",
            version,
            check=False,
            environment=self.environment,
        )

    def test_creates_annotated_tag_and_release_once(self) -> None:
        first = self.reconcile()
        self.assertEqual(first.returncode, 0, first.stdout)
        self.assertEqual(self.git("cat-file", "-t", "v1.3.0").stdout.strip(), "tag")
        self.assertEqual(
            self.git("rev-list", "-n", "1", "v1.3.0").stdout.strip(),
            self.version_commit,
        )
        self.assertEqual(self.release_count.read_text(encoding="utf-8").strip(), "1")

        second = self.reconcile()
        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertIn("already exists", second.stdout)
        self.assertEqual(self.release_count.read_text(encoding="utf-8").strip(), "1")

    def test_recreates_a_missing_release_without_moving_the_tag(self) -> None:
        first = self.reconcile()
        self.assertEqual(first.returncode, 0, first.stdout)
        original_tag = self.git("rev-parse", "v1.3.0^{tag}").stdout.strip()

        self.release_state.unlink()
        second = self.reconcile()

        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertEqual(self.release_count.read_text(encoding="utf-8").strip(), "2")
        self.assertEqual(
            self.git("rev-parse", "v1.3.0^{tag}").stdout.strip(), original_tag
        )

    def test_refuses_to_move_a_tag_on_the_wrong_commit(self) -> None:
        (self.repository / "README.md").write_text("# Changed\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "Change documentation")
        wrong_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("tag", "-a", "v1.3.0", wrong_commit, "-m", "Wrong tag")
        self.git("push", "origin", "refs/tags/v1.3.0")

        result = self.reconcile()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to move it", result.stdout)
        self.assertFalse(self.release_state.exists())

    def test_refuses_a_lightweight_tag(self) -> None:
        self.git("tag", "v1.3.0", self.version_commit)
        self.git("push", "origin", "refs/tags/v1.3.0")

        result = self.reconcile()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an annotated tag", result.stdout)
        self.assertFalse(self.release_state.exists())

    def test_rejects_a_prerelease_version(self) -> None:
        result = self.reconcile("1.3.0-rc1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid stable FilaBridge version", result.stdout)


if __name__ == "__main__":
    unittest.main()

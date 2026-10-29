"""Check cross-platform dispatch without executing foreign-platform binaries."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PlatformRuntimeTests(unittest.TestCase):
    def probe(self, system, machine):
        with tempfile.TemporaryDirectory() as tmp:
            uname = Path(tmp) / 'uname'
            uname.write_text(f'#!/bin/sh\ncase "$1" in -s) echo {system};; -m) echo {machine};; esac\n')
            uname.chmod(0o755)
            env = dict(os.environ, PATH=tmp + os.pathsep + os.environ['PATH'])
            return subprocess.run(['bash', '-c', 'source "$1" && printf "%s\\n" "$PPTAGENT_PLATFORM" "$PPTAGENT_PYTHON" "$PPTAGENT_NODE_MODULES" "$PLAYWRIGHT_BROWSERS_PATH"', 'test', str(ROOT / 'scripts/runtime-env.sh')], env=env, text=True, capture_output=True)

    def test_native_dependencies_never_share_paths(self):
        paths = []
        for system, arch, expected in [('Linux', 'x86_64', 'linux-x86_64'), ('Linux', 'aarch64', 'linux-arm64'), ('Darwin', 'arm64', 'macos-arm64')]:
            result = self.probe(system, arch)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(lines[0], expected)
            for path in lines[1:]:
                self.assertTrue(path.startswith(str(ROOT / '.runtime' / expected) + '/'))
            paths.extend(lines[1:])
        self.assertEqual(len(paths), len(set(paths)))

    def test_unsupported_platform_is_rejected(self):
        self.assertNotEqual(self.probe('FreeBSD', 'x86_64').returncode, 0)


if __name__ == '__main__':
    unittest.main()

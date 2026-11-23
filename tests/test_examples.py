"""@summary Verify authored project closure and portable package installation."""

import argparse
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"LuauExample", "PropApiExample", "TOMLExample", "TypeScriptExample", "BaseApiExample"}


def contained(base, relative):
    """@summary Resolve a project-relative regular file without escaping its owner.

    @param base Owning project directory.
    @param relative Declared source path.
    @return Existing contained regular file.
    """
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe path: {relative}")
    resolved = (base / path).resolve()
    resolved.relative_to(base.resolve())
    if not resolved.is_file():
        raise ValueError(f"Missing source: {relative}")
    return resolved


class ExamplesTest(unittest.TestCase):
    """@summary Check semantic authoring inputs without compiling or running mods."""

    def test_projects_and_inputs(self):
        """@summary Validate manifests, owner-local modules and scalar alias references."""
        projects = ROOT / "examples"
        self.assertEqual({p.name for p in projects.iterdir()}, EXPECTED)
        ids = set()
        for project in projects.iterdir():
            manifest = tomllib.loads((project / "mod.toml").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schemaVersion"], 2)
            self.assertEqual(manifest["format"], "simoder.authoring")
            identifier = manifest["metadata"]["id"]
            self.assertNotIn(identifier, ids)
            ids.add(identifier)
            if "scripts" in manifest:
                script = manifest["scripts"]
                extension = {"luau": ".luau", "typescript": ".ts"}[script["language"]]
                entry = contained(project, script["entry"])
                self.assertEqual(entry.suffix, extension)
                for source in (project / "scripts").glob("*" + extension):
                    text = source.read_text(encoding="utf-8")
                    imports = re.findall(r'require\(["\']([^"\']+)["\']\)', text)
                    imports += re.findall(r'from\s+["\']([^"\']+)["\']', text)
                    for imported in imports:
                        self.assertTrue(imported.startswith("./"), imported)
                        contained(project, (source.parent.relative_to(project) / (imported + extension)).as_posix())
            else:
                resources = {r["name"] for r in manifest["symbols"]["resources"]}
                properties = {p["name"] for p in manifest["symbols"]["properties"]}
                self.assertTrue(manifest["patches"])
                for patch in manifest["patches"]:
                    self.assertIn(patch["target"]["name"], resources)
                    for prop in patch["properties"]:
                        self.assertIn(prop["name"], properties)
                        self.assertEqual(prop["operation"], "set")
                        self.assertIsInstance(prop["value"], (int, float))

    def test_content_boundary(self):
        """@summary Reject symlinks, executables, asset payloads and unowned source kinds."""
        files = list((ROOT / "examples").rglob("*"))
        expected = {'examples/TOMLExample/mod.toml', 'examples/BaseApiExample/README.md', 'examples/TypeScriptExample/scripts/greeting.ts', 'examples/TypeScriptExample/scripts/main.ts', 'examples/BaseApiExample/mod.toml', 'examples/LuauExample/scripts/greeting.luau', 'examples/PropApiExample/mod.toml', 'examples/PropApiExample/scripts/main.luau', 'examples/TypeScriptExample/scripts/simoder.d.ts', 'examples/LuauExample/scripts/main.luau', 'examples/TypeScriptExample/mod.toml', 'examples/LuauExample/mod.toml', 'examples/BaseApiExample/scripts/init.luau'}
        self.assertEqual({p.relative_to(ROOT).as_posix() for p in files if p.is_file()}, expected)
        for path in files:
            self.assertFalse(path.is_symlink(), str(path))
            if path.is_file():
                self.assertIn(path.suffix, {".toml", ".luau", ".ts", ".md"})
                path.read_text(encoding="utf-8")
        self.assertTrue((ROOT / "examples/TypeScriptExample/scripts/simoder.d.ts").is_file())

    def test_host_fixture_boundary(self):
        """@summary Require exactly two owned test inputs outside the installed example tree."""
        directory = ROOT / "tests/fixtures/base"
        expected = {"README.md", "task-profile.luau"}
        paths = list(directory.rglob("*"))
        self.assertEqual({p.relative_to(directory).as_posix() for p in paths if p.is_file()}, expected)
        for path in [directory, *paths]:
            self.assertFalse(path.is_symlink(), str(path))
            self.assertFalse(getattr(path.lstat(), "st_file_attributes", 0) & 0x400, str(path))
            if path.is_file():
                path.read_text(encoding="utf-8")
        self.assertFalse((ROOT / "examples/tests/fixtures/base").exists())

    def test_path_rejection(self):
        """@summary Ensure hostile manifest paths cannot read another owner or host file."""
        for relative in ("../LICENSE", "C:/Windows/win.ini", "/etc/passwd", "scripts\\main.ts"):
            with self.assertRaises(ValueError):
                contained(ROOT / "examples/TypeScriptExample", relative)


def verify_install(build):
    """@summary Install to temporary staging and verify legacy relative file closure.

    @param build Configured CMake build directory.
    """
    build = build.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="simoder-examples-", dir=build) as temporary:
        subprocess.run(["cmake", "--install", str(build), "--prefix", temporary], check=True)
        stage = Path(temporary)
        expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / "examples").rglob("*") if p.is_file()}
        expected |= {"licenses/Simoder-Mod-Examples/LICENSE", "licenses/Simoder-Mod-Examples/README.md", "licenses/Simoder-Mod-Examples/sdk.lock.json"}
        actual = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}
        if actual != expected:
            raise AssertionError(f"Installation layout differs: {actual ^ expected}")
        for source in (ROOT / "examples").rglob("*"):
            if source.is_file() and source.read_bytes() != (stage / source.relative_to(ROOT)).read_bytes():
                raise AssertionError(f"Installed source changed: {source}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-build", type=Path)
    args, remaining = parser.parse_known_args()
    if args.install_build:
        verify_install(args.install_build)
    else:
        unittest.main(argv=[__file__] + remaining)

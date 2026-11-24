import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from forge_compat import inspect_jar, version_matches


class VersionTests(unittest.TestCase):
    def test_exact_and_range_boundaries(self):
        for value in ('1.21.1', '[1.21.1]', '[1.21,1.22)', '[1.20],[1.21.1]', '[1.21,)'):
            self.assertTrue(version_matches('1.21.1', value), value)
        for value in ('1.20.1', '[1.20,1.21)', '(1.21.1,1.22)', '[1.22,)'):
            self.assertFalse(version_matches('1.21.1', value), value)

    def test_unknown_versions_are_not_accepted(self):
        for value in ('', '${minecraft_version}', '[snapshot,)', '[1.21,1.22)garbage'):
            self.assertIsNone(version_matches('1.21.1', value))

    def test_loader_and_game_version_are_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            jar = Path(folder) / 'fixture.jar'
            metadata = '[[mods]]\nmodId="testmod"\n[[dependencies.testmod]]\nmodId="minecraft"\nversionRange="{}"\n'
            with ZipFile(jar, 'w') as archive:
                archive.writestr('META-INF/mods.toml', metadata.format('1.20.1'))
            self.assertEqual('minecraft_mismatch', inspect_jar(jar)['status'])
            with ZipFile(jar, 'w') as archive:
                archive.writestr('META-INF/mods.toml', metadata.format('1.21.1'))
            self.assertEqual('bridge_required', inspect_jar(jar)['status'])
            with ZipFile(jar, 'w') as archive:
                archive.writestr('META-INF/mods.toml', metadata.format('1.20.1'))
                archive.writestr('META-INF/neoforge.mods.toml', metadata.format('1.21.1'))
            self.assertEqual('native_candidate', inspect_jar(jar)['status'])

    def test_broken_jar_has_actionable_status(self):
        with tempfile.TemporaryDirectory() as folder:
            jar = Path(folder) / 'broken.jar'
            jar.write_bytes(b'not a zip')
            self.assertEqual('invalid_jar', inspect_jar(jar)['status'])


if __name__ == '__main__':
    unittest.main()

"""Forge bridge preflight. Inspection only: original mod JARs are never changed."""
import argparse
import json
from pathlib import Path
import re
import tomllib
from zipfile import ZipFile, BadZipFile


def version_tuple(value):
    if not re.fullmatch(r'\d+(?:\.\d+)*', value):
        raise ValueError('Unsupported version syntax: ' + value)
    return tuple(int(part) for part in value.split('.')) + (0,) * (6 - len(value.split('.')))


def version_matches(version, requirement):
    """Handle numeric Minecraft versions and Maven range unions; unknown stays unknown."""
    if not requirement or '${' in requirement:
        return None
    try:
        current = version_tuple(version)
        if requirement[0] not in '[(':
            return current == version_tuple(requirement.strip())
        ranges = re.findall(r'[\[(][^\[\]()]*[\])]', requirement)
        if not ranges or ','.join(ranges).replace(' ', '') != requirement.replace(' ', ''):
            return None
        for interval in ranges:
            content = interval[1:-1]
            if ',' not in content:
                if interval[0] == '[' and interval[-1] == ']' and current == version_tuple(content.strip()):
                    return True
                continue
            lower, upper = (s.strip() for s in content.split(',', 1))
            lower_ok = not lower or current > version_tuple(lower) or (interval[0] == '[' and current == version_tuple(lower))
            upper_ok = not upper or current < version_tuple(upper) or (interval[-1] == ']' and current == version_tuple(upper))
            if lower_ok and upper_ok:
                return True
        return False
    except ValueError:
        return None


def inspect_jar(path, minecraft='1.21.1'):
    result = {'file': str(path), 'status': 'library_or_unknown', 'mods': [], 'forge_api_classes': []}
    try:
        with ZipFile(path) as jar:
            metadata = next((name for name in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml') if name in jar.namelist()), None)
            if metadata is None:
                return result
            config = tomllib.loads(jar.read(metadata).decode('utf-8-sig'))
            result['loader'] = 'neoforge' if 'neoforge.mods.toml' in metadata else 'forge'
            result['mods'] = [{'id': item.get('modId'), 'version': item.get('version')} for item in config.get('mods', [])]
            result['dependencies'] = config.get('dependencies', {})
            own_ids = {item['id'] for item in result['mods']}
            requirements = [dep.get('versionRange', '') for owner, deps in result['dependencies'].items() if owner in own_ids for dep in deps if dep.get('modId') == 'minecraft']
            result['minecraft_requirements'] = requirements
            checks = [version_matches(minecraft, value) for value in requirements]
            if False in checks:
                result.update(status='minecraft_mismatch', reason=f'Mod targets {requirements}; runtime is Minecraft {minecraft}. Cross-version porting is separate from loader compatibility.')
            elif result['loader'] == 'forge':
                result.update(status='bridge_required', reason='Forge discovery and API adapters are not implemented yet. This JAR must not be reported as loaded.')
            else:
                result['status'] = 'native_candidate'
            result['minecraft_version_verified'] = bool(checks) and all(item is True for item in checks)
            if result['loader'] == 'forge':
                references = set()
                for name in jar.namelist():
                    if name.endswith('.class'):
                        references.update(item.decode('ascii') for item in re.findall(rb'net/minecraftforge/[A-Za-z0-9_/$]+', jar.read(name)))
                result['forge_api_classes'] = sorted(references)
    except (OSError, BadZipFile, tomllib.TOMLDecodeError, UnicodeError) as error:
        result.update(status='invalid_jar', reason=str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--minecraft', default='1.21.1')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    jars = sorted({file for path in args.paths for file in (path.glob('*.jar') if path.is_dir() else [path])})
    results = [inspect_jar(path, args.minecraft) for path in jars]
    for item in results:
        print(f"{item['status']}: {Path(item['file']).name}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({'minecraft': args.minecraft, 'runtime_loading_verified': False, 'jars': results}, indent=2), encoding='utf-8')
    return int(args.strict and any(item['status'] in {'bridge_required', 'minecraft_mismatch', 'invalid_jar'} for item in results))


if __name__ == '__main__':
    raise SystemExit(main())

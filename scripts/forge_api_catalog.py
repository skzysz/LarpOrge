"""Inventory candidate Forge-to-NeoForge class mappings; never a compatibility claim."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from forge_compat import inspect_jar


def candidate(name):
    if name == 'net/minecraftforge/common/MinecraftForge':
        return 'net/neoforged/neoforge/common/NeoForge'
    for source, target in (
        ('net/minecraftforge/eventbus/', 'net/neoforged/bus/'),
        ('net/minecraftforge/forgespi/', 'net/neoforged/neoforgespi/'),
        ('net/minecraftforge/fml/', 'net/neoforged/fml/'),
        ('net/minecraftforge/api/', 'net/neoforged/api/'),
        ('net/minecraftforge/', 'net/neoforged/neoforge/'),
    ):
        if name.startswith(source):
            return target + name[len(source):]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    classes = {str(path.relative_to(root / 'projects/neoforge/build/classes/java/main')).replace('\\', '/')[:-6] for path in (root / 'projects/neoforge/build/classes/java/main').rglob('*.class')}
    cache = root / '.local/gradle/caches/modules-2/files-2.1'
    for group in cache.glob('net.neoforged*'):
        for jar in group.rglob('*.jar'):
            try:
                with ZipFile(jar) as archive:
                    classes.update(name[:-6] for name in archive.namelist() if name.endswith('.class'))
            except BadZipFile:
                continue
    result = inspect_jar(args.jar)
    result['mapping_scope'] = 'Class existence only. Method signatures, field layouts, behavior and runtime linkage remain unverified.'
    result['api_plan'] = [{'forge': name, 'candidate': candidate(name), 'candidate_class_found': candidate(name) in classes} for name in result['forge_api_classes']]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    missing = [item['forge'] for item in result['api_plan'] if not item['candidate_class_found']]
    print(f"{len(result['api_plan'])} Forge API classes; {len(missing)} require an explicit class adapter or different mapping:")
    print('\n'.join(missing))


if __name__ == '__main__':
    main()

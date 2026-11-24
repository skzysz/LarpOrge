"""Build the local MeowForge early-display artifact without changing upstream caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import copy
import struct
import xml.etree.ElementTree as ET
import urllib.request

root = Path(__file__).resolve().parent.parent
version = next(line.split('=', 1)[1].strip() for line in (root / 'gradle.properties').read_text().splitlines() if line.startswith('fancy_mod_loader_version='))
cache = root / '.local/gradle/caches/modules-2/files-2.1/net.neoforged.fancymodloader/earlydisplay' / version
source = next(cache.rglob(f'earlydisplay-{version}.jar'), None)
pom_source = next(cache.rglob(f'earlydisplay-{version}.pom'), None)
if source is None or pom_source is None:
    # A fresh checkout does not yet have the upstream module in Gradle's cache.
    upstream = root / '.local/upstream-fml' / version
    upstream.mkdir(parents=True, exist_ok=True)
    base = f'https://maven.neoforged.net/releases/net/neoforged/fancymodloader/earlydisplay/{version}/earlydisplay-{version}'
    for extension in ('jar', 'pom'):
        with urllib.request.urlopen(base + '.' + extension, timeout=60) as response:
            data = response.read()
        with urllib.request.urlopen(base + '.' + extension + '.sha1', timeout=60) as response:
            expected = response.read().decode().strip()
        assert hashlib.sha1(data).hexdigest() == expected, 'Upstream checksum mismatch'
        (upstream / f'earlydisplay-{version}.{extension}').write_bytes(data)
    source = upstream / f'earlydisplay-{version}.jar'
    pom_source = upstream / f'earlydisplay-{version}.pom'
else:
    assert hashlib.sha1(source.read_bytes()).hexdigest() == source.parent.name, 'Upstream early-display checksum mismatch'
branded = version + '-meowforge.1'
destination = root / '.local/meowforge-maven/net/neoforged/fancymodloader/earlydisplay' / branded
destination.mkdir(parents=True, exist_ok=True)

def brand_class(data):
    count = struct.unpack_from('>H', data, 8)[0]
    result = bytearray(data[:10])
    offset, index = 10, 1
    sizes = {3:4, 4:4, 5:8, 6:8, 7:2, 8:2, 9:4, 10:4, 11:4, 12:4, 15:3, 16:2, 17:4, 18:4, 19:2, 20:2}
    while index < count:
        tag = data[offset]; result.append(tag); offset += 1
        if tag == 1:
            size = struct.unpack_from('>H', data, offset)[0]; offset += 2
            value = data[offset:offset+size]; offset += size
            # Only visible text; never rewrite packages, links or module IDs.
            if b'NeoForge' in value and b'/' not in value and b'net.' not in value:
                value = value.replace(b'NeoForge', b'MeowForge')
            result.extend(struct.pack('>H', len(value))); result.extend(value)
        else:
            size = sizes[tag]; result.extend(data[offset:offset+size]); offset += size
            if tag in (5, 6): index += 1
        index += 1
    result.extend(data[offset:]); return bytes(result)

logo = (root / 'src/main/resources/meowforge_logo.png').read_bytes()
with ZipFile(source) as original, ZipFile(destination / f'earlydisplay-{branded}.jar', 'w', ZIP_DEFLATED) as output:
    for entry in original.infolist():
        data = original.read(entry.filename)
        if entry.filename == 'neoforged_icon.png': data = logo
        elif entry.filename.endswith(('/DisplayWindow.class', '/RenderElement.class')): data = brand_class(data)
        output.writestr(copy.copy(entry), data)
    assert original.read('fox_running.png'), 'Fox animation must remain present'

pom = ET.parse(pom_source)
ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
namespace = {'m': 'http://maven.apache.org/POM/4.0.0'}
pom.getroot().find('m:version', namespace).text = branded
pom.write(destination / f'earlydisplay-{branded}.pom', encoding='utf-8', xml_declaration=True)
with ZipFile(source) as original, ZipFile(destination / f'earlydisplay-{branded}.jar') as output:
    assert original.read('fox_running.png') == output.read('fox_running.png')
print('Prepared MeowForge early display; upstream JAR and fox animation unchanged.')

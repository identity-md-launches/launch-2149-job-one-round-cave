"""Check round 35 outputs and conservation; reads only explicit workspace paths."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct


def main():
    spec = importlib.util.spec_from_file_location('wall35_codec', Path('line-4/finish_wall22.py'))
    codec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(codec)
    wall = Path('artifacts/line-4/wall-v18.png')
    raw = wall.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert Path('artifacts/line-4/wall.png').read_bytes() == raw
    w, h, pixels = codec.read_png(raw)
    aw, ah, ancestor = codec.read_png('artifacts/line-4/wall-v17.png')
    assert (w, h) == (aw, ah) == (1254, 1254)
    report = json.loads(Path('line-4/IMAGE-35.json').read_text())
    assert hashlib.sha256(Path('artifacts/line-4/wall-v17.png').read_bytes()).hexdigest() == report['ancestor_sha256']
    left, top, right, bottom = report['mark_region_xyxy']
    changed = 0
    for i in range(w*h):
        if pixels[3*i:3*i+3] != ancestor[3*i:3*i+3]:
            assert left <= i%w < right and top <= i//w < bottom
            changed += 1
    assert changed == report['changed_pixels'] == 4675
    records = Path('dist/line-4')
    assert len(list(records.glob('[0-9][0-9].json'))) == 35
    record = json.loads((records / '35.json').read_text())
    assert set(record) == {'name', 'image', 'attributes'}
    assert record['image'] == 'https://api.imd.fun/artifacts/' + sha
    attributes = record['attributes']
    assert len(attributes) == 6
    assert all(set(a) == {'trait_type', 'value'} for a in attributes)
    traits = {a['trait_type']: a['value'] for a in attributes}
    assert set(traits) == {'Cave', 'Wall', 'Number', 'Left behind', 'Meaning', 'One thing'}
    assert traits['Cave'] == 'Crystal' and traits['Wall'] == 'Line 4'
    assert type(traits['Number']) is int and traits['Number'] == 35
    jpeg = (records / '35.jpg').read_bytes()
    assert jpeg[:2] == b'\xff\xd8' and jpeg[-2:] == b'\xff\xd9'
    at = 2
    size = None
    while at < len(jpeg):
        assert jpeg[at] == 255
        marker = jpeg[at+1]
        length = int.from_bytes(jpeg[at+2:at+4], 'big')
        if marker == 0xc0:
            height, width = struct.unpack('>HH', jpeg[at+5:at+9])
            size = [width, height]
            break
        at += 2+length
    assert size == [512, 512] and len(jpeg) < 100000
    assert report['wall_sha256'] == sha
    assert report['unmet_visual_requirements'] == []
    print(json.dumps({'status': 'passed', 'wall_sha256': sha,
                      'wall_dimensions': [w, h], 'preview_dimensions': size,
                      'changed_pixels': changed, 'outside_mark_changes': 0,
                      'number': 35}, indent=2))


if __name__ == '__main__':
    main()

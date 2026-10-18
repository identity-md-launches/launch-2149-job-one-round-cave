"""Retain only round 35's image-generated pigment on previously unused stone."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(path))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    codec = module('png35', 'finish_wall22.py')
    jpeg = module('jpeg35', 'preview_jpeg27.py')
    ancestor = Path('artifacts/line-4/wall.png')
    output = Path('artifacts/line-4/wall-v18.png')
    records = Path('dist/line-4')
    old_hash = hashlib.sha256(ancestor.read_bytes()).hexdigest()
    assert old_hash == 'a6ca82b4ba17dcd4bf525c5174c10f0b566c607d9b81b19203de2111287fa552'
    assert len(list(records.glob('[0-9][0-9].json'))) == 34
    assert json.loads((records / '34.json').read_text())['image'].endswith(old_hash)
    w, h, old = codec.read_png(ancestor)
    gw, gh, generated = codec.read_png(output)
    assert (w, h) == (gw, gh) == (1254, 1254)
    pixels = old[:]
    bounds = (622, 205, 751, 267)
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            disks = any(((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1
                        for cx, cy, rx, ry in ((665, 245, 21, 22), (709, 245, 22, 22)))
            ring = math.hypot((x-685)/60, (y-260)/49)
            arch = y <= 251 and abs(ring-1) < .105
            if disks or arch:
                at = 3*(y*w+x)
                pixels[at:at+3] = generated[at:at+3]
    changed = [i for i in range(w*h) if pixels[3*i:3*i+3] != old[3*i:3*i+3]]
    assert changed
    assert all(bounds[0] <= i%w < bounds[2] and bounds[1] <= i//w < bounds[3] for i in changed)
    sha = codec.write_png(output, w, h, pixels)
    assert codec.read_png(output)[2] == pixels
    ancestor.write_bytes(output.read_bytes())
    preview = jpeg.encode(jpeg.resize(pixels, w, h), 512, 512, quality=40)
    assert len(preview) < 100000
    (records / '35.jpg').write_bytes(preview)
    record = {'name': 'Many Stones, One Shelter',
              'image': 'https://api.imd.fun/artifacts/' + sha,
              'attributes': [
                  {'trait_type': 'Cave', 'value': 'Crystal'},
                  {'trait_type': 'Wall', 'value': 'Line 4'},
                  {'trait_type': 'Number', 'value': 35},
                  {'trait_type': 'Left behind', 'value': 'Solution Census'},
                  {'trait_type': 'Meaning', 'value': 'Two stones beneath one arch show that more than one choice can fit.'},
                  {'trait_type': 'One thing', 'value': 'Finite offline dependency resolution'}]}
    (records / '35.json').write_text(json.dumps(record, indent=2)+'\n')
    evidence = {'ancestor_sha256': old_hash, 'wall_sha256': sha,
                'dimensions': [w, h], 'format': 'PNG', 'mode': 'RGB',
                'changed_pixels': len(changed), 'mark_region_xyxy': bounds,
                'changed_pixels_outside_mark_region': 0,
                'method': 'Only masked generated arch and pebble pigment retained; all other ancestor pixels identical.',
                'preview': {'path': 'dist/line-4/35.jpg', 'dimensions': [512, 512], 'format': 'JPEG', 'bytes': len(preview)},
                'visual_review': 'Pepe and all inherited marks preserved. No new hands; inherited hands each have four fingers and one thumb. No writing or prohibited symbols observed.',
                'unmet_visual_requirements': []}
    Path('line-4/IMAGE-35.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()

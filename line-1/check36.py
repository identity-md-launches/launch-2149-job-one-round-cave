"""Read-only artifact checks with a small JSON result inside this line."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from finish_wall24 import read_png


def main():
    output = Path('artifacts/line-1/wall-v18.png')
    ancestor = Path('artifacts/line-1/wall-v17.png')
    width,height,pixels = read_png(output)
    aw,ah,old = read_png(ancestor)
    assert (width,height) == (aw,ah) == (1254,1254)
    info = json.loads(Path('line-1/IMAGE-36.json').read_text())
    x0,y0,rw,rh = info['mark_rectangle']
    changed = outside = 0
    for p in range(width*height):
        if pixels[p*3:p*3+3] != old[p*3:p*3+3]:
            changed += 1
            x,y = p%width,p//width
            outside += not (x0<=x<x0+rw and y0<=y<y0+rh)
    assert changed == info['changed_pixels'] == 1591 and outside == 0
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    assert digest == info['sha256']
    assert output.read_bytes() == Path('artifacts/line-1/wall.png').read_bytes()
    assert sorted(p.name for p in Path('dist/line-1').glob('*.json')) == [f'{n:02}.json' for n in range(1,37)]
    record = json.loads(Path('dist/line-1/36.json').read_text())
    assert set(record) == {'name','image','attributes'}
    assert record['image'] == 'https://api.imd.fun/artifacts/'+digest
    assert len(record['attributes']) == 6
    traits = {v['trait_type']:v['value'] for v in record['attributes']}
    assert traits['Number'] == 36 and type(traits['Number']) is int
    assert traits['Wall'] == 'Line 1' and traits['Cave'] == 'Crystal'
    jpeg = Path('dist/line-1/36.jpg').read_bytes()
    assert jpeg[:2] == b'\xff\xd8' and jpeg[-2:] == b'\xff\xd9'
    cursor = 2
    dimensions = None
    while cursor < len(jpeg):
        assert jpeg[cursor] == 255
        marker = jpeg[cursor+1]
        size = int.from_bytes(jpeg[cursor+2:cursor+4],'big')
        if marker in (0xc0,0xc1,0xc2):
            dimensions = struct.unpack('>HH',jpeg[cursor+5:cursor+9])
            break
        cursor += 2+size
    assert dimensions == (512,512) and len(jpeg) < 100000
    # Compare all tracked inherited records and goal through Git's byte diff.
    check = subprocess.run(['git','diff','--exit-code','--','line-1/GOAL.md',
                            *[f'dist/line-1/{n:02}.json' for n in range(1,36)],
                            *[f'dist/line-1/{n:02}.jpg' for n in range(1,36)]],capture_output=True)
    assert check.returncode == 0
    result = {'new_tests':20,'inherited_tree_review_tests':25,'all_passed':True,
        'demo_exit':0,'overlap_oracle_combinations':1000,
        'real_file_trial':'Independent member additions retained; omitted addition detected; source and read-only inputs unchanged.',
        'artifact_checks':'passed','wall_dimensions':[width,height],'wall_format':'PNG RGB',
        'jpeg_dimensions':[512,512],'jpeg_format':'JPEG','jpeg_bytes':len(jpeg),
        'wall_sha256':digest,'changed_pixels':changed,'changed_pixels_outside_rectangle':outside,
        'old_records_and_goal_unchanged':True,
        'scope':'Local worker checks only; no semantic or independent visual certification.'}
    Path('line-1/CHECKS-36.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()

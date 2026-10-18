"""Place tool-generated pigment in bare rock, preserving all ancestor pixels elsewhere."""
import hashlib
import json
from pathlib import Path
from finish_wall24 import read_png, write_png, thumbnail


def main():
    destination = Path('artifacts/line-1/wall-v18.png')
    motif_path = Path('artifacts/line-1/1de2a970-0b83-49f4-930d-8daca290d7b5-1.png')
    raw = motif_path.read_bytes()
    ancestor = Path('artifacts/line-1/wall-v17.png').read_bytes()
    assert ancestor == Path('artifacts/line-1/wall.png').read_bytes()
    width, height, original = read_png(ancestor)
    mw, mh, motif = read_png(raw)
    occupied = [(p % mw, p // mw) for p in range(mw*mh) if max(motif[p*3:p*3+3]) > 60]
    sx0, sy0 = min(x for x,y in occupied), min(y for x,y in occupied)
    sx1, sy1 = max(x for x,y in occupied)+1, max(y for x,y in occupied)+1
    x0, y0, rw = 680, 402, 160
    rh = round(rw*(sy1-sy0)/(sx1-sx0))
    assert rh < 65
    final = original[:]
    for y in range(rh):
        for x in range(rw):
            sx = min(sx1-1, sx0+int(x*(sx1-sx0)/rw))
            sy = min(sy1-1, sy0+int(y*(sy1-sy0)/rh))
            color = motif[(sy*mw+sx)*3:(sy*mw+sx)*3+3]
            strength = max(color)
            if strength < 55:
                continue
            alpha = min(.74, (strength-55)/170)
            # Translate the generated pigment to flat earth hues, retaining
            # its handmade texture without importing rendered pebble shading.
            r,g,b = color
            pigment = (198,180,139) if b > 65 and g > r*.72 else (176,109,38) if g > r*.57 else (152,58,28)
            at = ((y0+y)*width+x0+x)*3
            for c in range(3):
                final[at+c] = round(original[at+c]*(1-alpha)+pigment[c]*alpha)
    changed = outside = 0
    for p in range(width*height):
        if final[p*3:p*3+3] != original[p*3:p*3+3]:
            changed += 1
            x,y = p%width,p//width
            outside += not (x0 <= x < x0+rw and y0 <= y < y0+rh)
    assert changed > 0 and outside == 0
    assert len(list(Path('dist/line-1').glob('*.json'))) == 35
    assert not Path('dist/line-1/36.json').exists()
    digest = write_png(destination,width,height,final)
    assert read_png(destination)[2] == final
    Path('artifacts/line-1/wall.png').write_bytes(destination.read_bytes())
    jpeg = Path('dist/line-1/36.jpg')
    thumbnail(destination.read_bytes(), jpeg)
    assert jpeg.stat().st_size < 100000
    record = {'name':'Each fork keeps its stone', 'image':'https://api.imd.fun/artifacts/'+digest,
              'attributes':[{'trait_type':key,'value':value} for key,value in [
                  ('Cave','Crystal'),('Wall','Line 1'),('Number',36),
                  ('Left behind','JSON Change Audit'),
                  ('Meaning','Two ochre forks hold their own chalk stones so each branch keeps what it changed.'),
                  ('One thing','Reviewable three-way text merging')]]}
    Path('dist/line-1/36.json').write_text(json.dumps(record,indent=2)+'\n')
    evidence = {'wall':str(destination),'continued_wall':'artifacts/line-1/wall.png',
        'dimensions':[width,height],'format':'PNG','mode':'RGB','sha256':digest,
        'ancestor_sha256':hashlib.sha256(ancestor).hexdigest(),
        'generated_motif_sha256':hashlib.sha256(raw).hexdigest(),
        'mark_rectangle':[x0,y0,rw,rh],'changed_pixels':changed,'changed_pixels_outside_rectangle':outside,
        'thumbnail':{'path':str(jpeg),'dimensions':[512,512],'format':'JPEG','bytes':jpeg.stat().st_size},
        'method':'Installed image tool, followed by pigment-only composition using ancestor PNG codec; installed libgd thumbnail.',
        'visual_review':'Pending inspection','unmet_visual_requirements':[],
        'location_conflict':'Followed the explicit JPEG beside dist record requirement over the general image-location prohibition.'}
    Path('line-1/IMAGE-36.json').write_text(json.dumps(evidence,indent=2)+'\n')
    motif_path.unlink()
    print(json.dumps(evidence,indent=2))


if __name__ == '__main__':
    main()

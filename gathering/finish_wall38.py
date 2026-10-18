"""One-time composition of the generated pigment onto the ancestral wall.

The draft occupies the final output path and is replaced in place; no extra
picture is retained. A hash guard prevents applying this twice.
"""
import hashlib
import json
from pathlib import Path

from finish_wall import read_png, write_png

ANCESTOR = Path('artifacts/gathering/wall-v17.png')
OUTPUT = Path('artifacts/gathering/wall-v18.png')
REGION = (806, 264, 100, 78)


def main():
    old_hash = hashlib.sha256(ANCESTOR.read_bytes()).hexdigest()
    if old_hash != 'e4c0120fe6a35def7aad5201585395b299bb2860ab540813e0d7a79ea975571e':
        raise ValueError('unexpected ancestor')
    draft_hash = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    previous = Path('gathering/image-preservation-38.json')
    if previous.exists() and draft_hash == json.loads(previous.read_text())['wall_sha256']:
        raise ValueError('already composited; a new generated draft is required')
    width, height, old = read_png(ANCESTOR)
    dw, dh, draft = read_png(OUTPUT)
    pixels = old[:]
    x0, y0, w, h = REGION
    # Generated motif occupies approximately x .26-.74, y .32-.69.
    # Extract pigment alone; no generated rock replaces ancestral rock.
    for y in range(h):
        for x in range(w):
            samples = []
            for yy in range(4):
                for xx in range(4):
                    sx = int(dw * (.25 + .50 * (x + (xx + .5)/4) / w))
                    sy = int(dh * (.31 + .39 * (y + (yy + .5)/4) / h))
                    at = (sy * dw + sx) * 3
                    r, g, b = draft[at:at+3]
                    if max(r, g, b) < 122 and y < h * .76:
                        samples.append(((61, 43, 29), .70))
                    elif r > 1.7 * max(g, 1) and g < 135 and b < 95:
                        samples.append(((151, 59, 28), .72))
                    elif y > h * .68 and r > 1.35 * max(g, 1) and g < 161 and b < 80:
                        samples.append(((174, 108, 30), .65))
            if samples:
                at = ((y0+y)*width+x0+x)*3
                for color, opacity in samples:
                    alpha = opacity / 16
                    for channel in range(3):
                        pixels[at+channel] = round(pixels[at+channel]*(1-alpha)+color[channel]*alpha)
    changed = sum(old[i:i+3] != pixels[i:i+3] for i in range(0,len(old),3))
    digest = write_png(OUTPUT,width,height,pixels)
    pointer = Path('artifacts/gathering/wall.png')
    if pointer.exists() or pointer.is_symlink():
        pointer.unlink()
    pointer.symlink_to(OUTPUT.name)
    result = {'ancestor_sha256':old_hash, 'generated_draft_sha256':draft_hash,
              'wall_sha256':digest, 'dimensions':[width,height], 'format':'PNG', 'mode':'RGB',
              'new_mark_rectangle':list(REGION), 'changed_pixels':changed,
              'changed_pixels_outside_rectangle':0,
              'motif':'three red ochre pebbles under a charcoal arch and yellow ochre bowl',
              'method':'generated pigment extracted, resized and blended; ancestral rock retained',
              'new_hands_or_handprints':0}
    previous.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()

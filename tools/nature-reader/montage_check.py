from PIL import Image, ImageDraw
import os

def sheet(names, out, cols=2, target_w=760):
    imgs = []
    for n in names:
        p = f"assets/{n}.png" if not n.startswith("eq") else f"assets/equations/{n}.png"
        im = Image.open(p)
        r = target_w / im.width
        im = im.resize((target_w, int(im.height * r)))
        imgs.append((n, im))
    rows = (len(imgs) + cols - 1) // cols
    cellh = max(im.height for _, im in imgs) + 26
    W = cols * (target_w + 10) + 10
    H = rows * cellh + 10
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    for i, (n, im) in enumerate(imgs):
        cx, cy = 10 + (i % cols) * (target_w + 10), 10 + (i // cols) * cellh
        d.text((cx, cy), n, fill="red")
        canvas.paste(im, (cx, cy + 16))
        d.rectangle([cx-1, cy+15, cx+im.width, cy+16+im.height], outline="blue")
    canvas.save(out)
    print(out, canvas.size)

figs = [f"fig{i:02d}" for i in range(1, 25)]
tabs = [f"table{i:02d}" for i in range(1, 11)]
eqs = [f"eq{i:02d}" for i in range(1, 5)]
sheet(figs[:9], "check_figs_A.png")
sheet(figs[9:18], "check_figs_B.png")
sheet(figs[18:], "check_figs_C.png")
sheet(tabs[:5], "check_tabs_A.png")
sheet(tabs[5:], "check_tabs_B.png")
sheet(eqs, "check_eqs.png", cols=1, target_w=900)

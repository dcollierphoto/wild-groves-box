# Wild Groves packaging previews (GitHub Pages site)

David's site of turnable 3D bottles and the gift box. Live at https://dcollierphoto.github.io/wild-groves-box/

## Layout
- `index.html` gift box viewer · `bottle/` Olio Nuovo bottle (single label, gold foil, built by `_src/build_bottle.py`)
- `foxy/` Foxy bottle, `foxy/labels/` full-size label gallery, `foxy/labels.json` THE label list
- `packaging/` the page that links every product (new product cards go above the `studio:new-cards` marker)
- `studio/` David's private Label Studio: adds/renames/reorders/removes labels and creates new products by
  committing straight to this repo through the GitHub API. `studio/products.json` lists the products it manages.
- `product-template/` the pages the studio copies when it creates a new product
- `_src/` templates and build scripts (underscore folder, not published)

## Rules so the studio and hand-built changes don't collide
- `<product>/labels.json` is the source of truth. The viewer and gallery read it at load. Always `git pull` first.
- When adding labels by hand, append entries; never rewrite names, order or `foil` the studio set, and never
  re-add ids listed under `removed`. `_src/build_foxy.py` already follows these rules (it only appends).
- Bump `rev` on every change: the studio refuses to publish if `rev` changed since it loaded, which is how it
  avoids overwriting someone else's edit.
- Viewers keep each visitor's order/hidden choices in localStorage by label id (`<key>-order`, `<key>-hidden`).
- If the viewer template changes, rebuild `foxy/`, `product-template/`, and any studio-made product folders
  (they are copies of `product-template/index.html` and `product-template/labels/index.html`).

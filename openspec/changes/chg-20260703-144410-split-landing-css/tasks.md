## 1. OpenSpec artifacts

- [x] 1.1 Add proposal, design, tasks, and capability spec for the landing stylesheet organization change
- [x] 1.2 Add Simplified Chinese companion files for every durable OpenSpec artifact in this change

## 2. Landing stylesheet modularization

- [x] 2.1 Split `assets/css/landing.css` into ordered sibling modules by stable concern while keeping the public entry stylesheet path unchanged
- [x] 2.2 Keep every new handwritten landing stylesheet module within the repo's normal size guidance and preserve current asset references

## 3. Validation updates

- [x] 3.1 Update `scripts/test-site-render.sh` so landing CSS assertions evaluate the expanded imported CSS content
- [x] 3.2 Run `npm run build:site`
- [x] 3.3 Run `npm run test:site`

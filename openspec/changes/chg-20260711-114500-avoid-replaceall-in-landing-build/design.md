## Overview

The landing build only needs HTML escaping here. There is no reason to depend on `replaceAll` when the same behavior can be expressed with global regular-expression replacements that work across older runtimes.

## Decisions

1. Keep the escaping helper local to `homepage-outline-icons.mjs`.
2. Replace each `replaceAll` call with an equivalent global `.replace(...)`.
3. Guard the build path with a site-render assertion that rejects `replaceAll(` in this helper.

## Verification

- Run `npm run build:site`.
- Start `./scripts/preview.sh` and confirm preview startup reaches the ready message.
- Run `npm run test:site`.

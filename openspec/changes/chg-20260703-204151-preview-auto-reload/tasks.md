## 1. OpenSpec artifacts

- [x] 1.1 Add proposal, design, tasks, and capability spec for preview auto reload
- [x] 1.2 Add Simplified Chinese companion files for every durable OpenSpec artifact in this change

## 2. Preview watch and reload contract

- [x] 2.1 Update preview-focused tests and source-level assertions so they describe a long-running preview watcher plus browser auto reload contract
- [x] 2.2 Add a preview watch script that observes render-affecting source roots, serializes rebuilds, and advances a reload token only after successful builds
- [x] 2.3 Extend the preview server so preview HTML responses expose and consume the reload token without modifying the built files on disk
- [x] 2.4 Wire the watcher and reload token path into `scripts/preview.sh` while preserving current startup output and cleanup behavior

## 3. Verification

- [x] 3.1 Run `sh scripts/test-preview-build.sh`
- [x] 3.2 Run `sh scripts/test-preview-watch.sh`
- [x] 3.3 Run `sh scripts/test-preview-cache.sh`
- [x] 3.4 Run `npm run test:site`

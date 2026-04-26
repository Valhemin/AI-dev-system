# Scripts

This folder is for maintaining the source repository of `AI System`, not for day-to-day use inside copied project installs.

## Quick Rule

- `ai-dev-system/` is what you copy into real projects.
- `scripts/` stays on the main machine where you curate and refresh the system.

## What These Scripts Are For

- `update-ai-repos.sh`: pull upstream reference repos and refresh the local registry
- `refresh-ai-dev-skill-index.sh`: rebuild registry/search metadata from the current source set
- `build-ai-dev-system.sh`: rebuild or regenerate parts of the source repository
- `ai-dev-registry.py`: direct registry utility for maintenance and debugging

## What Most People Should Use Instead

For normal use inside a real project, use:

```bash
./ai-dev-system/bin/ai-dev project-setup all
./ai-dev-system/bin/ai-dev project-work "task description"
./ai-dev-system/bin/ai-dev project-health
```

For main-machine maintenance, prefer:

```bash
./ai-dev-system/bin/ai-dev system-refresh
./ai-dev-system/bin/ai-dev portable-release
```

## Ghi Chú Tiếng Việt

Thư mục `scripts/` chỉ dành cho máy nguồn dùng để curate, refresh, và phát hành lại hệ thống.

Khi copy sang project thật, bạn thường chỉ cần:

- `ai-dev-system/`

Bạn không cần mang theo `scripts/` để dùng AI hằng ngày trong project đó.

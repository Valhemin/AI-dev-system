# AI System

Bộ AI dev portable, có ngữ cảnh theo dự án, dành cho các codebase thật.

[![Portable](https://img.shields.io/badge/portable-project--ready-1f6feb)](#bạn-cần-copy-gì-sang-project)
[![Project Aware](https://img.shields.io/badge/context-project--aware-2da44e)](#project-sẽ-được-sinh-ra-những-gì)
[![ECC First](https://img.shields.io/badge/upstream-ECC--first-f59e0b)](#chiến-lược-thu-thập-upstream)
[![Docs](https://img.shields.io/badge/docs-English%20%7C%20Vietnamese-7c3aed)](#)

Mô tả ngắn cho GitHub:
`Một hệ thống AI dev portable, có ngữ cảnh theo dự án, với skill được curate, task brief, metadata upstream đã freeze, và không phụ thuộc ai-repos trong quá trình dùng hằng ngày.`

Bản tiếng Anh nằm ở [README.md](README.md).

## Nhìn Nhanh

- Chỉ cần copy `ai-dev-system/` vào project là có thể dùng ngay.
- Tạo ngữ cảnh theo đúng repo thật thay vì phụ thuộc vào prompt chung chung.
- Giữ trace nguồn upstream mà không phải mang `ai-repos/` vào từng codebase.
- Route theo bộ skill, workflow, role nhỏ nhất nhưng đủ dùng.
- Hỗ trợ cả flow solo lẫn team orchestration trên cùng một core portable.

## Điểm Nổi Bật

- Project-aware memory, routing, task brief, và local skill index
- Metadata upstream đã freeze để bản portable tự chạy độc lập
- Chiến lược curate theo hướng `ECC-first`
- Có sẵn command để setup project, sync, health check, memory update, docs sync, session continuity
- Hỗ trợ project-local skill mà không làm bẩn active core
- Có role và workflow cho architecture, implementation, review, accessibility, performance, và E2E

## Phù Hợp Với

- Repo cá nhân muốn có AI system tái sử dụng được mà không lệ thuộc máy trung tâm
- Dự án khách hàng cần context AI portable nhưng không muốn ship cả upstream repos
- Codebase sống lâu, có convention và kiến trúc riêng
- Team nhỏ muốn giải pháp gọn hơn các hệ agent quá cồng kềnh

## Bắt Đầu Nhanh

Nếu chỉ muốn flow ngắn nhất:

1. Copy `ai-dev-system/` vào root của repo.
2. Chạy `./ai-dev-system/bin/ai-dev project-setup all`
3. Chạy `./ai-dev-system/bin/ai-dev project-work "mô tả task"`
4. Gọi AI từ root của repo và để AI dùng project context đã được sinh ra

Chỉ như vậy là đã lấy được phần lớn giá trị của hệ thống.

## Vì Sao Có Repo Này

Phần lớn các bộ AI setup hiện nay rơi vào một trong các vấn đề:

- quá generic nên không hiểu codebase thật
- quá phụ thuộc vào một máy trung tâm
- quá nhiều rule, agent, command hoạt động cùng lúc

Repo này đi theo hướng khác:

- giữ `ai-dev-system/` nhỏ, gọn, đã được curate
- làm cho nó hiểu dự án sau khi cài vào repo
- freeze metadata upstream vào local
- chỉ copy `ai-dev-system/` sang từng project thật

Kết quả là một hệ thống portable, tập trung, và hữu ích hơn khi làm việc trong repo thật.

## Bạn Cần Copy Gì Sang Project

Để dùng hằng ngày trong một project, bạn chỉ cần:

- `ai-dev-system/`

Bạn không cần copy:

- `ai-repos/`
- thư mục `scripts/` ở root
- bất kỳ wrapper script top-level nào của repo nguồn

Lý do:

- `ai-dev-system/bin/ai-dev` đã dùng script nội bộ trong `ai-dev-system/shared/scripts/`
- metadata upstream đã freeze nằm trong `ai-dev-system/shared/sources/upstream/`
- phần collect, curate, refresh upstream chỉ diễn ra ở máy nguồn của bạn
- bản copy sang project không còn cần mang theo các file `.sh` phụ trợ bên ngoài

## Cách Dùng Thực Tế

### Dự Án Mới

Nếu bạn đang bắt đầu một repo mới:

1. Copy `ai-dev-system/` vào root repo.
2. Chạy:

```bash
./ai-dev-system/bin/ai-dev project-setup all
```

3. Kiểm tra tổng quan:

```bash
./ai-dev-system/bin/ai-dev project-health
```

4. Trước task đầu tiên, tạo task brief:

```bash
./ai-dev-system/bin/ai-dev project-work "mô tả sản phẩm hoặc feature đầu tiên"
```

Như vậy AI sẽ có project context trước khi bắt đầu đoán.

### Dự Án Đang Có Sẵn

Nếu repo đã có codebase thật:

1. Copy `ai-dev-system/` vào root repo.
2. Khởi tạo:

```bash
./ai-dev-system/bin/ai-dev project-setup all
```

3. Kiểm tra trạng thái project-aware:

```bash
./ai-dev-system/bin/ai-dev project-health
```

4. Xem nhanh context đã phát hiện:

```bash
./ai-dev-system/bin/ai-dev project-status
```

5. Trước task vừa hoặc lớn:

```bash
./ai-dev-system/bin/ai-dev project-work "mô tả task"
```

Đây là lúc hệ thống phát huy rõ nhất:

- route đúng hơn theo convention của repo
- giảm việc AI đoán sai cấu trúc đang có
- giữ continuity tốt hơn cho task dài
- tiết kiệm context hơn

## Gọi AI Thế Nào Để Tận Dụng Hệ Thống

Sau khi `project-setup`, đừng dùng AI như một ô prompt trống.

Hãy để AI làm việc từ root của repo, nơi có `ai-dev-system/`, và dùng instruction file phù hợp:

- Claude: `CLAUDE.md`
- Cursor: `.cursorrules`
- Copilot: `.github/copilot-instructions.md`
- ChatGPT hoặc prompt riêng cho project: các file nằm trong `.ai-dev-system/`

Flow khuyên dùng:

1. setup project một lần
2. chạy `project-health` khi repo thay đổi đáng kể
3. chạy `project-work` cho task không nhỏ
4. để AI làm việc từ root của repo
5. để AI dùng `.ai-dev-system/` như nguồn memory, routing, và task context

Ví dụ prompt:

- `Đọc project context và sửa lỗi checkout này.`
- `Dùng current task brief và cập nhật flow xử lý lỗi API.`
- `Review repo này theo đúng project conventions trước khi đề xuất thay đổi.`

## Hành Vi Mặc Định Của CLI

Khi `ai-dev-system/` nằm trong project, `ai-dev` sẽ tự coi thư mục cha của nó là project hiện tại.

Vì vậy các lệnh sau chạy được mà không cần truyền path:

```bash
./ai-dev-system/bin/ai-dev project-setup all
./ai-dev-system/bin/ai-dev project-work "fix checkout voucher bug"
./ai-dev-system/bin/ai-dev project-status
```

Bạn vẫn có thể truyền path rõ ràng nếu muốn, nhưng không còn bắt buộc trong flow dùng thường ngày.

## Project Sẽ Được Sinh Ra Những Gì

Mỗi project sau khi được khởi tạo sẽ có một lớp project-aware trong `.ai-dev-system/`:

- `project-manifest.json`
- `project-memory.json`
- `custom-skill-index.json`
- `project-profile.md`
- `project-commands.md`
- `project-architecture.md`
- `project-conventions.md`
- `project-customizations.md`
- `project-routing.md`
- `current-task-brief.md`
- `skills/`

Đây là lớp giúp hệ thống hiểu repo của bạn thay vì hành xử như một assistant generic.

## Các Lệnh Nên Dùng

Lệnh dùng hằng ngày:

```bash
./ai-dev-system/bin/ai-dev project-setup all
./ai-dev-system/bin/ai-dev project-work "mô tả task"
./ai-dev-system/bin/ai-dev project-health
./ai-dev-system/bin/ai-dev project-status
```

Lệnh hữu ích cho project:

```bash
./ai-dev-system/bin/ai-dev update-project-memory
./ai-dev-system/bin/ai-dev update-docs-from-source
./ai-dev-system/bin/ai-dev project-doc-health
./ai-dev-system/bin/ai-dev project-dedupe-report
./ai-dev-system/bin/ai-dev save-session "checkout bugfix" "chạy lại verify sau khi sửa logic pricing"
./ai-dev-system/bin/ai-dev resume-session
./ai-dev-system/bin/ai-dev scaffold-project-skill "domain rules" "Business rules riêng của flow checkout"
```

Lệnh cấp hệ thống:

```bash
./ai-dev-system/bin/ai-dev doctor
./ai-dev-system/bin/ai-dev registry-health
./ai-dev-system/bin/ai-dev system-refresh
./ai-dev-system/bin/ai-dev portable-release
./ai-dev-system/bin/ai-dev search-skill "database migration"
./ai-dev-system/bin/ai-dev search-role "security review"
./ai-dev-system/bin/ai-dev search-workflow "verify"
./ai-dev-system/bin/ai-dev freeze-sources
```

## Mô Hình Upstream Portable

Trên máy nguồn, nơi bạn giữ các repo upstream tham chiếu, bạn có thể refresh và curate cả hệ thống bằng một lệnh:

```bash
./ai-dev-system/bin/ai-dev system-refresh
```

Khi muốn chuẩn bị một bản portable mới để copy sang project khác hoặc phát hành nội bộ, dùng:

```bash
./ai-dev-system/bin/ai-dev portable-release
```

Lệnh này sẽ:

- refresh registry
- chạy eval routing
- freeze source metadata
- chạy doctor

Thực tế sử dụng:

- máy nguồn: giữ `ai-repos/`, curate, refresh, freeze
- project thật: chỉ copy `ai-dev-system/`

## Những Mặc Định Quan Trọng

Hệ thống hiện đã được tối ưu quanh vài nguyên tắc chính:

- phản hồi cùng ngôn ngữ với người dùng
- ưu tiên project context trước generic skills
- chỉ chọn bộ skill, role, workflow nhỏ nhất nhưng đủ dùng
- sau khi compact context sẽ tự dựng lại goal, plan, touched files, verify, risks
- vẫn giữ được trace upstream mà không phải kéo cả source repos vào từng project

## Role Và Workflow Đang Có

Role files nằm trong [ai-dev-system/team-dev/roles](ai-dev-system/team-dev/roles).

Các nhóm role hiện có:

- `orchestrator`
- `explorer`
- `architect`
- `tech-lead`
- `project-planner`
- `product-manager`
- `frontend-engineer`
- `frontend-specialist`
- `backend-engineer`
- `backend-specialist`
- `database-architect`
- `qa-engineer`
- `qa-automation`
- `reviewer`
- `security-auditor`
- `security-reviewer`
- `devops-engineer`
- `code-archaeologist`
- `a11y-architect`
- `e2e-runner`
- `build-error-resolver`
- `doc-updater`
- `code-explorer`
- `code-reviewer`
- `performance-optimizer`
- `debugger`
- `documentation-writer`
- `mobile-developer`

Tham khảo thêm cách chọn role tại [AGENT_SELECTION.md](ai-dev-system/team-dev/orchestration/AGENT_SELECTION.md).

## Chiến Lược Thu Thập Upstream

Hệ thống đi theo hướng `ECC-first`, nhưng không khóa cứng mọi thứ vào một nguồn duy nhất.

Ý tưởng hiện tại:

- upstream ưu tiên: `ai-repos/everything-claude-code`
- nguồn bổ sung: `openai-skills`, `antigravity-kit`, `agent-skills`
- catalog lớn chủ yếu dùng để discovery, không phải active core mặc định
- project-local skill vẫn được phép thêm khi repo có domain rules riêng

Các bổ sung theo hướng ECC đã được tích hợp gồm:

- task skills: `accessibility`, `e2e-testing`
- roles: `a11y-architect`, `e2e-runner`, `code-explorer`, `code-reviewer`, `doc-updater`, `build-error-resolver`
- upgraded roles: `project-planner`, `performance-optimizer`
- workflows: `code-review`, `update-docs`, `build-fix`, `test-coverage`

Rule này nằm ở [source-strategy.json](ai-dev-system/shared/registry/source-strategy.json).

## Bảo Trì Trên Máy Nguồn

Đây là các lệnh dành chủ yếu cho máy đang giữ `ai-repos/` và làm nhiệm vụ curate hệ thống:

```bash
./ai-dev-system/bin/ai-dev system-refresh
./ai-dev-system/bin/ai-dev portable-release
./ai-dev-system/bin/ai-dev doctor
```

Thư mục `scripts/` ở root chỉ là bộ công cụ tiện ích để bảo trì repo nguồn. Nó không cần thiết trong các bản copy sang project.

Không còn wrapper script top-level bắt buộc nữa. Mọi thứ portable nằm trong `ai-dev-system/`, còn maintenance helper tập trung trong `scripts/`.

Xem thêm [scripts/README.md](scripts/README.md) để phân biệt nhanh đâu là phần dành cho máy nguồn và đâu là phần để mang sang project.

## Cấu Trúc Repo

```text
.ai-system/
├── ai-dev-system/
│   ├── AI_ENTRY.md
│   ├── bin/ai-dev
│   ├── solo-dev/
│   ├── team-dev/
│   ├── shared/
│   └── packs/
├── ai-repos/
└── scripts/
```

Entry points chính:

- [AI_ENTRY.md](ai-dev-system/AI_ENTRY.md)
- [AI_DEV.md](ai-dev-system/solo-dev/AI_DEV.md)
- [AI_TEAM.md](ai-dev-system/team-dev/AI_TEAM.md)
- [ai-dev](ai-dev-system/bin/ai-dev)

## Hướng Dẫn Public Repo

Thường an toàn để public:

- `ai-dev-system/`
- `README.md`
- `README_VI.md`
- `.gitignore`
- các script maintenance ở root, nếu không chứa secret

Thường không nên public:

- `ai-repos/`
- các bản `.ai-dev-system/` sinh ra cho project riêng có chứa thông tin nghiệp vụ
- session history, task brief tạm, hoặc project memory riêng
- bất kỳ file nào chứa secret, token, internal URL, hoặc kiến trúc riêng của khách hàng

Cách public an toàn nhất:

- public phần reusable của hệ thống
- giữ các upstream clone ở local
- giữ private các project-generated context trừ khi bạn cố ý curate lại để chia sẻ

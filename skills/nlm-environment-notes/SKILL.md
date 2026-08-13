---
name: nlm-environment-notes
description: >
  Supplementary environment and troubleshooting notes for the `nlm` CLI/MCP
  tool (jacob-bd/gemini-notebook-mcp-cli), covering the gotchas that only show
  up in real use: Cowork sandbox constraints, the correct MCP tool name
  pattern, the difference between the MCP-registered library and your full
  Google account, and multi-profile switching. This is a companion to the
  tool's own official guide, not a replacement — install `nlm skill install`
  first for the current, authoritative reference. Use this skill when a user
  reports that `nlm` MCP tools return empty results, notebooks aren't found,
  or the CLI works in a terminal but not inside Cowork.
---

# NotebookLM CLI/MCP — Environment Notes

이 문서는 [`jacob-bd/gemini-notebook-mcp-cli`](https://github.com/jacob-bd/gemini-notebook-mcp-cli)(`nlm`)를 실제로 운영하며 겪은 시행착오를 정리한 보충 자료입니다. **원작자의 공식 가이드를 대체하지 않습니다.** 설치 직후 `nlm skill install`로 최신 공식 가이드를 먼저 받고, 이 문서는 그 위에 추가로 참고하세요.

## Cowork 환경 — 가장 먼저 부딪히는 문제

**Claude Code CLI(터미널/IDE)**: `nlm`이 Bash로 직접 실행됩니다. 별도 조치가 필요 없습니다.

```bash
nlm notebook list --profile <profile>
```

**Cowork(Claude Desktop 샌드박스)**: `nlm` 바이너리는 Mac에 설치돼 있지만, Cowork의 샌드박스는 그 바이너리에 직접 접근하지 못합니다. Desktop Commander 같은 "호스트 셸 실행" 도구를 거쳐야 합니다.

```python
# 샌드박스 안에서 직접 실행하면 "command not found"로 실패한다
# 호스트 셸을 거치는 도구로 실행해야 한다
start_process(
    command="zsh -c 'source ~/.zshrc 2>/dev/null; nlm notebook list --profile <profile>'",
    timeout_ms=30000
)
```

## MCP 도구 이름 패턴 (검증됨)

Cowork에서 올바른 MCP 도구 접두어는 `mcp__notebooklm__*`입니다. `mcp__notebooklm-mcp__*`가 아닙니다. 이름이 비슷해 보여 툴 탐색 시 혼동하기 쉽습니다.

## MCP 라이브러리 ≠ Google 계정 전체 (중요)

`list_notebooks` 계열 MCP 도구는 **MCP 라이브러리에 등록된 노트북만** 반환합니다. Google 계정에 있는 전체 노트북이 아닙니다. "찾는 노트북이 안 보인다"는 문제는 대부분 이 차이에서 옵니다.

**전체 접근 워크플로:**

```
1단계 — CLI로 실제 노트북 목록 확인
  → nlm notebook list --profile <profile>
  → ID와 제목이 포함된 전체 목록 반환

2단계 — 대상 노트북을 MCP 라이브러리에 등록
  → add_notebook(url, name, description, topics)
  → ⚠️ description과 topics는 둘 다 필수 필드

3단계 — 이제 MCP로 조회
  → ask_question(notebook_id, question)
```

`add_notebook`을 호출할 때 `description`이나 `topics` 중 하나라도 빠지면 검증 오류가 납니다.

## 여러 Google 계정 전환 (프로필)

MCP 서버는 **현재 활성 기본 프로필** 하나만 사용합니다. 계정을 바꾸려면:

```bash
# 1) 등록된 프로필 전체 확인 — 이름이 드리프트하거나 무효한 항목이 섞여 있을 수 있어
#    표나 기억에 의존하지 말고 매번 확인한다
nlm login profile list

# 2) 목표 프로필로 전환
nlm login switch <profile-name>

# 3) 이제 MCP 도구가 새 계정을 사용한다 — 재시작 불필요
```

**노트북이 어느 프로필 소속인지 모를 때:** 유효한 프로필을 하나씩 시도한다. `PERMISSION_DENIED`는 잘못된 프로필, 성공하면 그 프로필이 정답이다.

```bash
nlm notebook get <uuid> --profile <profile-a> 2>&1
nlm notebook get <uuid> --profile <profile-b> 2>&1
```

## Notes ≠ Sources

Notes는 사용자가 NotebookLM 세션 안에서 직접 쓴 메모이고, Sources는 노트북이 읽어들인 문서입니다. 서로 완전히 다른 개체입니다.

- `nlm note list <nb-id>` — 테이블 미리보기(내용 잘림)
- `nlm note list <nb-id> --json` — 전체 내용(제목 + 본문) 반환. 메모 내용을 읽어야 한다면 항상 이 플래그를 쓴다.
- 목록에는 타임스탬프가 없어 CLI만으로는 최신순 정렬이 안 된다. "최종"이라는 제목이나 목록 마지막 위치가 보통 최신이다.

## 세션·인증

- 세션 수명은 약 20분. 명령이 인증 오류로 실패하기 시작하면 `nlm login`을 다시 실행한다.
- 생성·삭제 계열 명령은 전부 `--confirm`(또는 `-y`)이 필요하다.
- 삭제는 되돌릴 수 없다. 실행 전 항상 사용자에게 확인받는다.

## 자주 겪는 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| "Cookies have expired" | 세션 만료 | `nlm login` 재실행 |
| "Notebook not found" (MCP) | MCP 라이브러리에 미등록 | CLI로 ID 확인 후 `add_notebook`으로 등록 |
| `add_notebook` 검증 오류 | `description`/`topics` 누락 | 둘 다 채워서 재시도 |
| `PERMISSION_DENIED` (notebook get) | 다른 프로필 소속 | `nlm login profile list` 후 프로필별로 재시도 |
| Notes가 비어 보임 | `--json` 없이 조회 | `--json` 추가 (테이블 뷰는 미리보기만 반환) |
| "nlm: command not found" (Cowork) | 샌드박스에서 직접 실행 | Desktop Commander 등 호스트 셸 실행 도구 사용 |

## 이 문서가 다루지 않는 것

전체 명령어 목록, 콘텐츠 생성(Studio) 옵션, 소스 추가 방법 등은 원작자의 공식 가이드(`nlm skill install` 또는 [저장소 문서](https://github.com/jacob-bd/gemini-notebook-mcp-cli))를 참고하세요. 이 문서는 공식 가이드에 없는, 실제 운영 중에만 드러나는 환경 문제만 다룹니다.

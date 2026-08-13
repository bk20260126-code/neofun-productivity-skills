# NeoFun Productivity Skills

NeoFun이 실제로 운영하며 검증한 생산성 스킬 2종과, 함께 쓰면 좋은 검증된 외부 스킬 2종을 소개하는 저장소입니다.

이 저장소는 **NeoFun이 직접 작성한 스킬만** 파일로 담습니다. 외부 스킬은 파일을 복제하거나 재배포하지 않고 원작자의 공식 배포 위치로만 연결합니다.

## NeoFun 제공 스킬

| 스킬 | 무엇을 할 수 있나요? | 경로 |
|---|---|---|
| Cowork Best Practice | Claude Cowork 워크스페이스의 `CLAUDE.md`·`MEMORY.md` 설계, 파일 분류 규칙, 워크스테이션 vs 스킬 판단, Claude Projects 이전을 다루는 공식 SOP | [`skills/cowork-best-practice`](skills/cowork-best-practice) |
| YouTube to Playbook | 유튜브 영상의 자막(없으면 화면 OCR)을 분석해 실행 프롬프트·판단 기준·주의사항이 정리된 Playbook 문서로 변환 | [`skills/youtube-to-playbook`](skills/youtube-to-playbook) |

## 함께 쓰면 좋은 외부 스킬 (링크만 제공)

| 스킬 | 무엇을 할 수 있나요? | 원본 |
|---|---|---|
| Visual Plan | 코딩 에이전트의 계획을 다이어그램·파일트리·와이어프레임이 포함된 리뷰 가능한 `plan.html`로 만듭니다 | [BuilderIO/skills — visual-plan](https://github.com/BuilderIO/skills/tree/main/skills/visual-plan) |
| Claude Video /watch | 영상의 자막과 프레임을 추출해 화면과 음성을 함께 분석합니다 | [bradautomates/claude-video](https://github.com/bradautomates/claude-video) |

## 설치 방법

**NeoFun 제공 스킬**: 저장소를 클론하거나 원하는 스킬 폴더를 다운로드해 사용 중인 에이전트의 스킬 디렉터리(`~/.claude/skills/`, `~/.codex/skills/`, `~/.agents/skills/` 등)에 복사합니다.

```bash
git clone https://github.com/bk20260126-code/neofun-productivity-skills.git
cp -r neofun-productivity-skills/skills/cowork-best-practice ~/.claude/skills/
cp -r neofun-productivity-skills/skills/youtube-to-playbook ~/.claude/skills/
```

**외부 스킬**: 위 표의 원본 링크를 열어 원작자의 최신 설치 안내를 따릅니다.

## 요구사항

- Cowork Best Practice: 별도 설치 불필요, Claude Code / Cowork 환경에서 바로 사용
- YouTube to Playbook: `yt-dlp`, `python3` (자막 없는 영상은 `video-ocr-transcribe` 스킬 별도 필요)

## 라이선스

`skills/` 아래 NeoFun 제공 스킬 2종은 [MIT License](LICENSE)입니다. 표에 링크만 있는 외부 스킬은 이 라이선스의 적용을 받지 않으며, 각 원본 저장소의 라이선스를 따릅니다.

## 운영 원칙

- NeoFun은 외부 스킬을 복제·수정·재배포하지 않습니다.
- 링크가 변경되면 원본을 다시 확인한 뒤 갱신합니다.
- 이슈·개선 제안은 이 저장소의 GitHub Issues로 남겨주세요.

---

NeoFun · AI와 비즈니스, 시스템으로 완성하는 새로운 즐거움

Community: https://geekus.kr/neofun

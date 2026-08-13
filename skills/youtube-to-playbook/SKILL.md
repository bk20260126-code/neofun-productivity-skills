---
name: youtube-to-playbook
description: >
  Convert a YouTube video into a structured, actionable Playbook by extracting
  all on-screen prompts, frameworks, examples, and key concepts from its transcript.
  Use this skill when the user provides a YouTube URL and wants a Playbook, guide,
  reference doc, or structured summary — especially when they say "유튜브 내용으로
  플레이북 만들어줘", "이 영상 내용을 정리해줘", "영상에서 나온 프롬프트/예시 다 담아줘",
  "turn this video into a playbook", "extract prompts from this video", or provides
  an existing draft and asks to enhance it with on-screen examples.
  Also triggers when user provides a URL + an existing incomplete doc and asks to
  "complete it with what's shown on screen."
---

# YouTube → Playbook 변환 스킬

## 전체 파이프라인 (5단계)

---

### STEP 0 — 사전 확인 (30초, 절대 건너뛰지 말 것)

작업 시작 전 반드시 아래 두 가지를 확인한다.

**① 출력 형식 확인**
사용자가 원하는 결과물이 무엇인지 명확히 한다:
- Playbook (섹션별 프롬프트 + 설명 + 예시 포함)
- 요약 (핵심 개념만)
- 카드뉴스용 슬라이드 초안
- 기존 초안 보강 (사용자가 초안을 이미 제공한 경우)

**② 언어 방향 확인**
영상이 영어여도 출력은 한국어로 할지, 영어로 할지 확인한다.
사용자가 명시하지 않으면: **영상 언어와 무관하게 사용자와 대화한 언어로 출력**한다.

---

### STEP 1 — 영상 진단 (자막 존재 여부)

```bash
yt-dlp --list-subs "<YOUTUBE_URL>" 2>&1 | grep -E "(en|ko|ja|zh)" | head -20
```

**결과에 따른 분기:**

| 상황 | 처리 방식 |
|------|-----------|
| 자막 있음 (자동 포함) | → STEP 2A (자막 다운로드) |
| 자막 없음 | → STEP 2B (OCR 파이프라인, `video-ocr-transcribe` 스킬 참고) |

> 자막이 있으면 절대 OCR을 시도하지 않는다. 자막이 훨씬 정확하고 빠르다.

---

### STEP 2A — 자막 다운로드 및 클린 텍스트 추출

**다운로드:**
```bash
mkdir -p /tmp/yt_playbook/<VIDEO_ID>
yt-dlp --write-auto-subs --sub-lang en-orig --sub-format vtt \
  --skip-download -o "/tmp/yt_playbook/<VIDEO_ID>/video" "<YOUTUBE_URL>"
```

언어 우선순위: `en-orig` → `en` → `ko` → 기타 (원본 언어 우선)

**VTT → 타임스탬프 보존 클린 텍스트 변환:**
```bash
python3 scripts/vtt_to_timestamped.py \
  /tmp/yt_playbook/<VIDEO_ID>/video.en-orig.vtt \
  /tmp/yt_playbook/<VIDEO_ID>/transcript_ts.txt
```

> 타임스탬프를 반드시 보존한다. Playbook의 `[MM:SS]` 링크 검증에 사용된다.

---

### STEP 2B — 자막 없음: OCR 파이프라인

`video-ocr-transcribe` 스킬의 파이프라인을 사용한다:
```bash
/path/to/video-ocr-transcribe/scripts/transcribe.sh \
  "<YOUTUBE_URL>" /tmp/yt_playbook/<VIDEO_ID> "ko,en" 1
```

---

### STEP 3 — 트랜스크립트 분석 및 구조 추출

트랜스크립트를 읽은 후 다음 4가지 레이어로 분리해서 추출한다:

**레이어 1 — 구조 (Structure)**
- 영상의 섹션/챕터 구분
- 각 섹션의 핵심 주장 한 줄 요약

**레이어 2 — 실행 프롬프트 (Actionable Prompts)**
- 화자가 "type this", "use this prompt", "say this to Claude" 등으로 명시한 프롬프트
- 화면에 코드블록/텍스트박스로 표시된 입력값
- 인용문으로 제시된 예시 문장

**레이어 3 — 판단 기준 / 프레임워크 (Decision Frameworks)**
- if/then 조건 ("if X, do Y")
- 체크리스트, 단계별 프로세스
- 2×2 매트릭스, 필터 기준

**레이어 4 — 주의사항 / Gotchas**
- "avoid", "don't", "careful", "trap", "pitfall", "주의" 관련 내용
- 예외 상황, 엣지 케이스

---

### STEP 4 — Playbook 작성

**기본 구조:**

```markdown
# [영상 제목] — Playbook
> 출처: [URL] | 작성일: [DATE]

## [섹션 1 제목] [[MM:SS](링크)]

**핵심 개념:** 한 줄 요약

### 왜 써야 하는가?
(레이어 1 내용)

### 실전 프롬프트
\`\`\`
(레이어 2 내용 — 복사해서 바로 쓸 수 있도록)
\`\`\`

### 판단 기준
(레이어 3 내용 — 표 또는 체크리스트)

### ⚠️ Gotchas
(레이어 4 내용)

---
[다음 섹션 반복]

## 요약 테이블
| # | 프레이즈/개념 | 언제 쓰는가 | 핵심 프롬프트 한 줄 |
```

**기존 초안이 제공된 경우:**
- 기존 초안의 구조를 기준으로 삼는다
- 초안에 없는 프롬프트/예시/Gotchas를 `[레이어 2~4]`에서 추출해 보강한다
- 기존 내용을 삭제하거나 대체하지 않고 **추가**만 한다
- 보강된 항목에는 `(영상 원문 추가)` 태그를 붙이지 않아도 되나, 구조적으로 구분되어야 한다

---

### STEP 5 — 완성도 검증 (절대 건너뛰지 말 것)

Playbook 작성 후 아래 체크리스트를 실행한다:

```
□ 영상의 모든 섹션/챕터가 Playbook에 대응되는가?
□ 화자가 "type this" / "use this" 로 명시한 프롬프트가 전부 포함되었는가?
□ 판단 기준(if/then, 체크리스트)이 누락 없이 수록되었는가?
□ Gotchas/주의사항이 최소 1개 이상 각 섹션에 있는가?
□ 타임스탬프 링크가 정확한가? (트랜스크립트 ts 파일과 대조)
□ 실전 프롬프트가 코드블록 안에 있어 복사-붙여넣기가 바로 가능한가?
□ 출력 언어가 사용자 요청과 일치하는가?
```

누락 발견 시 → 해당 섹션으로 돌아가 보강 후 재검증.

---

## Gotchas

- **자막 언어 선택 실수:** `en` 대신 `en-orig`를 써야 원본 음성 기반 자막이 나온다. 자동 번역 자막(`en`이 번역본인 경우)을 받으면 왜곡 발생.
- **VTT 타임스탬프 제거 금지:** 타임스탬프를 버리면 Playbook의 `[MM:SS]` 링크 생성이 불가능해지고, 누락 검증도 할 수 없다. 반드시 `transcript_ts.txt`에 보존한다.
- **구술 내용 vs 온스크린 텍스트 혼동:** 화자가 말로 설명한 개념과 화면에 직접 띄운 프롬프트는 다르다. 화면 프롬프트(코드블록, 타이핑 시연)는 레이어 2에, 설명은 레이어 1에 분류한다.
- **기존 초안 덮어쓰기 금지:** 사용자가 초안을 제공했다면 그 구조가 의도된 것이다. 대체하지 말고 보강만 한다.
- **80/20 함정:** 트랜스크립트 일부만 읽고 Playbook을 쓰면 후반부 핵심 프롬프트를 놓친다. 반드시 전체를 읽어야 한다.
- **언어 가정 금지:** 영상이 영어라고 자동으로 영어 출력하지 않는다. 사용자가 한국어로 요청했으면 한국어로 출력한다.
- **자막 없는 영상에 STEP 2A 적용 금지:** 자막이 없는데 VTT 다운로드를 시도하면 빈 파일이나 오류가 발생한다. 반드시 STEP 1 진단 후 분기한다.

---

## 번들 스크립트

- `scripts/vtt_to_timestamped.py` — VTT를 타임스탬프 보존 클린 텍스트로 변환.

---

## 요구사항

- macOS / Linux: `yt-dlp`, `python3`
- Windows: WSL 권장

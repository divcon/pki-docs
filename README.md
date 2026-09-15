# PKI 설계 문서

C2PA 적용 설계와 Root Key 관련 설계·작업 내용을 관리하는 문서 저장소다. 주제별 디렉터리의 README에서 문서 범위와 현재 상태를 확인한다.

## 문서 안내

| 디렉터리 | 내용 | 시작 문서 |
|---|---|---|
| `c2pa-design/` | C2PA 인증서 발급·관리, 단말 연동과 보안 운영에 관한 기존 설계·검토 문서 | [C2PA 설계 문서](c2pa-design/README.md) |
| `root-key-design/` | Root Key 관련 작업을 위한 공간. 작업 범위와 방식은 진행하면서 정한다. | [Root Key 설계](root-key-design/README.md) |
| `references/` | 공식 자료의 출처, 버전과 로컬 확보 방법 | [원문 자료 목록](references/sources.md) |

## 디렉터리 구조

```text
./
├── README.md
├── AGENTS.md
├── .gitignore
├── c2pa-design/
│   ├── README.md
│   └── ...                       # 기존 설계 문서와 하위 디렉터리
├── root-key-design/
│   └── README.md
├── references/
│   └── sources.md
├── specifications/               # 공식 자료 로컬 사본, Git 제외
├── conformance-public/           # 공식 자료 로컬 사본, Git 제외
├── rfc3161.txt                    # 공식 자료 로컬 사본, Git 제외
└── rfc5816.txt                    # 공식 자료 로컬 사본, Git 제외
```

## 원문 자료와 작성 기준

공식 자료의 로컬 사본은 Git에 포함하지 않는다. 새 환경에서는 [원문 자료 목록](references/sources.md)에 따라 자료를 확보하고, 각 설계 문서에 명시된 원문 버전·commit·조항을 확인한다.

설계 문서와 원문 목록은 프로젝트 산출물이다. 요구사항과 사실을 검증할 때는 공식 원문을 확인하고, 표준 요구와 프로젝트 설계 선택을 구분한다. 세부 작성·검색 규칙은 [AGENTS.md](AGENTS.md)를 따른다.

## 기존 경로와 기록

기존 `architecture/`는 `c2pa-design/`으로 이름을 변경했다. 문서의 내부 디렉터리 구성은 유지한다.

과거 감사 기록, `tmp/`의 작업 프롬프트와 ZIP 사본에는 작성 당시의 `architecture/` 경로가 남아 있다. 당시 경로·해시·감사 결과는 과거 기록으로 보존하며, 현재 파일은 같은 하위 경로의 `c2pa-design/`에서 찾는다. ZIP은 생성 당시의 사본이므로 현재 문서 탐색과 수정은 Markdown 파일을 기준으로 한다.

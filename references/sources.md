# 원문 자료 목록

공식 자료의 출처, 로컬 위치와 확보 방법을 기록한다. 이 목록은 프로젝트가 작성한 안내이며, 요구사항이나 사실의 근거는 연결된 원문에서 확인한다.

## 기본 자료의 기준 버전

2026-09-15 KST에 확인한 checkout과 파일을 기록했다. 아래 commit은 로컬 자료의 식별 정보이며 모든 설계 문서의 기준을 하나로 통일한다는 뜻은 아니다. 문서가 별도 commit을 지정하면 해당 commit의 원문을 확인한다.

| 자료 | 공식 출처 | 프로젝트 루트 기준 로컬 위치 | 확인한 버전·commit |
|---|---|---|---|
| C2PA Specifications | [c2pa-org/specifications](https://github.com/c2pa-org/specifications) | `specifications/` | `9c58c8c27044e44e8601f6ab13f1bcac1376eb1f`; 기존 C2PA 설계는 2.4 문서를 참조 |
| C2PA Conformance 공개 자료 | [c2pa-org/conformance-public](https://github.com/c2pa-org/conformance-public) | `conformance-public/` | `2466172859fad1215f7aaf7e3768b41a0ac29abc`; `docs/v0.2/` 문서와 인증서 프로파일 |
| RFC 3161 | [RFC Editor 원문](https://www.rfc-editor.org/rfc/rfc3161.txt) | `rfc3161.txt` | RFC 3161 |
| RFC 5816 | [RFC Editor 원문](https://www.rfc-editor.org/rfc/rfc5816.txt) | `rfc5816.txt` | RFC 5816 |

네 로컬 경로는 루트 `.gitignore`로 제외되어 있다. 원문 사본을 수정하더라도 이 문서 저장소에는 변경이 기록되지 않는다. 근거를 확인할 때는 checkout의 줄바꿈 변환이나 로컬 수정과 구분하여 지정 commit의 원문을 확인한다.

## 새 환경에서 확보하기

아래 명령은 대상 디렉터리와 RFC 파일이 없는 새 환경에서 프로젝트 루트를 기준으로 실행한다. 기존 로컬 사본이 있으면 먼저 현재 상태를 확인한다.

```sh
gh repo clone c2pa-org/specifications specifications
git -C specifications switch --detach 9c58c8c27044e44e8601f6ab13f1bcac1376eb1f

gh repo clone c2pa-org/conformance-public conformance-public
git -C conformance-public switch --detach 2466172859fad1215f7aaf7e3768b41a0ac29abc

curl --fail --location --output rfc3161.txt https://www.rfc-editor.org/rfc/rfc3161.txt
curl --fail --location --output rfc5816.txt https://www.rfc-editor.org/rfc/rfc5816.txt
```

GitHub CLI 사용 시에는 프로젝트에 적용되는 실행 권한 지침을 따른다.

기존 설계가 참조하는 `specifications/build/site/specifications/2.4/`의 문서는 위 Specifications commit에 포함되어 있다. 다른 버전으로 바꾸는 경우에는 인용 경로와 문서별 근거 버전도 함께 확인한다.

2026-09-15에 확인한 로컬 RFC 파일의 SHA-256은 다음과 같다.

```text
39fd17644ff2d654bc83814a78b1c5b5e7517f496741f34ead5064943eb98240  rfc3161.txt
9a3eba6ecf14afc7820c51034a608d54d188344a43e9189b0e023d4a6a98f649  rfc5816.txt
```

## 2026-10-11 로컬 세팅

위 기본 자료를 지정 commit과 경로에 확보했다. Specifications의 `build/site/specifications/2.4/specs/C2PA_Specification.html`도 확인했다. 두 저장소는 detached HEAD이며 원문 사본을 열람하는 데 별도 빌드가 필요하지 않다.

Root Key 추가 자료는 아래 경로에 보관한다. 상세 출처와 기존 검토 범위는 [Root Key 원문 목록](root-key-sources.md), 실제 취득 URL·시각·SHA-256·Git commit은 [다운로드 명세](download-manifest.json)에 기록했다. 다운로드 명세는 취득 기록이며 사실 판단의 근거는 각 원문이다.

| 자료 | 프로젝트 루트 기준 로컬 위치 | 확보 기준 |
|---|---|---|
| Root Key 검토용 Conformance | `references/local/conformance-public-7b2fcb3/` | `7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50`; 기본 저장소의 별도 Git worktree |
| RFC 5280·6960·6024·9124 | `references/local/rfc/` | RFC Editor의 `.txt` 원문 |
| NIST SP 800-57 Part 1 Rev.5·FIPS 204 | `references/local/nist/` | 원문 PDF 2개와 FIPS 204 소개 페이지 |
| TUF specification 1.0.36 | `references/local/tuf-specification/tuf-spec.md` | 공식 `v1.0.36` tag, commit `59e601ed29c0d2e497264ae8b31c11b8ef07df1e` |
| AWS CloudHSM·중국 리전 서비스 목록 | `references/local/aws/` | 2026-10-11 취득 HTML 8개 |
| EJBCA·Microsoft AD CS·OpenSSL ca | `references/local/products/` | 2026-10-11 취득 HTML 3개 |

`references/local/`도 루트 `.gitignore`로 제외한다. 총 20개의 개별 다운로드 파일을 보관하며, Git 저장소와 worktree의 파일은 이 수에 포함하지 않는다. 기존 목록에 SHA-256이 기록된 RFC 2개와 Conformance 6개 파일은 모두 일치했다.

웹 문서는 취득 시점의 HTML 사본이다. CSS·이미지·스크립트 및 동적으로 불러오는 데이터까지 모두 보관한 오프라인 사이트는 아니며, 과거 조사 시점의 내용과 동일하다고 간주하지 않는다. TUF는 변경될 수 있는 `latest` 대신 기존 조사 버전 1.0.36을 고정했다.

기본 저장소를 확보한 다음, 추가 Git 자료는 프로젝트 루트에서 다음과 같이 재확보한다. 대상 경로가 없는 새 환경용 명령이다.

```sh
mkdir -p references/local
git -C conformance-public worktree add --detach \
  ../references/local/conformance-public-7b2fcb3 \
  7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50

git clone https://github.com/theupdateframework/specification.git \
  references/local/tuf-specification
git -C references/local/tuf-specification switch --detach \
  59e601ed29c0d2e497264ae8b31c11b8ef07df1e
```

개별 다운로드는 `download-manifest.json`의 `downloaded_files`에 있는 `source_url`에서 `path`로 받는다. 부모 디렉터리를 먼저 만들고 기존 파일은 덮어쓰기 전에 확인한다. 동적 웹 문서의 재다운로드 결과는 기존 해시와 달라질 수 있으므로 새 취득 시각과 해시를 별도로 기록한다. 별도 Conformance worktree는 `conformance-public/.git`에 의존하므로 단독 Git clone으로 취급하지 않는다.

## 자료 추가와 인용

- 새로운 자료는 제목, 공식 URL, 버전·commit 또는 발행일, 로컬 위치와 확인일을 기록한다.
- 파일 바이트를 고정해야 하는 검증에는 SHA-256도 기록한다.
- 구체적인 요구사항의 조항과 적용 이유는 해당 설계 문서에 연결한다.
- C2PA 설계에서 사용하는 추가 RFC·provider 자료는 각 상세 문서의 원문 목록을 따른다.
- Root Key 작업의 기준 자료와 검토 이력은 [Root Key 원문 목록](root-key-sources.md)에 기록한다.

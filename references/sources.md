# 원문 자료 목록

공식 자료의 출처, 로컬 위치와 확보 방법을 기록한다. 이 목록은 프로젝트가 작성한 안내이며, 요구사항이나 사실의 근거는 연결된 원문에서 확인한다.

## 현재 로컬 자료

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

## 자료 추가와 인용

- 새로운 자료는 제목, 공식 URL, 버전·commit 또는 발행일, 로컬 위치와 확인일을 기록한다.
- 파일 바이트를 고정해야 하는 검증에는 SHA-256도 기록한다.
- 구체적인 요구사항의 조항과 적용 이유는 해당 설계 문서에 연결한다.
- C2PA 설계에서 사용하는 추가 RFC·provider 자료는 각 상세 문서의 원문 목록을 따른다.
- Root Key 작업의 기준 자료는 범위와 방식이 정해진 뒤 추가한다.

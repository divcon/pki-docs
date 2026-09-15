# C2PA 설계 문서

이 디렉터리는 C2PA 적용을 위해 작성한 설계·검토 문서를 모은다. 주요 대상은 Claim Signing 인증서와 TSA 인증서를 발급·관리하는 Certificate Platform이며, 외부 단말과의 연동, 인증서 발급 요청, 보안 운영과 적합성 검토를 함께 다룬다.

처음 읽는 경우 [Overview](Overview.md)에서 전체 범위와 책임을 확인한 뒤, 아래 안내에 따라 필요한 문서로 이동한다.

## 다루는 범위

- Certificate Platform의 시스템 경계, 구성요소와 신뢰 모델
- Claim Signing·TSA 인증서 발급 요청, 인증 방식, CSR과 검증 증거
- 인증서 발급·상태 관리·폐기와 CA 보안 운영
- 외부 Generator Product·On-Device TSA와의 연동 및 수용 기준
- 요구사항 추적, 적합성 검토, 시험과 구현 로드맵

외부 단말의 콘텐츠 서명과 타임스탬프 생성은 발급 인증서를 사용하는 외부 시스템과의 연동 범위로 다룬다. 현재 설계에서 Certificate Platform이 제공하는 기능은 인증서 발급과 상태 관리다.

## 문서 구성

| 문서 | 역할 |
|---|---|
| [Overview](Overview.md) | 설계 대상, 전체 구조, 책임과 주요 결정의 출발점 |
| [01 — Architecture Foundation](01-Architecture-Foundation.md) | 시스템 경계, 컴포넌트 책임, 신뢰 모델과 공통 설계 기준 |
| [02 — Certificate Enrollment](02-Certificate-Enrollment.md) | C2PA 인증서 발급 요구를 구현 항목별로 설명하는 가이드 |
| [03 — On-Device Runtime](03-On-Device-Runtime.md) | 외부 Generator Product와 On-Device TSA의 동작·연동 수용 기준 |
| [04 — Security and Operations](04-Security-and-Operations.md) | CA 구성, 키·인증서 수명주기, 상태 서비스와 보안 운영 |
| [05 — Conformance and Roadmap](05-Conformance-and-Roadmap.md) | 요구사항 추적, 적합성·시험·구현 순서와 배포 판정을 위한 목차 초안 |
| [Claim Signing 발급 요청 문서](claim-signing-enrollment-request/README.md) | 인증 방식, 요청 본문, CSR·Dynamic Evidence, 서버 검증과 미결정 사항 |
| [TSA Leaf 발급 요청 문서](tsa-leaf-enrollment-request/README.md) | 기본 발급 요청 계약, CSR, 선택적 Attestation 확장과 서버 검증 |
| [부록](appendix/) | 주제별 설계·검토 자료와 원문 참조 목록 |

Claim Signing과 TSA 발급 요청의 세부 내용을 확인할 때는 각 문서 묶음의 README에서 시작한다. 해당 README가 안내하는 상세 문서, 정정 사항과 감사 기록을 함께 확인한다. Claim Signing 요청 문서 묶음은 요청 본문과 검증을 다루며, endpoint·response·state 등 일반 API 계약 전체를 정의하지 않는다.

## 권장 읽는 순서

1. **전체 설계 파악:** Overview → 01 → 02 순서로 시스템 범위와 발급 흐름을 읽는다.
2. **발급 요청 검토:** 필요한 인증서 종류에 따라 Claim Signing 또는 TSA Leaf 문서 묶음으로 이동한다.
3. **연동·운영 검토:** 03에서 외부 단말과의 연동 기준을, 04에서 CA와 인증서 운영을 확인한다.
4. **구현·검증 준비:** 05와 각 상세 문서의 미결정 사항·시험·승인 조건을 확인한다.

## 문서 상태와 근거 확인

이 문서들은 설계·검토 산출물이며, 상세 설계 초안과 목차 초안이 함께 있다. 문서의 존재만으로 구현이나 운영 준비가 완료됐음을 뜻하지 않는다. 사용할 때는 각 문서에 적힌 상태, 정정 이력, `TBD`와 승인 조건을 확인한다. 부록도 개별 문서의 초안·대체 여부를 확인한 뒤 사용한다.

[프로젝트 작성 지침](../AGENTS.md)에 따라 다음 원칙을 적용한다.

- `c2pa-design/`와 `root-key-design/` 하위 문서는 프로젝트 산출물이다. 표준·규격·사실 확인의 독립적인 근거로 사용하지 않는다.
- 자료 조사와 요구사항 검증에는 두 설계 디렉터리 외부의 공식 C2PA 자료, RFC, 공식 schema와 provider 원문을 사용한다.
- 기존 산출물은 새 문서 작성과 일관성 검토에 참고하되, 표준 요구와 프로젝트 설계 선택을 구분하고 관련 주장은 외부 원문으로 다시 확인한다.
- 근거를 확인할 때는 세부 문서가 지정한 원문의 버전·commit·조항을 확인한다.

[Source References](appendix/Source-References.md)는 문서 탐색을 위한 원문 목록 안내다. 이 안내 자체를 사실 근거로 인용하지 않고 외부 원문을 확인한다.

프로젝트 루트의 `specifications/`, `conformance-public/`, `rfc3161.txt`, `rfc5816.txt`는 공식 자료의 로컬 사본이며 `.gitignore`로 제외되어 있다. 새 환경의 자료 확보 방법은 [원문 자료 목록](../references/sources.md)을 확인하고, 세부 문서의 출처와 버전에 맞는 자료를 사용한다.

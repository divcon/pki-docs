# C2PA Claim Signing Certificate 인증·Enrollment 요구사항 조사 Goal

이 문서 전체를 하나의 실행 지시로 취급한다. 아래 완료 조건이 모두 충족될 때까지 조사, 수정, 검증과 독립 감사 루프를 계속한다.

## 1. Goal objective

C2PA Manifest/Claim 서명용 인증서의 **인증 방식과 enrollment 요구사항**을 원문 기준으로 전수조사한다. Enrollment request body에 필요한 값, 발급 전 server gate, onboarding/out-of-band 검증, runtime/operations 의무를 분리한 구현 가능한 아키텍처 문서를 작성한다.

HTTP endpoint, URL, response schema, transaction/state machine, idempotency, retry, stable error code와 일반적인 API 설계는 범위에서 제외한다. API와 관련해 설계하는 것은 profile·operation별 **enrollment request body의 필드, 형식, cardinality와 검증 근거**뿐이다.

기존 아키텍처의 관련 과잉·누락·모순을 함께 바로잡고, 서로 독립적인 세 서브에이전트가 같은 최종 파일 집합을 검사해 모든 심각도에서 `NO FINDINGS`를 보고할 때만 완료한다.

### 1.1 Goal 실행과 상태 전이

1. 조정 에이전트는 먼저 현재 Goal 상태를 확인한다.
2. unfinished Goal이 없거나 이전 Goal이 complete이면 이 문서의 objective를 참조하는 새 Goal을 생성한다. 사용자가 명시적인 예산을 주지 않았다면 `token_budget`을 설정하지 않는다.
3. 동일 objective의 Goal이 이미 active이면 새 Goal을 중첩 생성하지 않고 기존 Goal을 계속한다.
4. 다른 unfinished Goal이 있으면 덮어쓰지 말고 사용자에게 어느 Goal을 계속할지 확인한다.
5. 아래 완료 조건을 모두 만족한 뒤에만 Goal을 `complete`로 갱신한다.
6. 어렵거나 오래 걸리고 finding이 남았다는 이유로 `blocked` 처리하지 않는다.
7. 같은 외부 blocker가 세 번의 연속 Goal turn에서 반복되고 안전한 in-scope 대안을 모두 소진한 경우에만 Goal 시스템 규칙에 따라 `blocked`로 갱신한다.

## 2. 용어와 범위

1. “Manifest Signing Certificate”가 원문의 공식 용어인지 확인한다.
2. 원문이 `C2PA Claim Signing Certificate`를 사용한다면 이를 규범적 명칭으로 사용하고 사용자 표현과의 관계는 README에서 한 번 설명한다.
3. Claim Signing Leaf의 `INITIAL`, `REKEY`, `RENEWAL` 또는 원문이 실제로 정의한 동등 수명주기를 조사한다. 원문에 없는 operation 이름은 프로젝트 request-body 구분자라고 표시한다.
4. AL1과 AL2를 독립적으로 조사하며 한 Assurance Level의 요구를 다른 level로 전이하지 않는다.
5. TSA Leaf 요구나 기존 TSA 아키텍처를 Claim Signing 요구의 근거로 사용하거나 그대로 전이하지 않는다.
6. 인증 방식은 Subscriber I/A/V, Applicant Representative 권한, Subscriber Agreement, secure enrollment credential, Generator Product instance authentication, CSR PoP와 AL2 attestation trust를 서로 다른 predicate로 분석한다.

## 3. 절대 준수할 근거 규칙

1. `/mnt/c/Users/sungj/IdeaProjects/c2pa/architecture/**`는 프로젝트 산출물이며 표준·규격·사실의 근거로 사용하지 않는다.
2. `architecture/**`는 새 산출물 작성과 기존 산출물 일관성 감사 대상으로만 사용한다. 그 안의 주장은 외부 원문으로 재검증한다.
3. `architecture/appendix/**`, 경로나 파일명에 `appendix` 또는 `부록`이 포함된 자료는 검색·열람·인용·수정에서 제외한다.
4. 검색할 때 가능한 명령에 `-g '!architecture/**'` 또는 동등한 제외를 적용한다. 아키텍처 일관성 감사에서만 선정한 비부록 파일을 연다.
5. 권위 근거는 우선 다음 로컬 원문이다.
   - `conformance-public/docs/v0.2/C2PA Certificate Policy.md`
   - `conformance-public/docs/v0.2/C2PA Conformance Program.md`
   - `conformance-public/docs/v0.2/C2PA Generator Product Security Requirements.md`
   - `conformance-public/docs/v0.2/C2PA Generator Product Security Architecture Document Template.md`
   - `conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.*`
   - `conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.*`
   - `conformance-public/schemas/conforming-products/conforming-products-list.schema.json`
   - `conformance-public/schemas/conforming-products/Companion Guide for the C2PA Conforming Products List.md`
   - `conformance-public/schemas/mib/oid.txt`
   - `specifications/`의 C2PA Content Credentials 및 Security Considerations 원문
   - 저장소의 RFC 2986, RFC 5280 및 직접 관련 RFC
6. 로컬 원문이 없거나 불완전할 때만 공식 C2PA/RFC primary source를 조회한다. Provider 자료는 공식 기술 규격만 사용하고 `PROVIDER` authority로 한정한다. 원격 원문은 정확한 bytes를 `/tmp`에 고정하고 URL, version/조회일과 SHA-256을 source manifest에 기록한다.
7. 조사 시작 시 사용한 source commit, 문서 version과 schema hash를 기록한다. Dirty working tree는 기준으로 조용히 채택하지 않고 원문 저장소도 수정하지 않는다.
8. 모든 규범 주장에는 정확한 로컬 `파일:줄` 또는 공식 원격 URL+version/조회일+section/page/anchor를 붙인다.
9. 원문이 정하지 않은 JSON wrapper나 request-body field를 C2PA 필수라고 쓰지 않는다. HTTP endpoint, response, state, idempotency, retry와 오류 체계는 설계하지 않는다.

## 4. 요구사항 분류

모든 항목을 다음 독립 축으로 분류한다.

### 4.1 적용 시점

| 분류 | 의미 |
|---|---|
| `WIRE` | enrollment request body 또는 인증 transport에 실제 제공되는 값 |
| `ISSUANCE-GATE` | 발급 전에 서버가 확인하지만 같은 request body field일 필요는 없는 조건 |
| `ONBOARDING` | Subscriber I/A/V, 계약, CPL/Conformance 승인 등 별도 절차에서 충족 가능한 조건 |
| `RUNTIME` | 발급 전후 제품 구현과 운영에서 계속 유지해야 하는 조건 |

### 4.2 정의 주체

| 분류 | 의미 |
|---|---|
| `C2PA` | C2PA 원문이 정의 |
| `RFC` | 적용 RFC가 정의 |
| `CA-CPS` | CA의 공개 business practices/CPS가 정의 |
| `PROJECT` | 이 프로젝트가 선택한 request-body wrapper 또는 강화정책 |
| `PROVIDER` | attestation/platform provider 규격 또는 계약이 정의 |

### 4.3 규범 modality

| 분류 | 의미 |
|---|---|
| `REQUIRED` | 적용 범위에서 SHALL/MUST |
| `PROHIBITED` | SHALL NOT/MUST NOT |
| `RECOMMENDED` | SHOULD/SHOULD NOT |
| `PERMITTED` | MAY/OPTIONAL |
| `NON-BCP14-OBLIGATION` | lowercase 등 비-BCP 14 문장에 표현된 의무 |
| `NOT-SPECIFIED` | 조사한 원문이 정하지 않음 |

원문의 대문자/소문자와 부정형을 보존하고 문서의 BCP 14 적용 선언에 따라 분류한다.

### 4.4 적용 profile

`BASE`, `AL1`, `AL2`, GSPR implementation class 또는 `PROFILE-CONDITIONAL`을 별도 축으로 기록한다.

### 4.5 검증·집행 지점

| 분류 | 의미 |
|---|---|
| `REQUEST-BODY-VALIDATION` | request body의 field, 형식, cardinality와 profile 조합을 검증 |
| `ISSUANCE-EXPLICIT` | CA가 서명·발급 직전에 request와 최신 권위 상태를 재검사 |
| `ONBOARDING-REUSABLE` | onboarding/주기 심사 결과를 보관하고 발급 시 승인·유효기간·상태를 참조 |
| `OPERATIONS-DECISION` | CA/CPS, security, PKI 또는 product 운영 주체가 허용 범위 안의 방식·주기·provider를 결정 |
| `RUNTIME-ENFORCED` | 제품 secure boundary 또는 서비스 runtime이 지속 강제하고 시험·감사로 확인 |

`WIRE`와 `REQUEST-BODY-VALIDATION`은 동의어가 아니다. 예를 들어 credential은 transport에 있을 수 있고 Subscriber/CPL currentness는 server-authoritative state다.

다음 두 표를 반드시 별도로 만든다.

1. **Operations Decision Register**
   - decision ID와 결정할 정책
   - C2PA/RFC가 고정한 범위와 운영자가 선택할 범위
   - owner/approver와 CPS·정책·설정의 권위 저장소
   - status `APPROVED` 또는 `TBD`; 근거 없는 default 금지
   - `TBD`의 production-blocking profile/runtime, 해결 조건과 interim fail-closed 동작
   - 검토 주기, 변경 trigger, rollout/rollback과 audit evidence
   - 영향을 받는 request validation, issuance gate 또는 runtime control
2. **Enrollment Request Body Matrix**
   - `INITIAL`/`REKEY`/`RENEWAL`, AL1/AL2 조합
   - request body field와 정확한 cardinality/format
   - C2PA semantic requirement와 project wrapper의 구분
   - server-authoritative 값과의 binding predicate
   - 정의 주체, modality와 원문 locator 또는 project decision ID

Request-body 표에는 URL, HTTP method/status, response, transaction state, idempotency, retry 또는 stable error를 넣지 않는다.

운영 결정이 `TBD`이면 영향을 받는 production profile/runtime 경로를 비활성화한다. 한 항목이 제품 의무라는 이유만으로 증명 artifact를 `WIRE`로 올리지 않고, 원문이 instance Dynamic Evidence를 요구하면 설계 검토만으로 대체하지 않는다.

## 5. 반드시 답할 질문

`INITIAL`, `REKEY`, `RENEWAL`과 AL1/AL2 조합별로 다음을 답한다.

1. Enrollment request body에 필요한 CSR, Evidence와 식별자는 무엇인가?
2. Secure access credential은 request body 밖에서 어떻게 적용되며 무엇을 인증해야 하는가?
3. Subscriber I/A/V, representative authority, Agreement, GP instance authentication과 key-pair ownership/PoP는 어떻게 구분되고 언제 재검사되는가?
4. Generator Product의 Conformance, CPL record, Notice, status, DN과 Max Assurance Level은 어느 단계에서 검증하는가?
5. Static conformance evidence와 instance Dynamic Evidence를 어떻게 구분하는가?
6. AL1/AL2의 C2PA semantic Dynamic Evidence predicate는 무엇인가? Provider artifact 수와 project JSON cardinality를 별도 열로 둔다.
7. Operation별 freshness/replay 요구의 규범 출처는 무엇인가?
8. GSPR O.1~O.6의 implementation requirement, static evidence, Dynamic Evidence, 대안과 implementation class는 무엇인가?
9. Evidence signer/trust chain, audience, freshness, Generator Product, Subscriber, requested AL과 CSR SPKI는 어떻게 결속하는가?
10. 위 결속 중 C2PA, provider, CA CPS와 project request-body 선택은 각각 무엇인가?
11. Key 생성 위치, non-exportability, hardware root of trust, signing boundary와 용도 제한은 어느 적용 시점에 속하는가?
12. PKCS#10 CSR signature/PoP, Subject DN, SPKI, extension request와 AL1/AL2 schema 차이는 무엇인가?
13. 최종 Leaf의 EKU, KU, Basic Constraints, policy/OID, AL, CPL ID, validity, AIA/CRL/OCSP 요구는 무엇인가?
14. REKEY와 RENEWAL, 새 key, 동일 SPKI 재사용, 구·신 인증서 동시 유효성, revocation/cutover 관계는 무엇인가?
15. AL/profile downgrade, upgrade와 migration을 원문이 규정하는가?
16. Request body로 확정 가능한 값과 onboarding/server state/runtime 또는 clarification으로 남길 값은 무엇인가?
17. CA/CPS·PKI/security/product 운영자가 결정할 인증 방식, 알고리즘, validity/rotation, re-authentication, provider/trust/reference, retention/audit와 revocation/incident 정책은 무엇인가?

## 6. 작성 및 수정할 산출물

`architecture/claim-signing-enrollment-request/`에 다음 파일을 작성한다.

1. `README.md`
   - 공식 용어와 범위
   - 인증 방식 계층과 핵심 결론
   - AL1/AL2 × INITIAL/REKEY/RENEWAL 비교표
   - `WIRE`/`ISSUANCE-GATE`/`ONBOARDING`/`RUNTIME` 분류표
   - 주요 원문 locator와 미확정 사항
2. `01-Enrollment-Request-Body.md`
   - operation/profile별 request body 예시
   - field별 cardinality, 형식, authority와 source classification
   - Enrollment Request Body Matrix
   - C2PA 필수 의미와 project JSON wrapper의 구분
   - endpoint/response/state/idempotency/retry/error 설계는 포함하지 않음
3. `02-CSR-and-Dynamic-Evidence-Requirements.md`
   - AL1/AL2 CSR profile과 PoP
   - Dynamic Evidence, GSPR O.1~O.6와 instance binding
   - freshness/audience/replay와 subject-key binding
   - static/dynamic/runtime evidence 경계
4. `03-Server-Validation-Traceability-and-Gaps.md`
   - 인증·enrollment fail-closed validation 순서
   - 요구사항→원문→request/issuance/runtime check traceability
   - Operations Decision Register와 enforcement traceability
   - 표준 미규정 항목과 local gap ID
   - 기존 아키텍처 관련 과잉·누락·모순 처리
5. `04-Subagent-Audit-Resolution.md`
   - 감사 라운드, finding, 근거, 조치와 폐쇄 상태
   - scope 변경 전 API 설계 finding은 현재 요구로 유지하지 않음

조사 결과와 모순되는 경우 다음 비부록 문서도 필요한 범위에서만 수정한다.

- `architecture/Overview.md`
- `architecture/01-Architecture-Foundation.md`
- `architecture/02-Certificate-Enrollment.md`
- `architecture/03-On-Device-Runtime.md`
- `architecture/04-Security-and-Operations.md`
- `architecture/05-Conformance-and-Roadmap.md`

사용자 변경과 task 밖 파일을 보존한다. 시작 baseline과 실제 수정 allowlist를 기록하며 appendix는 내용을 열지 않고 name/state만 비교한다. 모든 Markdown 수정은 `apply_patch`로 수행한다.

## 7. Request body 작성 원칙

1. C2PA가 JSON schema를 정하지 않았다면 모든 wrapper field를 `PROJECT`로 표시한다.
2. 서버가 보유한 onboarding/CPL/Subscriber 원자료를 body에 복제하지 않고 필요한 opaque reference만 둔다.
3. CSR PoP와 attestation의 platform/key property를 혼동하지 않는다.
4. C2PA semantic Evidence, provider artifact 수와 project `evidenceItems` cardinality를 분리한다.
5. Profile별 optional/required field가 모순되지 않게 한다.
6. Challenge 등 서버 응답 설계는 하지 않는다. Freshness 입력이 필요하면 provider-signed artifact 안에서 검증해야 하는 의미와 미결정 정책만 기술한다.
7. REKEY/RENEWAL의 새 key, fresh Evidence와 identity currentness를 원문과 project 정책으로 분리한다.
8. 발급 가능 여부, certificate status와 runtime authorization을 합치지 않는다.
9. 운영 decision은 request field 또는 issuance/runtime predicate로 역추적한다.
10. URL, HTTP method/status, response object, transaction/state machine, idempotency, retry와 stable error model을 만들지 않는다.

## 8. 독립 서브에이전트 감사

메인 에이전트만 파일을 수정한다. 감사자는 read-only이며 서로의 결론을 근거로 사용하지 않는다. 최소 세 역할을 병렬로 사용한다.

### 8.1 Standards auditor

- architecture 외 pinned 원문만으로 용어, AL1/AL2, Dynamic Evidence, GSPR O.1~O.6, CPL, I/A/V, re-key와 certificate profile을 확인한다.
- TSA 또는 project policy가 Claim Signing C2PA 요구로 잘못 전이됐는지 찾는다.

### 8.2 Enrollment/security auditor

- Subscriber/representative/Agreement/GP-instance/PoP/attestation trust의 인증 경계를 검토한다.
- Request body의 field·cardinality·binding과 issuance/runtime gate가 과잉 또는 누락 없이 연결되는지 확인한다.
- Evidence freshness/replay/audience/key binding, downgrade/migration과 same-key reuse를 검토한다.
- Endpoint, response, state, idempotency, retry/error 설계가 남아 있으면 scope violation으로 보고한다.

### 8.3 Coverage/consistency auditor

- 신규 5개와 수정한 비부록 architecture 문서의 cardinality, 용어와 요구 시점을 비교한다.
- Decision ID가 request/issuance/runtime enforcement에 연결되는지 확인한다.
- Gap ID, source locator, local link/fragment와 ZIP entry/hash를 검증한다.

Finding은 severity, 정확한 `파일:줄`, basis(`EXTERNAL-NORMATIVE`, `PROJECT-CONTRACT`, `MECHANICAL`), 재현 설명과 최소 수정 방향을 포함한다. 근거 없는 취향 제안은 수용하지 않는다.

## 9. 피드백 폐쇄 루프

1. 초안과 관련 아키텍처 정정을 완료한다.
2. `architecture/claim-signing-enrollment-request.zip`에 예상한 5개 Markdown만 넣고 byte-for-byte 비교한다.
3. 신규 5개, 실제 수정한 기존 비부록 문서, ZIP과 pinned source identity를 포함한 allowlist를 확정한다.
4. 정렬된 path/source identity+SHA-256 manifest를 `/tmp`에 만들고 그 SHA-256을 snapshot ID로 사용한다.
5. 세 감사자에게 같은 snapshot을 주고 병렬 실행하며 감사 중 대상 파일과 ZIP을 수정하지 않는다.
6. 결과 회수 후 snapshot을 재계산해 하나라도 다르면 verdict를 폐기한다.
7. Finding을 근거로 재검증하고 유효한 항목을 수정해 resolution register에 기록한다.
8. Link/anchor, semantic evidence/cardinality와 decision↔enforcement를 다시 검사하고 ZIP을 재생성한다.
9. 마지막 변경 뒤 새 snapshot에서 세 감사자를 모두 다시 실행한다.
10. 모든 severity가 0이고 세 감사자가 같은 snapshot에 정확히 `NO FINDINGS`를 보고할 때만 종료한다.
11. 최종 무지적 감사 뒤에는 감사 대상 파일이나 ZIP을 수정하지 않는다.

## 10. 기계적 검증

1. 시작 baseline, 종료 allowlist와 사용자 변경 보존 비교
2. 신규 폴더의 예상 파일 5개와 예상 밖 파일 부재
3. 모든 local Markdown link target과 fragment 유효성
4. AL1/AL2 × operation별 semantic Evidence, provider artifact 수와 project cardinality 전수 검사
5. Operations Decision Register와 request/issuance/runtime enforcement의 양방향 누락 검사
6. 각 `TBD`의 owner, 해결 조건, blocking scope와 fail-closed 누락 검사
7. Enrollment Request Body Matrix의 operation/profile/field/cardinality/source 누락 검사
8. Endpoint/response/state/idempotency/retry/stable-error 설계가 신규 문서에 남지 않았는지 검사
9. `architecture/**`가 권위 source로 사용되지 않았는지 검사
10. appendix 제외 경로와 외부 원문 저장소가 baseline 대비 바뀌지 않았는지 확인
11. ZIP entry allowlist와 각 Markdown byte 일치
12. 최종 감사 전후 source/artifact snapshot ID 일치

## 11. 완료 조건

- 공식 용어와 source identity가 기록됨
- 인증 방식이 I/A/V, Agreement, secure credential, GP-instance auth, CSR PoP와 AL2 attestation trust로 분리됨
- AL1/AL2 × INITIAL/REKEY/RENEWAL 매트릭스가 원문 근거와 함께 완성됨
- Request body, issuance, onboarding과 runtime 경계가 일관됨
- Operations Decision Register와 request/issuance/runtime enforcement traceability가 완성됨
- 모든 `TBD`에 owner/해결 조건/blocking scope와 fail-closed가 있음
- C2PA semantic Evidence, provider artifact 수, project request cardinality와 freshness가 혼동되지 않음
- Endpoint/response/state/idempotency/retry/error 설계가 신규 문서에 없음
- 신규 5개와 필요한 기존 비부록 수정이 완료됨
- 모든 finding이 `PASS/CLOSED`이고 같은 최종 snapshot의 세 감사가 `NO FINDINGS`
- Local link/anchor와 ZIP 검사가 통과함
- Appendix와 외부 원문 저장소를 수정하지 않음

자료가 없어 규범 판단이 불가능하면 프로젝트 정책으로 추측하지 않고 missing source와 영향 범위를 기록한다.

## 12. 최종 보고 형식

1. 공식 용어와 핵심 인증·enrollment 결론
2. AL1/AL2 × operation별 CSR, Evidence와 request-body cardinality
3. `WIRE`/`ISSUANCE-GATE`/`ONBOARDING`/`RUNTIME` 경계
4. Operations Decision의 `APPROVED`/`TBD`와 blocking 상태
5. 생성·수정한 파일
6. 감사 라운드별 finding과 조치
7. 최종 snapshot, severity, link/anchor와 ZIP 검증
8. 남은 clarification 또는 외부 의존성

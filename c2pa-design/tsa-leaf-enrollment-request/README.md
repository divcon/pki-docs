# TSA Leaf 발급 요청 전수조사 — 원문 근거 재정리

> 상태: 2026-09-02 source-bound correction  
> 사실 근거: `conformance-public/`, `specifications/`, RFC 및 공식 schema  
> 제외: `c2pa-design/**`를 표준·사실 근거로 사용하지 않음. `c2pa-design/appendix/**`는 검색·열람·인용하지 않음.

## 1. 결론

TSA Leaf 발급 API를 호출할 때마다 Compound Evidence, TSA application의 TEE 실행 증거, timestamp-only ACL 증거 또는 single-active-key 증거를 제출해야 한다는 C2PA 요구는 확인되지 않았다.

C2PA Certificate Policy v0.2가 요구하는 것은 다음과 같이 나뉜다.

| 구분 | 원문상 요구 | 적용 gate | 매 API 요청에 동봉하는 wire evidence인가? |
|---|---|---|---|
| 안전한 enrollment credential | CA가 secure access credential을 요구 | enrollment request 인증 | credential은 요청에 제시. 구체 형식은 business practices/API가 정함 |
| 발급 대상 key pair 소유 확인 | CA가 key ownership을 확인. signed CSR 또는 KMS inspection은 예시 | 발급 대상 key마다 확인 | 반드시 payload일 필요는 없음. 이 architecture는 CSR payload를 선택 |
| TSA 신청자 검증 | TSA certificate issuance는 CA business practices의 identification/authentication/verification을 따름 | issuance 판단 | 아니오. onboarding/사전 심사 등 business practices가 절차를 정함 |
| TSA Leaf profile | Subject, SPKI, KU/EKU/policy 등 공식 profile 준수 | CSR/발급 결과 검증 | 아니오. 요청 증거가 아니라 발급 profile gate |
| TSA app의 TEE 실행 | On-Device TSA runtime/구현 요구 | runtime/implementation acceptance | 아니오 |
| TSU key의 TEE 내 생성·보관 | On-Device TSA runtime/구현 요구 | runtime/implementation acceptance | 아니오 |
| timestamp 전용 key | TSA runtime/운영 요구 | runtime/operations acceptance | 아니오 |
| TSU당 single active key | TSA runtime/운영 요구 | runtime/operations acceptance | 아니오 |
| Compound Evidence | TSA enrollment 요구로 정의되지 않음 | optional CPS profile에서만 | 아니오 |

따라서 기본 TSA Leaf enrollment는 다음처럼 정리한다.

```text
승인 TSA operator/service 확인
  → secure credential로 enrollment 요청
  → 발급 대상 key pair 소유 확인
     (이 설계에서는 DER PKCS#10 CSR 사용)
  → TSA CSR/profile 및 CA business-practices 검증
  → TSA Leaf 발급
```

Compound Evidence를 추가하려면 C2PA 필수 요건이 아니라 CA가 명시적으로 채택한 **선택적 CPS/provider 확장 profile**이어야 한다. 그 profile을 선택한 transaction에서만 challenge, Evidence, `x5chain`, key binding 및 provider trust 검증을 필수로 한다. 기본 TSA profile에는 `attestationEvidence`가 없다.

## 2. 운영 요구를 어떻게 입증하는가

TEE 실행, TEE key confinement, timestamp-only 사용 및 single-active-key는 다음 통제의 조합으로 충족할 수 있다.

- TEE/TA 설계와 보안 경계 검토
- key 생성·export 금지·operation ACL의 구현 통제
- TSU key state machine과 rotation 절차
- conformance/security 시험 및 negative test
- TSA practices/CPS와 운영 절차
- 배포 승인, 변경관리, 모니터링 및 감사

원문은 이 사실들을 certificate enrollment request 안의 서명된 Evidence로 매번 관찰하라고 규정하지 않는다. 다만 CA가 위험 모델상 원격 attestation을 추가 통제로 채택할 수는 있으며, 그 경우에도 “C2PA가 요구”한다고 표기하면 안 된다.

## 3. INITIAL과 REKEY

| 항목 | INITIAL | REKEY |
|---|---|---|
| secure enrollment credential | 필수 | 필수 |
| TSA applicant/operator I/A/V | CA business practices에 따라 필수 | 신규 신청과 동일한 identity validation |
| key ownership | 필수 | 새 key에 대해 필수 |
| CSR | 이 architecture가 선택한 기본 PoP 방식 | 새 key의 새 CSR을 쓰는 project policy |
| TSA CSR/profile 검증 | 필수 | 필수 |
| Compound Evidence | 기본 profile에는 없음 | 기본 profile에는 없음 |
| optional CPS attestation profile | 명시적으로 선택한 경우만 | 명시적으로 선택한 경우만 |

CP는 re-key 요청을 신규 신청과 동일한 identity validation으로 처리하라고 하지만, 이를 “항상 fresh Compound Evidence 제출”로 확장하지 않는다.

## 4. 원문 발췌 위치

| 판단 | 원문 위치 | 내용 |
|---|---|---|
| Dynamic Evidence의 범위 | `C2PA Certificate Policy.md:134-138` | Generator Product가 C2PA Claim Signing Certificate를 자동 enrollment할 때 평가하는 속성으로 정의 |
| enrollment credential/key ownership | 같은 문서 `:469-473` | secure credential과 key-pair ownership 확인. signed CSR/KMS inspection은 예시 |
| re-key | 같은 문서 `:479-481` | 신규 인증서 신청과 동일한 identity validation |
| TSA certificate issuance | 같은 문서 `:511-519` | CA business practices의 I/A/V 절차를 따름 |
| Dynamic Evidence 결과 | 같은 문서 `:521-529` | Max Assurance Level의 Generator Product와 Claim Signing Certificate에 적용 |
| dedicated/single-active key | 같은 문서 `:915-927` | TSA/TSU 운영 요구 |
| TEE app/key | 같은 문서 `:933-939` | On-Device TSA runtime 요구 |
| TSA Leaf profile | 같은 문서 `:1334` 이후 | 인증서 형식·extension 요구 |
| AL2 Evidence | 같은 문서 `:1684` 이후 | Conforming GP/Claim Generator의 automated enrollment 요구 |
| TSA-only conformance application | `C2PA Conformance Program.md:406` 부근 | TSA-only application은 받지 않음 |
| TSA Trust List intake | 같은 문서 `:416-422` | TSA root/intermediate record 취급이며 TSA Leaf wire가 아님 |

`specifications/build/site/specifications/2.4`에서 certificate enrollment를 전수 검색한 결과도 자동 evidence enrollment는 Claim Generator/Claim Signing Certificate 문맥이었다. Content Credentials의 timestamp 절은 RFC 3161 timestamp 생성·검증과 TSA trust anchor를 다루며 TSA Leaf enrollment payload를 정하지 않는다.

공식 `tsaLeaf.csr.schema.json`과 `tsaLeaf.cert.schema.json`에도 attestation, Compound Evidence, challenge, TEE, ACL 또는 active-key count 필드는 없다.

## 5. 문서 구성

CSR Subject의 구조·C/O/CN 검사와 TSA 운영기관·서비스의 식별·인증·권한 확인은 [02 §2.1](02-CSR-and-Attestation-Requirements.md#21-subject)에서 분리한다. Subject 또는 별도 신청·등록정보를 사용하는 방식과 DN 차이 처리는 CA 절차가 정한다. 모든 CSR에 등록 TSA DN 일치를 요구하거나 임의 Subject를 무조건 수락하는 공통 규칙으로 일반화하지 않는다.

- [01-Enrollment-Request-Contract.md](01-Enrollment-Request-Contract.md): 기본 TSA API와 선택적 확장 경계
- [02-CSR-and-Attestation-Requirements.md](02-CSR-and-Attestation-Requirements.md): CSR 필수 범위와 optional attestation 규칙
- [03-Server-Validation-Traceability-and-Gaps.md](03-Server-Validation-Traceability-and-Gaps.md): 서버 validation gate, 원문 추적, 정정된 gap 분류
- [04-Subagent-Audit-Resolution.md](04-Subagent-Audit-Resolution.md): 이전 결론의 철회 및 감사 결과

## 6. 외부 원문

- [C2PA Certificate Policy v0.2](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
- [C2PA Conformance Program v0.2](../../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md)
- [C2PA Governance Framework v0.2](../../conformance-public/docs/v0.2/C2PA%20Governance%20Framework.md)
- [C2PA Generator Product Security Requirements v0.2](../../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md)
- [TSA Leaf CSR schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json)
- [TSA Leaf certificate schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json)
- [RFC 2986 — PKCS #10](https://www.rfc-editor.org/rfc/rfc2986.html)
- [RFC 3161 — Time-Stamp Protocol](https://www.rfc-editor.org/rfc/rfc3161.html)
- [RFC 5280 — PKIX Certificate Profile](https://www.rfc-editor.org/rfc/rfc5280.html)

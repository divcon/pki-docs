# TSA Leaf 서버 검증·추적성·미결정 사항

## 1. 기본 TSA profile의 발급 전 검증

아래 검증은 모두 통과한 뒤 TSA Issuing CA/HSM을 호출한다.

1. secure credential, caller identity와 TSA operator/service 권한
2. transaction ownership, environment/profile/operation 및 project idempotency
3. CA business practices가 정한 TSA applicant identification/authentication/verification. CSR Subject, 별도 신청정보 또는 인증된 등록정보 중 선택한 정보로 서비스와 요청자 권한을 확인
4. key-pair ownership: 기본 구현은 CSR signature 검증
5. strict DER PKCS#10 parsing, algorithm/SPKI/Subject 구조·C/O/CN/requested-extension 검증. CSR DN 차이는 [02 §2.1](02-CSR-and-Attestation-Requirements.md#21-subject)의 절차로 처리
6. official `tsaLeaf.csr.schema.json` 검증([02 §2.3의 필수 확장 표](02-CSR-and-Attestation-Requirements.md#23-requested-extensions) 참조)
7. CA-controlled TSA Leaf template, issuer/HSM authorization 및 serial/key uniqueness
8. 발급 결과의 signature, CSR-SPKI 일치 및 official `tsaLeaf.cert.schema.json` post-check
9. certificate/result/audit record의 원자적 저장

다음 항목은 기본 submission validation gate가 아니다.

- Compound Evidence의 존재
- TEE/TA measurement, boot/debug/patch claim
- timestamp-only ACL의 signed observation
- active-key count 또는 `old/new/staged` 증거
- activation receipt/finalization token

위 artifact 자체는 optional이다. 별도 acceptance와 운영 통제에서 반드시 보증할 대상은 그 밑의 On-Device TSA runtime/implementation 속성, 즉 TEE 실행, TEE 내 key 생성·보관, timestamp 전용 사용과 single-active-key다.

## 2. 선택적 attestation profile의 조건부 gate

transaction이 승인된 `c2pa-on-device-tsa-attested-*` profile을 명시적으로 선택한 경우에만 기본 gate 사이에 다음 검증을 추가한다.

1. Evidence field의 required role/cardinality와 size/format
2. provider profile/version 및 signed bytes
3. signer trust path, status, signature와 current Reference Value
4. challenge/audience/transaction freshness
5. Evidence subject key와 CSR SPKI 결속
6. profile이 정의한 TA/TEE claims 및 compound-evidence join

이 profile에서 Evidence가 없거나 검증 결과가 unknown이면 fail-closed 한다. 이 gate를 기본 TSA profile에 적용하거나 C2PA 공통 요구라고 표기하지 않는다.

## 3. 운영/구현 acceptance

TSA 서비스가 production에서 timestamp를 발행하기 전에는 다음을 별도로 검증해야 한다.

- On-Device TSA application이 TEE에서 실행되는가
- TSU signing key가 TEE에서 생성·보관되고 export되지 않는가
- key가 timestamp 전용 operation으로 제한되는가
- TSU당 한 시점에 active signing key가 하나뿐인가
- UTC(k) traceability, declared accuracy, drift-stop, leap-second 및 24시간 sync-attempt 정책이 구현됐는가
- rotation/recovery가 위 불변조건을 깨지 않는가

허용 가능한 evidence source는 설계/코드 검토, TEE security mechanism, conformance/negative test, release artifact, TSA practices/CPS, 운영 journal/monitoring/audit 등이다. 원격 attestation은 선택 가능한 한 방법이지 원문이 지정한 유일한 방법이 아니다.

## 4. 발급 거부 조건

### 4.1 기본 profile

- credential 또는 TSA operator/service authorization 실패
- applicant I/A/V 실패
- transaction/profile/operation/current-certificate binding 실패
- key ownership 또는 CSR signature 실패
- malformed/unsupported CSR, Subject 구조·필수 C/O/CN 실패 또는 SPKI/extension profile 불일치
- CA의 식별·불일치 처리 절차를 적용해도 TSA 서비스·권한 또는 제출정보의 정확성을 확인할 수 없음. CSR Subject와 등록 DN의 차이만을 공통 자동 거부 조건으로 삼지 않음
- issuer/HSM/template/status/serial/key-uniqueness 실패
- post-issuance certificate profile self-check 실패
- 감사/저장 원자성을 보장할 수 없는 오류

### 4.2 선택적 profile에만 추가

- Evidence 누락/초과/unknown type 또는 version
- signature/path/status/freshness 실패
- challenge/audience/transaction mismatch
- Evidence subject key와 CSR SPKI mismatch
- provider-specific TA/TEE predicate 또는 compound join 실패

기본 profile에서 “active-key signed observation 없음”이나 “TEE Evidence 없음”만으로 인증서 발급을 거부하는 것은 C2PA 근거가 없다.

Subject 검증에서는 필수 C/O/CN 누락·PoP 실패, Subject 조회로 대상을 확인하지 못한 경우, 별도 서비스 ID로 대상을 확인한 경우의 문서화된 DN 차이 처리, 다른 운영자의 서비스 요청 및 최종 Subject의 서비스 불일치를 구분한다. 별도 식별정보가 있다는 이유만으로 의미상 충돌을 무시하거나 잘못된 원본 CSR의 서명을 유효하게 취급하지 않는다. 이는 향후 검증 조건이며 실행한 테스트 결과가 아니다.

## 5. INITIAL과 REKEY validation

| 검증 | INITIAL | REKEY |
|---|---|---|
| secure credential/I/A/V | 적용 | 신규 신청과 동일하게 적용 |
| key ownership | 적용 | 새 key에 적용 |
| CSR/profile | 적용 | 새 CSR/profile에 적용 |
| current certificate binding | 없음 | project policy로 적용 |
| Compound Evidence | base에는 없음 | base에는 없음 |
| optional profile Evidence | 그 profile을 선택한 경우만 | 그 profile을 선택한 경우만 |

## 6. `TSA-REQ-GAP-01~17`의 의미와 정정된 범위

이 ID들은 C2PA 요구사항 번호가 아니다. 이전 architecture 초안에서 구현 미결정 사항을 임시로 추적하기 위해 만든 **로컬 gap ID**다.

| ID | 뜻 | 정정된 영향 |
|---|---|---|
| `01` | OpenAPI/JSON Schema, strict parse/idempotency/state contract | project API production blocker |
| `02` | TSU slot request/response와 server-owned identifier | 해당 project API 기능 blocker |
| `03` | TSA 식별정보 출처·요청자 권한 결속, CSR Subject 차이 처리와 최종 Subject 구성 | CA business-practices/interoperability 결정; CSR과 등록 DN의 공통 exact-match 의무가 아님 |
| `04` | custom Compound Attestation schema | **optional attested profile만** blocker |
| `05` | trusted-time/activation Evidence field | enrollment blocker 아님; 선택적 attestation/telemetry 또는 runtime 설계 항목 |
| `06` | production attestation provider/trust bundle | **optional attested profile만** blocker |
| `07` | 실제 enrollment credential wire | project API production blocker |
| `08` | CSR input algorithm/size/parser policy | base TSA issuance blocker |
| `09` | binary/text canonicalization | CSR/API에 필요한 부분만 base blocker; Evidence 부분은 optional profile만 |
| `10` | challenge/retry/transaction 세부 | challenge를 채택한 project flow만 blocker; C2PA TSA 요구 아님 |
| `11` | CSR의 AIA/CDP 요청 방침 | interoperability/project template 결정 |
| `12` | staged activation wire | 해당 activation/runtime 사용 blocker; **TSA Leaf 발급 자체 blocker 아님** |
| `13` | error/status catalog | API integration blocker |
| `14` | certificate validity project 기본값 | CPS/template 결정; C2PA 최대 4110일은 유지 |
| `15` | `ENROLLMENT_POP`/timestamp-only ACL lifecycle | runtime/project implementation blocker; **per-enrollment Evidence 요구 아님** |
| `16` | attestation provider profile discovery | **optional attested profile만** integration blocker |
| `17` | timestamp serial namespace/counter wire | timestamp runtime blocker; **TSA Leaf 발급 자체 blocker 아님** |

이전 문서가 `04/05/06/12/15/16/17` 때문에 모든 production TSA Leaf issuance를 차단한다고 적은 부분은 철회한다.

## 7. 원문 추적

| 주장 | Primary source | 판정 |
|---|---|---|
| secure enrollment credential | C2PA CP `:469-473` | TSA 포함 공통 enrollment 요구 |
| key ownership | C2PA CP `:473` | 필수; signed CSR/KMS inspection은 예시 |
| re-key identity validation | C2PA CP `:479-481` | 신규 신청과 동일 |
| TSA issuance I/A/V | C2PA CP `:511-519` | CA business practices가 정함 |
| Dynamic Evidence | C2PA CP `:134-138`, `:521-529`, `:1684` 이후 | Generator Product/Claim Signing 범위 |
| timestamp-only/single-active | C2PA CP `:915-927` | TSA runtime/운영 요구 |
| On-Device TEE/app/key | C2PA CP `:933-939` | runtime/implementation 요구 |
| TSA Leaf profile | C2PA CP `:1334` 이후 및 공식 TSA schemas | certificate/CSR profile |
| Subject 식별·불일치 처리 | CP `:471-473,517,1542-1556`; TSA CSR `:692-740`, 최종 Subject CP `:1347` | 원문은 CSR Subject 입력 위치·등록 DN 불일치 시 단일 처리 방식을 고정하지 않음. 선택한 CA 절차로 대상·권한·정확성을 확인 |
| timestamp protocol | RFC 3161 및 C2PA Content Credentials | runtime request/token/validation; Leaf enrollment wire 아님 |

## 8. Source-negative 확인

다음 문서/스키마에서 TSA Leaf API마다 Compound Evidence를 요구하는 규정은 찾지 못했다.

- C2PA Certificate Policy v0.2
- C2PA Conformance Program v0.2
- C2PA Governance Framework v0.2
- C2PA Generator Product Security Requirements v0.2
- `specifications/build/site/specifications/2.4`
- `tsaLeaf.csr.schema.json`, `tsaLeaf.cert.schema.json`
- RFC 2986, RFC 3161, RFC 5280

“검색 결과 없음”만으로 정책을 단정한 것이 아니라, Dynamic Evidence의 정의·적용 대상과 TSA 절의 규범 문맥을 함께 대조해 범위를 구분했다.

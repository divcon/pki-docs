# 01 — System Boundary and Trust Model

> 상태: 상세 설계 초안. 이 문서는 [Overview](Overview.md)의 확정된 제품 경계를 시스템 구조, 컴포넌트 책임, 신뢰 경계, 키·인증서 모델과 공통 보안 불변조건으로 구체화한다. Certificate Platform은 외부 단말 키에 Leaf 인증서를 발급·상태 관리하지만 C2PA Claim/Manifest 또는 RFC 3161 Time-Stamp Token을 직접 서명하지 않는다.

> **2026-09-02 TSA enrollment 정정:** TSA의 TEE 실행·TEE key 보관·timestamp 전용·single-active-key는 runtime/implementation/operations 의무다. C2PA는 이 상태의 Compound Evidence를 TSA Leaf API 호출마다 요구하지 않는다. TSA의 Custom Attestation과 provider verifier는 명시적으로 선택한 optional CPS 확장에만 적용한다.

## 1. 문서 목적

### 1.1 이 문서가 답하는 질문

이 문서는 다음 질문에 대한 공통 답을 제공한다.

1. Certificate Platform이라는 시스템의 시작과 끝은 어디인가?
2. 어떤 컴포넌트가 어떤 보안 판정과 상태를 소유하는가?
3. 어떤 입력은 신뢰할 수 없고, 무엇을 검증한 뒤에만 인증서 발급에 사용할 수 있는가?
4. 단말 키, Attestation 키와 CA 키는 어떻게 다르며 어느 경계를 벗어나면 안 되는가?
5. Claim Signing Leaf와 TSA Time-Stamp Signing Leaf는 무엇을 인증하고 누가 사용하는가?
6. 02~05의 상세 설계와 구현이 공통으로 지켜야 할 보안 불변조건은 무엇인가?

이 문서는 enrollment API 필드, 인증서 extension 값, activation wire format, 운영 runbook 또는 시험 vector를 최종 확정하지 않는다. 그 상세 계약은 각 주제의 canonical owner 문서가 정의한다.

### 1.2 목표 보안 속성

Certificate Platform은 다음 속성을 보장하도록 설계한다.

- **Eligibility**: 승인된 Subscriber 또는 TSA operator와 허용된 제품·서비스만 해당 Leaf profile을 요청할 수 있다.
- **Proof of Possession**: 발급 대상 공개키와 대응하는 개인키의 소유를 검증하지 않고 인증서를 발급하지 않는다.
- **Evidence binding**: Attestation이 필요한 profile은 Evidence가 증명한 키, CSR 공개키와 발급 Leaf 공개키가 동일하다.
- **Purpose separation**: Claim 서명 자격과 Time-Stamp Token 서명 자격을 서로 다른 키, 인증서 profile과 issuing path로 분리한다.
- **Private-key confinement**: 단말 서명키는 단말의 승인된 보안 경계를, CA 서명키는 서버 HSM 경계를 벗어나지 않는다.
- **Server-side authority**: trust anchor, Reference Value, certificate template와 최종 policy verdict는 서버가 승인·관리한 값으로만 결정한다.
- **Fail-closed issuance**: 필수 신뢰 조건이 unknown, stale, expired, revoked 또는 검증 불가이면 CA/HSM 서명 전에 요청을 거부한다.
- **Accountability**: 발급 판단에 사용한 identity, Evidence, policy와 trust material의 버전을 감사 가능한 형태로 연결한다.

### 1.3 Overview와 02~05의 관계

```text
Overview
  └─ 제품의 목적, 납품 범위와 최상위 결정
       └─ 01 System Boundary and Trust Model
            ├─ 공통 구조·책임·신뢰 경계·불변조건
            ├─ 02 Certificate Enrollment
            │    └─ Claim request body, TSA API/transaction, Evidence 검증, Leaf profile
            ├─ 03 External Runtime Acceptance
            │    └─ 외부 Generator와 On-Device TSA의 사용 조건
            ├─ 04 Security and Operations
            │    └─ lifecycle, PKI/status, 운영 통제와 복구
            └─ 05 Conformance and Roadmap
                 └─ 요구 추적, 시험, 적합성과 release gate
```

교차 주제의 canonical owner는 다음과 같다.

| 교차 주제 | Canonical owner | 이 문서의 역할 |
|---|---|---|
| Lifecycle·상태 의미와 운영 recovery | 04 | 상태 영역을 구분하고 공통 불변조건만 정의 |
| Activation server transaction·signed artifact contract | 04 | Certificate Platform과 외부 TEE의 책임 경계만 정의 |
| Activation device-side acceptance | 03 | 외부 TEE가 server artifact를 검증·집행하는 조건만 소유 |
| Subscriber Leaf profile | 02 | Claim/TSA profile과 trust path의 분리 원칙만 정의 |
| Root·Intermediate·Issuing CA·OCSP responder profile | 04 | 논리적 CA 역할과 키 경계만 정의 |
| Provider schema·verifier semantics | 02 | verifier와 provider trust의 경계만 정의 |
| Organization·product/service·environment scope model | 01 | 02~05는 `OD-01`과 scope-binding 불변조건을 구체화·검증 |
| 요구 추적·시험·release evidence | 05 | 공통 불변조건 ID와 설계 locator 제공 |

## 2. 기준과 설계 결정의 분류

### 2.1 적용 기준

| 기준 | 이 문서에서 사용하는 범위 | 상세 owner |
|---|---|---|
| [C2PA Certificate Policy v0.2](<../conformance-public/docs/v0.2/C2PA Certificate Policy.md>) | CA/RA, Subscriber, Claim Signing Certificate, Assurance Level, key usage와 TSA certificate issuance의 상위 요구 | 02, 04, 05 |
| [C2PA Conformance Program v0.2](<../conformance-public/docs/v0.2/C2PA Conformance Program.md>) | Generator Product, CPL, Max Assurance Level과 적합성 주체 | 02, 05 |
| [Content Credentials Specification 2.4](../specifications/build/site/specifications/2.4/specs/C2PA_Specification.html) | 외부 Generator와 Validator의 C2PA Claim 서명·검증 상호운용 | 03, 05 |
| [RFC 3161](../rfc3161.txt), [RFC 5816](../rfc5816.txt) | 외부 On-Device TSA가 생성하는 TimeStampToken과 TSA certificate 사용 | 03, 05 |
| [RFC 2986 PKCS#10](https://www.rfc-editor.org/rfc/rfc2986), [RFC 5280 PKIX](https://www.rfc-editor.org/rfc/rfc5280) | CSR Proof of Possession과 CA가 발급하는 X.509 인증서·경로·상태 구조 | 02, 04 |
| CA CPS·TSA practices·provider profile | TSA 운영 정책과 선택적 On-Device TSA Attestation 확장 | 02, 04, 05 |

`c2pa-design/` 문서는 설계 산출물이며 외부 요구사항의 사실 근거가 아니다. 요구 추적 시 위 원문과 승인된 외부 자료를 source로 사용하고, 이 문서는 design locator로만 사용한다.

### 2.2 요구 수준

| 표기 | 의미 | 변경 방식 |
|---|---|---|
| `C2PA-REQUIRED` | C2PA 원문이 요구하는 항목 | 적용 원문 version을 바꾸거나 공식 요구를 충족해야 변경 가능 |
| `C2PA-OBLIGATION` | 대문자 BCP 14 키워드는 아니지만 C2PA 원문이 운영 의무로 서술한 항목 | 원문 문언·CPS 이행 증거와 함께 변경 검토 |
| `RFC-REQUIRED` | RFC 또는 PKIX/PKCS profile의 규범 요구 | protocol/profile 적합성 검토 필요 |
| `CPS-REQUIRED` | 이 CA가 C2PA 공통 기준보다 강화하여 강제하는 항목 | 보안·운영 검토와 CPS 변경 승인 필요 |
| `ARCH-DECISION` | 이 프로젝트가 선택한 공통 구조 또는 불변조건 | 영향 분석, 승인과 회귀 시험 필요 |
| `PROVIDER-BOUND` | provider·기기·배포 환경별로 승인해야 하는 값 | signed provider/deployment profile로만 활성화 |
| `OPEN` | 구현 전에 결정해야 하지만 아직 확정되지 않은 항목 | owner·근거·결정 기록이 없으면 production blocker |

On-Device TSA 관련 요구는 다음처럼 분리한다.

| 요구 수준 | 내용 |
|---|---|
| `C2PA-OBLIGATION` | General TSA time value의 UTC(k) traceability. CP 919행은 lowercase `shall`이므로 대문자 BCP 14 요구와 구분하지만 운영 baseline에서 생략하지 않음 |
| `C2PA-REQUIRED` | 선언 accuracy 유지, 공인 leap-second 통지 시 synchronization 유지와 drift 초과 시 발급 중단, timestamp 전용 private key, TSU당 하나의 active signing key |
| `C2PA-REQUIRED` | On-Device TSA의 24시간 이내 online time synchronization 시도, TSA application의 TEE 실행, TSU signing key의 TEE 내부 생성·보관 |
| `OPTIONAL CPS EXTENSION` / `ARCH-DECISION` | 선택적으로 원격 입증을 채택할 때의 Custom Compound Attestation 형식·trust mapping·freshness, staged activation protocol과 project-specific offline cutoff |
| `PROVIDER-BOUND` | 실제 TEE/TA identifier, Evidence schema, trust anchor, Reference Value, status source와 검증 vector |

따라서 TEE 실행·TEE 키 보관과 trusted-time 기본 속성은 완화 가능한 프로젝트 선택이 아니다. 다만 Custom Attestation은 이를 확인하는 선택적 강화 통제이고, staged activation은 single-active-key를 구현하는 project mechanism이다. 어느 것도 C2PA가 정한 TSA Leaf per-request wire prerequisite가 아니다.

## 3. System of Interest와 책임 경계

### 3.1 Certificate Platform이 제공하는 것

Certificate Platform은 다음 capability를 구현·운영한다.

| Capability | 책임 |
|---|---|
| Registration and authorization | Subscriber, Applicant, TSA operator/service와 product eligibility를 등록·검증한다. |
| Claim enrollment decision | 인증된 Claim request body를 검증하고 server-held freshness context, CSR/Evidence와 발급 gate를 결속한다. |
| TSA enrollment transaction | TSA 요청에만 idempotency, expiry와 transaction 상태를 제공하고 optional challenge profile에 challenge를 추가한다. |
| CSR validation | PKCS#10 구조, 허용 키 algorithm과 Proof of Possession을 검증한다. |
| Attestation verification | profile이 요구하는 Evidence의 trust, signature, freshness, subject-key binding과 platform/workload claims를 검증한다. |
| Certificate policy decision | identity, eligibility, CSR과 profile이 요구하는 경우 Evidence/provider verdict를 해당 Leaf profile 정책에 결합한다. |
| Certificate issuance | HSM의 Claim 또는 TSA Issuing CA key로 승인된 Leaf certificate template만 서명한다. |
| Repository and status | 발급 chain, OCSP/CRL, revocation과 인증서 상태 정보를 관리·게시한다. |
| Lifecycle coordination | re-enrollment, TSA activation coordination과 reconciliation에 필요한 서버 측 resource를 관리한다. |
| Audit and incident support | 판정 근거와 dependency version을 기록하고 차단·영향 분석·폐기를 지원한다. |

플랫폼의 최종 발급 결과는 두 종류다.

```text
K_claim public key ── Claim Signing Issuing CA ──> C2PA Claim Signing Leaf
K_tsu public key   ── TSA Issuing CA           ──> C2PA TSA Time-Stamp Signing Leaf
```

인증서는 개인키를 만들거나 전달하지 않는다. 인증서는 검증된 공개키에 용도·주체·정책을 연결하는 CA 서명 객체다.

### 3.2 외부 컴포넌트가 제공하는 것

| 외부 주체 | 필수 책임 | Certificate Platform과의 계약 |
|---|---|---|
| Subscriber / Applicant | 조직 신원, Conformance 자료, Subscriber Agreement와 승인된 접근 자격 관리 | 인증된 enrollment·revocation 요청 |
| Generator Product | Asset/Assertion/Claim/Manifest 구성, `K_claim` 사용, C2PA 서명 생성 | CSR·필요 Evidence 제출, 발급 Leaf/chain 설치 |
| Claim signing secure boundary | `K_claim` 생성·보관, 허용된 Claim signing operation만 수행 | 공개키·PoP·필요 Evidence 제공 |
| On-Device TSA / TSA TA | TEE 내부 `K_tsu` 관리, trusted time, RFC 3161 request 처리와 TimeStampToken 생성 | CSR/key ownership 제공, 발급 Leaf 설치; optional profile이면 Attestation 제출 |
| Attestation Service / provider | 선택된 profile에서 key·workload·platform 상태를 수집하고 Evidence에 서명 | optional versioned Evidence와 trust/status 자료 제공 |
| C2PA Validator / Relying Party | Claim chain과 timestamp chain을 독립적으로 검증 | repository/status/Trust List를 소비하되 enrollment을 호출하지 않음 |
| C2PA governance / Trust List | Conformance 및 Claim/TSA trust anchor 배포 | Certificate Platform 운영·적합성의 외부 전제 |

외부 컴포넌트의 acceptance contract를 시험한다고 해서 해당 runtime이 Certificate Platform의 납품 범위로 들어오지는 않는다.

### 3.3 명시적 비범위

Certificate Platform은 다음 기능을 제공하지 않는다.

- Asset, Assertion, Claim, Manifest 또는 Manifest Store 생성
- C2PA Claim의 COSE signature 생성
- MessageImprint 계산 또는 RFC 3161 TimeStampReq 생성
- RFC 3161 TimeStampToken 또는 TSTInfo 생성·서명
- 일반 network TSA endpoint
- 원격 HSM을 이용한 단말 대상 remote signing
- raw digest, arbitrary payload 또는 application message signing API
- 단말 `K_claim`·`K_tsu`의 생성, escrow, backup, export, recovery 또는 서버 보관
- 외부 단말의 trusted-time runtime 구현
- C2PA Validator 구현

향후 위 기능이 필요하면 기존 CA/HSM 경계에 endpoint를 추가하는 방식으로 확장하지 않는다. 별도의 System of Interest, 키 계층, threat model과 승인 절차를 가진 독립 제품 결정이 필요하다.

## 4. 아키텍처 원칙

### 4.1 인증서 발급과 콘텐츠 서명의 분리

정상 runtime에서 콘텐츠 서명 경로는 Certificate Platform을 통과하지 않는다.

```text
Enrollment time
Device public key + CSR [+ profile-conditional Evidence] ──> Certificate Platform ──> Leaf + chain

Runtime
Claim bytes ──> external K_claim ──> C2PA Claim signature
MessageImprint ──> external TSA TA / K_tsu ──> RFC 3161 TimeStampToken
```

서버 HSM에는 Claim/TSA Issuing CA key와 필요한 status signer key만 존재한다. 단말 `K_claim` 또는 `K_tsu`가 서버 HSM에 생성·import·backup되는 설계는 허용하지 않는다.

### 4.2 두 credential domain의 분리

Claim signing과 time stamping은 다음 차원에서 분리한다.

| 차원 | Claim Signing domain | TSA domain |
|---|---|---|
| 발급 대상 키 | `K_claim` | `K_tsu` |
| runtime 목적 | C2PA Claim 서명 | RFC 3161 TimeStampToken 서명 |
| runtime 경계 | Generator의 승인된 signing boundary | TEE 내부 TSA TA |
| Subscriber Leaf profile | Claim Signing AL1 또는 AL2 | TSA Time-Stamp Signing |
| Issuing role | Claim Signing Issuing CA | TSA Issuing CA |
| relying-party trust | C2PA Claim Signing trust path | C2PA TSA trust path |
| 상세 발급 조건 | CPL·AL·Dynamic Evidence | 승인 TSA operator/service, key ownership, TSA profile; optional Custom Attestation |

같은 key pair를 두 domain에서 공유하거나 한 Leaf의 용도를 다른 domain으로 해석하지 않는다. 한 domain의 검증 성공, CA 등록 또는 Trust List 등재는 다른 domain의 신뢰를 자동으로 부여하지 않는다.

### 4.3 전달자와 신뢰 주체의 분리

REE와 network client는 CSR, Evidence와 결과를 전달할 수 있지만 다음 값을 스스로 보증할 수 없다.

- key origin, exportability, purpose 또는 hardware protection
- TA/Generator identity와 measurement
- TEE/boot/patch state
- trusted time 상태
- provider verdict 또는 Reference Value 일치 여부

Evidence-required profile에서는 이 값을 승인된 Evidence의 서명 범위에서 추출하고 서버가 관리하는 trust material과 대조한 경우에만 원격 판정 입력으로 쓴다. Base TSA profile의 runtime 속성은 설계·TEE enforcement·시험·운영 감사로 보증한다. 어느 경우에도 클라이언트가 별도 JSON field로 반복한 자기 선언은 보안 판정에 사용하지 않는다.

### 4.4 판정과 서명의 분리

CA/HSM은 Evidence를 직접 해석하거나 외부 요청을 그대로 인증서로 변환하지 않는다.

```text
untrusted input
  └─ strict parser
       └─ identity / authorization
            └─ CSR PoP
                 └─ Evidence verifier
                      └─ policy decision
                           └─ CA-controlled certificate template
                                └─ HSM sign
```

필수 predicate가 모두 성공한 뒤에만 제한된 issuance authorization이 CA orchestrator에 전달된다. CSR extension, Subject, validity 또는 AIA/CRL 값은 요청에서 그대로 복사하지 않고 CA가 고정한 template과 policy로 구성한다.

CSR Subject의 구조·C/O/CN 검사와 발급 대상의 식별·인증·권한 확인은 별개다. 식별정보를 CSR Subject, 별도 신청정보 또는 인증된 등록정보에서 확인하는 방식은 CA 절차가 정하며, 원문이 모든 CSR Subject의 등록 DN 일치나 불일치 자동 거부를 고정한 것은 아니다. 단순 불일치를 처리하는 절차가 대상·권한 확인, 원본 CSR PoP 또는 최종 Subject의 정확성을 우회해서는 안 된다. [공통 Subject 원칙](02-Certificate-Enrollment.md#csr-subject-identification)에 따른다.

## 5. 시스템 컨텍스트

### 5.1 Level-0 컨텍스트

```text
┌──────────── External device and runtime / not delivered ────────────┐
│ Generator Product ── Claim signing boundary / K_claim              │
│         │                                                          │
│         └──────── TSA client ── TEE / TSA TA / K_tsu / trusted time│
│                                      │                             │
│ Attestation Service / AK ────────────┘                             │
└────────────────── CSR [+ profile-conditional Evidence] ───────────┘
                               │
                               ▼
┌──────────────── Delivered Certificate Platform ────────────────────┐
│ Access + Claim Request Body Validator / TSA Enrollment API         │
│ Claim Decision + TSA Transaction + Authorization                   │
│ Attestation Verifier ── Provider Trust / Reference Value Registry  │
│ Certificate Policy Engine                                         │
│ CA Orchestrator ── Claim CA HSM boundary / TSA CA HSM boundary     │
│ Certificate Repository + OCSP/CRL + Revocation                     │
│ Audit + Operations Control                                         │
└───────────────────────────┬────────────────────────────────────────┘
                            │ certificate chain / status
                            ▼
          External Validator, Relying Party and C2PA Trust Lists
```

### 5.2 내부 논리 컴포넌트

논리 컴포넌트는 구현 process 또는 microservice 수를 의미하지 않는다. 동일 process에 배치하더라도 아래 책임과 권한 경계를 유지해야 한다.

| 컴포넌트 | 소유 책임 | 금지 책임 | 주요 출력 |
|---|---|---|---|
| Access Gateway | TLS termination, caller credential 검증, request size/rate 제한 | product eligibility 또는 Evidence 최종 판정 | authenticated caller context |
| Claim Request Body Validator | Claim schema/version, field/cardinality와 immutable binding 검증 | transaction/response/state 정의, CA key 사용 | normalized Claim request decision input |
| TSA Enrollment API | TSA transaction 명령 접수와 결과 조회 | Claim request-body schema 소유, CA key 사용 | normalized TSA command/response |
| Identity & Authorization | Subscriber/TSA operator, product/service, profile 권한과 quota 판정 | Evidence cryptographic verdict | authorization decision + source version |
| TSA Transaction Service | TSA enrollment/activation challenge, idempotency, expiry, 상태 전이와 issuance·activation operation 연결 | Claim issuance 상태 정의, trust anchor 선택, 인증서 template 임의 변경, 외부 TEE key state 단정 | TSA transaction state and one-time authorization context |
| Attestation Verifier | provider-specific strict parsing, chain/signature/freshness, signed claim 추출 | 요청자가 제공한 root·Reference Value 신뢰, 인증서 발급 | normalized verified claims + dependency IDs |
| Provider Trust Registry | provider profile, trust anchor, status source와 Reference Value의 승인본 관리 | 미서명·만료·rollback version 활성화 | immutable versioned trust bundle |
| Certificate Policy Engine | identity, CSR, profile-conditional Evidence와 predicate의 최종 결합 | HSM 직접 key operation, mandatory predicate 우회 | explainable allow/deny decision |
| CA Orchestrator | approved template 구성, issuance authorization 검증, 중복 발급 통제 | 임의 payload signing, CSR field의 무검증 복사 | certificate-to-be-signed and issuance record |
| Claim Issuing CA / HSM | Claim Signing Leaf의 제한된 CA 서명 | TSA Leaf, Claim/Manifest 또는 arbitrary payload 서명 | Claim Signing Leaf signature |
| TSA Issuing CA / HSM | TSA Leaf의 제한된 CA 서명 | Claim Leaf, TimeStampToken 또는 arbitrary payload 서명 | TSA Leaf signature |
| Certificate Repository | 발급 Leaf와 chain publication·retrieval | private key 또는 Raw Evidence 보관 | certificate/chain object |
| Status Service | OCSP/CRL 생성·게시와 revocation projection | 외부 runtime key 상태를 CA-validity로 오인 | signed status information |
| Audit Pipeline | append-oriented security event, correlation과 integrity 보호 | secret/private key·불필요한 Raw Evidence 기록 | audit event and evidence index |
| Operations Control | provider/profile activation, issuance stop, incident와 recovery 명령 | 단독 운영자의 mandatory trust override | approved operational action |

### 5.3 주요 상태의 소유권

| 상태 | Authoritative owner | 소비자 | 금지되는 혼동 |
|---|---|---|---|
| Subscriber/TSA operator eligibility | Identity & Authorization | Enrollment, Policy Engine | 인증 성공을 profile 권한으로 간주 |
| Claim issuance decision | Policy Engine/CA Orchestrator | Claim Request Body Validator, Repository, Audit | 외부 response 또는 transaction 상태로 간주 |
| TSA enrollment transaction | TSA Transaction Service | TSA API, Policy Engine, Audit | HTTP 응답 상태를 발급 완료로 간주 |
| Provider/trust version | Provider Trust Registry | Verifier, Policy Engine, Operations | 요청에 포함된 provider root 사용 |
| Evidence verdict | Attestation Verifier | Policy Engine, Audit | client self-assertion을 verdict로 사용 |
| Certificate issuance record | CA Orchestrator/Repository | Claim decision 또는 TSA Transaction, Status, Audit | 외부 key activation과 동일 상태로 간주 |
| Certificate validity/revocation | CA repository/status authority | Validator, runtime acceptance | TEE key activation 여부를 X.509 상태로 표현 |
| Claim certificate acceptance | 외부 Subscriber/Generator Product; 서버는 선택적 audit observation만 보유 | Operations, Audit | 별도 CA certificate state 또는 activation transaction으로 간주 |
| TSA external device-key state | 외부 TSA TA; 서버는 승인된 runtime/운영 evidence와, 수집하는 경우 authenticated observation을 보유 | Runtime acceptance, Operations | CA-valid certificate 발급이나 서버 projection을 실제 active key로 간주 |
| TSA activation server transaction·signed artifact | Transaction Service; 의미 계약은 04 | 외부 TSA TA, Operations, Audit | device-authoritative key state 또는 X.509 certificate state로 간주 |

## 6. 신뢰 경계

### 6.1 경계 목록

| ID | 경계 | 경계를 넘는 데이터 | 기본 신뢰 | 필수 통제 방향 |
|---|---|---|---|---|
| `TB-01` | REE/Generator ↔ Claim signing boundary(`K_claim`) | Claim signing request, public key, CSR input/result | REE 비신뢰 | Claim-operation ACL, key purpose 제한, key metadata의 trusted-source 수집 |
| `TB-02` | REE/TSA client ↔ TSA TA/TEE(`K_tsu`) | TimeStampReq, activation artifact, TimeStampResp | REE·IPC 입력 비신뢰 | strict parser, timestamp 전용 operation, replay/rollback 보호 |
| `TB-03` | Device/client ↔ Certificate Platform | credential, CSR, Evidence, freshness value, certificate | network/client 비신뢰 | TLS, caller authn/authz, schema/size/rate 제한; idempotency는 TSA-only |
| `TB-04` | Verifier ↔ provider trust domain | Evidence chain/token, provider status | Evidence는 검증 전 비신뢰 | server-pinned trust, signature/path/status/freshness, version pin |
| `TB-05` | Verifier/Policy ↔ CA Orchestrator | normalized verdict, policy decision, issuance authorization | 최소 권한 내부 경계 | authenticated service identity, immutable decision binding |
| `TB-06` | CA Orchestrator ↔ HSM | fixed signing request, key handle | 최고 신뢰 | profile-bound key policy, authorization, audit, dual control |
| `TB-07` | Operator ↔ production control plane | profile activation, revocation, emergency action | privileged but not implicitly trusted | RBAC, separation of duties, multi-approval, immutable audit |
| `TB-08` | Certificate Platform ↔ repository/status consumers | certificate, OCSP/CRL, chain | public/untrusted consumer | signed object, freshness, availability, cache semantics |
| `TB-09` | production ↔ non-production | profile, trust material, fixtures, deployment artifact | 상호 불신 | 별도 credential·CA key·namespace와 promotion gate |
| `TB-10` | processing components ↔ persistence/audit/Evidence vault | Claim decision 또는 TSA transaction, verdict, digest, identifier, 선택적 Raw Evidence | 내부 저장소도 무조건 신뢰하지 않음 | 최소 수집, environment-scoped key 암호화, service authorization, integrity와 retention/deletion |

### 6.2 신뢰 전이 규칙

어떤 입력도 한 번의 검증으로 전체 시스템에서 신뢰되는 값으로 승격되지 않는다.

```text
raw request
  → syntactically valid
  → authenticated caller
  → authorized profile request
  → cryptographically verified CSR
  → [attestation-required profile only] provider-authentic and fresh Evidence
  → normalized claims
  → policy-compliant issuance decision
  → CA-signed certificate
```

각 전이는 입력 digest, 검증기·policy·trust bundle version과 결과를 남긴다. 후속 컴포넌트는 이전 단계의 raw client field를 다시 신뢰하지 않고, 인증된 내부 주체가 생성한 versioned 결과만 소비한다.

## 7. 공통 데이터 흐름

### 7.1 Claim Leaf enrollment 신뢰 흐름

Claim Signing은 transaction·response 계약 없이 인증, request body와 발급 predicate의 흐름만 정의한다.

```text
1. Caller authentication and profile authorization
2. Server resolves Subscriber/CPL and any required freshness/audience context
3. External secure boundary creates K_claim
4. Device creates CSR; AL2는 request context/key에 결속된 Evidence도 생성
5. Request-body validator performs strict decoding and immutable binding
6. CSR validator verifies Proof of Possession and profile constraints
7. AL2만 Verifier가 provider trust, signature, status, freshness and O.1~O.4 claims 검증
8. Policy Engine evaluates all mandatory predicates
9. CA Orchestrator constructs a CA-controlled Leaf template
10. Profile-bound Issuing CA key signs only the approved certificate object
11. Repository, status index, issuance decision and audit record commit
12. Device installs Leaf/chain; runtime use remains outside the platform
```

Claim AL1은 단계 7을 건너뛰고 instance authentication, identity/eligibility와 CSR PoP 결과를 policy decision에 결합한다. Claim AL2는 단계 7을 생략하거나 수동 승인으로 대체할 수 없다.

단계 1~8에서 해당 profile에 필수인 판정이 모두 성공하기 전에는 단계 9~10을 호출하지 않는다. TSA의 transaction, idempotency와 response 처리는 [Overview §6](Overview.md#6-tsa-certificate-enrollment-api-논리-계약)의 TSA-only 설계가 소유하며 이 Claim 흐름에 적용하지 않는다.

### 7.2 Trust material 배포 흐름

```text
provider/OEM source
  → independent validation
  → security and policy approval
  → signed versioned bundle
  → deployment promotion
  → verifier activation
  → monitoring / expiry / emergency revoke
```

production verifier가 읽는 trust anchor, Reference Value, status rule과 claim mapping은 Git의 임의 파일이나 운영자 local 설정이 아니라 승인된 deployment artifact여야 한다. bundle이 unknown, stale, expired, rollback되었거나 emergency-revoked이면 해당 provider의 발급을 차단한다.

### 7.3 Revocation과 status 흐름

```text
authenticated request or incident signal
  → revocation authority validation
  → affected certificate/dependency resolution
  → CA revocation state commit
  → OCSP/CRL publication
  → audit and notification
```

Certificate Platform이 보장할 수 있는 것은 신규 발급·activation coordination 차단과 status publication이다. 이미 offline인 외부 단말의 `K_claim` 또는 `K_tsu`가 즉시 사용 중단됐다고 주장하지 않는다. runtime cutoff와 refresh acceptance는 03, 운영 대응은 04가 정의한다.

### 7.4 Runtime 서명 흐름의 비경유성

```text
External Generator                    External On-Device TSA
Claim bytes                            TimeStampReq / MessageImprint
    │                                      │
    ▼                                      ▼
K_claim secure operation               TSA TA validates request/time/state
    │                                      │
    ▼                                      ▼
COSE Claim signature                   K_tsu signs TSTInfo → TimeStampToken

             Certificate Platform 호출 없음
```

runtime에서 status 또는 trust material을 조회할 수는 있지만, 실제 서명 대상 bytes나 digest를 Certificate Platform의 CA/HSM에 전송하여 서명받지 않는다.

## 8. 키·인증서·Evidence 모델

### 8.1 키 inventory

| 키 | 생성·보관 경계 | 허용 용도 | 공개되는 값 | 금지 사항 |
|---|---|---|---|---|
| `K_claim` | Generator Product의 승인된 secure key boundary | C2PA Claim 서명, CSR PoP | SPKI, CSR, 필요 시 Evidence subject key | TSA token·arbitrary payload 용도 공유, 서버 반출 |
| `K_tsu` | TSA TA가 실행되는 TEE | RFC 3161 TimeStampToken 서명, CSR PoP | SPKI, CSR, optional profile의 Attestation subject key | Claim 서명, raw signing, TEE 밖 반출 |
| Attestation Key (`AK`) | provider가 정의한 hardware/TEE attestation boundary | Evidence 또는 attestation result 서명 | verification certificate/key chain | C2PA Claim·TST·C2PA Leaf 발급 서명 |
| Claim Issuing CA key | production Claim CA HSM partition | Claim Signing Leaf 인증서 서명 | CA certificate의 public key | TSA Leaf·runtime payload 서명, 외부 export |
| TSA Issuing CA key | production TSA CA HSM partition | TSA Leaf 인증서 서명 | CA certificate의 public key | Claim Leaf·TST/runtime payload 서명, 외부 export |
| Root/Intermediate CA key | offline 또는 고통제 HSM 경계 | 승인된 subordinate CA certificate 서명 | CA chain | online enrollment 요청 직접 처리 |
| OCSP responder key | status signing 경계 | 승인된 OCSP response 서명 | responder certificate | Leaf/CA certificate 또는 runtime payload 서명 |
| Audit integrity key | audit service key boundary | audit batch/event integrity | verification metadata | 인증서·status·runtime payload 서명 |
| Device-binding HMAC key | environment별 server HSM/service key boundary | opaque hardware binding digest | key version 식별자만 | 원본 hardware handle 복구 목적 사용 |

`K_claim`의 정확한 하드웨어 보호 수준은 Claim AL1/AL2 profile에 따라 02가 정의한다. `K_tsu`는 이 프로젝트의 On-Device TSA profile에서 TEE 내부 생성·non-exportable·전용 사용을 요구한다.

### 8.2 세 개의 독립 trust path

```text
Attestation trust path                  Claim AL2/optional TSA profile의 발급 심사에 사용
Provider/OEM Root
  └─ Attestation Issuer / AK certificate
       └─ signed Evidence for K_claim or optional K_tsu profile

Claim Signing trust path                C2PA Claim 검증에 사용
C2PA-recognized Claim trust anchor
  └─ Claim Signing Issuing CA
       └─ Claim Signing Leaf(K_claim)

TSA trust path                          RFC 3161 timestamp 검증에 사용
C2PA-recognized TSA trust anchor
  └─ TSA Issuing CA
       └─ TSA Time-Stamp Signing Leaf(K_tsu)
```

Attestation path가 유효하다는 사실은 C2PA signing credential로 사용할 자격을 직접 부여하지 않는다. 이는 발급 policy의 한 입력이다. 반대로 C2PA Claim/TSA Leaf는 device platform 상태를 실시간으로 증명하는 Attestation artifact가 아니다.

### 8.3 공개키 결속

Attestation이 발급 대상 키를 증명하는 profile은 다음을 만족해야 한다.

```text
canonicalSPKI(Evidence.subjectKey)
  == canonicalSPKI(CSR.subjectPublicKeyInfo)
  == canonicalSPKI(IssuedLeaf.subjectPublicKeyInfo)
```

비교는 provider가 보낸 문자열이나 JSON 직렬화가 아니라 algorithm identifier와 key encoding을 profile 규칙에 따라 정규화한 값 또는 그 digest로 수행한다. Evidence 서명 검증용 AK와 Evidence가 증명하는 subject key를 혼동하지 않는다.

### 8.4 인증서와 Evidence의 수명 차이

| 객체 | 목적 | Authoritative issuer | 사용 시점 | status 의미 |
|---|---|---|---|---|
| Attestation Evidence | Evidence-required profile에서 key/workload/platform 사실 증명 | provider/OEM attestation domain | conditional enrollment decision | provider freshness/status 규칙 |
| Claim Signing Leaf | `K_claim`과 Generator Product/AL을 연결 | Claim Signing CA | Claim signature 검증 | X.509/OCSP/CRL과 Claim trust policy |
| TSA Signing Leaf | `K_tsu`와 TSA service signing 자격을 연결 | TSA CA | TimeStampToken 검증 | X.509/OCSP/CRL과 TSA trust policy |
| Activation artifact | 외부 TSA key 전환을 조정 | 04가 소유하는 server transaction/control signer; 03이 device-side acceptance | TSA lifecycle | X.509 certificate validity와 별도이며 C2PA/RFC 표준 wire format이 아님 |

Raw Evidence를 Leaf certificate에 복사하지 않는다. 발급 후 필요한 것은 검증 결과, dependency/version, digest와 정책상 최소 audit record이며 Raw Evidence 보존은 별도 privacy 승인을 따른다.

## 9. 삼성전자 전용 배포와 제품·환경 격리

### 9.1 확정된 배포 모델

`OD-01`의 배포 모델은 다음과 같이 확정한다.

| 항목 | 결정 |
|---|---|
| 조직 tenant | 삼성전자 단일 조직만 사용하는 전용 `single-tenant` Certificate Platform |
| 지원 대상 | 삼성전자 스마트폰·가전 등 복수 제품군의 Generator Product와 On-Device TSA |
| 공유 범위 | 공통 enrollment, verifier, policy, repository/status와 운영 control plane을 제품군이 공유할 수 있음 |
| 논리적 격리 단위 | Generator Product/CPL record, TSA service, TSU instance, certificate profile과 provider profile-or-NONE |
| 외부 조직 | 삼성전자 외 조직 또는 별도 법인은 현재 범위에 포함하지 않으며 필요하면 별도 onboarding·신원·권한·격리 결정을 요구 |
| 환경 경계 | production과 non-production은 CA key, credential, data store, trust/profile activation, namespace와 audit sink를 분리 |

여기서 single-tenant는 모든 제품이 같은 권한을 가진다는 뜻이 아니다. 조직 identity는 삼성전자로 고정되지만, 실제 발급 권한은 다음 resource scope로 좁힌다.

```text
Samsung Electronics organization
  ├─ Generator Product / CPL record
  │    ├─ Claim Signing AL1 profile
  │    └─ Claim Signing AL2 profile + allowed attestation provider
  └─ TSA service
       └─ TSU instance + provider profile or NONE
```

제품군, CPL record 또는 TSA service의 관리 권한을 가진 주체만 그 scope의 enrollment·re-key·revocation을 수행할 수 있다. 한 제품의 적합성, provider 허용 또는 quota가 다른 제품에 자동 상속되지 않는다.

Claim과 TSA의 authorization context는 각각 다음 tuple을 사용한다.

```text
Claim scope =
  {organization, subscriber, Generator Product, CPL record,
   requested AL, certificate profile, provider profile or NONE, environment}

TSA scope =
  {organization, TSA operator, tsaServiceId, tsuInstanceId,
   certificate profile, provider profile or NONE, environment}
```

Claim tuple은 request body와 server-held freshness context에서 고정하고 CSR, 필요한 Evidence, policy decision, issuance record와 발급 certificate의 Subject/profile/AL에 끝까지 결속한다. TSA tuple은 TSA-only transaction에서 고정한다. Challenge 또는 activation artifact를 사용하는 TSA profile은 같은 tuple에 추가 결속한다. 어느 단계에서든 tuple mismatch가 발생하면 해당 CA/HSM 또는 TSA activation authorization 전에 거부한다.

### 9.2 격리 불변조건

- Claim caller identity, authorization, request body/decision, certificate와 audit object는 삼성전자 조직과 정확한 product/profile scope에 연결한다. TSA transaction은 별도로 operator/service/profile scope에 연결한다.
- 다른 product, TSA service 또는 TSU의 resource identifier를 제출해도 존재 여부, 상태, digest 또는 오류 차이로 정보를 노출하지 않는다.
- 승인된 `keyReuseIdentity` profile이 있는 경우에만 Claim/TSA Subscriber Leaf의 전체 production 발급 이력에서 동일 public key를 판정한다. 현재 [`OD-KEY-01`](claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md#6-operations-decision-register)이 `TBD`이므로 모든 Claim/TSA issuance를 비활성화한다.
- X.509 certificate serial은 Issuing CA 범위에서 고유하게 발급한다.
- RFC 3161 TimeStampToken serial은 같은 TSA service Subject를 공유하는 모든 TSU와 모든 key rotation을 포함한 TSA service 범위에서 고유하다.
- `serialNamespace`는 TSU별로 서버가 발급하고 같은 TSU의 re-key에는 유지하며 다른 TSU에 영구 재사용하지 않는다.
- Claim freshness/replay context는 인증된 Subscriber, product/CPL, profile, operation과 CSR key에 결속한다. TSA idempotency identity와 challenge는 인증된 operator와 operation/transaction에 결속한다. Quota는 각각 Generator Product 또는 TSA service 범위로 강제한다.
- 한 product의 CPL/AL/provider eligibility를 다른 product의 요청에 재사용하지 않는다.
- 한 TSA service의 operator 권한을 다른 service에 재사용하지 않으며, TSU slot 또는 activation artifact는 같은 service 안에서도 다른 TSU에 재사용하지 않는다.
- 제품별 장애나 비정상 요청이 공유 플랫폼 전체 발급을 고갈시키지 않도록 product/service별 authorization과 quota를 둔다.
- Claim CA와 TSA CA는 제품군별로 나누지 않아도 되지만 key와 authorization policy를 서로 분리한다. 별도 product CA가 필요하면 04의 PKI topology 결정으로 다룬다.
- production과 non-production은 CA key, service credential, trust/profile activation, namespace와 audit sink를 공유하지 않는다.
- test root, test Leaf, fixture Evidence 또는 non-production activation artifact가 production 발급 predicate를 통과할 수 없어야 한다.

## 10. 위협 가정

### 10.1 보호 자산

- Claim/TSA/Root/Intermediate/status private key와 HSM authorization
- 발급 자격, certificate profile과 policy decision integrity
- provider trust anchor, Reference Value, status와 signed bundle sequence
- Claim freshness/replay binding과 issuance uniqueness; TSA challenge/transaction/idempotency
- 삼성전자 Subscriber/TSA operator identity와 product/service scope isolation
- Evidence, hardware identifier, measurement와 audit data의 기밀성
- repository, OCSP/CRL과 revocation 정보의 무결성·freshness·가용성
- 외부 `K_claim`/`K_tsu`의 non-exportability와 purpose restriction을 뒷받침하는 증거

### 10.2 공격자 능력

다음 능력을 가진 공격자를 기본 가정으로 한다.

- REE application, local IPC client와 network 요청을 제어한다.
- 과거 CSR, Evidence, challenge, certificate 또는 activation message를 재전송한다.
- field substitution, parser ambiguity, duplicate encoding과 algorithm downgrade를 시도한다.
- 다른 product, CPL record, TSA service 또는 TSU의 identifier를 조합한다.
- 만료·rollback·폐기된 provider trust material이나 Reference Value를 주입한다.
- Claim 동시 요청 또는 TSA 응답 손실/retry/partial failure를 이용해 중복 인증서나 이중 active TSA key를 만든다.
- 내부자 권한 또는 손상된 운영 credential을 이용해 profile·trust·revocation 정책을 우회하려 한다.
- provider, CA, status service 또는 time source compromise 뒤 영향을 숨기거나 오래된 정상 상태를 재사용한다.

### 10.3 신뢰 가정과 한계

| 대상 | 신뢰 가정 | 신뢰하지 않는 범위 |
|---|---|---|
| Secure key boundary / TEE | 승인 설계·구현·시험과, 사용된 경우 검증된 Evidence는 key confinement·measurement 보증을 제공 | REE가 보고한 상태, 미승인 firmware/provider version |
| Attestation provider | pinned trust와 status가 유효한 signer는 지정된 signed claims를 보증 | provider가 표준화하지 않은 claim 의미의 임의 추론 |
| HSM | key non-exportability와 승인된 operation policy를 강제 | 잘못된 policy decision을 스스로 교정 |
| Certificate Platform operator | 부여된 역할 범위에서 절차 수행 | 단독 승인, mandatory predicate override |
| Trusted-time source | 승인 runtime profile의 freshness·accuracy 조건 안에서 시간 제공 | offline cutoff를 넘긴 오래된 sync 결과 |
| Status/Trust List source | 검증된 서명과 freshness 범위에서 상태 제공 | stale cache, network failure를 정상으로 해석 |

TEE, provider 또는 HSM도 절대 신뢰가 아니다. version, status, 운영 통제와 compromise 대응이 함께 유효할 때만 제한된 보증을 제공한다.

### 10.4 대표 위협과 후속 owner

| Threat ID | 위협 | 공통 방어 방향 | 상세 owner |
|---|---|---|---|
| `TH-01` | Evidence-required profile에서 subject key와 CSR key 바꿔치기 | canonical SPKI 삼중 결속 | 02, 05 |
| `TH-02` | Evidence-required profile의 freshness/Evidence replay | Claim은 request-context·Subscriber·key binding, TSA는 transaction binding; one-time consume | 02, 05 |
| `TH-03` | Claim/TSA key 목적 혼동 | 별도 key/profile/issuing path/HSM policy | 02, 03, 04 |
| `TH-04` | client-supplied root/Reference Value 주입 | server-pinned signed trust bundle | 02, 04 |
| `TH-05` | provider policy rollback | signed sequence, expiry, emergency revoke, fail-closed | 04, 05 |
| `TH-06` | concurrent duplicate issuance | Claim lineage/key reservation과 승인된 key identity; TSA idempotency; atomic issuance record | 02, 05 |
| `TH-07` | CA/HSM confused deputy | profile-bound authorization와 fixed certificate template | 02, 04 |
| `TH-08` | runtime raw signing abuse | operation-specific API/ACL; Certificate Platform에는 signing endpoint 없음 | 03, 05 |
| `TH-09` | TSA time/serial rollback | TEE protected monotonic/rollback-safe state와 cutoff | 03, 05 |
| `TH-10` | product/CPL/service/TSU scope mix-and-match | Claim/TSA authorization tuple의 end-to-end 결속, uniform denial, storage/authz isolation | 02, 04, 05 |
| `TH-11` | privileged policy bypass | separation of duties, multi-approval, immutable audit | 04, 05 |
| `TH-12` | provider/CA compromise | dependency index, issuance stop, revocation, incident recovery | 04, 05 |
| `TH-13` | Evidence·장치 식별자 과다 수집 또는 유출 | 최소 수집, digest 우선, 승인된 Raw Evidence vault, 접근·보존·삭제 통제 | 04, 05 |

## 11. 공통 보안 불변조건

아래 항목은 02~05의 설계, 구현과 시험이 공통으로 만족해야 한다. `05`는 각 ID를 원문 요구 또는 승인된 아키텍처 결정, 구현, test와 evidence에 연결한다.

### 11.1 Scope와 signing boundary

| ID | 불변조건 |
|---|---|
| `AF-SCOPE-01` | Certificate Platform API에는 Claim, Manifest, TimeStampToken, raw digest 또는 arbitrary payload signing operation이 존재하지 않는다. |
| `AF-SCOPE-02` | 정상 runtime C2PA Claim/TST 생성 경로는 Certificate Platform CA/HSM을 호출하지 않는다. |
| `AF-SCOPE-03` | 외부 Generator/TSA acceptance 검증은 Certificate Platform의 납품 범위를 runtime 구현으로 확장하지 않는다. |

### 11.2 Key와 trust domain

| ID | 불변조건 |
|---|---|
| `AF-KEY-01` | `K_claim`과 `K_tsu`는 서로 다른 key pair이며 개인키가 Certificate Platform으로 전송·위탁·복구되지 않는다. |
| `AF-KEY-02` | Claim Issuing CA key, TSA Issuing CA key와 status signer key는 용도와 authorization policy가 분리된다. |
| `AF-KEY-03` | Evidence를 사용하는 profile에서는 Attestation trust path를 Claim Signing/TSA certificate trust path와 독립 검증한다. |
| `AF-KEY-04` | Evidence를 사용하는 profile에서는 Evidence signer key와 Evidence subject key를 별도 의미로 검증한다. |

### 11.3 Enrollment decision

| ID | 불변조건 |
|---|---|
| `AF-ENR-01` | caller 인증은 product/service/profile 발급 권한을 자동으로 부여하지 않는다. |
| `AF-ENR-02` | CSR Proof of Possession을 성공하지 않은 공개키에 Leaf를 발급하지 않는다. |
| `AF-ENR-03` | Attestation-required profile은 Evidence subject key, CSR SPKI와 발급 Leaf SPKI가 동일하다. |
| `AF-ENR-04` | client self-assertion, client-supplied root, policy, Reference Value 또는 certificate extension을 최종 판정에 직접 사용하지 않는다. |
| `AF-ENR-05` | mandatory predicate가 모두 성공하고 decision context가 고정되기 전에 CA/HSM을 호출하지 않는다. |
| `AF-ENR-06` | TSA-only idempotent operation의 재시도는 내용이 다른 요청이나 새 certificate issuance로 변형되지 않는다. |
| `AF-ENR-07` | Claim의 `{organization, subscriber, product, CPL, AL, certificate profile, provider profile-or-NONE, environment}` tuple을 request body, server-side freshness context, CSR·필요 Evidence·decision·issuance record와 certificate Subject/profile/AL까지 불변 결속하고 mismatch를 CA/HSM 호출 전에 거부한다. |
| `AF-ENR-08` | TSA의 `{organization, operator, tsaServiceId, tsuInstanceId, certificate profile, provider profile-or-NONE, environment}` tuple을 transaction부터 CSR·decision·issuance record·certificate까지 불변 결속한다. Optional Evidence/challenge/activation을 사용하는 profile은 그 artifact도 같은 tuple에 결속한다. 같은 service 안의 다른 TSU를 포함한 mismatch는 해당 CA/HSM 또는 activation authorization 전에 거부한다. |
| `AF-ENR-09` | C2PA의 same-key 재사용 금지는 모든 Claim/TSA Subscriber Leaf 발급 이력에 적용하되, cross-encoding identity는 승인된 `keyReuseIdentity` profile로만 판정한다. Profile 미승인 동안 issuance를 비활성화한다. |
| `AF-ENR-10` | X.509 certificate serial은 Issuing CA별, TimeStampToken serial은 TSA service Subject 전체 TSU·rotation별로 고유하고, `serialNamespace`는 TSU별 할당 후 다른 TSU에 영구 재사용하지 않는다. |
| `AF-ENR-11` | TSA idempotency identity는 인증된 operator+operation/transaction에 결속한다. Challenge를 쓰는 TSA profile은 challenge도 같은 scope에 결속하고 quota는 TSA service 범위로 강제한다. |

### 11.4 Lifecycle과 failure

| ID | 불변조건 |
|---|---|
| `AF-LIFE-01` | X.509 certificate 상태, Claim key acceptance와 외부 TSA key activation 상태를 서로 다른 state domain으로 관리한다. |
| `AF-LIFE-02` | 선택한 profile에 필요한 provider/trust dependency가 unknown, disabled, stale, expired, revoked 또는 rollback이면 그 profile의 production 발급을 허용하지 않는다. |
| `AF-LIFE-03` | mandatory trust predicate는 운영자 수동 승인이나 waiver로 `PASS`가 될 수 없다. |
| `AF-LIFE-04` | production과 non-production의 CA key, credential, trust activation과 artifact namespace를 공유하지 않는다. |
| `AF-LIFE-05` | Certificate Platform은 외부 offline key의 즉시 사용 중단을 보장한다고 주장하지 않는다. |
| `AF-LIFE-06` | TSU가 declared accuracy 밖 drift를 탐지하면 즉시 TimeStampToken 발급을 중단하고, 공인 통지된 leap second 동안 synchronization을 유지한다(`C2PA-REQUIRED`). |
| `AF-LIFE-07` | On-Device TSA는 UTC(k)-traceable online source와 최소 24시간마다 synchronization을 시도한다(`C2PA-REQUIRED`). |
| `AF-LIFE-08` | 24시간 sync-attempt miss 시 incident와 신규 activation 차단을 적용한다. 기존 TSU stop은 승인된 `ARCH-DECISION` offline cutoff 또는 accuracy/traceability failure가 별도로 성립할 때만 요구한다. |

### 11.5 Accountability와 privacy

| ID | 불변조건 |
|---|---|
| `AF-AUD-01` | 발급 record는 Claim/TSA authorization tuple, caller, CSR/key digest, policy version과 certificate serial/digest를 연결하고, Evidence를 사용한 경우에만 그 digest/verdict와 provider/trust version을 추가한다. |
| `AF-AUD-02` | 감사·metric·error에 private key, secret, 불필요한 Raw Evidence 또는 직접 장치 식별자를 기록하지 않는다. |
| `AF-AUD-03` | Raw Evidence 저장은 provider 검증 또는 법적 필요와 privacy 승인이 있는 최소 범위·기간으로 제한한다. |

### 11.6 신뢰 경계·위협·불변조건 교차 추적

이 표는 foundation 수준의 crosswalk다. 외부 원문의 정확한 requirement locator, 구현과 test/evidence 연결은 05의 RTM이 소유한다.

| Threat | 관련 경계 | 근거 수준 | 대응 불변조건 | 상세 owner |
|---|---|---|---|---|
| `TH-01` key substitution | `TB-01`, `TB-02`, `TB-03`, `TB-04`, `TB-05` | C2PA/CPS | `AF-KEY-04`, `AF-ENR-02`, `AF-ENR-03` | 02, 05 |
| `TH-02` replay | `TB-03`, `TB-04` | CPS/ARCH | `AF-ENR-06`, `AF-ENR-11`, `AF-AUD-01` | 02, 05 |
| `TH-03` purpose confusion | `TB-01`, `TB-02`, `TB-06` | C2PA/RFC/ARCH | `AF-KEY-01`, `AF-KEY-02`, `AF-KEY-03` | 02, 03, 04 |
| `TH-04` trust injection | `TB-03`, `TB-04` | CPS/ARCH | `AF-ENR-04`, `AF-LIFE-02` | 02, 04 |
| `TH-05` policy rollback | `TB-04`, `TB-07`, `TB-09` | CPS/ARCH | `AF-LIFE-02`, `AF-LIFE-03`, `AF-LIFE-04` | 04, 05 |
| `TH-06` duplicate issuance | `TB-03`, `TB-05`, `TB-06` | C2PA/CPS/ARCH | `AF-ENR-06`, `AF-ENR-09`, `AF-ENR-10`, `AF-ENR-11` | 02, 05 |
| `TH-07` CA confused deputy | `TB-05`, `TB-06` | CPS/ARCH | `AF-ENR-04`, `AF-ENR-05`, `AF-KEY-02` | 02, 04 |
| `TH-08` raw signing abuse | `TB-01`, `TB-02`, `TB-03`, `TB-06` | C2PA/RFC/ARCH | `AF-SCOPE-01`, `AF-SCOPE-02`, `AF-SCOPE-03`, `AF-KEY-01` | 03, 05 |
| `TH-09` TSA rollback | `TB-02` | C2PA/RFC/CPS | `AF-ENR-10`, `AF-LIFE-01`, `AF-LIFE-06` | 03, 04, 05 |
| `TH-10` scope mix-and-match | `TB-03`, `TB-05` | ARCH | `AF-ENR-01`, `AF-ENR-07`, `AF-ENR-08`, `AF-ENR-11` | 02, 04, 05 |
| `TH-11` privileged bypass | `TB-07` | CPS/ARCH | `AF-LIFE-03`, `AF-AUD-01` | 04, 05 |
| `TH-12` provider/CA compromise | `TB-04`, `TB-06`, `TB-07`, `TB-08` | C2PA/CPS/ARCH | `AF-LIFE-02`, `AF-LIFE-05`, `AF-AUD-01` | 04, 05 |
| `TH-13` privacy leakage | `TB-03`, `TB-04`, `TB-10` | CPS/ARCH | `AF-AUD-02`, `AF-AUD-03` | 04, 05 |

## 12. 품질 속성과 공통 설계 제약

| 속성 | 공통 요구 | 정량값 owner |
|---|---|---|
| Security | 최소 권한, defense in depth, mandatory fail-closed, HSM key confinement | 04, 05 |
| Correctness | deterministic policy, strict parsing, profile schema validation, explainable denial | 02, 05 |
| Consistency | Claim freshness/replay marker·issuance record·serial uniqueness; TSA challenge/idempotency의 원자적 관계 | 02 |
| Availability | issuance 장애가 무검증 발급으로 완화되지 않으며 status service는 별도 가용성 목표를 가짐 | 04 |
| Recoverability | TSA retry/response loss와 partial activation을 reconciliation 가능하게 기록 | 03, 04 |
| Auditability | 입력 digest와 dependency/version을 decision·certificate에 추적 | 04, 05 |
| Privacy | 데이터 최소화, purpose limitation, encrypted exception storage와 retention | 04 |
| Interoperability | C2PA certificate profile, Claim signature와 RFC 3161 token의 독립 검증 | 03, 05 |

이 문서에서는 SLO, RTO/RPO, retention day, challenge TTL, certificate validity 또는 algorithm 허용 목록을 임의 확정하지 않는다. 해당 값은 외부 원문, CPS와 provider/deployment 조건을 대조하여 canonical owner에서 결정한다.

## 13. 결정 기록과 완료 기준

### 13.1 결정 기록

| ID | 결정 | 상태 | 결과 |
|---|---|---|---|
| `OD-01` | 기본 deployment/tenant model | `DECIDED` | 삼성전자 전용 single-tenant, multi-product/service platform. Production과 non-production은 별도 security environment로 분리 |

현재 이 문서의 공통 경계에 열린 결정은 없다. 향후 상세화 과정에서 공통 경계를 바꾸는 선택은 이 표에 추가하고 사용자 확인 없이 확정하지 않는다. provider별 OID, Evidence schema, validity, trusted-time source와 retention 같은 값은 05의 provider/deployment decision backlog에서 관리한다.

### 13.2 문서 완료 기준

다음 조건을 모두 만족하면 이 문서를 foundation baseline으로 승인할 수 있다.

- Certificate Platform과 외부 Generator/On-Device TSA의 납품 경계가 이해관계자에게 동일하게 해석된다.
- 실제 runtime signing 기능이 서버 기능 또는 CA/HSM 책임으로 오해될 여지가 없다.
- 두 Leaf, 세 trust path와 각 private-key custody가 명확히 구분된다.
- 모든 논리 컴포넌트에 소유 책임, 금지 책임과 authoritative state가 지정된다.
- 신뢰 경계와 주요 데이터 흐름이 threat와 공통 불변조건에 연결된다.
- `AF-*` 불변조건이 05의 RTM·test에 추적된다.
- 02~05가 삼성전자 전용 single-tenant, multi-product/service와 production/non-production 분리 가정을 동일하게 사용한다.
- 02~05 상세 설계가 이 문서의 범위와 불변조건을 위반하지 않는다는 독립 감사 결과가 남는다.

현재 상태는 **foundation 본문 작성 완료, baseline 미승인**이다. 02~05가 아직 `OD-01`, `TB-*`, `TH-*`, `AF-*` locator를 실제로 인수하지 않았으므로 위 마지막 세 완료 조건은 후속 상세화와 회귀 감사 전까지 열린 integration blocker로 남는다.

## 14. 후속 상세 설계 입력

| 문서 | 이 문서에서 넘기는 입력 |
|---|---|
| 02 Certificate Enrollment | `OD-01` product/service/environment scope, `TB-03~06`, Claim/TSA authorization tuple, `AF-ENR-*`, key binding과 two-domain issuance boundary |
| 03 External Runtime Acceptance | `OD-01` product/service scope, `TB-01~02`, runtime non-transit boundary, `K_claim`/`K_tsu` custody, activation device-side acceptance, `AF-SCOPE-*`, `AF-KEY-*`, `AF-LIFE-06~08` |
| 04 Security and Operations | `OD-01` environment model, `TB-04`, `TB-06~10`, privileged boundary, trust/lifecycle state separation, `AF-LIFE-*`, audit/privacy constraint |
| 05 Conformance and Roadmap | `OD-01`, 모든 `TB-*`·`TH-*`·`AF-*` catalog, source/level crosswalk와 release-blocking condition |

01은 위 공통 계약을 소유하며 02~05의 세부 내용을 다시 기술하지 않는다. 후속 문서가 구체화되면서 공통 계약 자체를 바꿔야 할 경우, 해당 문서만 예외로 두지 않고 01의 결정과 영향 범위를 먼저 갱신한다.

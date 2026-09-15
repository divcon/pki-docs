# C2PA Signing Credential Issuance Architecture Overview

> 상태: Certificate Platform의 범위·책임·공통 설계 기준 / not implementation-ready. 이 프로젝트가 제공하는 기능은 외부 단말 서명키에 대한 Leaf 인증서 발급·상태 관리이며, runtime 콘텐츠 서명 기능은 제공하지 않는다. Provider·배포별 산출물과 21절 gate가 승인되기 전에는 production profile을 활성화하지 않는다.

> **2026-09-02 TSA enrollment 정정:** C2PA 원문은 On-Device TSA의 TEE 실행, TEE 내 TSU key 생성·보관, timestamp 전용 key와 TSU당 단일 active key를 runtime/implementation/operations 의무로 규정하지만, 이를 TSA Leaf API 호출마다 Compound Evidence로 제출하라고 규정하지 않는다. 기본 TSA enrollment는 secure credential, CA business practices의 I/A/V, key ownership과 TSA CSR/certificate profile을 검증한다. 아래 Custom Attestation 내용은 명시적으로 선택한 optional CPS/provider 확장 profile에만 적용한다.

> **2026-09-04 Claim Signing enrollment 정정:** 공식 명칭은 **C2PA Claim Signing Certificate**이며, AL1과 AL2는 독립적으로 판정한다. Claim Signing 인증 방식, request body, CSR/Dynamic Evidence 조건과 운영 결정의 canonical 프로젝트 소유자는 [Claim Signing enrollment 문서 세트](claim-signing-enrollment-request/README.md)다. 이 문서 세트는 endpoint·response·state 같은 일반 API를 설계하지 않는다. C2PA가 정한 AL2 의미 요구는 O.1~O.4이지만 provider artifact 개수는 원문에 규정되지 않는다. 선택된 provider profile의 개수를 프로젝트 `evidenceItems` cardinality `1..N_p`와 구분한다. `RENEWAL`은 같은 key 갱신 의미로 받아들이지 않고, 새 key·새 CSR은 `REKEY`로 처리한다.

## 1. 문서 목적과 확정된 아키텍처

이 문서는 Certificate Platform이 외부 단말의 두 서명키를 검증하고 Leaf 인증서를 발급하는 구조를 정의한다. 단말의 C2PA Claim 서명과 RFC 3161 Time-Stamp Token 생성은 발급 인증서의 적격성과 상호운용을 확인하기 위한 외부 통합 계약이지 이 프로젝트의 구현 산출물이 아니다.

### 1.1 System of Interest와 납품 범위

| 구분 | 범위 |
|---|---|
| 이 프로젝트가 구현·운영 | Subscriber/TSA operator 등록, Claim 인증·request-body 검증, TSA enrollment/activation API와 idempotency, CSR 및 profile-conditional Attestation 검증, policy engine, Claim/TSA Issuing CA, Leaf/chain 관리, repository, OCSP/CRL, revocation, audit |
| 외부 요청자 전제 | 단말 보안 경계에서 `K_claim`/`K_tsu` 생성, CSR 및 해당 profile이 요구하는 Evidence 생성, 발급 인증서 설치, private key 보호 |
| 외부 상호운용 계약 | Generator Product의 C2PA Claim 서명·Manifest 조립, TSA TA의 trusted time·RFC 3161 TimeStampToken 생성, Validator 검증 |
| 명시적 비범위 | Asset/Assertion/Claim/Manifest 생성, COSE Claim 서명, RFC 3161 token 서명, trusted-time runtime, private-key escrow/recovery, remote/arbitrary payload signing, network TSA endpoint |

이 문서에서 “구현 완료”는 Overview의 문장을 코드로 옮기는 것만 뜻하지 않는다. Certificate Platform 구현, 승인된 Claim request-body schema·TSA API·인증서 profile, CA CPS, 적용 profile의 Evidence/provider trust material, 운영 통제 및 검증 증거가 모두 release gate를 통과해야 한다. 외부 Generator Product나 TSA TA 자체의 구현 완료를 뜻하지 않는다. 10~12절은 외부 컴포넌트가 발급 인증서를 올바르게 사용할 수 있는지 확인하기 위한 acceptance contract이며 서버 기능 요구가 아니다. 따라서 **Overview 단독 구현만으로 전체 C2PA 설계나 production readiness가 완료되지 않는다.**

완료 판정의 경계는 다음과 같다.

| 질문 | 판정 |
|---|---|
| 이 문서가 정의하는 서버 제품은 무엇인가? | `K_claim`용 Claim Signing Leaf와 `K_tsu`용 TSA Time-Stamp Signing Leaf를 발급·상태 관리하는 Certificate Platform |
| 서버가 C2PA Manifest/Claim을 실제로 서명하는가? | 아니오. 외부 Generator Product가 `K_claim`으로 서명한다. |
| 서버가 RFC 3161 Time-Stamp Token을 실제로 서명하는가? | 아니오. 외부 On-Device TSA가 TEE 내부 `K_tsu`로 서명한다. |
| 이 Overview 구현만으로 완료되는가? | 아니오. 승인된 세부 계약·CPS·provider profile·시험 및 운영 증거가 추가로 필요하다. |
| 이 프로젝트 밖에서 별도로 완성할 것은 무엇인가? | Generator의 Manifest/Claim 생성·서명, On-Device TSA runtime/trusted time/token 생성, Validator 상호운용 |

이 프로젝트의 최상위 아키텍처 결정은 다음과 같다.

1. 외부 Generator Product의 C2PA Claim 서명은 단말이 보유한 Claim Signing Key(`K_claim`)로 수행한다.
2. 외부 On-Device TSA의 RFC 3161 Time-Stamp Token 서명은 단말 TEE 내부의 TSA Trusted Application(TSA TA)이 보유한 TSU Signing Key(`K_tsu`)로 수행한다.
3. 서버는 Manifest, Claim 또는 Time-Stamp Token을 대신 서명하지 않는다.
4. 서버는 CSR/key ownership, 제품·TSA service 적격성 및 해당 profile이 요구하는 경우에만 Attestation Evidence를 검증하고 다음 두 종류의 Leaf 인증서를 발급한다.
   - `K_claim`에 대한 C2PA Claim Signing Leaf 인증서
   - `K_tsu`에 대한 C2PA TSA Time-Stamp Signing Leaf 인증서
5. `K_claim`과 `K_tsu`의 개인키는 서버로 전송하거나 서버에 위탁하지 않는다.
6. 단말의 Rich Execution Environment(REE)는 요청과 결과를 전달하는 통로이며, 보안 판정의 신뢰 주체로 사용하지 않는다.

따라서 서버는 **remote signing service**가 아니라 다음 역할을 수행하는 **CA/RA 및 certificate enrollment system**이다.

```text
서버가 하는 일
  - Subscriber와 제품 적격성 확인
  - challenge 발급 및 replay 방지
  - CSR Proof of Possession 검증
  - profile이 요구하는 경우 Attestation Evidence 검증
  - 인증서 프로파일 구성
  - Leaf 인증서 발급
  - 인증서 상태·폐기·감사 기록 관리

서버가 하지 않는 일
  - Asset 또는 Manifest 생성
  - C2PA Claim 서명
  - 단말을 대신한 RFC 3161 Timestamp 서명
  - 단말 개인키 생성·보관·복구
  - REE가 보낸 자기 선언을 Attestation 판정으로 신뢰
```

## 2. 적용 기준과 요구 수준

이 아키텍처는 다음 기준을 함께 적용한다.

| 구분 | 기준 | 적용 내용 |
|---|---|---|
| C2PA 서명 상호운용 | Content Credentials Specification 2.4 | 외부 Generator/TSA acceptance contract, COSE `x5chain`, `sigTst2`, timestamp 요청·검증 |
| C2PA 제품 적합성 | C2PA Conformance Program v0.2 | Generator Product, CPL, Assurance Level 및 제출 증거 |
| Claim Signing 인증서 | C2PA Certificate Policy v0.2 | AL1/AL2 Claim Signing Leaf 발급 및 인증서 프로파일 |
| On-Device TSA | C2PA Certificate Policy v0.2 | TEE 실행, TEE 키 보관, 신뢰 시간 및 TSA 운영 요구 |
| Timestamp 프로토콜 | RFC 3161, RFC 5816 | TimeStampReq/Resp, TSTInfo, CMS, nonce 및 ESSCertIDv2 |
| 인증서 요청 | PKCS#10, X.509 | CSR 구조, Proof of Possession, 공개키 및 인증서 확장 |
| 단말 Attestation | Claim AL2 또는 optional TSA CPS/provider profile | profile-conditional Evidence, 신뢰 체인 및 Reference Value |

요구 수준은 다음과 같이 구분한다.

- **C2PA 필수**: C2PA Certificate Policy 또는 Content Credentials Specification의 규범 요구
- **RFC 필수**: RFC 3161, RFC 5816, PKCS#10 또는 X.509의 규범 요구
- **CPS 필수**: 이 CA가 안전한 On-Device TSA Leaf 발급을 위해 추가하는 운영 정책
- **설계 결정 필요**: production 구현 전에 OID, schema, 수명 또는 운영 주체를 확정해야 하는 항목

Custom Attestation의 특정 필드 이름과 wire format은 C2PA가 표준화한 것이 아니다. Claim AL2에는 C2PA Dynamic Evidence 요구가 적용되지만 TSA enrollment에서는 optional CA CPS/provider 확장이다. C2PA 공통 요구와 혼동하지 않고 별도 profile로 버전 관리한다.

## 3. 시스템 컨텍스트

### 3.1 전체 구조

```text
┌──────── External Subscriber Device / not delivered ───────────┐
│                                                               │
│  ┌──────────── REE / Generator Product Application ────────┐  │
│  │ Asset 처리                                               │  │
│  │ Assertion·Claim·Manifest 구성                            │  │
│  │ Enrollment API 전달                                     │  │
│  │ RFC 3161 TimeStampReq 전달                              │  │
│  └───────────────┬─────────────────────────┬────────────────┘  │
│                  │                         │                   │
│                  ▼                         ▼                   │
│  ┌──── Claim Signing boundary ──┐   ┌──── TEE / TSA TA ────┐ │
│  │ K_claim 생성·보관            │   │ K_tsu 생성·보관       │ │
│  │ C2PA Claim 서명              │   │ 신뢰 시간 관리        │ │
│  │ Claim Signing Leaf 사용      │   │ RFC 3161 TST 생성     │ │
│  └──────────────────────────────┘   │ TSA Signing Leaf 사용 │ │
│                                     └──────────┬─────────────┘ │
│                                                │               │
│  ┌─ Profile-conditional Attestation Service / AK ─▼──────────┐ │
│  │ Evidence-required profile의 키/TA/TEE 상태 Evidence      │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬────────────────────────────────┘
                               │ CSR + profile-conditional Evidence, TLS
                               ▼
┌──────────── Delivered and operated Certificate Platform ──────┐
│ Claim Request Body Validation / TSA Enrollment API            │
│   ├─ Subscriber/CPL 검증                                      │
│   ├─ Claim freshness context / TSA transaction·challenge       │
│   ├─ Attestation Verifier (Evidence-required profile만)        │
│   ├─ Reference Value / Provider Registry (동일 조건)           │
│   └─ Certificate Policy Engine                                │
│                                                               │
│ Issuing CA                                                    │
│   ├─ Claim Signing Issuing CA → Claim Signing Leaf            │
│   └─ TSA Issuing CA           → TSA Time-Stamp Signing Leaf   │
│                                                               │
│ OCSP/CRL · Certificate Repository · Audit/Incident Management │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 신뢰 경계

| 경계 | 신뢰 수준 | 원칙 |
|---|---|---|
| REE 애플리케이션 | 비신뢰 | 값 전달과 UX만 담당하며 보안 판정 근거를 직접 만들지 않음 |
| Claim Signing Key 영역 | 신뢰 대상 | `K_claim` 사용을 허가된 Claim signing 동작으로 제한 |
| TSA TA | 신뢰 대상 | `K_tsu`, 신뢰 시간 및 RFC 3161 처리의 보안 경계 |
| Attestation Service/AK | 신뢰 대상 | 키·TA·TEE 상태를 trusted source에서 수집하여 Evidence 서명 |
| 네트워크 | 비신뢰 | TLS와 request-context binding으로 보호; transaction/challenge는 TSA-only 계약에 적용 |
| Claim Request Body Validator / TSA Enrollment API | 보안 경계 | 공통 인증·replay·입력 크기/형식 제한; 상태 전이는 TSA-only |
| Attestation Verifier | 보안 경계 | 요청자가 아닌 서버 Trust Store와 Reference Value로 판정 |
| Issuing CA/HSM | 최고 신뢰 경계 | Leaf 발급키 보호, 다중 통제, 최소 권한 및 감사 |

## 4. 키와 인증서 모델

### 4.1 키 종류

| 키 | 소유 위치 | 용도 | 서버 전달 |
|---|---|---|---|
| `K_claim` | 단말 보안 키 저장소/TEE | C2PA Claim 서명 | 공개키만 CSR/Evidence로 전달 |
| `K_tsu` | TSA TA가 실행되는 TEE | RFC 3161 Time-Stamp Token 서명 | 공개키는 기본적으로 CSR로 전달; optional profile은 Attestation에도 결속 |
| Attestation Key(AK) | TEE Attestation Service | Evidence 또는 Attestation Leaf 서명 | 인증서/공개키 체인만 전달 |
| Claim Signing Issuing CA Key | 서버 HSM | Claim Signing Leaf 발급 | 외부 반출 금지 |
| TSA Issuing CA Key | 서버 HSM | TSA Signing Leaf 발급 | 외부 반출 금지 |

`K_claim`과 `K_tsu`는 서로 다른 키여야 한다. 인증서 EKU, 키 사용 목적, 수명주기와 폐기 사유도 분리한다.

```text
K_claim + Claim Signing Leaf
  └─ C2PA Claim 서명에만 사용

K_tsu + TSA Time-Stamp Signing Leaf
  └─ RFC 3161 Time-Stamp Token 서명에만 사용
```

### 4.2 인증서와 Evidence의 구분

```text
Attestation Root
  └─ Device/OEM Attestation Issuing Certificate
       └─ Attested Key Leaf 또는 Evidence Token
            ├─ K_claim 또는 K_tsu 공개키
            └─ challenge + key/workload/platform claims

C2PA Claim Signing CA Chain
  └─ Claim Signing Leaf(K_claim)

C2PA TSA CA Chain
  └─ TSA Time-Stamp Signing Leaf(K_tsu)
```

- Attestation Leaf/Evidence는 인증서 발급 심사를 위한 증거다.
- Claim Signing Leaf와 TSA Signing Leaf는 실제 서명 결과의 검증에 사용한다.
- Attestation Evidence와 원본 Attestation Chain을 최종 Leaf 인증서에 복사하지 않는다.
- 요청에 포함된 Attestation Root는 신뢰하지 않는다. 서버 Trust Store에 사전 등록된 Root만 사용한다.

## 5. 두 개의 독립적인 인증서 발급 경로

### 5.1 Claim Signing Leaf 발급

Claim Signing Leaf는 Generator Product의 `K_claim`에 발급한다.

Claim Signing 요청자는 인증된 Subscriber여야 한다. Signed Notice를 onboarding proof로 받은 경우에는 검증·보관하지만, 현재 interim production rule에서는 그 유무와 별개로 authenticated public CPL의 `status=conformant` record가 있어야 하며 그 Subscriber DN과 요청 주체가 일치해야 한다. 요청 AL은 해당 record의 Max Assurance Level을 넘을 수 없고, AL2 Evidence provider는 record의 허용 `attestationMethods` 및 CA provider profile과 일치해야 한다. Accepted product의 Max Assurance Level이 2이면 AL1/AL2 경로를 한 enablement unit으로 보고 둘 중 하나라도 준비되지 않은 동안 둘 다 비활성화한다(CP:465-467; Program:440-445). CP의 pre-public Notice 허용과 Conformance Program의 public-CPL-only 문구 사이 충돌 및 해소 조건은 [Claim gap register](claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md#7-gap-and-clarification-register)가 소유한다.

```text
1. 서버가 Subscriber, CPL record, 요청 AL과 product status 확인
2. 선택 provider profile에 필요한 경우 서버가 request-scoped freshness·audience context를 생성·보유
3. 단말이 K_claim 생성
4. 단말이 K_claim CSR과 적용 가능한 request-bound Attestation Evidence 생성
5. 서버가 request body, CSR PoP, Evidence, CPL, AL과 freshness/binding predicate 검증
6. Claim Signing Issuing CA가 동일 K_claim 공개키에 Leaf 발급
7. 단말이 Leaf와 chain을 K_claim에 연결하여 저장
```

Claim Signing AL2인 경우 다음 바인딩이 필수다.

```text
Evidence가 증명한 subject key
  == CSR.subjectPublicKeyInfo
  == 발급된 Claim Signing Leaf.subjectPublicKeyInfo
```

AL2 Evidence는 Generator Product의 O.1~O.4를 모두 증명해야 한다.

- O.1: CPL에 등록된 승인 제품 인스턴스
- O.2: `K_claim`의 하드웨어 생성·보관 및 possession
- O.3: Claim Generator와 실행 플랫폼의 무결성·패치 상태
- O.4: Asset/Assertion 처리 경로의 무결성·패치 상태

AL1은 C2PA 정책상 AL2와 동일한 하드웨어 Evidence를 요구하지 않지만, 안전한 enrollment 인증과 CSR PoP는 필요하다.

### 5.2 TSA Time-Stamp Signing Leaf 발급

TSA Signing Leaf는 TSA TA의 `K_tsu`에 발급한다.

TSA 요청자는 임의 Subscriber가 아니라 해당 CA Applicant의 TSA governance, business practices와 계약 아래 사전 승인된 TSA operator여야 한다. 서버는 operator에 불변 `tsaServiceId`를 등록하고, 별도 권한·quota 검사를 거쳐 TSU slot의 `tsuInstanceId`와 최종 Subject DN을 서버 측에서 결정한다. 요청자가 임의로 만든 TSA/TSU 식별자나 Subject DN은 발급 권한 또는 단일 활성키 판정에 사용하지 않는다.

```text
1. 서버가 승인된 TSA operator와 `tsaServiceId`, 앞서 발급한 `tsuInstanceId`/TSA-service-wide unique `serialNamespace` slot을 확인해 enrollment transaction에 바인딩
2. TSA TA가 TEE 내부에서 K_tsu 생성
3. TSA TA가 K_tsu로 PKCS#10 CSR 서명하여 이 architecture가 선택한 key ownership 증명 생성
4. REE가 CSR을 enrollment transaction으로 전달
5. 서버가 TSA operator/service I/A/V, CSR PoP, TSA CSR/profile과 CA policy 검증
6. TSA Issuing CA가 동일 K_tsu 공개키에 TSA Signing Leaf 발급
7. TSA TA가 Leaf와 chain을 K_tsu에 연결하여 저장
```

C2PA Certificate Policy는 TSA Leaf에 Claim Signing의 AL1/AL2 Dynamic Evidence 모델을 적용하지 않는다. TEE 실행·TEE key 보관·timestamp 전용·single-active-key는 runtime/implementation/operations 의무이며, 설계 검토, TEE enforcement, 시험, TSA practices/CPS와 운영 감사로 보증할 수 있다. 이를 enrollment 요청의 signed Evidence로 입증하는 방식은 표준 필수가 아니라 선택적 CA CPS/provider 확장이다.

optional attestation profile을 명시적으로 선택한 경우에만 다음 키 바인딩을 추가로 강제한다.

```text
provider profile이 고정한 Evidence.attestedSubjectKey
  == 형식별 재계산한 CSR.subjectPublicKeyInfo
  == 형식별 재계산한 발급 TSA Signing Leaf.subjectPublicKeyInfo
```

그 optional provider version은 `attestedSubjectKey` 표현을 정확히 하나로 고정한다. `DER_SPKI`는 strict DER `SubjectPublicKeyInfo` 전체 byte를 비교하고 `SHA256_DER_SPKI`는 그 exact DER byte의 SHA-256 32-byte 값을 비교한다. Cross-encoding public-key identity는 별도의 승인된 `keyReuseIdentity` profile이 있을 때만 사용한다. 현재 그 profile은 `TBD`이므로 임의 normalized-key digest를 계산하지 않는다. Claim AL2에는 별도로 C2PA Dynamic Evidence 요구가 적용된다.

## 6. TSA Certificate Enrollment API 논리 계약

이 절은 기존 On-Device TSA enrollment·activation 설계에만 적용하며 Claim Signing에는 적용하지 않는다. Claim Signing은 [인증·enrollment 요구사항](claim-signing-enrollment-request/README.md)과 [request body](claim-signing-enrollment-request/01-Enrollment-Request-Body.md)만 별도 문서가 소유한다. TSA Certificate Platform은 다음 versioned operation을 제공하며, production 착수 전 별도 승인되는 machine-readable TSA API schema가 조건부 필드와 상태별 배타 조건을 고정해야 한다.

| Operation | 목적 |
|---|---|
| `POST /v1/tsa-services/{tsaServiceId}/tsu-slots` | 승인된 TSA 운영자가 수량 제한 안에서 서버 식별 TSU slot과 영구 비재사용 `serialNamespace` 생성 |
| `POST /v1/enrollments` | profile별 transaction 생성; Evidence/challenge-using profile만 challenge 추가. TSA는 기존 server-issued TSU slot을 참조 |
| `POST /v1/enrollments/{transactionId}/submission` | CSR과 조건부 Evidence 제출 |
| `GET /v1/enrollments/{transactionId}` | 상태, 안정적 오류 또는 발급 결과 조회 |
| `POST /v1/enrollments/{transactionId}/activations` | TSA activation ID와 Prepare challenge/binding을 먼저 생성 |
| `POST /v1/activations/{activationId}/prepare-receipt` | signed Prepare Receipt를 검증하고 Commit Authorization 반환 |
| `POST /v1/activations/{activationId}/commit-receipt` | 장치의 durable Commit Receipt 제출 및 서버 finalization |
| `GET /v1/activations/{activationId}` | 동일 signed finalization 결과를 idempotent하게 조회 |
| `POST /v1/activations/{activationId}/reconciliation` | durable receipt/token과 append-only journal로 rollback된 projection 복구 |
| `POST /v1/certificates/{certificateId}/revocation-requests` | issuer+serial+certificate digest로 특정한 인증서의 폐기 요청 접수 |

모든 TSA 변경 요청은 TLS, TSA operator의 secure access credential, profile별 authorization과 `Idempotency-Key`를 요구한다. transaction resource는 생성 주체에게만 보이며 다른 tenant의 ID를 사용한 요청은 존재 여부를 노출하지 않고 거부한다.

TSA 프로파일별 사전 조건과 Evidence cardinality는 다음과 같다.

| Profile | 서버가 확인할 등록정보 | Evidence |
|---|---|---|
| `c2pa-on-device-tsa` | 승인 TSA operator, `tsaServiceId`, Subject DN, TSU slot, key ownership/CSR profile | `0`; C2PA TSA base profile |
| `c2pa-on-device-tsa-attested-*` | base 조건 + 승인된 optional CPS/provider profile | `1..N`; 해당 확장을 명시적으로 선택한 경우만 필수 |

### 6.1 Enrollment 시작

요청자는 발급할 프로파일을 명시한다.

```json
{
  "certificateProfile": "c2pa-on-device-tsa",
  "tsaServiceId": "server-registered-tsa-service-id",
  "tsuInstanceId": "server-issued-tsu-slot-id",
  "operation": "REKEY",
  "rotationOfCertificate": {
    "issuerNameHash": "sha256-canonical-issuer-der",
    "serialNumber": "01AB",
    "certificateDigest": "sha256-certificate-der"
  }
}
```

Claim Signing은 이 절의 endpoint, transaction, response와 state 계약 대상이 아니다. TSA operator가 먼저 TSU slot 생성 권한과 quota 검사를 통과하면 서버가 `tsuInstanceId`를 발급한다. 이후 initial enrollment와 re-key는 모두 이 opaque server-issued handle을 참조한다. `INITIAL`은 `rotationOfCertificate`를 금지하고 `REKEY`는 현재 issuer-name hash, serial과 certificate digest를 모두 요구한다. 서버가 service/TSU/tenant/current-certificate binding을 재확인하므로 클라이언트가 매 re-key를 신규 TSU로 위장할 수 없다.

다음 응답 예시는 TSA architecture에만 해당한다.

```json
{
  "transactionId": "server-issued-id",
  "expiresAt": "RFC3339 transaction timestamp"
}
```

`tsuInstanceId`는 앞선 TSU slot 생성 응답의 서버 원본을 transaction에 복사해 반환할 수 있으나 enrollment 요청자가 새 값을 선택하지 않는다.

### 6.2 Enrollment 제출

```json
{
  "transactionId": "server-issued-id",
  "certificateProfile": "c2pa-on-device-tsa",
  "csr": "base64(DER PKCS#10)"
}
```

위 payload가 base TSA submission이다. Optional attestation profile을 선택한 transaction은 `attestationEvidence` 배열을 `1..N` cardinality로 반드시 추가한다. 그 경우 `mediaType`은 provider profile에 따라 `application/pkix-cert`, `application/eat+cwt` 또는 등록된 COSE media type 중 하나를 사용한다. 한 문자열에 여러 형식을 함께 표시하지 않는다. X.509 Evidence profile에서는 `evidence`가 attestation leaf 인증서이고 `x5chain`에는 그 leaf를 중복하지 않은 intermediate들만 넣는다. COSE/EAT profile에서는 `evidence`가 token이고 `x5chain`은 token signer leaf부터 intermediate 순서다. 정확한 위치와 의미는 provider profile이 하나로 고정한다.

규칙은 다음과 같다.

- 아래 규칙은 Evidence를 요구하는 profile에만 적용한다.
- Root 인증서는 전송하지 않거나 참고용으로만 허용한다.
- 신뢰 경로는 서버 Trust Store의 anchor에서 시작한다.
- CSR과 모든 Evidence는 하나의 transaction에 묶는다.
- `attestationEvidence`의 존재와 항목 수는 위 profile decision table로 검증한다.
- 요청자가 지정한 `type`, `covers`, `hardwareProtected` 같은 값은 판정 결과로 신뢰하지 않는다.
- verifier가 서명이 검증된 Evidence에서 추출한 normalized claim만 정책 입력으로 사용한다.
- 알 수 없는 Evidence type/version은 fail-closed 한다.

### 6.3 응답

성공 응답은 발급 인증서와 signer leaf를 검증하는 데 필요한 모든 intermediate CA chain을 leaf의 issuer부터 순서대로 반환한다. trust anchor/root는 반환 목록에 넣지 않는다. 개인키나 signing service handle은 반환하지 않는다.

```json
{
  "transactionId": "server-issued-id",
  "certificateProfile": "c2pa-on-device-tsa",
  "certificate": "base64(DER leaf certificate)",
  "certificateChain": [
    "base64(DER TSA Issuing CA certificate)"
  ]
}
```

서버 API에는 Manifest, Claim, `MessageImprint` 또는 arbitrary payload를 받아 서명하는 endpoint를 두지 않는다. network TSA runtime endpoint도 제공하지 않는다.

## 7. Optional Custom On-Device TSA Attestation Profile

이 절 전체는 CA가 명시적으로 채택한 optional CPS/provider 확장에만 적용한다. Base `c2pa-on-device-tsa` 발급의 C2PA prerequisite가 아니다. 현재 이 architecture의 optional TSA attestation profile은 challenge flow만 정의하며 non-challenge TSA profile은 없다. Non-challenge freshness 선택지는 Claim AL2 provider profile에만 적용하고, TSA에 추가하려면 별도 versioned CPS/provider profile과 감사를 거쳐야 한다.

### 7.1 증명할 사실

이 optional profile의 TSA enrollment Evidence는 최소한 다음 사실을 하나의 검증 가능한 서명 범위로 결합해야 한다.

1. `K_tsu`가 승인된 TEE에서 생성되었다.
2. `K_tsu` 개인키가 non-exportable이다.
3. `K_tsu`가 Timestamp signing 용도로 제한된다.
4. 승인된 TSA TA가 해당 TEE에서 실행 중이다.
5. TSA TA identity/measurement와 `K_tsu`가 같은 Evidence에 결합되어 있다.
6. TEE/TCB가 production, non-debug, non-rollback 상태다.
7. Evidence가 현재 CA transaction challenge에 대한 것이다.

### 7.2 권장 Evidence claims

| 영역 | Claim | 요구 | 검증 목적 |
|---|---|---:|---|
| Profile | `profileId`, `profileVersion` | 필수 | parser와 정책 선택 |
| Freshness | `challenge` | 필수 | 현재 enrollment와 결합 |
| Audience | `audience`/`verifierId` | 필수 | 다른 CA로 Evidence 전용 방지 |
| Transaction | `transactionContext` | 조건부 | 추가적인 요청 바인딩 |
| TSA | `tsaServiceId` | 필수 | 승인된 TSA operator/service와 연결 |
| TSU | `tsuInstanceId` | 필수 | 서버가 발급한 TSU slot 및 단일 signing-active key 관리 |
| Key | `attestedSubjectKeyFormat` + `attestedSubjectKey` | 필수 | provider version이 고정한 `DER_SPKI` 또는 `SHA256_DER_SPKI`로 CSR 및 최종 Leaf와 바인딩; cross-encoding identity는 별도 승인 전 사용 금지 |
| Key | `keySecurityLevel` | 필수 | TEE 또는 승인 보안 수준 |
| Key | `keyOrigin` | 필수 | TEE 내부 `GENERATED` 확인 |
| Key | `nonExportable` | 필수 | 개인키 반출 금지 |
| Key | `keyPurpose` | 필수 | Timestamp 전용 sign 목적 |
| Key | algorithm/curve/size/digest/padding | 필수 | TSA 인증서 정책 적합성 |
| TA | `taUuid`, `taMeasurement` | 필수 | 승인된 TSA TA 식별 |
| TA | signer digest, version | 직접 또는 기준값 | 공급자·버전 적격성 |
| TEE | implementation ID | 필수 | provider profile 선택 |
| TEE | TCB/security version | 필수 | 최소 보안 버전 확인 |
| TEE | lifecycle/debug 상태 | 필수 | production 및 non-debug 확인 |
| TEE | secure boot/rollback 상태 | 지원 시 필수 | 이미지 인증과 downgrade 차단 |

Evidence의 `tsaServiceId`와 `tsuInstanceId`는 enrollment 응답에서 받은 서버 원본과 일치해야 한다. Evidence에 단말의 현재 시각을 넣더라도 인증서 발급 freshness의 신뢰 근거로 사용하지 않는다. Enrollment freshness는 서버 challenge로 판정한다.

### 7.3 Attestation signer 분리

권장 구조는 TSA TA와 Attestation signer를 논리적으로 분리하는 것이다.

- TSA TA: `K_tsu` 생성·사용, CSR, 신뢰 시간, RFC 3161 처리
- Attestation Service/AK: TEE가 제공하는 TA measurement와 키 속성을 읽어 Evidence 서명

동일 TA가 두 역할을 수행한다면 다음 조건이 필요하다.

- Attestation Key 사용이 승인된 TA identity에 하드웨어적으로 제한된다.
- TA가 임의로 전달한 measurement/TCB/debug 값을 그대로 서명할 수 없다.
- 측정값은 TEE core, secure monitor 또는 동등한 trusted source에서 직접 얻는다.
- Self-Assertion만으로 원격 신뢰를 구성하지 않는다.

## 8. CA 서버 검증 순서

서버는 아래 단계를 모두 통과한 경우에만 Leaf 인증서를 발급한다.

1. 호출자의 Subscriber 자격과 인증 수단을 확인한다.
2. Claim Signing이면 request body, credential verdict, Subscriber, profile, CPL, CSR과 server-held freshness/audience context의 결속을 확인한다. TSA이면 §6의 TSA-only transaction 결속을 확인한다.
3. Claim Evidence-required profile은 승인된 freshness/replay predicate와 request-context binding을 확인하고, challenge-using profile만 expected challenge의 유효성과 미사용 여부를 추가 확인한다. TSA transaction expiry는 §6의 TSA-only 계약으로 확인한다.
4. 요청 크기, 항목 수, DER/CBOR/COSE 중첩 깊이 제한을 적용한다.
5. CSR을 strict parser로 해석하고, Evidence-required profile이면 Evidence에도 strict parser를 적용한다. Trailing data, duplicate field 및 비정규 encoding을 거부한다.
6. 요청 profile에 대응하는 공식 `*.csr.schema.json`으로 CSR Subject, SPKI algorithm과 `extensionRequest`를 검증한다. 요청 extension은 존재·값을 검증하지만 최종 인증서에 그대로 복사하지 않는다.
7. CSR `CertificationRequestInfo` 서명을 검증하여 Proof of Possession을 확인한다.
8. Claim Signing 요청이면 signed Notice를 onboarding에 사용한 경우 그 record를 검증하고, 그와 별도로 current public CPL status, Subscriber·DN, Max Assurance Level과 허용 `attestationMethods`를 확인한다. 현재 interim rule에서 Notice alone은 issuance eligibility가 아니다.
9. AL1은 O.1의 secure enrollment authentication과 CSR PoP를 평가하며 현재 Claim Signing contract에서는 `evidenceItems`를 금지한다. 향후 CA가 AL1 CPS attestation 확장을 채택하려면 현재 AL1 profile에 암묵적으로 추가하지 않고 별도 versioned profile과 Operations Decision 승인을 정의한다.
10. AL2와 optional TSA attestation profile만 서버 Trust Store의 anchor로 Evidence 경로를 구성하고 체인 서명, 유효기간, Basic Constraints, Key Usage, path length, policy와 폐기 상태를 검증한다.
11. Evidence-required profile만 Evidence profile/version, signature와 signed byte 범위를 등록된 provider profile로 검증한다.
12. Evidence-required profile은 audience, enrollment context와 subject identity binding을 항상 검증한다. Challenge-using profile은 signed challenge를 서버 원본과 constant-time 비교한다. Non-challenge Claim AL2 profile은 승인된 signed time/counter/nonce 또는 envelope와 replay identity를 검증한다. 현재 optional TSA attestation profile은 모두 challenge-using이다.
13. Evidence-required profile에서 Evidence가 `DER_SPKI`이면 strict DER SPKI byte를 직접 비교하고, `SHA256_DER_SPKI`이면 CSR의 exact DER SPKI를 SHA-256으로 재계산한다. Cross-encoding subject-key 비교는 별도의 승인된 `keyReuseIdentity` profile이 있을 때만 수행한다. 등록 profile과 다른 형식·알고리즘·길이는 거부한다.
14. AL2이면 key protection과 O.1~O.4의 모든 필수 verdict가 `PASS`인지 확인한다.
15. TSA이면 `tsaServiceId`, 서버 발급 `tsuInstanceId`, Subject DN과 business-practices I/A/V를 검증한다. Optional attestation profile일 때만 signed Evidence에서 key/TA/TEE predicate를 검증한다.
16. TSA single-active-key와 optional staged activation은 별도 runtime/implementation acceptance에서 검증한다. Base certificate issuance gate가 signed device state를 요구하지 않는다.
17. 승인된 `keyReuseIdentity` profile과 발급 이력 전체로 같은 key의 renewal 및 Claim/TSA 간 재사용을 확인한다. 현재 identity profile은 `TBD`이므로 모든 Claim/TSA issuance를 비활성화하고, re-key는 새 key·CSR과 전체 재심사를 요구한다.
18. CA 정책으로 최종 인증서 필드를 다시 구성하고 공식 `*.cert.schema.json`으로 pre-issuance template을 검증한다.
19. 발급 직전 Subscriber/product/TSA operator와 issuer/revocation 상태를 다시 확인하고, optional provider profile이면 그 provider/TA 상태도 확인한다.
20. 발급된 Leaf의 SPKI가 CSR SPKI와 같은지 및 최종 DER 인증서가 profile schema에 맞는지 검증한다.
21. Claim은 발급 인증서 기록과 사용한 freshness/replay marker를 함께 확정하고, TSA의 transaction 결과 확정은 §6의 TSA-only 계약을 따른다.

검증 서비스 장애, status unknown, Reference Value 조회 실패 또는 revocation 조회 실패를 성공으로 간주하지 않는다.

## 9. Leaf 인증서 프로파일

Claim Signing Leaf와 TSA Leaf는 각각 `BasicConstraints.pathLenConstraint=0`인 승인된 subordinate Issuing CA에서만 발급한다. Claim Signing Issuing CA와 TSA Issuing CA는 서로 다른 CA key/HSM object와 operator role을 사용하고 각 chain을 C2PA Trust List와 TSA Trust List에 독립 등록한다.

### 9.1 Claim Signing Leaf

Claim Signing Leaf는 C2PA Certificate Policy의 AL1 또는 AL2 프로파일을 그대로 따른다.

| 항목 | AL1 | AL2 |
|---|---|---|
| 최대 유효기간 | 366일 | 90일 |
| Subject | CPL 제품 DN과 일치 | CPL 제품 DN과 일치 |
| 공개키 | RSA 2048+, P-256/384/521 또는 Ed25519 | 동일 |
| Key Usage | `digitalSignature`, `contentCommitment` | 동일 |
| EKU | `c2pa-kp-claimSigning` + email/document signing 중 하나 이상 | 동일 |
| C2PA AL OID | Assurance Level 1 | Assurance Level 2 |
| CPL Record ID | 필수 | 필수 |
| OCSP AIA | 필수 | 필수 |

사람이 읽는 `*.cert.yaml`은 설명용이다. 구현은 `claimSigningLeaf.al1.csr.schema.json`, `claimSigningLeaf.al2.csr.schema.json`, `claimSigningLeaf.al1.cert.schema.json`, `claimSigningLeaf.al2.cert.schema.json`을 version/hash와 함께 고정해 검증한다.

### 9.2 TSA Time-Stamp Signing Leaf

| 항목 | 요구 |
|---|---|
| Version | X.509 v3 |
| 유효기간 | C2PA profile 상한 4110일, 승인될 CPS에 반영할 project 기본·최대 90일 정책 |
| Subject | TSA service의 unique name을 식별하는 C, O, CN |
| 공개키 알고리즘 | RSA 2048+ 또는 EC P-256/P-384/P-521 |
| 인증서 서명 알고리즘 | RSA-PSS/SHA2, RSA/SHA2 또는 ECDSA/SHA2 |
| Ed25519 | 허용하지 않음 |
| Basic Constraints | critical, `cA=false` |
| Key Usage | critical, `digitalSignature`, `contentCommitment` |
| EKU | critical, 정확히 `id-kp-timeStamping` 하나 |
| Certificate Policies | C2PA policy OID `1.3.6.1.4.1.62558.1.1` 포함 |
| AIA/CRL | OCSP AIA 또는 CRL Distribution Point 중 최소 하나. 프로파일 조건 준수 |

TSA Leaf의 EKU나 Key Usage를 Claim Signing 용도와 혼합하지 않는다.

C2PA profile은 TSA service의 unique name과 C/O/CN 존재를 요구하지만 이 프로젝트의 DN canonical encoding까지 정의하지는 않는다. 이 프로젝트는 승인될 CPS/profile에서 RDN 순서를 `C,O,CN`, 각 RDN을 single-valued, DirectoryString을 UTF8String으로 고정한다. 값은 Unicode NFC로 정규화하고 control character와 leading/trailing space를 거부한 뒤 X.501 Name을 DER encoding한다. 그 exact DER byte를 `canonicalTsaSubjectDn`의 비교값으로 사용한다. 서로 다른 `tsaServiceId`는 같은 canonical Subject를 사용할 수 없고 DB global unique constraint로 강제한다. Subject는 TSU가 아니라 TSA service identity이므로 같은 service의 initial/re-key와 여러 TSU certificate는 같은 Subject를 사용하며 요청자 입력으로 바꾸지 않는다.

TSA CSR은 `tsaLeaf.csr.schema.json`, 발급 인증서는 `tsaLeaf.cert.schema.json`으로 검증한다. 공식 CSR profile이 요구하는 Basic Constraints, Key Usage, Extended Key Usage와 Certificate Policies의 `extensionRequest`를 검증하되, CA는 CSR 값을 신뢰해 복사하지 않고 최종 certificate template을 독립적으로 구성한다.

## 10. 외부 단말 acceptance contract: C2PA 2.4 서명 흐름

이 절은 Certificate Platform이 구현하는 runtime이 아니다. 인증서 발급 후 외부 Generator Product와 TSA TA가 발급 결과를 올바르게 사용하는지 검증하는 상호운용 조건이다. 정상 runtime에는 서버 signing API가 개입하지 않는다.

```text
REE / Generator Product
  1. Asset 및 Assertion 생성
  2. Hard Binding과 Claim 구성
  3. C2PA 2.4 Claim signature 입력과 protected header 구성
     - project generator profile은 integer label 33인 x5chain에 Claim leaf와 모든 intermediate 포함
     - trust anchor/root 제외
        │
        ▼
Claim Signing boundary
  4. K_claim으로 Claim 서명
        │
        ▼
REE → TSA TA
  5. v2 timestamp용 CounterSignature Sig_structure의 MessageImprint,
     optional nonce와 certReq=true 전달
        │
        ▼
TSA TA
  6. 신뢰 시간과 정책 상태 확인
  7. TSTInfo 생성
  8. K_tsu와 TSA Signing Leaf로 RFC 3161 TimeStampToken 생성
        │
        ▼
REE / Generator Product
  9. DER TimeStampToken을 CBOR byte string으로 감싸 sigTst2에 결합
 10. Manifest Store 및 최종 Asset 완성
```

C2PA `SHALL` 조건은 `x5chain`을 COSE protected header에 두고 signer leaf부터 모든 intermediate를 순서대로 포함하는 것이다. Root는 C2PA `SHOULD NOT` 포함 대상이며, 이 프로젝트의 신규 Generator acceptance profile은 이를 강화해 root 제외를 필수로 한다. Integer label 33 사용은 C2PA 2.4의 `SHOULD`이며 string `x5chain` label은 deprecated-but-allowed다. 이 프로젝트의 외부 Generator acceptance profile은 신규 생성에 integer 33만 사용하도록 강화하지만 Validator 상호운용 시험은 두 label을 모두 수용하고, 둘 다 있을 때 C2PA 우선순위를 적용해야 한다. C2PA 2.4 timestamp는 deprecated v1 payload를 만들지 않는다. v2 payload는 완성된 `COSE_Sign1_Tagged.signature` field의 serialized CBOR `bstr` 전체이고, 이를 `CounterSignature` context의 Sig_structure에 넣어 계산한 `ToBeSigned`를 hash하여 `MessageImprint`를 만든다. 임의의 Claim JSON이나 Asset 전체를 Timestamp 대상으로 재정의하지 않는다.

## 11. 외부 TSA TA acceptance contract: RFC 3161 처리

### 11.1 요청 입력

TSA TA는 REE에서 다음 값을 받을 수 있다.

- `MessageImprint`: hash algorithm OID와 digest
- `nonce`: optional
- `reqPolicy`: optional
- `certReq`: C2PA 2.4 호출에서는 반드시 `true`
- extensions: policy가 명시적으로 지원하는 것만 허용

REE는 요청을 구성할 수 있지만 다음 보안 결정을 내리지 않는다.

- 허용 hash algorithm
- 적용할 TSA policy
- 신뢰 시간과 accuracy
- token serial number
- TSU 키 선택
- 인증서 chain 포함 여부의 최종 정책

### 11.2 요청 검증

TSA TA는 다음을 확인한다.

1. TimeStampReq version이 v1이다.
2. MessageImprint digest 길이가 algorithm과 일치한다.
3. 허용 hash는 SHA-256, SHA-384, SHA-512뿐이다.
4. 요청 policy가 있으면 지원되는 policy다.
5. 지원하지 않는 extension이 있으면 token을 발급하지 않고 오류를 반환한다.
6. nonce가 있으면 응답 TSTInfo에 같은 값을 넣을 수 있어야 한다.
7. C2PA profile에서 `certReq`가 `true`다. false 요청은 거부하고 호출자가 `certReq=true`인 새 요청을 생성해야 한다. TSA가 false 요청을 내부에서 변조하거나 false 요청에 인증서 chain을 넣지 않는다.
8. 신뢰 시간 상태가 발급 가능 상태다.
9. `SIGNING_ACTIVE`인 `K_tsu`와 유효한 TSA Leaf가 정확히 하나다.

### 11.3 Token 생성

TSA TA는 다음 불변 조건을 지킨다.

- TSTInfo version은 v1이다.
- policy는 실제 적용한 TSA policy를 나타낸다.
- MessageImprint는 요청과 동일하다.
- serialNumber는 같은 service Subject를 공유하는 모든 TSU와 모든 key rotation을 포함한 해당 TSA 범위에서 고유하고 재부팅·장애 후에도 재사용하지 않는다. 서버 발급 8-byte `serialNamespace`와 rollback-safe uint64 counter를 결합하는 [Runtime §7.4](03-On-Device-Runtime.md#74-serial-number와-동시성) 계약을 사용한다.
- `genTime`은 UTC 기반 GeneralizedTime 규칙을 따른다.
- 선언한 accuracy를 TSTInfo 또는 policy로 표현한다.
- 요청에 nonce가 있으면 동일 nonce를 반드시 포함한다.
- token에는 TSA 서명 외의 다른 서명을 넣지 않는다.
- TSA signer certificate identifier를 SigningCertificate/SigningCertificateV2에 포함한다.
- SHA-1 이외의 certificate hash에는 ESSCertIDv2/SigningCertificateV2를 사용한다.
- C2PA profile에서는 CMS SignedData의 `certificates`에 TSA signer leaf와 trust anchor까지 경로 구성에 필요한 모든 intermediate를 포함한다. root는 포함하지 않는다.
- 성공 status에는 TimeStampToken을 포함하고 실패 status에는 포함하지 않는다.

### 11.4 전용키 통제

- `K_tsu`는 RFC 3161 Timestamp 이외의 arbitrary signature에 사용할 수 없다.
- TSA TA 외의 코드가 raw sign primitive로 `K_tsu`를 호출할 수 없어야 한다.
- 한 `tsuInstanceId`에는 한 시점에 하나의 활성 `K_tsu`만 존재한다.
- Debug/development TA는 production TSA Leaf를 사용할 수 없다.

## 12. 외부 TSA TA acceptance contract: 신뢰 시간

이 절도 외부 TSA TA의 적격성과 상호운용을 판정하기 위한 조건이다. C2PA On-Device TSA의 핵심은 단말 벽시계를 그대로 신뢰하지 않는 것이다.

### 12.1 필수 요구

- On-Device TSA는 최소 24시간마다 UTC(k)에 추적 가능한 온라인 시간원과 동기화를 시도한다.
- 선언한 accuracy를 벗어난 것을 탐지하면 Timestamp 발급을 중단한다.
- leap second를 포함한 시간 동기화 정책을 유지한다.
- 권장 accuracy는 1초 이하다.
- 마지막 성공 동기화와 status refresh 후 최대 24시간을 넘기면 Timestamp 발급을 중단한다. 이는 C2PA 공통 요구가 아니라 승인될 CA CPS에 반영할 project 강화 정책이며, 실제 중단 시점은 `min(sync max-age, status max-age, drift/uncertainty accuracy deadline, certificate validity deadline)`이다.

### 12.2 TEE 보호 상태

TSA TA는 최소한 다음 상태를 rollback 방지 가능한 TEE 저장소에 보관한다.

- 마지막 성공 동기화 시각과 신뢰 시간 증거 digest
- 동기화 당시의 trusted time과 monotonic counter
- 추정 가능한 최대 drift/uncertainty
- 적용 중인 time policy/version
- active `K_tsu` 식별자와 certificate serial
- 마지막 발급 token serial 또는 crash-safe serial state
- 마지막으로 승인한 status evidence digest, responder/issuer, certificate ID, `producedAt`/`thisUpdate`/`nextUpdate`와 CRL number
- terminal `REVOKED` latch와 마지막 status monotonic counter
- 발급 가능/중단 상태와 사유

TSA TA는 OCSP/CRL signature와 responder chain, issuer/certificate ID, validity interval과 freshness를 검증한다. stale, `unknown`, signature/chain 실패, rollback된 `producedAt`/CRL number 또는 status 조회 실패는 신규 Timestamp를 중단한다. `REVOKED`는 rollback으로 되돌릴 수 없는 terminal state다.

### 12.3 시간원

허용 가능한 시간원은 CPS에서 명시한다. 예를 들어 C2PA TSA Trust List에 연결되는 Backend TSA를 시간 동기화 증거로 사용할 수 있다. 이 경우 Backend TSA 응답의 서명, MessageImprint, nonce, 인증서 chain과 신뢰 상태를 TA 또는 신뢰 가능한 검증 경로에서 확인한다.

## 13. 인증서 수명주기와 상태 관리

### 13.1 발급·활성화·rotation 상태

인증서 상태, 외부 장치 키 상태와 activation transaction은 서로 다른 상태기계다. CA는 인증서 상태만 권위 있게 소유한다.

```text
Certificate record (CA authoritative):
  ISSUING → ISSUED_VALID → EXPIRED
                         └→ REVOKED (terminal, OCSP/CRL publication)

External TSA device key state (`K_tsu` only; device authoritative, server-observed only):
  STAGED_DISABLED → COMMITTED_DISABLED → SIGNING_ACTIVE → RETIRED → DESTROYED

Activation transaction (server authoritative):
  PREPARED → COMMIT_AUTHORIZED → DEVICE_COMMITTED → SERVER_FINALIZED
     └→ ABORTED (authorization 전만)
              COMMIT_AUTHORIZED/DEVICE_COMMITTED ─→ RECOVERY_REQUIRED
```

Claim Signing certificate의 설치·사용에 의한 acceptance는 발급 전 Agreement gate를 대체하지 않으며, 이 절의 TSA key activation protocol 대상이 아니다. Staged activation을 채택한 경우 서버는 freshness가 있는 authenticated TSA device observation과 `observedAt`을 보관한다. `RECOVERY_REQUIRED`는 TSA activation transaction 상태에만 사용한다. 공개 `SUSPENDED` 상태를 정의하지 않으며 내부 사용 차단은 CP가 요구하는 revocation을 대체하지 않는다.

모든 re-enrollment는 project policy에 따라 새 key와 새 CSR을 사용하고 전체 profile 검증을 다시 수행한다. Challenge를 사용하는 profile만 새 challenge를 사용한다. 같은 public key의 renewal 또는 재발급은 허용하지 않는다. Staged activation을 채택한 TSA 배포에서는 새 Leaf가 X.509 관점상 `ISSUED_VALID`이어도 provider hardware가 해당 key를 `STAGED_DISABLED`로 두고 RFC 3161 sign command를 거부한다. Status service의 `good`은 activation을 뜻하지 않는다.

Staged activation을 채택한 TSA 배포의 initial activation과 re-key는 다음 idempotent protocol을 동일하게 사용한다.

1. 장치는 새 certificate를 `STAGED_DISABLED` key에 설치한다. re-key이면 old key만 `SIGNING_ACTIVE`이고 initial이면 old key가 없다. hardware ACL은 staged key의 RFC 3161 및 raw signing을 모두 거부한다.
2. 클라이언트가 activation resource를 먼저 생성하면 서버가 `activationId`, transaction/profile/operation, 32-byte Prepare challenge, audience, service/TSU/serial namespace, old/new binding, expected counter, HSM 계산 `hardwareBindingDigest`, rollback epoch, provider manifest sequence와 whole-second validity를 저장·반환한다.
3. Attestation signer가 서버 응답 전체, device observed `issuedAt`, `old=SIGNING_ACTIVE|ABSENT`, `new=STAGED_DISABLED`를 묶은 Prepare Receipt를 서명한다. 서버는 TSU별 lock 아래 receipt를 검증하고 짧은 TTL·single-use의 signed Commit Authorization을 저장·반환한다.
4. TEE는 authorization을 검증한 뒤 한 rollback-safe transaction으로 old key를 `RETIRED`, new key를 `COMMITTED_DISABLED`, counter를 `n+1`로 만들고 동일 activation 재호출에 같은 durable signed Commit Receipt를 반환한다. 이 시점에도 Timestamp는 금지된다.
5. 서버는 Commit Receipt를 검증하고 append-only activation journal과 projection을 `SERVER_FINALIZED`로 기록한 뒤 signed Finalization Token을 만든다. 응답 유실 시 GET이 같은 token을 반환한다.
6. TEE는 Finalization Token을 확인한 뒤에만 new key를 `SIGNING_ACTIVE`로 허용한다. 서버 projection rollback은 sealed journal replay와 receipt/token reconciliation으로 복구한다. Journal 자체의 손실·충돌은 서버-side operation 차단, certificate revocation/status publication과 incident로 fail-closed하며, disconnected TEE는 승인된 status/reference-value refresh deadline 안에 중단한다. 즉시 원격 중단을 주장하지 않는다.

Staged activation 기능을 production에 사용할 경우 activation artifact의 정확한 COSE_Sign1 서명 입력, deterministic-CBOR field map, platform/provider 검증키 수명주기, anti-rollback epoch, 만료·재시도와 복구 규칙을 versioned machine contract로 승인해야 한다. 해당 계약과 fault evidence가 없으면 그 activation 방식과 runtime timestamp 사용을 차단한다. 이는 base TSA Leaf issuance에 대한 C2PA prerequisite가 아니다. 격리된 non-production test CA에서 발급한 시험용 인증서는 production status/trust list에 게시하거나 production `SIGNING_ACTIVE`로 전환할 수 없다.

Authorization 전 timeout은 안전하게 abort하고 새 certificate를 폐기한다. Authorization 후 receipt 유실은 장치가 같은 durable receipt를 재전송해 조정한다. receipt 검증 거부, server rollback 의심 또는 counter 충돌은 `RECOVERY_REQUIRED`이며 어떤 key도 임의로 되살리지 않는다. abandoned staged certificate와 상태가 암호학적으로 확인되지 않는 key의 certificate는 폐기한다. 동시 activation은 TSU lock과 expected counter로 하나만 승인한다. 사람의 확인이나 운영자 승인만으로 hardware Evidence를 우회하는 수동 activation은 금지한다. 이 protocol과 hardware-enforced `STAGED_DISABLED`/`COMMITTED_DISABLED` ACL을 입증하지 못하는 provider는 production `ENABLED`가 될 수 없다.

### 13.2 폐기 조건

다음 상황에서 Certificate Platform은 **영향 받은 certificate profile/service/TSU**의 신규 enrollment 또는 activation을 차단하고, CA 정책상 폐기 사유이면 관련 Leaf를 폐기해 상태를 게시한다. Attestation Root/AK/SAK, TA measurement/TCB와 debug lifecycle 사건은 그 dependency를 사용하는 Claim AL2/optional TSA attestation profile의 enrollment 또는 해당 TSA runtime/activation에만 적용하며 base TSA profile을 전역 차단하지 않는다. 외부 Generator/TSA runtime은 최신 authenticated status 또는 승인된 최대 refresh deadline 안에 신규 서명을 중단해야 한다. Certificate Platform은 연결이 끊긴 단말의 즉시 중단을 보장한다고 주장하지 않는다.

- 단말 또는 TA compromise 의심/확인
- Attestation Root/AK/SAK 폐기
- `K_claim` 또는 `K_tsu` 노출 가능성
- 미승인 TA measurement 또는 TCB downgrade
- debug/development lifecycle 전환
- TSA time accuracy 유지 실패가 장기화됨
- 인증서 또는 키의 목적 외 사용
- CPL 제품 status가 `revoked*`로 변경되거나 Claim Signing conformance 상실
- CPS/Certificate Policy 불이행

`revoked*` CPL 상태, 인증되고 유효한 Subscriber/C2PA 폐기 요청, key/제품 compromise와 CP가 정한 사유는 “사용 중단”만으로 대체하지 않고 CA revocation을 수행한다. 인증된 폐기 요청은 72시간 이내 처리한다.

### 13.3 서버 상태 서비스

- Claim Signing Leaf에는 OCSP를 제공한다.
- TSA Leaf/Issuing CA의 상태는 인증서 프로파일과 CP에 따라 OCSP 또는 CRL로 제공한다.
- Subscriber identity는 마지막 확인 후 398일을 넘기기 전에 재인증한다.
- 서버는 발급 인증서와 상태 기록을 만료 후 최소 1년 이상 또는 CPS의 더 긴 기간 동안 보호한다.
- Claim OCSP와 profile이 선택한 TSA OCSP/CRL status service는 current status를 24×7 공개해야 하며 publication freshness와 장애 SLO를 CPS에 수치화한다.
- Certificate Platform의 보장은 상태 정보의 24×7 적시 publication까지다. offline 단말의 즉시 사용 중단을 보장할 수 없다. 외부 On-Device TSA acceptance profile은 최소 24시간마다 trusted-time 동기화와 status 갱신을 시도하고, CPS의 successful-sync/status max-age 또는 더 이른 accuracy/certificate-validity deadline을 넘으면 신규 Timestamp 발급을 중단해야 한다.

## 14. 서버 데이터 모델의 핵심 불변 조건

하나의 Claim issuance 판정 기록은 다음 값을 변경 불가능하게 연결한다.

```text
Subscriber
  + certificate profile
  + request body schema/version과 canonical digest
  + CPL record
  + server-only GP-instance issuance history와 predecessor
  + 해당 provider profile이 요구하는 server-held freshness/audience/replay context
  + CSR digest/DER SPKI digest와 승인된 key-reuse identity(승인된 경우)
  + Evidence가 있으면 그 digest와 chain digest
  + Evidence가 있으면 provider root fingerprint, AK/SAK issuer+serial+SKI, TA measurement/version과 Reference Bundle version
  + 해당 profile이 provider를 사용하면 provider profile/trust store/reference value version
  + 개별 policy verdict
  + 발급 인증서 serial/digest
```

TSA enrollment/activation transaction의 데이터, idempotency identity와 response-loss 재조회 의미는 §6과 §13의 TSA-only 계약이 소유하며 위 Claim 기록에 적용하지 않는다.

Claim issuance 판정은 다음을 보장한다.

- challenge를 사용하는 provider profile에서는 freshness 값이 충분한 엔트로피를 갖고 request evaluation마다 고유하다.
- freshness 값과 replay identity는 Subscriber, profile, CPL, CSR subject key와 하나의 request context에만 결속된다.
- 같은 lineage/key에 대한 동시 요청 중 하나만 발급 단계에 진입한다.
- one-time freshness/replay marker의 사용 여부와 발급 인증서 기록은 함께 보존한다.
- Claim `INITIAL`은 server issuance history에 과거 발급이 없는 경우만 허용하고, `REKEY`는 같은 history의 정확한 predecessor와 새 key를 요구한다. 구·신 certificate overlap/cutover는 승인 lifecycle policy가 없으면 활성화하지 않는다.
- C2PA의 same-key reuse 금지를 전체 Claim/TSA Subscriber Leaf 발급 이력에 적용하되, cross-encoding identity algorithm은 C2PA가 정하지 않는다. `OD-KEY-01`이 typed encoding, byte order, curve/algorithm registry, deterministic serialization과 known-answer vectors를 승인하기 전에는 임의 digest를 만들지 않고 모든 issuance를 비활성화한다.
- Exact DER SPKI와 그 SHA-256은 CSR PoP, 같은 request의 Evidence/최종 Leaf equality와 진단에 사용할 수 있지만 cross-encoding reuse identity가 아니다. 승인된 identity profile이 생기면 그 identifier의 보존·privacy·collision/concurrency 정책도 함께 승인한다.

TSA transaction에 대해서만 다음을 추가 보장한다.

- 같은 idempotency identity와 같은 TSA 요청은 같은 결과를 반환한다.
- 이미 성공한 TSA 요청의 재시도로 새 인증서를 발급하지 않는다.
- CSR 또는 optional Evidence가 달라지면 같은 TSA transaction 재시도로 받아들이지 않는다.
- challenge를 사용하는 TSA profile은 인증서 발급과 challenge 소비 상태를 장애 후에도 하나의 결과로 복구한다.
- `tsaServiceId`, `tsuInstanceId`와 TSA-service-wide unique `serialNamespace`는 서버가 발급하고 Subscriber/TSA operator, canonical Subject DN과 tenant-scoped `hardwareBindingDigest`에 불변 연결한다. Namespace는 같은 TSU의 re-key에 유지하고 다른 TSU에 영구 재사용하지 않는다. `hardwareBindingDigest`는 tenant HSM의 versioned key로 provider profile ID와 canonical hardware handle의 길이 구분 deterministic-CBOR tuple에 HMAC-SHA-256을 적용한다. Raw hardware handle은 검증 뒤 저장하지 않으며, 기존 binding의 재검증 기간 동안 구 HMAC key를 HSM 내부 verification-only 상태로 유지한다.
- 서버 inventory는 authoritative device state라고 주장하지 않는다. Staged activation/telemetry를 채택하면 authenticated observation, receipt counter와 freshness를 저장하고, 그렇지 않으면 승인된 runtime/운영 evidence로 검증한다. Provider TEE는 한 `tsuInstanceId`의 `SIGNING_ACTIVE` key를 최대 하나로 강제한다.
- certificate에서 provider Root/AK/SAK/measurement/Reference Bundle/CPL로 가는 dependency index를 두고 signed status-feed ingest와 mass-revocation dry run으로 72시간 대응 가능성을 검증한다.

## 15. Reference Value와 Provider Profile

이 절의 attestation provider/Reference Value 통제는 Claim AL2와 optional TSA attestation profile에 적용하되 두 profile의 reference tuple을 합치지 않는다. Base TSA profile은 provider Evidence를 요구하지 않는다.

서버는 단말이 보낸 허용 목록을 사용하지 않고 독립적으로 관리하는 기준값과 비교한다.

```text
Provider Profile
  ├─ profile ID/version/media type
  ├─ evidence parser와 signature 규칙
  ├─ trust anchors와 chain policy
  ├─ challenge 사용 여부와 provider-native freshness/replay 방식
  ├─ audience/transaction/subject key 위치와 binding transform
  ├─ normalized claim mapping
  ├─ revocation/status source
  └─ size·TTL·algorithm 제한

Claim AL2 Reference Value Bundle
  ├─ Subscriber/CPL record와 O.1 product package/hash/code-signing identity
  ├─ O.2 requested key/KME security attributes와 CSR subject-key binding
  ├─ O.3 Claim Generator image, patch/revision와 vulnerability decision
  ├─ O.4 모든 content/assertion-processing component inventory와 image/patch/revision
  └─ signer/effective/expiry/sequence/emergency-revoke

Optional TSA Reference Value Bundle
  ├─ 허용 TSA TA UUID/measurement
  ├─ 허용 TA signer/version
  ├─ 최소 TCB/security version
  ├─ 허용 TEE implementation/lifecycle
  ├─ 허용 key security level/algorithm
  ├─ revoked measurement/version
  └─ effective time/version/signature
```

정책 bundle과 Reference Value 변경은 서명·승인·배포·rollback 방지·감사 절차를 가져야 한다. `ACTIVE` 하나와 `NEXT` 하나만 유효기간을 최대 24시간 겹칠 수 있다. verifier는 `effectiveAt < expiresAt`, signed sequence/rollback counter의 단조 증가와 emergency-feed signature/freshness를 강제한다. bundle expiry 뒤 grace 연장은 없으며 emergency revoke는 모든 overlap보다 우선한다. unknown, stale, expired 또는 rollback된 bundle은 fail-closed 한다.

Provider Profile은 임의 설정 묶음이 아니라 서명·승인된 배포 artifact다. 다음 항목이 모두 존재하고 known-answer/negative test vector를 통과한 version만 `ENABLED`로 전환한다.

- profile ID/version, media type, canonical encoding과 signed-byte 범위
- organization enterprise arc에서 배정한 OID 또는 표준 EAT profile identifier
- verification key 위치와 attested subject key 위치
- trust anchor/chain/path/revocation 규칙과 Root 운영자
- challenge 사용 여부와 Claim `OD-FRESHNESS-01` 또는 TSA policy가 승인한 entropy/length/encoding/TTL/transform(사용 시), non-challenge freshness/replay 방식, stable audience; Claim은 Subscriber/CPL/AL/GP-instance/CSR key/request context에, optional TSA는 `tsaServiceId`/`tsuInstanceId`/CSR key와 해당 enrollment context에 결속
- claim cardinality/type/range와 normalized verdict mapping
- Reference Value bundle signer, effective/expiry time, rollback counter와 emergency revoke 절차
- parser/verifier version, 최대 size/depth/item 수와 알고리즘 allowlist
- positive, malformed, replay, wrong-audience, wrong-key, revoked-root와 unknown-version test vector

Verifier는 CA/HSM과 별도 권한 경계의 격리 서비스로 배치하고 certificate signing 권한을 갖지 않는다. Claim Signing Issuing CA와 TSA Issuing CA는 서로 다른 CA key와 HSM object/role을 사용한다. 동일 HSM cluster를 쓰더라도 partition 또는 동등한 access-policy 경계를 둔다.

## 16. 실패 정책

Base Claim/TSA 발급은 다음 중 하나라도 발생하면 거부한다.

- 알 수 없거나 권한 없는 Subscriber/TSA operator/service 또는 issuer
- Claim Signing 요청에서 알 수 없는 CPL record, 잘못된 CPL status 또는 Max Assurance Level 불일치
- key ownership/CSR 서명 실패, unsupported key 또는 CSR/profile 불일치
- 요청자가 선택한 TSA/TSU identity 또는 승인되지 않은 Subject DN
- 승인된 `keyReuseIdentity` profile에서 과거 발급 또는 issuance reservation과 같은 public key로 판정된 요청
- 발급 후 인증서 profile self-check 실패

Claim AL2 또는 optional TSA attestation처럼 Evidence-required profile은 다음을 추가 거부 조건으로 적용한다.

- 알 수 없는 provider profile 또는 Evidence signature/chain/validity/revocation 실패
- CSR SPKI와 Evidence subject key 불일치
- 승인 freshness/replay predicate 실패; challenge-using profile이면 challenge 불일치·만료·재사용
- audience/profile/version 불일치
- 미승인·폐기 TA measurement/version/signer
- profile이 요구하는 debug/development, secure boot, TCB, rollback, key origin/storage/exportability/purpose predicate 미달
- verdict가 `UNKNOWN`, `NOT_PROVEN` 또는 verifier unavailable

TEE 실행·TEE key 보관·timestamp 전용·single-active-key의 runtime acceptance 실패는 timestamp 사용/activation을 차단한다. Signed device state가 없다는 이유만으로 base TSA Leaf 발급을 거부하지 않는다. Optional staged activation을 채택한 배포에서는 같은 `tsuInstanceId`에 두 번째 `SIGNING_ACTIVE` key를 만들려는 activation을 거부한다.

안정적 오류 코드와 재시도 가능 여부는 §6의 TSA API에만 적용한다. Claim Signing 범위는 외부 오류/response 모델을 정의하지 않고 발급 차단과 감사 근거만 규정한다. 어느 경우에도 세부 Reference Value나 방어 규칙을 불필요하게 노출하지 않는다.

## 17. 감사·개인정보 보호

감사 로그에는 다음을 남긴다.

- Claim request/issuance decision 또는 TSA transaction, Subscriber/operator, profile 및 인증서 serial
- CSR/Evidence/certificate digest
- trust store, provider profile, policy bundle과 Reference Value version
- Claim provider freshness/replay marker 또는 TSA challenge의 생성·만료·소비 상태
- 검증 단계별 판정과 내부 decision reason category; 외부 stable error는 TSA-only
- CA signing operation과 승인 주체
- revocation 및 incident 처리 이력

다음 값은 기본적으로 원문 저장을 피하거나 별도 보호한다.

- IMEI, 하드웨어 serial 등 장기 장치 식별자
- 불필요한 raw measurement
- Evidence 전체 원문과 Attestation chain
- 단말 위치·사용자 계정 등 enrollment에 필요하지 않은 개인정보

기본 저장은 digest, normalized verdict와 dependency identifier다. Raw Evidence는 provider 검증 또는 법적 근거가 privacy review에서 승인된 profile만 최소 field·tenant별 암호화·명시적 짧은 retention으로 별도 vault에 둔다. 인증서/상태 record의 만료+1년 의무를 Raw Evidence 전체에 자동 확장하지 않는다.

## 18. 시험 전략

### 18.1 Claim Signing Leaf 발급 시험

- AL1/AL2 정상 발급
- AL1 기본 profile에서 Evidence 없는 정상 발급과 unexpected Evidence 거부
- AL2에서 C2PA semantic O.1~O.4와, 승인된 provider profile이 정한 프로젝트 wrapper `evidenceItems=1..N_p` 조건 적용
- CPL status, DN, Max AL 및 attestation method 불일치
- CSR PoP 실패와 CSR/Evidence key mismatch
- challenge replay/expiry/cross-Subscriber 사용
- O.1~O.4 일부 누락 또는 `NOT_PROVEN`
- AL2 Leaf 90일, AL OID, CPL ID, EKU 및 OCSP 프로파일 검증
- 같은 요청의 동시 재시도에서 단일 인증서만 발급
- 승인된 identity profile이 있을 때 과거·폐기·만료 및 다른 profile의 동일 public-key 재사용·encoding variant 거부; 현재는 profile 미승인으로 issuance 비활성

### 18.2 Base TSA Signing Leaf 발급 시험

- secure enrollment credential과 CA business practices에 따른 현재 I/A/V 승인 확인
- CSR 서명에 의한 `K_tsu` ownership/PoP, Subject와 서버 발급 `tsaServiceId`/`tsuInstanceId` binding 검증
- `INITIAL`과 `REKEY`에서 Evidence 없는 정상 발급과 unexpected Evidence 거부
- `REKEY`의 새 key·새 CSR, current-certificate binding과 같은 key 재사용 거부
- 같은 요청의 동시 재시도에서 단일 인증서만 발급
- TSA Leaf의 critical EKU, 정확히 하나의 `id-kp-timeStamping`, KU/BC/policy/AIA/CRL 검증
- signed device state가 없거나 기존 key가 아직 active라는 이유만으로 base 발급을 거부하지 않음

### 18.3 Optional attested TSA profile 발급 시험

이 절은 CA가 별도로 승인한 Evidence-required CPS/provider profile에만 적용한다.

- 승인된 TA/TEE와 Evidence에 결속된 `K_tsu` 정상 발급
- 알 수 없는 Root/profile과 폐기된 AK/SAK
- TA measurement/version/signer 불일치
- profile이 요구한 debug lifecycle, TCB, rollback, exportability와 purpose/algorithm predicate 미달
- Attestation subject key와 CSR key 불일치
- `INITIAL`/`REKEY`의 fresh Evidence와 replay 거부, challenge flow를 사용하는 profile의 challenge/audience 검증, base↔attested profile 무단 전환 거부

### 18.4 외부 TSA TA runtime/activation acceptance 시험

- SHA-256/384/512 정상 요청
- 잘못된 digest 길이와 미지원 algorithm
- nonce 포함/미포함, 동일성 및 replay 시험
- 지원/미지원 policy와 extension
- C2PA 요청에서 `certReq=true` 및 TSA leaf/intermediate 포함
- `certReq=false` C2PA 요청 거부 또는 명시적 profile 오류
- 고유 serial의 재부팅·crash 복구
- 잘못된 시간 형식, accuracy 및 drift 초과 시 발급 중단
- ESSCertIDv2와 TSA signer certificate binding
- 한 `tsuInstanceId`에서 두 key를 동시에 `SIGNING_ACTIVE`로 만들거나 timestamp에 사용하는 전환 거부
- 새 TSA Leaf의 사전 발급과 runtime key activation을 분리하고, 기존 key가 active라는 이유만으로 인증서 발급 자체를 막지 않음
- TSA Leaf 만료·폐기·잘못된 EKU에 대한 token 검증 실패

### 18.5 외부 C2PA 2.4 상호운용 시험

- 단말에서 Claim 서명 → 로컬 Timestamp → C2PA Manifest 완성
- Validator가 Claim Signing chain과 TSA chain을 서로 독립적으로 검증
- 신규 Claim 생성의 protected integer label 33 `x5chain` 순서와 root 제외
- Validator의 deprecated string `x5chain` label 수용 및 두 label 동시 존재 시 C2PA 우선순위
- v2 payload, `CounterSignature` Sig_structure와 `sigTst2` 결합 검증
- C2PA Trust List와 TSA Trust List를 분리 적용
- 서버 signing endpoint 없이 offline On-Device TSA가 동작함을 검증
- 인증서 폐기 후 OCSP/CRL publication, Validator 결과와 외부 TSA의 bounded status-refresh 중단 정책 확인

## 19. C2PA Conformance와 운영 등록

### 19.1 Generator Product

외부 단말 Generator Product는 Content Credentials Specification 2.4와 Conformance Program 요구를 만족하고 CPL에 등록되어야 한다. Claim Signing Leaf 발급 서버는 signed Notice를 onboarding proof로 받은 경우 이를 확인하고, 현재 interim production issuance에서는 그 유무와 별개로 authenticated public CPL의 current `status=conformant` record를 요구한다. Generator Product 구현과 GPSA 작성은 이 Certificate Platform의 납품 범위가 아니다.

### 19.2 CA와 TSA

Production C2PA 신뢰 체계를 구성하려면 다음이 필요하다.

- CA는 C2PA Certificate Policy에 맞는 운영·보안·감사 체계를 갖춘다.
- Claim Signing CA chain은 C2PA Trust List 등록 절차를 따른다.
- TSA chain은 C2PA TSA Trust List 등록 절차를 따른다.
- C2PA Conformance Program은 TSA-only Applicant를 받지 않으므로 CA 역할과 함께 운영한다.
- TSA practices, hash algorithms, accuracy, 로그 보존, 사용 제한과 검증 방법을 공개한다.
- Root/Intermediate key ceremony와 인증서 프로파일 적합 증거를 준비한다.

## 20. 구현 단계

### Phase 1: Certificate Platform 계약 고정

- Claim Signing/TSA Issuing CA 구조
- Subject DN과 TSU identity 모델
- Evidence-required profile을 채택한 경우의 Custom Attestation OID와 profile ID
- 해당 optional Evidence의 DER 또는 canonical CBOR/COSE schema
- challenge를 사용하는 profile의 entropy/TTL/audience
- certificate validity와 rotation 정책
- profile별 CSR/certificate JSON schema version/hash
- Claim request-body schema, TSA OpenAPI·오류 catalog와 DB constraint

### Phase 2: 서버 enrollment 기반

- Claim request-body validator와 server-held freshness/replay context
- TSA transaction/idempotency 상태기계와 optional challenge 상태
- strict CSR parser와 PoP 검증
- Evidence-required profile을 채택한 경우의 provider profile/trust store/reference value registry
- 같은 optional 범위의 Attestation verifier와 normalized verdict
- Claim/TSA certificate policy engine

### Phase 3: 수명주기와 운영 서비스

- fresh-key re-enrollment와, 채택한 경우의 TSA staged activation
- OCSP/CRL, revocation request와 CPL event 처리
- Subscriber 재인증, audit/retention과 incident workflow
- Root/Intermediate/HSM ceremony와 recovery

### Phase 4: 외부 통합 acceptance

- provider/OEM의 CSR 및 Evidence-required profile의 Evidence 생성 interoperability
- Claim `x5chain`과 C2PA 2.4 `sigTst2` known-answer test
- TSA trusted-time, serial, status refresh와 단일 active key runtime acceptance; 채택한 경우 activation Evidence
- Validator 상호운용과 negative test

이 Phase는 외부 Generator/TSA runtime을 개발하는 단계가 아니라 Certificate Platform이 지원할 integration profile을 승인하는 단계다.

### Phase 5: PKI 운영과 적합성

- HSM, key ceremony, multi-party control
- OCSP/CRL와 incident/revocation
- CPS/TSA practices와 감사 증거
- Trust List/TSA Trust List 신청 자료
- 전체 정상·오류·상호운용 시험

## 21. Provider·환경 활성화 Gate

아래 값은 아키텍처 공통값이 아니라 해당 기능을 채택한 provider/배포 환경별 profile의 값이다. 미정 상태이면 그 기능/profile만 `DISABLED`로 유지하며 base TSA Leaf enrollment을 자동 차단하지 않는다. 실제 profile 활성화 기록은 production 착수 전에 승인된 별도 registry/release artifact에서 관리해야 하며, 이 Overview의 서술만으로 provider를 활성화할 수 없다. 현재 문서에는 production `ENABLED`로 승인된 attestation provider가 없다.

| 항목 | 확정된 공통 결정 | profile 활성화 증거 |
|---|---|---|
| Claim key boundary/AL2 provider | 외부 GP 책임, CPL 허용 method와 CA profile의 교집합만 사용 | provider 원문, O.1~O.4 mapping과 test vectors |
| Optional TSA Attestation signer | optional profile에서 논리 분리. 동일 TA는 TEE가 attestation 입력·키 사용을 하드웨어 강제할 때만 예외 | provider threat analysis와 negative test |
| Root/AK/SAK lifecycle | 공급자/OEM이 발급·폐기, CA가 독립 trust/status registry 운영 | owner, chain profile, rotation/revocation feed |
| Evidence schema/OID | provider별 하나의 canonical schema와 조직 소유 OID/profile ID | signed schema, assigned identifier, parser tests |
| TSU identity/optional activation | 서버가 service와 TSU slot을 분리 발급. Staged activation을 채택하면 Prepare→Commit Authorization→durable Receipt→Finalization을 조정하고 device 전환만 TEE-local atomic | API/DB constraint; 채택 시 crash/retry/reconciliation, staged-key ACL과 activation Evidence test |
| Reference Value | 승인된 공급자가 서명하고 CA가 version/effective/expiry/rollback 관리 | signed bundle과 emergency revoke rehearsal |
| Challenge/freshness | Claim `OD-FRESHNESS-01` 또는 TSA policy가 profile별 challenge 사용 여부와 entropy/length/encoding/TTL/transform을 승인; non-challenge profile도 provider-native signed freshness/replay와 audience/profile/request-context binding 필수. 현재 수치 default 없음 | provider 원문, RNG/entropy(사용 시), freshness/replay/cross-audience tests |
| TSA Leaf/re-key | 기본 최대 90일과 fresh key/동일 SPKI 재사용 금지는 project policy; re-attestation은 optional profile이 명시한 경우만 | expiry/rotation/failure test |
| Trusted time/offline | 외부 TSA profile이 UTC(k), accuracy≤1초, C2PA 24시간 sync 시도와 CPS 24시간 successful-sync/status max-age를 강제; 네 deadline 최솟값에서 stop | provider design, status rollback/drift/offline tests |
| Timestamp serial | 외부 TEE가 crash-safe·rollback-resistant unique serial을 보장 | persistence design과 crash/power-loss tests |
| Evidence retention | 인증서 record는 만료+최소 1년; Evidence를 사용하는 profile은 digest/verdict/dependency ID를 기본 보존하며 raw는 provider·법적 필요가 승인된 경우에만 최소화·암호화·기한 보존 | privacy review, retention/deletion test |
| Verifier boundary | CA/HSM signing 권한이 없는 격리 서비스 | IAM/DFD/deployment test |
| Claim/TSA CA separation | 서로 다른 CA key·HSM object·role 사용 | ceremony, access matrix와 profile conformance evidence |

## 22. 로컬 근거 문서

- [C2PA Conformance Program v0.2](../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md)
- [C2PA Certificate Policy v0.2](../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
- [C2PA Generator Product Security Requirements](../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md)
- [Content Credentials Specification 2.4](../specifications/build/site/specifications/2.4/specs/ContentCredentials.html)
- [C2PA Claim Signing Leaf AL1 Certificate Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.schema.json)
- [C2PA Claim Signing Leaf AL2 Certificate Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.schema.json)
- [C2PA Claim Signing Leaf AL1 CSR Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.csr.schema.json)
- [C2PA Claim Signing Leaf AL2 CSR Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.csr.schema.json)
- [C2PA TSA Leaf Certificate Schema](../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json)
- [C2PA TSA Leaf CSR Schema](../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json)
- [C2PA Claim Signing Issuing CA CSR Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json)
- [C2PA Claim Signing Issuing CA Certificate Schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json)
- [C2PA TSA Issuing CA CSR Schema](../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.csr.schema.json)
- [C2PA TSA Issuing CA Certificate Schema](../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.cert.schema.json)
- [TSA Leaf enrollment 원문 근거 재정리](tsa-leaf-enrollment-request/README.md)
- [RFC 3161](../rfc3161.txt)
- [RFC 5816](../rfc5816.txt)

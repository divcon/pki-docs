# TSA Leaf Enrollment 요청 계약

> 기본 profile은 CSR 기반 key ownership 확인을 사용한다. Attestation은 명시적으로 선택한 CPS 확장 profile에서만 요청한다. 아래 endpoint와 JSON field는 C2PA 표준 wire가 아니라 project API다.

## 1. 기본 호출 순서

| 순서 | Operation | 요청 | 서버 검증/응답 |
|---:|---|---|---|
| 0 | TSA operator/service 등록 | CA business practices가 요구하는 I/A/V 자료 | 승인 operator, `tsaServiceId`, authoritative Subject, 권한 |
| 1 | TSU 등록/slot 생성 | 승인 credential, service 식별자 | server-owned `tsuInstanceId` 등 project metadata |
| 2 | `POST /v1/enrollments` | profile, service/TSU, `INITIAL`/`REKEY` | transaction과 CSR 작성에 필요한 authoritative context |
| 3 | 단말 내부 | `K_tsu` 생성, CSR 서명 | 서버 호출 없음 |
| 4 | `POST /v1/enrollments/{transactionId}/submission` | CSR | key ownership, authorization, CSR/profile 검증 |
| 5 | `GET /v1/enrollments/{transactionId}` | transaction 조회 | TSA Leaf와 intermediate chain 또는 실패 |

별도 activation/state protocol을 채택할 수 있지만 C2PA가 TSA Leaf 발급 전에 특정 activation API나 signed receipt를 요구하는 것은 아니다.

## 2. 공통 transport와 권한

C2PA CP가 직접 요구하는 것은 secure enrollment credential과 key-pair ownership 확인이다. TLS, endpoint, idempotency header, tenant isolation, JSON encoding 및 구체 credential scheme은 project/CPS가 정한다.

권장 project contract:

- TLS와 승인된 TSA operator credential
- service/profile별 authorization
- 변경 요청의 `Idempotency-Key`
- strict JSON parsing, size/rate limit과 stable error code
- client가 보낸 Subject/TSU/issuer policy를 신뢰하지 않고 server registry와 비교

## 3. Enrollment 시작

### 3.1 INITIAL

```json
{
  "certificateProfile": "c2pa-on-device-tsa",
  "tsaServiceId": "server-registered-service",
  "tsuInstanceId": "server-registered-tsu",
  "operation": "INITIAL"
}
```

`INITIAL`은 해당 TSU의 최초 발급 이력이 없는 경우에만 허용한다. 이 상태 불변조건은 project lifecycle policy이며 C2PA wire requirement가 아니다.

### 3.2 REKEY

```json
{
  "certificateProfile": "c2pa-on-device-tsa",
  "tsaServiceId": "server-registered-service",
  "tsuInstanceId": "server-registered-tsu",
  "operation": "REKEY",
  "rotationOfCertificate": {
    "issuerNameHash": "project-defined encoding",
    "serialNumber": "01AB",
    "certificateDigest": "project-defined encoding"
  }
}
```

CP는 re-key를 신규 신청과 동일하게 처리하고 같은 identity validation을 하도록 요구한다. 새 key와 새 CSR, 현재 certificate binding 및 same-key renewal 금지는 이 architecture의 강화 policy다. Compound Evidence는 기본 INITIAL과 REKEY 모두 요구하지 않는다.

### 3.3 응답

기본 profile 응답 예시:

```json
{
  "transactionId": "server-issued-id",
  "canonicalTsaSubjectDn": "base64(DER Name)",
  "expiresAt": "RFC3339 timestamp"
}
```

기본 profile에서는 `challenge`, `audience`, `evidenceProfile` 및 `evidenceProfileVersion`을 TSA attestation 용도로 반환할 이유가 없다. Idempotency나 PoP protocol 자체에 challenge를 쓰는 별도 API 설계는 가능하지만, 그것을 C2PA TSA attestation 요구라고 부르지 않는다.

## 4. CSR 생성

1. 승인된 On-Device TSA 구현은 `K_tsu`를 TEE 안에서 생성·보관한다.
2. CSR Subject는 server-authoritative TSA service Subject를 사용한다.
3. [02 §2.3](02-CSR-and-Attestation-Requirements.md#23-requested-extensions)에 따른 `extensionRequest`를 포함한 PKCS#10 `CertificationRequestInfo`에 `K_tsu`로 서명한다.
4. private key는 enrollment client나 Certificate Platform으로 내보내지 않는다.

1번은 구현/runtime 의무이고 3번은 이 architecture가 선택한 key ownership 확인 방법이다. 기본 API 요청은 1번의 별도 원격 증거를 동봉하지 않는다.

## 5. Enrollment 제출

### 5.1 기본 TSA profile

```http
POST /v1/enrollments/{transactionId}/submission
Idempotency-Key: <opaque value>
Authorization: <approved credential>
```

```json
{
  "transactionId": "server-issued-id",
  "certificateProfile": "c2pa-on-device-tsa",
  "csr": "base64(DER PKCS#10)"
}
```

| Field | Cardinality | 근거 수준 |
|---|---:|---|
| path/body `transactionId` | project contract | `ARCH-DECISION` |
| `certificateProfile` | 1 | project routing; 발급 결과는 C2PA TSA profile 준수 |
| `csr` | 1 | key ownership은 C2PA 필수, PKCS#10 방식은 project 선택 |
| `attestationEvidence` | 0 | 기본 TSA profile에는 없음 |

### 5.2 선택적 CPS attestation 확장

CA가 별도 profile을 승인한 경우에만 다음처럼 확장할 수 있다.

```json
{
  "transactionId": "server-issued-id",
  "certificateProfile": "c2pa-on-device-tsa-attested-v1",
  "csr": "base64(DER PKCS#10)",
  "attestationEvidence": [
    {
      "type": "provider-profile-id",
      "mediaType": "application/eat+cwt",
      "evidence": "base64(raw signed evidence)",
      "x5chain": ["base64(DER signer certificate)"]
    }
  ]
}
```

이 경우에만 다음을 fail-closed로 검증한다.

- transaction이 해당 확장 profile을 명시적으로 선택했는가
- profile/version, media type, role과 cardinality
- signer trust path/status 및 signature
- freshness/challenge/audience
- Evidence subject key와 CSR SPKI binding
- profile이 실제로 정의한 TA/TEE claim과 Reference Value

기본 profile에 Evidence를 보내면 ambiguous downgrade/upgrade를 막기 위해 거부하는 것이 안전하다.

## 6. 서버의 기본 발급 gate

HSM/CA 서명 전 기본 gate는 다음과 같다.

1. caller credential과 TSA operator/service authorization
2. transaction ownership, operation과 idempotency
3. CA business practices가 정한 applicant identification/authentication/verification
4. 발급 대상 key ownership
5. strict CSR signature/DER/SPKI/Subject/requested-extension 검증
6. server-controlled TSA Leaf template 및 issuer 상태
7. key/serial uniqueness와 atomic issuance 기록 같은 project invariants

TEE 실행, TEE key storage, timestamp-only 및 single-active-key의 운영 적합성은 제품/서비스 승인, 구현 검토, 시험과 운영 통제로 확인한다. 기본 submission body에서 그 사실의 signed observation을 찾지 못했다는 이유만으로 C2PA 위반으로 거부하면 안 된다.

## 7. 결과

```json
{
  "transactionId": "server-issued-id",
  "certificateProfile": "c2pa-on-device-tsa",
  "certificate": "base64(DER TSA Leaf)",
  "certificateChain": ["base64(DER TSA Issuing CA)"]
}
```

client는 설치 전 Leaf signature/path, CSR과 Leaf SPKI 일치, Subject, KU/EKU/policy, validity 및 issuer chain을 확인한다. Root/trust anchor 배포는 별도 신뢰 경로다.

## 8. 보내지 않는 값

- `K_tsu` private key
- Claim, Manifest, asset, RFC 3161 `MessageImprint` 또는 runtime nonce
- client-selected authoritative Subject/TSU/serial policy
- client가 만든 `PASS`, `hardwareProtected`, `singleActive=true` 같은 자기 선언
- 기본 profile에서의 Compound Evidence/attestation chain

## 9. 상태/activation 경계

single-active-key를 강제하기 위한 local ACL/state machine과 activation protocol은 유효한 project 설계가 될 수 있다. 그러나 다음을 구분한다.

- **C2PA 의무:** 실제 TSU는 한 시점에 하나의 time-stamp signing key만 active여야 함.
- **project 구현:** staged state, receipt, counter, endpoint 및 rollback recovery.
- **비요구:** 그 state를 TSA Leaf API 호출마다 서명된 Evidence로 제출.

따라서 activation 계약이 미정이라는 사실은 해당 activation 구현의 production blocker일 수 있지만, 그 자체로 기본 TSA Leaf 인증서 발급 표준의 blocker는 아니다.

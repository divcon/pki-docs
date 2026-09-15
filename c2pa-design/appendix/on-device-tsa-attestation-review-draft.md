# On-Device TSA Custom Attestation 설계 검토안 (Superseded)

> 상태: **Superseded / non-implementation historical review**
> 대체 문서: [Architecture Overview](../Overview.md), [Certificate Enrollment](../02-Certificate-Enrollment.md), [External Runtime Acceptance](../03-On-Device-Runtime.md)
> 주의: 이 문서의 field 목록·검증 순서·미결정 checklist로 provider profile을 구현하거나 `ENABLED`로 전환하지 않는다. 충돌 시 위 대체 문서와 versioned machine-readable provider artifact가 우선한다.

## 타 팀 검토 요청

On-Device TSA의 TSA TA가 TEE 내부에서 TSU 키를 생성하고 Custom Attestation Chain과 CSR을 제출하면, CA가 동일 키·승인된 TA·TEE 상태를 검증한 뒤 RFC 3161 TSA Leaf 인증서를 발급하는 구조를 제안합니다. 아래의 **신뢰 체인, Custom Extension 필드, CSR 바인딩, TSA TA/Attestation signer 분리 및 CA 검증 순서**가 충분한지 검토해 주세요.

## 1. 제안 구조

### 1.1 목표

- TSU 개인키는 TEE 내부에서 생성·보관하고 외부로 내보내지 않는다.
- Custom Attestation은 다음 두 사실을 하나의 서명된 Evidence로 증명한다.
  1. TSU 키가 승인된 TEE에서 생성·보호되고 있다.
  2. 승인된 TSA TA가 TEE에서 실행되고 있으며 해당 TSU 키와 연결되어 있다.
- REE는 challenge, CSR 및 인증서 체인을 전달하는 통로일 뿐 신뢰하지 않는다.
- CA는 서버가 보유한 Attestation Root와 Reference Value를 기준으로 검증한다.

이 구조는 Key Attestation과 TA/Workload Attestation을 하나의 Custom Attestation Certificate Extension에 결합한 **Compound Attestation**이다.

### 1.2 전체 흐름

```text
CA                         REE                    TSA TA / Attestation Service
│                           │                                  │
│── challenge, transaction ─▶│                                  │
│                           │── challenge 전달 ────────────────▶│
│                           │                                  │ 1. TSU 키 생성
│                           │                                  │ 2. TA/TEE 상태 수집
│                           │                                  │ 3. Attestation Leaf 생성
│                           │                                  │ 4. CSR 생성·서명
│                           │◀── CSR + Attestation Chain ───────│
│◀── CSR + Chain + transaction ─│                              │
│                                                              │
│ 5. Chain/Extension/challenge/CSR/key binding 검증             │
│ 6. TSA Leaf 인증서 발급                                      │
│── TSA Leaf ───────────────▶│── TEE에 전달·등록 ──────────────▶│
```

### 1.3 Attestation 신뢰 체인

```text
Attestation Root CA
  └─ Device/OEM Attestation Issuing Key Certificate
       └─ Attested TSU Key Leaf Certificate
            ├─ SPKI = TSU 공개키
            └─ Custom TSA Attestation Extension
```

중요 전제:

- CA는 요청으로 전달된 Root를 신뢰하지 않고 **서버 Trust Store에 사전 등록된 Root만** 신뢰한다.
- TA가 런타임에 Root와 전체 체인을 임의 생성하면 신뢰 근거가 없으므로 허용하지 않는다.
- TA가 만드는 것은 원칙적으로 **Attested TSU Key Leaf**이며, 이를 서명하는 Attestation Key와 상위 체인은 제조·등록 단계에서 프로비저닝되어 있어야 한다.
- TSU Leaf를 직접 서명하는 Device/OEM Attestation Key 인증서는 X.509 경로상 인증서 발급자이므로 적절한 `BasicConstraints`, `KeyUsage=keyCertSign` 및 경로 제한이 필요하다.
- Attestation Leaf의 SPKI와 Custom Extension은 동일한 인증서 서명 범위에 있으므로 TA 상태와 TSU 키가 암호학적으로 결합된다.
- Attestation Leaf는 Evidence일 뿐 최종 TSA 인증서가 아니다. 최종 TSA Leaf는 검증 후 TSA Issuing CA가 같은 SPKI에 발급한다.

### 1.4 누가 Attestation을 서명하는가

권장 구조는 TSA TA와 Attestation signer를 논리적으로 분리하는 것이다.

| 구성요소 | 책임 |
|---|---|
| TSA TA | TSU 키 생성·사용, CSR 생성·서명, 신뢰 시간 및 RFC 3161 처리 |
| TEE Attestation Service/TA | TSA TA의 identity·measurement와 TEE 상태를 읽고 Attestation Key로 Evidence 서명 |

하나의 TA가 두 역할을 모두 수행할 수도 있지만 다음 조건이 필요하다.

- Attestation Key는 승인된 TA identity/measurement에서만 사용할 수 있어야 한다.
- measurement, TCB, debug, rollback 상태는 REE나 TSA 업무 로직이 전달한 값을 그대로 서명하면 안 된다.
- 해당 값은 TEE core, secure monitor 또는 신뢰 가능한 플랫폼 API에서 직접 얻어야 한다.
- TSA TA가 자기 상태를 임의로 선언하고 스스로 서명하는 구조는 Self-Assertion이므로 원격 신뢰 증거로 사용하지 않는다.

## 2. 전송 Artifact

REE는 CA에 다음 세 항목을 하나의 발급 transaction으로 제출한다.

```json
{
  "transactionId": "server-issued-id",
  "tsaServiceId": "server-registered-service-id",
  "tsuInstanceId": "server-issued-slot-id",
  "csr": "base64(DER PKCS#10)",
  "attestationChain": [
    "base64(DER Attested TSU Key Leaf)",
    "base64(DER Attestation Intermediate/Device AK Certificate)"
  ],
  "profile": "on-device-tsa-attestation-v1"
}
```

- Root 인증서는 보내지 않거나 참고용으로만 보낸다. 신뢰 여부는 서버 Trust Store로 결정한다.
- Challenge는 CSR 속성이 아니라 Attestation Extension 안에 포함한다.
- CSR과 Attestation Chain은 같은 transaction에서 제출한다.

## 3. Custom Attestation Extension

### 3.1 기본 형식

- 조직이 소유한 Private OID를 사용한다. 실제 OID는 PKI 팀이 배정한다.
- Extension 값은 버전이 있는 ASN.1 DER 또는 canonical CBOR 구조로 정의한다.
- CA는 Extension이 Attested TSU Key Leaf에 정확히 한 번 존재하는지 확인한다.
- Critical 여부는 사용하는 X.509 라이브러리 호환성을 확인하여 결정한다. Non-critical로 정하더라도 CA 정책에서는 필수 Extension으로 취급한다.

### 3.2 Extension에 포함할 필드

| 구분 | 필드 | 필수 | 검증 목적 |
|---|---|---:|---|
| Profile | `profileVersion` | 예 | 스키마 및 검증 정책 버전 |
| Profile | `profileId` | 예 | On-Device TSA용 Evidence임을 식별 |
| Freshness | `challenge` | 예 | CA challenge 일치 및 replay 방지 |
| Binding | `audience` | 예 | 다른 CA/서비스로 Evidence 전용 방지 |
| Binding | `transactionContext` | 선택 | 서버 transaction과 추가 바인딩 |
| TSU | `tsaServiceId` | 예 | 승인된 CA Applicant의 TSA service와 결합 |
| TSU | `tsuInstanceId` | 예 | TSU와 활성키 수명주기 연결 |
| Key | `keySecurityLevel` | 예 | TEE 또는 승인된 동등 보안 수준 |
| Key | `keyOrigin` | 예 | TEE 내부 `GENERATED` 확인 |
| Key | `nonExportable` | 예 | 개인키 외부 추출 금지 |
| Key | `keyPurpose` | 예 | `SIGN` 및 TSA 전용 정책 적용 |
| Key | `keyAuthorizations` | 예 | digest, padding, curve 등 TEE 강제 속성 |
| TA | `taUuid` | 예 | 실행 중인 TSA Trusted Application 식별 |
| TA | `taMeasurement` | 예 | 승인된 TSA TA 코드인지 판정 |
| TA | `taSignerDigest` | 직접 또는 기준값 | 승인된 공급자 서명 확인 |
| TA | `taVersion` | 직접 또는 기준값 | 승인·폐기된 TA 버전 판정 |
| TEE | `teeImplementationId` | 예 | TEE/OEM Provider Profile 식별 |
| TEE | `tcbSecurityVersion` | 예 | 최소 허용 TCB 및 취약 버전 판정 |
| TEE | `securityLifecycle` | 예 | Production/Development 상태 판정 |
| TEE | `debugEnabled` | 예 | Debug 실행 상태 거부 |
| TEE | `rollbackIndex` | 지원 시 필수 | 이전 취약 TA/TEE로 rollback 방지 |
| TEE | `secureBootState` | 지원 시 필수 | 승인된 TEE/TA 이미지 부팅 확인 |

### 3.3 Extension에 넣지 않아도 되는 값

| 값 | 처리 방법 |
|---|---|
| TSU 공개키 또는 SPKI digest | Attestation Leaf의 SPKI 자체가 TSU 공개키이므로 중복 저장 불필요 |
| TA signer·version 설명 | `taMeasurement`를 서버 Reference Value에 매핑할 수 있으면 생략 가능 |
| Attestation Root | 서버 Trust Store에서 선택 |
| 최종 TSA Subject·Issuer·EKU | CA가 최종 TSA Leaf를 발급할 때 설정 |
| On-Device 현재 시각 | 발급 freshness는 CA challenge로 판단하며 단말 시각을 신뢰하지 않음 |

서버 Reference Value 예:

```text
taMeasurement
  └─ taUuid
  └─ taVersion
  └─ taSignerDigest
  └─ APPROVED / REVOKED
  └─ minimumTcbSecurityVersion
```

## 4. CSR에 포함할 내용

| CSR 구성요소 | 처리 기준 |
|---|---|
| `version` | PKCS#10 v1의 값 `0` |
| `subject` | CA 정책에 따른 요청값. 최종 값은 CA가 신청자·TSU 등록정보로 결정 |
| `subjectPublicKeyInfo` | Attestation Leaf SPKI와 정확히 동일한 TSU 공개키 |
| `signatureAlgorithm` | TSA 인증서 정책이 허용하는 RSA-PSS 또는 ECDSA |
| `signature` | TSU 개인키가 `CertificationRequestInfo`에 생성한 서명 |
| `attributes` | 최소화. 필요한 요청 속성만 allowlist 방식으로 허용 |

CSR의 일반 attribute나 attestation payload에 넣지 않을 내용:

- Attestation challenge 또는 `challengePassword`
- TA UUID, measurement, TCB, debug 상태
- Attestation 인증서 체인

공식 C2PA `tsaLeaf.csr.schema.json`에 따라 CSR의 `extensionRequest`에는 다음 값을 요청해야 한다. CA는 요청의 존재와 값을 schema로 검증하지만 그대로 신뢰하거나 복사하지 않고 최종 TSA Leaf를 독립적으로 구성한다.

- `BasicConstraints`: critical, `cA=false`
- `KeyUsage`: critical, `digitalSignature`, `contentCommitment`
- `ExtendedKeyUsage`: critical, 정확히 `id-kp-timeStamping`
- C2PA TSA Certificate Policy OID

Subject와 SPKI의 승인된 RSA/EC 알고리즘·키 크기도 같은 공식 CSR schema로 검증한다.

## 5. 구성요소별 책임

| 단계 | REE | TSA TA | Attestation Service/AK | CA 서버 |
|---|---|---|---|---|
| Challenge | TLS로 수신·전달 | 입력 형식·대상 확인 | 서명 Evidence에 포함 | 고유값 발급, transaction·TTL·사용 상태 저장 |
| TSU 키 생성 | 관여하지 않음 | TEE 내부 생성·보관 | 생성 위치·속성 검증 | Evidence 정책 판정 |
| TA 상태 | 값을 만들거나 수정하지 않음 | 측정 대상 | TEE에서 measurement·TCB·lifecycle 수집 | Reference Value와 비교 |
| Attestation Leaf | 전달만 수행 | TSU 공개키 제공 | SPKI와 Extension을 Attestation Key로 서명 | 체인·Extension·Root·폐기 검증 |
| CSR | 전달만 수행 | CSR 생성 또는 CRI 검토 후 TSU 키로 서명 | 관여하지 않음 | CSR 구문·서명·SPKI 바인딩 검증 |
| 최종 인증서 | 수신·전달 | 동일 TSU 키에 등록 | 관여하지 않음 | TSA 프로파일로 Leaf 발급 |
| Timestamp | MessageImprint·nonce 전달 | 신뢰 시간 확인, TSTInfo 생성, TSU 키로 서명 | 필요 시 보안 상태 제공 | 발급 단계 이후 직접 관여하지 않음 |

REE에서 수행하는 파싱이나 사전 검사는 오류를 빨리 찾기 위한 편의 기능일 뿐 보안 판정으로 인정하지 않는다.

## 6. CA 서버 검증 순서

CA는 다음 순서를 모두 성공한 경우에만 TSA Leaf를 발급한다.

1. `transactionId`가 존재하고 신청자·challenge·profile과 연결되어 있는지 확인한다.
2. Transaction이 만료되지 않았고 challenge가 미사용 상태인지 확인한다.
3. CSR과 Attestation Chain을 엄격하게 DER 파싱한다.
4. 서버 Trust Store의 Root를 기준으로 Attestation 인증서 경로를 구성한다.
5. 체인 서명, 유효기간, `BasicConstraints`, `KeyUsage`, path length 및 정책 OID를 검증한다.
6. Attestation 인증서의 폐기·차단 상태를 검증한다.
7. Attested TSU Key Leaf에 Custom Extension이 정확히 한 번 존재하는지 확인한다.
8. `profileVersion`, `profileId`, `audience`, `tsaServiceId`와 server-issued `tsuInstanceId`를 지원 정책 및 transaction 원본과 비교한다.
9. Extension의 `challenge`가 transaction의 challenge와 정확히 일치하는지 확인한다.
10. TA measurement, UUID, signer, version, TCB, lifecycle, debug, rollback 상태를 서버 Reference Value와 비교한다.
11. Key security level, origin, non-exportable, purpose 및 authorization을 TSA 정책과 비교한다.
12. Attestation Leaf SPKI와 CSR SPKI를 DER 기준으로 정확히 비교한다.
13. CSR 자기서명을 검증하여 TSU 개인키 Proof of Possession을 확인한다.
14. 전체 발급 이력의 normalized public-key digest 재사용을 거부하고, re-key이면 같은 `tsuInstanceId`의 기존 active key를 허용하되 신규 key가 provider hardware에서 `STAGED_DISABLED`임을 확인한다.
15. 최종 TSA 인증서 프로파일을 CA가 구성하여 같은 SPKI에 발급한다. 인증서는 CA 관점에서 valid이며 runtime activation은 대체 문서의 별도 protocol을 따른다.
16. Challenge를 원자적으로 사용 완료 처리하고 Evidence digest, dependency identifiers, 정책 버전 및 판정 결과를 감사 로그에 남긴다.

다음 중 하나라도 발생하면 fail-closed 한다.

- 알 수 없는 Root 또는 Attestation Profile
- Extension 누락·중복·파싱 실패
- challenge 불일치·만료·재사용
- Attestation Leaf SPKI와 CSR SPKI 불일치
- 미승인·폐기 TA measurement
- Debug/Development 상태
- 최소 TCB·rollback 정책 미달
- 신규 key가 `STAGED_DISABLED`임을 hardware Evidence로 증명하지 못함 또는 승인 없는 이중 active 전환
- CSR 또는 인증서 체인 서명 실패

## 7. C2PA 공통 로직과 Custom TSA 로직

| 검증 항목 | C2PA AL2 로직 재사용 | Custom TSA 구현 |
|---|---:|---:|
| 인증서 체인·Root·폐기 검증 | 가능 | Root/Profile 설정 필요 |
| Challenge freshness | 가능 | 그대로 사용 |
| Attestation Leaf와 CSR SPKI 비교 | 가능 | 그대로 사용 |
| CSR Proof of Possession | 가능 | 그대로 사용 |
| TEE 보안 수준·key origin·purpose | 가능 | Custom 필드 매핑 필요 |
| 키 algorithm·size·digest·padding·curve | 가능 | TSA 허용 정책 적용 |
| Android package·앱 버전·앱 signer | 사용하지 않음 | TSA TA identity로 대체 |
| TSA TA UUID·measurement | 불가능 | Custom Extension 및 Reference Value 필요 |
| TEE TCB·lifecycle·debug·rollback | 일부 개념 재사용 | Provider별 Custom 판정 필요 |
| TA와 TSU 키의 결합 | C2PA Android 방식으로 불충분 | 같은 Attestation Leaf 서명으로 결합 |
| Timestamp 전용키·TSU 단일 활성키 | 불가능 | TA 접근 통제·서버 인벤토리 필요 |
| 신뢰 시간·RFC 3161 | 불가능 | TSA TA 및 운영 로직 필요 |

## 8. 인증서 발급 후 TSA TA가 보장할 사항

Key Attestation과 인증서 발급만으로 다음 사항은 증명되지 않는다. TSA TA 및 운영 정책에서 별도로 강제한다.

- TSU 개인키를 RFC 3161 Timestamp 이외의 서명에 사용하지 않는다.
- 한 TSU에는 하나의 활성 Timestamp 서명키만 사용한다.
- 최소 24시간마다 UTC(k)에 추적 가능한 시간원과 동기화를 시도한다.
- 선언한 정확도를 벗어나거나 신뢰 시간 상태를 판단할 수 없으면 발급을 중단한다.
- CPS가 정한 최대 24시간 status age를 지키고 OCSP/CRL rollback·stale·unknown·revoked 상태에서는 발급을 중단한다.
- 신뢰 시간 상태와 rollback 방지 상태를 TEE 보호 저장소에 보관한다.
- `MessageImprint`는 SHA-256/384/512만 허용한다.
- 요청 nonce, policy, serial number, `genTime`, accuracy를 RFC 3161 정책에 맞게 처리한다.

`STAGED_DISABLED`와 `COMMITTED_DISABLED` key는 RFC 3161 명령에도 사용할 수 없어야 한다. Initial/re-key activation은 대체 아키텍처의 Prepare Receipt → signed Commit Authorization → durable Commit Receipt → signed Finalization Token protocol만 사용하며 운영자 수동 승인은 이 Evidence를 우회하지 못한다.

## 9. 검토 결과와 이 문서의 사용 제한

공통 결정은 대체 아키텍처에 반영됐다. 서버가 `tsaServiceId`/`tsuInstanceId`와 32-byte challenge를 발급하고 audience를 필수 binding으로 사용하며, fresh key·전체 이력 key uniqueness·최대 90일 TSA Leaf·bounded status refresh를 적용한다. Existing active key가 있어도 new key의 staged 발급은 허용한다.

Provider별 Root/AK/SAK owner, 실제 OID와 canonical wire schema, Reference Value feed, TEE claim 가용성, staged-key hardware ACL, Prepare/Commit/Finalization fault behavior와 trusted-time/serial 구현은 공통값이 아니다. 이 값과 signed artifact/test vector가 승인되기 전 해당 provider는 `DISABLED`다. 이 historical review에는 그 값을 채우지 않는다.

## 10. 참고 자료

- [C2PA Certificate Policy v0.2](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
- [RFC 2986 — PKCS #10 Certification Request Syntax](https://datatracker.ietf.org/doc/html/rfc2986)
- [RFC 3161 — Time-Stamp Protocol](https://datatracker.ietf.org/doc/html/rfc3161)
- [Android Key Attestation](https://source.android.com/docs/security/features/keystore/attestation)

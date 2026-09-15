# C2PA AL2 SAK Attestation Evidence 설계

## 1. 목적

이 문서는 C2PA Claim Signing Leaf 인증서의 AL2 enrollment에 사용할 Attestation Evidence를 정의한다.

주요 범위는 다음과 같다.

- Attestation Evidence가 포함하고 서명해야 하는 값
- C2PA AL2 보안 목표 O.1~O.4와 Evidence claim의 매핑
- Google Android Key Attestation Evidence의 실제 생성 및 검증 구조
- Samsung Root of Trust에 연결된 custom SAK 기반 Evidence 생성 구조
- CSR, Claim Signing Key 및 Evidence 간 암호학적 바인딩
- CA가 보유해야 하는 기준값과 검증 순서
- 실패 조건, 보안 통제 및 개인정보 보호 요구사항

이 문서의 주 대상은 **인증서 enrollment 시 CA가 평가하는 Dynamic Evidence**다. C2PA Manifest 내부의 `c2pa.attestation` assertion은 별도 사용 사례이며, enrollment Evidence를 사용한다고 해서 Manifest에 Attestation Assertion이 자동으로 포함되는 것은 아니다.

## 2. 기준과 상태

### 2.1 C2PA 기준

C2PA Certificate Policy v0.2는 AL2 enrollment에서 하드웨어 Root of Trust가 지원하는 검증 가능한 artifact를 요구한다.

- O.1: 승인된 Generator Product 인스턴스
- O.2: Claim Signing 개인키의 하드웨어 기반 생성·보관 및 소유
- O.3: Claim Generator와 실행 플랫폼의 이미지 인증 및 보안 상태
- O.4: Asset/Assertion 처리 소프트웨어와 실행 플랫폼의 무결성

C2PA는 모든 플랫폼에 공통으로 적용되는 단일 Evidence wire format을 규정하지 않는다. CA CPS와 플랫폼별 Attestation profile이 원본 claim을 O.1~O.4 판정으로 매핑한다.

### 2.2 문서 내 요구 수준

| 표기 | 의미 |
|---|---|
| Required | custom SAK Evidence v1에서 반드시 포함하거나 검증하는 항목 |
| Conditional | 제품 유형 또는 CA 정책에 따라 포함하는 항목 |
| Recommended | 보안 또는 운영상 권장되는 항목 |
| Reference | Google/Samsung 구현을 설명하기 위한 참고 구조 |

`Required` 표시는 C2PA가 해당 claim 이름이나 wire field를 표준화했다는 의미가 아니다. C2PA가 요구하는 것은 O.1~O.4의 검증 결과이며, 이 문서의 claim 이름과 필수 조합은 그 결과를 만들기 위한 custom SAK Evidence v1 설계다.

## 3. 용어

| 용어 | 정의 |
|---|---|
| `K_claim` | 최종 C2PA Claim Signing Leaf 인증서에 포함될 공개키와 대응 개인키 |
| CSR | `K_claim` 공개키와 키 소유 증명을 포함하는 인증서 서명 요청 |
| Samsung Root | SAK 인증서 체인의 trust anchor |
| SAK | Samsung Root에 연결되고 하드웨어에서 보호되는 custom Samsung Attestation Key |
| AK | SAK가 인증한 운영용 Attestation Key. 실제 Evidence 또는 Evidence 인증서를 서명 |
| Evidence token | `K_claim` 공개키와 signed claims를 포함하고 AK가 서명한 COSE_Sign1 객체 |
| Evidence certificate | Google 방식과 유사하게 `K_claim`을 SPKI로 갖는 단기 X.509 인증서. custom SAK profile에서는 조건부 대안 |
| Evidence claims | challenge, 키 보안 속성, 플랫폼 상태, workload 식별값 등 서명 대상 값 |
| Endorsement | SAK/AK 인증서 및 제조·프로비저닝 정보를 포함한 신뢰 보조 자료 |
| Verifier | Evidence를 검증하는 CA 또는 CA가 위임한 Attestation 검증 서비스 |
| Reference values | 허용 product ID, 측정값, signer digest, revision, patch 기준 등 CA 측 정책값 |

## 4. 신뢰 모델

### 4.1 인증서 체인

custom SAK Evidence의 권장 신뢰 체인과 서명 관계는 다음과 같다.

```text
Samsung Root Certificate
        ↓ signs
SAK Certificate
        ↓ signs
Attestation Key Certificate

Attestation Key private key
        ↓ signs
COSE_Sign1 Evidence Token
        ├── subjectKey.spki = K_claim public key
        └── challenge + key/platform/workload claims
```

Root 인증서는 Evidence에 포함하지 않고 CA trust store에서 별도로 관리한다. 제출 package는 일반적으로 다음 객체를 포함한다.

```text
Evidence Token
Attestation Key Certificate
SAK Certificate
CSR
```

### 4.2 Evidence와 최종 인증서의 키 관계

CSR 기반 enrollment에서는 다음 공개키가 동일해야 한다.

```text
Evidence Token.subjectKey.spki
    == CSR.subjectPublicKeyInfo
    == Issued Claim Signing Leaf.subjectPublicKeyInfo
```

CSR 서명은 `K_claim` 개인키의 소유를 증명한다. Evidence Token 안의 `subjectKey.spki`와 그 속성은 SAK 신뢰 체계가 증명한 키를 인증서 발급 대상 키에 연결한다.

### 4.3 SAK와 AK의 역할

SAK는 장기·고가치 device Root of Trust key로 취급한다. Evidence마다 SAK를 직접 사용하는 방식보다 SAK가 AK를 인증하고 AK가 Evidence를 서명하는 계층이 권장된다.

| 키 | 역할 | 사용 빈도 | 보호 요구 |
|---|---|---|---|
| Samsung Root | SAK 인증 | 제조/프로비저닝 | 오프라인 또는 제조 HSM |
| SAK | AK 인증 | 낮음 | Knox Vault/TrustZone 등 하드웨어 |
| AK | Evidence Token 서명 | enrollment별 | 하드웨어 보호, 용도 제한 |
| `K_claim` | C2PA Claim 서명 | Manifest별 | 하드웨어 보호, non-exportable |

## 5. Attestation Evidence가 소유하는 정보

Evidence는 단순 상태 JSON이나 단독 서명이 아니다. 다음 구성요소 전체가 Evidence package를 이룬다.

```text
Evidence Package
├── COSE_Sign1 Evidence Token
│   ├── protected header
│   ├── K_claim public key
│   ├── Evidence profile/version
│   ├── CA challenge
│   ├── enrollment context
│   ├── key claims
│   ├── platform claims
│   ├── workload claims
│   └── AK signature
├── Attestation Key Certificate
├── SAK Certificate
└── CSR signed by K_claim
```

O.1~O.4 판정에 직접 필요한 최소 정보 그룹은 다음과 같다.

| 판정 | Evidence 안의 최소 정보 | CA가 보유할 비교값 |
|---|---|---|
| Freshness | challenge, enrollment context, policy ID | 원본 challenge, enrollment 상태, TTL |
| O.1 제품 적격성 | product ID와 하나 이상의 신뢰 가능한 product identity evidence | 등록 product ID, package/binary/signer/certificate 기준값 |
| O.2 키 보호 | `K_claim` SPKI, origin, protection, exportability, purpose, algorithm | Claim Signing key policy |
| O.3 Claim Generator | authenticated boot verdict, Claim Generator identity, patch 또는 승인 revision | 허용 boot 상태, Generator 측정값, patch/revision 기준 |
| O.4 처리 경로 | content processor identity, 해당 platform의 authenticated boot verdict, patch 또는 승인 revision | 허용 processor 목록과 platform 기준 |

boot measurement, debug 상태, TCB version 같은 값은 플랫폼이 신뢰 가능한 방식으로 제공할 때 판정 신뢰도를 높이는 추가 claim이다. 이러한 추가 claim이 없는 경우에도 기본 claim만으로 O.1~O.4를 입증할 수 있는지는 CA CPS의 플랫폼 profile에 명시해야 한다.

### 5.1 Envelope 및 freshness

| Claim | 요구 | 생성 주체 | 검증값 | 목적 |
|---|---|---|---|---|
| `profile` | Required | trusted attester | CA가 허용한 profile ID | schema와 정책 선택 |
| `version` | Required | trusted attester | 지원 version | parser downgrade 방지 |
| `challenge` | Required | CA가 발급, trusted attester가 포함 | CA 저장값과 byte-for-byte 일치 | freshness, replay 방지 |
| `enrollmentIdHash` | Required | trusted attester | CA enrollment ID의 hash | enrollment context 연결 |
| `policyId` | Required | CA가 지정, trusted attester가 포함 | 요청된 AL2 policy | policy confusion 방지 |
| `createdAt` | Conditional | trusted clock | 허용 clock skew | 진단 및 freshness 보조 |
| `expiresAt` | Conditional | trusted clock/CA policy | 현재 시각 이전이 아님 | Evidence 수명 제한 |
| `evidenceId` | Recommended | trusted attester | 중복 사용 여부 | replay 탐지 |

Challenge는 최소 256-bit CSPRNG 값 사용을 권장한다. CA는 challenge를 enrollment와 연결하고, 짧은 TTL 및 일회성 소비 상태를 관리한다. 신뢰 가능한 단말 시간이 없으면 freshness 판정은 CA challenge TTL을 기준으로 한다.

### 5.2 발급 대상 키 claims

| Claim | 요구 | 신뢰 가능한 원천 | CA 검증 |
|---|---|---|---|
| `subjectKey.spki` | Required | secure key manager | CSR SPKI와 byte-for-byte 동일 |
| `subjectKey.spkiSha256` | Required | secure key manager | CSR SPKI hash와 일치 |
| Evidence Certificate SPKI | X.509 대안에서 Required | secure key manager | CSR SPKI와 동일 |
| `subjectKey.origin` | Required | secure key manager | `generated` 또는 CA 허용값 |
| `subjectKey.protection` | Required | secure key manager | 허용된 TEE/SE/HSM/Knox Vault profile |
| `subjectKey.exportable` | Required | secure key manager | `false` |
| `subjectKey.purposes` | Required | secure key manager | `sign` 포함, 금지 용도 없음 |
| `subjectKey.algorithm` | Required | secure key manager | Claim Signing profile 허용값 |
| `subjectKey.parameters` | Required | secure key manager | RSA size, EC curve, digest/padding 정책 |
| `subjectKey.authPolicy` | Conditional | secure key manager | 앱/사용자 인증 정책 |
| `subjectKey.rollbackResistance` | Conditional | secure key manager | 제품 정책 |

키 속성은 일반 애플리케이션이 전달한 값을 서명하면 안 된다. SAK/AK와 연결된 secure key manager가 `K_claim`의 실제 key metadata를 읽어 Evidence에 넣어야 한다.

### 5.3 제품 및 workload claims

| Claim | 요구 | 신뢰 가능한 원천 | CA 검증 |
|---|---|---|---|
| `workload.productId` | Required | trusted loader/attester | Notice of Conformance와 CA 등록값 |
| `workload.implementationClass` | Required | 제품 profile | Edge/Backend/Distributed 등 등록값 |
| `workload.identityEvidence` | Required | measured boot/trusted loader/package verifier | 등록된 package, binary hash, signer digest 또는 identity certificate 중 하나 이상 |
| `workload.version` | Conditional | trusted loader | 허용 version |
| `workload.revision` | Conditional | trusted loader/build identity | 허용 revision/commit/image digest |
| `workload.configurationDigest` | Conditional | trusted configuration service | 허용 설정 profile |
| `workload.contentProcessors` | Required | trusted loader/measurement service | Asset/Assertion 처리 구성요소 목록과 각 구성요소의 identity evidence |

`identityEvidence` entry의 `type`은 `package`, `binary-measurement`, `signer-certificate-digest`, `identity-certificate`처럼 profile registry에 등록된 값만 허용한다. 각 entry는 type에 맞는 canonical value, hash algorithm, component name 및 필요한 version을 포함한다. CA의 제품별 profile은 허용 type과 최소 조합을 정한다.

패치 최신성 증거는 Applicant가 선택하고 CA가 승인한 방식에 따라 다음 중 하나를 사용한다.

- 패치 적용 시점 및 security patch level
- CA에 등록된 최소 허용 revision 이상임을 증명하는 version/revision/measurement

### 5.4 플랫폼 claims

| Claim | 요구 | 신뢰 가능한 원천 | CA 검증 |
|---|---|---|---|
| `platform.profile` | Required | immutable platform config | 허용 platform profile |
| `platform.securityLevel` | Required | Root of Trust | 허용 TEE/SE/Knox Vault/HSM 수준 |
| `platform.bootState` | Required | secure boot/measurement root | verified/approved 상태 |
| `platform.bootMeasurements` | Conditional | measured boot root | 허용 firmware/boot 측정값 |
| `platform.debugState` | Recommended | fuse/secure monitor | disabled 또는 허용 상태 |
| `platform.tcbVersion` | Conditional | secure monitor | 최소 TCB/security version |
| `platform.patchEvidence` | Required | trusted platform service | patch 기한 또는 승인 revision |
| `platform.rollbackState` | Conditional | secure monitor | rollback 방지 활성 |
| `platform.deviceClass` | Conditional | manufacturing data | 허용 제품군 |
| `platform.instancePseudonym` | Conditional | privacy-preserving hardware derivation | 중복/철회 확인용 pseudonym |

IMEI, serial number, 영구 device ID는 기본 Evidence에서 제외한다. 개별 단말 식별이 정책상 필요한 경우에도 raw identifier 대신 CA 전용 pseudonym 또는 keyed hash를 사용한다.

### 5.5 Evidence 바인딩 claims

| Binding | 요구 | 검증 |
|---|---|---|
| Evidence → enrollment | Required | `challenge`, `enrollmentIdHash`, `policyId` |
| Evidence → `K_claim` | Required | `subjectKey.spki`, `spkiSha256` 및 CSR SPKI |
| Evidence → product | Required | `workload.productId` |
| Evidence → platform | Required | SAK/AK chain 및 platform claims |
| Evidence → companion Evidence | Conditional | companion artifact hash |
| `K_claim` → CSR | CSR 사용 시 Required | CSR signature verification |

동일 challenge만 사용한 서로 다른 artifact는 같은 인스턴스에서 생성됐음을 완전히 증명하지 못한다. 여러 artifact를 조합할 경우 하나의 signed Evidence가 다른 artifact의 hash 또는 public key를 포함해야 한다.

## 6. 권장 Evidence 데이터 구조

### 6.1 COSE_Sign1 Evidence Token

기본안은 Samsung의 `AK signs attestation result` 구조에 맞춘 COSE_Sign1 token이다. 이 방식은 AK 인증서를 하위 CA로 사용할 필요가 없다.

| COSE 요소 | 값 |
|---|---|
| protected `alg` | CA가 허용한 AK signature algorithm |
| protected `content type` | `application/vnd.vendor.c2pa-sak-evidence+cbor` |
| protected `kid` | AK certificate 식별자 또는 AK SPKI hash |
| payload | deterministic CBOR로 인코딩한 `sak-evidence-claims` |
| external AAD | profile에 고정된 domain separation bytes |
| signature | AK private key로 생성한 COSE_Sign1 signature |

AK 인증서 체인은 token 외부의 Evidence package에 포함한다. Verifier는 package가 제공한 AK 인증서를 무조건 신뢰하지 않고 Samsung Root까지의 경로를 검증한 뒤 그 공개키로 token signature를 검증한다.

### 6.2 SAK 및 AK 인증서 profile

SAK가 AK 인증서를 발급하고 AK가 token만 서명하는 기본안의 profile은 다음과 같다.

| 인증서 | Basic Constraints | Key Usage | 권장 제약 |
|---|---|---|---|
| Samsung Root | `CA=true` | `keyCertSign`, `cRLSign` | trust anchor |
| SAK Certificate | `CA=true`, `pathLen=0` | `keyCertSign` | SAK policy OID, device hardware binding |
| AK Certificate | `CA=false` | `digitalSignature` | Evidence 전용 policy/EKU, 짧은 validity |

기존 Samsung SAK/AK 인증서 profile이 이 구조와 다르면 generic PKIX path를 임의로 가정하지 않고 Samsung이 정의한 chain validation 규칙을 사용해야 한다. production profile은 실제 인증서의 Basic Constraints, Key Usage, EKU 및 policy OID를 기준으로 확정한다.

### 6.3 `sak-evidence-claims` 논리 schema

아래 JSON은 사람이 읽기 위한 논리 표현이다. 실제 COSE payload는 deterministic CBOR를 사용한다.

```json
{
  "profile": "com.vendor.c2pa.sak-evidence",
  "version": 1,
  "challenge": "base64url-encoded-bytes",
  "enrollmentIdHash": "base64url-sha256",
  "policyId": "c2pa-al2-policy-id",
  "createdAt": 1786000000,
  "expiresAt": 1786000300,
  "evidenceId": "base64url-random-id",
  "subjectKey": {
    "spki": "base64url-der-subject-public-key-info",
    "spkiSha256": "base64url-sha256",
    "origin": "generated",
    "protection": "sak-backed-secure-hardware",
    "exportable": false,
    "purposes": ["sign"],
    "algorithm": "EC",
    "signatureAlgorithms": ["ES256"],
    "parameters": {
      "curve": "P-256"
    }
  },
  "platform": {
    "profile": "platform-profile-id",
    "securityLevel": "hardware",
    "bootState": "verified",
    "bootMeasurements": [
      {
        "component": "boot-chain",
        "alg": "sha-256",
        "digest": "base64url-digest"
      }
    ],
    "debugState": "disabled",
    "tcbVersion": "security-version",
    "patchEvidence": {
      "mode": "approved-revision",
      "value": "revision-id"
    }
  },
  "workload": {
    "productId": "generator-product-id",
    "implementationClass": "edge",
    "identityEvidence": [
      {
        "type": "binary-measurement",
        "component": "claim-generator",
        "alg": "sha-256",
        "digest": "base64url-digest"
      },
      {
        "type": "signer-certificate-digest",
        "alg": "sha-256",
        "digest": "base64url-sha256"
      }
    ],
    "version": "product-version",
    "revision": "approved-revision",
    "contentProcessors": [
      {
        "component": "asset-processor",
        "identityEvidence": [
          {
            "type": "binary-measurement",
            "alg": "sha-256",
            "digest": "base64url-digest"
          }
        ]
      }
    ]
  },
  "bindings": {
    "csrSha256": "base64url-sha256",
    "companionEvidenceHashes": []
  }
}
```

### 6.4 Canonical encoding

서명 대상 byte sequence가 구현마다 달라지지 않도록 다음을 고정한다.

- deterministic CBOR
- 정수 label 또는 고정 text label 중 하나를 profile에서 확정
- byte string과 text string 타입 구분
- hash algorithm 명시
- unknown critical field 처리 규칙
- 중복 map key 거부
- 부동소수점 값 사용 금지
- Unicode normalization이 필요한 text claim 최소화

COSE_Sign1 signature는 protected header, deterministic CBOR payload 및 profile에 고정된 external AAD를 함께 보호한다. `subjectKey.spki`, challenge, enrollment context, key/platform/workload claims가 모두 동일한 signature scope 안에 있어야 한다.

다음 hash 입력 형식을 profile에서 고정한다.

| 값 | 계산 규칙 |
|---|---|
| `subjectKey.spkiSha256` | `SHA-256(DER SubjectPublicKeyInfo)` |
| `bindings.csrSha256` | `SHA-256(DER CertificationRequest)` |
| `enrollmentIdHash` | `SHA-256(ASCII("C2PA-ENROLLMENT-ID-V1") || 0x00 || UTF8(enrollmentId))` |
| binary/firmware measurement | profile이 지정한 원본 image bytes 또는 measured-boot canonical input의 hash |
| signer digest | `SHA-256(DER signer certificate)` |
| companion Evidence hash | `SHA-256(companion artifact의 canonical bytes)` |

CBOR payload에서는 hash와 challenge를 byte string으로 저장한다. JSON 표현이나 전송 envelope에서 byte string을 표현해야 할 때는 padding 없는 base64url을 사용한다. 동일한 이름의 값을 UTF-8 text, PEM text 또는 platform-native object serialization에 대해 임의로 계산하지 않는다.

### 6.5 X.509 Evidence Certificate 대안

Google Key Attestation과 유사한 X.509 Evidence Certificate도 사용할 수 있다.

| X.509 필드 | 값 |
|---|---|
| `SubjectPublicKeyInfo` | `K_claim` public key |
| `Issuer` | Attestation Key Certificate subject |
| `BasicConstraints` | `CA=false` |
| `KeyUsage` | `digitalSignature` |
| `Validity` | enrollment 용도의 짧은 수명 |
| custom extension OID | deterministic CBOR `sak-evidence-claims` |
| Certificate signature | AK private key signature |

이 대안은 AK가 인증서를 발급할 권한이 있어야 하므로 AK Certificate에 `CA=true`, `pathLen=0`, `keyCertSign` 및 적절한 certificate policy가 필요하다. SAK Certificate의 `pathLen`도 subordinate CA인 AK를 허용하도록 최소 `1`이어야 한다. AK Certificate가 `CA=false` 또는 `digitalSignature` 전용이면 이 형식을 사용하지 않는다. custom extension OID는 조직에 할당된 enterprise OID arc 아래에서 발급하고, production에서 임시 OID를 사용하지 않는다.

## 7. Google Android Key Attestation의 실제 구조

### 7.1 생성 절차

Google Android Key Attestation은 임의 JSON Evidence를 Google key로 직접 서명해 반환하는 방식이 아니다. 실제 Evidence는 **생성된 키의 X.509 인증서 체인과 Android Key Attestation extension**이다.

```text
1. 서버가 challenge 생성
2. 앱이 KeyGenParameterSpec에 key policy와 challenge 설정
3. Android Keystore/KeyMint가 하드웨어에서 key pair 생성
4. Attestation infrastructure가 해당 public key의 인증서 발급
5. 인증서의 Attestation extension에 KeyDescription 포함
6. 앱이 KeyStore.getCertificateChain(alias)로 체인 획득
7. 체인을 off-device verifier로 전송
```

인증서 체인의 attested key certificate는 생성된 key의 public key를 포함한다. 인증서 서명이 public key와 Attestation extension을 함께 보호한다.

### 7.2 Google Evidence 구성

```text
Google Key Attestation Evidence
├── X.509 certificate chain
│   ├── attested key certificate
│   ├── attestation/intermediate certificates
│   └── Google Hardware Attestation Root로 연결
└── Key Attestation extension
    └── KeyDescription
```

최신 Android 검증 지침에서는 Attestation extension이 항상 leaf에 있다고 가정하지 않는다. Root에서 가장 가까운 방향으로 탐색했을 때 처음 발견되는 신뢰 가능한 Attestation extension을 사용하고, 공격자가 추가한 하위 인증서의 중복 extension은 신뢰하지 않는다.

### 7.3 `KeyDescription` 주요 값

| 필드 | 의미 | custom SAK 대응 |
|---|---|---|
| `attestationVersion` | schema version | `version` |
| `attestationSecurityLevel` | attested key 저장 위치의 security level | `platform.securityLevel` 및 `subjectKey.protection` |
| `keyMintVersion` | KeyMint implementation version | `platform.tcbVersion` |
| `keyMintSecurityLevel` | KeyMint security level | `subjectKey.protection` |
| `attestationChallenge` | key 생성 시 전달된 challenge | `challenge` |
| `uniqueId` | 선택적 privacy-sensitive 식별값 | 기본 제외, 필요 시 pseudonym |
| `softwareEnforced` | Android platform이 적용한 authorization | workload/platform software claims |
| `hardwareEnforced` | TEE/StrongBox가 적용한 authorization | key/platform hardware claims |

### 7.4 C2PA AL2 관련 Google authorization 값

저장소의 C2PA Certificate Policy v0.2가 Android Key Attestation을 AL2에 매핑한 주요 기대값은 다음과 같다.

| 영역 | KeyDescription 값 | CA 비교값 |
|---|---|---|
| security level | `attestationSecurityLevel` | `TrustedEnvironment(1)` 또는 `StrongBox(2)` |
| KeyMint security level | `keyMintSecurityLevel` | `TrustedEnvironment(1)` 또는 `StrongBox(2)` |
| freshness | `attestationChallenge` | CA challenge와 byte-for-byte 일치 |
| 앱 식별 | `softwareEnforced.attestationApplicationId.packageInfos` | 등록 package name과 version |
| 앱 signer | `softwareEnforced.attestationApplicationId.signatureDigests` | 등록 signing certificate SHA-256 |
| 키 용도 | `hardwareEnforced.purpose` | `SIGN(2)` 포함 |
| 키 algorithm | `hardwareEnforced.algorithm` | `RSA(1)` 또는 `EC(3)` |
| RSA key size | `hardwareEnforced.keySize` | `2048`, `3072`, `4096` 중 허용값 |
| EC key size | `hardwareEnforced.keySize` | `256`, `384`, `521` 중 허용값 |
| digest | `hardwareEnforced.digest` | `SHA_2_256(4)`, `SHA_2_384(5)`, `SHA_2_512(6)` 중 허용값 |
| RSA padding | `hardwareEnforced.padding` | `RSA_PSS(3)` |
| EC curve | `hardwareEnforced.ecCurve` | `P_256(1)`, `P_384(2)`, `P_521(3)` 중 허용값 |
| 키 생성 위치 | `hardwareEnforced.origin` | `GENERATED(0)` |
| 부팅 잠금 | `hardwareEnforced.rootOfTrust.deviceLocked` | `true` |
| verified boot | `hardwareEnforced.rootOfTrust.verifiedBootState` | `Verified(0)` |
| OS patch | `hardwareEnforced.osPatchLevel` | CP v0.2 기준 CSR 제출월과 직전 3개월 범위, 미래 값 거부 |
| vendor/boot patch | `hardwareEnforced.vendorPatchLevel`, `bootPatchLevel` | CSR 제출일 기준 90일 이내, 미래 값 거부 |
| 선택적 OEM 식별 | brand, manufacturer, model | 제품이 특정 OEM/모델로 제한될 때 CA 등록값 |

`softwareEnforced` 값은 Android OS가 보안 모델을 준수할 때 신뢰할 수 있다. `hardwareEnforced` 값은 TEE/StrongBox가 직접 수집하거나 적용한 값이다.

C2PA v0.2의 Android 표는 Attestation extension을 leaf certificate 경로로 표현한다. 최신 Android 검증 지침은 extension이 항상 leaf에 있다고 가정하지 않고 root에서 가장 가까운 신뢰 가능한 첫 extension을 사용하도록 요구한다. 구현은 Google의 최신 chain parsing 규칙으로 신뢰 가능한 extension을 선택한 뒤 그 값을 C2PA 정책에 매핑한다.

### 7.5 Google verifier 절차

1. 검증을 단말 외부의 신뢰 서버에서 수행
2. 현재 허용된 Google Hardware Attestation Root로 certificate path 검증
3. 체인 내 모든 인증서 서명과 Google provisioning 방식별 제약조건 검증
4. Google revocation status 확인
5. 신뢰 가능한 첫 Attestation extension 탐색
6. KeyDescription ASN.1 parsing 및 schema/version 검증
7. challenge 일치 검증
8. security level과 software/hardware authorization을 정책값과 비교
9. attested certificate public key와 발급 대상 public key 비교

Android 16 출시 기기는 Remote Key Provisioning(RKP)만 지원한다. RKP 인증서는 factory-provisioned certificate보다 짧은 수명을 사용하므로 인증서 validity와 최신 trust anchor/revocation 정보를 동적으로 관리해야 한다.

현재 Google 지침은 2021년 이전 출시 기기의 일부 만료된 factory attestation certificate를 지정된 legacy root로 연결되고 revocation되지 않은 경우 계속 신뢰하도록 안내한다. 반면 RKP certificate는 validity 검증이 필수다. 자체적인 일괄 만료 규칙보다 Google 검증 library와 최신 provider policy를 적용한다.

## 8. Samsung SAK의 실제 reference 구조

Samsung Knox 문서는 SAK를 장기 device attestation root 역할로 사용하고, 별도의 Attestation Key가 실제 결과를 서명하는 계층을 설명한다.

```text
제조 시:
Samsung Root
    └── signs SAK Certificate

초기화 시:
SAK
    └── signs Attestation Key Certificate

Attestation 시:
Attestation Key
    └── signs Attestation Result + nonce
```

검증 서버는 Samsung Root를 trust anchor로 보유하고 다음을 검증한다.

1. SAK Certificate가 Samsung Root로 연결되는지 확인
2. Attestation Key Certificate가 SAK로 인증됐는지 확인
3. Attestation Result signature를 AK public key로 검증
4. 요청 nonce와 Result nonce를 비교
5. Result의 device/platform 상태를 정책과 비교

Samsung 문서에는 SAK 인증서 체인의 subject UID가 IMEI와 serial number를 포함해 계산한 hash를 담을 수 있다고 설명되어 있다. raw identifier가 아니더라도 안정적인 device-linked 값이므로 Evidence package 수집, 보관 및 접근 정책에서 개인정보와 장기 linkability를 고려해야 한다.

같은 Samsung 문서는 Keystore attest API가 application key의 attested key certificate, SAK certificate 및 Root certificate로 구성된 체인을 반환하는 형태도 설명한다. SAK 서비스가 `K_claim`에 대한 attested key certificate 발급 기능을 제공한다면 Google과 유사한 X.509 방식을 사용할 수 있고, AK가 result 서명만 제공한다면 COSE_Sign1 Evidence Token 방식을 사용한다.

custom SAK 설계는 이 계층을 유지한다. SAK는 AK의 권한과 출처를 인증하고, AK가 enrollment별 Evidence Token을 서명한다. SAK가 Evidence를 직접 서명하는 축약형은 가능하지만 SAK 사용량, device linkability, key rotation 및 compromise 영향이 커지므로 기본 profile로 사용하지 않는다.

## 9. Custom SAK Evidence 생성 절차

### 9.1 CA challenge 생성

CA는 다음 enrollment context를 생성하고 서버 상태에 저장한다.

```text
enrollmentId
challenge
policyId
productId
expectedKeyProfile
issuedAt
expiresAt
status = ISSUED
```

challenge와 policy context는 TLS로 제품 인스턴스에 전달한다.

### 9.2 `K_claim` 생성

secure key manager가 `K_claim`을 생성한다.

- 하드웨어 내부 생성
- private key non-exportable
- C2PA Claim Signing profile에 맞는 algorithm과 parameter
- sign 용도 제한
- key metadata를 trusted attester가 직접 조회 가능

### 9.3 CSR 생성

CSR 기반 profile에서는 `K_claim` 생성 직후 CSR을 만들고 같은 개인키로 서명한다.

```text
CSR.signature = Sign(K_claim_private, CertificationRequestInfo)
```

`bindings.csrSha256`를 사용하는 경우 PEM text가 아니라 DER-encoded CSR 전체의 SHA-256을 계산한다. CSR 전체 hash binding을 사용하지 않는 profile에서도 Evidence Token의 `subjectKey.spki`와 CSR SPKI 비교는 필수다.

### 9.4 trusted claims 수집

trusted attester는 다음 값을 신뢰 원천에서 직접 수집한다.

- `K_claim` SPKI 및 key metadata
- secure boot/verified boot state
- firmware/TCB/patch/revision
- Claim Generator binary measurement
- code-signing identity
- Asset/Assertion 처리 구성요소 measurement
- CA challenge 및 enrollment context

일반 앱이 전달한 `bootState`, `exportable`, `binaryDigest` 같은 값을 검증 없이 Evidence에 복사하지 않는다.

### 9.5 Evidence claims 생성

trusted attester가 `sak-evidence-claims`를 만들고 deterministic CBOR로 직렬화한다.

```text
claimsBytes = DeterministicCBOR(sak-evidence-claims)
```

### 9.6 Evidence Token 생성 및 서명

trusted attester는 claims를 COSE_Sign1 payload로 넣고 AK로 서명한다.

```text
protectedHeader = {
    alg,
    contentType = application/vnd.vendor.c2pa-sak-evidence+cbor,
    kid = AK identifier
}

payload = claimsBytes
externalAAD = "C2PA-AL2-SAK-EVIDENCE-V1"
signature = Sign(AK_private, COSE_Sig_structure)
evidenceToken = COSE_Sign1(protectedHeader, payload, signature)
```

AK certificate는 SAK가 서명하고, SAK certificate는 Samsung Root로 연결된다. SAK와 AK private key는 일반 애플리케이션에 노출하지 않는다.

### 9.7 제출 package 생성

CA 제출 package는 다음과 같다.

```json
{
  "enrollmentId": "server-issued-id",
  "csr": "PEM-or-DER-CSR",
  "attestationEvidence": {
    "profile": "com.vendor.c2pa.sak-evidence",
    "evidenceToken": "base64url-COSE-Sign1",
    "certificateChain": [
      "Attestation Key Certificate",
      "SAK Certificate"
    ]
  }
}
```

Samsung Root Certificate는 package에 포함하지 않고 CA trust store에서 선택한다.

### 9.8 X.509 대안 생성

실제 AK Certificate가 하위 인증서 발급 권한을 갖는 profile에서는 6.5의 X.509 Evidence Certificate를 생성할 수 있다. 이 경우 Evidence Certificate SPKI를 `K_claim`으로 설정하고 동일한 claims를 custom extension에 넣은 뒤 AK로 `TBSCertificate`를 서명한다. AK 인증서가 `CA=false`인 환경에서 이 절차를 사용하지 않는다.

## 10. Custom SAK Evidence 검증 절차

### 10.1 구조 검증

- 지원 profile 및 version
- COSE_Sign1 구조, protected header 및 content type
- envelope profile과 signed payload profile 일치
- certificate chain 순서와 최대 길이
- 허용 signature/hash algorithm
- deterministic CBOR와 schema 적합성
- unknown critical claim 거부

### 10.2 신뢰 체인 검증

- Evidence Token signature를 AK public key로 검증
- protected `kid`가 AK Certificate 식별자 또는 AK SPKI hash와 일치
- protected `alg`와 고정 external AAD가 profile과 일치
- AK Certificate signature를 SAK public key로 검증
- SAK Certificate를 Samsung Root trust anchor로 검증
- Basic Constraints, Key Usage, path length 및 certificate policy 검증
- SAK/AK revocation, suspension 또는 denylist 확인
- certificate validity 및 algorithm 정책 확인

### 10.3 freshness 검증

- `challenge`가 CA 저장값과 byte-for-byte 일치
- enrollment ID와 `enrollmentIdHash` 일치
- `policyId` 일치
- TTL 이내
- enrollment 상태가 `ISSUED`
- 성공 시 challenge를 원자적으로 `CONSUMED` 처리
- 인증되지 않은 format/path 실패로 challenge를 소비하지 않고 별도 rate limit 적용
- `evidenceId` 중복 여부 확인

### 10.4 키 바인딩 및 PoP 검증

```text
Evidence subjectKey.spki == CSR SPKI
Evidence subjectKey.spkiSha256 == SHA-256(Evidence subjectKey.spki)
CSR signature == valid
```

추가로 Evidence의 key origin, protection, exportability, purpose 및 algorithm을 AL2 key policy와 비교한다.

### 10.5 O.1 제품 적격성

- 서명된 Notice of Conformance 검증
- Notice 안의 CPL record와 Subscriber DN 확인
- `workload.productId` 일치
- Max Assurance Level이 AL2 이상
- 제품 profile이 요구하는 package, binary, signer 또는 certificate identity와 version/revision 일치
- Evidence method가 제품 등록정보와 CA CPS에서 허용됨

### 10.6 O.2 키 보호

- `K_claim` hardware generation
- non-exportable
- 허용 secure hardware profile
- Claim Signing 용도
- 허용 algorithm/parameter
- CSR PoP
- SAK/AK가 해당 key metadata를 trusted path로 확인

### 10.7 O.3 Claim Generator 보호

- 승인된 authenticated boot verdict
- 플랫폼 profile에서 제공하는 경우 boot measurements
- debug/rollback 상태
- TCB/security version
- platform patch 기준
- Claim Generator patch 시점 또는 승인 revision
- Claim Generator의 승인된 identity evidence

### 10.8 O.4 콘텐츠 처리 경로 보호

- Asset/Assertion 처리 component 목록
- 각 component의 승인된 identity evidence
- patch 시점 또는 승인 revision
- 동일 platform/workload context 바인딩

### 10.9 최종 판정

```text
trustChain        = PASS | FAIL | NOT_PROVEN
freshness         = PASS | FAIL | NOT_PROVEN
keyBinding        = PASS | FAIL | NOT_PROVEN
O.1 eligibility   = PASS | FAIL | NOT_PROVEN
O.2 keyProtection = PASS | FAIL | NOT_PROVEN
O.3 generator     = PASS | FAIL | NOT_PROVEN
O.4 contentPath   = PASS | FAIL | NOT_PROVEN
```

AL2 Leaf는 모든 필수 항목이 `PASS`일 때만 발급한다. `NOT_PROVEN`은 `PASS`로 간주하지 않는다. 정책이 허용하면 다음으로 낮은 Assurance Level을 별도로 평가할 수 있다.

## 11. CA가 사전에 보유해야 하는 값

### 11.1 Trust material

- Samsung Root Certificate 목록
- 허용 SAK certificate policy 및 profile
- AK certificate profile
- revocation/denylist 조회 위치와 cache 정책
- 허용 signature/hash algorithm
- root rotation 및 overlap 정책

### 11.2 Product reference values

- Notice of Conformance와 CPL record
- product ID 및 Subscriber DN
- Max Assurance Level
- implementation class
- 허용 code-signing certificate digest
- 허용 binary/image/firmware measurements
- 허용 version/revision/commit
- 최소 patch/security/TCB version
- Asset/Assertion 처리 component 목록

### 11.3 Key policy

- 허용 algorithm 및 parameter
- key purpose
- hardware protection profile
- non-exportability 요구
- key authentication 정책
- rotation과 lifetime

### 11.4 Enrollment state

- enrollment ID
- challenge 원문
- policy ID
- product ID
- 요청 시각과 만료 시각
- 사용 상태
- evidence ID replay cache

## 12. 실패 코드

| 코드 | 의미 |
|---|---|
| `EVIDENCE_FORMAT_INVALID` | schema, CBOR 또는 extension 오류 |
| `EVIDENCE_PROFILE_UNSUPPORTED` | profile/version 미지원 |
| `TRUST_CHAIN_INVALID` | Samsung Root까지 path 검증 실패 |
| `ATTESTATION_SIGNATURE_INVALID` | Evidence Token, AK 또는 SAK signature 실패 |
| `ATTESTATION_KEY_REVOKED` | AK 또는 SAK가 revoked/suspended |
| `CHALLENGE_MISMATCH` | CA challenge 불일치 |
| `EVIDENCE_EXPIRED` | enrollment/Evidence TTL 만료 |
| `EVIDENCE_REPLAYED` | challenge 또는 evidence ID 재사용 |
| `POLICY_CONTEXT_MISMATCH` | enrollment, product 또는 policy binding 실패 |
| `SUBJECT_KEY_MISMATCH` | Evidence `subjectKey.spki`와 CSR SPKI 불일치 |
| `PROOF_OF_POSSESSION_INVALID` | CSR signature 실패 |
| `KEY_NOT_HARDWARE_PROTECTED` | 허용 하드웨어 보호 증거 없음 |
| `KEY_EXPORTABLE` | private key export 가능 |
| `KEY_PROFILE_INVALID` | algorithm/purpose/parameter 불일치 |
| `PRODUCT_NOT_CONFORMANT` | Notice/CPL 검증 실패 |
| `WORKLOAD_NOT_APPROVED` | binary, signer, version/revision 불일치 |
| `PLATFORM_NOT_APPROVED` | boot, debug, TCB 또는 patch 정책 실패 |
| `CONTENT_PATH_NOT_APPROVED` | Asset/Assertion 처리 component 검증 실패 |
| `REQUIRED_CLAIM_MISSING` | 필수 claim 부재 |

## 13. Google 방식과 custom SAK 방식 비교

| 항목 | Google Android Key Attestation | custom SAK Evidence |
|---|---|---|
| Trust anchor | Google Hardware Attestation Root | Samsung Root |
| 장기 device key | factory/RKP attestation infrastructure | SAK |
| 운영 attestation key | factory 또는 RKP key | SAK가 인증한 AK |
| Evidence 형태 | X.509 chain + KeyDescription extension | COSE_Sign1 token + SAK/AK X.509 chain |
| 발급 대상 키 binding | attested certificate SPKI | signed `subjectKey.spki` |
| challenge 위치 | KeyDescription.attestationChallenge | signed token payload의 `challenge` |
| key claims | softwareEnforced/hardwareEnforced | subjectKey/platform claims |
| workload claims | attestationApplicationId 등 | workload claims |
| revocation | Google status list | Samsung/custom revocation service 필요 |
| 검증 위치 | off-device verifier | CA 또는 위임 verifier |

## 14. 보안 및 개인정보 보호 요구사항

- SAK direct signing 대신 SAK-certified AK 사용
- Evidence schema 밖의 arbitrary data signing 금지
- trusted component가 직접 측정·수집한 claim만 포함
- challenge, policy ID, product ID 및 subject key를 하나의 signature scope에 포함
- deterministic encoding 및 domain separation 적용
- raw IMEI/serial/device ID 기본 제외
- SAK Certificate subject UID와 certificate serial의 장기 linkability 평가
- SAK chain 원문 접근 권한과 보존 기간 최소화
- 필요하면 별도 verifier가 SAK chain을 검증하고 CA에는 policy verdict와 `K_claim` binding만 전달
- AK rotation과 short-lived Evidence 사용
- root/AK/SAK revocation 체계 필수
- verifier는 단말 외부에서 실행
- 실패 시 상세 내부 사유를 단말에 과도하게 노출하지 않음
- 로그에 raw identifier, Evidence 원문 또는 민감 measurement를 불필요하게 저장하지 않음

## 15. 확정이 필요한 설계 항목

1. COSE protected header와 deterministic CBOR의 정수 label registry
2. 실제 SAK 및 AK certificate profile
3. AK rotation, validity 및 revocation 방식
4. Samsung Root 배포와 rotation 방식
5. platform별 trusted measurement 수집 경로
6. Claim Generator 및 content processor reference measurement 공급 방식
7. patch 시점 방식과 approved revision 방식 중 제품별 선택
8. Evidence TTL 및 challenge TTL
9. device pseudonym 사용 여부와 privacy policy
10. CSR 전체 hash binding 포함 여부
11. Evidence 검증을 CA 내부에서 수행할지 별도 verifier에 위임할지
12. X.509 Evidence Certificate 대안 지원 여부와 production OID

## 16. 구현 체크리스트

### Evidence producer

- [ ] `K_claim` 하드웨어 생성 및 non-exportable 설정
- [ ] trusted key metadata 수집
- [ ] trusted platform/workload measurement 수집
- [ ] challenge와 enrollment context 포함
- [ ] deterministic CBOR 생성
- [ ] `subjectKey.spki`에 `K_claim` public key 사용
- [ ] AK로 COSE_Sign1 Evidence Token 서명
- [ ] SAK → AK chain 포함
- [ ] `K_claim`으로 CSR 서명

### CA verifier

- [ ] Samsung Root trust anchor 관리
- [ ] Evidence → AK → SAK → Root path 검증
- [ ] revocation 및 validity 검증
- [ ] COSE header, signature 및 CBOR schema 검증
- [ ] challenge/TTL/replay 검증
- [ ] Evidence `subjectKey.spki`와 CSR SPKI 일치
- [ ] CSR PoP 검증
- [ ] O.1~O.4 reference value 비교
- [ ] 모든 필수 verdict PASS 확인
- [ ] 최종 Claim Signing Leaf에 동일 SPKI 사용

## 17. 근거 자료

### 저장소

- [C2PA Certificate Policy v0.2](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
  - enrollment 인증 및 키 소유 검증: 469행 부근
  - Dynamic Evidence 및 인증서 발급: 511행 부근
  - AL2 O.1~O.4 요구사항: 1697행 부근
  - challenge 및 Android profile: 1766행 부근
- [C2PA Generator Product Security Requirements v0.2](../../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md)
  - AL2 product identity evidence: 364행 부근
  - key protection evidence: 378행 부근
  - Claim Generator evidence: 474행 부근
  - content processing evidence: 560행 부근

### 공식 외부 자료

- [Android Developers: Verify hardware-backed key pairs with key attestation](https://developer.android.com/privacy-and-security/security-key-attestation)
- [AOSP: Key and ID attestation](https://source.android.com/docs/security/features/keystore/attestation)
- [Android Developers: KeyGenParameterSpec.Builder](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder)
- [Samsung Knox: Enhanced Attestation v3](https://docs.samsungknox.com/dev/knox-attestation/enhanced-attestation-v3/)
- [Samsung Knox: Device Health Attestation](https://docs.samsungknox.com/admin/fundamentals/whitepaper/core-platform-security/device-health-attestation/)
- [C2PA: Attestation in the C2PA Framework](https://spec.c2pa.org/specifications/specifications/1.4/attestations/attestation.html)
- [RFC 9052: CBOR Object Signing and Encryption](https://www.rfc-editor.org/rfc/rfc9052.html)
- [RFC 8949: Concise Binary Object Representation](https://www.rfc-editor.org/rfc/rfc8949.html)

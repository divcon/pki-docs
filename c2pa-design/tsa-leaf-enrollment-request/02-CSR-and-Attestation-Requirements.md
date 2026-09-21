# TSA CSR과 선택적 Attestation 요구사항

## 1. 서로 다른 요구를 분리한다

| 대상 | 필수성 | 설명 |
|---|---|---|
| key-pair ownership | `C2PA-REQUIRED` | CA가 발급 대상 key pair 소유를 확인해야 함 |
| PKCS#10 CSR | `ARCH-DECISION` | CP가 든 소유 확인 방법의 한 예. 이 architecture의 기본 방법 |
| TSA CSR/certificate profile | `C2PA-REQUIRED` | 공식 TSA Leaf profile과 schema 준수 |
| On-Device TSA TEE/키/용도/active-key 상태 | `C2PA-REQUIRED` runtime/implementation | 제품·서비스가 실제 운영에서 만족해야 함 |
| per-enrollment Compound Evidence | 기본 `NOT REQUIRED` | C2PA TSA enrollment wire로 정의되지 않음 |
| custom attestation | `OPTIONAL CPS EXTENSION` | CA가 별도 profile로 채택한 경우에만 해당 transaction에서 필수 |

CSR은 key ownership/PoP를 보여 주지만 TEE 실행, non-exportability, TA identity, trusted time 또는 single-active-key 전체를 증명하지 않는다. 그렇다고 그 사실들이 자동으로 enrollment payload가 되는 것도 아니다. 운영 요구는 설계·구현·시험·감사로 보증할 수 있다.

## 2. TSA PKCS#10 CSR

기본 TSA profile은 하나의 strict DER PKCS#10 object를 받는다.

```text
CertificationRequest ::= SEQUENCE {
  certificationRequestInfo CertificationRequestInfo,
  signatureAlgorithm       AlgorithmIdentifier,
  signature                BIT STRING
}
```

서버는 최소한 다음을 확인한다.

- trailing bytes, BER-only encoding, duplicate/unknown 구조를 허용하지 않는 strict DER
- `CertificationRequestInfo` 원본 DER에 대한 CSR signature
- 허용된 RSA/ECDSA algorithm, key size/curve 및 parameter 규칙
- CSR Subject의 ASN.1 Name 구조와 공식 schema의 C/O/CN 포함 조건; 서비스 식별·Subject 불일치 처리는 §2.1에서 별도 판단
- 공식 `tsaLeaf.csr.schema.json`에 부합하는 requested extension
- `K_tsu` 공개키 재사용 금지 등 project lifecycle policy

CSR signature 검증은 C2PA가 요구하는 key ownership 확인을 구현하는 방법이다. CP 473은 signed CSR 외에 KMS configuration inspection도 예로 들므로, “PKCS#10 자체가 C2PA에서 유일하게 필수”라고 표기하지 않는다.

### 2.1 Subject

공식 TSA CSR schema는 Subject의 구조와 `C`, `O`, `CN` 포함을 요구한다(`tsaLeaf.csr.schema.json:692-740`). 최종 TSA Leaf Subject는 해당 TSA service를 식별하는 unique name이며 C/O/CN을 포함한다(CP:1347). 최종 Subject 조건과 원본 CSR의 등록 DN 일치 조건을 동일하게 취급하지 않는다.

CP:517은 TSA 발급에 CA business practices의 identification/authentication/verification 절차를 요구한다. CPL은 Generator Product의 기준이며 TSA 서비스 DN을 대조하는 목록이 아니다. CA는 CSR Subject, 별도 신청정보의 서비스 식별자 또는 인증 계정에 연결된 등록정보로 대상을 식별하도록 절차를 정할 수 있다. 이들은 가능한 설계 예시이며 C2PA가 지정한 wire field가 아니다.

- **식별:** 어느 TSA 운영기관·서비스의 요청인지 확인한다. CSR Subject는 조회용 이름으로 사용할 수 있다.
- **인증:** 등록된 신청자가 실제로 요청하는지 secure credential로 확인한다. Subject 문자열은 인증수단이 아니다.
- **검증:** 해당 TSA를 위한 발급 권한, 발급 대상 키 소유와 인증서에 넣을 정보의 정확성을 확인한다. CSR signature/PoP는 key ownership을 확인하는 방법이며 운영기관·서비스의 신원을 대신 증명하지 않는다(CP:471-473,1542-1556).

CSR C/O/CN 누락·구조 부적합은 CSR profile 실패다. 등록 TSA DN과 다른 문자열이 들어왔다는 사실만으로 모든 요청을 자동 거부하거나 수락하지 않는다. CA의 문서화된 절차가 거부·보완 요청·독립적으로 검증된 식별정보 사용을 정한다. CSR Subject로 식별하는데 대상이 확인되지 않으면 보완 전에는 발급하지 않는다. 별도 정보로 대상을 확인한 경우에도 요청의 정확성·권한·키와의 관계 및 Subject 불일치 처리 근거를 확인·기록한다. 확인되지 않은 서비스에 임의의 Subject를 붙여 승인하는 절차가 아니다.

원본 CSR의 서명 bytes는 변경하지 않는다. CSR 변경이 필요하면 신청자가 다시 서명한다. 최종 Subject는 확인된 TSA 서비스와 인증서 profile에 따라 구성한다. [01의 서비스 ID 기반 API](01-Enrollment-Request-Contract.md)는 이 식별 방식의 한 예이며, 원문이 CSR Subject의 일괄 무시·덮어쓰기를 명시적으로 허용했다고 해석하지 않는다.

### 2.2 SPKI

공식 profile이 허용하는 범위는 다음과 같다.

- RSA `rsaEncryption`, 2048 bits 이상
- EC `id-ecPublicKey`, P-256/P-384/P-521
- EdDSA 제외

구체 signature AlgorithmIdentifier/parameter 조합은 RFC와 공식 decoded-output schema에 맞게 strict allow-list로 고정한다.

### 2.3 Requested extensions

이 프로젝트의 TSA leaf PKCS#10 CSR은 `CertificationRequestInfo.attributes`의 `extensionRequest`에 아래 네 확장을 반드시 포함해야 한다. 이는 [공식 TSA leaf CSR profile](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json)의 요구사항이며, 표는 디코딩한 확장값을 나타낸다.

| 필수 요청 확장 | 요청값 | `critical` |
|---|---|---|
| Basic Constraints (`2.5.29.19`) | `cA=FALSE` | `TRUE` |
| Key Usage (`2.5.29.15`) | `digitalSignature`, `contentCommitment` 두 비트만 `TRUE`. 나머지 비트는 모두 `FALSE` | `TRUE` |
| Extended Key Usage (`2.5.29.37`) | `id-kp-timeStamping` (`1.3.6.1.5.5.7.3.8`) 정확히 하나만 포함 | `TRUE` |
| Certificate Policies (`2.5.29.32`) | `c2pa-certificate-policy` (`1.3.6.1.4.1.62558.1.1`) 반드시 포함 | `FALSE` |

`contentCommitment`와 `nonRepudiation`은 같은 Key Usage 비트의 이름이다. CA는 인증서 정책에 따라 자신이 관리하는 IANA private arc의 CPS 식별용 policy OID를 추가할 수 있으며, policy qualifier는 선택사항이다. CSR은 C2PA Claim Signing용 AL/CPL 확장을 요청하지 않는다.

**CSR 작성 방침:** 최종 TSA leaf 인증서의 제약을 반영하여 `pathLenConstraint`는 요청하지 않는다. 공식 CSR 스키마는 이 생략을 검사하지 않는다. 생략의 근거는 [최종 인증서 스키마](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json)와 [RFC 5280 §4.2.1.9](https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.9)이다.

CA는 CSR 요청값을 검증한 뒤 server-controlled certificate template를 생성한다. 최종 인증서는 [CP의 TSA leaf profile](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#tsa-time-stamp-signing-leaf-certificates)과 공식 인증서 스키마에 부합해야 한다. SKI, AKI, issuer, serial, validity, AIA/CDP와 최종 extension encoding은 CA가 결정·생성한다.

## 3. TEE·timestamp-only·single-active-key

C2PA CP의 TSA 절에서 직접 확인되는 의무는 다음과 같다.

1. time-stamp private key는 그 목적에 전용이다.
2. TSU는 한 시점에 하나의 time-stamp signing key만 active다.
3. On-Device TSA application은 TEE에서 실행된다.
4. TSU signing key는 TEE에서 생성·보관된다.
5. time traceability/accuracy, drift-stop 및 On-Device 24시간 sync-attempt 요구를 만족한다.

이 문장들은 runtime/implementation/operations 요구다. 원문에는 각 Leaf enrollment request에 다음 값을 넣으라는 규정이 없다.

- TA UUID/measurement
- boot/patch/debug state
- timestamp-only ACL dump
- active-key count 또는 `old/new/staged` state
- signed time observation
- custom EAT/OID 또는 attestation `x5chain`

따라서 기본 발급 심사는 이러한 field를 요구하지 않는다. 조직은 설계 검토, TEE enforcement, operation-specific API, local state machine, conformance test, release approval, 운영 audit와 monitoring으로 위 의무를 보증한다.

## 4. 선택적 CPS Compound Attestation

CA가 위 운영 보증에 원격 attestation을 추가하려면 별도 profile로 명확히 선택한다. 예:

```text
c2pa-on-device-tsa              # base, no attestationEvidence
c2pa-on-device-tsa-attested-v1  # optional CPS extension
```

확장 profile은 최소한 다음을 machine-readable하게 고정해야 한다.

- Evidence format/media type와 signed bytes
- signer trust anchor, chain/status 및 algorithm
- required Evidence role과 정확한 cardinality
- transaction/challenge/audience freshness
- subject key 표현과 CSR SPKI binding
- TA/TEE claim의 의미와 Reference Value source/version
- parser limits, error contract, retention/privacy 및 test vector

이 profile이 선택된 transaction에서는 누락·unknown version·signature failure·key mismatch를 fail-closed로 처리한다. 반대로 base profile에 이 검증을 소급 적용하지 않는다.

### 4.1 INITIAL과 REKEY

CP의 “re-key를 신규 신청처럼 identity validate” 조항만으로 fresh attestation이 자동 도출되지는 않는다. 다만 이 문서의 예시 `c2pa-on-device-tsa-attested-v1` profile은 INITIAL과 REKEY 모두 fresh Evidence를 요구하도록 고정한다. 다른 operation/cardinality/freshness 정책이 필요하면 다른 이름/version의 profile로 정의하고, base와 attested profile 사이 전환은 server-authorized explicit migration으로만 허용한다.

### 4.2 Android Key Attestation

C2PA CP의 상세 Android/Dynamic Evidence predicate는 Generator Product의 Claim Signing AL2 경로다. TSA Leaf에 그대로 적용되는 규정이 아니다.

Android Key Attestation을 optional TSA profile에 쓰면 key origin/security level, boot state 등 일부 사실을 보조할 수 있지만 다음을 단독으로 증명하지는 않는다.

- TSA application 자체의 TEE 실행
- RFC 3161 parsing/time/serial path의 identity
- timestamp-only operation ACL 전체
- trusted-time traceability와 drift-stop
- TSU당 single-active-key 및 rollback-safe rotation

그러므로 Android evidence를 TSA에 사용하려면 custom provider contract가 그 범위와 추가 보증을 명시해야 한다. “Android chain만으로 TSA가 C2PA conformant” 또는 “Android chain이 항상 TSA enrollment에 필요”라고 결론 내리면 안 된다.

## 5. 감사와 개인정보

기본 profile의 발급 기록은 caller/service, key/CSR digest, policy/issuer version, serial/certificate digest와 decision을 연결한다. Evidence 관련 digest/verdict/provider version은 optional profile에서 Evidence가 실제 제출된 경우에만 기록한다.

private key, 불필요한 raw Evidence, 직접 장치 식별자 및 client self-asserted verdict를 일반 log/metric에 남기지 않는다.

## 6. 근거

- `C2PA Certificate Policy.md:469-473`: credential과 key ownership
- 같은 문서 `:511-529`: TSA issuance와 Claim Signing Dynamic Evidence의 분리
- 같은 문서 `:915-939`: TSA runtime/implementation 의무
- [C2PA Certificate Policy — TSA Time-Stamp Signing Leaf Certificates](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#tsa-time-stamp-signing-leaf-certificates), 1334–1385행: 최종 인증서 profile. 1362–1377행은 네 확장의 값·critical 및 추가 정책 OID·qualifier의 선택성
- 같은 문서 `:1684` 이후: Generator Product AL1/AL2 Dynamic Evidence
- [TSA leaf CSR schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json), 852–1078행: `requestedExtensions`와 네 확장의 필수값·critical, AL/CPL 요청 금지
- [TSA leaf certificate schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json): 최종 인증서의 decoded-output profile. 1077–1113행은 Basic Constraints와 `pathLenConstraint` 제약
- [RFC 2985 §5.4.2](https://www.rfc-editor.org/rfc/rfc2985.html#section-5.4.2): CSR의 `extensionRequest` 속성
- [RFC 5280 §4.2.1.9](https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.9): `cA=FALSE`인 인증서의 `pathLenConstraint` 금지
- RFC 2986, RFC 5280, RFC 3161

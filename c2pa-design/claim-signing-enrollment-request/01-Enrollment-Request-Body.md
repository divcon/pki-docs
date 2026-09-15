# Enrollment Request Body

## 1. 문서 경계

이 문서는 C2PA Claim Signing Certificate enrollment에 필요한 **요청 body**만 정의한다. URL, HTTP method/status, response, transaction/state machine, idempotency, retry와 stable error는 정의하지 않는다.

C2PA Certificate Policy는 secure enrollment credential, key ownership, CSR, Claim Signing 자격과 AL별 Dynamic Evidence의 의미를 규정하지만 JSON wrapper는 규정하지 않는다(CP:457-529,1686-1768). RFC 2986도 PKCS#10 구조와 signature를 정의할 뿐 전송 형식은 범위 밖으로 둔다(RFC 2986 §1, §3). 따라서 아래 JSON field와 cardinality는 C2PA field가 아니라 C2PA 의미를 운반하기 위한 `PROJECT` 선택이다.

## 2. 인증 방식은 하나가 아니다

Enrollment에서 “인증”은 다음 여섯 predicate를 합친 말이다. 서로 대체할 수 없다.

| predicate | 확인 대상 | 시점 | body 포함 여부 | authority / source |
|---|---|---|---|---|
| Subscriber I/A/V | 신청 조직과 대표자의 identity·authority, ≤398일 재인증 | onboarding + issuance gate | 원자료 없음; server approval 참조 | `C2PA REQUIRED`, CP:401-477,491-509 |
| Subscriber Agreement/Terms | legally valid agreement 또는 affiliated terms acknowledgement | onboarding + issuance gate | 원문서 없음; current agreement record 참조 | `C2PA NON-BCP14-OBLIGATION`, CP:1518-1558와 CP:10-12 |
| secure enrollment credential | 호출 주체가 승인된 Subscriber 측 주체임 | request transport + issuance gate | body에 secret을 넣지 않음 | `C2PA REQUIRED`, CP:469-473,507-509; 구체 방식은 `CA-CPS` |
| GP instance authentication | 적격 Generator Product의 실제 instance가 요청함 | 매 INITIAL/REKEY enrollment | body의 자기주장이 아니라 credential verdict와 server binding | AL1 `C2PA REQUIRED` CP:1686-1695; AL2 `C2PA REQUIRED` CP:1712-1714; GSPR:338-376 |
| CSR proof of possession | 요청 공개키의 private key로 CSR을 서명할 수 있음 | 매 INITIAL/REKEY | `csr.value`의 PKCS#10 signature | RFC 2986 §3/§4.2; `C2PA REQUIRED` CP:471-473 |
| AL2 attestation trust | O.1~O.4를 hardware Root of Trust가 뒷받침함 | AL2 INITIAL/REKEY | provider-signed `evidenceItems` | `C2PA REQUIRED`, CP:1712-1751; format은 `PROVIDER` |

CSR PoP가 Subscriber identity나 GP instance 적격성을 증명하지 않는다. 반대로 credential 또는 attestation만으로 CSR signature 검증을 생략할 수 없다. AL2 attestation signer key와 발급 대상 subject key도 서로 다른 키일 수 있으므로, signed Evidence가 가리키는 subject key를 CSR SPKI에 명시적으로 결속한다.

## 3. 최소 request body

### 3.1 AL1 INITIAL 예시

```json
{
  "requestSchemaVersion": "2026-09-04",
  "certificateProfile": "c2pa-claim-signing-al1",
  "operation": "INITIAL",
  "cplRecordId": "0194513c-bc37-7208-8108-6d3971bcc283",
  "csr": {
    "mediaType": "application/pkcs10",
    "encoding": "base64",
    "value": "base64(DER-PKCS10)"
  }
}
```

### 3.2 AL2 REKEY 예시

```json
{
  "requestSchemaVersion": "2026-09-04",
  "certificateProfile": "c2pa-claim-signing-al2",
  "operation": "REKEY",
  "cplRecordId": "0194513c-bc37-7208-8108-6d3971bcc283",
  "replacesCertificate": {
    "issuerNameSha256": "64-lowercase-hex",
    "serialNumberHex": "positive-even-length-hex-up-to-40-digits",
    "certificateSha256": "64-lowercase-hex"
  },
  "csr": {
    "mediaType": "application/pkcs10",
    "encoding": "base64",
    "value": "base64(DER-PKCS10)"
  },
  "evidenceItems": [
    {
      "profileId": "provider-profile/version",
      "artifactType": "provider-defined-artifact-type",
      "mediaType": "provider-registered-media-type",
      "encoding": "base64",
      "value": "base64(provider-signed-artifact)",
      "certificateChain": [
        "base64(DER-signer-or-intermediate-as-profile-defines)"
      ]
    }
  ]
}
```

예시 중 `requestSchemaVersion=2026-09-04`, 두 `certificateProfile` ID, `INITIAL/REKEY`, CSR의 `application/pkcs10` 및 `base64`는 아래 계약의 고정값이다. 반면 CPL UUID, predecessor hash/serial, CSR·artifact bytes와 provider 식별 문자열은 설명용 placeholder이며 실제 승인값이나 유효한 암호 입력이 아니다. Android의 실제 `profileId/artifactType/mediaType`와 limit은 아직 운영 registry에서 확정해야 한다. Password, bearer token, private key, onboarding 원자료, client가 판정한 Subscriber DN/AL/conformance 결과는 body에 넣지 않는다.

## 4. AL × operation body matrix

`INITIAL`, `REKEY`, `RENEWAL`은 원문의 wire operation 이름이 아니라 이 프로젝트의 body 구분자다. CP는 initial application, re-key와 금지된 same-key renewal의 의미를 제공한다(CP:479-481,573-579).

| AL / operation | CSR | `replacesCertificate` | C2PA semantic enrollment evidence | provider artifact 수 | project `evidenceItems` | disposition |
|---|---:|---:|---|---|---:|---|
| AL1 / `INITIAL` | `1` | `0` | secure credential로 적격 GP instance 인증 + CSR PoP | `NOT-SPECIFIED`; hardware artifact 의무 없음 | `0`, field 금지 | 요구 충족 시 발급 평가 가능 |
| AL1 / `REKEY` | `1`, 새 key | `1` | AL1 instance authentication과 신규 신청과 같은 auth/PoP | `NOT-SPECIFIED` | `0`, field 금지 | current eligibility 전체 재검사 |
| AL1 / `RENEWAL` | `0` | `0` | 적용 없음 | `0` | `0` | same-key renewal 금지; body를 처리하지 않음 |
| AL2 / `INITIAL` | `1` | `0` | AL1 predicate + hardware-backed O.1/O.2/O.3/O.4 | `NOT-SPECIFIED`; 선택 profile에서는 `PROVIDER-PROFILE-DEFINED` | `1..N_p` | 승인 provider profile 필요 |
| AL2 / `REKEY` | `1`, 새 key | `1` | AL2 O.1~O.4를 새 issuance에 다시 평가 | `NOT-SPECIFIED`; 선택 profile에서는 `PROVIDER-PROFILE-DEFINED` | `1..N_p` | 새 CSR과 fresh Evidence 필요 |
| AL2 / `RENEWAL` | `0` | `0` | 적용 없음 | `0` | `0` | same-key renewal 금지; body를 처리하지 않음 |

Provider artifact의 표준 개수와 project JSON array cardinality는 다른 축이다. C2PA 원문은 공통 artifact count를 고정하지 않는다. 이 프로젝트가 AL2 wrapper를 `1..N_p`로 정하며, 양의 정수 `N_p`와 한 item의 의미는 승인 provider profile이 소유한다. Profile이 없으면 AL2 production enrollment를 비활성화한다.

## 5. Enrollment Request Body Matrix

다음 입력 문법은 `OD-BODY-01`의 `PROJECT` 계약이다. JSON 최상위는 object이며, 모든 단계에서 unknown/duplicate member를 거부한다.

- Cardinality `1`은 **키 존재와 지정 타입**을 모두 요구한다. `null`은 부재나 빈 값의 대안이 아니다. `0`, field 금지는 키 자체가 없어야 하며 `null`, `[]`, `{}`로 보내도 거부한다.
- `csr`, REKEY의 `replacesCertificate`, 각 `evidenceItems` 원소는 object다. 각 하위 필수 필드도 존재해야 한다. `RB-01..RB-04`, `csr.mediaType/encoding/value`, `RB-13`의 다섯 값은 non-empty string이며 number/boolean/object로 강제 변환하지 않는다. 배열은 명시한 최소 원소 수를 충족해야 한다.
- `base64`는 표준 `A–Z a–z 0–9 + /` alphabet, 필요한 `=` padding과 zero pad bits를 사용하는 canonical 표현이다. whitespace, PEM header/footer, base64url 및 비정규 padding을 거부한다. decode 후 같은 규칙으로 재인코딩한 문자열이 입력과 같아야 한다. CSR 및 Android 각 인증서의 decoded bytes는 비어 있지 않은 strict DER 한 개여야 한다.
- 문자열/DER byte 크기, JSON depth, item/chain 최대 개수의 운영 상한은 `OD-LIMIT-01`의 `TBD`다. 최소 존재·타입 규칙까지 미정이라는 뜻은 아니며, 상한 승인 전 발급은 계속 비활성화한다.

### 5.1 공통·operation field

| ID | field | applicable body | cardinality / format | validation and server binding | authority · modality · source / decision |
|---|---|---|---|---|---|
| `RB-01` | `requestSchemaVersion` | INITIAL+REKEY / AL1+AL2 | `1`; exact string `2026-09-04` | 현재 계약의 고정 version과 exact match; 임의 날짜 불가 | `PROJECT REQUIRED`; `OD-BODY-01` |
| `RB-02` | `certificateProfile` | INITIAL+REKEY / AL1+AL2 | `1`; exact AL1 또는 AL2 profile ID | profile과 CSR certificate policy/AL extension 조합이 일치; CPL maximum을 넘지 않으며 AL2 실패를 AL1로 변환하지 않음 | 의미는 `C2PA REQUIRED` CP:491-497; AL별 CSR extension은 AL1/AL2 CSR:1051-1179; wrapper는 `PROJECT`; `OD-BODY-01`, `OD-CPL-01`, `OD-DOWNGRADE-01[AL2]` |
| `RB-03` | `operation` | INITIAL+REKEY / AL1+AL2 | `1`; `INITIAL` 또는 `REKEY` | INITIAL은 prior issuance가 없는 server lineage, REKEY는 exact predecessor와 새 key | lifecycle 의미 CP:479-481,573-579; token은 `PROJECT`; `OD-BODY-01`, `OD-LIFECYCLE-01[REKEY]` |
| `RB-04` | `cplRecordId` | INITIAL+REKEY / AL1+AL2 | `1`; CPL schema의 lowercase UUIDv7 | authenticated current CPL의 exact record에 resolve하고 Subscriber/product/DN/max AL을 server state에서 검증 | application meaning `C2PA REQUIRED` CP:461-467,491-497; CPL schema:11-14; wrapper `PROJECT`; `OD-BODY-01`, `OD-CPL-01` |
| `RB-05` | `replacesCertificate` | INITIAL | `0`, field 금지 | INITIAL lineage에 과거 발급이 없어야 함 | `PROJECT`; `OD-BODY-01` |
| `RB-06` | `replacesCertificate` | REKEY | `1`; issuer-name DER hash + positive serial hex + certificate DER hash | server history의 same-lineage exact predecessor 하나에 resolve | re-key `C2PA NON-BCP14-OBLIGATION` CP:579; locator wrapper `PROJECT`; `OD-BODY-01`, `OD-LIFECYCLE-01[REKEY]` |

### 5.2 CSR field

| ID | field | applicable body | cardinality / format | validation and server binding | authority · modality · source / decision |
|---|---|---|---|---|---|
| `RB-07` | `csr` | INITIAL+REKEY / AL1+AL2 | `1` object | 정확히 한 PKCS#10 object; trailing bytes와 ambiguous parse 거부 | `C2PA REQUIRED` CP:471-473; RFC 2986 §4; container `PROJECT`; `OD-BODY-01` |
| `RB-08` | `csr.mediaType` | INITIAL+REKEY / AL1+AL2 | exact `application/pkcs10` | 다른 media type 거부 | `PROJECT REQUIRED`; `OD-BODY-01` |
| `RB-09` | `csr.encoding` | INITIAL+REKEY / AL1+AL2 | exact `base64` | canonical base64만 허용하고 strict DER로 decode | `PROJECT REQUIRED`; `OD-BODY-01`, `OD-LIMIT-01` |
| `RB-10` | `csr.value` | INITIAL+REKEY / AL1+AL2 | `1`; non-empty bounded string | CSR signature/PoP, Subject, SPKI, extensionRequest와 profile schema 검증 | RFC 2986 §3/§4; CP:383-395,473; AL1/AL2 CSR:683-1336; `OD-BODY-01`, `OD-ALG-01`, `OD-LIMIT-01` |

### 5.3 Evidence field

| ID | field | applicable body | cardinality / format | validation and server binding | authority · modality · source / decision |
|---|---|---|---|---|---|
| `RB-11` | `evidenceItems` | AL1 INITIAL+REKEY | `0`, field 금지 | AL1 GP-instance authentication은 credential verdict로 확인; AL2 artifact를 전이하지 않음 | artifact count `C2PA NOT-SPECIFIED` CP:1686-1695; wrapper prohibition `PROJECT`; `OD-BODY-01` |
| `RB-12` | `evidenceItems` | AL2 INITIAL+REKEY | `1` array with `1..N_p` items | 승인 profile이 O.1~O.4 전부를 덮고 item 조합·중복 규칙을 고정 | semantics `C2PA REQUIRED` CP:1712-1751; count `PROVIDER-PROFILE-DEFINED`; wrapper `PROJECT`; `OD-BODY-01`, `OD-EVIDENCE-01` |
| `RB-13` | `profileId`, `artifactType`, `mediaType`, `encoding`, `value` | each AL2 item | 각 exact `1`; provider registry와 일치 | 등록 parser/signature/trust/freshness/binding profile을 선택하고 signed bytes를 검증 | format `PROVIDER`; wrapper `PROJECT REQUIRED`; `OD-BODY-01`, `OD-EVIDENCE-01` |
| `RB-14` | `certificateChain` | each AL2 item | profile별 `0` 또는 `1` array; depth/bytes bounded | requester root를 trust anchor로 채택하지 않고 server trust store로 path 검증; Android는 §5.4와 02 §13.3의 인증서 선택·키 결속 적용 | `PROVIDER/PROJECT`; Google `#verifying/#certificate_status`, AOSP `#attestation-extension` (README §6 pinned sources); `OD-BODY-01`, `OD-LIMIT-01`, `OD-EVIDENCE-01`, `OD-REVOCATION-01` |

각 item의 unknown field, duplicate member, 비정규 encoding과 서로 결속되지 않은 artifact 조합은 거부한다. Signer leaf가 `value`인지 `certificateChain[0]`인지, intermediate 순서와 최대 수는 provider profile이 정확히 하나로 고정한다.

<a id="android-evidence-body"></a>

### 5.4 Android evidence item의 인증서 결속

선택한 Android provider의 field 가이드는 [02 §13](02-CSR-and-Dynamic-Evidence-Requirements.md#android-key-attestation)에 있다. 아래 포장은 기존 wrapper에 적용하는 `PROJECT` 계약이며 Google이나 C2PA가 정한 JSON 형식이 아니다. 운영 `profileId/artifactType/mediaType`, 지원 schema 버전과 byte/count limit은 `OD-EVIDENCE-01/OD-LIMIT-01`에서 확정한다.

| field | Android item에서의 역할 |
|---|---|
| `value` | CSR 대상 공개키를 인증하는 **X.509 attestation certificate 한 개의 DER**를 base64로 담는다. 확장 bytes만 떼어 내거나 client가 만든 decoded JSON을 대신 넣지 않는다. |
| `certificateChain` | 필수 non-empty 배열(`1..N_chain`; 최대 `N_chain`은 `OD-LIMIT-01`). 각 원소는 non-empty canonical base64 string이며 `value`의 직접 issuer부터 root까지의 나머지 DER 인증서를 순서대로 담는다. `null`, 빈 배열, 비문자열 원소와 `value` 중복을 거부한다. 제공된 root도 서버 Google trust registry와 일치해야 한다. |
| `encoding` | 기존 계약의 `base64`; 각 인증서는 strict DER로 파싱한다. |
| `profileId/artifactType/mediaType` | 위 인증서·체인 해석을 선택하는 승인 registry 값이다. 원래 §3.2의 provider placeholder 예시는 실제 Android 등록값을 뜻하지 않는다. |

서버는 `value + certificateChain`으로 검증된 경로를 구성한 뒤 Google 규칙에 따라 root에 가장 가까운 첫 `.17` 확장을 찾는다. **그 확장을 담은 인증서가 `value`와 같고 그 공개키가 CSR 공개키와 같아야 한다.** 다른 인증서에 신뢰 가능한 확장이 있는데 `value`에는 공격자가 만든 확장이 있는 경우를 거부한다. `.30` provisioning 확장 위치, 체인 상태와 정확한 검증 전제는 [02 §13.3](02-CSR-and-Dynamic-Evidence-Requirements.md#android-verification)에 있다.

이 인증서와 체인 전체가 하나의 evidence item을 구성한다. 인증서 수나 O.1~O.4 목표 수가 곧 `evidenceItems` 개수라는 뜻은 아니다. 전체 허용 item 조합과 `N_p`는 운영 profile에 속하며, O.3/O.4 coverage를 확인하지 않고 한 item이 전부 충족한다고 선언하지 않는다. AL1에서는 이 item을 받지 않는다.

## 6. Body 밖에서 반드시 확인할 것

다음은 발급 조건이지만 client body의 자기주장으로 받지 않는다.

- Subscriber/Applicant Representative I/A/V와 ≤398일 재인증 상태
- legally valid/current Subscriber Agreement 또는 Terms acknowledgement
- secure credential의 구체 방식, lifecycle와 GP-instance binding
- authenticated current CPL/Notice source, `productType=generatorProduct`, status, Subscriber, DN, `minVersion`, `maxAssuranceLevel`과 AL2 `attestationMethods`
- CSR algorithm allowlist, same-public-key history와 REKEY predecessor/cutover
- provider trust anchor/status/reference-value registry
- final certificate template, issuer/HSM, serial, validity와 OCSP readiness
- 발급 이후 runtime key-use, O.3~O.6, status refresh와 incident response

Body가 `requestedAssuranceLevel`, Subscriber DN, package 이름, `hardwareProtected`, `covers` 같은 값을 추가로 보내더라도 server authority나 verified Evidence를 대신하지 않는다. 이 문서는 그런 중복 자기주장을 최소 body에 포함하지 않는다.

## 7. Freshness와 binding

C2PA는 모든 provider에 공통인 challenge JSON field, TTL 또는 replay identifier 형식을 정하지 않는다. Challenge를 사용하는 key/platform flow에서는 CA가 만든 unique dynamic challenge와 report nonce의 일치를 검증하고 provider 권고를 따라야 한다(CP:1764-1768). Non-challenge profile은 provider-native signed time/counter/nonce 또는 승인된 signed envelope가 freshness와 replay identity를 제공해야 한다.

이 request body는 challenge를 별도 field로 설계하지 않는다. 필요한 freshness 값은 `evidenceItems[].value`의 provider-signed 범위 안에 있어야 하며, server가 별도로 보유한 expected value·audience·request context와 비교한다. Evidence가 최소 다음을 검증 가능하게 결속하지 못하면 해당 profile을 승인하지 않는다.

- provider profile/version과 signed-byte 범위
- 이 CA/verifier audience
- Subscriber, CPL product와 실제 GP instance
- 요청 profile/AL과 CSR subject public key
- provider freshness 값과 replay identity
- 여러 artifact가 있으면 동일 instance와 동일 requested key

Android는 `.17`의 signed `attestationChallenge`와 CA가 보관한 요청 범위로 결속한다. CA challenge가 먼저 있고 그 값으로 새 키를 생성한 뒤 동일 키의 CSR을 만든다. 아직 생성되지 않은 CSR hash를 선행 challenge의 필수 입력으로 삼지 않는다. Android에 독립된 `audience` 확장 필드가 있다고 가정하지 않으며 자세한 결속과 미정 TTL은 [02 §13.3](02-CSR-and-Dynamic-Evidence-Requirements.md#android-verification)에 따른다.

## 8. Request-body validation order

1. Body byte/depth/count limit을 적용하고 JSON을 strict parse한다.
2. Unknown/duplicate field와 operation/profile별 cardinality를 검사한다.
3. Server-authoritative Subscriber/CPL/profile approval을 조회한다.
4. CSR을 strict DER parse하고 signature/PoP, Subject, SPKI와 extension profile을 검사한다.
5. AL1은 Evidence field 부재를 확인한다.
6. AL2는 provider schema/signature/chain/status/freshness/binding과 O.1~O.4 각각을 검사한다.
7. 발급 직전에 current I/A/V, Agreement, credential/instance, CPL/provider/reference, same-key history, issuer와 final certificate template를 다시 검사한다.

이 순서는 인증·enrollment predicate의 의존 관계일 뿐 endpoint 처리 순서나 transaction state machine이 아니다.

# 02 — C2PA Certificate Enrollment 구현 가이드

> 상태: C2PA Conformance Program v0.2 기준 상세 가이드 초안  
> 성격: API·DB·provider wire format을 확정하는 시스템 설계서가 아니라, C2PA 인증서 발급 요구를 구현 항목별로 해석한 가이드다.  
> 기준 snapshot: `conformance-public` commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`

> **2026-09-02 TSA enrollment 정정:** C2PA는 TSA Leaf API마다 Compound Evidence를 요구하지 않는다. Base TSA profile은 secure credential, CA business practices의 I/A/V, key ownership과 TSA CSR/certificate profile을 검증한다. 6.4~6.6은 명시적으로 채택한 optional CPS attestation profile에만 적용한다.

> **2026-09-04 Claim Signing enrollment 정정:** 공식 명칭은 **C2PA Claim Signing Certificate**다. Claim Signing의 인증 방식, AL1/AL2 독립 판정, `INITIAL`/`REKEY`/거부되는 `RENEWAL`, request-body cardinality, CSR/Dynamic Evidence binding 및 fail-closed 운영 결정은 [Claim Signing enrollment 문서 세트](claim-signing-enrollment-request/README.md)가 소유한다. 이 문서는 그 원문 요구를 설명하는 상위 가이드이며 endpoint·response·state 등 일반 API 계약을 정의하지 않는다.

이 snapshot의 규범 문서와 schema digest는 위 commit의 Git blob exact bytes를 기준으로 한다. Checkout CRLF나 별도 newline normalization 결과는 canonical source가 아니며, release evidence는 `commit+path+blob object ID+SHA-256`으로 재현해야 한다.

이 문서의 locator shorthand `CP:x-y`, `Program:x-y`, `GSPR:x-y`는 각각 위 commit의 `docs/v0.2/C2PA Certificate Policy.md:x-y`, `docs/v0.2/C2PA Conformance Program.md:x-y`, `docs/v0.2/C2PA Generator Product Security Requirements.md:x-y` exact Git blob line을 뜻한다. Claim AL1/AL2 schema locator는 같은 commit의 `docs/v0.2/cert-profiles/claimSigningLeaf.al{1,2}.{csr,cert}.schema.json:x-y`를 뜻한다.

## 1. 이 문서를 읽는 방법

이 문서는 삼성전자 제품에 C2PA Claim Signing 기능과 On-Device TSA 기능을 넣을 때, Certificate Authority와 제품이 **C2PA를 지키기 위해 무엇을 확인해야 하는지** 설명한다.

각 요구사항은 다음 네 수준으로 구분한다.

| 표기 | 의미 |
|---|---|
| `C2PA 필수` | C2PA Certificate Policy 또는 Conformance Program이 요구한다. 구현 방식은 달라도 결과는 충족해야 한다. |
| `C2PA 선택` | C2PA가 허용하지만 강제하지 않는다. 채택 여부는 CA의 CPS나 제품 정책에서 정한다. |
| `구현 지침` | C2PA 요구를 놓치지 않기 위한 구현 방법이다. 특정 API 모양을 강제하지 않는다. |
| `프로젝트 선택` | C2PA가 정하지 않은 삼성전자 시스템 내부 선택이다. 상위 architecture/CPS에서 이미 확정된 선택은 이 문서가 따르고, 미확정 선택은 production 전 결정 대상으로 남긴다. |

`c2pa-design/` 문서는 요구사항의 원문 근거가 아니다. 이 문서의 C2PA 요구는 `conformance-public`의 원문과 공식 schema로 다시 확인했다.

## 2. 먼저 구분해야 하는 두 인증서

Certificate Platform이 발급하는 Leaf는 아래 두 종류다. Claim Signing Leaf는 **외부 Subscriber의 Generator Product instance가 보유한 `K_claim` 공개키**에 발급한다. TSA Leaf는 **conformant CA service를 함께 제공하는 조직이 운영하고 C2PA TSA Trust List에 별도 record로 승인·등록된 TSA의 TSU가 보유한 `K_tsu` 공개키**에 발급한다. 어느 경우에도 Certificate Platform이 콘텐츠나 timestamp를 대신 서명하지 않는다.

| 구분 | Claim Signing Leaf | TSA Time-Stamp Signing Leaf |
|---|---|---|
| 인증되는 키 | Generator Product의 `K_claim` | Time-Stamping Unit의 `K_tsu` |
| 발급 후 사용 | C2PA Claim의 COSE 서명; Claim Signature를 Manifest에 포함 | RFC 3161 TimeStampToken 서명 |
| C2PA Assurance Level | AL1 또는 AL2 | AL 체계를 사용하지 않음 |
| CPL record | 필수 | 인증서에 넣지 않음 |
| C2PA AL extension | 필수 | 넣지 않음 |
| 핵심 EKU | `c2pa-kp-claimSigning` | 정확히 `id-kp-timeStamping` 하나 |
| 발급 CA | Claim Signing Issuing CA | TSA Issuing CA |
| 발급 판단 | Subscriber·CPL·AL·조건부 Dynamic Evidence | TSA 운영자 신원·CA business practices·TSA Leaf profile |

다음 기능은 이 문서가 설명하는 인증서 enrollment 기능이 아니다.

- C2PA Claim/Manifest 생성, C2PA Claim의 COSE 서명 또는 arbitrary payload 서명을 서버가 대신 수행하는 기능
- `MessageImprint`를 받아 TimeStampToken을 생성하는 network TSA 기능
- 외부 Generator Product의 C2PA Manifest 생성 절차
- 외부 TSA의 RFC 3161 request/response 처리 절차
- 삼성전자 내부 enrollment URL, JSON field 또는 DB table 확정. TSA staged activation은 [04의 server transaction·signed artifact contract](04-Security-and-Operations.md#33-tsa-key-activation과-ca-validity의-분리)와 [03의 device-side acceptance](03-On-Device-Runtime.md#8-key-activation-rotation과-revocation)가 소유하며 이 문서는 정의하지 않는다.

## 3. 공통 기술 검증과 Claim Subscriber 심사

### 3.1 Claim Subscriber 신원과 권한

> 분류: `C2PA 필수/Claim`. 이 절의 initial identity validation과 398일 재인증을 TSA Leaf에 그대로 적용하지 않는다. TSA는 6.2절처럼 CA business practices에 문서화한 별도 identification/authentication/verification 절차를 따른다.

#### C2PA가 요구하는 것

- CA는 Applicant 조직의 법적 신원과 주소를 확인해야 한다. DBA를 사용하면 그 이름을 사용할 권리도 확인한다.
- 조직을 대신하는 대표자의 실재와 권한, 신뢰할 수 있는 연락 수단을 확인해야 한다.
- revocation을 요청할 권한이 있는 사람 또는 역할을 등록해야 한다.
- Applicant는 Subscriber가 되기 위한 formal application에 대상 Generator Product와 CPL record, 요청할 AL, 해당하는 경우 CA가 처리할 수 있는 attestation artifact를 만들 수 있다는 증거를 제출해야 한다.
- CA는 application의 완전성·정확성, Applicant identity와 해당하는 경우 attestation artifact 처리 가능성을 심사해야 한다.
- CA는 Subject가 certificate 발급을 승인했고 Applicant Representative가 Subject를 대신해 요청하고 계약 조건에 구속할 권한이 있는지 확인하며, 최종 certificate의 모든 정보를 authoritative source와 대조해야 한다.
- CA와 Subscriber가 affiliated 관계가 아니면 C2PA 요구를 충족하는 legally valid and enforceable Subscriber Agreement의 당사자여야 한다. 같은 entity이거나 affiliated이면 Applicant Representative가 해당 Terms of Use를 확인·수락해야 한다. 이 조건은 certificate 발급 시점에 충족되어야 한다.
- application process가 성공한 뒤에만 새 credential 또는 기존의 안전한 credential을 newly-approved Subscriber와 연결하여 enrollment 요청 인증에 사용한다.
- Subscriber identity는 마지막 initial validation 후 최대 398일 안에 다시 검증해야 한다.

#### 구현 시 확인할 것

- formal application 심사·승인과 credential 결속을 certificate별 enrollment보다 먼저 완료한다. 구체적인 상태명이나 API 모양은 프로젝트가 정하되 이 순서를 뒤집지 않는다.
- 인증 성공과 인증서 발급 권한을 분리한다. 로그인에 성공했다는 이유만으로 모든 제품·AL·TSA service 인증서를 발급하지 않는다.
- Claim 요청은 신청 조직, CPL record와 requested AL을 함께 확인한다.
- application 승인 근거, 신원 확인일, 확인 방법, Subject의 발급 승인, 대표자 권한, credential 식별자와 재검증 만료일을 발급 판단에 사용할 수 있게 기록한다.
- 최종 인증서의 product name을 포함하는 Subject와 승인 profile에 따라 SAN이 존재하는 경우 그 값의 사용권/control을 확인한다. Profile이 금지하는 SAN을 warranty 문구만으로 새로 넣지 않는다.
- 발급 전 predicate에는 affiliation 분류, 적용 Agreement 또는 Terms of Use의 immutable version/digest, 서명·수락 주체와 시각, legal-validity approval을 결속한다. 발급 뒤 설치·사용에 따른 certificate acceptance와 이 발급 전 legal gate를 같은 상태로 축약하지 않는다.

#### 발급을 거부해야 하는 경우

- 조직 또는 대표자의 신원·권한을 확인할 수 없음
- application 정보가 불완전·부정확하거나 Subscriber 승인이 완료되지 않음
- Subject의 발급 승인, product name 사용권/control, Applicant Representative의 요청·계약 권한 또는 최종 certificate 정보의 정확성을 증명할 수 없음
- 적용 가능한 Subscriber Agreement가 법적으로 유효·집행 가능하지 않거나 affiliated Terms of Use acknowledgement를 증명할 수 없음
- 필요한 AL의 attestation artifact를 CA가 처리할 수 있는 형식으로 생성할 능력을 확인할 수 없음
- credential은 유효하지만 대상 Generator Product 또는 requested AL 발급 권한이 없음
- Subscriber 재인증 기한 398일을 넘음
- revocation 요청 권한자를 확인할 수 없음

#### 원문

- `CP:403-477`: Applicant/대표자 I/A/V, conformance proof, Max AL, secure credential, key ownership과 ≤398-day re-authentication
- `CP:489-509`: formal application, application processing과 승인 후 credential 결속
- `CP:531-535`, `CP:1518-1558`: certificate acceptance 및 발급 시점 Subscriber Agreement/Terms of Use warranty

### 3.2 발급 대상 키의 생성 주체와 소유 증명

#### C2PA가 요구하는 것

- Claim Signing key는 Subscriber 또는 Subscriber의 key-management system이 생성해야 한다. CA가 Subscriber key를 대신 생성하면 안 된다.
- Claim Signing private key는 해당 Generator Product instance가 배타적으로 통제하고 다른 device·application instance·party에 export하거나 공유하지 않는다. GSPR이 허용하는 경우는 그 범위만 따른다.
- 이 CP에서는 Subscriber key escrow와 recovery를 지원하지 않는다.
- CA는 발급 대상 공개키에 대응하는 개인키를 신청자가 보유하는지 확인해야 한다.
- 동일 key pair에 새 인증서를 발급하는 same-key renewal은 금지된다.
- re-key에는 새 key를 사용하고 신규 certificate application과 같은 issuance authentication·key ownership/PoP를 적용한다. 저장된 조직·대표자 승인은 currentness, 변경 trigger와 ≤398-day 재인증 규칙으로 다시 확인하되 원문이 initial I/A/V 원자료의 매회 재수집을 명시한다고 확대하지 않는다.

#### 구현 시 확인할 것

> 프로젝트 선택: 이 프로젝트의 enrollment wire contract는 `Overview` 6.2절처럼 DER PKCS#10을 채택한다. C2PA CP가 key ownership 확인 수단을 PKCS#10 하나로 제한하는 것은 아니지만, 별도 승인된 profile 없이 KMS configuration inspection을 암묵적 fallback으로 사용하지 않는다.

1. DER PKCS#10 CSR을 파싱한다.
2. CSR의 `CertificationRequestInfo`에 대한 signature를 CSR SPKI로 검증한다.
3. 공개키 알고리즘과 key size/curve는 C2PA CSR profile로 확인한다. Outer CSR signature algorithm은 cryptographically valid해야 하며 CA가 별도로 문서화한 secure PoP algorithm policy를 충족해야 한다.
4. CSR signature 검증 성공을 Proof of Possession으로 기록한다.
5. 과거 발급 이력과 비교해 같은 공개키가 재사용되지 않았는지 확인한다.

공식 `*.csr.schema.json`은 DER PKCS#10의 wire schema가 아니다. CSR을 parser로 해석한 **decoded JSON 결과가 C2PA profile에 맞는지 검사하는 schema**다. 그러므로 schema validation만 하고 실제 CSR signature 검증을 생략하면 안 된다.

#### 발급을 거부해야 하는 경우

- CSR signature가 유효하지 않음
- CSR SPKI와 signature algorithm이 맞지 않음
- 허용되지 않은 key algorithm, key size 또는 curve
- 과거에 인증서를 발급한 동일 key pair의 재사용
- CSR parser가 구조를 하나로 해석할 수 없거나 trailing data가 있음

#### 원문

- `CP:471-473`: secure credential과 key ownership
- `CP:815-823`: Subscriber key generation; CA key generation 금지
- `CP:563-565`, `CP:615-623`: Subscriber key control과 escrow/recovery
- `CP:573-585`: renewal, re-key와 modification
- RFC 2986 §3~§4

### 3.3 CSR 값과 최종 인증서 값의 관계

CSR의 Subject와 `extensionRequest`는 신청자의 요청값이다. CA는 이를 검증 없이 최종 인증서에 복사하지 않는다. CSR Subject의 입력 적합성, 발급 대상의 식별·인증·권한 확인, 최종 인증서 Subject의 정확성을 별도로 판단한다.

<a id="csr-subject-identification"></a>

#### CSR Subject와 발급 대상 식별

| 판단 대상 | Claim Signing Leaf | TSA Leaf | 원문 근거 |
|---|---|---|---|
| CSR Subject 입력 | ASN.1 Name 구조와 공식 CSR schema의 C/O/CN 포함 조건 | 동일 | AL1/AL2/TSA CSR schemas:692-740; RFC 2986 §4.1 |
| 발급 대상 확인 | 신청 제품·CPL record와 DN, 적합성, 신청자 권한을 확인 | CA business practices에 정한 TSA 신청자·서비스의 식별·인증·검증 | CP:405-455,461-473,491-517 |
| 최종 Subject | 해당 CPL 제품 DN과 일치; ASCII 및 개별 instance 식별 금지 | 해당 TSA 서비스를 식별하는 unique C/O/CN | CP:387-399,1217,1282,1347 |

공식 CSR schema에는 CSR Subject와 등록 DN의 일치를 검사하는 조건이 없다. CP의 제품 식별·CPL 대조 의무도 그 입력을 반드시 `CSR.subject`에서 읽도록 고정하지 않는다. 그렇다고 제출정보의 정확성 검증이나 발급 대상 확인을 생략해도 된다는 뜻은 아니다(CP:501-503,1542-1556,1568-1570).

**CA가 정할 수 있는 식별 방식의 예:** CSR Subject로 대상을 조회하거나, 별도 신청정보의 제품/CPL record 번호·TSA service 식별자 또는 인증된 계정에 연결된 등록정보로 대상을 확인한다. 이는 원문 요구를 충족하기 위한 설계 선택이며, C2PA가 특정 API 필드나 CSR Subject 덮어쓰기를 명시적으로 허용한 절차가 아니다. 선택한 정보는 인증된 신청자 및 이번 요청의 발급 대상 키와 결속해야 한다. Subject 문자열이나 CSR PoP만으로 신청자 신원·발급 권한을 증명하지 않는다.

Claim의 기준 DN은 CPL `product.DN`이며 서명된 Notice도 해당 CPL record를 담는다(CP:461-463). 신청 시 제품 정보와 CPL record 번호를 제출한다(CP:491-493). 기존 CPL/Notice의 적합성·상태 확인 절차를 유지하며, 최종 인증서 DN만 맞춰 넣는 것으로 발급 전 제품 확인을 대신하지 않는다. TSA에는 CPL 제품 DN 대조 의무가 없고 CA가 확인한 TSA 서비스 정보를 사용한다(CP:517).

| CSR Subject 상태 | 처리 원칙 |
|---|---|
| 필수 C/O/CN 누락 또는 구조·형식 부적합 | 해당 CSR profile 검증 실패. 최종 인증서 보충으로 원본 CSR의 적합성을 대신하지 않음 |
| 등록 DN과 문자열·필드 구성이 다름 | 차이 자체를 모든 요청의 자동 거부 또는 자동 수락 조건으로 고정하지 않음. CA가 문서화한 절차에 따라 거부·보완 요청·독립적으로 검증된 식별정보의 사용 여부를 결정 |
| CSR Subject를 대상 식별에 사용하는데 대상을 확인할 수 없음 | 일치 여부나 보완 정보를 확인하여 대상·권한을 확정하기 전까지 발급하지 않음 |
| 별도 정보로 대상이 확인되지만 CSR Subject가 다름 | 제출정보의 정확성과 해당 요청과의 관계를 확인하고 불일치 처리 근거를 남김. 다른 제품·서비스의 권한을 대신 사용하거나 확인되지 않은 값을 임의 보정하지 않음 |

원본 CSR의 서명 대상 bytes를 고쳐 검증하거나 바뀐 값으로 원본이 유효했다고 판단하지 않는다. CSR 수정이 필요하면 신청자가 새로 서명한 CSR을 제출한다. 최종 Subject는 확인된 대상과 해당 인증서 profile에 따라 구성하고, CSR 원본·식별 근거·불일치 처리·최종 Subject의 관계를 발급 기록에서 추적한다.

#### 구현 시 확인할 것

- Claim 발급 대상과 최종 Subject는 authoritative CPL/서명된 Notice의 product DN에 결속한다. CSR Subject의 대조·불일치 처리는 위 식별 절차를 따른다.
- TSA 발급 대상과 최종 Subject는 CA가 확인한 unique TSA service에 결속한다. CSR Subject를 반드시 그 서비스의 사전 등록 DN과 같게 요구하지 않는다.
- 요청된 Basic Constraints, Key Usage, EKU, Certificate Policies, C2PA AL과 CPL extension을 profile과 비교한다.
- Issuer, serial, validity, SKI, AKI, AIA와 CRL Distribution Points는 CA-controlled template에서 만든다.
- serial은 양수이고 20 octets 이하이며, 같은 Issuing CA가 발급한 모든 인증서 사이에서 유일해야 한다. C2PA profile은 high entropy serial을 권장한다.
- 발급 후 인증서를 다시 파싱하고 공식 `*.cert.schema.json`으로 검증한다.

#### 발급을 거부해야 하는 경우

- CSR의 필수 extension, 값 또는 criticality가 선택한 공식 CSR schema와 다름
- Claim 발급 대상의 신원·권한·적합성을 확인할 수 없거나, CSR의 AL·CPL record extension이 확인된 요청 profile/record와 다름. CSR Subject의 단순 불일치는 위 식별 절차로 판단
- TSA 신청자·서비스의 신원·권한 또는 최종 Subject의 정확성을 확인할 수 없음
- TSA CSR에 C2PA AL 또는 CPL record extension이 있음
- TSA CSR의 EKU가 critical인 `id-kp-timeStamping` 정확히 하나가 아님

Claim CSR의 추가 EKU나 unknown critical 요청을 무조건 거부하는 것은 C2PA 공통 규칙이 아니라 CA CPS의 strict-input 정책이다. 거부하지 않더라도 해당 요청값을 최종 인증서에 복사하지 않고 CA-controlled Claim template만 적용한다. 중복 extension처럼 PKCS#10 또는 선택한 공식 schema를 모호하게 만드는 입력은 거부한다.

### 3.4 Server challenge 적용 범위와 검증

Server challenge는 모든 Leaf enrollment에 동일하게 적용되는 C2PA 필드가 아니다. 먼저 요청 종류에 따라 규범의 출처를 구분한다.

| 발급 경로 | 스펙이 명시한 것 | CA 서버가 결정할 것 |
|---|---|---|
| Claim AL1 | C2PA Dynamic Evidence challenge 요구 없음 | AL1에 추가 attestation을 요구할지 여부는 CPS 강화정책 |
| Claim AL2 공통 | O.1~O.4 hardware-backed Evidence가 필수다. 선택한 key/platform attestation 흐름이 challenge를 사용하면 CA가 발급한 값과 Evidence nonce를 일치시키고 provider 권고를 따라야 한다 | challenge 사용 여부는 provider profile에 따름. 사용할 때의 byte 길이, entropy, TTL, encoding, 저장·소진 방식, enrollment context 결속 |
| Claim AL2 Android | Android profile은 `attestationChallenge`와 CA 발급값의 일치를 명시한다. Android API는 최대 128 bytes, AOSP 구현 지침은 최소 16-byte nonce를 권고하고 재사용의 replay 위험을 경고한다 | 허용 길이 하나, 생성 알고리즘, single-use, raw/random 또는 domain-separated transform, replay identity와 사용 여부 보존 |
| TSA Leaf | C2PA CP와 공식 TSA CSR/certificate profile은 enrollment challenge를 정의하지 않음 | Android/custom TSA Attestation을 CPS에서 요구할 경우 challenge 규칙을 provider profile에 정의 |
| RFC 3161 request | 선택적 `TimeStampReq.nonce`는 runtime request/response matching용 | enrollment challenge로 재사용하지 않음 |

#### C2PA와 Android가 고정한 부분

- C2PA AL2는 O.1~O.4 Evidence를 요구하지만 모든 provider에 공통인 challenge field나 protocol을 정하지는 않는다.
- key/platform attestation 흐름이 challenge를 사용하는 경우 CA 또는 위임 RA가 unique·dynamic 값을 발급한다. Evidence가 challenge를 포함하면 CA는 자신이 해당 Generator Product instance에 발급한 예상값과 exact-match하고 provider의 nonce 생성 권고를 따라야 한다.
- Android AL2 profile에서는 이 조건이 `attestationChallenge`의 필수 검증값으로 구체화된다.
- Android `KeyGenParameterSpec.Builder.setAttestationChallenge()` 입력은 최대 128 bytes다.
- Android attestation extension의 `attestationChallenge`는 key 생성 시 전달된 bytes다. 빈 값도 Android API 자체는 허용하지만 C2PA AL2의 unique·dynamic challenge 목적을 충족하는 값으로 사용해서는 안 된다.
- AOSP 구현 지침은 validating service가 제공한 최소 16-byte nonce를 사용하고, challenge 재사용 시 과거 attestation replay에 취약할 수 있다고 경고한다.

#### CA/CPS가 명시적으로 결정할 부분

C2PA는 아래 값을 정하지 않는다. CA는 선택한 provider의 제한을 만족하는 하나의 규칙으로 문서화해야 한다.

| 결정 항목 | 필요한 결정 |
|---|---|
| 생성 | 승인 CSPRNG, 실제 byte 길이와 최소 entropy. 예를 들어 32 random bytes를 쓰는 것은 합리적인 CA 선택이지만 C2PA 고정값은 아님 |
| 표현 | 서버 내부 canonical bytes, 외부 전송 encoding과 decode 오류 처리. 비교는 base64 문자열이 아니라 decode된 bytes로 수행 |
| context binding | Claim/TSA purpose, enrollment 식별자, Subscriber·CPL 또는 TSA service, certificate/provider profile을 challenge record에 결속하는 방법 |
| provider transform | raw challenge를 그대로 넣을지, provider 제한 때문에 domain-separated digest/HMAC 등으로 변환할지와 정확한 algorithm/version |
| 유효시간 | 발급 시각, 만료시간과 clock-skew 정책 |
| replay | single-use 상태, 성공·실패·timeout 때 소진 여부, 동시 제출 처리와 재시도 규칙 |
| 보존 | raw challenge 또는 보호된 원문을 언제까지 보관할지, digest만 남기는 시점 |

#### CA 서버가 유지할 논리 정보

API나 DB field 이름은 구현자가 정하되 다음 의미는 잃지 않아야 한다.

```text
challenge identifier
+ exact challenge bytes 또는 동일 예상값을 재계산할 보호된 입력
+ creation/expiration time
+ Claim-AL2 또는 custom-TSA-attestation purpose
+ Subscriber/CPL/provider profile 또는 TSA service/provider profile
+ transform algorithm/version
+ unused/consumed/expired 상태
```

검증기는 request에 실린 challenge 값을 신뢰하지 않고 서버 record에서 예상값을 읽거나 재계산한다. ASN.1 `OCTET STRING`에서 추출한 Android `attestationChallenge`를 exact byte comparison하며, 다른 문자열 정규화나 암묵적 hashing을 적용하지 않는다. transform을 사용한다면 등록된 provider profile의 동일 version에서만 재계산한다.

#### Android key 생성·CSR 순서

다음은 CP의 Android predicate와 Android API에 부합하는 권장 CA 구현 순서다. C2PA가 정한 API/wire protocol 순서는 아니며, 다른 절차를 쓰더라도 fresh challenge, attested SPKI와 CSR SPKI의 일치 및 CSR PoP를 보장해야 한다.

```text
CA challenge 수신
→ challenge를 setAttestationChallenge(bytes)에 전달하여 새 K_claim 생성
→ AndroidKeyStore certificate chain 수집
→ 같은 private key로 PKCS#10 CSR 서명
→ CA가 attested certificate SPKI == CSR SPKI와 challenge를 함께 검증
```

위 순서는 C2PA가 Android profile을 명시한 Claim AL2 경로다. `K_tsu`에 Android Key Attestation을 적용하는 경우는 6.5절의 CA/CPS custom profile을 따른다. same-key renewal이 금지되므로 Claim fresh re-key에서는 새 challenge와 새 key를 사용한다. 이미 만들어진 다른 key의 attestation chain과 현재 CSR을 조합하면 SPKI 결속에서 거부한다.

### 3.5 발급 완료 전 공통 gate

CA signing key를 사용하기 전에 최소한 다음 결과가 모두 성공해야 한다.

```text
신청자 신원·credential·발급 권한
AND CSR 구조·profile·Proof of Possession
AND 요청 Leaf 종류에 맞는 eligibility
AND 필요한 경우 Dynamic Evidence 검증
AND 발급 직전 authoritative 상태 재확인
AND 최종 certificate template 검증
```

검증 결과가 `UNKNOWN`, `NOT_PROVEN`, timeout 또는 stale이면 성공으로 바꾸지 않는다.

## 4. Claim Signing Leaf AL1 발급 가이드

> 분류: `C2PA 필수/Claim AL1`.

### 4.1 대상 자격 확인

#### C2PA가 요구하는 것

- 대상은 CPL의 `generatorProduct`여야 한다.
- 공개 CPL을 사용하는 경우 record의 현재 `status`가 `conformant`여야 한다.
- CP와 Program의 Notice 절은 공개 CPL 게시 전 signed Notice로 production certificate를 받을 수 있다고 표현하지만(`CP:457-463`; `Program:472-478`), Program의 machine-readable-list 절은 CA가 public CPL의 `status=conformant` record가 있는 instance에만 발급해야 한다고 쓴다(`Program:488-498`). 이는 해결되지 않은 원문 충돌이지 Notice-only 발급 허가를 이 architecture가 확정했다는 뜻이 아니다.
- 현재 interim production rule은 authenticated public CPL의 current `status=conformant`를 authoritative eligibility로 요구한다. Signed Notice를 받은 경우에는 onboarding proof로 검증·보관하되 current non-conformant·removed 또는 pre-public 상태를 우회하는 근거로 사용하지 않는다. CP가 public posting도 conformance proof로 허용하므로 signed Notice 자체를 모든 Applicant에게 추가 의무화하지 않는다. 공개 여부나 현재 상태를 확인할 수 없으면 fail-closed한다.
- requested AL은 CPL record의 `maxAssuranceLevel`을 넘을 수 없다.
- CA가 승인하여 수용한 Subscriber와 Generator Product에는 `maxAssuranceLevel` 이하의 모든 AL 요청 경로를 제공해야 한다. 각 유효한 요청에는 해당 AL의 gate를 적용하고 모든 mandatory gate가 성공하면 그 AL 인증서 발급으로 진행한다. 이는 모든 AL 인증서를 자동으로 동시에 발급한다는 뜻이 아니다. `CP:465-467`의 `SHALL issue`와 `CP:519-529`의 Evidence 검증 후 `MAY issue` 사이 규범어 긴장은 [Claim gap register](claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md#7-gap-and-clarification-register)에서 추적한다.
- Signed Notice를 onboarding에 사용했다면 그 안의 Subject DN/CPL record UUID와 current public CPL이 일치함을 확인하고, 현재 interim production rule에서는 current CPL 값으로 최종 확정한다.

#### 구현 시 확인할 CPL 값

| CPL 값 | 확인 목적 |
|---|---|
| `recordId` | 인증서의 C2PA CPL Record ID extension |
| `applicant` | Subscriber 조직과 record 소유자 일치 |
| `product.productType` | `generatorProduct` 여부 |
| `product.DN` | 인증서 Subject C/O/CN과 조건부 OU |
| `product.minVersion` | record에 존재하는 경우 요청 제품 version의 최소 eligibility 기준 |
| `product.assurance.maxAssuranceLevel` | requested AL의 상한과 그 이하 모든 Claim AL 요청 가능 범위 |
| `product.assurance.attestationMethods` | AL2 요청 시 provider method 일치 여부 |
| `specVersion`, `conformanceProgramVersion` | 어떤 적합성 기준으로 승인됐는지 기록 |
| `status`와 record dates | 현재 발급 가능 상태와 snapshot 시점 |

제품군 이름이 비슷하더라도 스마트폰, TV, 가전 또는 서로 다른 Generator Product를 하나의 CPL record로 임의 합치지 않는다. 실제 발급 대상이 해당 record의 제품인지 확인한다.

### 4.2 AL1 Evidence 요구

AL1은 AL2와 같은 O.1~O.4 hardware Dynamic Evidence를 C2PA가 일괄 요구하지 않는다. AL1에서 C2PA가 요구하는 핵심은 안전한 enrollment 인증으로 적격 Generator Product instance에 대한 신청인지 확인하는 것이다.

**C2PA 필수:** 자동 certificate enrollment를 사용하는 경우 CA는 enrollment를 시도하는 entity가 승인된 Subscriber의 해당 Generator Product instance인지 CA가 요구한 secure authentication method로 검증한다.

**구현 지침:** Subscriber application·credential·발급 권한 판정과 GP instance authentication 판정을 별도 predicate로 기록한다. 같은 secure credential 또는 evidence가 두 판정에 사용될 수 있으므로 C2PA가 별도 factor를 요구한다고 해석하지 않는다. 다만 일반 Subscriber 로그인 성공만으로 GP instance 인증을 대체하지 않으며, mix-up을 막기 위해 인증 결과를 현재 enrollment request와 검증된 Subscriber·CPL·product authorization context에 연결한다.

**C2PA 필수/외부 GP:** 자동 enrollment를 사용하는 **Edge** Implementation Class의 GP TOE binary에는 authentication secret을 포함하면 안 된다. Applicant는 GP TOE의 automated enrollment process, authentication secret 관리 설계와 enrollment/renewal trigger를 반드시 GPSA에 기록한다. Enrollment authentication method의 상세는 application에 포함하며, application 시점에 그 상세를 제공할 수 없었던 경우에만 conformance 승인 후 90일 안에 Conformance Program에 별도 update한다. 이는 GP TOE와 Applicant의 적합성 의무이며 CA가 매 enrollment마다 binary나 GPSA를 다시 분석해야 한다는 뜻은 아니다.

CA가 CPS로 AL1에 추가 attestation을 요구할 수는 있지만, 이는 `프로젝트 선택` 또는 CA 강화정책이며 C2PA AL1 공통 요구라고 표기하면 안 된다.

> 원문: `CP:1684-1695`; `GSPR:330-358`.

### 4.3 AL1 발급 판단

다음 조건을 모두 만족할 때 AL1 Leaf 발급으로 진행한다.

```text
Subscriber application approval/identity/credential/authorization == PASS
Generator Product instance authentication == PASS
Generator Product conformance proof == PASS
(현재 interim production rule: authenticated public CPL의 status=conformant; signed Notice는 onboarding proof로만 보관)
requested AL == AL1
requested AL <= CPL maxAssuranceLevel
CSR PoP and AL1 CSR profile == PASS
current conformance source state == PASS
```

## 5. Claim Signing Leaf AL2 발급 가이드

> 분류: `C2PA 필수/Claim AL2`.

AL2는 AL1 자격 조건에 더해 hardware Root of Trust가 뒷받침하는 Dynamic Evidence로 O.1~O.4를 모두 입증해야 한다.

### 5.1 AL2 공통 Evidence 처리

#### C2PA가 요구하는 것

- O.1~O.4를 hardware-backed Evidence로 입증한다.
- 선택한 key/platform attestation 흐름이 challenge를 사용하면 CA 또는 위임 RA가 unique·dynamic challenge를 발급한다.
- Evidence가 challenge를 포함하면 provider 권고에 따라 생성하고, CA가 해당 Generator Product instance에 발급한 값과 일치하는지 확인한다. Android AL2에서는 `attestationChallenge` 검증이 명시된 필수 predicate다.
- Applicant가 선택한 attestation method가 CPL record와 CA가 지원하는 method에 맞아야 한다.
- 필요한 Evidence가 없거나 해당 검증이 실패하면 그 AL의 인증서를 발급하지 않는다.

#### 구현 시 확인할 것

- provider가 서명한 원본 bytes와 서명 검증 chain
- 서버가 보유한 trust anchor까지의 경로와 provider status/revocation
- provider flow가 challenge를 사용하면 현재 challenge와 Evidence nonce의 일치
- Evidence가 증명한 subject key와 CSR SPKI의 일치
- Evidence signer key와 인증서 발급 대상 subject key의 구분
- provider profile/version과 실제 signed Evidence format의 일치
- Evidence가 여러 개면 같은 product instance와 key에 대한 것인지 검증 가능한 결속
- 판정에 사용한 Reference Value의 출처, version, 적용 시각

C2PA는 모든 provider가 공통으로 쓰는 JSON, COSE, EAT 또는 X.509 Evidence wire format을 정하지 않는다. 정확한 signed bytes, claim 위치, trust root와 Reference Value mapping은 provider별 공식 자료와 CA 검증 절차가 정해야 한다.

### 5.2 O.1 — Generator Product instance 식별

> 원문: `CP:1712-1714`; `GSPR:360-376`.

#### C2PA가 요구하는 것

hardware-backed artifact를 사용해 실제 제품 instance의 binary identity를 확인한다. 예시는 package name, binary hash, code-signing certificate 또는 이에 상응하는 identity다.

#### 구현 시 확인할 것

- Evidence의 제품/app identity가 CPL record의 Generator Product와 연결되는지
- CPL record에 `minVersion`이 존재하면 package/binary/firmware version을 입증하고, CA가 사전 정의한 비교 규칙으로 최소값 이상인지 확인
- code signer 또는 제품 인증서가 승인된 값인지
- 일반 앱이 자기 선언한 제품명이 아니라 hardware-backed Evidence에서 얻은 값인지

#### 실패 조건

- 제품 identity가 누락되거나 승인값과 다름
- 서명되지 않은 request field만으로 제품을 식별함
- `minVersion`이 존재하는데 version을 입증할 수 없거나, 비교 규칙이 없거나, 정의된 비교 결과가 최소값보다 낮음

### 5.3 O.2 — Claim Signing key 보호

> 원문: `CP:1716-1718`; `GSPR:422-472`.

#### C2PA가 요구하는 것

- `K_claim`이 hardware-backed platform keystore service 또는 Key Management Service에서 생성·보관되고, 그 사실이 hardware-backed artifact로 입증되는지 확인한다.
- 해당 key를 검증된 Generator Product instance가 실제로 소유함을 확인한다.

#### 구현 시 확인할 것

- key origin이 `generated`인지
- private key가 export되지 않는지
- key purpose가 signing인지
- algorithm, size/curve와 digest/padding authorization이 Claim profile에 맞는지
- Evidence subject key, CSR SPKI와 최종 Leaf SPKI가 동일한지
- key와 O.1의 제품 instance가 같은 신뢰 경로로 결속되는지

CSR PoP는 private key 보유를 보여 주지만 hardware 생성·보관 사실까지 증명하지는 않는다. CSR signature 검증과 attestation key-property 검증을 둘 다 수행한다.

### 5.4 O.3 — Claim Generator와 실행 환경

> 원문: `CP:1720-1734`; `GSPR:474-556`.

#### C2PA가 요구하는 것

- Claim Generator가 실행되는 platform의 authenticated/secure boot 상태를 확인한다.
- platform의 HIGH/CRITICAL 취약점이 탐지된 뒤 90일 안에 patch 또는 mitigation되었는지 판단한다.
- Claim Generator software 자체는 다음 중 Applicant가 선택해 등록한 방식으로 확인한다.
  - patch 적용 후 90일 이내인지 확인하는 방식
  - CA에 등록된 승인 revision인지 확인하는 방식

#### 구현 시 확인할 것

- boot가 locked/verified 상태인지
- OS, vendor, boot patch level과 신뢰 가능한 vulnerability/reference feed
- Claim Generator package/binary/signer/version/measurement
- platform patch와 Claim Generator revision을 서로 다른 항목으로 평가했는지

#### 실패 조건

- secure boot가 꺼져 있거나 boot state를 확인할 수 없음
- 오래된 HIGH/CRITICAL 취약점이 수정·완화되지 않음
- platform은 최신이지만 Claim Generator가 승인되지 않음
- 일반 software가 전달한 patch/version 값을 그대로 신뢰함

### 5.5 O.4 — Asset/Assertion 처리 경로

> 원문: `CP:1737-1751`; `GSPR:558-636`.

#### C2PA가 요구하는 것

GP TOE 안에서 Digital Content 및/또는 Assertion을 처리하거나 수정하는 관련 software 전체에 대해 다음을 확인한다.

- software identity가 승인값과 일치
- 각 software가 실행되는 platform의 authenticated boot
- 각 platform의 HIGH/CRITICAL 취약점 patch/mitigation
- 각 처리 component의 90일 patch recency 또는 승인 revision

#### 구현 시 확인할 것

먼저 제품별 GP TOE 경계를 정하고 Claim Generator 외에 camera/media pipeline, encoder, assertion producer 등 실제 Asset/Assertion 처리 component 목록을 만든다. 각 component가 어느 Evidence와 Reference Value로 입증되는지 추적한다.

Android Key Attestation이나 device-health verdict 하나가 제품의 전체 O.4 처리 경로를 자동으로 증명한다고 가정하면 안 된다. Evidence가 다루지 못하는 component가 있으면 보완 Evidence가 필요하다.

#### 실패 조건

- 처리 component inventory가 없음
- component 하나라도 identity, boot, platform patch 또는 software revision을 입증하지 못함
- 여러 Evidence가 서로 같은 제품 instance에서 나온 것인지 결속할 수 없음

### 5.6 O.5와 O.6

C2PA Certificate Policy v0.2의 AL2 Dynamic Evidence 표는 O.5(구성요소 간 traffic 보호)와 O.6(hosting environment 보호)에 대해 추가 stipulation을 두지 않는다. 이는 해당 보안 문제가 존재하지 않는다는 뜻이 아니라, 이 AL2 certificate enrollment 검증표에 별도 CA predicate가 없다는 뜻이다. GSPR이나 제품 보안 설계에서 요구되는 보호를 생략하지 않는다.

### 5.7 Android Key Attestation을 사용하는 경우

C2PA Certificate Policy v0.2는 `K_claim`을 Android Key Attestation으로 입증하는 AL2 경로에 아래 field predicate를 명시한다. 이 표는 Android Claim AL2용이다. TSA Leaf에 그대로 적용되는 C2PA profile은 아니다.

#### 5.7.1 요청을 신뢰하기 전에 확인할 chain과 key 결속

CA는 Android attestation을 단말 밖의 신뢰 환경에서 다음 순서로 검증한다.

1. CPL record가 `Android_KeyAttestation`을 허용하고 requested AL2가 `maxAssuranceLevel` 이내인지 확인한다.
2. request가 함께 보낸 root를 신뢰하지 않고, CA가 사전에 승인한 provider profile의 trust-anchor snapshot으로 전체 X.509 chain과 certificate signature를 검증한다.
3. certificate validity를 검증하고 provider가 공개한 certificate status/revocation 정보를 chain의 각 certificate에 적용한다.
4. 최신 Android 검증 지침에 따라 trust anchor 쪽에서 leaf 방향으로 provisioning-information extension OID `1.3.6.1.4.1.11129.2.1.30`의 첫 occurrence를 찾는다. 이 extension이 있으면 Key Attestation extension OID `1.3.6.1.4.1.11129.2.1.17`이 root→leaf 순서의 바로 다음 certificate에 있어야 하며, 인접 조건이 맞지 않으면 거부한다.
5. root 쪽에서 찾은 첫 Key Attestation extension occurrence만 선택한다. extension이 항상 배열의 leaf 위치에 있다고 가정하지 않는다.
6. 선택된 certificate의 SPKI가 CSR SPKI와 같은지 확인하고 CSR signature PoP도 별도로 검증한다.
7. `attestationVersion`과 `keymasterVersion`/`keyMintVersion`에 맞는 공식 DER schema로 extension을 파싱한다. version pair가 일치하지 않거나 지원하지 않는 version이면 추측해 파싱하지 않는다.
8. 아래 predicate, O.3 보완 Evidence와 O.4 component coverage를 모두 평가한다.

발급 전후의 key 결속은 다음과 같아야 한다.

```text
Android attestation extension을 가진 certificate의 SPKI
== verified CSR.subjectPublicKeyInfo
== issued Claim Leaf.subjectPublicKeyInfo
```

Google Play Services를 사용하는 Android 제품은 Google Hardware Attestation root set과 Google certificate status source를 provider profile로 사용한다. RKP attestation certificate의 `notBefore`/`notAfter`는 반드시 적용한다. 2021년 이전 factory attestation key의 expired-certificate 예외는 Google 공식 지침이 정한 root subject `SERIALNUMBER=f92009e853b6b045`로 이어지는 chain과 status 조건에만 적용하고, RKP나 OEM provider certificate에 일반화하지 않는다. Google Play Services가 없는 Android 제품은 OEM의 공식 root·chain·status·schema 문서와 CA의 별도 승인이 있어야 한다.

#### 5.7.2 Claim AL2 field predicate

Android `AuthorizationList`의 field가 ASN.1 문법상 `OPTIONAL`이어도, 아래 C2PA AL2 판정에 필요한 field가 없으면 증명 실패로 처리한다.

| signed 위치/field | C2PA Claim AL2에서 확인할 값 | 실패 또는 구현 주의 |
|---|---|---|
| `attestationSecurityLevel` | `TrustedEnvironment(1)` 또는 `StrongBox(2)` | `Software(0)`, unknown 또는 누락 거부 |
| `keymasterSecurityLevel` 또는 `keyMintSecurityLevel` | 해당 version schema의 `TrustedEnvironment(1)` 또는 `StrongBox(2)` | `Software(0)`, unknown 또는 누락 거부 |
| `attestationChallenge` | 서버 record의 현재 challenge bytes와 exact-match | empty, mismatch, expired, replay 또는 이미 소진된 값 거부 |
| `softwareEnforced.attestationApplicationId[709]` | 내부 DER `AttestationApplicationId`를 파싱 | malformed 또는 누락 거부 |
| `package_infos[].package_name` | CA/CPL product profile에 등록한 Android package name | request의 평문 package name과만 비교하지 않음 |
| `package_infos[].version` | 등록된 허용 version이며, CPL `minVersion`이 있으면 그 조건도 충족 | Android version 값과 CPL version 표현의 mapping은 CA가 사전 정의 |
| `signature_digests[]` | app signing certificate chain별 leaf certificate의 등록된 SHA-256 digest | `SET OF OCTET_STRING`의 digest 길이·값 불일치 거부 |
| `hardwareEnforced.purpose[1]` | `SIGN(2)` 포함 | 다른 purpose도 허용할지는 CA 강화정책. `SIGN` 누락은 거부 |
| `hardwareEnforced.algorithm[2]` | `RSA(1)` 또는 `EC(3)` | Android C2PA 표는 Claim 일반 profile의 Ed25519 경로를 다루지 않음 |
| `hardwareEnforced.keySize[3]` | RSA `2048/3072/4096`, EC `256/384/521` | algorithm과 size 불일치 또는 허용 외 값 거부 |
| `hardwareEnforced.digest[5]` | SHA2-256(4), SHA2-384(5), SHA2-512(6) 중 허용값 | 누락 또는 허용 외 digest 거부 |
| `hardwareEnforced.padding[6]` | RSA이면 `RSA_PSS(3)` | RSA인데 PSS authorization이 없으면 거부 |
| `hardwareEnforced.ecCurve[10]` | EC이면 P-256(1), P-384(2), P-521(3) | key size와 curve가 맞지 않거나 EC인데 누락되면 거부 |
| `hardwareEnforced.origin[702]` | `GENERATED(0)` | imported, derived, unknown 또는 누락 거부 |
| `hardwareEnforced.rootOfTrust[704].deviceLocked` | `TRUE` | false 또는 누락 거부 |
| `hardwareEnforced.rootOfTrust[704].verifiedBootState` | `Verified(0)` | SelfSigned, Unverified, Failed 또는 누락 거부 |
| `hardwareEnforced.osPatchLevel[706]` | CSR 제출 월과 그 직전 3개월 중 하나이며 미래가 아님 | `YYYYMM` calendar parsing 후 비교 |
| `hardwareEnforced.attestationIdBrand[710]` | 특정 brand로 제한된 제품이면 등록값 | 제품 제한이 있을 때 누락·불일치 거부 |
| `hardwareEnforced.attestationIdManufacturer[716]` | 특정 manufacturer로 제한된 제품이면 등록값 | 제품 제한이 있을 때 누락·불일치 거부 |
| `hardwareEnforced.attestationIdModel[717]` | 특정 model로 제한된 제품이면 등록값 | 제품 제한이 있을 때 누락·불일치 거부 |
| `hardwareEnforced.vendorPatchLevel[718]` | CSR 제출일 기준 90일 이내이며 미래가 아님 | `YYYYMMDD` 유효 날짜로 파싱 |
| `hardwareEnforced.bootPatchLevel[719]` | CSR 제출일 기준 90일 이내이며 미래가 아님 | CP v0.2 표의 Tag 718 표기는 Android 공식 schema와 불일치한다. 의미 조건은 CP를 따르고 parser tag는 공식 Android Tag 719를 사용 |

`uniqueId`, `verifiedBootKey`, `verifiedBootHash`에는 C2PA가 공통 기대값을 정하지 않는다. 특히 `uniqueId`를 개별 device identity나 key-binding 근거로 사용하거나 불필요하게 보존하지 않는다. 특정 OEM firmware/image까지 제한하려면 `verifiedBootKey`·`verifiedBootHash`를 어떤 승인 Reference Value와 비교할지는 CA/provider profile이 별도로 정한다.

`attestationVersion`과 `keymasterVersion`/`keyMintVersion`은 공식 schema의 대응쌍 `(1,2)`, `(2,3)`, `(3,4)`, `(4,41)`, `(100,100)`, `(200,200)`, `(300,300)`, `(400,400)`, `(500,500)` 중 CA가 지원하는 값이어야 한다. legacy와 최신 security-level field 이름도 선택된 version schema를 따른다.

`softwareEnforced.attestationApplicationId`는 Android platform이 수집한 값이지만, `deviceLocked=true`와 `verifiedBootState=Verified`를 포함한 전체 신뢰 조건과 함께 평가한다. shared UID에서는 여러 package가 들어갈 수 있으므로, 예상하지 않은 동거 package를 허용할지, 등록 package의 포함만 볼지, exact set equality를 요구할지는 CA가 profile에 명시해야 한다. signing-key rotation 또는 여러 signing certificate chain을 지원할 때도 expected digest set의 포함만 요구할지 exact equality를 요구할지와 예상하지 않은 digest의 거부 여부를 정한다.

#### 5.7.3 Android Evidence가 O.1~O.4 중 증명하는 범위

| AL2 목표 | Android 표가 직접 제공하는 근거 | 별도로 필요한 판정 |
|---|---|---|
| O.1 Product instance | challenge, package/version, signing certificate digest, 조건부 brand/manufacturer/model | CPL version mapping, shared UID 정책, product Reference Value 일치 |
| O.2 `K_claim` 보호 | attested SPKI, TEE/StrongBox level, hardware authorization, `origin=GENERATED`, CSR PoP | key가 해당 Generator Product instance의 Claim 서명 용도로 배타 통제되는 운영 보장 |
| O.3 Claim Generator | verified boot와 platform patch, package/version/signer 일부 | Claim Generator 자체의 승인 revision/measurement와 vulnerability 판정 |
| O.4 처리 경로 | device boot/patch 상태 일부 | camera/media/assertion pipeline 전체 component inventory와 각 identity/revision/Evidence coverage |

따라서 Android 표의 값만 맞는다는 이유로 AL2를 발급하지 않는다.

```text
Android Key Attestation predicates
AND Claim Generator revision/reference-value evidence
AND O.4 component inventory coverage
AND CPL/product mapping
== AL2 PASS
```

### 5.8 AL2 실패 시 lower AL 평가

C2PA는 AL2 Evidence 검증에 실패했을 때 다음 하위 AL로 평가하는 것을 허용한다(`MAY`). 그러나 이 프로젝트의 승인된 `OD-DOWNGRADE-01`은 silent/automatic downgrade를 금지한다.

AL1 발급을 원하면 실패한 AL2 request를 AL1로 변환하지 않고 사용자가 동의한 별도 AL1 request에 AL1 gate를 처음부터 적용한다. 새 request의 결과는 다음을 모두 AL1 값으로 확정한다.

- certificate profile
- validity 상한
- C2PA Assurance Level extension 값
- 발급 판단과 감사 기록

AL2 OID를 유지한 채 Evidence 실패를 무시하거나 최종 certificate만 AL1로 바꾸면 안 된다. 현재 승인 결정을 바꾸려면 명시적 consent/threat/profile behavior test와 CPS update를 거친 새 policy version이 필요하다.

## 6. TSA Time-Stamp Signing Leaf 발급 가이드

> 분류: 6.1~6.3은 `C2PA 필수/TSA` 운영 범위이고, 6.4~6.6의 enrollment Attestation 적용 방식은 `프로젝트 선택/CA CPS 구현`이다. 단, 아래 General TSA UTC(k) traceability는 CP의 lowercase `shall` 운영 의무이고 On-Device 24시간 online source traceability는 대문자 `SHALL`이므로 요구 추적표에서는 둘을 구분한다.

### 6.1 Claim AL 모델과 분리

TSA Leaf에는 Claim Signing의 AL1/AL2 및 CPL record extension을 적용하지 않는다. CPL은 Generator Product 목록이며 TSA operator/service/TSU registry가 아니다.

TSA-only로 C2PA Conformance를 신청하는 모델도 허용되지 않는다. conformant CA 운영자가 TSA를 함께 운영하고, TSA trust chain을 별도 C2PA TSA Trust List에 등록하는 구조를 따라야 한다.

### 6.2 TSA 신청자와 service 확인

#### C2PA가 요구하는 것

- CA는 TSA Leaf 발급을 위한 identification, authentication, verification 절차를 공개 business practices에 문서화해야 한다.
- TSA key는 timestamp 전용이어야 한다.
- TSA service를 식별하는 unique Subject name을 사용해야 한다.
- TSA practices에는 지원 hash algorithm, time-stamp signature의 예상 수명, Subscriber/Relying Party 의무, 사용 제한, 검증 방법, 의도한 time accuracy와 TSA event logging·보존기간을 공개해야 한다.

#### 구현 시 확인할 것

- 신청자가 승인된 TSA 운영자인지
- CSR Subject, 별도 신청정보 또는 인증된 등록정보 중 CA 절차가 사용하는 정보로 TSA 서비스를 식별하고 요청자의 권한을 확인했는지
- 최종 Subject가 그 확인된 TSA 서비스를 식별하는지. CSR Subject의 입력 검사와 불일치 처리는 [3.3절](#csr-subject-identification)을 따름
- CSR key가 TSA Leaf profile에 맞는지
- key가 timestamp 외 용도로 사용되지 않도록 제품과 운영 절차가 보장하는지

`tsaServiceId`, `tsuInstanceId`, quota 또는 device slot API는 유용할 수 있지만 C2PA가 정한 필드가 아니다. 필요하면 삼성전자 내부 설계나 CA CPS에서 별도로 정의한다.

### 6.3 General TSA와 On-Device TSA 요구

모든 C2PA TSA가 지킬 runtime 요구는 다음과 같다.

| General TSA 항목 | C2PA 요구 |
|---|---|
| 시간 기준 | UTC(k)에 traceable한 time value 사용. General TSA 문언은 lowercase `shall` 운영 의무이고, On-Device 24시간 online synchronization source의 같은 속성은 대문자 `SHALL` |
| 정확도 | time-stamp에 intended accuracy를 정의하고 그 범위로 동기화. 선언 정확도는 1초 이하 권고 |
| leap second | 적절한 기관의 통지에 맞춰 clock synchronization 유지 |
| drift | 선언한 accuracy를 벗어나는 drift를 탐지하면 timestamp 발급 중단 |
| key purpose | timestamp 전용 key 사용 |
| active key | 한 TSU에서 active signing key는 최대 하나 |
| 요청 hash | SHA-2 256/384/512를 사용한 요청만 허용 |

On-Device TSA에는 다음 요구가 추가된다.

| On-Device 추가 항목 | C2PA 요구 |
|---|---|
| online sync | 최소 24시간마다 UTC(k)에 traceable한 online time source와 synchronization 시도 |
| 실행 위치 | TSA application이 TEE에서 실행 |
| key 생성·보관 | TSU signing key를 TEE에서 생성하고 TEE 안에 보관 |

이 항목들은 인증서 extension만으로 지속 보장되지 않는다. 제품의 TSA TA/TEE 구현과 운영 acceptance에서 별도로 검증해야 한다.

### 6.4 TSA enrollment Attestation의 경계 — 프로젝트 선택/CA CPS 구현

C2PA는 On-Device TSA의 TEE 실행과 TEE key 보관을 요구하지만, 이를 인증서 발급 시 제출할 **Custom Compound Attestation wire format**은 정하지 않는다.

Base TSA enrollment는 per-request attestation을 요구하지 않는다. TEE 실행·key confinement·timestamp-only·single-active-key는 TEE enforcement, 설계/코드 검토, conformance/negative test, TSA practices/CPS, 배포 승인과 운영 감사로 보증할 수 있다.

CA가 위험 모델에 따라 발급 시 attestation을 추가로 요구한다면 이는 별도로 명명·승인한 optional CA business practices/CPS 확장이다. 현재 architecture의 optional TSA attestation profile은 challenge flow만 정의하며 non-challenge TSA profile은 없다. Non-challenge 방식을 추가하려면 별도 versioned CPS/provider profile과 독립 검증이 필요하다. 이 경우에만 provider profile은 최소 다음 사실을 검증할 수 있어야 한다.

아래 claim 이름과 조합은 C2PA가 정한 TSA enrollment field가 아니라 custom provider profile의 최소 보안 설계다.

- signed profile ID/version과 `purpose=c2pa-on-device-tsa-enrollment`
- audience 또는 CA/service-specific domain separation
- Evidence freshness와 현재 enrollment challenge
- transaction/challenge, TSA service·TSU와 `K_tsu`의 동일 signature-scope 결속
- Evidence signer trust path와 status
- attested `K_tsu`와 CSR SPKI의 일치
- `K_tsu`의 TEE 내부 생성·보관·non-exportability
- timestamp 전용 key authorization
- TSA TA identity/version/measurement
- TEE implementation, secure boot, lifecycle/debug/rollback 상태
- 해당 TSA service/TSU와 key의 결속

위 항목의 field name, ASN.1 OID, COSE/EAT label 또는 X.509 extension을 C2PA 표준값이라고 부르면 안 된다. 실제 provider가 서명하는 canonical schema와 test vector가 있어야 구현할 수 있다.

### 6.5 Android Key Attestation을 `K_tsu`에 적용하는 경우

C2PA는 Android Key Attestation의 상세 field 표를 Claim AL2 `K_claim` 발급에 제시한다. TSA Leaf enrollment에는 Android profile, challenge field 또는 O.1~O.4 판정표를 정의하지 않는다. 따라서 Android Key Attestation을 `K_tsu` 심사에 쓰는 것은 CA가 business practices/CPS에 정하는 **부분 증거**다.

#### Android Key Attestation으로 확인 가능한 것

CA가 TSA용 custom provider profile을 정의했다면 5.7.1의 chain·status·extension selection과 SPKI 결속 절차를 재사용하여 다음을 확인할 수 있다.

| Android signed 값 | `K_tsu`에 대해 뒷받침하는 사실 | C2PA 고정값 여부 |
|---|---|---|
| CA challenge와 `attestationChallenge` 일치 | Evidence가 현재 TSA enrollment에서 생성됐다는 freshness | TSA에는 C2PA 고정 field가 아님. challenge length·TTL·소진은 CA 결정 |
| attestation certificate SPKI = CSR SPKI | attested key가 발급 대상 `K_tsu`라는 결속 | custom CPS 검증 |
| TrustedEnvironment/StrongBox security levels | key implementation이 hardware-backed secure environment에 있음 | C2PA의 TSA용 Android 숫자 profile은 없음 |
| `hardwareEnforced.origin=GENERATED` | key가 해당 secure implementation에서 생성됨 | custom CPS 검증 |
| `hardwareEnforced.purpose`에 `SIGN` | key에 일반 signing authorization이 있음 | timestamp 전용성까지 증명하지 않음 |
| locked/Verified RootOfTrust와 patch fields | Android platform boot·patch 상태 | TSA TA identity나 trusted-time subsystem 상태는 아님 |
| `attestationApplicationId` | Android package identity | package가 TEE 안에서 실행된다는 증거가 아님 |

TSA custom profile에서 Android field의 허용값을 Claim AL2와 같게 채택할 수는 있지만, 그 선택은 C2PA TSA 표준값이 아니라 CA 강화정책으로 기록한다.

#### Android Key Attestation만으로 확인할 수 없는 것

- TSA application/Trusted Application 자체가 TEE 안에서 실행되는지
- TSA TA의 identity, version, measurement와 secure lifecycle/debug/rollback 상태
- `SIGN` key가 RFC 3161 timestamp에만 사용되는 의미적 전용성
- TSA service·TSU·audience/profile·challenge와 `K_tsu`가 같은 signed scope에 결속되는지
- UTC(k) source, 24시간 online synchronization 시도, intended accuracy, leap-second 처리와 drift-stop 상태
- 한 TSU에 active signing key가 하나뿐인지와 전체 trusted-time path

그러므로 Android Key Attestation 하나만으로 On-Device TSA runtime 적합성을 전부 입증했다고 판단하면 안 된다. Base TSA profile은 나머지 요구를 설계·구현·시험·운영 통제로 확인한다. CA가 optional enrollment attestation profile을 채택했다면 TA/TEE 또는 trusted-time provider Evidence 등 profile이 정한 추가 검증을 수행하고, `profile/version`, `audience`, `challenge`, TSA service/TSU, `K_tsu`, TA identity/measurement와 TEE state의 결속 방식을 CA/provider 계약에 고정한다.

### 6.6 TSA CSR과 Leaf key 결속

Attestation을 사용하는 구현에서는 다음 세 공개키가 같아야 한다.

```text
Evidence가 증명한 TSA subject key
== CSR.subjectPublicKeyInfo
== 발급된 TSA Leaf.subjectPublicKeyInfo
```

Evidence signature를 검증하는 attestation signer 공개키와, 인증서를 발급할 `K_tsu` 공개키를 혼동하지 않는다.

## 7. 공식 CSR profile 적용 방법

### 7.1 Claim AL1·AL2 CSR

| 항목 | AL1 | AL2 |
|---|---|---|
| Subject | ASN.1 Name 구조·C/O/CN 포함; 제품 식별과 DN 차이 처리는 [§3.3](#csr-subject-identification) 참조 | 동일 |
| SPKI | RSA 2048+, EC P-256/P-384/P-521, Ed25519 | 동일 |
| Basic Constraints | critical, `cA=false` | 동일 |
| Key Usage | critical, 정확히 `digitalSignature` + `contentCommitment` | 동일 |
| EKU | non-critical, `c2pa-kp-claimSigning` + email/document signing 중 하나 이상 | 동일 |
| Certificate Policies | non-critical, C2PA policy OID | 동일 |
| C2PA AL | 필수, non-critical; extension OID `.62558.3`, value `.3.10` | 필수, non-critical; extension OID `.62558.3`, value `.3.20` |
| CPL Record ID | 필수, non-critical; extension OID `.62558.4`, DER UTF8String(36) UUID | 동일 |
| AIA 요청 시 | optional, non-critical; OID `1.3.6.1.5.5.7.1.1`, 모든 accessLocation은 HTTP URI | 동일 |
| CDP 요청 시 | optional, non-critical; OID `2.5.29.31`, distributionPoint는 HTTP URI | 동일 |

AL1과 AL2 CSR profile의 핵심 차이는 C2PA Assurance Level 값이다.

### 7.2 TSA CSR

| 항목 | 요구 |
|---|---|
| Subject | ASN.1 Name 구조·C/O/CN 포함; 서비스 식별과 DN 차이 처리는 [§3.3](#csr-subject-identification) 참조 |
| SPKI | RSA 2048+ 또는 EC P-256/P-384/P-521; Ed25519 금지 |
| Basic Constraints | critical, `cA=false` |
| Key Usage | critical, 정확히 `digitalSignature` + `contentCommitment` |
| EKU | critical, 정확히 `id-kp-timeStamping` 하나 |
| Certificate Policies | non-critical, C2PA policy OID |
| C2PA AL | 요청 금지 |
| CPL Record ID | 요청 금지 |
| AIA 요청 시 | optional, non-critical; OID `1.3.6.1.5.5.7.1.1`, 모든 accessLocation은 HTTP URI |
| CDP 요청 시 | optional, non-critical; OID `2.5.29.31`, distributionPoint는 HTTP URI |

### 7.3 CSR parser 최소 검증 순서

1. 입력 크기와 단일 DER object 여부 확인
2. PKCS#10 version `0` 확인
3. Subject와 SPKI 구조 확인
4. `extensionRequest` cardinality와 중복 extension 확인
5. SPKI algorithm/parameters는 C2PA CSR profile로, outer CSR signature algorithm/parameters는 CA의 secure PoP policy로 확인
6. CSR signature로 PoP 확인
7. decoded CSR을 선택한 공식 CSR schema로 검증
8. CSR Subject의 형식 검사와 별도로 [3.3절](#csr-subject-identification)의 대상 식별·권한 검증을 수행하고, 해당 CSR extension을 확인된 profile/record와 비교

## 8. 최종 Leaf certificate profile

### 8.1 세 profile 비교

| 항목 | Claim AL1 | Claim AL2 | TSA Leaf |
|---|---|---|---|
| X.509 version | v3 | v3 | v3 |
| serial | 양의 정수, 최대 20 octets, Issuing CA별 유일; high entropy 권장 | 동일 | 동일 |
| 최대 validity | 366일 | 90일 | 4110일 |
| Issuer | Claim Signing Issuing CA Subject와 exact match | 동일 | TSA Issuing CA Subject와 exact match |
| Subject | CPL product DN, C/O/CN, 조건부 OU | 동일 | unique TSA service C/O/CN |
| Subject 제한 | ASCII, unique device identity 금지 | 동일 | service identity |
| SPKI | RSA 2048+, P-256/384/521, Ed25519 | 동일 | RSA 2048+ 또는 P-256/384/521 |
| CA signature algorithm | RSA-PSS 또는 RSA SHA-2, ECDSA SHA-2; 현재 profile 교집합에서 Ed25519 제외 | 동일 | RSA-PSS 또는 RSA SHA-2, ECDSA SHA-2; Ed25519 금지 |
| Basic Constraints | critical, `cA=false` | 동일 | 동일 |
| Key Usage | critical, `digitalSignature`, `contentCommitment` | 동일 | 동일 |
| EKU | non-critical, Claim EKU + email/document 중 하나 이상 | 동일 | critical, 정확히 timeStamping 하나 |
| Certificate Policies | 필수, non-critical, C2PA policy OID | 동일 | 동일 |
| AIA/CDP | AIA 필수·non-critical, OCSP HTTP 필수·caIssuers HTTP 권장; CDP는 optional·non-critical·HTTP | 동일 | non-critical OCSP AIA 또는 non-critical HTTP CDP 중 최소 하나; AIA가 있으면 caIssuers HTTP 권장 |
| C2PA AL | 필수, non-critical, AL1 OID | 필수, non-critical, AL2 OID | 금지 |
| CPL Record ID | 필수, non-critical, authoritative CPL UUID | 동일 | 금지 |

표의 validity는 **C2PA 상한**이다. 실제 CA가 더 짧게 발급할 수 있지만, 그 값은 CA CPS의 별도 결정이다. 특히 TSA 90일은 C2PA 공통값이 아니며 채택한다면 프로젝트 강화정책이다.

Claim의 `SPKI` 행에서 Ed25519는 **Leaf subject key** 알고리즘으로 허용된다. 반면 현재 Claim Signing Issuing CA profile은 issuer SPKI와 signature를 RSA 또는 EC로 제한하므로, Leaf profile이 certificate signature algorithm으로 열어 둔 Ed25519는 conformant chain에서 실현할 수 없다. 따라서 clarification 또는 profile 개정 전 Claim Leaf의 실제 issuer signature는 RSA/ECDSA 교집합만 허용한다. 이 upstream 불일치와 production 결정은 [Claim `GAP-NORM-04`와 `OD-ALG-01`](claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md#7-gap-and-clarification-register)에서 관리한다.

### 8.2 공통 extension

- SKI: 필수, non-critical. RFC 5280 §4.2.1.2 Method (1)에 따라 `subjectPublicKey` BIT STRING 내용의 160-bit SHA-1 hash로 계산한다.
- AKI: 필수, non-critical. `keyIdentifier`는 선택된 Issuing CA certificate의 SKI와 byte-for-byte 같아야 한다. `authorityCertIssuer`와 serial은 optional이다.
- Basic Constraints: 필수, critical, `cA=false`
- Key Usage: 필수, critical, `digitalSignature`와 `contentCommitment`
- Certificate Policies: 필수, non-critical, C2PA policy OID 포함
- CA가 소유한 별도 CPS policy OID는 추가할 수 있지만 C2PA policy OID를 제거할 수 없다.

### 8.3 사용하는 주요 OID

| 이름 | OID |
|---|---|
| Subject Key Identifier | `2.5.29.14` |
| Authority Key Identifier | `2.5.29.35` |
| Key Usage | `2.5.29.15` |
| Basic Constraints | `2.5.29.19` |
| Extended Key Usage | `2.5.29.37` |
| Certificate Policies | `2.5.29.32` |
| Authority Information Access | `1.3.6.1.5.5.7.1.1` |
| CRL Distribution Points | `2.5.29.31` |
| `id-kp-emailProtection` | `1.3.6.1.5.5.7.3.4` |
| `id-kp-timeStamping` | `1.3.6.1.5.5.7.3.8` |
| `documentSigning` | `1.2.840.113583.1.1.5` |
| C2PA certificate policy | `1.3.6.1.4.1.62558.1.1` |
| `c2pa-kp-claimSigning` | `1.3.6.1.4.1.62558.2.1` |
| C2PA Assurance Level extension | `1.3.6.1.4.1.62558.3` |
| AL1 value | `1.3.6.1.4.1.62558.3.10` |
| AL2 value | `1.3.6.1.4.1.62558.3.20` |
| C2PA CPL Record ID | `1.3.6.1.4.1.62558.4` |

### 8.4 발급 후 self-check

```text
certificate signature valid
AND certificate SPKI == verified CSR SPKI
AND Subject == verified CPL DN 또는 registered TSA service DN
AND Issuer == selected Issuing CA Subject
AND SKI == RFC 5280 Method (1) hash of issued subjectPublicKey BIT STRING contents
AND AKI.keyIdentifier == selected Issuing CA SKI
AND serial is positive, <= 20 octets, and unique within Issuing CA
AND validity <= selected C2PA profile maximum
AND tbsCertificate.signature == outer signatureAlgorithm with RFC 5280-compatible parameters
AND required extensions/criticality/cardinality correct
AND forbidden extensions absent
AND official certificate schema validation == PASS
AND chain builds to the correct Claim 또는 TSA trust domain
```

## 9. 발급 이후에도 지켜야 하는 항목

### 9.1 Certificate acceptance

Certificate acceptance는 Subscriber Agreement 조건의 수락을 의미하며 Claim Generator Product instance가 인증서를 성공적으로 설치하고 사용함으로써 implicit하게 성립한다. 그러나 이 발급 후 implicit acceptance는 3.1절에서 발급 시점에 이미 충족해야 하는 legally valid Subscriber Agreement 또는 affiliated Terms of Use acknowledgement gate를 대체하지 않는다. 이 implicit-installation 규칙을 TSA certificate에 자동 확장하지 않으며, 별도 activation callback이나 receipt API는 C2PA가 일괄 요구하지 않는다.

이 project의 TSA staged activation은 별도 `ARCH-DECISION`이다. Certificate issuance 성공이나 위 implicit certificate acceptance를 activation authorization으로 해석하지 않으며, 02는 검증된 `{organization, TSA operator, service, TSU, K_tsu, TSA Leaf, provider profile-or-NONE, environment}` tuple을 issuance record에 고정한다. Activation을 채택한 배포만 이 tuple을 04의 server transaction으로 넘긴다.

Claim Signing certificate는 Subject로 명시되고 CPL에 등록된 Generator Product가 인증서에 표시된 AL로 C2PA Claim을 서명하는 용도로만 사용한다.

### 9.2 Renewal, re-key와 변경

- 동일 key로 renewal하지 않는다.
- re-key는 새 key와 새 CSR을 사용하고 issuance authentication·key ownership/PoP 및 모든 current eligibility gate를 다시 수행한다. Initial 조직·대표자 I/A/V 원자료는 변경 trigger 또는 ≤398-day 재인증 시점에 갱신한다.
- Subject 변경은 initial identity validation을 다시 수행한다.
- 발급된 인증서 내용을 modification하지 않는다. 변경이 필요하면 새 인증서를 발급한다.

### 9.3 Revocation

다음 C2PA CP 사유가 발생하면 CA는 관련 certificate를 revoke해야 한다.

- Generator Product의 CPL status가 `revoked`로 시작하는 값으로 전이
- C2PA Governing Authority의 인증되고 검증된 요청
- Subscriber의 인증되고 검증된 요청
- Generator Product의 suspected 또는 confirmed compromise, 또는 적용 대상 AL의 attestation failure
- confirmed private key exposure
- C2PA Certificate Policy non-compliance
- certificate misuse

인증된 revocation 요청은 진위와 권한을 확인하고 72시간 안에 처리한다.

private key loss 등 CP 목록 밖의 추가 사유는 CA CPS가 더 엄격한 revocation 사유로 정의할 수 있다.

### 9.4 상태 정보

- 모든 Claim Leaf에는 인증서 만료 후 최소 1년인 record-keeping 기간까지 OCSP를 제공하고, 응답은 최소 RFC 6960 profile을 따른다.
- TSA/Subordinate certificate에 OCSP를 제공하지 않으면 RFC 5280 §5에 맞는 CRL을 제공해야 한다.
- CA는 모든 unexpired certificate의 current valid/revoked status를 제공하는 24×7 publicly accessible Repository를 유지한다.
- OCSP 검증기는 RFC 6960 §3.2에 따라 request의 CertID와 응답 certificate의 correspondence, signature, signer identity/authorization, 충분히 최근인 `thisUpdate`와 존재하는 `nextUpdate`가 현재보다 미래인지 확인한다. `producedAt`은 응답이 서명된 시각이며, 추가 허용편차는 검증 정책에서 정한다.
- OCSP의 `good`은 certificate가 revoked로 알려지지 않았다는 제한된 뜻이지, 발급 사실·현재 유효기간 또는 외부 TSA key activation을 보장하지 않는다.

### 9.5 발급 기록과 개인정보

CA는 모든 issued certificate에 대해 다음 repository record를 인증서 만료 후 최소 1년 보존한다.

- serial, Subject, validity와 extensions
- revocation status

그와 별도로 CA는 certificate application·발급·revocation·attestation validation과 access attempt를 포함하여 certificate operation과 관련된 모든 system/user activity를 상세히 기록해야 한다. 각 event에는 Subscriber와 operation을 요청한 CA system/personnel의 identity, timestamp, action과 relevant parameter가 연결되어야 한다. log를 비인가 접근·변경·삭제로부터 보호하고 정기적으로 검토한다. CSR 심사와 AL2 판정에는 사용한 policy/provider/reference version과 상태 snapshot도 재현 가능하게 연결한다.

CA archival policy는 보존할 record 종류, 기간, secure storage와 retrieval 절차를 정의한다. 상세 audit log의 event schema, 저장 기술과 Raw Evidence·CSR·challenge 보존기간은 그 policy/CPS에서 정한다. issued-certificate repository의 최소 1년 규칙이 이 raw artifact 전체에 자동 적용되는 것은 아니며, C2PA가 특정 WORM 제품이나 raw Evidence 영구보존을 요구하지도 않는다.

Claim Subject에는 제품 모델을 식별할 수 있지만 개별 device를 고유 식별하는 serial을 넣지 않는다. 비공개 Subscriber business information의 기밀성을 유지하고, 서면 동의·법적 요구·허용된 감사 등 정당한 예외 외에는 제3자에게 공개하지 않는다. 개인정보는 적용법과 enrollment·identity validation·certificate issuance라는 명시 목적에 한정해 처리하며, 법적 제약 안에서 정보주체의 접근·정정·삭제 권리를 지원한다. Audit identity 의무를 충족하면서도 필요한 검증·감사 목적에 맞는 최소 식별자만 수집·보존하고 접근을 통제한다.

## 10. Trust List와 chain을 적용하는 방법

| 대상 | 적용 목록 | 주의점 |
|---|---|---|
| Claim Signing chain | C2PA Trust List | Claim Issuing CA와 Claim trust domain 사용 |
| TSA chain | C2PA TSA Trust List | TSA Issuing CA와 TSA trust domain 사용 |

- Claim Leaf와 TSA Leaf를 서로 다른 `pathLenConstraint=0` Issuing CA가 발급한다.
- Claim과 TSA Issuing CA key, HSM authorization과 목적별 Trust List 소비를 혼용하지 않는다. Offline Root는 공유할 수 있다. 공유하는 경우 Conformance Program은 같은 Root certificate를 CA와 TSA 신청 section 양쪽에 기재하도록 안내하며, 실제 CA Trust List와 TSA Trust List 등록은 각각 별도 심사·승인을 받는다. 실제 Root 공유 여부는 `04-Security-and-Operations.md`의 `OPEN-PKI-01`에서 결정한다.
- C2PA TSA Trust List는 개별 TSA Leaf 또는 TSU device registry가 아니다. 승인된 TSA/CA trusted-entity service record, 그 Root·Intermediate certificate와 service status를 배포한다.
- schema/release는 pin할 수 있지만 운영 Trust List 파일의 현재 hash를 영구 고정하면 안 된다. 새 snapshot의 issue/next-update, service status, 출처·무결성과 digest를 검증·기록해야 한다. C2PA Trust List schema가 공통 snapshot signature wire format을 정하는 것은 아니므로, 별도 signature를 쓰는 경우 그 인증 배포 방식은 프로젝트/운영 정책으로 구분한다.
- trust chain topology와 Root/Intermediate/OCSP responder 운영 상세는 별도 PKI 운영 문서에서 다룬다.

## 11. 스펙 고정 요구와 CA/CPS 결정의 분리

API endpoint, request/response body와 database schema는 이 문서의 범위가 아니다. 구현 형식과 무관하게 아래 의미와 판정은 유지해야 한다.

### 11.1 스펙에서 명확히 정한 것

| 영역 | CA가 반드시 충족·검증할 요구 |
|---|---|
| Claim eligibility | CP의 signed Notice 선발급 허용과 Conformance Program의 public-CPL-only 문구가 충돌하므로, 현재 interim production rule은 authenticated public CPL의 `status=conformant`를 요구하고 Notice를 받은 경우 onboarding proof로만 사용한다. `generatorProduct`, Applicant·DN·recordId, 존재하는 `minVersion`, requested AL≤max AL을 확인한다. 최종 CPL/Notice 정책은 Claim Operations Decision Register 승인 전까지 production-blocking이다. |
| Enrollment 기본 | formal Subscriber application 심사·승인 후 credential 결속, 안전한 credential, 신청자의 발급 권한과 발급 대상 key pair ownership 검증. signed CSR은 CP가 허용한 방법이며, 선택하면 실제 CSR signature를 검증해야 함 |
| Agreement·warranty | product-name control, Subject 발급 승인, Applicant Representative의 요청·계약 권한, 최종 certificate 정보 정확성과 발급 전 legally valid Subscriber Agreement 또는 affiliated Terms of Use acknowledgement |
| Claim key | Subscriber 측 생성·배타 통제, escrow/recovery 금지, same-key renewal 금지 |
| Claim AL1 | Subscriber authorization과 구분된 적격 Generator Product instance authentication. AL2 O.1~O.4 hardware Evidence는 공통 필수가 아님 |
| Claim AL2 | O.1~O.4 hardware-backed Evidence와 fail-closed. challenge를 쓰는 provider flow는 CA 발급값 exact-match와 provider nonce 권고 준수 |
| Android Claim AL2 | 5.7.2의 challenge, security levels, app identity, key authorization, boot와 patch predicate |
| TSA 운영 | UTC(k) traceability, accuracy/drift-stop, leap second, timestamp 전용 key, TSU당 active key 하나, SHA-2 256/384/512 |
| On-Device TSA | TSA application의 TEE 실행, `K_tsu`의 TEE 생성·보관, 최소 24시간마다 online synchronization 시도 |
| CSR/certificate profile | 7~8절의 algorithm, Subject, extension OID/value/criticality/cardinality, 금지 extension과 validity 상한 |
| 발급 CA와 trust | Claim과 TSA를 별도 Issuing CA/trust domain으로 분리하고 해당 C2PA Trust List 경로 사용 |
| lifecycle/status | full re-key validation, 정해진 revocation 사유·72시간 처리, Claim OCSP와 TSA OCSP-or-CRL, issued-certificate record 최소기간 |
| audit/privacy | certificate-operation 상세 log와 필수 identity/time/action/parameter, log 보호·정기검토, archival policy, 비공개 Subscriber 정보와 개인정보 보호 |

#### 외부 Generator Product Conformance 전제

다음은 CA가 request-time에 자체 판정하는 항목이 아니라 외부 GP TOE와 Applicant가 Conformance Program에서 충족할 의무다. Certificate Platform은 signed Notice를 받은 경우 onboarding proof로 검증·보관하되, 현재 interim production issuance에서는 그 유무와 별개로 authenticated public CPL의 `status=conformant` record와 그 `maxAssuranceLevel`을 eligibility 입력으로 사용한다. 요청자가 직접 제출한 binary나 GPSA를 authoritative conformance 결과의 대체물로 사용하지 않는다.

| 외부 owner | C2PA 필수 의무 | Certificate Platform 연계 |
|---|---|---|
| 자동 enrollment를 사용하는 GP TOE | CA가 요구한 secure authentication method 구현; Edge binary에 authentication secret 포함 금지 | CA는 매 요청에서 GP instance authentication을 수행하고 authoritative conformance status를 확인 |
| GP Applicant | automated enrollment process·secret 관리 설계·enrollment/renewal trigger를 GPSA에 기록; authentication method 상세를 application 또는 허용된 90일 update로 제출 | CA가 binary/GPSA를 매 요청마다 재심사하지 않고 Conformance Program의 승인 결과를 소비 |

### 11.2 프로젝트 선택과 CA 서버 구현자·CPS가 반드시 정할 것

아래 표에는 이미 확정된 프로젝트 선택과 C2PA가 단일 값을 주지 않아 production 전에 CA CPS, provider profile 또는 운영정책에서 선택해야 할 값이 함께 있다. 프로젝트 선택을 C2PA 고정값으로 오표기하지 않고, 남은 선택은 미정인 채 production에 투입하지 않으며 상호운용 test vector로 검증한다.

| 결정 영역 | CA/CPS에서 정할 내용 |
|---|---|
| 지원 발급 범위 | 승인하여 수용한 Subscriber/product에는 CPL max AL 이하 모든 Claim AL 요청을 지원하고, 유효한 요청이 해당 AL의 mandatory gate를 모두 통과하면 발급으로 진행. CA/CPS는 TSA 종류, 수용할 customer/product service scope, 실제 key algorithm subset과 profile 상한보다 짧은 validity를 결정 |
| Agreement·warranty | affiliation 판정, legally valid Subscriber Agreement 또는 Terms of Use acknowledgement, 문서 version/digest·승인자·시각, Subject/product-name control·대표자 권한·최종 certificate 정보 정확성의 발급별 evidence |
| CPL/Notice | source 인증, snapshot freshness/cache, 상태 변경 시 fail-closed, Android version과 CPL `minVersion` 비교 규칙 |
| PoP/CSR input policy | 이 프로젝트는 DER PKCS#10 CSR signature 검증을 key ownership PoP로 채택. CA/CPS는 outer CSR signature algorithm allow-list, 추가·미인지 attribute/extension의 reject/ignore 정책, 입력 크기와 parser 제한을 결정. KMS inspection 등 다른 PoP는 별도 승인된 profile로만 추가 |
| Provider 등록 | provider profile/version, signed Evidence schema, trust anchors, chain/status source와 rotation·freshness, Reference Value 출처·version |
| Challenge | 적용할 provider flow, byte length·entropy·encoding·transform, 목적/Subscriber/CPL 또는 TSA service 결속, TTL, single-use/동시성, 재제출 시 이전 freshness 값 재사용 금지와 보존 |
| Android app mapping | package/version/signing digest 등록, shared UID와 signing-key rotation의 expected-set/exact-set 여부, extra key purpose/digest 허용 여부, product-specific brand/manufacturer/model/boot Reference Value |
| AL2 coverage | O.3 Claim Generator revision/vulnerability 판정, O.4 component inventory와 component별 Evidence coverage, 여러 Evidence의 같은 instance/key 결속 |
| AL2 downgrade | `OD-DOWNGRADE-01` 승인값은 silent/automatic downgrade 금지와 별도의 명시적 AL1 request. 변경 시 consent/threat/profile test와 CPS update 필요 |
| TSA 신청자 심사 | TSA operator/service/TSU 등록·권한·unique Subject와 business-practices evidence |
| Optional TSA enrollment attestation | 채택 여부. 채택 시 Android KA/추가 TA·TEE·trusted-time Evidence schema와 challenge, trust/status/reference values, `K_tsu`·service·TSU 결속 |
| TSA runtime acceptance | timestamp 전용성, single-active-key, UTC(k) source, accuracy, 24시간 sync, drift-stop을 어떤 시험·운영 증거로 확인할지 |
| 발급 template 선택값 | serial 생성·예약, 실제 validity, CA-controlled AIA/CDP URI, optional Claim CDP와 private CPS policy OID |
| 기록·개인정보 | raw Evidence/challenge/reference snapshot의 감사 보존기간, 접근통제, 민감 field 최소수집·파기 |
| 운영 실패 정책 | provider/status/reference source timeout·stale·unknown 처리, resource·abuse limit, root/profile 긴급 차단 |

Claim Signing의 JSON field name, schema와 cardinality는 [전용 request-body 문서](claim-signing-enrollment-request/01-Enrollment-Request-Body.md)가 고정하며 구현자가 바꾸지 않는다. Claim endpoint, response와 transaction은 이 문서 범위가 아니다. TSA 등 명시적으로 분리된 계약만 자체 API shape를 소유한다. CA가 선택한 값을 C2PA 표준 자체의 고정값이라고 표현하지 않고, 반대로 선택이 필요하다는 이유로 C2PA 필수 predicate를 생략하지 않는다.

## 12. 구현 완료 점검표

### 12.1 공통

- [ ] DER PKCS#10 parsing과 실제 CSR signature PoP 검증
- [ ] profile별 key algorithm/size/curve 확인
- [ ] CSR requested extension을 CA template에 그대로 복사하지 않음
- [ ] Issuing CA별 serial 유일성과 양수·20 octets 상한 확인
- [ ] 동일 key renewal 금지와 re-key full validation
- [ ] 발급 후 공식 certificate schema와 chain self-check
- [ ] revocation 요청 권한과 72시간 처리 절차
- [ ] RFC 6960 OCSP 및 조건부 RFC 5280 CRL profile 확인
- [ ] 모든 unexpired certificate의 24×7 공개 current-status Repository 확인
- [ ] 만료 후 최소 1년 issued-certificate repository record 확인
- [ ] issuance·revocation·attestation validation·access attempt 등 전체 certificate-operation audit event와 필수 identity/time/action/parameter 기록
- [ ] audit log 비인가 접근·변경·삭제 방지와 정기 검토
- [ ] archival policy의 record 종류·보존기간·secure storage·retrieval 및 개인정보 목적 제한 확인

### 12.2 Server challenge를 사용하는 경로

- [ ] 이 provider flow에서 challenge가 C2PA/provider 필수인지 CA 강화정책인지 구분
- [ ] provider 제한에 맞는 length·entropy·encoding·transform을 CPS/profile에 고정
- [ ] challenge를 purpose, enrollment, Subscriber/CPL 또는 TSA service와 결속
- [ ] 서버가 보관·재계산한 예상 bytes와 signed Evidence bytes를 exact-match
- [ ] TTL, single-use, 동시 제출, retry와 실패 시 소진 정책 적용
- [ ] RFC 3161 runtime nonce와 enrollment challenge를 분리

### 12.3 Claim 공통 및 AL1

- [ ] formal Subscriber application의 완전성·정확성·identity와 조건부 attestation 처리능력 심사, 승인 후 credential 결속 확인
- [ ] 신청 조직, 대표자와 발급 범위 확인
- [ ] Subject의 발급 승인, product name 사용권/control, Applicant Representative의 요청·계약 권한과 최종 certificate 정보 정확성 확인
- [ ] non-affiliated Subscriber Agreement의 legal validity/enforceability 또는 affiliated Terms of Use acknowledgement를 발급 전에 확인하고 version/digest·주체·시각을 enrollment record에 결속
- [ ] secure enrollment credential 확인
- [ ] 승인된 Subscriber/product에 대해 CPL max AL 이하 모든 Claim AL 요청 경로를 지원하고, 유효한 요청의 해당 AL mandatory gate 전체 성공 후 발급으로 진행
- [ ] 자동 enrollment에서 GP instance authentication 성공을 Subscriber authorization과 별도 predicate로 기록하고, 구현 지침에 따라 request/authorization context에 연결
- [ ] 398일 Subscriber 재인증 관리
- [ ] Claim Signing private key의 exclusive control과 escrow/recovery 금지
- [ ] signed Notice를 받은 경우 onboarding proof로 확인하고 authenticated public CPL의 current `status=conformant`를 별도로 확인; Notice-only pre-public issuance는 source tension이 해소될 때까지 금지
- [ ] `generatorProduct`, Applicant, DN, recordId와 존재하는 `minVersion` 확인
- [ ] requested AL이 CPL max AL 이하인지 확인
- [ ] AL1 CSR/Leaf의 AL OID와 validity 확인

### 12.4 Claim AL2

- [ ] CPL `attestationMethods`와 실제 provider method 일치
- [ ] challenge를 사용하는 provider이면 unique dynamic challenge와 Evidence nonce 일치; Android는 반드시 `attestationChallenge` 확인
- [ ] provider trust/signature/certificate-validity/status 검증과 provider별 공식 legacy 예외 적용
- [ ] Evidence subject key와 CSR SPKI 결속
- [ ] Android이면 provisioning-information extension 인접 규칙과 root 쪽 첫 Key Attestation extension 선택 확인
- [ ] Android `attestationVersion`/Keymaster·KeyMint version pair, version별 DER parse와 5.7.2 field 전체 확인
- [ ] Android CP의 `bootPatchLevel`은 공식 Android Tag 719로 parse
- [ ] package/version/signing digest, shared UID와 CPL mapping 정책 확인
- [ ] O.1 제품 identity 판정
- [ ] O.2 hardware key 생성·보관·possession 판정
- [ ] O.3 platform과 Claim Generator 각각 판정
- [ ] O.4 모든 Asset/Assertion 처리 component 판정
- [ ] missing/unknown/stale 결과를 PASS로 처리하지 않음
- [ ] AL2 실패를 변환하지 않고 별도의 명시적 AL1 request에서 AL1 policy decision과 certificate profile 생성

### 12.5 TSA

- [ ] conformant CA의 TSA 운영 구조와 별도 TSA trust chain 확인
- [ ] business practices에 TSA 신청자 확인 절차 문서화
- [ ] TSA practices의 hash, signature lifetime, 의무·제한, 검증, time accuracy와 logging 공개
- [ ] TSA CSR에서 timeStamping EKU만 허용
- [ ] TSA Leaf에서 C2PA AL/CPL extension 금지
- [ ] On-Device TSA의 TEE 실행과 TEE key 생성·보관을 설계·구현·시험·운영 acceptance로 확인
- [ ] UTC(k), accuracy/drift stop, single active key, 24시간 sync 시도와 공인 leap-second 통지 시 synchronization 유지를 runtime/운영 acceptance로 확인
- [ ] SHA-2 256/384/512 요청만 허용
- [ ] optional custom attestation profile을 쓰면 provider 공식 schema·trust·status·challenge·key binding 확보
- [ ] Android Key Attestation을 optional TSA profile에 쓰더라도 나머지 TSA TA/TEE/trusted-time 요구를 다른 승인 통제로 확인

### 12.6 외부 GP Conformance 연계

- [ ] GP Applicant가 automated enrollment process·authentication secret 관리 설계·enrollment/renewal trigger를 GPSA에 기록했는지 Conformance Program 책임으로 추적
- [ ] enrollment authentication method 상세가 application에 포함됐거나, 당시 제공할 수 없었다면 conformance 승인 후 90일 안에 별도 update됐는지 Conformance Program 책임으로 추적
- [ ] Edge GP TOE binary의 authentication secret 금지를 외부 GP 적합성 요구로 추적
- [ ] Certificate Platform은 signed Notice를 받은 경우 onboarding proof로 검증하고 production issuance에는 그 유무와 별개로 authenticated public CPL의 current `status=conformant`를 요구하며 self-submitted binary/GPSA를 request-time 대체 증거로 사용하지 않음

## 13. 근거 자료와 적용 범위

### 13.1 직접 적용한 C2PA 원문

- [C2PA Certificate Policy v0.2](../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md): enrollment, AL1/AL2 Dynamic Evidence, On-Device TSA, Leaf profile, renewal/re-key/revocation/status의 주 근거
- [C2PA Conformance Program v0.2](../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md): Generator Product/CA/TSA 자격과 Trust List 등록 관계
- [C2PA Generator Product Security Requirements v0.2](../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md): Claim key 보호와 O.1~O.4 제품 보안 요구 보조 근거
- [CPL schema](../conformance-public/schemas/conforming-products/conforming-products-list.schema.json)와 [Companion Guide](../conformance-public/schemas/conforming-products/Companion%20Guide%20for%20the%20C2PA%20Conforming%20Products%20List.md): Claim eligibility field 의미
- [C2PA OID registry](../conformance-public/schemas/mib/oid.txt): C2PA policy, Claim EKU, AL과 CPL extension OID

### 13.2 직접 적용한 공식 CSR/certificate profile

- Claim AL1: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.yaml)
- Claim AL2: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.yaml)
- TSA Leaf: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.yaml)

### 13.3 함께 적용할 외부 표준·provider 원문

- [RFC 2986](https://www.rfc-editor.org/rfc/rfc2986.txt): PKCS#10 CSR 구조와 signature
- [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.txt): X.509 certificate, extension과 path validation
- [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960.txt): OCSP
- [RFC 3161](../rfc3161.txt)과 [RFC 5816](../rfc5816.txt): 외부 TSA runtime과 time-stamping certificate purpose의 보조 근거
- [Android Key Attestation verification](https://developer.android.com/privacy-and-security/security-key-attestation): off-device chain 검증, trust root/status와 attestation extension 선택 규칙
- [AOSP Key and ID Attestation](https://source.android.com/docs/security/features/keystore/attestation): KeyDescription·AuthorizationList·RootOfTrust·AttestationApplicationId ASN.1 field와 challenge 재사용 주의
- [Android `KeyGenParameterSpec.Builder`](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder): `setAttestationChallenge`의 의미와 최대 128-byte 제한

### 13.4 조사했지만 enrollment 규칙으로 직접 적용하지 않은 자료

- [Additional Conformance Requirements](../conformance-public/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md): `specVersion`, actions, crJSON, `digitalSourceType` 등 Manifest/Generator/Validator 요구이며 Leaf enrollment field를 추가하지 않는다.
- [Content Credentials Specification 2.4](../specifications/build/site/specifications/2.4/specs/C2PA_Specification.html): Claim/Manifest와 timestamp 사용을 확인하는 runtime 기준이며, Certificate Platform에 runtime signing endpoint를 요구하지 않는다.

### 13.5 기준 snapshot Git-blob hash

아래 값은 `2466172859fad1215f7aaf7e3768b41a0ac29abc:path`가 가리키는 Git blob의 exact byte stream에 대한 SHA-256이다. Local link가 가리키는 dirty/EOL-converted worktree bytes를 해시한 값이 아니다.

| 자료 | SHA-256 |
|---|---|
| Certificate Policy v0.2 | `124fad3e3d578f40867557719f5599110a57be010e6aa4d3a3408695afdae77b` |
| Conformance Program v0.2 | `23c8dedd6e39238b3f4d0b8b2ba0bad38fe717a683146440f6354c6a58e50586` |
| Generator Product Security Requirements v0.2 | `4275064eebf01025ac0d7596f1a25a207b90d8cb921f3cbcd3327f7ec78c3a95` |
| Claim AL1 CSR / cert schema | `89487e5ae29099f1c4f799dee03f1a363c582b8eb8912150702ffe2b8d5c7919` / `8e7470d0a4f282ba88d017a3b3d864c757e4104e7d4b77657c560beaa0e4a50b` |
| Claim AL2 CSR / cert schema | `5bbb03a4ca7614e66c6d15d3fb2ef2e767b523bb2b23f6e019ffa0c984258b44` / `c0971eae5df9724b3c1c8bc51af809eb462f07540833c0bd30d8c442ab212e06` |
| TSA CSR / cert schema | `3026be2b88148d3f6e1a0f721da9ef527a3cd0eac4c44691ee97ac25aa6ff58e` / `dcd99637469e871765e33dfec05e1ec5850fde365822a9171019444fe743c39a` |
| CPL schema | `6664f41092dd8e0c798f52d4f8cc24de66585312e179fcbd881f8c016caa8cfb` |
| OID registry | `f66386f8b9b2e298a6a72bbf38f982e879908632ab58e7f32ca2b56fe4bf9b1a` |

운영 CPL과 Trust List는 계속 갱신되는 자료이므로 위와 같은 고정 source schema hash가 아니라, 실제 판단에 사용한 snapshot의 발행 시각·상태·digest를 발급 기록에 남긴다.

이 작업에서 사용한 RFC와 Android 공식 원격 원문의 exact URL, version/update date, 조회일 및 content SHA-256은 [Claim Signing source snapshot](claim-signing-enrollment-request/README.md#6-원문-snapshot)에 기록했고 `/tmp/c2pa-claim-signing-sources/`의 고정 bytes를 감사 입력으로 사용한다. Android 자료는 provider-specific 해석에만 적용하며 C2PA authority로 취급하지 않는다.

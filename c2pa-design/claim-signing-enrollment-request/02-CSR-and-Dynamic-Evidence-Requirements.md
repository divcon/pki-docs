# CSR and Dynamic Evidence Requirements

## 1. Authority와 용어

이 문서는 Claim Signing만 다룬다. TSA Leaf나 기존 TSA 아키텍처의 Evidence, EKU, lifecycle 또는 runtime 요구를 Claim Signing 근거로 사용하지 않는다.

| 표기 | 의미 |
|---|---|
| `C2PA` | commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`의 Certificate Policy/Conformance Program/GSPR/profile/CPL 원문 |
| `RFC` | README §6에 identity를 고정한 RFC Editor 원문; CSR 기본 구조는 RFC 2986/2985, extension은 RFC 5280, SPKI encoding은 RFC 3279/5480/8410 |
| `PROVIDER` | 선택한 attestation provider의 signed artifact 문법·trust·freshness·claim 의미 |
| `CA-CPS` | CA가 공개하고 승인한 business practice, algorithm/validity/provider 운영 범위 |
| `PROJECT` | 이 문서 집합의 request-body wrapper, binding과 fail-closed 강화정책 |

CP는 all-caps BCP 14 keyword에만 RFC 2119/8174 의미를 부여한다(CP:10-12). GSPR은 별도 BCP 14 선언이 없지만 각 절을 requirements로 제시하고 uppercase `SHALL`을 사용하므로, 아래 표는 원문의 대소문자를 보존해 “C2PA requirement text”로 분류한다. lowercase `shall` 또는 서술 의무는 `NON-BCP14-OBLIGATION`이다.

## 2. PKCS#10 CSR와 PoP

RFC 2986 v1.7의 request는 `CertificationRequestInfo`, signature algorithm과 signature로 구성된다. 정보부는 version 0, Subject Name, SubjectPublicKeyInfo와 attributes를 담고, request 주체의 private key가 그 DER-encoded 정보부에 서명한다(RFC 2986 §3, §4.1, §4.2). CA는 요청 주체를 인증하고 signature를 검증한다(§3). 전송 protocol과 response 형식은 RFC 범위 밖이다(§1, §3).

따라서 server는 다음을 별도 predicate로 수행한다.

1. canonical base64를 decode하고 exactly one strict DER PKCS#10 object인지 확인한다.
2. `CertificationRequestInfo.version == 0`인지 확인한다.
3. Subject, SPKI와 extensionRequest를 AL별 official schema 및 authoritative state와 확인한다.
4. outer signature algorithm/parameters가 `OD-ALG-01`의 승인값인지 확인한다.
5. CSR SPKI로 exact `CertificationRequestInfo` signature를 cryptographically verify한다. 이것이 PoP다.
6. CSR에 requested value가 있어도 최종 TBS certificate는 server-authoritative template로 다시 만든다.

Schema parser가 `signature_hex` field를 출력하거나 JSON Schema validation이 성공했다는 사실은 signature의 cryptographic validity를 증명하지 않는다. 반대로 AL2 attestation이 key possession/property를 주장해도 RFC 2986 PoP를 생략하지 않는다(CP:471-473).

## 3. AL1/AL2 CSR profile

AL1과 AL2 CSR schema는 title/definition name과 requested `c2pa-al` value 외에는 byte-level diff상 동일하다. AL1은 `.3.10`, AL2는 `.3.20`이다(AL1 CSR:1090-1133; AL2 CSR:1090-1133).

### 3.1 공통 CSR predicate

| field | cardinality / predicate | authority · modality | locator |
|---|---|---|---|
| `version` | exactly `0` | `RFC`, required syntax | RFC 2986 §4.1 |
| Subject | C, O, CN each present. 추가로 CSR의 full DN을 authoritative CPL record와 일치시키고, CPL에 OU가 있으면 동일하게 요구하며, all value plain ASCII·unique instance ID 금지를 선검사 | C/O/CN 존재는 `C2PA REQUIRED`; 최종 certificate의 CPL DN 제약을 CSR에도 적용하는 것은 `PROJECT` 강화 | AL1 CSR/AL2 CSR:692-740; 최종 Subject 근거 CP:383-395 |
| SPKI RSA | `rsaEncryption`, modulus ≥2048 | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:798-823; CP:1218-1222,1283-1287 |
| SPKI EC | `id-ecPublicKey`, P-256/P-384/P-521 | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:758-795; CP:1218-1222,1283-1287 |
| SPKI EdDSA | Ed25519 only | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:825-866; CP:1218-1222,1283-1287 |
| Basic Constraints request | present, critical, `cA=false` | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:881-919 |
| Key Usage request | present, critical; exactly `digitalSignature=true`, `contentCommitment=true`, all other represented bits false | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:920-984 |
| EKU request | present, non-critical; `c2pa-kp-claimSigning` plus at least one of emailProtection or documentSigning | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:985-1049 |
| Certificate Policies request | present, non-critical; includes `1.3.6.1.4.1.62558.1.1` | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:1050-1091 |
| C2PA AL request | present, non-critical; profile-specific OID value | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:1092-1134 |
| CPL Record request | present, non-critical; DER UTF8String length 36 and exact authoritative UUID | `C2PA REQUIRED` | AL1 CSR/AL2 CSR:1135-1179; MIB:46-48 |
| AIA if requested | non-critical; access location HTTP URI under schema | `C2PA REQUIRED when present` | AL1 CSR/AL2 CSR:1188-1257 |
| CDP if requested | non-critical; fullName HTTP URI under schema | `C2PA REQUIRED when present` | AL1 CSR/AL2 CSR:1258-1336 |
| outer CSR signature | cryptographically valid; allow-list/parameters from approved policy | `RFC` PoP + `PROJECT/CA-CPS` algorithm choice | RFC 2986 §4.2; CP:473 |

“contains” 기반 official schema가 extra Subject RDN, duplicate extension 또는 unrecognized extension을 모두 배제한다고 가정하지 않는다. 이 프로젝트 parser는 exact authoritative DN, required-extension uniqueness와 `OD-ALG-01`의 unknown attribute/extension policy를 추가 검사한다.

### 3.2 Profile 차이

| profile | requested AL extension value | max final validity | Dynamic Evidence |
|---|---|---:|---|
| `c2pa-claim-signing-al1` | `1.3.6.1.4.1.62558.3.10` | 366 days | secure instance credential authentication; provider artifact count `NOT-SPECIFIED`, project `evidenceItems=0` |
| `c2pa-claim-signing-al2` | `1.3.6.1.4.1.62558.3.20` | 90 days | O.1~O.4 hardware-backed semantic coverage required |

두 profile의 CSR schema는 validity를 담지 않는다. validity는 CA가 최종 certificate를 만들 때 적용한다.

<a id="csr-input-fields"></a>

### 3.3 CSR DER 입력 필드와 확장 식별자

`requestedExtensions`, `_pyasn1_decoded`, `signature_hex`, JSON의 `format=csr`는 official inspector/schema의 **decoded projection** 이름이지 PKCS#10 DER 필드나 client body의 추가 JSON field가 아니다. Client는 01의 `csr.value`에 DER를 담는다. 서버는 실제 ASN.1을 검증하고 필요하면 그 결과를 official schema의 projection으로 변환한다.

| 실제 ASN.1 경로 | 타입 / 필수 값·개수 | 근거 |
|---|---|---|
| `CertificationRequest` | `SEQUENCE`의 세 필수 member: `certificationRequestInfo`, `signatureAlgorithm`, `signature` | RFC 2986 §4.2 |
| `certificationRequestInfo` | `SEQUENCE`: `version INTEGER = 0`, `subject Name`, `subjectPKInfo SubjectPublicKeyInfo`, `attributes [0] IMPLICIT SET OF Attribute`가 순서대로 존재 | RFC 2986 §4.1, Appendix A |
| `subject` | C `2.5.4.6`, O `2.5.4.10`, CN `2.5.4.3` 필수; OU `2.5.4.11`은 authoritative CPL에 있으면 같은 값. ASN.1 Name/RDN 구조를 파싱하고 §3.1의 존재 조건 및 project DN 선검사를 구분 | CSR:692-740; RFC 5280 §4.1.2.4; CP:387-395 |
| `attributes`의 `extensionRequest` | Attribute type OID `1.2.840.113549.1.9.14`; `values SET OF` 안에 **정확히 한 `Extensions` 값**. 이 profile에서는 해당 attribute도 정확히 한 개 요구 | value 단일성 RFC 2985 §5.4.2, Appendix A; attribute 존재/중복 거부는 CSR profile + `PROJECT` |
| 각 requested `Extension` | `SEQUENCE { extnID OBJECT IDENTIFIER, critical BOOLEAN DEFAULT FALSE, extnValue OCTET STRING }`; `extnValue` 내용은 아래 inner type의 DER 한 개 | RFC 5280 §4.1, §4.2; RFC 2985 §5.4.2 |
| `signatureAlgorithm`, `signature` | 각각 `AlgorithmIdentifier`, `BIT STRING`; 승인된 outer signature OID/parameters로 exact DER 정보부의 signature 검증. SPKI OID를 outer signature OID로 대신 사용하지 않음 | RFC 2986 §4.2; `OD-ALG-01` |

아래 첫 여섯 확장은 **AL1/AL2 모두 필수**이며 각각 정확히 한 개 요구한다. Extension 중복 거부는 project 강화다. 고정 CP/CSR schema의 요구값과 DER 문법을 함께 표시하되, 추가 EKU/policy/미인식 확장의 수락 여부는 `OD-ALG-01`에서 제한한다. `critical=false`는 DER에서 DEFAULT이므로 해당 member를 **생략**한다. Decoded projection에는 schema가 요구하는 boolean `false`를 생성한다. 마찬가지로 `BasicConstraints.cA=false`의 DEFAULT도 DER에서는 생략할 수 있는 것이 아니라 DER 규칙에 따라 생략하며, decoded 의미는 false다.

| 요청 확장 | `extnID` | critical | `extnValue` 안의 DER 타입과 필수 값 | 고정 원문 |
|---|---|---|---|---|
| Basic Constraints | `2.5.29.19` | `true` | `BasicConstraints SEQUENCE`, `cA=false` 의미. `pathLenConstraint`는 CA가 아닌 최종 cert에 금지되므로 CSR에서도 거부(`PROJECT` 선검사) | CSR:881-919; RFC 5280 §4.2.1.9 |
| Key Usage | `2.5.29.15` | `true` | `BIT STRING`: bit 0 `digitalSignature`와 bit 1 `contentCommitment/nonRepudiation`만 true; bits 2..8 false. DER named-bit-list의 trailing zero bits를 임의 고정 길이로 요구하지 않음 | CSR:920-984; RFC 5280 §4.2.1.3 |
| Extended Key Usage | `2.5.29.37` | `false` | `SEQUENCE OF OBJECT IDENTIFIER`: `1.3.6.1.4.1.62558.2.1`을 포함하고, `1.3.6.1.5.5.7.3.4` 또는 `1.2.840.113583.1.1.5` 중 최소 하나를 포함 | CSR:985-1049; MIB:34-37; RFC 5280 §4.2.1.12 |
| Certificate Policies | `2.5.29.32` | `false` | `SEQUENCE OF PolicyInformation`; 적어도 하나의 `policyIdentifier OBJECT IDENTIFIER = 1.3.6.1.4.1.62558.1.1` | CSR:1050-1091; RFC 5280 §4.2.1.4 |
| C2PA AL | `1.3.6.1.4.1.62558.3` | `false` | **OBJECT IDENTIFIER** 값: AL1 `1.3.6.1.4.1.62558.3.10`, AL2 `1.3.6.1.4.1.62558.3.20`. 문자열이나 INTEGER 1/2가 아님 | CSR:1092-1134; MIB:39-44 |
| CPL Record | `1.3.6.1.4.1.62558.4` | `false` | **UTF8String**, 길이 36의 authoritative CPL UUID와 exact match; body `cplRecordId`와 동일 record | CSR:1135-1179; MIB:46-48 |
| AIA — CSR에서는 선택 | `1.3.6.1.5.5.7.1.1` | `false` | `SEQUENCE OF AccessDescription`; 각 항목에 `accessMethod OBJECT IDENTIFIER`와 `accessLocation GeneralName` 필수. 이 CSR schema는 URI 선택의 값이 `^http://.+`와 일치하도록 요구 | CSR:1188-1257; RFC 5280 §4.2.2.1 |
| CDP — CSR에서는 선택 | `2.5.29.31` | `false` | `SEQUENCE OF DistributionPoint`; schema가 요구하는 `distributionPoint.fullName`의 URI가 `^http://.+`와 일치 | CSR:1258-1336; RFC 5280 §4.2.1.13 |

이 표의 `documentSigning`은 고정 CSR schema가 이름 붙인 **`1.2.840.113583.1.1.5`**다. 라이브러리의 다른 동명 OID로 치환하지 않는다. CSR의 선택 AIA에는 특정 OCSP `accessMethod`를 필수화하지 않는다. 반면 **최종 certificate**는 §4에 따라 OCSP AIA가 필수이며 `id-ad-ocsp=1.3.6.1.5.5.7.48.1`을 사용한다. 권고 `caIssuers`의 OID는 `1.3.6.1.5.5.7.48.2`다. CSR이 요청한 URI를 그대로 최종 certificate에 복사하지 않는다.

### 3.4 SPKI 타입·OID와 parameters

`SubjectPublicKeyInfo`는 필수 `algorithm AlgorithmIdentifier`와 `subjectPublicKey BIT STRING`으로 이루어진다. 아래 encoding 규칙은 알고리즘을 선택한 경우의 고정 조건이고, 운영에서 이들 중 어떤 조합을 지원할지는 별도 `OD-ALG-01 TBD`다.

| key family | `algorithm.algorithm` | `algorithm.parameters` | `subjectPublicKey` 내용 및 일치 조건 |
|---|---|---|---|
| RSA | `1.2.840.113549.1.1.1` (`rsaEncryption`) | **ASN.1 NULL 필수** | DER `RSAPublicKey SEQUENCE { modulus INTEGER, publicExponent INTEGER }`; modulus ≥2048 bits. 이 두 INTEGER를 생략하거나 JSON 값으로 대체하지 않음 |
| EC | `1.2.840.10045.2.1` (`id-ecPublicKey`) | **namedCurve OBJECT IDENTIFIER 필수**: P-256 `1.2.840.10045.3.1.7`, P-384 `1.3.132.0.34`, P-521 `1.3.132.0.35` | BIT STRING 내용은 EC point bytes이며 OCTET STRING TLV로 한 번 더 감싸지 않음. curve/point/key size가 일치해야 함; RFC는 uncompressed 지원 필수, compressed 선택, hybrid 금지 |
| Ed25519 | `1.3.101.112` | **absent**; NULL도 거부 | BIT STRING 내용은 public-key byte stream; 다른 EdDSA curve는 이 CSR profile에 없음 |

근거: AL1/AL2 CSR:758-866; [RFC 3279 §2.3.1](https://www.rfc-editor.org/rfc/rfc3279.html#section-2.3.1), [RFC 5480 §2.1.1·§2.2](https://www.rfc-editor.org/rfc/rfc5480.html#section-2.1.1), [RFC 8410 §3·§4](https://www.rfc-editor.org/rfc/rfc8410.html#section-3). Android key profile의 RSA/EC 및 크기·curve 제한은 §13.2와 추가 교집합을 취한다. RSA exponent의 운영 허용값, CSR signature의 RSA-PSS parameters 등 알고리즘별 상세 allowlist는 `OD-ALG-01` 승인 전 임의 default로 활성화하지 않는다.

## 4. 최종 Claim Signing Leaf profile

| field / extension | AL1 | AL2 | authority / locator |
|---|---|---|---|
| Version | v3 | v3 | CP:1211-1213,1276-1278 |
| Serial | positive integer, high entropy recommended, max 20 octets | same | CP:1213,1278 |
| certificate signature algorithm | RSA PSS/SHA2 variants, ECDSA SHA2 variants, or Ed25519 in leaf profile | same | CP:1214,1279 |
| Issuer | Claim Signing Issuing CA Subject | same | CP:1215,1280 |
| validity | ≤366 days | ≤90 days | CP:1216,1281 |
| Subject | exact CPL product DN; C/O/CN required | same | CP:1217,1282; CP:387-395 |
| SPKI | RSA≥2048, EC P-256/384/521, Ed25519 | same | CP:1218-1222,1283-1287 |
| SKI | MUST, non-critical, RFC 5280 method 1 | same | CP:1224-1228,1289-1293 |
| AKI | MUST, non-critical, issuer SKI keyIdentifier | same | CP:1229-1232,1294-1297 |
| KU | MUST, critical; digitalSignature + nonRepudiation/contentCommitment | same | CP:1233-1236,1298-1301 |
| Basic Constraints | MUST, critical, cA=false | same | CP:1237-1240,1302-1305 |
| EKU | MUST, non-critical; c2pa-kp-claimSigning + emailProtection or documentSigning | same | CP:1241-1244,1306-1309 |
| Certificate Policies | MUST, non-critical, C2PA CP OID; optional CA private CPS OID | same | CP:1245-1248,1310-1313 |
| AIA | MUST, non-critical; OCSP MUST; caIssuers SHOULD; accessLocation “must be HTTP URI” is `NON-BCP14-OBLIGATION` | same | CP:1249-1252,1314-1317 |
| CDP | OPTIONAL, non-critical; if present HTTP URI | same | CP:1253-1256,1318-1321 |
| `c2pa-al` | MUST, non-critical, `.3.10` | MUST, non-critical, `.3.20` | CP:1257-1261,1322-1326; MIB:39-44 |
| `c2pa-cpl-record` | MUST, non-critical, UTF8String(36) authoritative UUID | same | CP:1262-1266,1327-1331; MIB:46-48 |

이 profile summary에서 all-caps `MUST`/`SHOULD`/`OPTIONAL`은 각각 `REQUIRED`/`RECOMMENDED`/`PERMITTED`로 분류한다. `Version`, algorithm list, validity ceiling, “Matches” 같은 constraint 문장과 lowercase “high entropy recommended”·“accessLocation must”는 CP의 BCP 14 선언상 `NON-BCP14-OBLIGATION`이며, 위 표는 대소문자를 바꾸지 않는다.

Claim Signing Issuing CA profile은 issuer SPKI와 certificate signature를 RSA/EC로 제한한다(CP:1044-1061). 따라서 leaf profile이 열어 둔 Ed25519 **certificate signature**는 현재 conforming issuer chain에서는 실현되지 않는다. Ed25519 **leaf subject key**는 허용된다. 실제 issuer signature algorithm은 RSA/ECDSA 교집합만 활성화하고 이 source 불일치는 `GAP-NORM-04`로 추적한다.

Content Credentials Specification 2.4의 Claim signature allowed list는 ES256/384/512, PS256/384/512와 Ed25519인 EdDSA다(`specifications@9c58c8c:build/site/specifications/2.4/specs/C2PA_Specification.html:4071-4141`). Certificate의 issuer signature algorithm, CSR outer signature algorithm과 runtime Claim COSE algorithm은 서로 다른 선택이다. `OD-ALG-01`은 이 세 교집합/매핑을 각각 고정한다.

Claim certificate에는 mandatory OCSP AIA가 있으며 CP는 Claim certificates의 OCSP status를 record-keeping 기간까지 제공하도록 요구한다. CRL은 Claim에 의무가 아니고 추가 제공할 수 있다(CP:605-609). AIA/CDP URI와 실제 responder readiness가 없으면 issuance를 시작하지 않는다.

## 5. AL1 semantic evidence

AL1의 issuance Dynamic Evidence table은 O.1에서 CA가 SCEP/EST/ACME/client certificate 등 certificate enrollment에 일반적으로 쓰이는 authentication method로 요청 entity가 Subscriber의 Generator Product instance인지 확인하라고 한다. O.2~O.6은 `No stipulation`이다(CP:1686-1695).

GSPR O.1 AL1은 GP TOE가 CA의 secure authentication method를 구현하고, Edge binary가 authentication secret을 포함하지 않으며, Applicant가 process/secret management/triggers를 GPSA에 기록하도록 한다. Dynamic Evidence는 GP instance가 secure credential로 CA에 인증하는 것이다(GSPR:332-358).

분류:

| item | timing | authority / modality | evidence cardinality | enforcement |
|---|---|---|---:|---|
| Authorization/mTLS 등 secure credential | `WIRE` | `C2PA REQUIRED`, AL1 | request transport에 `1`; body에는 secret `0` | credential 검증 + issuance currentness |
| GP instance authentication verdict | `ISSUANCE-GATE` | `C2PA REQUIRED`, AL1 | server verdict `1` | Subscriber+CPL product+request context에 명시 결속 |
| hardware provider artifact | 없음 | C2PA AL1은 artifact 수를 정하지 않음 | provider `NOT-SPECIFIED`, project JSON `0` | `evidenceItems` present 시 project contract로 거부 |
| GPSA process/secret/trigger description | `ONBOARDING` | `C2PA requirement text`, AL1/2 | static document, request-body cardinality `0` | Conformance assessment; CA는 current approval 참조 |
| Edge binary secret exclusion | `RUNTIME` | `C2PA requirement text`, Edge | runtime control, request-body cardinality `0` | product conformance/test |

일반 Subscriber login만으로 GP instance 판정을 암묵적으로 대신하지 않는다. 같은 credential mechanism을 사용할 수는 있지만 verdict는 principal+Subscriber+CPL product+현재 enrollment request scope에 결속해 별도 기록한다.

## 6. AL2 semantic Dynamic Evidence

AL2는 AL1 요구에 추가되며, 한 artifact로 모두 증명해야 한다거나 네 artifact가 필요하다고 C2PA는 말하지 않는다. semantic predicate와 transport count를 분리한다.

| objective | C2PA issuance predicate | required signed/verified meaning | provider artifact count | project wire |
|---|---|---|---|---|
| O.1 | entity가 Subscriber GP instance임을 hardware-backed artifact로 확인 | package name/hash/code-signing certificate/other certificate 또는 조합이 current product reference와 일치 | `NOT-SPECIFIED`; selected profile `PROVIDER-PROFILE-DEFINED` | 전체 O.1~O.4 묶음에서 `1..N_p` |
| O.2 | requested key가 hardware-backed keystore/KMS에서 생성·보관되고 GP instance가 possession함을 확인 | key origin/storage/security attributes, possession, CSR SPKI binding | same | same array |
| O.3 | integrated Claim Generator platform의 authenticated boot/image와 patch/revision 적격성 | secure boot/authenticated image; critical/high mitigation; chosen ≤90-day patch-recency 또는 good-standing revision | same | same array |
| O.4 | Digital Content/assertion 처리·수정 software 전체의 authenticated image와 patch/revision 적격성 | in-scope component coverage, authenticated image; critical/high mitigation; chosen patch/revision rule | same | same array |
| O.5 | CP enrollment table `No stipulation` | 없음; GSPR runtime/static 의무는 별도 | `NOT-SPECIFIED`; O.5만을 위한 artifact 의무 없음 | O.5는 mandatory semantic coverage/item 수를 늘리지 않음 |
| O.6 | CP enrollment table `No stipulation` | 없음; class-conditional runtime/static 의무는 별도 | `NOT-SPECIFIED`; O.6만을 위한 artifact 의무 없음 | O.6는 mandatory semantic coverage/item 수를 늘리지 않음 |

근거: CP:1712-1759; GSPR:360-376,422-472,498-556,572-636. `artifact(s)`의 복수형은 wire `1..N`의 규범 근거가 아니다. `1..N_p`는 여러 provider artifact를 한 request body에 담기 위한 `PROJECT` container choice다.

한 evidence item이 여러 objective를 cover할 수 있고 한 objective가 여러 item을 필요로 할 수도 있다. Server는 request의 `covers` label이 아니라 verified claim→semantic predicate mapping을 승인 provider profile에서 계산하며, O.1/O.2/O.3/O.4 verdict가 각각 `PASS`일 때만 합성 `AL2_PASS`를 만든다.

선택한 Android provider에는 CP:1770-1816의 구체적인 필드 가이드가 이미 있다. [Android Key Attestation 상세](#android-key-attestation)는 이 매핑과 Google/AOSP 검증 규칙을 함께 정의한다. 공통 Evidence wrapper가 없다는 사실을 Android 필드 매핑도 없다는 뜻으로 해석하지 않는다.

## 7. GSPR O.1~O.6: implementation/static/dynamic/runtime 경계

| objective / level / class | implementation requirement 요약 | Static Evidence | Dynamic Evidence | enrollment gate와 runtime 경계 |
|---|---|---|---|---|
| O.1 AL1 / automated, all; Edge 추가 | CA secure auth 구현; Edge binary에 auth secret 금지 | enrollment/renewal trigger, auth/secret design; method application 또는 허용된 90일 update | secure credential로 CA 인증 | AL1 enrollment gate; secret storage는 runtime/conformance |
| O.1 AL2 / all | AL1 + RoT-backed GP binary identity artifact capability | binary identity artifact method | CA에 hardware-backed artifact 제시 | CP AL2 O.1 gate |
| O.2 AL1 / all; Distributed/Backend 추가 | key encryption, least privilege/time-bound access, rotation; subsystem mutual auth와 valid Edge 확인 | access/encryption/plaintext handling/rotation; distributed/backend mutual auth | `No stipulation` | runtime/static; enrollment에는 PoP만, AL2로 전이 금지 |
| O.2 AL2 / all | higher-privilege key environment, caller restriction, raw key sequestration, hardware-derived wrapping, artifact capability **or** accredited auditor certification; distributed/backend counterpart attestation/runtime denial | KME/security/rotation; class-specific artifact method | RoT-backed artifact confirming requested private-key possession | CP/GSPR Dynamic section 때문에 auditor alternative만으로 AL2 enrollment artifact를 대체하지 못함; `GAP-NORM-02` |
| O.3 AL1 / all | Claim Generator SCA/SBOM; critical/high fix/mitigate within 90 days | tool와 release-prevention process | `No stipulation` | runtime/static only |
| O.3 AL2 / all | countermeasures, static analysis, privileged access/image auth where available, patch-recency or revision method, external input controls | build/test/tools/access/image/input 및 chosen patch/revision method | chosen patch-recency 또는 allowed revision hardware artifact | CP AL2 O.3 gate + ongoing runtime |
| O.4 AL1 / all in-scope software | content/assertion-processing software SCA/SBOM 및 critical/high 90-day mitigation | 별도 Static Evidence heading이 원문에 없음: `NOT-SPECIFIED` | 별도 Dynamic heading 없음: `NOT-SPECIFIED` | implementation/runtime; AL2 artifact로 전이 금지 |
| O.4 AL2 / all in-scope software | countermeasures/static analysis/image auth, RoT artifacts, patch/revision, process/IPC/memory protection | image/patch method, build/test/tools, isolation/IPC evidence | 모든 in-scope software image auth + chosen patch/revision artifact | CP AL2 O.4 gate + runtime |
| O.5 AL1 / Distributed+Backend | subsystem channels TLS 1.3+ or equivalent | protocol/version documentation | `No stipulation` | runtime/static; CP issuance table에도 없음 |
| O.5 AL2 / Edge+Distributed+Backend | kernel/OS process/thread isolation and IPC protection | isolation/UID/account/ACL evidence | `No stipulation` | all three implementation classes의 runtime/static; request-body Evidence로 요구하지 않음 |
| O.6 AL1 / Distributed+Backend only | IAM RBAC, dependency/interface review, timely fixes, countermeasures/OS patch | IAM/policy/scanning/mitigation descriptions | `No stipulation` | runtime/static only |
| O.6 AL2 / Distributed+Backend only | AL1 + audit monitoring, HIDS/equivalent, segmentation | design + active reports | `No stipulation` | runtime/static only |

Exact locators: GSPR O.1 `330-376`, O.2 `378-472`, O.3 `474-556`, O.4 `558-636`, O.5 `638-680`, O.6 `682-744`; general applicability and dual static/dynamic rule `324-328`. 이 general rule은 달리 제한하지 않은 요구를 Edge, Backend와 Distributed에 모두 적용한다. O.5 AL1은 Distributed/Backend로 명시적으로 제한되지만 O.5 AL2에는 그 예외가 없고, GPSA Template:327-343도 AL2 추가 evidence를 class 제한 없이 둔다. 따라서 O.5 AL2는 세 class 모두에 적용한다. 이 해석 폐쇄는 `GAP-NORM-03`에 기록한다.

## 8. Binding authority matrix

| binding | C2PA가 고정한 의미 | provider가 정할 것 | project/CA가 강제할 것 |
|---|---|---|---|
| Evidence signer/trust | CA가 verifiable hardware-backed artifact를 validate | artifact signature, chain, trust anchor/status | pinned profile/trust registry; requester root 무시; fail-closed |
| audience/verifier | 공통 field 없음 | native audience claim 또는 대체 signed binding | 이 CA/verifier audience에 결속되지 않으면 profile disabled |
| nonce/challenge | key/platform flows는 일반적으로 CA unique dynamic challenge를 쓰며, report nonce가 CA 값과 같음을 CA가 `SHALL` verify; provider 권고 준수(CP:1766-1768) | signed field, byte constraints, transform, replay semantics | server expected value와 exact compare; request body는 challenge field를 별도 정의하지 않음 |
| request context | C2PA 공통 wire field 없음 | signed challenge와 CA 보관 context의 결속, 또는 signed custom claim/envelope 지원 여부 | 현재 enrollment request/audience와 approved binding; mix-and-match 거부. Android의 생성 전 challenge와 생성 후 CSR 관계는 §13.3 |
| GP instance / Subscriber | O.1은 Subscriber GP instance를 요구 | package/hash/cert/device claim semantics | verified reference→Subscriber+CPL mapping; client text 불신 |
| requested AL / profile | issued AL≤CPL max; O.1~O.4 AL2 coverage | profile capability | body의 `certificateProfile`과 exact binding; silent downgrade 금지 |
| CSR SPKI / requested key | CA key ownership, O.2 requested key generation/storage/possession | attested-key representation | provider representation을 승인 transform으로 같은 public-key value에 결속; exact DER SPKI는 CSR PoP와 final Leaf 재확인에 사용. 발급 이력상 reuse 판정은 별도의 승인된 `keyReuseIdentity` profile만 사용하며 현재 `OD-KEY-01`은 `TBD` |
| O.3/O.4 software inventory | Claim Generator와 모든 in-scope processing software coverage | measurement/version claim | onboarding component inventory/reference version과 completeness 검증 |

CSR PoP만으로 “key가 hardware-backed/non-exportable”을 추론하지 않는다. Provider key attestation만으로 “현재 CSR을 그 key가 서명했다”를 추론하지 않는다. 두 검증의 SPKI가 일치해야 한다.

### 8.1 Key generation, boundary와 용도 분류

| obligation | timing | authority / modality / profile | wire와 gate | 지속 집행 |
|---|---|---|---|---|
| Claim key는 Subscriber 또는 GSPR이 허용한 KMS가 생성하고 CA는 생성하지 않음 | `RUNTIME` + CA `ISSUANCE-GATE` | `C2PA REQUIRED/PROHIBITED`, `BASE`; CP:815-823 | self-declared location field는 받지 않음; CSR PoP와 server가 key-generation service를 제공하지 않는 구성을 확인 | product/KMS provisioning과 CA service boundary test |
| requested private key ownership/PoP | `WIRE` + `ISSUANCE-GATE` | `RFC` + `C2PA REQUIRED`, `BASE`; RFC 2986 §3/§4.2, CP:471-473 | PKCS#10 DER `1`; every INITIAL/REKEY에서 signature verify | issuance 뒤 key property의 지속성까지 증명하지 않음 |
| private key exclusive control, no export/share, Claim-only use | `RUNTIME` | `C2PA REQUIRED/PROHIBITED`, `BASE`; CP:537,563-565,815-823 | AL1에서 이를 위한 provider artifact를 임의로 wire에 요구하지 않음 | GP secure boundary, least privilege, misuse monitoring과 revocation |
| AL1 persistent-key encryption/access/rotation | `RUNTIME` + static conformance | `C2PA requirement text`, `AL1`; GSPR:378-420 | provider artifact count `NOT-SPECIFIED`, project `evidenceItems=0`; enrollment은 PoP/instance auth만 | implementation class별 key store/access/rotation control |
| AL2 privileged hardware-backed keystore/KMS generation/storage/possession | `RUNTIME` + `ISSUANCE-GATE` | `C2PA REQUIRED`, `AL2`; CP:1716-1718, GSPR:422-472 | provider artifact(s)가 project `evidenceItems=1..N_p`로 WIRE에 오고, verified key representation이 CSR SPKI와 같아야 함 | raw key sequestration, authenticated caller와 KME policy를 계속 강제 |

따라서 “non-exportable” 또는 “hardware Root of Trust”는 모든 AL의 client boolean field가 아니다. AL2에서는 verified Dynamic Evidence의 semantic predicate이고, AL1에서는 GSPR/static/runtime 통제로 확인하되 request-body hardware Evidence gate로 승격하지 않는다.

## 9. Freshness와 replay

| operation / AL | C2PA requirement | provider count | project rule |
|---|---|---|---|
| INITIAL / AL1 | secure credential/instance auth와 PoP | `NOT-SPECIFIED`; artifact 의무 없음 | project `evidenceItems=0`; current credential/approval, new key history check |
| REKEY / AL1 | 신규 신청과 같은 issuance auth/PoP | `NOT-SPECIFIED`; artifact 의무 없음 | project `evidenceItems=0`; new key/CSR, stored I/A/V currentness |
| INITIAL / AL2 | issuance에서 required Dynamic Evidence request+verify | `PROVIDER-PROFILE-DEFINED` | request-bound Evidence; provider freshness predicate |
| REKEY / AL2 | re-key는 신규 신청처럼 처리하고 issuance Dynamic Evidence 적용 | `PROVIDER-PROFILE-DEFINED` | 새 request; challenge flow면 fresh challenge; new-key Evidence |
| RENEWAL / either | same-key renewal prohibited | `0` | request body를 처리하지 않음 |

C2PA는 모든 provider에 공통인 seconds/minutes TTL, timestamp field 또는 artifact 재사용 횟수를 정하지 않는다. 그러나 challenge flow에서는 unique dynamic challenge와 exact-match가 있어야 한다. 이 프로젝트는 AL2 profile 승인의 조건으로 `(provider-native signed freshness 또는 trusted freshness를 제공하는 승인된 signed envelope) AND request-context·audience·subject-key binding AND replay identity`를 요구한다. 새 envelope가 stale underlying attestation에 서명만 다시 한 경우에는 freshness를 충족하지 않는다. 이 조건을 제공하지 못하는 profile은 비활성화한다. Client clock은 freshness authority가 아니다.

## 10. Lifecycle, migration과 revocation

| question | source conclusion | project contract |
|---|---|---|
| renewal | same key renewal prohibited; previously issued key에 새 cert 발급 금지(CP:573-575) | `RENEWAL` request body를 지원하지 않음 |
| re-key | issuance authentication과 key ownership/PoP는 새 신청과 동일(CP:479-481,577-579); initial 조직/대표자 I/A/V 원자료의 매회 재수집은 명시하지 않고 398일 re-auth rule이 별도 적용 | new key+CSR, current reusable I/A/V와 all gates; predecessor reference required |
| same public-key reuse | prohibited by CP | 승인된 `keyReuseIdentity` profile에 따른 global Claim/TSA issuance-history 판정만 허용; 현재 profile이 없으므로 `OD-KEY-01`은 `TBD`이고 모든 issuance가 비활성. Exact DER/SPKI hash는 PoP·동일 request 비교·진단용이지 cross-encoding reuse authority가 아님 |
| old/new simultaneous validity | CP does not specify | `OD-LIFECYCLE-01`; until approved REKEY disabled |
| automatic revocation on re-key | CP does not specify | no implicit revocation; approved cutover/incident policy required |
| revocation triggers | revoked* CPL status, authenticated C2PA/Subscriber request, compromise/attestation failure, key exposure, CP noncompliance, misuse(CP:587-603) | dependency index, incident workflow, authenticated request ≤72h(CP:483-485) |
| AL2 failure downgrade | CA `MAY` evaluate next-lower AL(CP:529) | no silent downgrade; 별도의 명시적 AL1 request |
| AL1→AL2 upgrade | no lifecycle protocol specified | new-key REKEY with AL2 profile and Evidence; never mutate cert |
| AL2→AL1 migration | lower certificate allowed if ≤max, but protocol unspecified | new-key explicit AL1 REKEY; AL2 artifact absent |
| provider migration | not specified | new-key REKEY with newly approved profile/evidence; existing cert status remains separate unless revocation trigger |

Certificate issuance eligibility, X.509 status와 runtime key authorization/activation은 독립 조건이다. Claim Leaf 발급 성공이 product runtime이 key-use ACL, patching, O.5/O.6 또는 current status refresh를 계속 지킨다는 자동 증명이 아니다.

## 11. Static, onboarding, issuance, runtime evidence map

| artifact/state | owner | request body에 제출? | request/issuance가 확인할 것 |
|---|---|---:|---|
| legal identity/representative verification | CA/RA onboarding | 아니오 | approval active, re-auth age≤398 days, exact Subscriber binding |
| Subscriber Agreement / terms | CA onboarding | 아니오 | current accepted version/status |
| signed Notice/CPL record | C2PA/CA registry | record ID만 wire | signature/source/current status, product type, DN, max AL, methods |
| GPSA/static GSPR evidence | Applicant/Conformance Program | 아니오 | current conformance approval 참조; CA가 raw GPSA를 매 호출 재평가하지 않음 |
| CSR | GP instance | 예, INITIAL/REKEY마다 | strict DER/profile/PoP/SPKI/new key |
| AL1 credential authentication | GP instance/CA | transport credential | current request의 instance verdict |
| AL2 Dynamic Evidence | GP/provider | 예, `1..N_p` | provider trust/freshness/binding와 semantic O.1~O.4 |
| product runtime controls | GP TOE | 아니오 | Conformance/monitoring/audit; incident/status가 issuance eligibility에 반영 |
| final TBS/Leaf | CA/HSM | server-generated | official schema, authoritative DN/AL/CPL/SPKI, status service readiness |

## 12. 구현자가 추측해서는 안 되는 값

다음은 원문이 제공하는 가이드를 적용하기 위해 CA가 구체화해야 하는 운영값이다. [Operations Decision Register](03-Server-Validation-Traceability-and-Gaps.md#6-operations-decision-register)의 해당 결정이 `APPROVED`일 때만 운영에 사용한다. Android의 원문 필드·태그·값 가이드는 이미 존재하며 §13에 분리해 기록한다.

- concrete credential/TLS profile, algorithm subset과 CSR outer signature policy
- profile 상한 이하 실제 validity, serial policy, AIA/CDP/CPS OID
- CPL/Notice refresh/conflict policy와 `minVersion` 비교
- provider schema의 지원 버전·암호 subset, artifact 포장/count와 trust/status 운영값; Android §13 매핑에 대입할 제품별 reference와 O.3/O.4 coverage
- challenge length/entropy/TTL/transform/consumption 또는 challenge 없는 provider freshness
- Evidence/CSR/audit retention
- re-key overlap/cutover, AL/provider migration과 incident/revocation playbook

미승인값에 임의 default를 적용하는 대신 영향 profile을 비활성화한다.

<a id="android-key-attestation"></a>

## 13. Android Key Attestation

### 13.1 선택 범위와 근거

2026-09-11 사용자 선택에 따라 AL2 provider는 **Google 신뢰 루트로 검증하는 Android Key Attestation**이다. 대상 artifact는 Android가 생성한 X.509 attestation certificate와 그 체인이며, 검증할 확장은 OID `1.3.6.1.4.1.11129.2.1.17`이다. 발급할 C2PA Claim Signing Leaf와 제출된 Android attestation certificate는 별개다. 이 확장을 C2PA Leaf에 복사하라는 요구가 아니다.

- `C2PA`: 고정 CP:1770-1774가 Android의 O.1~O.4 지원 범위를 설명하고, CP:1794-1816이 AL2 필드·값 가이드를 제공한다. 아래 표는 그 21개 행을 모두 추적한다. `Guidance on Values`의 서술값을 임의로 새 BCP 14 `MUST`로 바꾸지 않는다. 상위 발급 의무는 CP:1712-1751,1766에 따른다.
- `PROVIDER`: [Google 검증 절차](https://developer.android.com/privacy-and-security/security-key-attestation#verifying), [신뢰 루트](https://developer.android.com/privacy-and-security/security-key-attestation#root_certificate), [폐기 상태](https://developer.android.com/privacy-and-security/security-key-attestation#certificate_status), [AOSP ASN.1 schema](https://source.android.com/docs/security/features/keystore/attestation#schema)가 실제 parser·체인·필드 의미의 근거다. Exact-byte identity는 README §6의 2026-09-04 사본을 유지하며 2026-09-11 원격 원문과 해당 규칙을 재대조했다.
- `PROJECT/CA-CPS`: 지원 schema/version, trust 갱신·상태 정책, 제품 기준값, 패치 경계·시간대, nonce TTL과 허용 artifact 조합은 운영 profile에서 확정한다. Provider 선택 및 매핑 보강으로 이 결정들이 자동 승인되지는 않는다. `OD-EVIDENCE-01`, `OD-FRESHNESS-01`, `OD-REFERENCE-01`은 운영 승인 `TBD`를 유지한다.

AL1의 Android 가이드는 `No stipulation`이다(CP:1786-1788). 이 절은 AL2에만 적용하며 AL1의 `evidenceItems` 필드 금지는 유지한다.

<a id="android-field-mapping"></a>

### 13.2 CP의 21개 필드 매핑

표의 `SW`는 `softwareEnforced`, `HW`는 `hardwareEnforced`다. 모든 경로는 §13.3에 따라 선택·검증한 인증서의 `.17` 확장 내부이며, `CP 분류`는 원문의 목표 표기를 보존한다. 값 존재만으로 목표 전체를 PASS 처리하지 않고 §13.4의 판정을 함께 적용한다.

| ID | CP 분류 | 확장 필드 / ASN.1 태그 | CP의 값 가이드와 검증 의미 | 원문 |
|---|---|---|---|---|
| `AK-01` | O.3, O.4 | `attestationSecurityLevel` | `TrustedEnvironment(1)` 또는 `StrongBox(2)` | CP:1796 |
| `AK-02` | O.3, O.4 | `keyMintSecurityLevel` | `TrustedEnvironment(1)` 또는 `StrongBox(2)`; 구버전 명칭은 아래 참조 | CP:1797 |
| `AK-03` | O.1, O.2, O.3, O.4 | `attestationChallenge` | CA가 발급해 보관한 challenge bytes와 exact match | CP:1798 |
| `AK-04` | O.1 | SW.`attestationApplicationId` `[709]` → `package_infos` → `package_name` | CA에 등록된 GP 앱 패키지명과 일치 | CP:1799 |
| `AK-05` | O.1 | SW.`attestationApplicationId` `[709]` → `package_infos` → `version` | CA에 등록된 허용 앱 버전 중 하나 | CP:1800 |
| `AK-06` | O.1 | SW.`attestationApplicationId` `[709]` → `signature_digests` | 등록한 앱 서명 인증서의 SHA-256 digest와 일치 | CP:1801 |
| `AK-07` | Claim Signing profile | HW.`purpose` `[1]` | 집합에 `SIGN(2)` 포함 | CP:1802 |
| `AK-08` | Claim Signing profile | HW.`algorithm` `[2]` | `RSA(1)` 또는 `EC(3)` | CP:1803 |
| `AK-09` | Claim Signing profile | HW.`keySize` `[3]` | RSA: `2048/3072/4096`; EC: `256/384/521` | CP:1804 |
| `AK-10` | Claim Signing profile | HW.`digest` `[5]` | 비어 있지 않은 집합, 원소는 SHA-2 `256(4)/384(5)/512(6)` 범위; 세 값 전부 포함할 의무는 없음. 실제 사용 조합은 `OD-ALG-01` | CP:1805 |
| `AK-11` | Claim Signing profile | HW.`padding` `[6]` | RSA에 적용: 집합에 `RSA_PSS(3)` 포함. scalar `3`으로 파싱하지 않음 | CP:1806 |
| `AK-12` | Claim Signing profile | HW.`ecCurve` `[10]` | EC에 적용: `P_256(1)/P_384(2)/P_521(3)`이며 `keySize`와 일치 | CP:1807 |
| `AK-13` | O.2 | HW.`origin` `[702]` | `GENERATED(0)` | CP:1808 |
| `AK-14` | O.4 | HW.`rootOfTrust` `[704]` → `deviceLocked` | `true` | CP:1809 |
| `AK-15` | O.4 | HW.`rootOfTrust` `[704]` → `verifiedBootState` | `Verified(0)` | CP:1810 |
| `AK-16` | O.4 | HW.`osPatchLevel` `[706]` | 유효한 `YYYYMM`, 미래 월 불가; CP의 월 기준과 예시 차이는 아래에 보존 | CP:1811 |
| `AK-17` | O.1 조건부 | HW.`attestationIdBrand` `[710]` | 제품에 특정 OEM brand 제한이 있을 때 등록값과 일치 | CP:1812 |
| `AK-18` | O.1 조건부 | HW.`attestationIdManufacturer` `[716]` | 제품에 특정 OEM brand 제한이 있을 때 등록값과 일치 | CP:1813 |
| `AK-19` | O.1 조건부 | HW.`attestationIdModel` `[717]` | 제품에 특정 모델 제한이 있을 때 등록값과 일치 | CP:1814 |
| `AK-20` | O.4 | HW.`vendorPatchLevel` `[718]` | 유효한 `YYYYMMDD`, CSR 제출일과의 차이가 `0..90`일(양끝 포함) | CP:1815 |
| `AK-21` | O.4 | HW.`bootPatchLevel` `[719]` | 유효한 `YYYYMMDD`, CSR 제출일과의 차이가 `0..90`일(양끝 포함); CP 태그 오기는 아래 참조 | CP:1816 |

원문 차이와 구현 시 해석은 다음처럼 처리한다.

1. **태그·이름 정정 (`PROVIDER`)**: CP:1816의 `bootPatchLevel [718]`은 [AOSP schema](https://source.android.com/docs/security/features/keystore/attestation#schema)의 `[719]`와 다르다. `[718]`은 vendor 필드이며 boot 필드에 중복 사용하지 않는다. CP의 `attestationApplicationID`는 AOSP 명칭 `attestationApplicationId`로 표기했다. ASN.1에서 필드 문자열이 전송된다고 가정하지 않는다.
2. **버전 (`PROVIDER/PROJECT`)**: `attestationVersion`으로 지원 schema를 선택한다. Keymaster 계열의 `keymasterVersion/keymasterSecurityLevel`과 KeyMint 계열의 대응 필드는 승인된 버전별 parser에서 공통 의미로 매핑한다. 정확한 필수 member·타입·버전 쌍은 [§13.6](#android-asn1-input)에 있다. 미지원 버전·타입, duplicate tag, parser ambiguity는 거부하며, ASN.1 `OPTIONAL`이라는 이유로 이 profile에서 필요한 증거 부재를 PASS로 바꾸지 않는다. OEM 제한 필드와 RSA/EC 조건부 필드는 적용 조건을 먼저 확인한다. 근거: [AOSP KeyDescription/AuthorizationList](https://source.android.com/docs/security/features/keystore/attestation#keydescription-fields).
3. **OS 월 경계 (`C2PA` 가이드 + `PROJECT` 해석안)**: CP:1811은 4개월 이내라는 표현과 함께 2026년 8월 요청에서 `202608/202607/202606/202605`를 허용하는 예시를 제시한다. 예시를 따르는 보수적 해석안은 제출 월과 직전 3개월, 즉 월 차이 `0..3`이다. 이를 원문에 명시된 수식으로 주장하지 않는다. `OD-REFERENCE-01`에서 이 해석과 CA가 기록한 CSR 제출일의 시간대를 확정하기 전에는 운영 적용하지 않는다. vendor/boot의 일 단위 `0..90`과 서로 바꾸거나 OS 월 값을 임의의 일자로 보정하지 않는다. AOSP의 OS patch 우선 권고가 CP의 vendor/boot 행을 제거하지 않는다.
4. **암호 조합 (`C2PA/CA-CPS`)**: `AK-07..AK-12`는 별도의 Claim Signing profile 제약이며 O.1~O.4 자체로 재분류하지 않는다. 허용 key 목적·digest·padding 집합, CSR signature와 실제 Claim COSE 알고리즘의 조합을 `OD-ALG-01`에서 고정하고 CSR SPKI와 대조한다. 일반 C2PA Leaf가 Ed25519를 허용해도 이 Android 가이드의 RSA/EC 범위를 자동 확장하지 않는다.

<a id="android-verification"></a>

### 13.3 확장 검증의 전제와 요청 결속

다음은 `SG-04`, `SG-06`, `SG-08`이 함께 집행할 검증 조건이며 REST API나 transaction state를 정의하지 않는다.

1. **신뢰와 상태**: 별도 서버에서 체인 서명을 검증하고 Google의 공식 신뢰 루트 집합에 연결한다. 제출 root의 이름이나 자체 서명만으로 신뢰하지 않는다. 공식 [root registry](https://developer.android.com/privacy-and-security/security-key-attestation#root_certificate)와 [status list](https://developer.android.com/privacy-and-security/security-key-attestation#certificate_status)를 사용하며, 체인 각 인증서의 `REVOKED/SUSPENDED`를 거부한다. 유효한 최신 status list에 항목이 없는 경우와 조회 실패·오래된 캐시를 구분한다. Root 교체, status `Cache-Control` 및 장애 시 freshness 정책은 `OD-EVIDENCE-01/OD-REVOCATION-01`에 속한다.
2. **인증서 선택**: [Google 절차](https://developer.android.com/privacy-and-security/security-key-attestation#verifying)에 따라 검증된 경로를 루트에서 대상 방향으로 살펴 **처음 만나는 `.17` 확장**을 선택한다. CP 표의 일괄 `Leaf certificate` 경로를 무조건 배열의 첫/마지막 원소 선택으로 구현하지 않는다. `.30` provisioning information 확장이 존재하면 루트에 가장 가까운 해당 확장을 확인하고, `.17` 확장이 그 바로 다음 인증서에 있는지 검사한다. 공격자가 아래에 덧붙인 인증서의 추가 `.17` 확장은 신뢰하지 않는다.
3. **증명된 키**: 선택한 `.17` 확장을 담은 인증서의 SubjectPublicKeyInfo가 증명 대상 키다. 그 공개키와 CSR SPKI가 같은 공개키인지 승인된 algorithm/encoding 규칙으로 확인하고, CSR signature/PoP를 별도로 검증한다. Attestation 서명자의 공개키나 제출된 다른 leaf의 키로 대신 비교하지 않는다. [Android body 결속](01-Enrollment-Request-Body.md#android-evidence-body)의 `value`가 이 선택된 인증서가 아니면 거부한다.
4. **유효기간 구분**: Google의 [expired factory keys 가이드](https://developer.android.com/privacy-and-security/security-key-attestation#expired_factory_keys)는 특정 legacy factory chain에 예외를 설명하지만 RKP certificate의 유효기간 검사는 계속 요구한다. 예외를 도입한다면 검증된 root identity와 provisioning 분류로 범위를 고정하고 status 검증을 유지한다. Subject 문자열만으로 예외를 활성화하거나 모든 Android 체인의 만료 검사를 끄지 않는다. 지원 범위와 예외 적용 여부는 `OD-EVIDENCE-01` 승인값이다.
5. **앱 정보의 신뢰**: `softwareEnforced`는 Android 플랫폼이 수집한 값이며 hardware가 직접 측정한 값으로 재분류하지 않는다. [AOSP](https://source.android.com/docs/security/features/keystore/attestation#keydescription-fields)는 이 값의 신뢰 전제로 locked bootloader와 `Verified` boot를 설명한다. 따라서 `AK-14/AK-15` 및 검증된 hardware attestation을 전제로 `AK-04..AK-06`을 사용한다. Shared UID이면 [복수 package](https://source.android.com/docs/security/features/keystore/attestation#attestationapplicationid-schema)가 포함될 수 있으므로 전체 package/version·signer 집합을 승인된 조합과 비교한다. 일치하는 원소 하나로 미등록 package나 signer를 덮지 않는다. `signature_digests`는 앱 **서명 인증서**의 SHA-256이며 APK 전체나 앱 signature bytes의 hash가 아니다. Package 정보만으로 사용자·조직·유일한 기기 instance를 식별했다고 가정하지 않고, credential 및 CA의 Subscriber/CPL 결속도 확인한다.
6. **Challenge의 생성 시점**: Android [setAttestationChallenge](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder#setAttestationChallenge(byte[]))는 키 생성 시 challenge를 넣으며 provider 상한은 128 bytes다. 의존 관계는 CA challenge → 그 challenge를 넣어 새 attested key 생성 → 같은 키로 CSR 서명이다. CA는 challenge에 현재 인증 주체·Subscriber·CPL·요청 AL·이 CA의 요청 범위를 결속해 보관하고, 이후 검증한 증명키와 CSR 키를 그 범위에 연결한다. 생성 전 challenge에 아직 없는 CSR hash를 반드시 포함시키는 순환 조건은 만들지 않는다. Android에 공통 `audience` 필드가 있다고 가정하지 않는다. 이러한 CA context 결속은 `PROJECT` 방식이며 길이·엔트로피·TTL·재사용 방지 기준은 `OD-FRESHNESS-01`에서 확정한다. 빈/고정 challenge, 다른 요청의 challenge, 만료·재사용 증거는 허용하지 않는다. 새로운 envelope 서명만으로 과거 attestation을 최신 상태로 만들지 않는다.

<a id="android-coverage"></a>

### 13.4 O.1~O.4 전체 판정과 reference 경계

`AK-*`의 원문 분류와 전체 objective 판정은 같은 표가 아니다. CP는 boot/patch 세부 행을 O.4로 분류했지만 O.3 일반 요구에도 플랫폼 boot·취약점 조치·Claim Generator patch/revision 검증을 명시한다(CP:1720-1734). 따라서 `AK-01/AK-02`의 보안수준만으로 O.3를 PASS로 만들지 않는다.

| 목표 | Android 검증을 전체 발급 predicate에 연결하는 조건 | 외부 근거 / gate |
|---|---|---|
| O.1 | 검증된 app package/version/signing-certificate 집합과 조건부 OEM 기준값이 현재 등록 GP에 결속되고 현재 요청의 Subscriber/instance 인증과 모순 없음 | CP:1712-1714,1799-1801,1812-1814; `SG-01,SG-03,SG-06` |
| O.2 | 검증된 hardware security level·`origin=GENERATED`·키 속성, 증명키=CSR 키, CSR PoP를 모두 만족 | CP:1716-1718,1796-1798,1802-1808; `SG-04,SG-06` |
| O.3 | authenticated platform boot와 취약점 조치 조건을 확인하고, 검증된 앱/release 식별값이 통합 Claim Generator의 현재 승인 revision 또는 선택한 patch-recency 기준을 증명 가능하게 덮음 | CP:1720-1734,1766; `SG-06,SG-08` |
| O.4 | boot/patch 검사에 더해 검증된 release가 콘텐츠·assertion을 처리/수정하는 **모든** in-scope software의 image·취약점 조치·선택한 patch/revision 기준을 덮음 | CP:1737-1751,1766,1809-1816; `SG-06,SG-08` |

`OD-REFERENCE-01`에는 승인 package/version/signer 조합, 조건부 OEM 값, Claim Generator 및 모든 처리 component의 inventory, release→component revision 대응, 취약점 조치 상태와 reference의 갱신/철회 근거를 등록한다. 앱 버전이 동일하다는 사실만으로 외부 프로세스·별도 앱·동적 로딩 모듈의 상태까지 증명된다고 추론하지 않는다. [AOSP RootOfTrust](https://source.android.com/docs/security/features/keystore/attestation#rootoftrust-fields)의 `verifiedBootHash`도 Verified Boot 보호 대상의 digest이며 임의 GP component 전체의 hash가 아니다. 이 필드는 버전 3/4/100 이상 schema의 `RootOfTrust`에서 **구조상 필수**다(§13.6). 다만 CP Android 표에는 이 hash를 제품 등록 기준값과 직접 비교하는 행이 없으므로 모든 제품에 공통인 **expected-hash 비교 의무**를 새로 만들지는 않는다. 구조상 존재 조건과 제품별 reference 비교는 별개다.

이는 CP의 일반 O.3/O.4 요구를 Android 제품 구조에 연결하는 `PROJECT` 구현 판정이다. 검증된 artifact와 승인 reference로 전체 범위를 입증할 수 있으면 하나의 Android evidence item이 복수 objective를 지원할 수 있다. Coverage가 부족하면 해당 요청을 거부하고 제품 구조에 맞는 추가 증거 또는 검증 가능한 release binding을 정의한다. C2PA가 네 개 artifact를 요구한다고 주장하거나 미검증 client metadata로 빈 범위를 채우지 않는다.

<a id="android-vectors"></a>

### 13.5 구현 검증에 필요한 반례

다음은 향후 verifier의 수락 기준이며 이 문서 보강에서 실행된 암호 테스트를 뜻하지 않는다.

- 정상 체인·키·challenge·reference에서 각 objective를 별도 판정하고, 정상 `INITIAL/REKEY`에서 새 key 조건을 유지한다.
- 공격자가 추가한 leaf/두 번째 `.17` 확장, 신뢰하지 않는 root, 잘못된 `.30` 위치, revoked/suspended chain, 조회 실패·stale status를 거부한다. Factory 예외가 RKP 만료 우회로 전이되지 않는지 확인한다.
- 선택 인증서와 CSR의 키 불일치, 잘못된 CSR signature, `Software(0)` security level, imported origin, 잘못된 알고리즘/목적·타입·중복 태그·미지원 버전·필수 태그 누락을 거부한다.
- 미등록 package/version/signer, shared UID의 추가 미승인 package, `deviceLocked=false` 또는 unverified boot를 거부한다.
- 다른 요청·빈 값·만료·재사용 challenge와 기존 attestation의 envelope 재서명을 거부한다. Nonce TTL과 OS/vendor/boot patch age는 별도로 검증한다.
- 승인된 월 경계의 직전/직후, 일 경계 `0/90/91`일, 미래 날짜·불가능한 날짜를 확인한다. `vendorPatchLevel [718]`을 `bootPatchLevel [719]` 대신 읽지 않는다.
- Android 필드가 모두 정상이어도 Claim Generator 또는 처리 component coverage·승인 revision·취약점 조치 상태가 불명확하면 O.3/O.4 전체 PASS가 되지 않음을 확인한다.
- JSON 필수 키 누락/`null`/타입 오류, AL1의 `evidenceItems=null`, Android 빈 chain, 비정규 base64를 거부한다. CSR의 잘못된 extension OID·inner type·criticality, 복수 `extensionRequest` 값, RSA parameters 부재와 Ed25519 NULL parameters를 거부한다.
- KeyDescription 필수 member 누락·잘못된 version/HAL 쌍, 집합을 scalar로 바꾼 purpose/digest/padding, malformed AppId 내부 DER·32-byte가 아닌 signer digest를 거부한다. Version 3 이상 RootOfTrust에서 `verifiedBootHash`가 없으면 reference 비교 정책과 무관하게 거부한다. `uniqueId`의 정상 빈 OCTET STRING을 member 누락과 혼동하지 않는다.

<a id="android-asn1-input"></a>

### 13.6 Android ASN.1 입력의 필수 구조·타입

§13.2의 21행은 CP의 **의미·값 가이드**이며 완전한 ASN.1 schema 목록이 아니다. `.17` X.509 extension의 `extnValue OCTET STRING`에는 아래 `KeyDescription`의 DER가 들어간다. 바깥 인증서와 선택·신뢰 조건은 §13.3을 먼저 적용한다. 다음 구조는 [AOSP 버전별 schema](https://source.android.com/docs/security/features/keystore/attestation#schema)를 따른다.

| 순서 | KeyDescription SEQUENCE member | ASN.1 타입 | 존재·값 조건 |
|---|---|---|---|
| 1 | `attestationVersion` | `INTEGER` | 필수; 아래 version 쌍 및 승인 지원 subset과 일치 |
| 2 | `attestationSecurityLevel` | `SecurityLevel ENUMERATED` | 필수; 선택 AL2 profile에서는 `TrustedEnvironment(1)` 또는 `StrongBox(2)` |
| 3 | `keymasterVersion` / `keyMintVersion` | `INTEGER` | 필수; attestationVersion과 아래 쌍을 이룸 |
| 4 | `keymasterSecurityLevel` / `keyMintSecurityLevel` | `SecurityLevel ENUMERATED` | 필수; 선택 AL2 profile에서는 `TrustedEnvironment(1)` 또는 `StrongBox(2)` |
| 5 | `attestationChallenge` | `OCTET STRING` | 필수; CA 보관 challenge bytes와 동일한 non-empty 값, provider 최대 128 bytes; §13.3의 freshness 적용 |
| 6 | `uniqueId` | `OCTET STRING` | **member 존재는 필수**, unique ID를 요청하지 않은 경우 내용은 empty. C2PA가 새 기기 식별자 수집을 요구하는 것은 아님 |
| 7 | `softwareEnforced` | `AuthorizationList SEQUENCE` | 필수 container; 이 profile은 SW `[709]` 등 아래 조건을 추가 요구 |
| 8 | `hardwareEnforced` | `AuthorizationList SEQUENCE` | 필수 container; 이 profile은 아래 hardware 항목을 추가 요구 |

고정 원문의 `attestationVersion → Keymaster/KeyMint version INTEGER` 쌍은 `1→2`, `2→3`, `3→4`, `4→41`, `100→100`, `200→200`, `300→300`, `400→400`, `500→500`이다. 문서상의 Keymaster 4.1을 INTEGER `4.1`로 보내지 않는다. Field 이름이나 `keymint`의 대소문자는 wire 문자열이 아니며 SEQUENCE의 위치·타입으로 해석한다. 원문에 schema가 있다는 것과 운영 수락은 다르다. `OD-EVIDENCE-01`에서 지원 subset을 승인하고 미지원 버전은 거부한다. 특히 v1/v2는 이 CP 가이드에서 필요한 vendor/boot patch 필드를 제공하지 않으므로 현재 Android AL2 profile을 PASS할 수 없다.

`AuthorizationList`의 다음 태그는 모두 **context-specific EXPLICIT**이다. 아래 `필수`는 generic ASN.1의 OPTIONAL 여부가 아니라 **선택 Android AL2 profile에 필요한 위치와 증거**를 뜻한다. 동일 값이 SW에 있다는 이유로 HW 요구를 충족시키지 않는다. 배열/scalar coercion, 중복 태그 또는 버전에서 허용하지 않는 타입을 수락하지 않는다.

| 위치 / 태그 | 안쪽 ASN.1 타입 | profile 존재 조건과 값 |
|---|---|---|
| SW `attestationApplicationId [709]` | `OCTET STRING` | 필수; 내용은 아래 AppId DER. JSON/package 문자열 자체가 아님 |
| HW `purpose [1]` | `SET OF INTEGER` | 필수; `2 ∈ purpose` (`SIGN`). CP 가이드는 `SIGN`만 있어야 한다고 정하지 않음 |
| HW `algorithm [2]`, `keySize [3]` | 각각 `INTEGER` | 필수; `AK-08/AK-09`의 RSA/EC 값과 증명키·CSR SPKI 일치 |
| HW `digest [5]` | `SET OF INTEGER` | 필수; 비어 있지 않은 `{4,5,6}`의 부분집합. 세 값을 모두 요구하지 않고 활성화 algorithm과의 실제 사용 가능성도 검사 |
| HW `padding [6]` | `SET OF INTEGER` | RSA이면 필수이며 `3 ∈ padding` (`RSA_PSS`); EC에는 RSA padding 요구 없음 |
| HW `ecCurve [10]` | `INTEGER` | EC이면 필수; `1/2/3` 중 선택 curve 및 `256/384/521` bit·SPKI OID와 각각 일치 |
| HW `rsaPublicExponent [200]` | `INTEGER` | RSA의 조건부 provider 속성. KeyMint의 RSA 키는 hardware-enforced exponent가 필수이며 unsigned 64-bit 범위·provider RSA exponent 제약을 만족. 증명키와 CSR의 `publicExponent`와 같아야 함. CP 21행에 추가된 C2PA 공통 의무로 취급하지 않음 |
| HW `origin [702]` | `INTEGER` | 필수; `0` (`GENERATED`) |
| HW `rootOfTrust [704]` | `RootOfTrust SEQUENCE` | 필수; 아래 내부 구조와 `deviceLocked=true`, `verifiedBootState=0` |
| HW `osPatchLevel [706]`, `vendorPatchLevel [718]`, `bootPatchLevel [719]` | 각각 `INTEGER` | 필수; `AK-16/AK-20/AK-21`의 날짜 형식과 승인된 recency 정책. 문자형 날짜로 대체하지 않음 |
| HW `attestationIdBrand [710]`, `attestationIdManufacturer [716]`, `attestationIdModel [717]` | 각각 `OCTET STRING` | `AK-17..AK-19`의 제품 제한이 적용될 때 필수이며 등록 bytes와 일치. 모든 제품에 IMEI/serial 등 추가 ID를 요구하지 않음 |

`purpose/digest/padding`의 숫자는 **attestation의 Keymaster/KeyMint enum 값**이며 Android SDK API의 동명 bit flag로 치환하지 않는다. CP가 허용한 값 범위와 운영의 더 좁은 집합은 다르다. Purpose의 추가 원소 및 PSS 이외 padding의 허용 여부는 `OD-ALG-01`에서 provider 호환성·Claim-only runtime 정책과 함께 승인한다. 이 문서가 `purpose={2}` 또는 `padding={3}`만을 C2PA 원문 의무로 만든 것은 아니다. RSA exponent의 provider 근거는 README §6에 고정한 [AOSP KeyMint Tag.aidl의 RSA_PUBLIC_EXPONENT](https://android.googlesource.com/platform/hardware/interfaces/+/28e04e62213887d2ce572c80498b26bc3e12b709/security/keymint/aidl/android/hardware/security/keymint/Tag.aidl#161)이며, `65537` 지원 의무와 모든 제출키가 그 값이어야 한다는 조건을 혼동하지 않는다. 실제 허용 exponent는 `OD-ALG-01`에서 승인한다.

`RootOfTrust` 내부는 위치 기반 SEQUENCE다. v1/v2는 `verifiedBootKey OCTET STRING`, `deviceLocked BOOLEAN`, `verifiedBootState ENUMERATED`의 **세 필수 member**이며, v3/v4/100/200/300/400/500은 여기에 **필수 `verifiedBootHash OCTET STRING`**이 마지막으로 추가된다. `verifiedBootKey`의 구조상 존재 역시 reference-value 비교 여부와 무관하다. `VerifiedBootState`의 wire 값은 `Verified(0)`, `SelfSigned(1)`, `Unverified(2)`, `Failed(3)`이며 이 AL2 profile은 `0`만 수락한다. Boot hash를 누락해도 된다는 의미로 §13.4를 해석하지 않는다.

SW `[709]` OCTET STRING 내용의 **[AttestationApplicationId](https://source.android.com/docs/security/features/keystore/attestation#attestationapplicationid-schema) DER**는 다음 필수 중첩 구조다.

| 경로 | 타입 | 존재·검증 조건 |
|---|---|---|
| `AttestationApplicationId` | `SEQUENCE` | `package_infos`, `signature_digests` 두 member 필수 |
| `package_infos` | `SET OF AttestationPackageInfo` | 이 profile에서는 non-empty; 전체 집합이 승인 package/version 조합과 일치 |
| 각 `AttestationPackageInfo` | `SEQUENCE { package_name OCTET STRING, version INTEGER }` | 두 member 필수; 이름 bytes와 version을 등록값과 대조; 이 version은 KeyDescription schema version이 아님 |
| `signature_digests` | `SET OF OCTET STRING` | 이 profile에서는 non-empty; 각 원소는 SHA-256의 **32 bytes**, 전체 승인 앱 서명 인증서 digest 집합과 일치 |

AppId의 non-empty·전체 승인 집합 검사는 CP:1799-1801과 §13.3의 `PROJECT` 결속을 적용한 것이다. Provider ASN.1의 `SET OF`를 임의 JSON 배열이나 단일 값으로 바꾸어 서명 범위 밖에서 검증하지 않는다. 이 절은 필수 검증에 필요한 구조를 명시한 것으로, 다른 optional authorization tag의 수락을 자동 승인하지 않는다. 지원 버전의 나머지 문법과 허용/거부 정책도 `OD-EVIDENCE-01`의 parser profile에서 고정한다.

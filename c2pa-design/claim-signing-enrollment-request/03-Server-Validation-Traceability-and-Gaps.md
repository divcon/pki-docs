# Server Validation, Traceability and Gaps

## 1. 판정 원칙

서버는 request body의 자기주장보다 CA/RA의 authoritative state와 cryptographically verified artifact를 우선한다. Unknown, stale, timeout, parser ambiguity, missing policy와 conflicting source는 성공으로 바꾸지 않는다.

```text
ISSUE =
  secure credential과 GP-instance authentication PASS
  AND Subscriber I/A/V·representative authority·Agreement current
  AND authenticated current CPL과 requested profile/AL eligible
  AND CSR profile·signature/PoP·new-key predicate PASS
  AND (AL1 Evidence field absent
       OR AL2 provider trust·freshness·binding·O.1..O.4 all PASS)
  AND final certificate profile·issuer·status readiness PASS
  AND every production-blocking decision APPROVED
```

Request body, issuance gate, onboarding evidence와 runtime control은 독립 축이다. 저장된 onboarding 승인을 참조해도 발급 시 currentness 검사가 사라지지 않고, runtime 의무가 있다는 이유로 그 증명자료를 임의로 body에 추가하지 않는다.

## 2. 인증·Enrollment requirement traceability

Locator의 CP/GSPR/Program은 `conformance-public@2466172859fad1215f7aaf7e3768b41a0ac29abc` commit blob이다.

| requirement ID | requirement / classification | authoritative source | enforcement |
|---|---|---|---|
| `REQ-TERM-01` | 공식 명칭 C2PA Claim Signing Certificate | CP:56-58,276-280 | 문서·profile 용어 |
| `REQ-IAV-01` | Applicant/Subscriber와 representative I/A/V, ≤398-day re-auth; `ONBOARDING+ISSUANCE-GATE` | CP:401-477 | `SG-02,SG-08` |
| `REQ-AGREEMENT-01` | legally valid Subscriber Agreement/Terms를 issuance 전에 확인; `NON-BCP14-OBLIGATION` | CP:1518-1558; CP:10-12 | `SG-02,SG-08` |
| `REQ-ACCEPT-01` | 발급 뒤 설치·사용에 의한 certificate acceptance; 발급 전 Agreement와 별도 `REQUIRED` | CP:531-535 | post-issuance record/runtime |
| `REQ-CRED-01` | secure access credential; `WIRE+ISSUANCE-GATE`, `C2PA REQUIRED` | CP:469-473,507-509 | `SG-01,SG-08` |
| `REQ-GP-AUTH-01` | 적격 Generator Product instance 인증; Subscriber authorization과 별개 | AL1 CP:1686-1695; AL2 CP:1712-1714; GSPR:338-376 | `SG-01,SG-08` |
| `REQ-ELIG-01` | conforming GP instance에만 발급 | CP:124-128,278-280; Program:368-374,488-498 | `RB-04,SG-03,SG-08` |
| `REQ-CPL-01` | CPL product type/status/DN/record/max AL과 조건부 method | CP:457-467,491-527; CPL schema:24-110,554-562 | `RB-02,RB-04,SG-03,SG-08` |
| `REQ-ALSET-01` | 수용 product에는 CPL maximum 이하 Claim AL 경로 제공 | CP:465-467; Program:440-445 | profile enablement gate |
| `REQ-POP-01` | requested key ownership과 CSR signature/PoP | CP:471-473; RFC 2986 §3,§4.1-4.2 | `RB-07..RB-10,SG-04,SG-08` |
| `REQ-DN-01` | CSR의 구조·C/O/CN, 발급 전 제품/CPL DN·권한 확인과 최종 Subject의 CPL DN·ASCII·unique instance ID 금지를 분리. 식별 입력 위치 및 CSR DN 불일치 처리는 CA 절차의 선택이며 공통 exact-match gate로 고정하지 않음 | CSR schemas:692-740; CP:381-405,461-509,1542-1556; [02 §3.1.1](02-CSR-and-Dynamic-Evidence-Requirements.md#csr-subject-identification) | `RB-04,RB-10,SG-02,SG-03,SG-04,SG-07` |
| `REQ-AL1-01` | AL1은 secure credential 기반 GP instance 인증; hardware Evidence count 미규정 | CP:1686-1695; GSPR:330-358 | `RB-11,SG-01` |
| `REQ-AL2-O1` | hardware-backed GP product-instance identity | CP:1712-1714; GSPR:360-376; Android CP:1799-1801,1812-1814 | `RB-12..RB-14,SG-06`; 02 §13의 `AK-04..AK-06,AK-17..AK-19` 및 공통 검증 |
| `REQ-AL2-O2` | requested key의 hardware generation/storage/possession | CP:1716-1718; GSPR:422-472; Android CP:1808 | `RB-12..RB-14,SG-06`; `AK-13` 및 hardware security level·증명키/CSR/PoP 결속 |
| `REQ-AL2-O3` | Claim Generator boot/image, vulnerability와 patch/revision | CP:1720-1734; GSPR:498-556; Android CP:1796-1797 | `RB-12..RB-14,SG-06`; `AK-01/AK-02`만으로 판정하지 않고 02 §13.4의 boot·reference coverage 검사 |
| `REQ-AL2-O4` | 모든 in-scope content/assertion-processing software coverage | CP:1737-1751; GSPR:572-636; Android CP:1796-1797,1809-1811,1815-1816 | `RB-12..RB-14,SG-06`; `AK-01/AK-02,AK-14..AK-16,AK-20/AK-21` 및 전체 component coverage |
| `REQ-ANDROID-01` | Android의 검증된 root-nearest 확장·chain/status·schema 필수 member/type/version과 증명키 결속; `PROVIDER/PROJECT`, AL2 조건부 | Google `#verifying/#root_certificate/#certificate_status/#expired_factory_keys`; AOSP `#attestation-extension/#schema/#keydescription-fields/#attestationapplicationid-schema`, 고정 KeyMint Tag.aidl의 조건부 RSA exponent (README §6) | `RB-13,RB-14,SG-04,SG-06,SG-08`; 01 §5.4, 02 §13.3 및 [§13.6](02-CSR-and-Dynamic-Evidence-Requirements.md#android-asn1-input) |
| `REQ-ANDROID-02` | Android Claim Signing key profile의 목적·algorithm·size·digest·padding·curve | CP:1802-1807; AOSP `#authorizationlist-fields` | `RB-10,SG-04,SG-06,SG-07`; `AK-07..AK-12`, `OD-ALG-01` |
| `REQ-O5O6-01` | issuance Dynamic Evidence는 O.5/O.6 `No stipulation`; GSPR runtime/static은 별도이며 O.5 AL2는 모든 class, O.6은 Distributed/Backend | CP:1753-1759; GSPR:324-328,638-744; GPSA Template:327-343 | `RT-01`; request body에는 추가 artifact 없음 |
| `REQ-FRESH-01` | challenge-using key/platform flow는 CA nonce exact match와 provider 권고 준수 | CP:1764-1768; Android CP:1798; Android Builder `setAttestationChallenge(byte[])` | `SG-06`; Android `AK-03`와 02 §13.3, 구체 TTL 등은 `OD-FRESHNESS-01` |
| `REQ-CSR-01` | AL1/AL2 CSR 필수 ASN.1 member, Subject/SPKI OID·parameters 및 extensionRequest의 OID·타입·criticality·값 | AL1/AL2 CSR:683-1336; RFC 2986 §4, RFC 2985 §5.4.2, RFC 5280 §4.2, RFC 3279 §2.3.1, RFC 5480 §2, RFC 8410 §§3-4 | `RB-07..RB-10,SG-04,SG-07`; [02 §3.3~§3.4](02-CSR-and-Dynamic-Evidence-Requirements.md#csr-input-fields) |
| `REQ-CERT-01` | AL1/AL2 final Leaf fields와 validity | CP:1204-1331; AL1/AL2 cert schemas:715-1535 | `SG-07,SG-08` |
| `REQ-KEY-01` | Subscriber key generation·exclusive control·no export/share; same-key renewal 금지 | CP:537,563-579,815-823; GSPR:378-472 | `RB-03,RB-05,RB-06,SG-05,RT-01` |
| `REQ-REKEY-01` | re-key는 새 key/CSR과 신규 신청과 같은 issuance auth·PoP | CP:475-481,573-579 | AL1/AL2 REKEY body 전체와 `SG-01..SG-08` |
| `REQ-REV-01` | enumerated revocation triggers, authenticated request ≤72h, Claim OCSP | CP:483-485,587-609 | `SG-07,SG-08,RT-01` |
| `REQ-RECORD-01` | issued certificate record를 expiry 뒤 ≥1년 보호 | CP:367-375,693-725 | records policy; `OD-RETENTION-01` |

## 3. Server validation gates

| ID | gate | exact predicate | decision IDs |
|---|---|---|---|
| `SG-01` | credential + instance | 승인된 secure credential이 Subscriber와 적격 GP instance에 결속되고 현재 유효함 | `OD-AUTH-01` |
| `SG-02` | onboarding authority | Subscriber/representative I/A/V, ≤398일 재인증과 legally valid/current Agreement가 유효함 | `OD-IAV-01` |
| `SG-03` | conformance/CPL | 인증된 신청자·GP instance와 발급 대상 제품을 결속하고 authenticated current CPL의 applicant, `generatorProduct`, `conformant`, DN, record ID, `minVersion`, max AL과 조건부 method를 확인. CSR Subject가 유일한 식별 입력이라고 가정하지 않으며 silent downgrade가 없음 | `OD-CPL-01`, `OD-DOWNGRADE-01[AL2]`, `OD-REVOCATION-01` |
| `SG-04` | CSR | strict DER PKCS#10 한 개, 02 §3.3~§3.4 필수 member/OID/type/parameters/criticality/value, signature/PoP, Subject 구조·C/O/CN 및 SPKI/extension profile이 유효함. CSR DN 차이는 02 §3.1.1의 절차로 처리하고 SG-03의 대상·권한 확인을 우회하지 않음 | `OD-SOURCE-01`, `OD-LIMIT-01`, `OD-ALG-01`, `OD-CPL-01` |
| `SG-05` | lifecycle/key | INITIAL/REKEY 의미와 server issuance history가 일치하고 승인된 same-public-key 판별 정책에서 새 key임 | `OD-BODY-01`, `OD-KEY-01`, `OD-LIFECYCLE-01[REKEY]` |
| `SG-06` | AL2 Evidence | provider parser/signature/chain/status/freshness/audience/subject-key binding과 O.1/O.2/O.3/O.4 각각이 PASS; Android는 02 §13의 `AK-01..AK-21`, §13.6의 필수 구조·타입·조건부 provider 필드, root-nearest 확장 및 전체 reference coverage 적용 | `OD-SOURCE-01`, `OD-LIMIT-01`, `OD-ALG-01`, `OD-EVIDENCE-01`, `OD-FRESHNESS-01`, `OD-REFERENCE-01`, `OD-REVOCATION-01` |
| `SG-07` | certificate construction | CSR extension을 복사하지 않고 authoritative TBS를 구성해 official cert schema, validity, issuer, serial과 OCSP readiness를 통과 | `OD-SOURCE-01`, `OD-ALG-01`, `OD-VALIDITY-01`, `OD-REVOCATION-01` |
| `SG-08` | pre-issuance currentness | 서명 직전에 applicable authoritative source와 decision version이 여전히 current이고 body/CSR/Evidence hash가 바뀌지 않음 | `OD-SOURCE-01`, `OD-BODY-01`, `OD-AUTH-01`, `OD-IAV-01`, `OD-CPL-01`, `OD-ALG-01`, `OD-VALIDITY-01`, `OD-EVIDENCE-01[AL2]`, `OD-FRESHNESS-01[AL2]`, `OD-REFERENCE-01[AL2]`, `OD-KEY-01`, `OD-DOWNGRADE-01[AL2]`, `OD-LIFECYCLE-01[REKEY]`, `OD-RETENTION-01`, `OD-REVOCATION-01` |
| `RT-01` | runtime | private-key boundary/용도, rotation, O.3~O.6, conformance/status refresh와 incident sign-stop을 지속 강제 | `OD-REVOCATION-01`, `OD-RUNTIME-01` |

권장 의존 순서는 credential/path authentication → strict body parse → body value authorization → onboarding/CPL currentness → CSR PoP/profile → AL별 Evidence → lifecycle/key history → authoritative certificate construction → pre-issuance currentness다. 이는 내부 구현의 fail-closed data dependency이며 네트워크 API나 상태 머신을 규정하지 않는다.

Subject 관련 검증 예시는 다음을 구분한다. 이는 향후 검증 조건이며 실행한 테스트 결과가 아니다.

- CSR C/O/CN 누락·잘못된 ASN.1 또는 PoP 실패는 거부한다.
- CSR Subject를 제품 식별에 사용하는 절차에서 제품/CPL record·권한이 확인되지 않으면 보완 전 발급하지 않는다.
- `cplRecordId`나 인증된 등록정보로 동일 요청의 제품·권한을 확인하는 절차에서는 CSR DN 차이만을 공통 자동 거부 조건으로 추가하지 않는다. CA가 정한 불일치 처리와 제출정보 정확성 확인 결과를 검증한다.
- 다른 Subscriber의 CPL record로 바꿔치기하거나 최종 인증서 DN이 확인된 CPL DN과 다른 경우는 거부한다. Subject 식별 방식 변경으로 AL/CPL extension, Evidence 또는 원본 CSR hash 결속을 완화하지 않는다.

## 4. Pre-issuance invariant set

| invariant | exact condition | fail-closed action |
|---|---|---|
| `INV-AUTH` | credential, GP instance, Subscriber와 representative approval current | 발급 중단 |
| `INV-AGREEMENT` | legally valid/current Agreement record가 동일 Subscriber와 발급 범위에 결속 | 발급 중단 |
| `INV-CPL` | exact CPL record/applicant/product/status/DN/max AL/method pass | profile 발급 중단 |
| `INV-CSR` | 저장된 DER hash, PoP, Subject/SPKI/extensions unchanged | 보안 사건으로 격리 |
| `INV-AL1` | Evidence item이 없고 GP-instance authentication pass | 발급 중단 |
| `INV-AL2` | Evidence hashes, trust/freshness/binding과 O.1~O.4 pass/current | AL2 발급 중단 |
| `INV-LIFECYCLE` | INITIAL은 prior issuance 없음; REKEY는 same-lineage predecessor와 새 key | 발급 중단 |
| `INV-KEY` | 승인된 key-reuse identity profile과 전체 Claim/TSA history에서 미사용 | 전체 발급 중단 |
| `INV-TEMPLATE` | exact profile field/criticality/value와 CSR SPKI; unknown field를 복사하지 않음 | 발급 중단 |
| `INV-ISSUER` | Claim Issuing CA key/chain/status/OCSP와 algorithm 교집합 active | 발급 중단 |

## 5. Production enablement

현재 architecture snapshot은 미승인 값을 임의 default로 채우지 않는다.

- `COMMON = OD-SOURCE-01, OD-BODY-01, OD-LIMIT-01, OD-AUTH-01, OD-IAV-01, OD-CPL-01, OD-ALG-01, OD-VALIDITY-01, OD-KEY-01, OD-RETENTION-01, OD-REVOCATION-01`
- `AL2 = OD-EVIDENCE-01, OD-FRESHNESS-01, OD-REFERENCE-01, OD-DOWNGRADE-01`
- `REKEY = OD-LIFECYCLE-01`

| profile / operation | blocking set | current state |
|---|---|---|
| AL1 INITIAL | `COMMON` | `DISABLED` |
| AL1 REKEY | `COMMON + REKEY` | `DISABLED` |
| AL2 INITIAL | `COMMON + AL2` | `DISABLED` |
| AL2 REKEY | `COMMON + AL2 + REKEY` | `DISABLED` |
| AL1/AL2 RENEWAL | same-key renewal이 원문상 금지 | 지원하지 않음 |
| product runtime release | `OD-RUNTIME-01` + profile decisions | `DISABLED` |

Accepted CPL의 `maxAssuranceLevel=2` product는 AL1/AL2 요청 경로를 모두 제공해야 하므로 둘 중 하나라도 미준비이면 두 profile을 함께 비활성화한다(CP:465-467; Program:440-445). 이는 한 요청에서 두 certificate를 발급한다는 뜻이 아니다.

## 6. Operations Decision Register

### 6.1 Decision, owner와 fail-closed

| decision ID | policy boundary | owner → approver / authority store | status / current value | blocking scope / interim action | resolution condition |
|---|---|---|---|---|---|
| `OD-SOURCE-01` | CP/Program/GSPR와 CSR/cert/CPL, RFC 및 README §6에 고정한 provider 원문 identity | Architecture → PKI+Security / source registry | `APPROVED`: conformance `2466172…`, specifications `9c58c8c…`; RFC/Android는 README §6의 고정 사본·commit/blob | identity mismatch profile disabled | source diff, migration test와 audit; 문서의 source identity와 실제 운영 trust registry 승인은 구분 |
| `OD-BODY-01` | JSON field/cardinality/schema version과 fixed INITIAL/REKEY body·eligibility 구분; C2PA는 wrapper 미규정 | Enrollment owner → Security / versioned request schema | `APPROVED`: [01](01-Enrollment-Request-Body.md)의 `2026-09-04` body | artifact/hash mismatch 시 enrollment disabled | machine-readable schema와 operation vectors가 RB-01~RB-14, SG-05/SG-08에 일치 |
| `OD-LIMIT-01` | body/CSR/item/chain/depth positive limits | Platform/SRE → Security / config registry | `TBD`; 수치 default 없음 | 모든 profile `DISABLED` | capacity·abuse·parser test로 bound 승인 |
| `OD-AUTH-01` | secure credential 종류와 GP-instance binding | IAM/CA CPS → PKI+Security / CPS+IAM policy | `TBD` | 모든 profile `DISABLED` | threat model, credential lifecycle/revocation와 negative tests |
| `OD-IAV-01` | identity source, representative authority, Agreement와 re-auth workflow | RA/Legal → CA Policy / CPS+RA registry | `TBD`; 398일 ceiling만 고정 | 모든 profile `DISABLED` | source/procedure/agreement evidence와 boundary tests |
| `OD-CPL-01` | Notice/CPL authenticity/currentness/conflict, 제품 식별정보의 출처·요청자 결속, CSR DN 차이 처리, 최종 DN과 `minVersion` mapping | Conformance ingest → PKI+Security / CPL registry | `TBD` | 모든 Claim profile `DISABLED` | signature/freshness/conflict/대상·권한/DN/version rules와 tests |
| `OD-ALG-01` | CSR, subject key, issuer signature와 runtime COSE algorithm 교집합 | Crypto policy → PKI+Security / CPS crypto registry | `TBD` | 모든 Claim profile `DISABLED` | HSM/client matrix, KAT와 CPS approval |
| `OD-VALIDITY-01` | actual AL1≤366/AL2≤90 validity, serial, AIA/OCSP와 optional CDP/OID | PKI operations → CA Policy / template registry | `TBD`; C2PA ceilings만 고정 | 모든 Claim profile `DISABLED` | template/status/serial/profile end-to-end tests |
| `OD-EVIDENCE-01` | AL2 provider 지원 버전·`N_p`·signed artifact 포장·trust/status 운영과 objective map 적용 | Evidence owner → Security+CA Policy / provider registry | `TBD` 운영 승인; 사용자는 Google-rooted Android Key Attestation 선택, CP 21개 매핑은 02 §13에 문서화 | AL2 `DISABLED` | 01 §5.4 포장의 registry 값·지원 parser/algorithm·root rotation·factory/RKP 범위, status feed 및 02 §13.5 positive/negative vectors 확정 |
| `OD-FRESHNESS-01` | signed freshness와 CA request-context/audience/key 결속·replay identity | Evidence owner → Security / provider registry | `TBD` 운영 승인; Android는 CP의 nonce exact-match와 생성 시 challenge 사용을 확인 | AL2 `DISABLED` | 02 §13.3의 CA context 결속, provider 128-byte 상한 내 길이/엔트로피·TTL·소비 정책과 freshness/replay/concurrency tests; stale envelope 우회 거부 |
| `OD-REFERENCE-01` | Android app/OEM 기준값, 패치 경계·시간대, O.2 key property와 O.3/O.4 inventory/reference | Product security → Security+CA Policy / reference registry | `TBD` 운영 승인; 사용할 원문 필드는 02 §13.2에 고정, 실제 제품값·coverage는 미확정 | AL2 `DISABLED` | 승인 package/version/signer 및 조건부 OEM 조합, 월 차이 `0..3` 해석안 처분, release→전체 component revision·취약점 조치 연결, reference update/revoke와 coverage tests |
| `OD-KEY-01` | cross-encoding same-public-key identity, global Claim/TSA history와 concurrency | PKI engineering → Security / immutable key-history registry | `TBD`; 승인된 identity algorithm 없음 | Claim/TSA 모든 issuance `DISABLED` | typed encoding, byte order, curve/algorithm registry, deterministic serialization, cross-algorithm KAT와 collision/concurrency/crash tests |
| `OD-DOWNGRADE-01` | AL2 failure 뒤 lower AL 처리 | CA Policy → Security / policy registry | `APPROVED`: silent/automatic downgrade 금지; 별도 명시적 AL1 request만 | AL2는 그대로 fail-closed | policy 변경 시 consent/threat/profile tests |
| `OD-LIFECYCLE-01` | REKEY overlap/cutover/revocation, predecessor와 profile migration | Product+PKI ops → CA Policy+Security / lifecycle policy | `TBD`; 새 key/full validation은 고정 | 모든 REKEY `DISABLED` | overlap, activation/use-stop, rollback와 incident semantics |
| `OD-RETENTION-01` | CSR/Evidence/reference/audit 보존·접근·삭제; issued record expiry+≥1y | Privacy+Audit → Legal+Security / records policy | `TBD` | 모든 issuance `DISABLED` | purpose/legal basis, duration, access/delete/audit evidence |
| `OD-REVOCATION-01` | CPL/provider/key incident ingest, ≤72h workflow와 OCSP publication | PKI incident → CA Policy+Security / CPS+incident registry | `TBD` | 모든 issuance `DISABLED` | drills, dependency index, status SLA와 mass-revoke evidence |
| `OD-RUNTIME-01` | key-use ACL, status refresh, O.3~O.6 monitoring와 sign-stop | Product security → Security/Conformance / release policy | `TBD` | runtime production release `DISABLED` | class-exact controls, tests/monitoring와 incident integration |

총 17개: `APPROVED` 3, `TBD` 14. `TBD`에 의존하는 활성 production path는 0개다.

### 6.2 Decision → enforcement

| decision ID | enforcement IDs |
|---|---|
| `OD-SOURCE-01` | `SG-04,SG-06,SG-07,SG-08` |
| `OD-BODY-01` | `RB-01,RB-02,RB-03,RB-04,RB-05,RB-06,RB-07,RB-08,RB-09,RB-10,RB-11,RB-12,RB-13,RB-14,SG-05,SG-08` |
| `OD-LIMIT-01` | `RB-09,RB-10,RB-14,SG-04,SG-06` |
| `OD-AUTH-01` | `SG-01,SG-08` |
| `OD-IAV-01` | `SG-02,SG-08` |
| `OD-CPL-01` | `RB-02,RB-04,SG-03,SG-04,SG-08` |
| `OD-ALG-01` | `RB-10,SG-04,SG-06,SG-07,SG-08` |
| `OD-VALIDITY-01` | `SG-07,SG-08` |
| `OD-EVIDENCE-01` | `RB-12,RB-13,RB-14,SG-06,SG-08[AL2]` |
| `OD-FRESHNESS-01` | `SG-06,SG-08[AL2]` |
| `OD-REFERENCE-01` | `SG-06,SG-08[AL2]` |
| `OD-KEY-01` | `SG-05,SG-08` |
| `OD-DOWNGRADE-01` | `RB-02[AL2],SG-03[AL2],SG-08[AL2]` |
| `OD-LIFECYCLE-01` | `RB-03[REKEY],RB-06[REKEY],SG-05[REKEY],SG-08[REKEY]` |
| `OD-RETENTION-01` | `SG-08` + records policy |
| `OD-REVOCATION-01` | `RB-14,SG-03,SG-06,SG-07,SG-08,RT-01` |
| `OD-RUNTIME-01` | `RT-01` |

각 `RB-*`는 [request body matrix](01-Enrollment-Request-Body.md#5-enrollment-request-body-matrix), `SG-*`와 `RT-01`은 이 문서 §3의 exact predicate다.

## 7. Gap and clarification register

| gap ID | exact issue | disposition | interim behavior |
|---|---|---|---|
| `GAP-NORM-01` | provider 공통 Evidence format, artifact count, TTL/audience/replay field는 미규정(CP:1697-1768). Android에는 별도의 ASN.1 schema와 CP:1796-1816 값 가이드가 있음 | Android 매핑 누락은 02 §13으로 보강; 실제 `OD-EVIDENCE-01/OD-FRESHNESS-01` 운영 결정은 유지 | AL2 disabled |
| `GAP-NORM-02` | GSPR의 KME third-party certification 대안이 CP의 issuance Dynamic Evidence를 제거하는지 불명확(GSPR:436-440,470-472; CP:1716-1718) | certification은 static 대안으로만 취급; 명시적 C2PA clarification 전 O.2 artifact 유지 | AL2 artifact required |
| `GAP-NORM-03` | O.5 AL2에는 AL1의 class 제한이 없고 general applicability가 적용됨(GSPR:324-328,638-680) | Edge/Backend/Distributed runtime 의무로 폐쇄 | request body artifact로 전이하지 않음 |
| `GAP-NORM-04` | Leaf profile은 Ed25519 certificate signature를 열지만 conforming issuer SPKI는 RSA/EC만 허용(CP:1044-1061,1214,1279) | RSA/ECDSA issuer intersection만 enable | Ed25519 issuer signature disabled |
| `GAP-NORM-05` | signed Notice 선발급 문구와 public CPL `conformant` record 요구가 긴장(CP:461-463; Program:474,498) | stricter current-public-CPL rule; `OD-CPL-01` clarification | Claim profiles disabled |
| `GAP-NORM-06` | CP는 REKEY 뒤 overlap/cutover/automatic revocation을 정하지 않음(CP:573-579) | `OD-LIFECYCLE-01` | REKEY disabled |
| `GAP-NORM-07` | lower AL 평가는 허용하지만 migration protocol은 없음(CP:42,519-529) | no silent downgrade; 별도 AL1 request | automatic downgrade 없음 |
| `GAP-NORM-08` | CPL schema의 `attestationMethods`는 optional이며 그 schema 자체가 provider semantic 검증을 정의하지 않음. Android CP 가이드의 존재와는 별개 | `OD-EVIDENCE-01`; current CPL/method와 선택 Android profile의 적용 가능성 확인 | usable method 없는 AL2 disabled |
| `GAP-ANDROID-01` | CP:1816의 boot `[718]` 오기 및 CP/AOSP 필드 명칭 차이 | 02 §13.2에 AOSP `[719]`와 schema/version 해석을 명시; 원문 오염 없이 정정 기록 | parser가 CP 오기를 그대로 사용하면 거부 |
| `GAP-ANDROID-02` | CP:1811의 OS 4개월 문구와 당월+직전3개월 예시 사이의 경계 | `OD-REFERENCE-01`에서 02 §13.2의 예시 기반 해석안·시간대 확정 | 미확정 Android profile disabled |
| `GAP-ANDROID-03` | CP Android 표의 목표 label만으로 일반 O.3/O.4 전체 component coverage를 판정할 수 없음(CP:1720-1751,1766) | 02 §13.4의 verified release→inventory/revision·취약점 조치 연결을 `OD-REFERENCE-01`에서 확정 | coverage 불명확 시 O.3/O.4 PASS 금지 |
| `GAP-OPS-01` | 14 operational decisions가 `TBD` | 각 decision resolution condition 충족 | 영향 path 모두 disabled |
| `GAP-OPS-02` | C2PA는 같은 공개키 금지를 규정하지만 cross-encoding identity algorithm은 정의하지 않음 | `OD-KEY-01`의 typed algorithm과 vectors 승인 | Claim/TSA issuance 전부 disabled |

## 8. 기존 비부록 architecture 일관성

이 절의 architecture locator는 수정 대상일 뿐 규범 근거가 아니다.

| target | issue | action |
|---|---|---|
| `c2pa-design/Overview.md` | Claim enrollment가 endpoint/state 설계와 섞이고 provider count가 project cardinality처럼 읽힐 수 있음 | Claim 범위는 request-body 문서로 연결하고 count/source 경계를 명시 |
| `c2pa-design/01-Architecture-Foundation.md` | underdefined normalized-key digest를 active invariant로 선언 | 승인된 `keyReuseIdentity` profile 전제로 바꾸고 미승인 동안 issuance disabled |
| `c2pa-design/02-Certificate-Enrollment.md` | Claim source locator, Notice/CPL tension과 AL별 Evidence 경계를 current source로 맞춰야 함 | 원문 재검증 후 Claim enrollment 요구와 request-body owner 연결 |
| `c2pa-design/04-Security-and-Operations.md` | 같은 underdefined key digest와 tombstone 형식을 active policy로 선언 | identity algorithm/retention approval 전 fail-closed로 수정 |
| 기타 비부록 architecture | Claim 요구와 직접 충돌하는지 점검 | 사실 정정이 없으면 변경하지 않음 |

## 9. Traceability checklist

- 각 `REQ-*`에 external source와 `RB/SG/RT` enforcement가 있는가.
- I/A/V, Agreement, secure credential, GP-instance authentication, CSR PoP와 AL2 attestation trust를 분리했는가.
- AL2 O.1~O.4를 각각 요구하고 O.5/O.6를 request body로 전이하지 않았는가.
- Provider artifact count와 project `1..N_p`를 혼동하지 않았는가.
- 선택 Android provider의 CP 21개 행과 `REQ-AL2-*`, `REQ-ANDROID-*`, `SG-06` 연결이 빠지지 않았는가. 원문 오기·provider parser 규칙·PROJECT 정책을 구분했는가.
- Android `value`의 인증서 선택·CSR 키 결속, chain/status, challenge, softwareEnforced 신뢰 전제와 O.3/O.4 전체 coverage를 검사하는가.
- 각 `TBD`에 owner, resolution, blocking scope와 disabled state가 있는가.
- `RENEWAL`은 금지되고 REKEY는 새 key와 전체 current gate를 거치는가.
- URL, response, state machine, idempotency, retry와 stable error 설계가 신규 문서에 없는가.

# Root와 First ICA 세레모니 — 설정

작성 중 · 행사 기준은 [메인 스크립트](script.md)입니다. 실제 값과 선택 근거를 채우고, 승인된 버전을 [승인본 목록](preparation.md#승인본-목록)에 고정합니다. 샘플의 가상 값은 복사하지 않습니다.

행사 일정·참여자 명단은 `script.md`에서 관리하고, 이 문서에서는 그 역할과 실제 계정·키·권한을 연결합니다. 선택값을 다른 문서에 반복해서 쓰기보다 이 표를 참조합니다.

**2026-10-12 작성 범위:** 현재는 타 부서와 협의할 세레모니의 정책·역할·승인·준비 조건을 우선한다. 생성 도구·버전·raw/digest·변환/조립 명령·파일 규칙·검증 명령 등 개발 구현 상세는 후속 작성으로 미룬다. 기존 세부 항목은 미작성 상태로 보존하며 행사 전 구현·검증·리허설 조건은 유지한다.

## 승인 설정

2026-10-12 작성: 고정된 CP v0.2·Root/First YAML·인증서/CSR schema 원문을 대조해 필수 조건을 채웠다. **규칙**은 원문 요구, **기존 결정**은 사용자가 이미 정한 값, **호환 처리**는 고정 schema와 함께 사용하기 위한 작성 방침, **선택 필요**는 아직 승인하지 않은 값이다. 아래 표 작성은 인증서 생성·검증이나 행사 승인을 뜻하지 않는다. 원문은 [Root 프로파일][root-profile]·[First 프로파일][first-profile]·[CP][cp-source] 및 [schema 차이 처리](#프로파일과-schema-차이-처리)를 참조한다.

| 항목 | Root | First ICA |
|---|---|---|
| 형식·버전 | **규칙:** X.509 v3 (`TBSCertificate.version=2`), DER | **규칙:** X.509 v3 (`TBSCertificate.version=2`), DER |
| 키 알고리즘·곡선 | EC / NIST P-384 (`secp384r1`), ECDSA 서명용 | EC / NIST P-384 (`secp384r1`), ECDSA 서명용. Root와 별도 키 쌍 |
| SubjectPublicKeyInfo | **기존 결정의 인코딩:** `id-ecPublicKey` (`1.2.840.10045.2.1`), parameters는 namedCurve `secp384r1` (`1.3.132.0.34`). Root 공개키 | 같은 식별자·곡선, First 공개키. CSR·HSM에서 확인한 공개키와 일치 |
| 키 라벨·속성·소유·공유 | 개인키는 서명 전용. `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false`, `extractable=false`, `sensitive=true`, `token=true`. 잠금 기본안은 `modifiable=false`, `destroyable=false`. 사용·관리 quorum 각각 `2`, 승인 집합 O·A·B. 폐기 계획·잠금 시험 완료 전 운영 키 생성 금지. 라벨·계정 매핑: {{Root_키_설정}} | 개인키는 서명 전용. `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false`, `extractable=false`, `sensitive=true`, `token=true`. 잠금 기본안은 `modifiable=false`, `destroyable=false`. 사용·관리 quorum 각각 `2`, 승인 집합 O·A·B. 폐기 계획·잠금 시험 완료 전 운영 키 생성 금지. 라벨·계정 매핑: {{First_키_설정}} |
| Subject / Issuer DN | **규칙:** CA를 고유하게 식별하는 Subject에 C (`2.5.4.6`)·O (`2.5.4.10`)·CN (`2.5.4.3`) 필수. Issuer=Subject. **추후 결정(U01):** {{Root_C_O_CN_추가RDN}} | **규칙:** 고유한 Subject에 C·O·CN 필수. Issuer=Root Subject. **추후 결정(U01):** {{First_C_O_CN_추가RDN}}. CSR Subject와 발급 승인값 대조 |
| 인증서 서명 알고리즘·키 | **기존 결정:** Root 키의 ECDSA + SHA-384 (`1.2.840.10045.4.3.3`), parameters 생략. TBS의 signature와 바깥 signatureAlgorithm 동일 | **기존 결정:** Root 키의 ECDSA + SHA-384, parameters 생략. TBS의 signature와 바깥 signatureAlgorithm 동일. First CSR은 First 키로 서명 |
| 서명 입력 형식 | S02: Root TBSCertificate DER. CLI raw/digest 전달 방식은 미정 | S05: First TBSCertificate DER. S04 CSR 입력은 아래 별도 표. CLI raw/digest 전달 방식은 미정 |
| 유효기간 UTC | **사용자 확정(2026-10-12):** 20년. 실제 시작·만료 UTC 시각은 발급 전 고정: {{Root_notBefore_notAfter}}. 원문의 예시를 이번 행사의 선택값으로 채택 | **사용자 확정(2026-10-12):** 5년. 실제 시작·만료 UTC 시각은 발급 전 고정: {{First_notBefore_notAfter}}. Root 만료와 후속 Issuing 운용 기간을 함께 검토 |
| Serial 생성·중복 방지 규칙 | **규칙:** 양수, 최대 20 octets, 발급자별 중복 금지. 고엔트로피 권고. **사용자 확정(2026-10-12, 5-A):** CSPRNG 기반 최대 159-bit 양수, 0 제외, 원장 예약·중복 차단. [C2PA 권고와 일반 사례](#u05-serial-정책의-c2pa-기준과-일반-사례) 참조. 실제 값은 서명 전에 원장 예약 | 같은 규칙. Root가 발급하므로 Root 자기서명 인증서와 같은 발급자 원장에서 중복 검사. 값은 CSR에서 받지 않음 |
| SKI (`2.5.29.14`) | **규칙:** 필수, non-critical. Root 공개키에 RFC 5280 Method 1 SHA-1 적용, 20-byte keyIdentifier | **규칙:** 필수, non-critical. First 공개키에 같은 방법 적용. 실제 값은 키 생성 후 계산 |
| AKI (`2.5.29.35`) | **호환 처리:** 포함, non-critical, `keyIdentifier=Root SKI`. CP/YAML은 선택이나 고정 schema는 존재 요구. 선택 하위 필드 issuer/serial은 기본 생략 | **규칙:** 필수, non-critical, `keyIdentifier=Root SKI` (First SKI가 아님). 선택 하위 필드 issuer/serial은 기본 생략 |
| Key Usage (`2.5.29.15`) | **규칙:** 필수, critical. `keyCertSign=true`, `cRLSign=true`; 나머지 비트 모두 false | Root와 동일. CSR의 요청 KU도 동일 |
| Extended Key Usage (`2.5.29.37`) | 해당 Root 프로파일에 필수 EKU 없음. **사용자 확정 정책(6-A):** 생략 | 해당 First 프로파일에 필수 EKU 없음. **사용자 확정 정책(6-A):** 생략. 하위 Issuing/leaf용 EKU를 자동 복사하지 않음 |
| Basic Constraints (`2.5.29.19`) | **규칙:** 필수, critical, `cA=true`, 정수 `pathLenConstraint`는 0–2. **사용자 확정(2026-10-12):** `pathLenConstraint=2`. Root → First → Issuing → leaf 구성을 수용하는 값 | **규칙:** 필수, critical, `cA=true`, `pathLenConstraint=1` |
| Certificate Policies (`2.5.29.32`) | **규칙:** 선택 확장, 포함하면 non-critical. **사용자 확정 정책(6-A):** 생략 | **규칙:** 필수, non-critical, `1.3.6.1.4.1.62558.1.1` 포함. **사용자 확정 정책(6-A):** 이 C2PA OID만 포함하고 추가 CPS 정책 OID·qualifier 생략 |
| AIA (`1.3.6.1.5.5.7.1.1`) / CDP (`2.5.29.31`) | **규칙:** 둘 다 포함 금지 | **규칙:** OCSP AIA 또는 CDP 필요, 포함하면 non-critical·HTTP URI. **사용자 확정(2026-10-12, U04):** 방식 A — AIA에 OCSP·caIssuers 포함, CDP 생략. 실제 URL은 미정, OCSP·URL 제공 기능은 미구현. 고정 schema의 `oneOf` 및 caIssuers 조건 적용 |
| 기타 확장·critical 여부 | **사용자 확정 정책(6-A):** 위 표 외 추가 확장 없음. 추가할 경우 OID·값·critical·허용 근거를 개별 승인 | 같은 처리. 확장 OID 중복 금지. 미인식 critical 확장과 임의 확장 추가는 검사·승인 없이 허용하지 않음 |

설정 원본과 버전: {{설정_원본}}. 프로파일 차이는 [처리 기록](#프로파일과-schema-차이-처리)에 관리한다. 공개키 지문·파일 해시 방식: {{해시_대상과_알고리즘}}. **SKI의 SHA-1, CA 서명의 SHA-384, 증거 식별용 SHA-256은 서로 다른 용도**다.

SKI는 `subjectPublicKey` BIT STRING의 공개키 값에 SHA-1을 적용한다. ASN.1 tag·length·unused-bits 수와 SPKI 전체 DER는 해시 대상이 아니다. First AKI는 서명자인 Root의 SKI를 사용한다. KU의 나머지 비트는 `digitalSignature`, `contentCommitment`, `keyEncipherment`, `dataEncipherment`, `keyAgreement`, `encipherOnly`, `decipherOnly`이며 모두 false다. HSM의 `sign=true`를 KU의 `digitalSignature=true`로 옮기지 않는다. [RFC 5280 §4.2.1.1–3][rfc5280]

SPKI parameters에는 곡선 OID를 포함하지만 ECDSA 서명 AlgorithmIdentifier의 parameters는 생략한다. 각각 [RFC 5480 §2.1.1][rfc5480]과 [RFC 5758 §3.2][rfc5758]를 적용한다. 유효기간은 UTC 초 단위로 고정하며 2049년까지 UTCTime, 2050년부터 GeneralizedTime으로 인코딩한다. Serial은 DER INTEGER의 부호용 바이트까지 고려해 길이와 양수 여부를 별도로 검사한다. [RFC 5280 §4.1.2][rfc5280]

### First CSR 설정

아래 값은 [공식 First CSR schema][first-csr-schema]의 `c2paFirstIntermediateCaCsrConstraints`를 기준으로 한다. CSR의 요청 확장은 발급 허가가 아니며, 최종 인증서 설정과 독립 대조한다.

| 항목 | 작성할 값·검사 조건 |
|---|---|
| 형식·버전 | PKCS #10, `CertificationRequestInfo.version=0` (v1), DER. [RFC 2986 §4][rfc2986] |
| Subject | 위 표의 First DN. C·O·CN 필수, 실제 값은 U01에서 추후 결정 |
| SubjectPublicKeyInfo | HSM에서 생성한 First P-384 공개키, `id-ecPublicKey`와 namedCurve `1.3.132.0.34`. 최종 First 인증서 공개키와 대조 |
| 서명 | First 개인키로 CertificationRequestInfo DER에 ECDSA + SHA-384. `1.2.840.10045.4.3.3`, parameters 생략. CSR 자체 서명 검증 |
| 요청 확장 전달 | PKCS #9 `extensionRequest` (`1.2.840.113549.1.9.14`) 속성에 Extensions를 넣음. schema의 `requestedExtensions`는 디코딩 결과의 표현. [RFC 2985 §5.4.2][rfc2985] |
| 필수 요청 Basic Constraints | `2.5.29.19`, critical, `cA=true`, `pathLenConstraint=1` |
| 필수 요청 Key Usage | `2.5.29.15`, critical, `keyCertSign=true`, `cRLSign=true`, 나머지 7개 비트 false |
| 필수 요청 Certificate Policies | `2.5.29.32`, non-critical, C2PA OID `1.3.6.1.4.1.62558.1.1` 포함. 추가 정책·qualifier는 승인한 First 선택과 일치 |
| AIA / CDP 요청 처리 | **작성 방침: CSR에서는 둘 다 생략.** 발급 단계에서 승인한 OCSP·caIssuers AIA를 First TBSCertificate에 포함하고 CDP는 생략. CSR schema는 AIA/CDP를 요청했을 때만 조건을 검사하며 존재를 강제하지 않음. 최종 인증서 조건은 별도 검증 |
| 기타 요청 | SKI·AKI·EKU는 이 CSR schema의 필수 요청 항목이 아님. 작성 방침은 위 필수 3개 확장만 요청하고, 추가 요청으로 변경하면 목록·근거를 승인. SKI·AKI는 발급 단계에서 실제 키로 계산·대조 |
| 인증서 전용 값 | issuer·serial·notBefore/notAfter는 PKCS #10 기본 필드가 아니므로 발급 설정에서 관리 |

**CSR의 AIA 생략과 발급 단계 추가 근거(2026-10-12):** 고정 [First CSR schema][first-csr-schema]의 `$defs/c2paFirstIntermediateCaCsrConstraints/allOf/2`는 Basic Constraints·Key Usage·Certificate Policies를 필수 요청으로 검사한다. `allOf/3`과 `allOf/4`는 AIA/CDP가 요청된 경우에만 적용하는 조건이며 존재를 요구하지 않는다. [RFC 2986 §3](https://www.rfc-editor.org/rfc/rfc2986.html#section-3)은 CA가 CSR 속성뿐 아니라 CA가 알고 있는 다른 정보도 사용해 인증서 확장을 구성할 수 있다고 설명한다. 따라서 CSR 원본과 서명을 유지한 채, 발급용 First TBSCertificate에 승인한 AIA를 넣는 작성 방식은 확인한 규격에 부합한다. 발급 후 인증서를 수정한다는 뜻이 아니다.

최종 인증서는 [First 프로파일][first-profile]·[First schema][first-schema]에 따라 OCSP·caIssuers·non-critical·HTTP URI 조건을 독립 검증한다. 이는 해당 작성 방식의 적합성 판단이며 실제 CSR/인증서 검증이나 Conformance 심사 완료를 뜻하지 않는다. 본문·설정의 준비 시점은 [사전 고정과 당일 작성](preparation.md#csr인증서-사전-고정과-당일-작성)을 따른다.

### 프로파일과 schema 차이 처리

2026-10-12에 공식 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`에서 원문을 직접 추출해 대조했다. 사용 원문 해시는 [고정본 목록](preparation.md#적용-원문-고정본)과 일치한다. 아래는 프로젝트의 호환 처리이며 C2PA의 해석 회신이나 예외 승인이 아니다.

| 항목 | 공식 원문과 고정 schema의 차이 | 이번 설정표의 처리 |
|---|---|---|
| Root AKI | [CP/Root YAML][root-profile]은 선택. [Root schema][root-schema]의 `c2paRootCaConstraints/allOf/4` 내 extensions는 AKI를 `contains`로 요구 | non-critical AKI를 포함하고 Root SKI와 같게 설정해 양쪽 조건을 충족하도록 작성 |
| First AKI의 참조 키 | [First YAML][first-profile]의 SKI 일치 문구는 발급자를 명시하지 않음. [RFC 5280 §4.2.1.1–2][rfc5280]는 발급자 키 식별 관계를 정의 | First AKI=Root SKI. 문자열 형식만 검사하는 schema 외에 실제 키 연결 검사 필요 |
| First OCSP AIA + CDP | CP/YAML의 조건은 양쪽 병행을 명시적으로 금지하지 않음. [First schema][first-schema]의 `c2paFirstIntermediateCaConstraints/allOf/5`는 `oneOf`여서 두 분기를 함께 만족하면 실패 | 사용자 결정으로 방식 A(OCSP AIA, CDP 생략)를 확정. 병행이 필요하면 적용 schema와 외부 수용 근거를 해결하기 전 발급 보류 |
| AIA의 caIssuers | YAML은 SHOULD. 같은 schema `allOf/6`은 description에서 권고라고 설명하지만 실제 `contains`는 caIssuers 존재를 검사 | AIA를 쓰는 방식 A에서는 OCSP와 caIssuers를 모두 포함. caIssuers 주소는 발급자인 Root 인증서 제공 위치 |
| 주소 scheme | YAML은 HTTP URI, 인증서·CSR schema는 `^http://.+` 검사 | 이 고정본에 맞추는 주소는 `http://`로 작성. HTTPS만 넣고 호환된 것으로 처리하지 않음 |
| 유효기간·EKU·추가 확장 | Root 20년·First 5년은 예시. Root/First 필수 EKU는 열거하지 않음 | 사용자가 예시 기간을 이번 행사의 값으로 채택. 규격의 의무 기간으로 표현하지 않음. EKU·추가 확장 생략은 사용자 채택 기본안이며 규격의 금지로 표현하지 않음 |

schema는 디코딩한 JSON을 검사한다. 실제 DER, SKI 계산, AKI/issuer 연결, 서명, 공개키와 체인은 별도로 검증한다. 문서 설정과 schema 조건 대조를 실제 인증서·CSR 검증 완료로 기록하지 않는다.

2026-10-12 확인: 고정 schema의 해당 제약 부분만 대상으로 합성 JSON 13건을 검사했다. Root AKI 포함/누락, OCSP+caIssuers 또는 CDP 단독, 두 상태 분기 병행·상태 누락·caIssuers 누락·HTTPS OCSP, CSR 필수 3개 확장과 각각의 누락·digitalSignature 활성화를 대조했으며 예상한 허용/거부 결과와 일치했다. 실제 DER 디코더나 인증서/CSR 전체 검증, HSM 시험은 수행하지 않았다.

### First 상태 제공과 발급 조건

| 선택 | First 인증서 확장 | 사용자 결정·준비할 값 |
|---|---|---|
| A — OCSP (**사용자 확정**) | non-critical AIA에 OCSP (`1.3.6.1.5.5.7.48.1`)와 caIssuers (`1.3.6.1.5.5.7.48.2`) 포함. CDP 생략 | First 상태 OCSP의 `http://` 주소, Root 인증서 배포 `http://` 주소, 응답 서명·제공 주체, 운영·인수 담당자와 가동 시점 |
| B — CRL (미채택 비교안) | non-critical CDP에 CRL의 `http://` URI 포함. AIA 생략 | First 상태를 담을 CRL의 배포 주소, CRL 발급·갱신·게시 담당자와 주기, 운영·인수 담당자와 가동 시점 |

현재 선택: **사용자 확정(2026-10-12, U04) — 방식 A: AIA + OCSP**. First 인증서에 non-critical AIA를 포함하고 OCSP·caIssuers 두 accessMethod를 기재하며 CDP는 생략한다. 이전의 방식 추후 결정 상태를 이 결정으로 대체한다. **방식만 확정했으며 OCSP 구현과 URL 제공 기능은 미구현**, 실제 URL·운영 주체·가동 시점은 추후 결정이다. 주소·담당·발급 전 준비 증거: {{First_상태서비스_승인과_증거}}. Root 인증서 자체에는 AIA/CDP를 넣지 않는다.

#### AIA·OCSP 채택 근거

| 공식 원문 | 확인한 요구·권고 | 이번 결정에 적용한 내용 |
|---|---|---|
| [C2PA CP v0.2 Certificate Status Services][cp-status] | Claim Signing 인증서는 OCSP 필수. Subordinate CA는 OCSP를 제공할 수 있고, 제공하지 않으면 CRL 필수 | First의 OCSP는 허용된 선택이며 CP가 First에 OCSP만 강제한다고 해석하지 않음 |
| [C2PA 기술 사양 2.4 §14.5.2][c2pa-spec-revocation] | 생성기의 OCSP·stapling 사용 및 CA의 OCSP AIA 포함 권고. 생성기는 CRL을 사용하지 않음. 서명에 포함하는 중간 CA의 OCSP 응답 첨부도 권고 | C2PA 콘텐츠 처리와 상태 응답 첨부 흐름에 맞춰 First도 OCSP 채택 |
| [공식 First YAML][first-profile] | CDP가 없으면 AIA 필수. AIA에는 OCSP 필수, caIssuers 권고, non-critical·HTTP URI | First AIA에 OCSP와 발급자 Root 인증서 다운로드 정보를 함께 포함 |
| [고정 First schema][first-schema] `allOf/5`, `allOf/6` | OCSP AIA/CDP 분기에 `oneOf` 사용. AIA의 caIssuers 존재 및 `http://` 주소 검사 | CDP 생략, OCSP·caIssuers 모두 포함하고 두 URL은 `http://`로 준비. 이는 고정 schema 호환 처리이며 일반 PKI에서 병행이 금지된다는 뜻은 아님 |
| [RFC 5280 §4.2.2.1](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.2.1) | AIA의 id-ad-ocsp는 상태 서비스 위치, id-ad-caIssuers는 발급자 인증서 정보 위치 | OCSP 응답 기능과 Root 인증서 다운로드 기능을 각각 준비. caIssuers만으로 폐지 상태를 제공한 것으로 처리하지 않음 |

CP·프로파일·schema의 적용 고정본은 기존 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`를 유지한다. 기술 사양 2.4는 OCSP 선택 이유의 보충 근거로 사용한다. U06의 6-A는 추가 선택 확장을 생략하는 정책이며, U04에서 확정한 상태 제공용 AIA를 제외하는 뜻이 아니다.

#### OCSP·URL 기능 준비 상태

| 항목 | 현재 상태 | 후속 작업 |
|---|---|---|
| First AIA·OCSP 방식 | **확정** | 실제 인증서 생성 시 승인값과 확장 대조 |
| OCSP URL (`id-ad-ocsp`) | **실제 URL 미정 / 제공 기능 미구현** | {{First_OCSP_HTTP_URL}} 확정, DNS·HTTP 접근과 OCSP 요청/응답 제공 구현 |
| Root 인증서 URL (`id-ad-caIssuers`) | **실제 URL 미정 / 다운로드 기능 미구현** | {{Root_caIssuers_HTTP_URL}} 확정, 발급자 Root 인증서 게시·다운로드 구현 |
| OCSP 응답자 | **미구현** | 응답자 키·인증서 준비, 상태 저장소·발급 원장 연계, 응답 서명·갱신 구현 |
| 운영·가동·검증 | **담당·가동 시점 미정 / 시험 미실시** | 두 URL의 동작, 응답 서명·상태·유효시각, 인증서 다운로드 내용과 운영 인수 증거 확보 |

이번 갱신은 정책·준비 상태 기록이다. 실제 URL을 가상 값으로 채우거나 서비스 구현·가동 완료로 표시하지 않는다. **S05 발급 전 준비 조건과 C04 미해결 상태는 유지**한다.

**방식 선택 참고:** AIA는 발급자 정보의 위치를 담는 확장이며 OCSP 주소와 caIssuers(발급자 인증서 다운로드) 주소를 담을 수 있다. CDP는 CRL 배포 위치를 담는다. 따라서 상태 제공 방식 비교는 OCSP 대 CRL이며 caIssuers 주소만 있는 AIA로 상태 제공을 대신하지 않는다. [RFC 5280 §4.2.2.1](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.2.1), [§4.2.1.13](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.13)

OCSP는 요청한 인증서의 상태 응답을 제공하고 CRL은 해당 목록 범위의 폐지 정보를 배포한다. 둘 다 서명·갱신·가용성 관리가 필요하다. OCSP도 미리 만든 응답을 제공할 수 있으므로 항상 실시간이라고 간주하지 않는다. 이번처럼 상태 대상 CA 인증서가 적고 서비스를 새로 구축하는 경우 CRL의 정적 배포가 더 단순할 수 있다는 것이 프로젝트 판단이며, 기존 OCSP 운영 기반·검증기 요구가 있으면 OCSP가 적합할 수 있다. [RFC 6960 §2·§2.5](https://www.rfc-editor.org/rfc/rfc6960.html#section-2), [RFC 5280 §5](https://www.rfc-editor.org/rfc/rfc5280.html#section-5)

**2026-10-12 C2PA 적용 범위 보완:** 위 운영 복잡도 비교와 C2PA 콘텐츠 처리 흐름의 권고를 구분한다. CP v0.2의 Certificate Status Services는 Claim Signing 인증서에 OCSP 제공을 의무화하고, Subordinate CA·Time Stamping 인증서는 OCSP를 선택하되 제공하지 않으면 CRL을 요구한다. 한편 [기술 사양 2.4 §14.5.2][c2pa-spec-revocation]는 claim generator에 OCSP·stapling 사용을 권고하고 CRL 사용을 금지하며, CA의 OCSP AIA 포함을 권고한다. 서명에 포함하는 중간 CA에도 OCSP 조회·응답 첨부 흐름을 설명한다. First의 CP상 CRL 허용을 콘텐츠 생성기의 CRL 처리 지원으로 확대 해석하지 않는다. **C2PA 전체 서비스와 응답 첨부의 일관성을 위해 First도 OCSP를 채택한다는 프로젝트 판단**을 결정 근거로 삼았다. 사용자 결정으로 U04의 방식 A를 확정했다. 추가 응답자와 두 URL의 제공 기능은 미구현이며 실제 체인·신뢰 앵커 배치의 검증도 남아 있다.

**이번 Root 키의 제약:** [CP Key Pair and Certificate Usage](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage)의 Root 서명 허용 목록에는 OCSP 응답자 인증서와 CRL이 있으나 OCSP 응답 자체는 없다. 따라서 방식 A에서는 Root 키로 응답을 직접 서명하는 경로를 기본안으로 두지 않고 별도 응답자 키·인증서·갱신 운영을 준비한다. 일반적인 위임 경로는 발급자 Root가 서명한 `id-kp-OCSPSigning` 인증서를 사용한다. 이 EKU는 응답자 인증서의 값이며 6-A에서 생략하기로 한 Root·First EKU와 구분한다. [RFC 6960 §4.2.2.2](https://www.rfc-editor.org/rfc/rfc6960.html#section-4.2.2.2)

[CP Certificate Status Services][cp-status]는 Subordinate CA에 OCSP를 제공하지 않으면 CRL로 상태를 제공하도록 하며, [Lifecycle Security Controls][cp-lifecycle]는 상태 정보의 가용성을 요구한다. **이번 행사의 승인 조건은 First 발급 시 상태 제공 준비가 완료되어 있도록 하는 것**이다. 이는 원문에 별도 유예가 확인되지 않은 데 따른 프로젝트 통제다. 늦추려면 허용되는 시점·제한에 관한 외부 해석·수용 근거를 확보해 승인해야 하며, 담당자·기한만 기입해 통과시키지 않는다.

S05 전에는 방식·실제 주소·서명 주체·게시/응답·갱신 절차와 사전 시험 증거를 확인한다. 발급 결과 저장과 실제 First serial의 상태 제공을 연결하는 절차도 준비한다. 확정한 방식 A의 위임 OCSP 응답자와 Root 인증서 게시 등 추가 준비 작업을 필수 선행 조건으로 연결한다. 해당 서명을 현재 CMD에 구현된 것으로 간주하지 않는다. S07에서는 실제 상태 조회와 지속 운영 책임 인수를 확인한다. C04는 이 증거를 확보할 때까지 미해결이다.

### 사용자 선택이 필요한 인증서 값

2026-10-12 사용자 결정으로 U02의 기간과 U03을 확정했다. **U01은 추후 결정**, **U04의 방식 A(AIA + OCSP)는 확정**했다. U04의 실제 URL·운영 값은 추후 결정이고 OCSP·URL 제공 기능은 미구현이다. U05는 5-A 난수 방식을 확정했고 U06은 6-A를 정책으로 확정했다. 아래 ID는 결정 이력을 위해 유지한다. U02의 실제 시작·만료 UTC 시각은 행사 일정에 맞춰 발급 전에 확정한다.

| ID | 선택·입력할 내용 | 규칙과 제안 |
|---|---|---|
| U01 | Root와 First 각각의 C·O·CN, 추가 DN 속성 여부 | **추후 결정.** 실제 조직·국가·CA 이름을 후속 확정. 가상 DN을 운영값으로 채우지 않으며 해당 CSR·인증서 본문 승인 전 확정 |
| U02 | Root·First 유효기간과 시작 기준 | **기간 확정:** Root 20년·First 5년. 사용자 요청으로 채택한 프로젝트 값. 실제 notBefore/notAfter UTC 시각과 시작 기준은 발급 전 확정 |
| U03 | Root pathLen | **확정:** `2`. Root → First → Issuing → leaf 구성을 수용. First는 규칙상 `1` 고정 |
| U04 | First AIA·OCSP와 실제 URL·운영 준비 | **방식 A 확정:** AIA에 OCSP·caIssuers 포함, CDP 생략. **OCSP·URL 제공 기능 미구현**, 실제 URL·운영 주체·가동 시점은 추후 결정. S05 발급 전 준비·검증 필요 |
| U05 | Serial 생성 정책 | **확정: 5-A.** CSPRNG 기반 최대 159-bit 양수·0 제외·원장 중복 차단. [근거와 상세 정책](#u05-serial-정책의-c2pa-기준과-일반-사례) 참조 |
| U06 | 선택 정책·확장 | **확정: 6-A.** 필수 및 schema 호환 확장 유지, 추가 정책·qualifier·EKU·기타 확장 생략. [근거와 대안](#u06-선택-확장의-c2pa-기준과-일반-사례) 참조 |

이 목록은 인증서·CSR 설정의 선택 항목이다. SKI/AKI의 실제 바이트와 공개키는 생성 후 계산할 값이며 사용자가 임의로 정하지 않는다. HSM 환경·실명/계정·생성 통제 구현·도구·백업·로그 등 기존 미정 항목은 아래 환경 표와 P02–P07에서 계속 관리한다.

### U05 Serial 정책의 C2PA 기준과 일반 사례

아래 일반 사례는 RFC와 CA 도구 공식 문서에서 확인할 수 있는 구현 유형이다. 사용 빈도나 모든 PKI에 공통인 의무를 뜻하지 않는다. **2026-10-12 사용자 결정으로 5-A 난수 방식을 확정했다.** 아래 비교는 선택 근거로 유지한다.

| 구분 | 내용 | 근거·이번 행사에서의 의미 |
|---|---|---|
| C2PA 필수 형식 | Root·First 모두 양수, 최대 20 octets | [Root][root-profile]·[First][first-profile]의 Serial Number. 난수라도 길이·양수 조건을 검사 |
| C2PA 권고 | 고엔트로피 Serial | 같은 원문은 고엔트로피를 권고하지만 최소 엔트로피 비트 수·CSPRNG 제품·UUID·고정 길이를 지정하지 않음 |
| PKIX 공통 규칙 | 같은 발급자가 발급한 인증서 간 Serial 고유성 | [RFC 5280 §4.1.2.2][rfc5280-serial]. 난수 생성만으로 중복 검사를 대체하지 않음 |
| 일반 사례 A — 난수 | 발급마다 난수 Serial 생성. OpenSSL CA는 `-rand_serial`을 지원하고, x509의 micro-CA 문서도 난수 생성을 권고하는 경로를 설명 | [OpenSSL ca][openssl-ca]·[OpenSSL x509][openssl-x509]. C2PA 고엔트로피 권고에 맞는 방향. 도구 기본값만 믿지 않고 양수·길이·중복 검사 필요 |
| 일반 사례 B — 순차 번호 | 발급자가 마지막 번호를 보관하고 증가시킴. OpenSSL x509의 `-CAserial` 경로가 이 방식을 제공 | [OpenSSL x509][openssl-x509]. 중복 없이 관리하면 PKIX 형식을 만족할 수 있으나, 단순 카운터는 C2PA의 고엔트로피 권고를 반영하지 못하므로 이번 행사에는 제안하지 않음 |

**이번 행사 확정 정책(5-A):** CSPRNG로 20 octets를 생성한 뒤 최상위 비트를 0으로 제한하고, 값이 0이면 다시 생성한다. 양수 범위는 `1`부터 `2^159-1`까지이며 20 octets의 DER INTEGER 한도 안에 들어가도록 최종 인코딩을 확인한다. 이는 고엔트로피 권고를 구현하기 위해 사용자가 채택한 프로젝트 정책이며 C2PA가 지정한 159-bit 규칙은 아니다.

Root 자기서명과 First 인증서는 모두 Root 발급 원장에서 예약·중복 검사한다. 서명할 본문 승인 전에 Serial을 고정하고 작업 ID·본문 해시와 연결한다. 충돌 시에는 **서명 요청 전** 새 후보를 만들고, 이미 서명 요청을 보냈거나 결과가 불명인 작업은 Serial만 바꿔 재발급하지 않고 [장애 판정](runbook.md#작업-원장과-장애-판정)을 따른다. CSPRNG·생성 도구·동시 예약 및 복구 구현은 후속 확정한다. 위 OpenSSL 옵션은 일반 사례의 근거이며 이번 CloudHSM 실행 도구를 채택했다는 뜻이 아니다.

### U06 선택 확장의 C2PA 기준과 일반 사례

**C2PA는 Root·First의 선택 확장을 한 묶음으로 추천하는 단일 기본안을 제시하지 않는다.** 고정 CP·프로파일의 필수/선택 조건과 명시된 권고를 아래처럼 구분한다. U06은 정책 OID·qualifier·EKU·기타 추가 확장을 다루며, 필수 KU·Basic Constraints·SKI/AKI를 생략하는 선택이 아니다. AIA/CDP는 추후 결정인 U04에서 관리한다.

보완 근거: [C2PA 기술 사양 2.4 §14.5.1.2][c2pa-spec-chain]는 CA 인증서에 EKU가 필수는 아니며 보통 포함하지 않는다고 설명하고, 존재하더라도 C2PA validator가 무시하도록 한다. 이는 이번 Root·First EKU 생략을 뒷받침한다. 추가 정책 OID·qualifier·모든 기타 확장을 일괄 생략하라는 권고로 확대하지 않는다. Claim Signing Issuing CA 등 다른 계층의 CP상 발급 프로파일은 별도로 준수한다.

| 항목 | C2PA의 요구·선택 범위 | 일반 PKI 사례와 이번 행사 검토 |
|---|---|---|
| Root Certificate Policies | 선택 확장. 포함하면 non-critical. 특정 OID 채택이나 확장 생략을 별도로 권고하지 않음 | 최소 구성은 정책 확장을 생략. 정책을 식별해야 하는 구성은 해당 CP/CPS를 나타내는 OID를 포함. 이는 구성 대안이며 사용자 확정 정책은 **생략** |
| First Certificate Policies | non-critical로 `1.3.6.1.4.1.62558.1.1` 필수. CA가 관리하는 IANA private arc의 CPS 정책 OID 추가 허용 | 최소 구성은 필수 C2PA OID만 포함. 조직 정책 식별이 필요하면 실제 관리 OID를 추가. C2PA OID를 조직 OID로 대체하지 않음 |
| Policy qualifier | First 프로파일은 선택으로 규정. CPS URI나 userNotice를 넣으라는 별도 권고는 없음 | OID만 쓰는 구성과 CPS 문서 URI를 넣는 구성이 있음. RFC 5280은 상호운용성을 위해 OID만 사용하도록 권고하고, 필요 시 CPS Pointer/User Notice를 정의. OpenSSL도 해당 구성을 지원 |
| Root·First EKU | 두 프로파일에 필수 EKU 없음. 기술 사양 §14.5.1.2는 CA EKU가 보통 없다고 설명하고 존재해도 validator가 무시하도록 규정 | 이번 상위 CA 확정 정책은 **생략**. 일반 PKI에서 EKU가 목적 제한에 쓰이더라도 C2PA validator의 CA 용도 제한 수단으로 가정하지 않음. 하위 Issuing/leaf의 CP 필수 EKU와 구분 |
| 기타 추가 확장 | 이번 Root·First 프로파일에 추가 필요가 명시되지 않은 항목은 개별 근거 검토 필요 | 이름 제한(Name Constraints), 정책 제한(Policy Constraints)처럼 하위 인증 경로를 제한할 목적이 있을 때 추가하는 구성이 있음. 구체 제한 요건이 없는 현재 기본안은 **추가하지 않음** |

C2PA 근거: [Root 프로파일][root-profile]·[First 프로파일][first-profile]·[CP][cp-source]. 일반 PKI 근거: [RFC 5280 Certificate Policies][rfc5280-policies], [EKU][rfc5280-eku], [Name Constraints][rfc5280-name-constraints], [Policy Constraints][rfc5280-policy-constraints], [OpenSSL 확장 설정][openssl-extensions]. 일반 사례는 이 표준·도구로 구성할 수 있는 유형을 뜻하며 특정 CA 사업자의 운영 사례나 C2PA 권고로 인용하지 않는다.

| 구성 사례 | Root | First | 선택이 필요한 경우 |
|---|---|---|---|
| A — 필요한 확장만 포함 (**사용자 확정 정책, 6-A**) | 필수 및 schema 호환 확장 유지, Certificate Policies·EKU·기타 추가 확장 생략 | 필수 확장과 C2PA 정책 OID 유지, 추가 정책 OID·qualifier·EKU·기타 추가 확장 생략 | 별도의 조직 정책 식별·추가 경로 제한 요구가 없는 경우. U04에서 확정한 AIA(OCSP·caIssuers)는 유지 |
| B — 조직 CP/CPS 식별 | 필요하면 조직 정책 OID를 non-critical로 포함 | 필수 C2PA OID에 조직의 실제 정책 OID를 추가하고 필요하면 CPS Pointer 포함 | 실제 OID 관리 권한, 적용 CP/CPS와 공개 URI가 정해진 경우 |
| C — 추가 경로 제한 | 필요가 입증된 제한만 별도 설계 | 이름·정책·용도 제한을 목적에 맞게 추가 설계 | 하위 발급 범위 제한 요구가 있을 때. critical 여부·전체 체인·검증기 호환 검토 후 결정 |

2026-10-12 사용자 요청으로 **6-A를 정책으로 확정했다**. 추가 요구가 생기면 B/C안을 다시 검토하되 현재 설정에 자동 추가하지 않는다. Root 정책 확장 생략이나 First의 qualifier 생략은 CPS 작성·공개 등 다른 CP 의무를 면제한다는 뜻이 아니다. B/C안이 필요하면 실제 OID·URI·제한값을 받아 별도 승인하고 CSR 요청 확장과 최종 인증서 설정의 차이도 함께 관리한다.

### 환경과 보호 설정

| 환경과 보호 항목 | 승인값 또는 근거 |
|---|---|
| AWS 계정·리전·클러스터 | AWS CloudHSM 사용. 리전 후보는 사용자 표기 `UW2`를 `us-west-2`(US West / Oregon)로 해석하며, 최종 확정은 미완료. AWS 계정·클러스터 ID는 미정 |
| HSM 모델·모드·보안 수준 | 사용자 결정: `hsm2m.medium`, 클러스터 `FIPS` 모드, FIPS 140-3 Level 3 인증 모듈 사용. AWS가 제시한 인증 근거는 CMVP 4703. 실제 배포 모듈·펌웨어·승인 모드와 인증 조건의 대응 증거는 구축 후 확인. CP 저장 조항의 문구 차이는 아래 N01에 기록 |
| HSM 환경 준비 상태 | 현재 미구축이며 신규 구축 예정. 리허설과 실제 운영용 키 생성 행사에서는 구축된 환경을 사용할 계획. 구축·초기 설정·접속 확인의 실제 결과, 리허설/운영 환경 분리와 클러스터 구성은 미확정 |
| 실행 호스트·접근·네트워크·코드·검증 도구 | 명령 실행용 전용 EC2 사용. 외부 작업자 단말 → VPC 내 jumphost → 전용 EC2로 접속하며, 전용 EC2의 작업자 접속은 작업자 계정으로 제한. 작업자가 CloudHSM CLI로 키 생성·서명을 요청. EC2 식별자·OS·인증 방식·네트워크 허용 규칙·CLI/SDK 버전·코드·검증 도구의 버전과 해시는 미정. [실행 환경과 역할 분담](#실행-환경과-역할-분담) 참조 |
| 키 생성 통제 | 별도의 다인 승인과 승인된 명령만 실행하는 통제 방향을 잠정 반영. 키 생성 명령 자체에 HSM quorum이 적용된다고 간주하지 않는다. **생성 승인은 O·A·B 중 서로 다른 2명(2 of 3)으로 확정.** 인증 수단·접근 활성화·제한된 실행·우회 시험은 후속 작성·검증. 아래 N02 참조 |
| 서명 quorum | 사용자 결정: S02/S04/S05에 AWS CloudHSM의 키별 `key-usage` quorum 사용. 작업자 O와 승인자 A·B, 서로 다른 3명 중 2명이 승인하는 `2 of 3`. O의 자기승인 허용. 키 사용 quorum 값은 `2`. 실명·CU 계정·승인키·실제 명령·시험은 미정. [서명 quorum 결정](#서명-quorum-결정) 참조 |
| 키 관리 quorum·우회 시험 | 잠정 반영: Root·First 개인키 각각 `key-management` 값 `2`, O·A·B 중 서로 다른 2명 승인. 서명 quorum과 별도 토큰 사용. 실제 계정·공유·등록키·권한·잠금 상태의 관리 시험은 미완료. [키 관리와 관리자 통제](#키-관리와-관리자-통제) 참조 |
| HSM 관리자 quorum | 잠정 반영: 서로 다른 3명의 개인 관리자 계정, `user`·`quorum`·`cluster` 각 값 `2`. CU 계정·승인키와 관리자 역할을 구분. 실명·계정·등록키·초기 설정·시험은 미정 |
| 속성 잠금·개별 키 삭제·폐기 | 개인키 생성 시 `modifiable=false`, `destroyable=false`를 적용하는 기본안을 잠정 반영. 키 삭제 자체는 네이티브 quorum 대상이 아님. 폐기 경로·백업 처리·공유 클러스터 영향과 잠금/삭제 거부 시험 완료 전 운영 키 생성 금지. [N03](#n03-속성-잠금과-폐기-검증-조건) 참조 |
| 별도 통제할 AWS API·실행 환경·승인키 변경 | 백업 복원·복사·삭제·보존 변경, HSM/클러스터 삭제, EC2/jumphost/네트워크/실행 코드 변경, 승인키 등록·교체는 별도 다인 승인 실행과 권한 분리로 설계. IAM/SCP만으로 다인 승인이 구현된 것으로 보지 않음. 정족수·정책·실행 경로·우회 시험은 미정 |
| 개인 계정·승인 키·활성화 재료 | {{목록_관리자_보호_위치_참조}} |
| 입회·시간·로그·증거 보존·접근 통제 | {{입회와_기록_정책}} |
| 로그 수집·검토 | {{HSM별로그_CloudTrail_호스트_실행기_승인기록_원천과_사람계정연결_시각오차_검토자}} |
| 인증서 발급 기록 보존 | CP 적용 인증서의 만료 후 최소 1년 이상 / {{구체_종료일_권한_복구검사}} |
| 기타 기록 보존 | {{스크립트_승인_로그_영상별_기산점_기간_권한_조회방법}} |
| 생성 직후 보호·백업·off-site·복구 | 개인키의 일반 반출을 차단하고 CloudHSM의 암호화된 클러스터 백업으로 복구하는 방향 확정. 원본과 같은 다인 통제 적용. off-site 위치·보존·복원 권한·신규 키 포함 확인·복구 시험·책임자: {{보호_계획_복구시험_책임자}} |
| 키 외 중요 자료 백업 | {{원장_설정_감사로그_승인_증거목록의_백업과_복원검사}} |
| 종료 시 접근 유지·회수 | {{남길_HSM계정공유와_회수할_임시접근_세션_토큰_검사}} |
| First 요청 권한·발급 허가 | {{요청_검증과_허가_기록}} |
| 장소 보안·행사 후 물리 보관 | {{적용_여부_근거와_해당시_절차}} |

## 키와 서명 알고리즘 결정

사용자의 “전부 ecd 384”는 **Root와 First ICA 모두 ECDSA 서명용 P-384 키를 사용하는 결정**으로 반영한다. 두 CA는 같은 알고리즘을 사용하되 각각 별도의 키 쌍을 생성한다. 해시는 P-384에 맞춰 SHA-384를 선택하며, 이는 이번 행사의 프로젝트 선택이다.

| 대상 | 사용할 키 | 서명 알고리즘·해시 |
|---|---|---|
| S02 Root 자기서명 인증서 | Root P-384 키 | ECDSA + SHA-384 |
| S04 First CSR | First P-384 키 | ECDSA + SHA-384 |
| S05 First 인증서 | Root P-384 키. 인증서에는 First P-384 공개키 수록 | ECDSA + SHA-384 |

C2PA v0.2의 [Root 공식 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml)과 [First 공식 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml)은 ECC 곡선 P-384와 ECDSA SHA-2 계열 서명을 허용한다. P-384는 허용된 곡선 중 이번 행사에서 선택한 값이며, 모든 프로파일 검사나 적합성 심사가 완료되었다는 뜻은 아니다.

CloudHSM의 [EC 생성 명령](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html)에는 `--curve secp384r1`, [ECDSA 서명 명령](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html)에는 `--hash-function sha384`를 반영한다. 실제 명령은 키 속성·계정·입출력·CLI 버전을 정한 뒤 완성하고 시험한다.

인증서·CSR의 서명 식별자는 `ecdsa-with-SHA384` (`1.2.840.10045.4.3.3`)를 사용한다. AlgorithmIdentifier의 parameters는 생략한다. [RFC 5758 §3.2](https://www.rfc-editor.org/rfc/rfc5758.html#section-3.2)

CLI raw/digest 입력 방식과 변환 도구는 미정이다. 어느 방식을 선택하든 고정 본문에 대해 SHA-384를 한 번 적용한 ECDSA 서명이 되도록 정의한다. CloudHSM의 원본 `r||s` 서명 응답은 보존하고 인증서·CSR 조립에 필요한 ASN.1 DER 형식으로 변환한다. [AWS 서명 입력·출력 정의](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html)

이 선택은 CA 키와 위 세 서명 작업에 적용한다. 증거 파일의 SHA-256 식별 해시와 AWS quorum 토큰의 승인키·서명 규칙은 별도로 관리한다. AWS CU quorum 초기 설정 문서의 승인키는 RSA 2048이며 이를 CA용 P-384 키로 대체하지 않는다. [AWS quorum 승인키 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html)

## 개인키 용도와 추출 검토

사용자 결정: **Root·First 개인키는 서명 전용으로 사용하고, 일반 반출은 `extractable=false`로 금지한다.** 복호화·키 파생·다른 키 unwrap을 금지하고, 개인키로 암호화·검증·다른 키 wrap을 수행하는 용도도 허용하지 않는다. `sensitive=true`, `token=true`로 보호·영구 보관을 설정한다. 공개키 출력·공개키의 서명 검증과 승인된 백업·관리는 별도 절차를 따른다.

| 항목 | 확정 정책과 남은 작업 |
|---|---|
| 확정한 용도 속성 | `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false` |
| 그 밖의 용도 | 실제 개인키 조회에서 암호화·검증·wrap 용도가 활성화되지 않았는지 확인. private key에서 생성 인자로 지원하지 않는 속성은 전달하지 않음 |
| 개인키의 모듈 밖 평문 존재 | C2PA CP가 금지. 실제 개인키를 EC2 파일·메모리에서 평문으로 사용하는 방식 금지 |
| 일반 개인키 반출 | `extractable=false`를 생성 시 적용. 일반 wrap/export를 통한 암호화 반출도 차단. CP가 이 AWS 속성값 자체를 지정하는 것은 아니며, 사용자 요청으로 권고 채택 |
| 보호·영구 보관 | 생성 시 `sensitive=true`, `token=true` 적용. 세션 키로 생성하지 않음 |
| 백업·복원 | CloudHSM의 암호화된 클러스터 백업을 사용하도록 설계. 원본과 같은 다인 통제 적용. off-site 위치·권한·보존·백업 포함/복원 시험은 미정 |

CP는 평문 반출을 금지하면서 보호된 백업과 off-site 사본을 요구한다. 모든 암호화 반출을 일괄 금지하는 요구로 해석하지 않는다. 이번 일반 반출 차단은 실제 개인키 파일이 필요 없는 운영 흐름과 HSM 안의 `2 of 3` 서명 통제를 유지하려는 프로젝트 선택이다. 근거·백업과의 구분·이식성의 대가는 [개인키 추출 조사](../../../references/cloudhsm-ca-key-extraction-2026-10-11.md)에 정리했다. 사용자 요청에 따라 이 권고를 채택했으며, 실제 설정·시험 완료와 구분한다.

원문: [CP의 CA 키 저장·사용·백업 통제](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys), [AWS 키 속성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html), [AWS 백업 보안](https://docs.aws.amazon.com/cloudhsm/latest/userguide/data-protection-backup-security.html).

CloudHSM에서 `extractable=false`는 나중에 `true`로 되돌릴 수 없으므로, 일반 반출로 다른 공급자의 HSM에 키를 이전하는 경로는 사용하지 않는다. 실제 속성·백업 포함·복원 후 보호 유지 여부는 테스트 키로 검증한다. 키 관리 quorum·속성 잠금과 별도 통제의 기본안은 아래에 잠정 반영했다. `modifiable=false`·`destroyable=false`의 적용은 폐기 계획과 시험 확인을 운영 생성의 선행 조건으로 둔다.

## 키 관리와 관리자 통제

사용자의 “일단 전부 반영하고 나중에 재검토” 요청에 따라 다음 기본안을 행사 초안에 반영한다. 구현·시험 완료나 운영 수행 승인은 아니다. 선택 이유·공식 근거·대안·재검토 질문은 [별도 재검토 기록](key-management-control-review.md)에 보관한다.

| 통제 | 기본안과 적용 범위 | 시행 전에 확인할 조건 |
|---|---|---|
| 개인키 관리 quorum | Root·First 각각 값 `2`. 키 소유자와 공유 CU를 서로 다른 O·A·B에 대응시키고 O+A·O+B·A+B 허용. O의 자기승인은 유효한 개인 토큰 서명이 있을 때만 계산 | 소유 CU만 수행할 수 있는 관리 작업의 실행자 지정, 현재 승인 집합·등록키와 작업 전후 조회, 단독·중복·집합 밖 승인 거부 |
| 속성 잠금 | 생성 시 `modifiable=false`. 관리 승인을 충족해도 금지한 기능을 켜거나 속성 잠금을 해제하지 않음 | 잠금 동작, 공유·공유 해제·승인자 교체의 별도 동작, 폐기 방법과 잠금 해제 불가 영향 검증 |
| 개별 키 삭제 차단 | 생성 시 `destroyable=false`. 삭제 자체에 관리 quorum이 붙는다고 기록하지 않음 | 소유자의 직접 삭제 거부 확인, 관련 백업·복사본을 포함한 폐기 계획과 공유 클러스터 영향 확인 |
| 관리자 user·quorum·cluster | 개인별 관리자 계정 3개와 독립 보호한 승인키, 각 서비스 값 `2` | 모든 HSM의 최종값 인수, 관리자 변경·정족수 낮추기·MFA·mTLS 변경 단독 거부, 초기 설정 중간값과 최종값 구분 |
| 승인자 명단·등록키 | 공유 변경을 승인자 집합 변경으로 취급. O·A·B 외 추가는 현재 정책에서 금지. 교체는 명단·정책·등록키를 함께 변경 승인 | 신원·공개키 지문·중복 소유 확인, 단독 등록/교체·관리자 우회와 복원 후 과거 승인키 부활 시험 |
| 키 생성·AWS API·호스트/코드 | 별도 작업 계획 다인 승인과 제한된 실행 경로. 권한 정책·승인 검사 코드의 변경도 분리 | 직접 CLI/API·다른 호스트/SDK·관리자·정책/코드 변경 우회 차단. 정족수·계정·실제 프로그램은 후속 확정 |

관리 quorum은 공유·공유 해제·속성 변경·wrap·unwrap을 지원한다. 이 중 금지한 암호 연산은 quorum 승인으로 허용하지 않는다. 토큰에는 해당 `key-management` 서비스를 사용하고 키 사용 토큰과 혼용하지 않는다. 관리자 `quorum` 서비스는 관리자 서비스 값 변경 보호이며 개인키의 사용·관리 값 설정과 구분한다. [AWS 지원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html), [관리자 값 변경](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm-token-set-qm.html)

현재값·변경값·명령·대상 키·승인자 명단·기한을 별도 작업 계획으로 고정한다. AWS 토큰만으로 특정 변경값과 명령 전체가 고정된다고 가정하지 않으며, 실행 직전 대조와 사후 조회를 기록한다. `modifiable=false`가 공유나 승인키 등록까지 잠근다고 단정하지 않고 실제 동작을 시험한다. [관리 quorum 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

AWS API 작업의 접근 권한은 IAM 및 필요 시 SCP로 제한하고 별도 승인 실행 경로에 연결한다. 승인 기록만 있고 직접 실행 권한이 남아 있으면 통제 완료로 보지 않는다. 복원한 환경은 백업 시점 사용자·설정·정책을 현재 명단·등록키·quorum·속성·접속 정책과 대조하기 전 사용하지 않는다. [IAM 작업 목록](https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudhsm.html), [백업 복원](https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster-from-backup.html)

공개키에는 AWS 개인키 quorum이 적용되지 않으며, 공개키 출력·검증·보관은 별도 관리한다. 위 잠금 설정은 CA 개인키에 대한 기본안이며 공개키 세부 속성은 실제 명령 작성 시 확정한다.

## 보안 선택과 특이사항

### N01 CP의 FIPS 판본 문구 차이

CP v0.2의 `Key Pair Generation and Installation by CAs`는 키 생성에 FIPS 140-2 또는 140-3 Level 2 이상을 허용한다. 반면 `Controls for CA Keys / Key Storage`는 FIPS 140-2 Level 2 이상으로만 표현한다. [고정 CP 원문](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md)

이 차이를 특이사항으로 기록하고, 이번 행사는 현행 FIPS 140-3의 Level 3 인증 모듈과 FIPS 모드를 사용하는 보안 방향으로 결정한다. Level 2 최소 등급보다 높은 인증 등급을 선택하는 프로젝트 결정이며, 저장 조항의 문구를 임의로 바꾸거나 외부 적합성 수용이 완료되었다고 기록하지 않는다. 문구 차이에 대한 외부 해석·수용 근거는 아직 확보하지 않았다.

AWS는 `hsm2m.medium`을 FIPS 140-3 Level 3 및 CMVP 4703에 연결한다. 해당 인증은 승인 모드와 정해진 설치·초기화·구성 조건을 전제로 하므로, 구축 후 실제 모듈·펌웨어·모드의 대응 자료를 준비한다. [AWS 인증 안내](https://docs.aws.amazon.com/cloudhsm/latest/userguide/fips-validation.html), [NIST CMVP 4703](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4703)

**행사 승인 조건:** C2PA 측의 저장 조항 적용 해석·수용 근거와 실제 모듈·펌웨어·FIPS 모드의 인증 대응 자료를 함께 확보한다. 해석 자료에는 적용 CP 판본·대상 구성·발행 주체·일자·답변 범위와 남은 조건을 기록한다. 담당자·요청/회신 위치: {{N01_확인담당과_외부근거}}. 현재 외부 회신은 미확보이며 N01은 미해결이다. 보안 등급 선택이나 이번 설정표 작성만으로 해소하지 않고, 근거 미확보 시 운영 행사 승인을 보류한다.

### N02 키 생성 승인과 생성 시 quorum 설정의 구분

AWS의 CloudHSM CLI quorum 지원 작업 목록에는 키 서명과 일부 키 관리 작업이 있으나 키 생성 명령은 열거되어 있지 않다. 생성 시 지정하는 키 사용·관리 quorum 값은 **생성된 키의 이후 사용·관리에 적용되는 값**이며, 생성 요청 자체에 여러 사람의 HSM 토큰 승인이 적용된다는 뜻이 아니다. [AWS quorum 지원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html)

**2026-10-12 사용자 요청 반영: Root·First 키 생성 승인도 O·A·B 중 서로 다른 2명(2 of 3)으로 정한다.** O+A·O+B·A+B를 허용한다. 작업자 O도 생성 계획을 명시적으로 승인하면 1명으로 세지만 명령 실행 자체를 승인으로 세지 않는다. Root와 First는 각각 별도 계획·작업 ID로 승인하고 승인 대상은 대상 환경, 키 종류·알고리즘·속성, 소유·공유 및 이후 사용·관리 quorum이다. 독립 입회·검증은 생성 승인 인원과 별도 역할이다.

[고정 CP v0.2의 Key Pair Generation and Installation by CAs][cp-generation]는 다인 통제·지식 분할을 요구하며 생성 승인에 3명 전원을 지정하지 않는다. [Separation of Duties][cp-duties]의 다인 접근 통제와 함께 보아 2 of 3은 이번 프로젝트의 통제 정책으로 채택한다. 승인 인원만으로 준수를 선언하지 않으며, 한 사람이 승인 재료·권한을 모두 보유하거나 다른 경로로 단독 생성할 수 없도록 구성·검증해야 한다.

**생성 승인 방식 확정:** O·A·B는 각자 독립 보유한 개인 승인용 키로 같은 생성 계획에 서명한다. 앱은 사전에 신원을 확인한 승인 명단의 공개키로 서로 다른 2명 이상의 서명을 검증하고 승인된 계획의 생성만 허용한다. 계획에는 전체 승인자 명단·CU 계정·공개키 지문·대상 환경·키 속성·소유/공유·사용/관리 quorum·작업 ID·기한을 포함한다.

생성 계획 검증에 사용한 것과 **같은 개인 승인용 공개키를 각자의 CloudHSM CU에 등록**한다. 최초 등록 시 AWS 등록 토큰에는 별도로 서명하고, 등록이 완료돼 있으면 공개키·계정 연결을 대조한다. O·A·B 세 명의 등록을 확인한 뒤, 생성 명령에서는 해당 CU들의 소유·공유 관계와 quorum 값을 설정한다. 생성 후 실제 키 설정을 승인 계획과 대조한다. 개인 승인키는 Root·First CA 키와 별개이며 앱에 개인키를 모으지 않는다. [AWS 등록·생성 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html)

**CA 인증서 발급과 CSR 서명:** S02/S04/S05는 같은 승인자가 같은 개인 승인키로 작업별 새 HSM key-usage 토큰에 서명하고, CloudHSM이 2 of 3을 검증해 CA 키의 서명을 수행한다. 생성 계획 승인·등록 토큰·사용 토큰의 서명은 서로 대체하거나 재사용하지 않는다. [AWS quorum 사용](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

공개키 소유자 확인, 승인 명단의 변경 통제, 승인된 생성 옵션과 실행의 일치, 앱 검사를 건너뛰는 단독 생성 방지를 준비 조건으로 둔다. 앱·명령·인증 수단 보호·우회 차단의 구현 상세는 후속 개발 작성 사항으로 미룬다. 기존 S01/S03 및 G01/G05는 구현·시험 완료를 뜻하지 않는다. 생성 통제 검증 전에는 N02를 종료하지 않는다.

검토 자료는 [키 생성 승인 검토안](key-generation-control-review.md)에 연결한다. 기존의 3인 전원 승인 제안은 이번 2 of 3 결정으로 대체한다. 실제 신원·계정·승인키 보호·구현은 후속 작성한다. 계획 승인 서명과 생성된 CA 키를 사용하는 AWS 서명 quorum을 구분한다.

### N03 속성 잠금과 폐기 검증 조건

`modifiable=false`·`destroyable=false`를 생성 시 적용하는 기본안을 잠정 반영한다. AWS에서 `modifiable`은 false에서 true로 되돌릴 수 없으며, 개별 객체 삭제 허용 여부는 `destroyable`과 구분한다. 관리 quorum 승인은 속성 잠금을 해제하는 수단이 아니다. [AWS 속성 정의](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html), [PKCS #11 객체 속성](https://docs.oasis-open.org/pkcs11/pkcs11-base/v2.40/pkcs11-base-v2.40.html)

잠금·소유자 삭제 거부·승인자 교체와 복구를 테스트 키로 검증하고, 키·관련 백업/복사본의 폐기 경로 및 공유 클러스터의 다른 키 영향을 확인해야 한다. 완료 전 운영 키 생성은 금지한다. 실패하면 값을 임의로 완화하지 않고 재검토·변경 승인·필요한 재시험을 거친다. 전체 HSM·클러스터·백업 삭제는 이 속성의 보호 대상이 아니므로 별도 다인 통제가 필요하다. 검토 기준과 기록란은 [별도 재검토 기록](key-management-control-review.md#다시-검토할-항목과-판정-기록)에 연결한다.

## 서명 quorum 결정

사용자 결정: **작업자 O를 포함한 서로 다른 3명 O·A·B 중 2명이 승인한다(`2 of 3`).** O는 CLI 실행자이면서 승인자일 수 있고, 자신의 승인용 개인키로 토큰에 서명한 경우에만 승인 1명으로 센다. CLI 명령을 실행했다는 사실만으로 승인 수에 포함하지 않는다.

| 항목 | 확정한 규칙 |
|---|---|
| 적용 작업 | S02 Root 자기서명, S04 First CSR 서명, S05 Root 키의 First 인증서 서명 |
| 승인 가능한 사람 | 작업자 O, 승인자 A, 승인자 B의 3명. 실제 신원·개인 CU 계정·등록 승인키 지문은 추후 작성 |
| 필요한 승인 | 서로 다른 2명의 유효한 토큰 승인 서명 |
| 허용 조합 | O+A, O+B, A+B. 세 명 모두 승인해도 충족 |
| 실행 담당 | O. A+B가 승인한 경우에도 O가 CLI로 실행하며, 이 경우 O의 토큰 승인 서명은 필수가 아님 |
| AWS 키 설정 | Root·First 개인키의 사용 quorum 값 `2`. 키별 소유·공유 CU와 등록 승인키를 O·A·B에 대응시키고, 승인 가능한 집합이 이 3명과 일치하는지 확인 |
| 거부 조건 | 승인 0명·1명, 동일인의 중복 승인, 집합 밖 승인으로 인원 충족, 만료·작업/키 불일치 |
| 기록할 내용 | 승인 가능 집합, 실제 승인자와 조합, 개인별 승인키 지문·시각·검사, 실행자와 명시적 실행 지시 |

각 작업의 실제 승인자는 같은 고정 본문을 검토하고 본문 승인과 토큰 승인을 작업 ID로 연결한다. 생성 계획 승인에 사용한 것과 같은 개인 승인키로 작업별 새 HSM 토큰에 서명하며, 생성 계획의 서명을 재사용하지 않는다. 검증자 V의 독립 검사·발급 허가·입회 등 다른 역할은 해당 절차를 따른다. 생성도 2 of 3을 채택했지만 생성 계획 승인과 이 HSM 서명 승인은 별도 절차다. 키 관리 quorum은 별도 선택으로 [키 관리와 관리자 통제](#키-관리와-관리자-통제)에 잠정 반영한다.

설정·명령 작성과 시험은 아직 미완료다. [공통 Q01–Q08](runbook.md#공통-서명-절차-q01부터-q08)과 [리허설과 통제 시험](preparation.md#리허설과-통제-시험)에 연결한다. 요청자의 자기승인 가능 여부는 [AWS quorum 설명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli.html)을 근거로 한다.

## 실행 환경과 역할 분담

사용자가 지정한 구성 방향이며, 구축·접근 제한·통제 시험 완료를 뜻하지 않습니다.

| 구성 요소 | 역할과 사용 방식 |
|---|---|
| 외부 작업자 단말 | 작업자가 jumphost를 거쳐 전용 EC2에 접속하는 단말 |
| jumphost | 외부에서 VPC 내 전용 EC2로 접속하는 경유 호스트 |
| 명령 실행용 전용 EC2 | 작업자 계정만 작업자 접속을 허용. 작업자가 CloudHSM CLI를 실행해 Root·First 키 생성과 CSR·인증서 서명을 요청 |
| 요청·본문 작성 애플리케이션 | CloudHSM CLI와 같은 전용 EC2에서 별도 애플리케이션으로 실행. CSR·인증서 발급 요청과 서명할 본문을 작성해 EC2 내부의 작업 파일로 저장하고, 작업자가 확인한 파일을 CLI 서명 입력으로 사용 |
| AWS CloudHSM | 전용 EC2의 CLI 요청을 받아 지정된 키를 생성하거나 서명을 수행 |

애플리케이션에서 준비한 요청·본문을 CLI 실행 입력으로 연결하는 흐름은 [runbook.md](runbook.md#실행-환경과-작업-흐름)에 기록합니다. 같은 EC2 내부의 파일로 연결하며, 실제 작업 디렉터리·파일명·접근 권한·입력 대조 방법은 미정입니다. 서명값을 반영한 CSR·인증서 조립 도구, 승인·독립 검사·기록 방법은 후속 상세 정의에서 확정합니다. 전용 EC2의 작업자 접속 제한과 HSM 키 사용에 필요한 승인·정족수는 각각 설정·시험합니다.

## 사람과 권한의 연결

역할 배정은 [스크립트 명부](script.md#역할자-명부)의 5명 구성을 따른다. Administrator가 진행·검증·기록·운영 인수를 겸하고 Crypto Officer가 Key Custodian 1을 겸한다. Key Custodian 2·3과 Independent Witness는 별도 사람이다. 기존 설정 항목의 식별자를 보존하기 위해 사용하는 대응은 P/V/R/C=Administrator, O=Crypto Officer(Key Custodian 1), A=Key Custodian 2, B=Key Custodian 3, W=Independent Witness이다. 이 식별자는 추가 인원을 뜻하지 않는다. HSM 관리자 겸임은 스크립트의 계정 분리·단독 우회 방지 조건을 적용한다.

| 사람·역할 | CU 또는 admin 계정·승인 공개키 지문 | Root와 First 소유·공유 | 허용 작업·승인 집합 | 등록·교체·복구 권한과 부정 시험 |
|---|---|---|---|---|
| Crypto Officer / Key Custodian 1 | {{O_개인_CU_계정과_등록키_지문}} | {{O_Root_First_소유공유_관계}} | CLI 실행. 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함, 유효한 토큰 자기승인 허용. 소유자 전용 명령의 실행 권한은 계정 매핑 후 확정 | {{O_등록교체복구_권한과_시험참조}} |
| Key Custodian 2 | {{A_개인_CU_계정과_등록키_지문}} | {{A_Root_First_소유공유_관계}} | 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함 | {{A_등록교체복구_권한과_시험참조}} |
| Key Custodian 3 | {{B_개인_CU_계정과_등록키_지문}} | {{B_Root_First_소유공유_관계}} | 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함 | {{B_등록교체복구_권한과_시험참조}} |
| HSM Administrator 3명 — Key Custodian 1·2·3의 겸임 가능, 실제 배정 미정 | {{개인별_admin_계정과_등록키_지문}} | CU의 소유/공유와 별도 역할 | user·quorum·cluster 각각 `2 of 3`. 같은 사람이 CU와 겸임하더라도 계정·역할별 재료를 구분하고 한 사람이 다른 사람의 재료까지 보유하지 않음 | {{관리자_등록교체복구_권한과_시험참조}} |
| {{기타_사람과_역할}} | {{계정과_등록키_지문}} | {{키별_관계}} | {{기타_허용작업과_승인집합}} | {{등록교체_권한과_시험참조}} |

| 통제 행위 | 각자 보유·보호할 재료와 권한 | 단독으로 수행할 수 없는 이유 | 허용·거부 시험 및 당일 확인 |
|---|---|---|---|
| 생성·생성 접근 활성화 | O·A·B가 각자의 개인 승인키를 독립 보유. 앱은 고정 명단의 공개키로 생성 계획 서명 검증 | 서로 다른 2명 승인 후 승인된 계획만 실행. 단독 생성·명단/설정 변경·직접 접근 우회 차단 필요 | 승인 부족·동일인 중복·계획 변경·직접 실행 거부와 생성 결과 대조 / {{생성_시험과_G01_G05}} |
| 서명 | O·A·B 각자의 승인용 개인키, 개인 CU 계정·등록키와 연결. 보관·교체·복구 상세는 미정 | 사용 quorum `2`와 승인 가능 집합 3명으로 서로 다른 2명의 승인을 요구. 실제 설정·우회 차단은 구현·시험 필요 | O+A·O+B·A+B 성공, 단독·중복·집합 밖 승인 거부 / {{서명_직접SDK_우회시험과_Q절차}} |
| 키 관리 | O·A·B 각자의 CU 승인키. 소유 CU의 실행 권한과 공유 CU의 승인 권한 구분 | 관리 quorum `2`. 공유 전후 명단 대조. 잠긴 속성과 금지 연산은 승인 수 충족으로 허용하지 않음 | 관리 단독·중복·집합 밖 승인 거부, 2명 승인 허용, 잠금 상태의 공유 변경 / {{관리_시험참조}} |
| 관리자·승인키 등록/교체 | 개인별 admin 계정·승인키. 승인 공개키 등록/교체는 별도 신원·지문·명단 변경 승인 | user·quorum·cluster 각 `2`. 등록/교체까지 자동 보호된다고 가정하지 않고 단독 교체 경로를 별도 통제 | {{관리자_등록교체_단독거부_시험과_B00}} |
| 백업 복원·삭제·호스트 변경 | 별도 다인 승인 실행 경로와 분리한 IAM/호스트/코드 변경 권한. 구체 정족수 미정 | 직접 실행·권한 정책·승인 검사 코드 변경 우회 차단. 복원 후 과거 사용자·승인키·정책 대조 전 사용 금지 | {{별도통제_시험과_B01_X01}} |

지식 분리의 적용 설명과 검토 근거: {{지식분리_설명과_검토}}. 사람 승인 quorum과 HSM 노드 가용성 quorum은 별도로 확인합니다.

## 최종 보관 기준

최종 자료와 마지막 판정까지의 보존·복제 계약: {{최종_보관_절차와_완료기준}}.

위 보존 정책에 따라 승인본, 실제 수행 기록, 확인 서명, 종료·최종 판정과 그 저장 확인까지 보관합니다. 실제 보관 결과는 [수행 기록](records/record-template.md)에 남기고 파일별 위치와 해시는 [증거 목록](evidence-index.md)에 연결합니다.

[cp-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[cp-status]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-status-services
[cp-lifecycle]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#lifecycle-security-controls
[root-profile]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml
[first-profile]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml
[root-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json
[first-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCA.cert.schema.json
[first-csr-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCA.csr.schema.json
[rfc5280]: https://www.rfc-editor.org/rfc/rfc5280.html
[rfc5480]: https://www.rfc-editor.org/rfc/rfc5480.html
[rfc5758]: https://www.rfc-editor.org/rfc/rfc5758.html
[rfc2986]: https://www.rfc-editor.org/rfc/rfc2986.html
[rfc2985]: https://www.rfc-editor.org/rfc/rfc2985.html
[rfc5280-serial]: https://www.rfc-editor.org/rfc/rfc5280.html#section-4.1.2.2
[rfc5280-policies]: https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.4
[rfc5280-eku]: https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.12
[rfc5280-name-constraints]: https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.10
[rfc5280-policy-constraints]: https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.11
[openssl-ca]: https://docs.openssl.org/3.5/man1/openssl-ca/#options
[openssl-x509]: https://docs.openssl.org/3.5/man1/openssl-x509/#micro-ca-options
[openssl-extensions]: https://docs.openssl.org/3.5/man5/x509v3_config/#certificate-policies
[c2pa-spec-chain]: https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html#_certificate_trust_chain
[c2pa-spec-revocation]: https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html#_certificate_revocation

[cp-generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[cp-duties]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#separation-of-duties

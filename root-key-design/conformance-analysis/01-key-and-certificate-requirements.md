# 01. 키 자체와 인증서 요구사항

## 키 재료와 생성·보호

| ID | 적용 / 강도 | 요구사항 | 근거 / 설계 시 증거 |
|---|---|---|---|
| K01 | Root·모든 ICA / 필수 | CA 공개키는 RSA 3072bit 이상 또는 ECC P-384/P-521. SPKI는 `rsaEncryption` 또는 `id-ecPublicKey`. | [네 CA 프로파일][profiles]. HSM 키 속성과 발급 DER의 SPKI를 함께 확인 |
| K02 | Root·모든 ICA 인증서 / 필수 | 인증서 서명은 RSA SHA-2 계열(PKCS#1 v1.5 또는 PSS)이나 ECDSA SHA-2 계열. Spec §14.5.1.1의 SHA-256/384/512 및 PSS hashAlgorithm·MGF hash 일치 조건도 확인한다. | [CP 프로파일][profiles], [Spec §14.5.1.1][spec] |
| K03 | 모든 CA 키 생성 / 필수 | 공개한 업무 관행과 상세 세레모니 script에 따라 안전한 물리/클라우드 환경에서 trusted roles의 다인 통제·split knowledge로 생성. FIPS 140-2 Level 2+, FIPS 140-3 Level 2+, 또는 적절한 CC PP/ST EAL4+ 모듈. 독립 입회 및/또는 기록, 활동 logging. | [CP Key Pair Generation and Installation by CAs][generation], 제3장 「키 생성 세레모니 스크립트 요구사항」 |
| K04 | Root·Issuing CA 저장 및 사용 / 필수 | Key Storage 원문은 FIPS 140-2 Level 2+ 장치와 `3-tier data center` 또는 상용 클라우드 HSM 배치를 기재. CA 개인키는 모듈 경계 밖에 평문으로 존재할 수 없다. | [CP Controls for CA Keys][storage]. 생성 조항의 FIPS 140-3/CC 대안을 저장 조항에도 자동 적용하지 않음(Q01) |
| K05 | Root·Intermediate 서명키 / 필수 | 개인 한 명이 물리적 또는 논리적으로 단독 접근하지 못하도록 multi-party controls. 개인키 사용은 암호 모듈에서 직접 수행. | [CP Key Usage and Access Control][storage]. 관리자·복구·backup을 포함하는 통제 증거 |
| K06 | 모든 CA private key / 필수·금지 | 백업은 원본과 동일 다인 통제 및 평문 반출 금지, 최소 한 사본 off-site. CA 개인키 archival은 금지. | [CP Key Backup and Recovery / Key Archival][storage]. 백업과 장기 archive 구분 |

Spec §13.2의 Claim 서명 지원 목록(예: Ed25519, P-256, RSA 2048bit)을 CA 키의 허용 목록으로 가져오지 않는다. CP의 네 CA 프로파일은 더 좁다. **Ed25519·P-256·RSA 2048bit CA, PQC 또는 hybrid CA는 이 기준의 적합한 선택으로 제시하지 않는다.** SHA-1은 아래 SKI 식별자 계산 용도이며 인증서 서명 해시 허용이라는 뜻이 아니다.

## 인증서 역할별 비교

아래는 CP의 [Root][root], [First Intermediate][first], [Claim Issuing][claim], [TSA Issuing][tsa] YAML과 CP 내장 프로파일을 대조한 결과다. `필수/금지/선택`과 criticality를 구분했다.

| 항목 | Root | First Intermediate CA | Claim Signing Issuing CA | TSA Issuing CA |
|---|---|---|---|---|
| 식별 ID | P01 | P02 | P03 | P04 |
| Version | v3 | v3 | v3 | v3 |
| Serial | 양의 정수, 최대 20 octets. 높은 entropy는 권고 | 동일 | 동일 | 동일 |
| Subject | 고유 CA 이름, C·O·CN 포함 | 고유 CA 이름, C·O·CN 포함 | 고유 CA 이름, C·O·CN 포함 | 고유 CA 이름, C·O·CN 포함 |
| Issuer | Subject와 같고 self-signed | Root의 Subject | 실제 발급 Root 또는 subordinate의 Subject | YAML에는 signing Root의 Subject; AKI는 Root 또는 Intermediate를 허용하는 표현. Q02 확인 |
| 유효기간 | 장기, 20년은 예시 | 중기, 5년은 예시 | **최대 1827일** | **최대 5479일** |
| SKI | 필수, non-critical, RFC5280 Method 1 SHA-1 | 동일 | 동일 | 동일 |
| AKI | 선택, 넣으면 non-critical이며 자기 SKI와 일치하는 keyIdentifier. schema는 필수 검사(Q11) | 필수, non-critical. 원문은 어느 SKI인지 모호; 실제 발급자 SKI 대조(Q03) | 필수, non-critical, 발급 CA의 SKI와 keyIdentifier 일치 | 필수, non-critical, 발급 CA의 SKI와 keyIdentifier 일치 |
| KU | 필수·critical, `keyCertSign`, `cRLSign` | 동일 | 동일 | 동일 |
| Basic Constraints | 필수·critical, cA=TRUE, pathLenConstraint ≤2 | 필수·critical, cA=TRUE, pathLen=1 | 필수·critical, cA=TRUE, pathLen=0 | 필수·critical, cA=TRUE, pathLen=0 |
| EKU | 이 프로파일에서 별도 요구 없음 | 이 프로파일에서 별도 요구 없음 | 필수·non-critical, `c2pa-kp-claimSigning` + (`emailProtection` 또는 `documentSigning` 중 최소 하나). schema OID 차이는 Q12 | 필수·non-critical, 정확히 `id-kp-timeStamping` |
| Certificate Policies | 선택·non-critical | 필수·non-critical, C2PA CP OID 포함 | 동일 | 동일 |
| AIA | **금지** | CDP 없으면 필수, non-critical | 동일 | 동일 |
| CDP | **금지** | OCSP AIA 없으면 필수, non-critical | 동일 | 동일 |

ICA의 AIA를 넣으면 `id-ad-ocsp`가 필수이고 `id-ad-caIssuers`는 SHOULD, accessLocation은 HTTP URI다. CDP는 CRL을 가리키는 HTTP URI를 포함한다. **AIA의 caIssuers만으로 OCSP/CDP 조건을 충족하지 않는다.** 둘 다 포함하는 것은 가능하다. JSON schema의 caIssuers 강제 여부 차이는 Q04에 기록했다.

ICA Certificate Policies에는 `c2pa-certificate-policy = 1.3.6.1.4.1.62558.1.1`가 필수이고 CA 소유 IANA private arc의 CPS용 OID를 추가할 수 있다. Qualifier는 선택이다. `c2pa-kp-claimSigning = 1.3.6.1.4.1.62558.2.1`, `emailProtection = 1.3.6.1.5.5.7.3.4`, `documentSigning = 1.3.6.1.5.5.7.3.36`, `timeStamping = 1.3.6.1.5.5.7.3.8`이다. AL 확장은 Claim Signing **leaf**의 속성이며 CA 프로파일의 필수 필드가 아니다.

**검사 schema 차이**: [Root certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json#L1013-L1045)는 CP/YAML에서 선택인 AKI를 필수 검사한다(Q11). [Claim Issuing certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json#L1129-L1155)와 [CSR schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json#L980-L1006)의 documentSigning 분기는 `1.2.840.113583.1.1.5`를 사용하여 위 Spec의 표준 OID와 다르다(Q12). `c2pa-kp-claimSigning`과 표준 documentSigning만 사용하면 이 schema의 EKU 조건을 만족하지 못한다. 표준 OID를 다른 OID로 바꾸거나 동일 의미로 단정하지 않고 CP/Spec 적합성과 제공 checker 결과를 분리하여 보고한다.

P05 — [Spec §14.5.1.1][spec]의 공통 요구도 검사한다: `issuerUniqueID`·`subjectUniqueID` 금지, `anyExtendedKeyUsage` 금지, CA의 cA·keyCertSign 관계, 비 self-signed 인증서 AKI, CA의 SKI. Spec §14.5.1.2는 validator가 CA EKU를 무시하도록 하지만 **CP Issuing CA EKU 발급 요건을 없애지 않는다**.

## 키로 할 수 있는 일

| ID | 대상 | 허용 범위 / 금지 경계 | 근거 |
|---|---|---|---|
| U01 | Root 키 | 자기 Root 인증서, subordinate·cross-certified CA 인증서, OCSP Responder 인증서, CRL에만 서명 | [CP Key Pair and Certificate Usage 1][use] |
| U02 | pathLen=1 Intermediate 키 | 인증서 서명은 subordinate CA, 인프라 목적 인증서, OCSP Response 검증용 인증서에 한정 | [CP Usage 2][use]. 이 항목은 인증서 서명의 범위이며 CRL 서명 금지를 뜻하지 않음 |
| U03 | Claim·TSA leaf 발급 | 반드시 pathLen=0 subordinate CA에서 발급 | [CP Usage 3][use] |
| U04 | Claim·timestamp·OCSP 응답 서명 | end-entity 키로만 수행. CA 키로 직접 서명하지 않음 | [Spec §14.5.1.1][spec]. Root가 OCSP **인증서**를 발급하는 것과 응답을 직접 서명하는 것은 다름 |
| U05 | OCSP responder | 자신을 발급한 CA가 발급한 인증서의 OCSP 응답에만 사용. 별도 leaf에 cA=FALSE, critical KU=digitalSignature, EKU=OCSPSigning 하나, NoCheck=NULL, AIA/CDP 금지 | [CP Usage 8][use], [OCSP profile][ocsp] |
| U06 | CA가 생성하는 키의 범위 | CA는 Subscriber의 Claim Signing 키 쌍을 생성할 수 없음 | [CP Key Pair Generation and Installation by Subscribers][cp] |

허용 계층 예는 Root → First(pathLen=1) → Claim Issuing(pathLen=0) → Claim leaf, 또는 Root → Claim Issuing(pathLen=0) → Claim leaf다. Root의 pathLen은 계획한 실제 CA 깊이를 수용해야 한다. TSA를 First 아래에 둘 때는 P04의 원문 차이를 먼저 해소한다. 이 예시는 전용 First ICA나 특정 계층 수를 반드시 두라는 요구가 아니다.

## 발급 전 확인할 산출물

설계 제안: 역할별 프로파일 템플릿, 허용 알고리즘·OID 표, DER/PEM, 디코딩 결과, key/SPKI/CSR/인증서 일치 기록, 서명·체인·AKI-SKI·기간·criticality 검사 보고서를 한 묶음으로 관리한다. JSON schema 통과만으로 이 전체가 입증되지는 않는다. 유효기간 예시를 고정 수명으로 오인하거나 CA 키와 인증서의 갱신을 같은 작업으로 처리하지 않는다.

[profiles]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/
[spec]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html
[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[storage]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L827-L857
[root]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml
[first]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml
[claim]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.yaml
[tsa]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml
[use]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L539-L571
[ocsp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.yaml
[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md

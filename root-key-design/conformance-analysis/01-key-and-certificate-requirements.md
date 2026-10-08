# 01. 키 자체와 인증서 요구사항

ID별 원문 파일·고정 줄·절은 [원문 위치 대응표](06-source-map.md)에 있다.

## 키 재료와 생성·보호

| ID | 적용 / 강도 | 요구사항 | 근거 / 설계 시 증거 |
|---|---|---|---|
| K01 | Root·모든 ICA / 필수 | CA 공개키는 RSA 3072bit 이상 또는 ECC P-384/P-521. SPKI는 `rsaEncryption` 또는 `id-ecPublicKey`. | [네 CA 프로파일][profiles]. HSM 키 속성과 발급 DER의 SPKI를 함께 확인 |
| K02 | Root·모든 ICA 인증서 / 필수 | 인증서 서명은 RSA(PKCS#1 v1.5 또는 PSS)나 ECDSA이며 해시는 **SHA-256/384/512**로 한정한다. PSS는 `hashAlgorithm`·`maskGenAlgorithm` 필드를 모두 포함하고, 선택한 hashAlgorithm과 MGF의 hash 알고리즘을 일치시킨다. | [CP 프로파일][profiles], [Spec §14.5.1.1 Certificate signatureAlgorithm / PSS parameters][spec-alg] |
| K03 | 모든 CA 키 생성 / 필수 | 공개한 업무 관행과 상세 세레모니 script에 따라 안전한 물리/클라우드 환경에서 trusted roles의 다인 통제·split knowledge로 생성. FIPS 140-2 Level 2+, FIPS 140-3 Level 2+, 또는 적절한 CC PP/ST EAL4+ 모듈. 독립 입회 및/또는 기록, 활동 logging. | [CP Key Pair Generation and Installation by CAs][generation], 제3장 「키 생성 세레모니 스크립트 요구사항」 |
| K04 | Root·Issuing CA 저장 및 사용 / 필수 | Key Storage 원문은 FIPS 140-2 Level 2+ 장치와 `3-tier data center` 또는 상용 클라우드 HSM 배치를 기재. CA 개인키는 모듈 경계 밖에 평문으로 존재할 수 없다. | [CP Controls for CA Keys][storage]. 생성 조항의 FIPS 140-3/CC 대안을 저장 조항에도 자동 적용하지 않음(Q01) |
| K05 | Root·Intermediate 서명키 / 필수 | 개인 한 명이 물리적 또는 논리적으로 단독 접근하지 못하도록 multi-party controls. 개인키 사용은 암호 모듈에서 직접 수행. | [CP Key Usage and Access Control][storage]. 관리자·복구·backup을 포함하는 통제 증거 |
| K06 | 모든 CA private key / 필수·금지 | 백업은 원본과 동일 다인 통제 및 평문 반출 금지, 최소 한 사본 off-site. CA 개인키 archival은 금지. | [CP Key Backup and Recovery / Key Archival][storage]. 백업과 장기 archive 구분 |

Spec §13.2의 Claim 서명 지원 목록(예: Ed25519, P-256, RSA 2048bit)을 CA 키의 허용 목록으로 가져오지 않는다. CP의 네 CA 프로파일은 더 좁다. **Ed25519·P-256·RSA 2048bit CA, PQC 또는 hybrid CA는 이 기준의 적합한 선택으로 제시하지 않는다.** SHA-1은 아래 SKI 식별자 계산 용도이며 인증서 서명 해시 허용이라는 뜻이 아니다.

## 인증서 역할별 비교

아래는 CP의 [Root][root], [First Intermediate][first], [Claim Issuing][claim], [TSA Issuing][tsa] YAML과 [CP 내장 CA 프로파일][ca-profiles]을 대조한 결과다. 내장·별도 YAML의 내용은 일치한다. `필수/금지/선택`과 criticality를 구분했다. Version·Serial·Subject·알고리즘·유효기간은 YAML의 프로파일 값이며, 각 줄이 별도의 SHALL 문장인 것은 아니다. SHOULD 또는 예시로 표시된 값은 의무로 올리지 않는다.

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

ICA의 AIA를 넣으면 `id-ad-ocsp`가 필수이고 `id-ad-caIssuers`는 SHOULD, accessLocation은 HTTP URI다. CDP는 CRL을 가리키는 HTTP URI를 포함한다. **AIA의 caIssuers만으로 OCSP/CDP 조건을 충족하지 않는다.** CP/YAML은 OCSP AIA와 CDP를 함께 넣는 것을 금지하지 않으며, 둘 다 넣더라도 AIA 안의 OCSP 요구는 유지된다. 아래 schema 차이를 이유로 CP의 허용을 금지로 바꾸지 않는다(Q04).

- 세 ICA와 Claim AL1·AL2 및 TSA leaf의 **certificate schema 6개**는 AIA가 있을 때 caIssuers를 `contains`로 강제한다.
- 세 ICA와 TSA leaf는 CDP와 caIssuers-only AIA를 함께 넣으면 해당 제약이 OCSP 누락을 검출하지 못한다. Claim leaf는 별도 OCSP 필수 제약이 있어 이 경우 실패한다.
- **First ICA**는 OCSP AIA/CDP 선택에 `oneOf`를 써서 두 조건을 모두 만족하는 OCSP+caIssuers AIA와 CDP의 조합을 거부한다. 다른 다섯 certificate schema의 관련 제약은 이 조합을 수락한다.

이 결과는 해당 JSON 제약의 동작이며 공식 checker 전체의 수용 방침과는 구분한다.

| Q04 영향 역할 | Certificate schema의 AIA 관련 제약 |
|---|---|
| First ICA / Claim Issuing / TSA Issuing | [First][first-aia-schema] / [Claim Issuing][claim-aia-schema] / [TSA Issuing][tsa-aia-schema] |
| Claim leaf AL1 / AL2 | [AL1 L1407–1455][al1-aia-schema] / [AL2 L1407–1455][al2-aia-schema] |
| TSA leaf | [L1386–1434][tsa-leaf-aia-schema] |

이 6개 역할의 CSR schema는 AIA의 non-critical·HTTP URI 형태를 검사하지만 caIssuers/OCSP accessMethod를 같은 방식으로 강제하지 않는다. certificate와 CSR 결과를 서로의 검증으로 대체하지 않는다. 각 CSR 원문도 [Q04 대응 위치](06-source-map.md#q04)에 연결했다.

ICA Certificate Policies에는 `c2pa-certificate-policy = 1.3.6.1.4.1.62558.1.1`가 필수이고 CA 소유 IANA private arc의 CPS용 OID를 추가할 수 있다. Qualifier는 선택이다. `c2pa-kp-claimSigning = 1.3.6.1.4.1.62558.2.1`, `emailProtection = 1.3.6.1.5.5.7.3.4`, `documentSigning = 1.3.6.1.5.5.7.3.36`, `timeStamping = 1.3.6.1.5.5.7.3.8`이다. AL 확장은 Claim Signing **leaf**의 속성이며 CA 프로파일의 필수 필드가 아니다.

**검사 schema 차이**: [Root certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json#L1013-L1045)는 CP/YAML에서 선택인 AKI를 필수 검사한다(Q11). Claim Issuing 및 Claim AL1·AL2의 certificate/CSR 총 6개 schema는 documentSigning 분기에 `1.2.840.113583.1.1.5`를 사용하여 [Spec §14.4.1의 표준 OID][spec-eku]와 다르다(Q12). `c2pa-kp-claimSigning`과 표준 documentSigning만 사용하면 이 schema들의 EKU 조건을 만족하지 못한다. 표준 OID를 다른 OID로 바꾸거나 동일 의미로 단정하지 않고 CP/Spec 적합성과 제공 checker 결과를 분리하여 보고한다.

| Q12 영향 역할 | Certificate schema의 EKU 제약 | CSR schema의 EKU 제약 |
|---|---|---|
| Claim Issuing CA | [L1129–1155][claim-eku-cert] | [L980–1006][claim-eku-csr] |
| Claim leaf AL1 | [L1156–1182][al1-eku-cert] | [L1002–1028][al1-eku-csr] |
| Claim leaf AL2 | [L1156–1182][al2-eku-cert] | [L1002–1028][al2-eku-csr] |

P05 — [Spec §14.5.1.1 General Requirements][spec-common]에 따라 `issuerUniqueID`·`subjectUniqueID` 금지, CA의 cA·keyCertSign 관계, 비 self-signed 인증서 AKI, CA의 SKI를 확인한다. leaf는 비어 있지 않은 EKU가 필수이며 `anyExtendedKeyUsage`를 넣지 않는다. **Claim 서명·timestamp 서명·OCSP 응답 서명의 세 목적 중 최대 하나에만 유효해야 한다**. Claim의 필수 EKU에 timeStamping 또는 OCSPSigning을 추가해 용도를 겸용하지 않는다. [Spec §14.5.1.2 Certificate Trust Chain][spec-chain]은 validator가 CA EKU를 무시하도록 하지만 **CP Issuing CA EKU 발급 요건을 없애지 않는다**. private credential store의 예외는 직접 신뢰하는 signer credential에 대한 것으로, 해당 저장소의 인증서를 CA나 trust anchor로 사용할 수 없다.

## CA가 발급하는 leaf의 정책 인계

아래는 [CP leaf 프로파일][leaf-profiles] 중 발급 CA가 확정해야 할 정책이다. leaf의 공개키와 그 인증서에 서명한 CA의 키를 구분한다. Claim leaf의 공개키로 Ed25519가 허용된다고 CA 키까지 허용되는 것은 아니다. 원문 leaf 프로파일의 인증서 서명 알고리즘 목록과 실제 발급 CA가 사용할 수 있는 알고리즘을 함께 적용한다. 제품의 COSE claim 서명 또는 TSA token 서명에 쓰는 알고리즘은 [Spec §13.2][spec-signatures]에 따라 별도로 판단한다.

| 항목 | P06 — Claim AL1 | P07 — Claim AL2 | P08 — TSA time-stamp leaf | P09 — OCSP responder leaf |
|---|---|---|---|---|
| 별도 원문 | [AL1 YAML][al1] | [AL2 YAML][al2] | [TSA leaf YAML][tsa-leaf] | [OCSP YAML][ocsp] |
| Version·Serial | v3; 양의 정수, 최대 20 octets, 높은 entropy는 권고 | 동일 | 동일 | 동일 |
| 유효기간 | 최대 **366일** | 최대 **90일** | 최대 **4110일** | C2PA profile에 최대 기간 미지정; 생성 시 구체 날짜 설정 |
| Issuer | 발급 Claim Signing Issuing CA의 Subject | 동일 | 발급 TSA Issuing CA의 Subject | 발급 CA의 Subject |
| Subject | CPL entry와 일치하며 C·O·CN 포함 | 동일 | 고유 TSA service 이름, C·O·CN 포함 | 고유 responder 이름, C·O·CN 포함 |
| 공개키·SPKI | RSA 2048bit+(`rsaEncryption`) / P-256·P-384·P-521(`id-ecPublicKey`) / Ed25519(`id-Ed25519`) | 동일 | RSA 2048bit+(`rsaEncryption`) / P-256·P-384·P-521(`id-ecPublicKey`) | 동일 |
| 인증서 서명 알고리즘 | RSA SHA-2(PKCS#1 v1.5/PSS), ECDSA SHA-2, Ed25519가 profile에 기재됨; 발급 CA에는 K01–K02 적용 | 동일 | RSA SHA-2 또는 ECDSA SHA-2; EdDSA 제외 | 동일 |
| SKI / AKI | 모두 필수·non-critical; SKI는 RFC5280 Method 1, AKI keyIdentifier는 발급 CA SKI와 일치; issuer/serial 선택 | 동일 | 동일 | 동일 |
| Basic Constraints | 필수·critical, cA=FALSE | 동일 | 동일 | 동일 |
| KU | 필수·critical, digitalSignature + nonRepudiation(contentCommitment) | 동일 | 동일 | 필수·critical, digitalSignature |
| EKU | 필수·non-critical, c2pa-kp-claimSigning + (emailProtection 또는 documentSigning 중 최소 하나) | 동일 | 필수·**critical**, 정확히 timeStamping 하나 | 필수·non-critical, 정확히 OCSPSigning 하나 |
| Certificate Policies | 필수·non-critical, C2PA CP OID 포함; CA private arc의 CPS OID 및 qualifier 선택 | 동일 | 동일 | 이 프로파일에서 별도 요구 없음 |
| AIA | 필수·non-critical, OCSP 필수·caIssuers SHOULD, HTTP URI | 동일 | CDP가 없으면 필수·non-critical; 넣으면 OCSP 필수·caIssuers SHOULD, HTTP URI | 금지 |
| CDP | 선택·non-critical; 넣으면 CRL HTTP URI 필수 | 동일 | OCSP AIA가 없으면 필수·non-critical, CRL HTTP URI | 금지 |
| AL 확장 | 필수·non-critical, OID `1.3.6.1.4.1.62558.3`, 값 `1.3.6.1.4.1.62558.3.10` | 필수·non-critical, 같은 확장 OID, 값 `1.3.6.1.4.1.62558.3.20` | 이 프로파일에서 별도 요구 없음 | 이 프로파일에서 별도 요구 없음 |
| CPL Record ID 확장 | 필수·non-critical, OID `1.3.6.1.4.1.62558.4`, CPL UUID를 담는 길이 36의 UTF8String | 동일 | 이 프로파일에서 별도 요구 없음 | 이 프로파일에서 별도 요구 없음 |
| OCSP NoCheck | 이 프로파일에서 별도 요구 없음 | 동일 | 동일 | 필수·non-critical, NULL |

Claim leaf의 사용자는 해당 GP instance로 한정되고 키 통제·공유/반출 예외는 GP Security Requirements에 따른다. timestamp leaf는 명명된 TSA/TSU의 timestamp 서비스 전용이고, OCSP leaf는 자신을 발급한 CA가 발급한 인증서의 응답에만 사용한다. [CP Usage 5–9][leaf-use]의 용도 제한을 profile에 없는 다른 용도의 허용으로 확대하지 않는다. Claim 인증서의 발급 자격·AL 증거는 제4장 E09–E12와 함께 적용한다.

## 키로 할 수 있는 일

| ID | 대상 | 허용 범위 / 금지 경계 | 근거 |
|---|---|---|---|
| U01 | Root 키 | 자기 Root 인증서, subordinate·cross-certified CA 인증서, OCSP Responder 인증서, CRL에만 서명 | [CP Key Pair and Certificate Usage 1][use] |
| U02 | pathLen=1 Intermediate 키 | 인증서 서명은 subordinate CA, 인프라 목적 인증서, OCSP Response 검증용 인증서에 한정 | [CP Usage 2][use]. 이 항목은 인증서 서명의 범위이며 CRL 서명 금지를 뜻하지 않음 |
| U03 | Claim·TSA leaf 발급 | 반드시 pathLen=0 subordinate CA에서 발급 | [CP Usage 3][use] |
| U04 | Claim·timestamp·OCSP 응답 서명 | end-entity 키로만 수행. CA 키로 직접 서명하지 않음 | [Spec §14.5.1.1][spec-common]. Root가 OCSP **인증서**를 발급하는 것과 응답을 직접 서명하는 것은 다름 |
| U05 | OCSP responder | 자신을 발급한 CA가 발급한 인증서의 OCSP 응답에만 사용. 별도 leaf에 P09의 필수 필드·criticality 적용 | [CP Usage 8][use], [OCSP profile][ocsp] |
| U06 | CA가 생성하는 키의 범위 | CA는 Subscriber의 Claim Signing 키 쌍을 생성할 수 없음 | [CP Key Pair Generation and Installation by Subscribers][subscriber-generation] |

허용 계층 예는 Root → First(pathLen=1) → Claim Issuing(pathLen=0) → Claim leaf, 또는 Root → Claim Issuing(pathLen=0) → Claim leaf다. Root의 pathLen은 계획한 실제 CA 깊이를 수용해야 한다. TSA를 First 아래에 둘 때는 P04의 원문 차이를 먼저 해소한다. 이 예시는 전용 First ICA나 특정 계층 수를 반드시 두라는 요구가 아니다.

## 발급 전 확인할 산출물

설계 제안: 역할별 프로파일 템플릿, 허용 알고리즘·OID 표, DER/PEM, 디코딩 결과, key/SPKI/CSR/인증서 일치 기록, 서명·체인·AKI-SKI·기간·criticality 검사 보고서를 한 묶음으로 관리한다. JSON schema 통과만으로 이 전체가 입증되지는 않는다. 유효기간 예시를 고정 수명으로 오인하거나 CA 키와 인증서의 갱신을 같은 작업으로 처리하지 않는다.

[profiles]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/
[spec-signatures]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html#L4071-L4137
[spec-alg]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html#L4595-L4692
[spec-common]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html#L4697-L4746
[spec-chain]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html#L4755-L4772
[spec-eku]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html#L4450-L4495
[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[storage]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L827-L857
[root]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml#L1-L40
[first]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml#L1-L45
[claim]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.yaml#L1-L49
[tsa]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml#L1-L49
[use]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L539-L571
[ocsp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.yaml#L1-L45
[ca-profiles]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L949-L1150
[leaf-profiles]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1152-L1386
[al1]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.yaml#L1-L60
[al2]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.yaml#L1-L60
[tsa-leaf]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.yaml#L1-L49
[leaf-use]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L563-L571
[subscriber-generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L815-L823
[first-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCA.cert.schema.json#L1218-L1440
[claim-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json#L1231-L1453
[tsa-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaIssuingCA.cert.schema.json#L1210-L1432
[claim-eku-cert]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json#L1129-L1155
[claim-eku-csr]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json#L980-L1006
[al1-eku-cert]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.schema.json#L1156-L1182
[al1-eku-csr]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al1.csr.schema.json#L1002-L1028
[al2-eku-cert]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.schema.json#L1156-L1182
[al2-eku-csr]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al2.csr.schema.json#L1002-L1028

[al1-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.schema.json#L1407-L1455

[al2-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.schema.json#L1407-L1455

[tsa-leaf-aia-schema]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json#L1386-L1434

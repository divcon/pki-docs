# Appendix — Source References

> 상태: Source registry baseline. 원문과 조사 자료의 버전·권위·적용 위치를 관리하는 인덱스다.

로컬 공식 자료의 checkout 정보와 새 환경의 확보 방법은 [원문 자료 목록](../../references/sources.md)을 확인한다.

## 1. 문서 목적

이 부록은 아키텍처의 각 요구와 설계 판단을 검증할 때 확인해야 하는 `c2pa-design/` 외부 자료를 분류하고 연결한다. 어떤 자료가 규범 원문이고 어떤 자료가 프로젝트 조사·초안인지 구분하는 데 사용한다.

## 2. 사용 규칙

- `c2pa-design/` 하위의 모든 문서는 프로젝트 산출물이며 독립적인 레퍼런스가 아니다.
- 자료 조사, 요구사항 분석, 사실 확인과 인용에서는 `c2pa-design/` 전체를 제외한다.
- 이 부록의 설명을 근거로 인용하지 않고, 연결된 `c2pa-design/` 외부 원문을 직접 열어 확인한다.
- 외부 표준의 규범 문구와 프로젝트 해석을 분리해서 기록한다.
- 버전이 달라질 수 있는 자료는 version, commit 또는 발행일을 고정한다.
- 프로젝트 작성 문서나 review draft는 공식 C2PA/RFC 요구와 동등한 권위를 갖지 않는다.
- 검색할 때는 가능한 경우 `rg ... -g '!c2pa-design/**'`처럼 산출물 디렉터리를 명시적으로 제외한다.

## 3. 각 자료에 기록할 메타데이터

| 필드 | 내용 |
|---|---|
| Source ID | 추적표에서 사용하는 안정적인 식별자 |
| 제목 | 원문 제목 |
| 분류 | C2PA Spec, C2PA Policy, RFC, Profile, Research 또는 Draft |
| 권위 | normative, informative, project research 또는 proposal |
| 버전 | version, revision, commit 또는 발행일 |
| 위치 | `c2pa-design/` 외부의 로컬 경로 또는 공식 URI |
| 적용 범위 | 어떤 컴포넌트와 요구에 사용하는지 |
| 확인 위치 | section, requirement ID, OID 또는 schema path |
| 검증일 | 마지막으로 원문과 버전을 확인한 날짜 |
| 비고 | 충돌, 해석, 대체 문서 또는 미확정 상태 |

## 4. 수록할 자료 분류

### 4.1 C2PA 규격과 Conformance 원문

다음 자료와 실제 적용 버전을 기록한다.

- Content Credentials Specification
- C2PA Conformance Program
- C2PA Certificate Policy
- Generator Product Security Requirements
- Trust List 및 TSA Trust List 관련 절차
- Conformance test asset/rubric 또는 공식 tooling

현재 로컬 후보:

- [Content Credentials Specification 2.4](../../specifications/build/site/specifications/2.4/specs/ContentCredentials.html)
- [C2PA Conformance Program v0.2](../../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md)
- [C2PA Certificate Policy v0.2](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
- [C2PA Generator Product Security Requirements](../../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md)

| Source ID | Authority | Version | 적용 위치 | 확인일(KST) |
|---|---|---|---|---|
| `CC-2.4` | normative C2PA specification | 2.4 | 외부 Claim/TimeStamp acceptance | 2026-08-28 |
| `CONF-0.2` | normative C2PA program | 0.2 | CPL/Applicant/Trust List 절차 | 2026-08-28 |
| `CP-0.2` | normative C2PA policy | 0.2 | CA/TSA issuance, lifecycle, profiles | 2026-08-28 |
| `GPSR-0.2` | normative C2PA security requirements | 0.2 | 외부 Generator AL1/AL2 eligibility | 2026-08-28 |
| `RFC-2986` | PKCS#10 syntax | RFC 2986 | CSR structure and PoP | 2026-08-28 |
| `RFC-5280` | PKIX certificate/CRL profile | RFC 5280 | certificate/path/CRL validation | 2026-08-28 |
| `RFC-6960` | OCSP | RFC 6960 | OCSP request/response validation | 2026-08-28 |
| `RFC-9052` | COSE | RFC 9052 | signed activation/provider envelope | 2026-08-28 |
| `RFC-8949` | CBOR | RFC 8949 | deterministic CBOR encoding | 2026-08-28 |

### 4.2 Machine-Readable CSR·인증서 프로파일

각 profile의 schema/version과 적용 certificate class를 기록한다.

- [C2PA Claim Signing Leaf AL1 CSR Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.csr.schema.json)
- [C2PA Claim Signing Leaf AL1 Certificate Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al1.cert.schema.json)
- [C2PA Claim Signing Leaf AL2 CSR Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.csr.schema.json)
- [C2PA Claim Signing Leaf AL2 Certificate Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.schema.json)
- [C2PA TSA Leaf CSR Schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.csr.schema.json)
- [C2PA TSA Leaf Certificate Schema](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.json)
- [C2PA Claim Signing Issuing CA CSR Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json)
- [C2PA Claim Signing Issuing CA Certificate Schema](../../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json)
- [C2PA TSA Issuing CA CSR Schema](../../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.csr.schema.json)
- [C2PA TSA Issuing CA Certificate Schema](../../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.cert.schema.json)

동일 디렉터리의 `*.yaml`은 사람이 읽는 summary이며 validator의 machine-readable 기준으로 사용하지 않는다. production build는 위 JSON schema의 version과 digest를 고정한다.

추가로 Root, Claim Signing Issuing CA, OCSP responder 또는 다른 관련 profile이 있다면 함께 등록한다.

### 4.3 RFC와 PKI 원문

다음 규격의 정확한 section과 적용 내용을 기록한다.

- [RFC 3161 — Time-Stamp Protocol](../../rfc3161.txt)
- [RFC 5816 — ESSCertIDv2 Update](../../rfc5816.txt)
- [RFC 2986 — PKCS #10 Certification Request Syntax v1.7](https://datatracker.ietf.org/doc/html/rfc2986)
- [RFC 5280 — X.509/PKIX Certificate and CRL Profile](https://datatracker.ietf.org/doc/html/rfc5280)
- [RFC 6960 — OCSP](https://datatracker.ietf.org/doc/html/rfc6960)
- [RFC 9052 — COSE Structures and Process](https://datatracker.ietf.org/doc/html/rfc9052)
- [RFC 8949 — CBOR and Deterministic Encoding](https://datatracker.ietf.org/doc/html/rfc8949)
- CMS SignedData와 ESS signed attributes는 RFC 3161/RFC 5816 및 그 normative reference version을 release source manifest에 고정한다.
- OCSP와 CRL 관련 RFC
- 사용하기로 결정한 시간 동기화/시간 증거 프로토콜

### 4.4 Attestation 조사와 프로젝트 설계 자료

다음 문서는 로컬 조사·설계 입력이며 공식 C2PA 원문과 구분한다.

- [C2PA AL2 Attestation Guide](c2pa-al2-attestation-guide.md)
- [C2PA AL2 Evidence Enrollment Specification](c2pa-attestation-evidence-enrollment-spec.md)
- [C2PA SAK Attestation Evidence Design](c2pa-sak-attestation-evidence-design.md)
- [On-Device TSA Custom Attestation Review Draft](on-device-tsa-attestation-review-draft.md)

각 문서에 대해 다음을 추가로 표시한다.

- 공식 요구의 해설인지 프로젝트 제안인지
- 적용 가능한 플랫폼/provider
- 아직 합의되지 않은 claim, OID 또는 wire format
- Architecture Decision으로 승격된 내용
- 더 최신 자료로 대체되었는지 여부

### 4.5 Provider와 플랫폼 원문

실제 Attestation provider가 결정되면 다음 자료를 추가한다.

- TEE/Key Attestation 공식 API 문서
- evidence certificate/profile과 Root program
- claim semantics와 security level 정의
- device lifecycle/debug/boot/rollback claim 정의
- key origin, purpose와 non-exportability 증명 방법
- status/revocation endpoint
- Root/intermediate rotation 공지
- privacy/data processing 조건

공식 provider 문서와 내부 mapping profile을 분리한다.

### 4.6 운영·감사·보안 기준

production CA/TSA 운영에 실제 적용하기로 한 기준만 기록한다.

- CA key/HSM 운영 기준
- key ceremony 및 multi-party control
- CPS/CP/TSA Practices 작성 기준
- 감사와 logging 기준
- incident response와 vulnerability management
- privacy, retention과 data protection
- secure development, code signing과 supply-chain 기준

적용하지 않는 일반 참고 기준을 무분별하게 나열하지 않는다.

## 5. 문서별 Source Mapping

| 아키텍처 문서 | 주로 연결할 원문 |
|---|---|
| [Architecture Foundation](../01-Architecture-Foundation.md) | C2PA Specification, Conformance Program, Certificate Policy |
| [Certificate Enrollment](../02-Certificate-Enrollment.md) | Certificate Policy, certificate profiles, PKCS#10/X.509, provider Attestation 원문 |
| [On-Device Runtime](../03-On-Device-Runtime.md) | C2PA signature/time-stamp 절, RFC 3161, RFC 5816, trusted-time 원문 |
| [Security and Operations](../04-Security-and-Operations.md) | Certificate Policy, CPS/TSA Practices, OCSP/CRL, HSM·감사·privacy 기준 |
| [Conformance and Roadmap](../05-Conformance-and-Roadmap.md) | Conformance Program, security requirements, test assets/profiles, Trust List 절차 |

## 6. 완료 기준

- 모든 규범 요구가 `c2pa-design/` 외부의 정확한 원문 section으로 추적된다.
- 공식 표준, machine-readable profile, provider 원문과 프로젝트 draft가 명확히 구분된다.
- 각 source의 적용 version과 마지막 검증일이 기록되어 있다.
- 폐기되거나 대체된 자료가 현재 근거처럼 사용되지 않는다.
- Source link가 실제 파일 또는 공식 원문으로 해석된다.
- 이 부록 자체를 규범 근거로 인용하지 않는다는 규칙이 유지된다.

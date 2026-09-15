# 04 — Security and Operations 상세 설계

> 상태: 상세 설계 초안. Certificate Platform의 CA/ICA, status service, provider trust, lifecycle, 보안 운영과 사고 대응을 구체화한다. Production baseline 승인을 위해 10.3절의 미결정값을 CPS·운영 절차·배포 profile에 고정해야 한다.  
> 기준: C2PA Conformance Program/Certificate Policy v0.2, `conformance-public` commit `722b639fd140871eb8b8ff0322f2f6e0538dd50a`  
> 원칙: `c2pa-design/` 문서는 설계 산출물이며 규범 원문이 아니다. 아래 요구는 11절의 C2PA 원문, 공식 profile schema, RFC와 provider 원문으로 다시 검증한다.

> **2026-09-02 TSA enrollment 정정:** On-Device TSA의 TEE/key/time/single-active 요구는 설계·구현·시험·운영으로 보증할 수 있으며, C2PA는 그 signed Evidence를 TSA Leaf API마다 요구하지 않는다. 이 문서의 TSA attestation provider/Reference Value gate는 optional CPS profile에만, staged activation/signed receipt는 해당 mechanism을 채택한 runtime에만 적용한다.

이 snapshot의 규범 문서와 schema는 mutable worktree 파일이 아니라 위 commit의 Git blob exact bytes로 식별한다. Release manifest는 각 source의 `commit`, `path`, Git blob object ID와 SHA-256을 기록한다. OS checkout의 CRLF 변환이나 별도 newline normalization 결과는 canonical artifact로 인정하지 않는다.

## 1. 문서 목적과 운영 책임

### 1.1 이 문서가 답하는 질문

이 문서는 다음 질문의 canonical owner다.

1. Root, First Intermediate, Claim Signing Issuing CA, TSA Issuing CA와 OCSP Responder를 어떤 profile과 절차로 생성·발급·검증하는가?
2. Claim과 TSA trust domain, HSM key와 operator 권한을 어떻게 분리하는가?
3. 발급된 인증서의 status를 OCSP/CRL/Repository에 어떻게 반영하고 장애·rollover·compromise를 어떻게 처리하는가?
4. Attestation provider root, status source, provider profile과 Reference Value를 누가 어떤 상태기계로 운영하는가?
5. 어떤 dependency 장애와 불확실성을 fail-closed하고 어떤 기능을 read-only로 유지하는가?
6. 어떤 audit·privacy·monitoring·DR 증거가 있어야 production을 승인할 수 있는가?
7. TSA activation server transaction, signed artifact contract와 reconciliation을 어떻게 운영하는가?

다음 내용은 다른 문서가 소유한다.

| 주제 | Canonical owner | 이 문서의 역할 |
|---|---|---|
| CSR·profile-conditional Evidence 요청별 검증과 Leaf template | [02 Certificate Enrollment](02-Certificate-Enrollment.md) | 운영 중 사용할 trust/profile 상태와 CA/HSM gate 제공 |
| 외부 Claim/Timestamp runtime과 activation device acceptance | [03 External Runtime Acceptance](03-On-Device-Runtime.md) | Claim에는 incident·status handoff만, TSA activation에는 server transaction·signed contract와 reconciliation만 정의 |
| 공통 신뢰 경계와 `AF-*` 불변조건 | [01 Architecture Foundation](01-Architecture-Foundation.md) | `AF-LIFE-*`, `AF-AUD-*`, `AF-KEY-*`를 운영 통제로 구체화 |
| RTM, test catalog와 release 판정 | [05 Conformance and Roadmap](05-Conformance-and-Roadmap.md) | 검증 가능한 control ID와 production gate 제공 |
| TSA Enrollment API의 Leaf/chain 반환 형식 | [Overview §6.3](Overview.md#63-응답) | TSA-only 반환 chain의 적격성·순서·상태를 보장; Claim response는 정의하지 않음 |

Certificate Platform은 CA certificate와 Subscriber Leaf의 발급·상태를 운영한다. 외부 Generator의 `K_claim`, TSA TA의 `K_tsu`, trusted-time runtime과 Timestamp 발급 상태는 권위 있게 소유하지 않는다. 외부 상태 telemetry를 수집하는 설계라면 freshness와 source authenticity가 검증된 observation만 기록하며, CA의 `good` status를 외부 key activation이나 runtime 정상 상태로 해석하지 않는다. Runtime 준수는 signed observation만이 아니라 설계·시험·운영 감사 evidence로도 판정할 수 있다.

### 1.2 요구 수준

| 표기 | 의미 |
|---|---|
| `C2PA-REQUIRED` | C2PA Certificate Policy 또는 Conformance Program의 대문자 `REQUIRED`/`SHALL`/`SHALL NOT`/`MUST`/`MUST NOT` |
| `C2PA-SHOULD` | C2PA 원문의 대문자 `SHOULD`/`SHOULD NOT`; 이 project에서 예외를 허용하려면 위험·보완통제·승인자를 문서화 |
| `C2PA-OBLIGATION` | 대문자 BCP 14 키워드가 아니어도 CP가 CA의 의무·보증 또는 공개 practice로 명시한 항목 |
| `RFC-REQUIRED` | RFC 5280, RFC 6960 등 적용 profile의 필수 동작 |
| `CPS-REQUIRED` | C2PA가 수치를 정하지 않아 승인된 CPS/business practices가 고정해야 하는 운영값 |
| `ARCH-DECISION` | 이 프로젝트가 선택한 구조·강화 통제 |
| `PROVIDER-BOUND` | provider별 원문·signed profile·test vector로 승인해야 하는 값 |
| `OPEN` | production 전에 결정·승인이 필요한 blocker |

Generator Product Security Requirements의 O.1~O.6는 Generator Product TOE에 적용된다. 그 문서의 hosting HIDS, GP network segmentation과 GP audit 조건을 CA 서버의 직접 C2PA 의무라고 재분류하지 않는다. CA 서버에는 C2PA Certificate Policy의 Facility, Procedural, Technical Security, Audit와 Incident 조항을 직접 적용하고, 필요한 추가 통제는 `ARCH-DECISION` 또는 `CPS-REQUIRED`로 표시한다.

### 1.3 운영상 분리해야 하는 상태

| 상태 영역 | Authoritative owner | 이 문서의 보장 | 혼동하면 안 되는 것 |
|---|---|---|---|
| CA key와 CA certificate | CA/HSM Operations | 생성, certification, activation, rollover, disable, destruction | Leaf의 상태 |
| Subscriber Leaf certificate | CA Repository/Status | issued, expired, revoked와 publication | 외부 private key의 실제 파기·활성 상태 |
| Claim issuance decision/freshness context | Policy Engine/CA Orchestrator | request-context binding, replay marker와 issuance 기록 | 외부 transaction/response state |
| TSA enrollment transaction/challenge | TSA Transaction Service | one-time decision과 issuance 원자성 | 인증서 validity |
| Claim key 사용 가능 상태 | 외부 Generator | CA는 certificate와 해당 profile의 Evidence만 기록 | OCSP `good` |
| TSA device key activation | 외부 TEE; staged activation을 쓰면 서버는 transaction만 소유 | 선택된 mechanism의 receipt와 reconciliation | X.509 certificate 상태 |
| Provider/profile/reference 상태 | Provider Trust Operations | Evidence-required profile의 신규 발급 허용 여부와 emergency epoch | 과거 발급 인증서의 자동 폐기 |

## 2. 보안 거버넌스와 권한 분리

### 2.1 Trusted role과 책임

| 역할 | 허용 책임 | 금지 책임·조합 |
|---|---|---|
| Policy/CPS Owner | CP/CPS, algorithm, validity, status와 retention 정책 승인 | 자신의 변경을 단독 배포 |
| Root CA Accountable Owner | Issuing CA의 CP 준수·certificate warranty·책임 이행을 감독 | Issuing CA의 책임을 위임했다는 이유로 면책 처리 |
| RA / Identity Authority | Applicant·대표자·권한·CPL/TSA service 자격 확인 | CA signing key 사용, Evidence cryptographic verdict |
| Evidence Verifier Operator | Claim AL2/optional TSA profile의 parser/verifier와 signed Evidence 검증 서비스 운영 | Reference Value 변경 단독 승인, certificate signing |
| Provider Trust Operator | provider root/status/profile candidate 등록·rotation 준비 | 동일 변경의 최종 단독 승인 |
| Reference Value Approver | product/TA/TCB/measurement 기준과 취약 revision 승인 | Evidence verifier 운영자와 동일인이 단독 판정·배포 |
| CA Issuance Operator | 승인된 CA/Leaf template과 HSM operation 실행 | identity/Evidence predicate 우회, revocation 단독 승인 |
| HSM Custodian / Key Shareholder | ceremony, activation share, backup inventory와 recovery | 한 명이 quorum 전체를 구성하거나 plaintext key 접근 |
| Revocation Authority | 요청 인증, trigger·scope·사유 판정과 revocation 승인 | status publication 결과를 단독 검증 |
| Status Operator | OCSP/CRL 생성·배포·freshness 운영 | revocation 요청의 진위·scope 단독 승인 |
| Incident Commander | containment, dependency 분석, 통지와 recovery 조정 | 감사 결과 또는 자신의 emergency action 단독 종결 |
| Auditor | read-only log·ceremony·configuration·control 검토 | production 변경, 발급·폐기 operation |
| Privacy/Data Steward | 데이터 분류, raw Evidence 예외, retention/deletion/legal hold 승인 | 감사 로그 원문 변경·삭제 |

`C2PA-REQUIRED`로 최소한 attestation validation, certificate issuance와 revocation을 서로 다른 개인 또는 팀에 분리한다. 나머지 역할 세분화와 금지 조합은 `ARCH-DECISION`이며, 한 사람이 여러 역할을 겸할 때도 동일 operation의 요청·승인·실행·감사를 모두 수행할 수 없도록 IAM과 workflow가 강제한다.

Root CA는 Issuing CA가 수행한 CP 준수, certificate warranty, liability와 indemnification obligation에 대해 자신이 직접 발급한 것처럼 책임진다(`C2PA-REQUIRED`). 계약이나 RA/Issuing CA delegation으로 이 accountable oversight를 제거할 수 없다.

### 2.2 중요 작업의 승인 규칙

| 작업 | 최소 통제 | 실패 시 |
|---|---|---|
| Root certificate signing | trusted role 최소 2인의 참여(`C2PA-REQUIRED`); 그중 한 명의 deliberate command(`C2PA-OBLIGATION`) | operation 미수행, incident/audit event |
| CA key generation·복구 | generation은 trusted-role multi-person/split knowledge, recovery는 승인 plan과 원 key 수준의 multi-person control | operation 미수행, incident/audit event |
| 모든 CA certificate 발급 | 문서화된 issuance process, trusted roles, multi-person control, split knowledge, profile self-check; key-generation ceremony는 별도 통제 | CA certificate 폐기 또는 inactive 유지 |
| CA equipment 물리 접근·특정 CA operation | 사전 정의된 `m-of-n` dual control, 승인된 key shareholder, access audit | 접근·operation 거부, incident/audit event |
| Claim/TSA ICA key 활성화 | 별도 HSM object/authorization, profile·chain·Trust List gate | 신규 Leaf 발급 금지 |
| OCSP responder key 활성화 | 대상 Issuing CA 직접 발급, responder profile 검증, status scope 제한 | responder traffic 전환 금지 |
| Evidence provider/profile `ENABLED` 전환 | Trust+Reference+Verifier+Privacy+Negative test의 분리 승인 | 해당 Evidence-required profile은 최대 `SHADOW` 유지 |
| Reference Value 활성화 | signed/authenticated bundle, independent review, monotonic sequence | 이전 `ACTIVE` 유지 또는 affected issuance stop |
| Emergency block | 사전 정의된 incident 권한으로 즉시 차단; 해제는 새 정상 변경 승인 | 차단 우선, cached PASS 무효화 |
| Revocation | trigger와 scope 검증, 승인, durable status commit, publication 검증 | revoked 상태를 되돌리지 않고 publication incident |
| 정책·코드·인프라 변경 | change record, 사전 시험·승인, rollback 또는 roll-forward plan | 배포 중단·복구 |

Mandatory trust predicate를 운영자 waiver, break-glass 또는 수동 DB 수정으로 `PASS`로 바꿀 수 없다. Break-glass는 발급·activation을 더 강하게 차단하거나 status를 복구하는 데만 사용하며, 사용 후 독립 review를 필수로 한다. 이 break-glass 제한은 `ARCH-DECISION`이다.

Root signing의 2인 참여와 모든 CA certificate issuance의 multi-person/split-knowledge는 대문자 `SHALL` 통제다. Deliberate command는 CP의 lowercase `must` 문구를 `C2PA-OBLIGATION`으로 보존한다. Root가 수행하는 CRL 등 비-certificate signature에 split knowledge까지 요구하려면 별도 `ARCH-DECISION`으로 CPS에 명시한다.

### 2.3 접근·환경·네트워크 통제

- CA/HSM, verifier, trust registry, status signer, audit store와 운영 control plane에 least privilege와 MFA를 적용한다.
- Password authentication path가 있는 모든 CA system에는 CPS가 수치화한 strong-password policy, MFA와 정기 access review를 적용한다(`C2PA-REQUIRED`). Password policy를 `N/A`로 판정하려면 password credential과 fallback/break-glass password path가 없음을 configuration·credential inventory·negative authentication test로 증명해야 한다. MFA와 access review는 이 `N/A`로 면제되지 않는다.
- Critical PKI infrastructure와 민감 데이터가 있는 시설은 controlled-access secure environment에 두고, server room/data center 같은 restricted area는 승인된 인원만 physical MFA로 접근한다. Server·network device·HSM은 비인가 접근·변조·절도를 막도록 물리적으로 보호한다.
- CA equipment의 물리 접근과 사전에 지정한 CA operation은 일반 IAM MFA만으로 대체하지 않고 2.2절의 `m-of-n` dual control을 통과한다.
- Root, Claim ICA, TSA ICA, OCSP responder와 operational signing authorization을 key ID와 operation allowlist로 제한한다.
- Production과 non-production은 CA key, HSM partition/object, credential, provider trust/profile activation, database, namespace, audit sink와 public status endpoint를 공유하지 않는다.
- 삼성전자 single-tenant 배포에서도 Generator Product/CPL record, TSA service, TSU instance와 environment scope authorization을 분리한다.
- CA 내부 network는 firewall/routing control, authenticated service identity, encrypted transport, diagnostic port 통제와 정기 configuration audit를 적용한다.
- verifier는 untrusted DER/CBOR/COSE를 처리하는 별도 격리 boundary이고 CA/HSM signing 권한을 갖지 않는다.
- audit reader, privacy export와 backup restore 권한을 issuance 권한과 분리한다.
- CA 조직이 사용하는 모든 network service를 inventory로 유지하고 service별 protocol/port, purpose, owner, source·destination zone, exposed audience, authenticated identity/method, encryption, data classification, firewall/routing/ACL, diagnostic access, approval과 last-review를 문서화한다(`C2PA-REQUIRED`). 불필요한 service·port·diagnostic access는 비활성화한다.

### 2.4 인력·절차·변경 관리

- Permanent staff의 background verification은 채용 지원 시 수행하고 Trusted Role 담당자는 최소 5년마다 다시 검증한다.
- PKI, data protection, incident response, attestation validation과 담당 역할 교육을 정기 수행하고 material change 뒤 재교육한다.
- CA issuance, revocation, key management, attestation validation, incident/DR와 access control 절차를 최신 상태로 유지한다.
- 모든 변경은 owner, 영향 dependency, 승인자, 시험 결과, rollback/roll-forward, 배포 시각과 artifact digest를 기록한다.
- parser, certificate schema, provider root, Reference Value, HSM policy와 status freshness 변경은 security-sensitive change로 분류한다.
- CA software와 verifier에는 secure coding, artifact/code signing, dependency·OS의 정기 security update를 적용하고 배포 artifact의 provenance와 digest를 release record에 연결한다.
- Issuance부터 revocation까지 certificate lifecycle 전체에서 certificate와 관련 데이터의 confidentiality, integrity와 availability 통제를 유지한다.
- CP가 요구하는 business practices를 public CPS 또는 C2PA와 합의한 공개 방식으로 제공하며, 실제 운영 절차와 불일치하면 production approval을 내리지 않는다.

### 2.5 Certificate warranty와 법적 관계 gate

Claim Signing Leaf 발급은 CA가 Certificate Beneficiary에게 CP와 공개 business practices를 준수했다는 warranty를 발생시킨다(`C2PA-OBLIGATION`). 각 Claim Leaf의 최종 CA/HSM signing 전에 아래 Claim predicate가 모두 `PASS`인 `WARRANTY_READY` decision을 durable하게 commit한다. TSA Leaf에는 Claim Subscriber Agreement·product-name warranty를 자동 확장하지 않고 02 §6.2의 TSA business-practices identification/authentication/verification와 TSA profile/status predicate를 적용한다. 별도 TSA operator 계약 gate를 채택하면 `CPS-REQUIRED`/`ARCH-DECISION`으로 표시한다. CA/OCSP certificate 자체에도 Subscriber Agreement predicate를 적용하지 않지만 2.1절의 Root/Issuing CA warranty·oversight와 4절의 CA profile gate는 그대로 적용한다.

| Predicate | Canonical owner | 필수 evidence |
|---|---|---|
| `CLAIM_NAME_CONTROL` | 02 Identity/Enrollment | Claim product name 사용권/control, authoritative Subject 및 profile에 따라 존재하는 SAN 비교 |
| `CLAIM_SUBJECT_AUTHORIZED` | 02 Identity/Enrollment | Claim Subject 승인, Applicant Representative의 요청·계약 구속 권한 |
| `CLAIM_CERT_INFO_ACCURATE` | 02 Enrollment/Template | 최종 Claim TBS certificate 정보와 authoritative record/template 비교 결과 |
| `CLAIM_LEGAL_RELATIONSHIP_ACTIVE` | Legal/CPS Operations | 비계열 Claim Subscriber Agreement 또는 계열 Terms of Use acknowledgement의 version, digest, 유효기간, scope와 승인 |
| `STATUS_WARRANTY_READY` | 04 Status Operations | 모든 unexpired certificate의 24×7 current-status Repository readiness |
| `REVOCATION_WARRANTY_READY` | 04 Revocation Authority | CP revocation trigger와 publication path readiness |

Claim Subscriber Agreement는 CP의 필수 stipulation을 포함하고 private-key 보호·관리의 sole responsibility를 명시한다. 동일 법인 또는 계열 관계이면 권한 있는 Applicant Representative가 Terms of Use를 발급 전에 acknowledge해야 한다. Claim certificate의 설치·사용에 따른 implicit certificate acceptance는 이 발급 전 법적 관계 gate를 대체하지 않는다. Claim final signing gate는 Subscriber/product scope, Agreement/Terms version과 current 유효상태를 다시 읽고 request evaluation context와 다르면 발급을 차단한다. Raw 계약서는 일반 enrollment/audit log에 복제하지 않고 restricted legal repository의 reference와 digest만 기록한다.

## 3. 인증서·키·activation 수명주기

### 3.1 CA key와 CA certificate 상태

내부 상태 이름은 프로젝트 설계지만 상태 의미와 전이를 다음처럼 고정한다.

```text
PLANNED
  → CEREMONY_APPROVED
  → GENERATED_INACTIVE
  → CERTIFIED
  → TRUST_PUBLISHED
  → ISSUANCE_ACTIVE
  → RETIRING
  → RETIRED
  → DESTROYED

ISSUANCE_ACTIVE / RETIRING
  → COMPROMISE_SUSPECTED
  → DISABLED
  → REVOKED_OR_TRUST_REMOVED
```

| 상태 | 허용 operation | 진입 조건 |
|---|---|---|
| `GENERATED_INACTIVE` | CSR/PoP와 backup 검증만 | ceremony sign-off, HSM key 생성·inventory 완료 |
| `CERTIFIED` | certificate self-check와 path test | CA certificate의 DER·schema·cross-object gate 통과 |
| `TRUST_PUBLISHED` | shadow validation | 필요한 Claim/TSA Trust List, AIA, OCSP/CRL 준비 확인 |
| `ISSUANCE_ACTIVE` | profile-bound signing만 | HSM policy, status, monitoring, runbook와 release 승인 |
| `RETIRING` | 신규 Leaf 금지; 기존 certificate status만 유지 | successor 활성화와 issuer switch 완료 |
| `DISABLED` | signing 금지 | compromise 의심, policy/profile/status 중대 실패 |
| `DESTROYED` | 없음 | 보존 의무와 복구 필요 종료, destruction ceremony 완료 |

CA private key의 복구용 `backup`과 장기 `archive`를 구분한다. 보호된 backup은 운영 복구용으로 존재하지만 CA private key archive는 금지한다. 종료 후 destruction 방식·시점·증거는 CP가 고정하지 않으므로 CPS에 정의한다.

### 3.2 Subscriber Leaf lifecycle

```text
ISSUING → ISSUED_VALID → EXPIRED
                       └→ REVOKED (terminal)
```

- Claim과 TSA Subscriber certificate의 same-key renewal은 금지한다.
- re-key는 새 key와 새 CSR을 사용하고 신규 신청과 동일하게 처리한다. Challenge를 사용하는 provider flow이면 새 unique challenge도 발급한다. Claim은 현재 identity/authorization, CPL eligibility와 요청 Assurance Level에 적용되는 Dynamic Evidence를 검증하고, TSA는 공개 business practices의 identification/authentication/verification 절차를 적용한다. 매 re-key마다 initial identity validation 전체를 반복하는 것은 CP 최소선이 아니라 이 project의 강화정책으로 채택할 때 CPS에 명시한다.
- certificate modification은 허용하지 않는다. Subject 변경은 initial identity validation부터 다시 수행한다.
- Claim key는 Subscriber 또는 허용된 Subscriber key-management system이 생성한다. CA는 생성·escrow·recovery하지 않는다. 발급 뒤 해당 private key는 Generator Product instance의 exclusive control 아래 있고 허용된 GSPR 예외 외에는 다른 device·application instance·party로 export 또는 share하지 않는다.
- Claim certificate와 key는 Subject로 명명되고 CPL에 등재된 Generator Product가 표시된 Assurance Level의 C2PA Claim을 서명하는 용도로만 사용한다. TSA와 OCSP key도 각 timestamp/OCSP 전용 목적만 허용하며 다른 사용은 misuse revocation trigger다.
- Subscriber Agreement에는 private key 보호·관리의 sole responsibility가 Subscriber에게 있음을 명시한다. Subscription 종료 또는 관련 활동 중단 시 Subscriber는 industry best practice에 따라 private key를 파기하고 offboarding evidence를 남긴다.
- Claim Subscriber identity는 마지막 authentication 또는 re-authentication 후 398일을 넘기기 전에 initial identity validation 절차로 재인증한다. 기한 초과 시 신규 enrollment/re-key를 차단하되 기존 certificate status를 임의 변경하지 않는다.
- Claim certificate acceptance는 Subscriber Agreement 조건의 수락이며 Generator Product의 성공적 설치·사용으로 implicit하게 성립한다. 이는 2.5절의 발급 전 legal gate를 대체하지 않는다. 이 규칙을 TSA acceptance에 자동 확장하지 않고 TSA business practices에 별도로 정의한다. Acceptance는 별도 CA certificate state나 TSA activation authorization이 아니며 필요하면 `CERTIFICATE_ACCEPTED` audit event만 남긴다.

동일 key 재사용 차단은 전체 production Claim/TSA Leaf 발급 이력에 적용한다. 다만 cross-encoding public-key identity algorithm은 C2PA가 정하지 않으므로 승인된 `keyReuseIdentity` profile이 있을 때만 판정한다. 현재 [`OD-KEY-01`](claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md#6-operations-decision-register)이 `TBD`이므로 모든 Claim/TSA issuance를 비활성화한다. 향후 identifier 보존기간, 원 공개키/Subscriber 연결정보 분리와 삭제 예외는 CPS/privacy inventory에서 함께 승인한다.

### 3.3 TSA key activation과 CA validity의 분리

On-Device TSA의 staged activation은 C2PA가 정한 X.509 상태가 아니라 이 프로젝트의 `ARCH-DECISION`이다.

이 절은 Certificate Platform의 server activation resource/state machine, signed authorization·receipt·finalization contract와 reconciliation의 canonical owner다. 03은 device-side 검증·실행과 실제 key-state observation을, 02는 TSA Leaf enrollment와 검증된 issuance tuple 전달만 소유한다. 이 protocol은 `ARCH-DECISION`이며 C2PA 또는 RFC 3161 wire format이 아니다.

```text
TSA Leaf certificate: ISSUED_VALID 또는 REVOKED/EXPIRED

External TEE key: STAGED_DISABLED → COMMITTED_DISABLED
                                     → SIGNING_ACTIVE → RETIRED → DESTROYED

Server activation transaction: PREPARED → COMMIT_AUTHORIZED
                                         → DEVICE_COMMITTED → SERVER_FINALIZED
```

모든 activation authorization/receipt/finalization artifact는 최소 `artifactType+version`, `transactionId/idempotencyKey`, `{organization, operator, tsaServiceId, tsuInstanceId, environment}`, provider/profile, `K_tsu` SPKI digest, TSA Leaf issuer+serial+digest, current/target key ID와 state, device epoch/monotonic counter, request/previous-artifact digest, `issuedAt/notBefore/expiresAt`, emergency/policy version과 signer key ID/signature를 결속한다. Receipt는 적용 결과, resulting device state/active-key count와 authorization digest를 device-authoritative signature로 결속한다. Unknown version, wrong tuple/key/certificate/environment, expiry, replay, counter rollback, out-of-order transition 또는 signature failure는 `RECOVERY_REQUIRED`이며 수동 `PASS`가 없다.

- 새 TSA Leaf가 X.509 관점에서 `good`이어도 staged key는 RFC 3161 signing에 사용할 수 없다.
- 서버는 device key state를 권위 있게 소유하지 않고 signed Prepare/Commit Receipt와 freshness를 기록한다.
- timeout, response loss와 retry는 동일 durable receipt/finalization result로 reconciliation한다.
- server journal 손실·counter 충돌·receipt 검증 실패는 `RECOVERY_REQUIRED`로 처리하고 수동 승인만으로 key를 활성화하지 않는다.
- 한 TSU의 active timestamp key는 최대 하나여야 한다. 외부 TEE hardware ACL과 acceptance test가 이를 강제해야 한다.
- HSM activation PIN/share와 TSA key activation transaction을 같은 `activation`이라는 이유로 혼동하지 않는다.

### 3.4 CA key generation·보호·backup

`C2PA-REQUIRED` 통제는 다음과 같다.

1. 승인된 ceremony script에 역할, 사전 승인, HSM/activation material, 상세 단계, 물리 조건, 종료 후 보관, 참가자·증인 sign-off와 deviation을 포함한다.
2. CA key generation은 secure physical/cloud environment, trusted roles, multi-person/split knowledge 아래 수행하고 독립 입회 또는 녹화와 audit log를 남긴다.
3. 생성 module은 FIPS 140-2 Level 2+, FIPS 140-3 Level 2+ 또는 적용 technical/business requirement에 적합한 Common Criteria Protection Profile or Security Target, EAL4+ 조건을 만족한다.
4. Root와 Issuing CA private key의 저장·사용 module은 CP 문언상 FIPS 140-2 Level 2+ secure cryptographic device여야 하고, 그 device는 3-tier data center 또는 commercial cloud provider의 HSM 환경에 둔다. CA private key plaintext가 module boundary 밖에 존재해서는 안 된다.
5. Root/Intermediate signing key는 한 사람이 단독으로 물리·논리 접근할 수 없으며 private-key operation은 module 내부에서 수행한다.
6. backup/recovery plan을 최소 연 1회 검토하고 모든 copy를 inventory하며 원본과 같은 multi-person control을 적용한다.
7. 최소 한 copy를 off-site에 두되 plaintext export/storage는 금지한다.
8. Root/Issuing CA 외 key는 key class별로 backup의 `PERMITTED`/`FORBIDDEN`을 CPS와 key inventory에 고정한다. Backup이 허용되면 원 cryptographic module과 일관된 security controls를 적용하고 plaintext export/storage를 금지한다(`C2PA-REQUIRED`, conditional). 금지된 class는 HSM/TEE policy로 backup/export operation을 거부한다. 이 규칙은 CP가 금지한 Subscriber Claim key escrow/recovery를 CA가 수행할 권한을 만들지 않는다.
9. CA/HSM activation data를 암호학적·물리적 통제로 보호한다.

위 2번은 일반 CA key generation에 적용되는 CP 최소선으로 독립 입회 또는 녹화를 허용한다. 그러나 C2PA Trust List 또는 C2PA TSA Trust List에 올릴 Root/Intermediate certificate의 key ceremony evidence는 다음 중 하나를 만족해야 한다.

1. 독립 입회된 key generation ceremony와 참가자·증인이 서명한 ceremony script, 또는
2. ceremony와 script가 적용 요구에 적합함을 증명하는 qualifying WebTrust for CA report를 C2PA가 waiver evidence로 수용한 기록.

Trust List 대상 ceremony에서 녹화만 존재하는 것은 위 application evidence를 충족하지 않는다.

CP의 key generation 문구는 FIPS 140-3/CC를 포함하지만 Root/Issuing CA key storage 문구는 FIPS 140-2 Level 2+만 명시하는 불일치가 있다. FIPS 140-3-only 또는 CC-only module을 저장·사용 경계로 채택하려면 C2PA Conformance owner의 서면 clarification 전에는 production activation을 차단한다. CPS와 ceremony evidence에는 정확한 module certificate/version, 물리·cloud 배치와 검증 상태를 기록한다.

## 4. PKI와 Certificate Status 운영

### 4.1 Claim/TSA trust domain과 production topology

C2PA v0.2 profile 문구의 stricter intersection을 따르는 production baseline은 다음과 같다.

```text
C2PA Root CA (project ARCH: offline; cA=true, pathLen<=2)
├─ [Root-issued certificate status signer/source: OPEN-STS-01]
├─ C2PA First Intermediate CA (cA=true, pathLen=1)
│   ├─ [First-Intermediate-issued certificate status signer/source: OPEN-STS-01]
│   └─ Claim Signing Issuing CA (cA=true, pathLen=0)
│       ├─ Claim Signing Leaf AL1/AL2
│       └─ Claim OCSP signer: issuer CA 자체 또는 direct delegated responder
└─ TSA Issuing CA (cA=true, pathLen=0, direct Root issuance)
    ├─ TSA Time-Stamp Signing Leaf
    └─ TSA Leaf status signer/source: OCSP 또는 CRL
```

Root를 offline으로 운영하는 것은 C2PA certificate profile 자체의 요구가 아니라 key-exposure를 줄이기 위한 이 project의 `ARCH-DECISION`이다. 따라서 Root-issued certificate에 OCSP를 선택하면 offline signing policy를 훼손하지 않는 별도 direct delegated responder와 ceremony를 설계해야 한다.

논리적 trust domain은 반드시 분리한다.

| 항목 | Claim domain | TSA domain |
|---|---|---|
| Last Issuing CA | Claim Signing Issuing CA | TSA Issuing CA |
| EKU | Claim 전용 profile | 정확히 `id-kp-timeStamping` |
| HSM (`ARCH-DECISION`) | Claim 전용 key/object/authorization | TSA 전용 key/object/authorization |
| Relying-party anchor set | C2PA Trust List | C2PA TSA Trust List |
| Status | Claim OCSP 필수 | TSA OCSP 또는 CRL |

Conformance Program은 Claim과 TSA가 같은 Root로 ladder-up하는 구성을 금지하지 않으며, 그러한 경우 같은 Root certificate를 두 신청 section에 기재하라고 안내한다. 그러나 실제 C2PA Trust List와 TSA Trust List 등록은 각각 C2PA 심사·승인을 받아야 한다. 별도 Root로 compromise blast radius를 분리할 수도 있으므로 실제 Root 공유 여부는 `OPEN-PKI-01`이다. 어느 선택에서도 Claim/TSA Issuing CA key, HSM authorization, certificate profile, status scope와 trust-list 소비는 분리한다.

TSA Issuing CA의 human-readable profile은 Issuer가 Root CA라고 명시하지만 AKI 설명은 root 또는 intermediate를 허용하여 upstream 모순이 있다. 서면 clarification 전까지 `First Intermediate → TSA Issuing CA` 경로는 production에서 금지하고 direct Root issuance만 사용한다. Claim Issuing CA는 Root 또는 subordinate parent가 허용되며 이 설계는 First Intermediate를 사용한다.

각 delegated OCSP responder certificate는 상태를 제공할 certificate의 cognizant Issuing CA가 직접 발급한다. 한 responder credential로 다른 Issuing CA의 certificate status를 서명하지 않는다. Issuer별 status 선택은 다음 표에 고정한다.

| Certificate class | Issuer | CP 최소 status | Production 결정 |
|---|---|---|---|
| First Intermediate CA | Root CA | OCSP 또는 CRL | `OPEN-STS-01`; Root 직접 online signing을 피하려면 CRL 또는 Root 직접발급 delegated OCSP responder |
| Claim Signing Issuing CA | First Intermediate CA | OCSP 또는 CRL | `OPEN-STS-01`; 선택한 source가 Claim ICA status를 권위 있게 제공 |
| Claim Signing Leaf | Claim Signing Issuing CA | OCSP 필수; CRL은 추가만 가능 | issuer CA 자체 OCSP 또는 Claim ICA가 직접 발급한 responder |
| TSA Issuing CA | Root CA | OCSP 또는 CRL | `OPEN-STS-01`; Root-issued First Intermediate와 같은 responder credential을 자동 공유하지 않음 |
| TSA Time-Stamp Signing Leaf | TSA Issuing CA | OCSP 또는, OCSP 미제공 시 CRL 필수 | `OPEN-STS-01`; TSA ICA별 source와 cache scope 고정 |
| OCSP Responder Leaf | cognizant Issuing CA | profile에 AIA/CDP·Certificate Policies 금지, OCSP NoCheck | `ARCH-DECISION`으로 짧은 수명·선제 rollover·compromise 즉시 traffic 차단을 운영 |

### 4.2 Profile 판정과 upstream 불일치 처리

CA/OCSP certificate conformance는 다음 세 gate를 모두 통과해야 한다.

```text
strict raw DER와 암호학적 검증
AND decoded certificate의 공식 JSON schema 검증
AND parent/child·chain·운영상 cross-object invariant 검증
```

공식 `*.cert.schema.json`은 decoded JSON의 shape/profile regression 기준이며 다음 사실을 단독으로 증명하지 않는다.

- 실제 certificate signature가 유효한지
- Issuer가 실제 Parent Subject와 같은지
- AKI가 Parent SKI와 같은지
- serial이 Issuing CA 범위에서 유일한지
- 올바른 Trust List anchor까지 path가 구성되는지
- OCSP/CRL과 certificate가 현재 상태인지

현재 snapshot의 upstream 불일치는 더 엄격한 교집합으로 처리한다.

| 항목 | 불일치 | Production 결정 |
|---|---|---|
| Root AKI | YAML/CP summary는 optional, 공식 JSON schema는 AKI occurrence 요구 | non-critical AKI를 필수로 넣고 `AKI.keyIdentifier == Root.SKI` |
| TSA ICA parent | Issuer 설명은 Root, AKI 설명은 root 또는 intermediate | direct Root issuance만 허용; intermediate 경로는 clarification 전 차단 |
| First Intermediate AKI 설명 | YAML이 parent가 아닌 자기 SKI처럼 읽힐 수 있음 | RFC 5280 의미대로 `Child.AKI == Parent.SKI`를 cross-object 검사 |
| Android `bootPatchLevel` | CP 표는 Tag 718, AOSP schema는 vendor 718/boot 719 | provider parser는 AOSP Tag 719 사용, clarification trace 유지 |
| Claim Leaf Ed25519 issuer signature | Leaf profile은 Ed25519 certificate signature를 허용하지만 Claim Signing Issuing CA profile의 signature/SPKI는 RSA 또는 EC만 허용 | Leaf subject SPKI의 Ed25519는 허용하되 issuer signature는 clarification 전 RSA/ECDSA 교집합만 허용 |
| Android attestation extension 위치 | CP v0.2 표는 Leaf extension을 지칭하지만 Android current guidance는 root에서 가까운 첫 occurrence를 선택 | current Android rule을 적용하고 선택된 attestation certificate의 SPKI가 CSR public key와 일치하는지 검증; clarification trace 유지 |

새 C2PA release/errata가 해결하면 source version·schema digest·CPS와 회귀 시험을 함께 갱신한다. 한 source만 조용히 바꿔 기존 production artifact의 의미를 변경하지 않는다.

### 4.3 CA·OCSP certificate profile

공통 CA certificate profile은 X.509 v3, 양수·최대 20-octet serial, RSA-PSS/RSA-SHA2 또는 ECDSA-SHA2 signature, RSA 3072+ 또는 EC P-384/P-521 SPKI, C/O/CN Subject, non-critical RFC 5280 Method (1) SKI, critical Key Usage `keyCertSign+cRLSign`를 사용한다.

Profile의 `Unique Subject Name` 요구를 operationalize하는 canonical ownership registry와 rollover 재사용 범위는 이 project의 `ARCH-DECISION`이다. 단일 certificate JSON schema만으로 증명하지 않고 최소 `logicalPkiIdentityId`, profile role, trust domain, environment, canonical DN, lineage ID, certificate digest, serial, SKI, issuer/AKI와 validity를 기록한다. 동일 canonical DN을 서로 다른 logical Root, First Intermediate, Claim ICA, TSA ICA 또는 OCSP responder identity와 Claim/TSA·production/non-production·서로 다른 issuer scope에 할당하지 않는다. Rollover에서는 동일 `logicalPkiIdentityId`, role, trust domain, environment와 명시적 predecessor/successor lineage에 속하는 경우에만 old/new certificate overlap과 Subject 재사용을 허용한다. 이 규칙을 CPL product의 여러 Claim instance certificate가 같은 product DN을 쓰는 것을 금지하는 전역 Leaf DN 규칙으로 확장하지 않는다.

| Profile | Issuer/validity | Basic Constraints | EKU·Policy | AIA/CDP |
|---|---|---|---|---|
| Root CA | self-signed; `20년`은 예시이고 C2PA max 아님 | critical `cA=true`, `pathLen<=2` | Certificate Policies optional | AIA/CDP 금지 |
| First Intermediate CA | Root; `5년`은 예시이고 C2PA max 아님 | critical `cA=true`, `pathLen=1` | C2PA policy 필수 | OCSP AIA 또는 HTTP CDP 중 최소 하나 |
| Claim Signing Issuing CA | Root 또는 subordinate; 최대 1827일 | critical `cA=true`, `pathLen=0` | non-critical Claim EKU + email/document signing 중 하나 이상; C2PA policy | OCSP AIA 또는 HTTP CDP 중 최소 하나 |
| TSA Issuing CA | 이 project는 Root direct; 최대 5479일 | critical `cA=true`, `pathLen=0` | non-critical, 정확히 timeStamping EKU; C2PA policy | OCSP AIA 또는 HTTP CDP 중 최소 하나 |
| OCSP Responder Leaf | 상태 대상 Issuing CA가 직접 발급; C2PA max 미지정 | critical `cA=false` | critical KU `digitalSignature`; non-critical, 정확히 OCSPSigning EKU; non-critical OCSP NoCheck NULL; Certificate Policies 금지 | AIA/CDP 금지 |

AIA가 있으면 `id-ad-ocsp` HTTP URI를 포함하고 `id-ad-caIssuers` HTTP URI를 포함하는 것이 권고된다. CA가 소유한 별도 private CPS policy OID를 허용할 수 있지만 필수 C2PA policy OID를 대체하지 않는다.

OCSP Responder Leaf는 위 공통 CA key size를 상속하지 않는다. Responder profile은 양수·최대 20-octet serial, RSA-PSS/RSA-SHA2 또는 ECDSA-SHA2 certificate signature(EdDSA 제외), C/O/CN Subject, RSA 2048+ 또는 EC P-256/P-384/P-521 SPKI, non-critical Method (1) SKI와 `AKI.keyIdentifier == IssuingCA.SKI`를 요구한다.

### 4.4 CA CSR과 CA certificate 발급 gate

Root, First Intermediate, Claim ICA와 TSA ICA key에는 3.4절의 C2PA CA-key cryptographic-module 통제를 적용한다. OCSP responder key를 HSM 또는 승인 cryptographic boundary에서 생성·사용하는 것은 이 project의 `ARCH-DECISION`이다. 각 key의 PKCS#10 CSR은 다음 gate를 통과한다.

1. raw DER가 trailing data 없는 단일 PKCS#10 object인지 확인한다.
2. CSR `CertificationRequestInfo` signature를 CSR SPKI로 실제 검증한다.
3. duplicate attribute/extension, ambiguous encoding과 unknown critical request를 거부한다.
4. decoded CSR을 해당 공식 `*.csr.schema.json`과 고정 digest로 검증한다.
5. Subject, key algorithm/size/curve, BC/KU/EKU/policy와 AIA/CDP 요청을 profile과 비교한다.
6. CSR requested extension을 최종 certificate에 복사하지 않고 CA-controlled template을 다시 구성한다.
7. Issuer, serial, validity, SKI, AKI, AIA/CDP와 policy는 ceremony-approved profile에서 결정한다.
8. Parent key operation 권한과 pathLen을 HSM authorization 및 pre-sign policy에서 확인한다.
9. Root signing은 최소 2 trusted persons가 참여하고 한 명이 deliberate command를 수행한다.
10. 발급 후 4.5절의 self-check가 실패하면 certificate를 activate·publish하지 않는다.

Root key는 self-signed Root, subordinate/cross certificate, OCSP responder와 CRL의 허용된 서명에만 사용한다. First Intermediate `pathLen=1` key는 subordinate CA, 승인 infrastructure certificate와 직접 발급하는 OCSP responder 범위로 제한한다. Claim/TSA Subscriber Leaf는 `pathLen=0` last Issuing CA만 발급한다. Cross-certificate는 C2PA 허용 key-use 범위에는 있지만 이 project production default는 금지하며 사용하려면 별도 CPS·path ambiguity 분석·상호운용 승인이 필요하다.

### 4.5 CA certificate output self-check

발급된 CA/OCSP certificate마다 다음을 재검증하고 immutable DER digest와 결과를 ceremony record에 연결한다.

```text
strict DER parse and one certificate object
AND certificate signature valid
AND tbsCertificate.signature == outer signatureAlgorithm
AND serial positive, <=20 octets, unique within issuer
AND notBefore < notAfter and profile validity bound
AND Subject/Issuer canonical comparison PASS
AND canonical Subject ownership and rollover lineage PASS
AND SPKI algorithm/size/curve PASS
AND SKI == RFC 5280 Method (1)
AND AKI.keyIdentifier == Parent.SKI
AND BC/KU/EKU/policy/AIA/CDP/criticality/cardinality PASS
AND forbidden/duplicate/unknown-critical extensions absent
AND official decoded certificate schema PASS
AND RFC 5280 path validation to intended trust anchor PASS
AND status mechanism and publication readiness PASS
```

추가 cross-object 조건은 다음과 같다.

- Root는 `Issuer == Subject`, self-signature valid, project-required `AKI == SKI`다.
- 모든 child는 `Issuer == Parent.Subject`, signature가 Parent SPKI로 검증되고 `AKI == Parent.SKI`다.
- Canonical Subject DN은 production history 전체에서 하나의 logical PKI identity와 lineage에만 귀속된다. 같은 lineage의 rollover는 허용하지만 다른 role, trust domain, environment 또는 issuer scope의 identity와 충돌하면 발급을 거부한다(`ARCH-DECISION`).
- Child validity가 Parent validity 밖으로 나가지 않도록 하는 것을 project invariant로 적용한다.
- Root `pathLen<=2`, First Intermediate `pathLen=1`, last Issuing CA `pathLen=0`를 path 전체에서 평가한다.
- Claim Leaf는 Claim ICA만, TSA Leaf는 TSA ICA만 서명한다.
- Claim과 TSA path는 각각 올바른 C2PA Trust List anchor set으로 검증한다.
- API `certificateChain`은 Leaf issuer부터 상위 intermediate 순서이며 trust anchor/root는 제외한다.

### 4.6 Certificate chain publication과 Trust List

- Claim chain과 TSA chain의 source, cache, active anchor set을 별도로 유지한다.
- C2PA Trust List/TSA Trust List의 trust anchor는 Root 또는 subordinate일 수 있으므로 path validator는 해당 목록에서 선택된 active anchor를 명시적 input으로 사용한다.
- Trust List ingestion은 pinned C2PA extension schema와 모든 external `$ref` dependency의 exact-byte bundle로 schema를 검증하고, `LoTESequenceNumber`, `ListIssueDateTime`, `NextUpdate`, service certificate, `ServiceStatus`, `StatusStartingTime`과 digest를 기록한다. `$ref`를 network latest나 checkout-relative 미고정 파일로 해석하지 않는다.
- Schema PASS와 별도로 모든 current `ServiceInformation` 및 존재하는 각 `ServiceHistory` entry에 `ServiceStatus`와 `StatusStartingTime`이 실제 위치에 존재하는지 검사한다. Status는 `http://c2pa.org/conformance/trust-list/trusted` 또는 `http://c2pa.org/conformance/trust-list/untrusted`와 exact-match해야 하고, time은 엄격한 RFC 3339 `date-time` parser를 통과해야 한다. Missing/wrong-type/unknown URI, parse 불가 시각, 모순되거나 역행하는 history는 list 전체를 malformed로 거부한다. 이는 11.3절에 기록한 upstream schema gap을 보완하는 독립 semantic gate이며 schema validator의 `format` 동작에 의존하지 않는다.
- 운영 list의 파일 hash를 영구 pin하지 않는다. 판단에 사용한 각 snapshot digest·issue/next-update·status를 record에 pin한다.
- 현재 C2PA Trust List가 공통 detached-signature wire format을 정의한다고 가정하지 않는다. 승인된 배포 channel의 인증, schema/digest 검증과 multi-party change review를 CPS에 정의한다.
- stale, malformed, rollback된 list 또는 source authenticity를 확인할 수 없는 상태에서 신규 production issuer activation과 영향을 받는 발급을 차단한다.
- C2PA list removal/emergency notice는 local cache의 `trusted`를 이기며 영향 path와 Leaf를 dependency index로 찾는다.
- Test CA/TSA certificate는 Trust List 신청·production chain·production status에 포함하지 않는다.

선택한 trust anchor/service certificate가 해당 목록에 게시되고 `ServiceStatus`가 `trusted`이며 `StatusStartingTime <= activationAt`이고 독립 path test와 3.4절의 Trust List 대상 ceremony evidence acceptance가 통과하기 전에는 `TRUST_PUBLISHED`를 완료하거나 production issuer로 전환하지 않는다. 모든 신규 subordinate/issuer를 list에 직접 올려야 한다는 뜻은 아니며, 실제 등록 대상과 ladder-up chain은 C2PA 승인 record를 따른다.

### 4.7 Issued-certificate Repository와 revocation source

두 repository 역할을 분리한다.

| Repository | 대상·접근 | 최소 보존/가용성 |
|---|---|---|
| Internal issued-certificate repository | serial, Subject, validity, extensions, DER digest, revocation status; 엄격한 접근·감사 | certificate 만료 후 최소 1년 |
| Public status repository | 모든 unexpired certificate의 current valid/revoked status | 24×7 publicly accessible |

Claim certificate의 OCSP response는 certificate 만료 후 최소 1년인 record-keeping 기간까지 제공한다. Claim에 CRL을 추가할 수 있지만 OCSP를 대체하지 않는다. Subordinate CA와 TSA certificate는 OCSP를 제공할 수 있고, 제공하지 않으면 CRL이 필수다.

Revocation case는 다음 시각과 상태를 별도로 기록한다.

```text
DETECTED → CASE_OPEN → ISSUANCE_HOLD
→ REQUEST_AUTHENTICATED (외부 요청인 경우)
→ SCOPE_RESOLVED → REVOCATION_APPROVED
→ CA_STATUS_REVOKED → OCSP/CRL_PUBLISHED
→ MULTI_VANTAGE_VERIFIED → NOTIFIED → CLOSED/RCA
```

CP의 revocation trigger는 CPL status `revoked*`, 인증·검증된 C2PA/Subscriber 요청, suspected/confirmed Generator compromise 또는 적용 AL의 attestation failure, confirmed private-key exposure, CP non-compliance와 misuse다. 이 조건이 성립한 certificate는 모두 revoke해야 한다. Subscriber/C2PA 요청은 요청자를 인증하고 진위·유효성을 검증한 뒤 72시간 안에 revoke한다. 다른 trigger의 처리 SLA는 CPS가 정하되 revocation 의무 자체를 재량으로 바꾸지 않는다.

내부 status가 `REVOKED`로 commit된 뒤 publication이 실패해도 `good`으로 rollback하지 않는다. `STATUS_PUBLICATION_FAILED` incident를 열고 재게시하며, 신규 발급은 영향 범위에 따라 중단한다.

### 4.8 OCSP 운영

OCSP response는 최소 RFC 6960 profile을 따른다.

- malformed request, unsupported service 또는 필요한 식별정보가 없으면 성공 response를 만들지 않는다.
- RFC 6960 authorization은 issuer CA 자체, 대상 certificate issuer가 직접 발급한 designated responder 또는 requestor가 local configuration으로 별도 신뢰한 responder를 허용한다. 이 project의 portable production response는 issuer CA 자체 또는 C2PA profile의 direct delegated responder만 사용한다. Locally trusted responder는 CPS·relying-party 범위·C2PA 상호운용 승인을 명시하기 전 금지한다.
- delegated responder certificate는 C2PA OCSP responder profile과 정확한 `id-kp-OCSPSigning`, OCSP NoCheck를 가져야 한다.
- Portable direct delegation에서는 responder certificate와 status 대상 certificate가 같은 issuer signing key로 서명됐는지 확인한다. 다른 issuer key나 CA rollover key에 걸친 responder는 local-trust 예외로 조용히 수용하지 않고 새 direct credential을 발급한다.
- response의 `CertID`에 있는 `issuerNameHash`, `issuerKeyHash`, serial이 request certificate와 대응하는지, signature, ResponderID, signer identity/authorization을 검증한다.
- `thisUpdate`가 충분히 최근인지 확인하고 `nextUpdate`가 있으면 현재보다 미래인지 확인한다.
- `producedAt`은 response signing 시각이며 status가 알려진 시각인 `thisUpdate`를 대체하지 않는다.
- `good`은 해당 serial이 revoked로 알려지지 않았다는 제한된 의미다. 발급 사실, certificate validity, chain 또는 TSA activation을 보장하지 않는다.
- `unknown`, signature/authorization 실패, stale response와 `tryLater/internalError`를 `good`으로 변환하지 않는다.

다음 값은 `CPS-REQUIRED`다.

- responder credential 실제 validity와 re-key lead time
- authoritative DB→response projection latency
- `thisUpdate` max age, `nextUpdate` horizon과 clock skew
- pre-produced response와 cache/CDN TTL, purge와 multi-region verification
- request nonce 지원 여부와 cache interaction
- signer compromise 시 stop/replace 절차
- external availability, latency, correctness SLO

OCSP NoCheck 때문에 responder credential 자체 status를 반복 확인하지 않는 client가 있을 수 있으므로 responder key compromise를 고영향 incident로 취급하고 key를 짧게 운영하며 Issuing CA별 scope를 제한한다.

### 4.9 CRL 운영

CRL을 선택한 certificate class는 RFC 5280 §5의 최소 profile과 현재 적용되는 update를 따른다.

- v2 CRL, non-empty Issuer, `tbsCertList.signature == outer signatureAlgorithm`과 유효 signature를 확인한다.
- CRL signer가 해당 scope에 대해 authorized되고 certificate Key Usage에 `cRLSign`이 있는지 확인한다.
- `thisUpdate`, `nextUpdate`, AKI와 단조 증가하는 non-critical CRL Number를 검증한다.
- CDP/Issuing Distribution Point와 CRL scope가 target certificate에 맞는지 확인한다.
- revoked entry의 serial, revocationTime과 reason/invalidityDate를 일관되게 처리한다.
- 이해하지 못하는 critical CRL/entry extension, rollback된 CRL Number, signature failure와 stale CRL을 거부한다.

RFC 10007은 RFC 5280 CRL validation에 `cRLSign` 확인을 명시적으로 추가한다. Production source manifest는 RFC 5280과 적용 update를 함께 고정한다.

다음은 CPS에서 결정한다.

- complete/delta CRL 여부, partition과 scope
- 발행 주기, `nextUpdate`, overlap과 maximum stale
- CDN/cache TTL, emergency publication과 purge
- CRL Number durable allocation·rollback 방지
- 대량 폐기 시 size/capacity와 mirror consistency

### 4.10 CA rollover와 changeover

```text
PREPARED → CERTIFIED → TRUST_PUBLISHED
→ ISSUANCE_ACTIVE → RETIRING → RETIRED
→ EXPIRED 또는 REVOKED → DESTROYED
```

1. 새 HSM key와 backup을 ceremony로 생성한다.
2. CA CSR signature/PoP와 공식 CSR schema를 검증한다.
3. Parent가 새 CA certificate를 발급하고 4.5절의 3중 gate를 수행한다.
4. AIA/OCSP/CRL endpoint와 chain retrieval을 먼저 게시·시험한다.
5. 필요한 C2PA Trust List/TSA Trust List 등록과 active status를 확인한다.
6. old/new path, Leaf issuance, status와 relying-party interoperability를 overlap 시험한다.
7. issuer switch를 승인하고 old issuer의 신규 Leaf signing authorization을 제거한다.
8. old certificate의 status, repository와 audit를 의무기간 동안 유지한다.
9. 종료 조건 뒤 private key destruction ceremony를 수행한다.

CA key changeover는 secure·documented periodic process로 수행하고 Subscriber에 사전 통지하는 것이 권고된다. 실제 Root/First Intermediate validity, rollover lead/overlap, 최대 child `notAfter`, subscriber notification, cross-cert와 destruction 시점은 CPS decision이다.

## 5. Attestation trust와 Reference Value 운영

### 5.1 Claim AL2와 On-Device TSA의 규범 경계

| Usage | C2PA가 직접 요구 | Provider/CPS가 정의 |
|---|---|---|
| Claim AL2 | CPL method, O.1~O.4 hardware-backed Dynamic Evidence, challenge를 사용하는 flow의 일치, Android predicate | wire schema, root/status 배포, Reference Value feed, cache·rotation |
| On-Device TSA | TA의 TEE 실행, `K_tsu` TEE 생성·보관, UTC(k), drift-stop, timestamp 전용 key, TSU당 active key 하나 | 이를 보증할 설계·TEE enforcement·시험·운영 audit; optional custom Evidence와 project staged activation |
| Backend TSA | TSU signing key를 ISO/IEC 15408 또는 동등한 국제 평가 기준의 EAL4+ trustworthy system, FIPS 140-2/140-3 Level 3+, 또는 private key와 관련 asset 보호가 평가 범위인 적절한 Common Criteria Protection Profile or Security Target EAL4+ device에서 생성·보관 | enrollment custom Evidence 채택 여부 |

Claim AL2와 optional TSA attestation profile은 같은 registry implementation을 재사용할 수 있지만 `usage`, policy namespace, trust anchor authorization과 normalized verdict를 공유하지 않는다. Claim O.1~O.4 PASS를 TSA TEE/time 적합성 PASS로 바꾸지 않는다.

현재 CPL schema의 `attestationMethods`는 optional이지만 값이 있으면 열거된 공식 method만 허용된다. AL2 요청인데 record에 method가 없거나 제출 Evidence와 승인 method를 연결할 수 없으면 “schema가 optional”이라는 이유로 진행하지 않고 발급을 차단하여 C2PA/Provider owner의 clarification을 받는다. Custom SAK Claim Evidence는 단순히 새 method 문자열을 만들어 사용할 수 없고, 기존 method에 정확히 부합하는지 또는 C2PA 확장이 승인됐는지 확인해야 한다. Optional TSA custom Evidence는 CPL method가 아니라 별도의 TSA CPS extension namespace다.

TSA는 hashing algorithm, time-stamp signature의 예상 수명, Subscriber/Relying Party 의무, 사용 제한, 검증 방법, intended accuracy와 TSA event logging·retention을 공개 business practices에 명시한다. Intended accuracy는 각 time-stamp에 정의되고 그 범위로 동기화되어야 하며 1초 이하는 `C2PA-SHOULD`다. 적절한 기관이 leap second를 통지하면 clock synchronization을 유지하는 것은 `C2PA-REQUIRED`다. Bulletin source/authentication, step·smear·holdover 방식과 rehearsal window는 `PROVIDER-BOUND`/`CPS-REQUIRED`이며 어느 방식도 declared accuracy와 UTC(k) traceability를 약화할 수 없다. 요청 MessageImprint는 SHA2-256/384/512만 허용하고, timestamp key는 전용이며 TSU당 active key는 하나다.

General TSA time value의 UTC(k) traceability는 CP lowercase `shall`에 따른 `C2PA-OBLIGATION`이고, On-Device TSA가 최소 24시간마다 시도하는 online synchronization source의 UTC(k) traceability는 대문자 `SHALL`에 따른 `C2PA-REQUIRED`다. 구현 predicate는 같더라도 RTM의 source locator와 요구 수준은 분리한다.

On-Device TSA runtime 준수 판정은 [03 §7~§8](03-On-Device-Runtime.md#7-on-device-tsa의-trusted-time과-보호-상태)의 external acceptance가 소유한다. 최소 `lastSyncAttemptAt`, UTC(k)-traceable source identity, sync result, declared accuracy, observed drift, active-key count, leap-bulletin authority/version/checked-at, 다음 event/effective time, handling mode와 readiness/result를 설계·시험·운영 record로 확인한다. Remote telemetry를 채택하면 freshness와 source authenticity가 검증된 observation으로 수집한다. 마지막 online synchronization **시도**가 24시간을 초과하거나 drift가 declared accuracy 밖이거나 leap readiness를 증명할 수 없으면 관련 runtime/activation을 차단하고 incident를 연다. 24시간 attempt miss만으로 기존 TSU도 중단하려면 승인된 offline-cutoff `ARCH-DECISION`이 별도로 있어야 한다. Drift 초과 또는 leap 처리 실패로 declared accuracy를 벗어나면 외부 TSA owner는 TSU timestamp issuance를 즉시 중단해야 한다. X.509 certificate status와 Leaf enrollment은 이 runtime 상태와 별도다.

### 5.2 Provider Profile과 trust bundle

5.2~5.6의 Evidence provider lifecycle은 Claim AL2와 optional TSA attestation profile에만 적용한다. Base TSA Leaf enrollment은 provider가 없다는 이유로 차단하지 않는다.

Provider Profile은 mutable configuration이 아니라 immutable·versioned deployment artifact로 관리한다(`ARCH-DECISION`/`PROVIDER-BOUND`).

| 영역 | 필수 등록정보 |
|---|---|
| Identity | `providerId`, `usage`, immutable `profileVersion`, owner, environment |
| C2PA mapping | Claim이면 정확한 CPL `attestationMethods` 값과 O.1~O.4 coverage |
| Encoding | media type, ASN.1/CBOR/COSE schema, canonical signed bytes, size/depth/count limits |
| Discriminator | signed profile ID/version, audience 또는 domain separator의 정확한 위치 |
| Key binding | attested subject key 위치·format·normalization과 CSR SPKI 비교법 |
| Challenge | 위치, raw/transform algorithm, entropy·길이·TTL·single-use 규칙 |
| Trust | root certificate/SPKI fingerprint, chain constraints, policy OID, algorithms |
| Status | authoritative source, source authentication, response semantics, freshness/cache/rollback |
| Time | UTC(k) source, sync-attempt semantics, declared accuracy/drift, leap-bulletin authority/authentication·rollback, step/smear/holdover mode와 recovery |
| Reference | bundle signer, component scope, version comparison과 effective/expiry rules |
| Appraisal | signed claims를 Claim O.1~O.4 또는 TSA-specific verdict로 mapping |
| Implementation | parser/verifier artifact digest·version과 runtime isolation |
| Tests | positive, malformed, wrong-key/audience, replay, revoked/stale/rollback vectors |
| Operations | lifecycle state, cutover, emergency owner/epoch와 dependency index |

Root를 enrollment request 또는 Evidence package에서 trust anchor로 받아들이지 않는다. Provider의 authenticated official channel과 별도 out-of-band channel로 Root fingerprint/SPKI를 확인하고 권한을 `{providerId, usage, profileVersion, environment}`로 제한한다.

### 5.3 Provider lifecycle

다음 상태 이름과 transition은 C2PA가 정한 wire/state model이 아니라 이 project의 `ARCH-DECISION`이다.

```text
DRAFT → VERIFIED → SHADOW → ENABLED → DRAINING → RETIRED
   └──────────────→ EMERGENCY_BLOCKED ←──────────────┘
```

| 상태 | 새 production freshness context | in-flight evaluation | Certificate 발급 |
|---|---:|---:|---:|
| `DRAFT/VERIFIED` | 금지 | 금지 | 금지 |
| `SHADOW` | 금지 | 비교 판정만 | 금지 |
| `ENABLED` | 허용 | 허용 | 허용 |
| `DRAINING` | 금지 | cutoff 전 challenge만, security block이 없을 때 | 조건부 |
| `RETIRED` | 금지 | 금지 | 금지 |
| `EMERGENCY_BLOCKED` | 금지 | 즉시 실패 | 금지 |

모든 production gate를 통과하기 전 상태는 최대 `SHADOW`다. 현재 문서 기준 production `ENABLED` provider는 없다.

최종 CA/HSM signing 직전에 provider state, `emergencyEpoch`, status freshness와 current Reference/CPL state를 다시 읽는다. 검증 시작 때 `ENABLED`였더라도 중간 차단 뒤 cached PASS로 발급하지 않는다.

### 5.4 Provider root/status rotation과 cache

Planned rotation은 새 root/profile을 새 version으로 등록하고 old/new overlap과 cutover를 명시한다. 신규 freshness context는 cutover 뒤 새 profile에 bind하고 구 profile은 `DRAINING`으로 전환한다. 구 trust material은 감사 재현용 archive에 보관할 수 있지만 active trust store에서 제거하며 configuration rollback으로 재활성화하지 않는다.

Provider status는 다음처럼 판정한다.

```text
fresh authenticated status + provider semantics상 GOOD
  → 다음 검증 가능

REVOKED / SUSPENDED / BLOCKED
  → 거부

timeout / authentication failure / malformed / stale /
rollback / unknown semantics
  → 발급 금지와 내부 failure 기록
```

```text
freshUntil = min(provider-declared expiry,
                 authenticated feed/HTTP Cache-Control expiry,
                 CA CPS maxStatusAge)
```

- `stale-if-error`로 AL2/TSA certificate를 발급하지 않는다.
- status fetch는 single-flight와 bounded backoff로 thundering herd를 막되 freshness를 연장하지 않는다.
- `fetchedAt`, source sequence/version, digest, result와 `freshUntil`을 decision record에 pin한다.
- 정상적으로 검증된 empty/not-listed 결과와 feed 자체의 조회·검증 실패를 구분한다.
- local emergency deny는 provider의 이후 `GOOD` 결과보다 우선하며 새 승인 없이는 자동 해제하지 않는다.

Android provider profile은 공식 current guidance에 맞춰 off-device에서 전체 chain과 모든 chain certificate status를 검증하고 current root set의 overlap을 지원한다. Attestation extension이 leaf에 있다고 가정하지 않고 root에서 가까운 첫 신뢰 occurrence를 선택하며 provisioning-information extension의 인접 규칙을 적용한다. 선택된 attestation-bearing certificate의 SPKI가 CSR SPKI와 일치해야 한다. Factory-key legacy validity 예외와 RKP validity를 같은 규칙으로 일반화하지 않는다.

### 5.5 Reference Value lifecycle

다음 상태 이름, bundle wire shape와 overlap mechanism은 C2PA가 표준화한 형식이 아니라 이 project의 `ARCH-DECISION` 또는 provider별 `PROVIDER-BOUND` 계약이다. 실제 O.1~O.4 predicate는 [02 §5](02-Certificate-Enrollment.md#5-claim-signing-leaf-al2-발급-가이드)가 소유한다.

```text
DRAFT → APPROVED → ACTIVE → DEPRECATED
                         └→ REVOKED
```

Reference Value bundle은 최소 다음을 포함한다.

- provider/producer identity와 bundle authentication
- 적용 product/package/signer, TA UUID/measurement, component inventory
- hash/measurement algorithm과 canonical encoding
- version comparison, minimum TCB/security version
- 승인 revision 또는 patch 기준
- HIGH/CRITICAL vulnerability ID, detection date, affected range와 minimum fixed version
- `issuedAt`, `validFrom`, `expiresAt`, monotonic sequence/version
- supersedes 관계, digest와 revocation reason

상태기계와 무관하게 Claim AL2 판정은 CP가 고정한 다음 경계를 완화할 수 없다.

- O.3 platform의 HIGH/CRITICAL vulnerability는 detection 후 90일 안에 patch 또는 mitigation되어야 한다.
- Claim Generator는 security patch 적용 후 90일 이내이거나 CA에 good standing으로 등록된 revision이어야 한다.
- O.4의 Digital Content/Assertion 처리 component 각각에 같은 secure-boot, vulnerability와 patch/revision 조건을 적용하고 inventory coverage 누락을 허용하지 않는다.
- Android `osPatchLevel`은 CSR 제출 월과 직전 3개월의 네 달 값 중 하나이고 미래일 수 없다. `vendorPatchLevel`과 `bootPatchLevel`은 CSR 제출일 기준 90일 이내이고 미래일 수 없다.
- Android parser는 공식 AOSP schema의 `bootPatchLevel[719]`를 사용하며 CP v0.2 표의 Tag 718 불일치는 4.2절 clarification으로 추적한다.

클라이언트가 전달한 Reference Value, `approved=true` 또는 verdict를 정책 입력으로 신뢰하지 않는다. future/expired/unauthenticated/rollback bundle과 revoked measurement는 발급을 차단한다. 과거 allow set으로 되돌려야 해도 기존 version을 재활성화하지 않고 새 sequence와 승인을 만든다.

각 Claim request evaluation 또는 TSA transaction은 하나의 immutable trust/profile/reference/policy snapshot으로 평가한다. 이는 Claim transaction 계약을 뜻하지 않는다. Emergency revoke와 current CPL/provider block은 final signing gate에서 다시 확인하여 pin된 정상 snapshot보다 우선한다. `ACTIVE`/`NEXT` bundle overlap 최대 24시간과 expiry grace 금지는 C2PA 고정값이 아닌 `ARCH-DECISION`이며, `OPEN-RV-01`에서 risk basis·clock/cache 조건과 함께 승인하기 전 production gate로 사용하지 않는다.

### 5.6 Dependency index와 emergency block

모든 issued Leaf를 다음 dependency로 역추적할 수 있어야 한다.

```text
certificate issuer+serial+digest
→ Claim request decision 또는 TSA transaction / CSR SPKI digest
→ provider/profile/verifier version
→ root/intermediate/AK/SAK identifier
→ provider status snapshot
→ Reference Value bundle / measurement / component
→ CPL record and snapshot (Claim)
→ TSA service/TSU/activation artifact (TSA)
```

Emergency block은 provider 전체, usage, profile version, root fingerprint, AK/SAK key ID, Reference bundle, measurement와 component 단위로 적용할 수 있어야 한다. Deny cache는 positive verdict cache보다 우선하고 in-flight issuance를 final gate에서 차단한다. 차단 해제는 이전 bundle 복원이 아니라 새 approved bundle과 incident closure approval로 수행한다.

## 6. 보안 통제와 fail-closed 정책

### 6.1 발급·운영 failure matrix

| 실패 | 요구 수준 | 신규 발급/activation | Status/Repository | 운영 동작 |
|---|---|---|---|---|
| identity/CPL/TSA authorization unknown | `C2PA-REQUIRED`/`CPS-REQUIRED` | 차단 | 기존 status 유지 | source 복구·case 조사 |
| Claim warranty/Agreement/Terms decision missing·expired·scope mismatch | `C2PA-OBLIGATION`/`ARCH-DECISION` enforcement | Claim final signing 차단 | 영향 없음 | Legal/CPS owner 재검증; 수동 waiver로 `PASS` 금지 |
| CSR/key-ownership invalid 또는 CSR key mismatch | key ownership `C2PA-REQUIRED`; CSR 방식 `ARCH-DECISION` | 해당 요청 발급 거부 | 영향 없음 | 발급 차단·audit; Claim 외부 response 형식은 정의하지 않음 |
| Claim AL2 Evidence invalid 또는 key mismatch | `C2PA-REQUIRED` | 요청 AL 발급 거부 | 영향 없음 | lower AL은 별도 명시적 AL1 request만; audit |
| Optional TSA Evidence invalid 또는 key mismatch | `CPS-REQUIRED`/`ARCH-DECISION`, profile-local | 해당 optional profile 발급 거부 | base TSA와 기존 certificate에 자동 영향 없음 | stable failure code·audit |
| provider/profile/reference unknown·stale·rollback | Claim AL2는 C2PA predicate의 project enforcement; optional TSA는 `CPS-REQUIRED`/`ARCH-DECISION` | 영향 Evidence-required profile 차단 | 기존 certificate 자동 good/revoke 판단 금지 | refresh 또는 emergency review |
| provider `EMERGENCY_BLOCKED` | `ARCH-DECISION` | in-flight 포함 차단 | CP trigger 성립 여부와 dependency scope 판정 | incident·mass-impact query |
| HSM unavailable/signing 결과 불확실 | `ARCH-DECISION`/`CPS-REQUIRED` | issuance stop; 불확실 결과를 성공으로 취급하지 않음 | status 별도 유지 | HSM audit+reservation reconciliation |
| certificate post-check 실패 | `ARCH-DECISION` | 반환·publish 금지 | invalid artifact 격리 | CA operation incident |
| issuance DB integrity 불확실 | `ARCH-DECISION` | issuance stop/read-only | 검증된 status 우선 유지 | HSM/repository/audit reconciliation |
| audit durable sink unavailable | `ARCH-DECISION` enforcing audit obligation | security-sensitive 변경·발급 차단 | public status는 별도 continuity | sink 복구·buffer integrity 검증 |
| OCSP/CRL publish 실패 | status availability `C2PA-REQUIRED`; freshness/SLO `CPS-REQUIRED`; 영향 issuance stop `ARCH-DECISION` | risk scope에 따라 신규 발급 stop | revoked를 good으로 rollback 금지 | status incident, multi-vantage 복구 |
| Trust List stale/removed | `C2PA-REQUIRED`/`ARCH-DECISION` | 신규 issuer activation과 영향 issuance 차단 | last artifact를 유효기간 밖으로 연장 금지 | controlled refresh/C2PA coordination |
| On-Device TSA last online sync attempt `>24h` | `C2PA-REQUIRED` attempt obligation + `ARCH-DECISION` response | 관련 신규 activation 차단 | certificate status와 별도 | nonconformance incident; 기존 TSU stop은 승인 offline cutoff 또는 별도 accuracy/traceability failure일 때 |
| TSA drift outside declared accuracy | `C2PA-REQUIRED` | 관련 activation 차단 | certificate status와 별도 | 외부 TSU TST issuance 즉시 stop, 승인된 운영 evidence로 확인; telemetry를 쓰면 authenticated observation 사용 |
| leap bulletin/readiness 또는 activation/time observation unknown·stale·invalid | `ARCH-DECISION` observation; 실제 accuracy 이탈은 `C2PA-REQUIRED` | 관련 신규 activation 차단, 서버 정상 주장 금지 | certificate status와 별도 | 03 acceptance/reconciliation; accuracy 이탈 시 TSU stop |

### 6.2 공통 불변조건

| ID | 불변조건 |
|---|---|
| `SO-GOV-01` | attestation validation, issuance와 revocation은 분리된 권한으로 수행한다. |
| `SO-GOV-02` | Root certificate signing은 trusted role 2인 이상이 참여하고, 모든 CA certificate issuance는 문서화된 multi-person/split-knowledge control을 통과한다. CA key generation·backup·recovery 및 지정 CA equipment/operation access는 `m-of-n`으로 단독 접근을 막는다. Routine Leaf/status signing은 승인 HSM policy와 CPS 자동화 범위에서 수행하며 매 건 human quorum을 요구한다는 뜻이 아니다. |
| `SO-GOV-03` | Claim final signing은 current `WARRANTY_READY`와 Agreement/Terms scope/version을 재확인하며 implicit certificate acceptance나 수동 waiver로 발급 전 legal gate를 대체하지 않는다. |
| `SO-SRC-01` | Profile validator와 release evidence는 pinned Git blob exact bytes만 사용하고 worktree/EOL 변환 또는 digest mismatch를 production input으로 수용하지 않는다. |
| `SO-PKI-01` | CA certificate는 raw DER crypto, 공식 schema, cross-object/chain gate를 모두 통과해야 활성화된다. |
| `SO-PKI-02` | Claim과 TSA Issuing CA key/profile/HSM authorization/status scope를 분리한다. |
| `SO-PKI-03` | Root→First Intermediate→Claim ICA와 Root→TSA ICA direct 경로만 production baseline으로 허용한다. |
| `SO-STS-01` | Revoked durable state는 publication 장애로 good으로 rollback되지 않는다. |
| `SO-STS-02` | Claim OCSP는 Claim certificate 만료 후 최소 1년인 record-keeping 기간까지 제공한다. TSA/Subordinate certificate는 OCSP를 제공하거나, 제공하지 않으면 CRL을 제공하되 그 publication 기간·freshness는 CPS에 고정한다. |
| `SO-TRUST-01` | request가 제공한 root, Reference Value, policy 또는 PASS verdict를 신뢰 설정으로 사용하지 않는다. |
| `SO-TRUST-02` | unknown, stale, expired, revoked, disabled 또는 rollback dependency로는 요청한 Assurance Level의 production issuance를 허용하지 않는다. AL2 실패를 AL1로 처리하려면 02의 별도 lower-AL 재평가·profile·OID·감사 절차를 모두 통과해야 하며 자동 downgrade하지 않는다. |
| `SO-TRUST-03` | Claim AL2와 optional On-Device TSA attestation provider profile은 usage·policy·verdict namespace를 공유하지 않는다. |
| `SO-TRUST-04` | final signing 직전에 current emergency/provider/CPL 상태를 다시 확인한다. |
| `SO-IR-01` | dependency index로 CA/provider/reference compromise의 영향 certificate를 역추적할 수 있다. |
| `SO-IR-02` | TSA signing-key compromise handoff는 해당 key의 모든 TST가 untrusted임을 03에 전달하고 적용 acknowledgement를 audit한다. |
| `SO-AUD-01` | 중요 operation의 actor, time, decision, dependency version과 결과 artifact를 tamper-evident audit에 연결한다. |
| `SO-PRV-01` | private key, credential, HSM activation data와 불필요한 raw device identifier를 log/metric에 기록하지 않는다. |

## 7. Incident Response와 복구

### 7.1 공통 incident 흐름

```text
DETECT
→ TRIAGE AND PRESERVE EVIDENCE
→ CONTAIN / ISSUANCE HOLD
→ RESOLVE DEPENDENCY SCOPE
→ REVOKE / BLOCK / NOTIFY
→ RESTORE IN ISOLATION
→ RECONCILE HSM + DB + REPOSITORY + AUDIT
→ RE-APPROVE
→ ROOT-CAUSE REVIEW AND ACTION TRACKING
```

Incident plan이 breach, key compromise, 자연재해와 CA 운영 중단을 처리하고, critical certificate DB, CA key material, configuration과 audit log의 secure backup 및 documented recovery plan을 유지하는 것은 `C2PA-REQUIRED`다. 역할·communication·escalation의 명시, 정기 drill, 일반 backup의 off-site 보관과 정기 restore test는 CP lowercase `should`를 production baseline으로 채택한 `ARCH-DECISION`이다. 단, CA private key 최소 한 copy의 off-site 보관은 별도 `C2PA-REQUIRED`다.

Security Incident 후 root cause, impact와 lessons learned를 검토하고 재발방지 action을 만든다. C2PA Steering Committee와 Conformance Task Force에 공유해야 하는 incident report 절차를 runbook에 포함한다.

### 7.2 Incident matrix

| 사건 | 즉시 containment | 영향 index | 복구·외부 조치 |
|---|---|---|---|
| Root key compromise | Root/HSM disable, 모든 descendant issuance stop | Root→CA→all Leaf/status signer | 새 trust anchor ceremony, C2PA list 전환, issuer별 descendant status/revocation 수행 |
| First Intermediate/ICA compromise | affected issuer signing stop | issuer key/cert→descendant Leaf | Parent revocation/status, replacement ICA, Trust List/AIA 갱신 |
| OCSP responder compromise | responder key stop, traffic 격리 | responder cert와 서명 response 기간 | 새 직접발급 responder, cache purge, 잘못된 response 조사 |
| Provider Root/AK/SAK compromise | profile/root emergency block | provider key→Evidence→issued Leaf | status 확인, 영향 Leaf revoke 판단, 새 trust bundle |
| Reference Value 오류·malicious allow | 해당 bundle block | bundle/measurement→decisions/certificates | 새 sequence, re-appraisal, 영향 revoke·통지 |
| CPL/Trust List stale·변조 | 영향 issuance 차단 | snapshot→product/chain | authenticated snapshot 복구, C2PA coordination |
| Issuance DB/audit integrity 상실 | issuance read-only/stop | HSM log, serial reservation, repository | isolated restore와 reconciliation; 불확실 artifact 차단 |
| Subscriber Claim key compromise | 특정 Leaf revoke | normalized key/SPKI→serial | fresh key 신규 enrollment |
| TSA signing-key compromise | 외부 TSU signing 즉시 중단, 관련 activation 차단 | TSA service/TSU/key→TSA Leaf와 external impact-handoff ID | TSA Leaf를 revoke한다. CRL reasonCode가 있으면 `keyCompromise(1)`로 하고, 해당 key가 서명한 모든 TST가 `genTime`과 무관하게 untrusted라는 signed handoff를 03 runtime/validator owner와 C2PA incident channel에 전달한다. Fresh key는 과거 TST의 신뢰를 복구하지 않는다. |
| TSA non-compromise cessation | 외부 TSU 신규 signing 중단, activation 종료 | TSA service/TSU/key→TSA Leaf, revocationTime·CRL reason | TSA Leaf를 revoke한다. Revocation 전 TST 신뢰를 유지하려면 authoritative CRL entry에 `unspecified(0)`, `affiliationChanged(3)`, `superseded(4)`, `cessationOfOperation(5)` 중 하나를 넣는다. 그러면 `genTime < revocationTime`만 유지하며, reasonCode가 없거나 그 밖의 값이면 해당 key의 모든 TST를 invalid로 전달한다. |
| TSA time drift/rollback/leap handling failure | 외부 TSU가 timestamp issuance 중단, 관련 activation 차단 | TSA service/TSU/key/time source/bulletin | 승인된 stop record 확인, time 재동기화와 external acceptance 재승인 |
| 전체 zone 장애 | issuance 중단 허용, status continuity 우선 | service/data dependencies | DR restore, no-duplicate reconciliation |

Compromise가 의심되면 definitive scope 확정 전에도 영향 범위의 신규 issuance를 hold한다. Suspected 또는 confirmed Generator Product compromise와 적용 Assurance Level의 attestation failure 자체가 CP revocation trigger이므로, 그 사실과 영향 certificate의 결속이 확인되면 해당 certificate를 revoke해야 한다. Revocation Authority의 재량은 사실관계·영향 scope·dependency 결속을 확인하는 데 있고 CP trigger를 무효화하는 데 있지 않다. Confirmed private-key exposure, CP non-compliance와 misuse도 같은 의무를 따른다.

RFC 3161 token trust 판정과 Claim/Manifest 재검증은 03의 external runtime/validator acceptance가 소유한다. 04는 TST inventory를 직접 소유한다고 주장하지 않고 compromise에는 최소 `{incidentId, tsaServiceId, tsuInstanceId, compromised key/SPKI, TSA Leaf issuer+serial+digest, revocation status/reason, first/last-known observation, allTokensUntrusted=true, publishedAt}`를 서명해 전달하고 delivery/acknowledgement를 audit한다. 가능한 compromise 시각은 incident 우선순위 정보일 뿐 그 이전 TST를 자동 신뢰시키는 cutoff가 아니다. Non-compromise cessation handoff에는 key/certificate binding, authoritative status source와 CRL digest, `revocationTime`, `reasonCodePresent`, `reasonCode`, `tokensBeforeRevocationRemainValid`를 포함한다. ReasonCode가 존재하면 허용값 `0/3/4/5`만 수용하고 `genTime < revocationTime`만 유지하며, reasonCode가 없거나 허용값 밖이면 `allTokensUntrusted=true`로 전달한다.

Root compromise에서 하나의 OCSP responder가 모든 descendant를 전이적으로 `revoked`로 표현할 수 있다고 가정하지 않는다. 각 certificate는 cognizant issuer의 권위 있는 OCSP/CRL source에서 처리하고, subordinate CA status와 C2PA Trust List/TSA Trust List removal·replacement를 함께 수행한다. 이 절차도 trust-anchor replacement를 대신하지 않는다.

### 7.3 CA 또는 RA 종료

CA 운영 종료 또는 RA delegation 폐지를 위한 orderly termination procedure를 CPS와 runbook에 사전 정의한다(`C2PA-REQUIRED`).

1. 종료 결정의 권한, effective time, 영향 CA/RA·Subscriber·certificate·repository scope를 승인한다.
2. RA delegation과 credential을 폐지하고 enrollment/approval access를 차단하며 미완료 Claim request evaluation과 TSA transaction을 fail-closed 또는 승인된 successor로 이관한다.
3. Security incident로 expedited action이 필요한 경우를 제외하고 Subscriber에게 대체 CA/RA로 전환할 충분한 시간을 두고 사전 통지한다(`C2PA-REQUIRED`).
4. 민감 데이터, private key·backup·activation material과 equipment의 보존·이관·파기 방법을 정하고 multi-person evidence를 남긴다. 구체적인 시점과 disposal method는 CPS에 고정한다. 이 secure handling/disposal 상세는 CP lowercase `should`를 채택한 `ARCH-DECISION`이며 다른 절의 private-key backup/archive 금지와 retention 의무를 변경하지 않는다.
5. Unexpired certificate의 24×7 current status, Claim OCSP의 record-keeping 기간, issued-record와 audit/legal hold를 종료 뒤에도 충족하도록 contracted successor 또는 continuity custodian을 지정한다(`C2PA-OBLIGATION`/`ARCH-DECISION`). 이는 Subscriber 또는 CA private key의 escrow/recovery를 허용하지 않으며 private-key custody를 successor에게 자동 이전하지 않는다.
6. C2PA Trust List/TSA Trust List record 변경·removal, Subscriber 통지, public CPS/endpoint 변경과 최종 reconciliation을 완료한다.
7. 종료 뒤 credential·network route·HSM authorization이 남지 않았는지 독립 검토하고 termination report를 보존한다.

### 7.4 DR와 reconciliation

- RTO/RPO는 issuance, status, trust registry, audit와 control plane별로 따로 승인한다.
- Status service는 issuance와 다른 failure domain으로 두고 issuance 중단 중에도 current status를 제공하도록 한다.
- Backup restore는 격리 환경에서 HSM object, certificate DB, serial reservation, revocation, provider sequence와 audit checkpoint를 대조한 뒤 production에 연결한다.
- HSM에서 signature가 생성됐지만 DB commit 여부가 불확실하면 동일 serial/key로 재서명하지 않고 HSM audit와 immutable reservation으로 결과를 확인한다.
- activation projection은 signed receipt/finalization journal에서 복구하고 external TEE state를 서버 추정값으로 덮어쓰지 않는다.
- 복구 후 independent approver가 integrity, status freshness, blocked dependency와 no-duplicate 결과를 확인해야 issuance를 재개한다.
- disaster/compromise/rollback drill 결과와 미해결 action은 release blocker에 연결한다.

## 8. 감사와 개인정보 보호

### 8.1 필수 audit 범위와 event schema

C2PA CP는 issuance, revocation, attestation validation과 access attempt를 포함한 certificate operation의 상세 system/user activity log를 요구한다. 각 event는 Subscriber와 요청한 CA system/personnel identity, timestamp, action과 relevant parameter를 포함한다.

권장 공통 event envelope은 다음과 같다.

```text
eventId, eventType, occurredAt, recordedAt
correlationId, requestContextId, tsaTransactionId, incidentId
actorType, actorId, role, environment, product/service scope
operation, objectType, objectId
previousState, resultingState
decision, decisionReasonCategory, tsaStableReasonCode, tsaRetryable
policy/profile/verifier/reference/trust/status version+digest
csrDigest, normalizedKeyDigest, evidenceDigest
certificateIssuer, serial, certificateDigest
approvalIds, quorumResult, HsmOperationId
sourceCheckedAt, freshUntil, emergencyEpoch
```

다음 event를 최소 catalog에 포함한다.

- identity validation·398일 re-authentication과 authorization change
- Claim freshness/replay context와 TSA challenge/transaction 생성·만료·consume
- CSR/Evidence parse, signature, chain/status와 policy verdict
- CA/OCSP key ceremony, backup, activation, signing, rollover와 destruction
- CA/Leaf issuance, post-check, repository publication과 retrieval
- revocation request, authentication, decision, status publication과 verification
- provider/profile/reference lifecycle, emergency block과 rollback detection
- privileged access, access denial, break-glass와 configuration change
- backup/restore, DR reconciliation, incident action과 report

이 event 이름과 envelope field는 C2PA가 정한 wire schema가 아니라 필수 audit facts를 누락 없이 연결하기 위한 `ARCH-DECISION`이다.

### 8.2 Log protection과 review

- Audit log를 비인가 접근·변경·삭제로부터 보호하고 regular review를 수행한다.
- Append-only/WORM 또는 cryptographic chaining은 가능한 구현이며 특정 제품 자체가 C2PA 의무는 아니다. 선택한 방식은 tampering·truncation·reordering을 탐지해야 한다.
- source service는 event를 durable sink에 전달하기 전 security-sensitive operation 성공을 확정하지 않는다. 비동기 buffer를 쓰면 integrity, bounded capacity와 replay recovery를 증명한다(`ARCH-DECISION`).
- auditor access는 read-only이고 export는 승인·목적·scope·만료를 갖는다.
- log time source, sequence/checkpoint, signing key와 verification procedure를 문서화한다.
- 정기 review 주기, alert triage SLA와 audit finding remediation은 CPS/운영정책에 고정한다.

### 8.3 Compliance audit와 보안 평가

- CA는 독립적이고 자격을 갖춘 제3자에 의한 정기 compliance audit를 수행하는 것이 `C2PA-SHOULD`다. 주기는 risk profile과 Assurance Level에 따라 정하며, CP의 “최소 연례 audit”은 lowercase recommendation이므로 대문자 의무로 오표기하지 않는다. 이 project의 실제 주기는 CPS에서 승인한다.
- Audit scope에는 issuance/re-key/revocation, attestation validation, Subscriber·CA key management, 논리·절차 통제, 인력·교육, incident response와 DR을 포함한다.
- Audit report의 C2PA Steering Committee/승인 당사자 제공, non-conformity 명시, 영어 또는 전문 영어 번역과 corrective action은 `C2PA-SHOULD`다. Finding severity, owner, due date, exception과 closure evidence SLA는 CPS에 고정한다.
- CA infrastructure, system과 attestation validation에 대한 정기 vulnerability assessment·penetration test, 자격 있는 assessor 사용, 관련 Generator Product platform과 attestation service review 및 remediation plan은 `C2PA-SHOULD`다.
- Security Incident 발생 시 root cause·impact·lesson을 검토하고 재발방지 action을 만들며 report를 C2PA Steering Committee와 Conformance Task Force에 공유하는 것은 `C2PA-REQUIRED`다.

### 8.4 데이터 분류와 최소 수집

| 데이터 | 기본 저장 | Raw 저장 조건 |
|---|---|---|
| Issued certificate fields/DER | CP 최소 record인 serial, Subject, validity, X.509v3 extension/value와 revocation status; project는 immutable DER+digest도 저장 | full DER/digest 보존은 `ARCH-DECISION`이며 privacy/CPS inventory에 명시 |
| CSR | digest, exact DER SPKI digest, parsed fields | appeal/audit 필요와 retention 승인 시 |
| Attestation Evidence/chain | digest, signer/root IDs, normalized claims/verdict | provider 검증·법적 필요가 privacy review에서 승인된 별도 vault |
| Claim freshness context / TSA challenge | Claim은 provider policy가 요구하는 평가 기간 동안 보호 후 replay marker만 보존; TSA는 active transaction 동안 bytes 보호 후 digest·상태 보존 | Claim provider/CPS decision 또는 TSA reconciliation 최소기간 |
| Device identifier | 기본 미수집 또는 scoped pseudonym/HMAC | 명시 목적·법적 근거·접근/삭제 정책 필요 |
| Measurement/Reference | approved value ID/version/digest | 민감 원문은 restricted registry |
| Public-key reuse identity | 승인된 profile의 identifier만; 현재 미승인으로 issuance disabled | 원 공개키/Subscriber 연결 분리와 보존은 별도 approval 필요 |

Password, bearer token, private key, HSM activation data, unprotected key handle, 불필요한 IMEI/serial, raw Evidence와 Subject 전체를 일반 log·error·metric label에 넣지 않는다. Claim certificate Subject 자체도 개별 device instance를 유일 식별해서는 안 된다.

비공개 Subscriber business information은 Subscriber의 explicit **written** consent, 법률·규정의 요구 또는 independent audit 필요 외 제3자에게 공개하지 않는다. 개인정보는 identity validation과 certificate issuance 등 명시 목적에 한정하며 적용법과 보존 의무 안에서 access·rectification·erasure를 지원한다.

### 8.5 Retention과 deletion

| Record | 최소/결정 |
|---|---|
| Issued certificate repository record | certificate 만료 후 최소 1년 `C2PA-REQUIRED` |
| Claim OCSP status | 위 record-keeping 기간까지 `C2PA-REQUIRED` |
| Detailed audit log | 종류·기간·secure storage/retrieval을 archival policy에서 결정 |
| Raw CSR/Evidence/challenge | C2PA 고정기간 없음; CPS/privacy decision |
| CA private key | operational backup만; archive 금지 |
| Key-reuse tombstone | project 기본은 CA 운영기간; privacy/CPS에 목적 명시 |
| Incident legal hold | 승인된 case 범위·기간; 종료 후 normal deletion 재개 |
| TSA event log | 공개 TSA practices가 정한 기간; intended accuracy·time incident 입증에 충분해야 함 |

Deletion은 primary, replica, backup과 search index를 포함하고 deletion proof 또는 exception을 남긴다. 보존기간을 늘릴 때도 “감사에 유용”하다는 이유만으로 raw device-linked Evidence를 무기한 보관하지 않는다.

## 9. Monitoring과 운영 수준 (`ARCH-DECISION` production SLI)

### 9.1 필수 SLI와 경보

| 영역 | SLI·경보 |
|---|---|
| Enrollment | Claim request/decision latency·queue age·duplicate key reservation; TSA transaction/result와 idempotency conflict |
| Verifier | provider별 PASS/FAIL/NOT_PROVEN, unknown root/profile, parser error, SPKI/challenge mismatch |
| Trust/Reference | last successful refresh, `freshUntil`, sequence rollback, expiry horizon, emergency epoch |
| CA/HSM | key state, signing rate/failure, unauthorized mechanism, quorum/break-glass, backup inventory |
| Certificate inventory | issuer별 serial uniqueness, validity horizon, rollover backlog, orphan/unknown issuer |
| OCSP | external availability/latency, status correctness, `thisUpdate`/`nextUpdate`, signer expiry |
| CRL | generation/publish, CRL Number monotonicity, `nextUpdate`, mirror consistency |
| Repository | public status reachability, internal record integrity와 expiry+1y coverage |
| Security | failed MFA, privileged change, replay/malformed burst, cross-scope access |
| Audit/Privacy | ingest lag, checkpoint gap, unauthorized export, raw sensitive data detection |
| DR | backup age, restore-test age, replication lag와 reconciliation mismatch |
| TSA external acceptance | 승인된 운영 evidence 및, 수집하는 경우 authenticated observation의 freshness; time/status age, drift, leap-bulletin readiness와 active-key count. 서버 추정값으로 정상 판정 금지 |

성공률의 급증도 감시한다. Reference Value가 과도하게 넓어졌거나 verifier 단계가 빠진 신호일 수 있으므로 profile/reference 배포와 verdict 변화를 상관 분석한다.

Metric label은 provider/profile/version, stable reason code와 coarse product/service scope까지만 사용한다. certificate serial, CSR, Subject, hardware ID와 device pseudonym을 high-cardinality label로 사용하지 않는다.

### 9.2 CPS/SLO가 수치화할 항목

C2PA가 수치를 고정하지 않은 다음 구현 SLO 값을 production 전에 정한다. Percentage·latency·freshness SLO는 “모든 unexpired certificate의 current valid/revoked status를 24×7 public Repository로 제공”한다는 CA warranty를 완화할 수 없다.

- issuance/verifier/HSM latency·availability와 queue/capacity
- OCSP availability, `thisUpdate` max age, `nextUpdate`와 cache TTL
- CRL publication interval, overlap, maximum stale와 emergency publish 목표
- Trust List/CPL/provider/reference refresh와 maximum age
- incident severity, escalation, notification, containment과 mass-revocation 목표
- log/access review, backup/restore, DR와 compromise drill 주기
- service별 RTO/RPO
- audit/raw Evidence/challenge/provider snapshot retention

SLO 미달은 trust predicate를 완화하는 이유가 아니다. Issuance를 중단하더라도 status와 revocation path를 우선 유지한다.

## 10. Production readiness와 완료 기준

### 10.1 Provider·PKI activation gate

| Gate | 승인 증거 |
|---|---|
| Governance | role/IAM matrix, Root accountable oversight, quorum, 공개 CPS/business practices, training/access review, Claim certificate-warranty crosswalk, Claim Agreement/Terms template·필수 stipulation legal approval과 active relationship inventory |
| Physical/Software Security | restricted-area physical MFA, equipment protection, CA operation `m-of-n`, secure-coding/code-signing/update evidence, authentication-mechanism/password-policy inventory, 모든 network-service attribute와 deployed configuration reconciliation |
| Source snapshot | pinned commit와 source-path inventory, Git blob object ID+SHA-256 manifest, certificate-profile 및 Trust List `$ref` closure의 exact-byte validator bundle, relevant worktree clean check |
| CA key generation | 일반 ceremony script/sign-off/deviation; 실제 generation module의 FIPS 140-2 L2+, FIPS 140-3 L2+ 또는 적절한 CC PP/ST EAL4+ certificate/version·evaluated configuration과 generation operation scope mapping; Trust List 대상은 independent-witness signed script 또는 C2PA가 수용한 qualifying WebTrust waiver |
| CA key storage/use | Root·Issuing CA key를 저장·사용하는 FIPS 140-2 L2+ secure cryptographic device의 certificate/version·검증 상태, 실제 key object와 operation scope mapping, 3-tier data center 또는 commercial-cloud HSM 배치; key class별 backup policy·module-protection mapping·inventory/denial evidence. CC-only/FIPS 140-3-only 증거로 이 gate를 대체하지 않음 |
| CA profile | CSR PoP/schema, certificate DER/schema/cross-object report, canonical Subject ownership/lineage, fixed Git-blob schema digest |
| Chain | Claim/TSA independent path, correct Trust List active status, AIA retrieval |
| Status | certificate class별 issuer/source topology, OCSP/CRL known-answer, freshness/cache, revocation E2E, 24×7 public multi-vantage check |
| Provider | immutable profile, root/status/rotation owner, Claim CPL method mapping |
| Reference | authenticated bundle, component coverage, expiry/rollback/emergency test |
| Verifier | fixed artifact digest, positive/negative vectors, parser fuzz/resource limit |
| Failure | stale/unknown/timeout/rollback/HSM partial failure에서 no issuance |
| Concurrency | Claim freshness/replay marker·lineage/key reservation; TSA challenge/idempotency; serial과 emergency mid-flight test |
| Incident/DR/Termination | dependency query, mass-revoke capacity, isolated restore/reconciliation, CA 종료·RA delegation 폐지 tabletop |
| Audit/Privacy | event completeness/integrity, retention/deletion, sensitive-data scan |
| Compliance Assessment | independent audit risk/frequency decision, assessment scope, vulnerability/penetration test와 finding remediation evidence |
| TSA 추가 | 공개 TSA practices, TEE/key/purpose/single-active 설계·시험·운영 evidence, 24h sync-attempt·drift-stop·leap handling drill. Optional attestation/activation을 채택하면 해당 contract E2E도 추가 |

### 10.2 최소 운영 시험

- 단일 principal로 Root/ICA key activation, CA certificate issuance, backup restore를 완료할 수 없어야 한다.
- Password path에는 strong-password/MFA/access-review 통제를 적용하고, passwordless `N/A`는 password/fallback login negative test로 증명한다. Network discovery와 inventory를 양방향 대조해 undocumented service·port·route를 거부한다.
- Pinned Git blob과 다른 worktree/CRLF-converted schema는 release artifact와 근거 자료로 수용하지 않는다. Validator가 실제 로드한 certificate-profile 또는 Trust List `$ref` closure bytes의 SHA-256이 manifest와 다르거나 CP/Program/profile/trust-schema source에 uncommitted content가 있으면 source audit와 release evidence 생성을 실패시킨다.
- Root/Intermediate/Claim ICA/TSA ICA/OCSP certificate의 official schema와 4.5 self-check를 실행한다.
- Root AKI 누락, wrong parent AKI, pathLen, wrong EKU와 cross-domain issuer를 거부한다.
- 서로 다른 logical CA/responder가 같은 canonical Subject DN을 요청하면 거부하고, 동일 identity의 승인된 old/new rollover lineage와 overlap만 허용한다(`ARCH-DECISION`).
- TSA ICA를 First Intermediate가 발급하는 topology를 clarification 전 거부한다.
- HSM에서 Claim ICA key로 TSA Leaf/arbitrary payload를, TSA ICA key로 Claim Leaf를 서명하지 못해야 한다.
- 모든 revocation trigger와 72시간 대상 요청을 E2E로 status service에 반영한다.
- First Intermediate, Claim ICA, TSA ICA, Claim Leaf와 TSA Leaf 각각의 issuer-specific OCSP/CRL source를 검증하고 한 responder credential의 cross-issuer 사용을 거부한다.
- OCSP stale/unknown/unauthorized responder와 CRL rollback/wrong scope를 거부한다.
- OCSP responder rollover에서 same-issuer-key direct delegation은 허용하고, 다른 issuer/rollover key와 locally trusted responder는 명시적 CPS·상호운용 승인 없이는 거부한다. `CertID` issuer name/key hash와 serial mismatch도 거부한다.
- Trust List/provider/reference rollback·expiry·source failure에서 신규 발급이 없어야 한다. Trust List schema 자체가 PASS하더라도 current/history의 `ServiceStatus` 또는 `StatusStartingTime` 누락, unknown/wrong-scheme status URI, malformed date-time와 역행 history를 독립 semantic gate에서 거부한다.
- Provider emergency block이 cached PASS와 in-flight issuance를 final gate에서 차단해야 한다.
- 비계열 Claim Subscriber Agreement의 부재·무효·만료, 계열 Terms acknowledgement 부재, representative 계약 권한 부재, scope/version mismatch와 request 평가 중 철회·대체를 Claim final signing에서 거부한다. Post-issuance implicit acceptance만으로 이 gate를 통과하지 않는다.
- 최종 TBS certificate의 Subject/조건부 SAN 또는 다른 warranty field가 승인 evidence와 다르면 HSM을 호출하지 않는다.
- O.3/O.4 90일 vulnerability·patch/revision, Android 4개월 `osPatchLevel`, 90일 vendor/boot patch와 future-date 거부 boundary vector를 실행한다.
- Android chain에서 root-nearest attestation extension과 selected-certificate SPKI binding을 검증하고, 정상 not-listed와 status fetch/인증 실패, factory legacy validity 예외와 RKP validity를 구분한다.
- 마지막 online synchronization 시도가 정확히 24시간인 경계와 `24h+epsilon`을 시험한다. 초과하면 C2PA nonconformance, incident와 신규 activation 차단을 검증하고, 기존 TSU도 중단하는 offline cutoff를 채택하면 별도 `ARCH-DECISION` vector로 시험한다.
- Time이 declared accuracy 밖으로 drift하면 외부 TSU가 즉시 TST issuance를 중단하고 signed stop observation 전에는 정상 복구되지 않음을 검증한다(`C2PA-REQUIRED`).
- 유효·stale·replayed·superseded·cancelled·wrong-authority leap bulletin, step/smear source-profile mismatch, event 중 reboot/rollback/holdover exhaustion을 시험한다. Declared accuracy를 벗어나면 즉시 no-new-TST이며, leap 처리 중에도 serial uniqueness와 single-active key를 유지한다.
- Activation contract의 wrong service/TSU/key/certificate/environment, unknown signer/version, expiry/future/replay, counter rollback, out-of-order transition, concurrent two-key activation, response loss/retry와 forged receipt를 fail-closed하고 03의 device result와 reconciliation한다.
- TSA key compromise 시 certificate를 revoke하고, 해당 key의 revocation 전·후 `genTime` TST를 모두 거부하며 replacement key가 old-key token 신뢰를 복구하지 않음을 03 handoff/acknowledgement까지 E2E 검증한다.
- TSA non-compromise cessation에서 CRL reasonCode `0/3/4/5` 각각은 `genTime < revocationTime` TST만 유지하고, 정확히 revocationTime 또는 그 이후 TST를 거부한다. ReasonCode absent, `keyCompromise(1)` 또는 다른 값은 cutoff를 허용하지 않고 해당 key의 모든 TST를 거부하며 03 handoff/acknowledgement까지 검증한다.
- Root/Issuing CA 외 key class의 backup `PERMITTED`이면 원 module과 동등한 protection/restore를, `FORBIDDEN`이면 backup/export operation 거부를 검증한다. Subscriber Claim key가 CA backup inventory에 들어오면 실패한다.
- Root/AK/SAK/measurement/CPL dependency로 영향 certificate를 조회하고 dry-run mass revoke할 수 있어야 한다.
- Backup restore 뒤 HSM/serial/reservation/repository/status/audit가 일치하고 duplicate certificate를 만들지 않아야 한다.
- Audit log 수정·삭제·truncation을 탐지하고 raw Evidence/device identifier가 일반 log와 metric에 없어야 한다.
- Issuance 장애 중에도 status service continuity 목표를 검증한다.
- CA 종료와 RA delegation 폐지 tabletop에서 advance Subscriber notice 예외, credential 차단, key/data/equipment 처리, Trust List와 status/repository continuity를 검증한다.

### 10.3 Production 전 결정 register

| ID | 결정할 내용 | Owner | 미결정 시 |
|---|---|---|---|
| `OPEN-PKI-01` | Claim/TSA가 offline Root를 공유할지 별도 Root를 사용할지 | PKI/CPS Owner | ceremony/topology 승인 불가 |
| `OPEN-PKI-02` | Root/First Intermediate 실제 validity·rotation·overlap | PKI/CPS Owner | CA certificate 발급 금지 |
| `OPEN-PKI-03` | CP의 FIPS 140-2 L2+ storage/use 최소선을 충족하는 실제 module/version·3-tier/cloud 배치와 그 위의 partition, `m-of-n`, backup·destruction 구현값 | Security/HSM Owner | key ceremony 금지 |
| `OPEN-PKI-04` | DN encoding/canonicalization, logical Subject uniqueness registry와 rollover lineage, serial generation/reservation, AIA/CDP URI | PKI Owner | template 활성화 금지 |
| `OPEN-STS-01` | First Intermediate·Claim ICA·TSA ICA·Claim Leaf·TSA Leaf별 OCSP/CRL 선택, issuer-specific signer/source, freshness, cache, responder lifetime과 SLO | Status/CPS Owner | production issuer 활성화 금지 |
| `OPEN-TL-01` | Trust List 인증·refresh·rollback·removal 절차 | Trust Operations | issuer activation 금지 |
| `OPEN-AT-01` | 실제 provider Root/AK/SAK, schema/OID, status와 Claim CPL mapping | Provider Owner | provider 최대 `SHADOW` |
| `OPEN-RV-01` | Reference Value producer, bundle schema, freshness/emergency feed와 project의 24시간 `ACTIVE/NEXT` overlap risk basis | Product Security | provider 최대 `SHADOW` |
| `OPEN-IR-01` | severity, notification, RTO/RPO와 mass-revoke capacity | Incident/DR Owner | release 금지 |
| `OPEN-PRV-01` | raw Evidence/challenge/audit/tombstone retention과 deletion | Privacy/CPS Owner | raw 저장 금지·release 조건부 |
| `OPEN-LEG-01` | Claim Agreement/Terms template·required stipulation, affiliation decision, legal validity/effective interval과 `WARRANTY_READY` evidence contract | Legal/CPS Owner | Claim Signing certificate 발급 금지 |
| `OPEN-ACT-01` | Activation artifact schema/version, control/device signer trust, audience, tuple/key/certificate binding, counter/freshness와 recovery acknowledgement | Activation/Runtime Owner | TSA staged activation 금지 |
| `OPEN-TIME-01` | leap-bulletin authority/authentication, step·smear·holdover mode, drill/recovery와 24h miss offline cutoff | TSA/Provider Owner | TSA activation 금지 |

다음 upstream 불일치는 별도 clarification register에서 추적하며 서면 확인과 profile/test 갱신 전 4.2절의 stricter intersection 또는 각 행의 보수적 production 결정을 벗어나지 않는다.

| ID | Clarification |
|---|---|
| `OPEN-C2PA-TSA-PARENT` | TSA ICA의 direct Root issuer 설명과 AKI의 root/intermediate 표현 불일치 |
| `OPEN-C2PA-CLAIM-ED25519` | Claim Leaf의 Ed25519 certificate signature 허용과 Claim ICA의 RSA/EC issuer 제한 불일치 |
| `OPEN-C2PA-CLAIM-AL-MODALITY` | CP 467행의 max AL 이하 모든 level `SHALL issue`와 CP 527행의 Evidence 검증 후 `MAY issue` 간 규범어 긴장; clarification 전 승인된 유효 요청은 해당 AL gate 전체 성공 후 발급으로 진행 |
| `OPEN-C2PA-ANDROID` | CP 표의 Leaf extension·boot Tag 718과 Android current first-occurrence·Tag 719 불일치 |
| `OPEN-C2PA-HSM` | key generation은 FIPS 140-3/CC를 허용하지만 CA key storage/use는 FIPS 140-2 L2+만 명시한 불일치 |
| `OPEN-C2PA-TL-SCHEMA` | pinned C2PA extension schema의 current status constraint가 `ServiceInformation`을 한 단계 더 중첩하고, ETSI base의 current `ServiceInformation.required`가 `ServiceStatus`/`StatusStartingTime`을 포함하지 않아 schema PASS만으로 C2PA status 의미를 보장하지 못함 |

### 10.4 문서 완료 기준

- `SO-*` control이 외부 원문 locator, 구현 enforcement point, test와 audit evidence에 연결된다.
- 모든 CA/OCSP profile과 Trust List schema `$ref` closure의 pinned commit/path/Git blob object ID와 exact-byte SHA-256이 release manifest에 고정되고 validator-loaded bytes와 일치한다.
- Claim/TSA chain이 올바른 trust domain에서 독립 검증되고 wrong-purpose HSM operation이 차단된다.
- status, provider/reference emergency block, incident/DR와 privacy runbook이 승인·시험된다.
- 10.3의 blocker가 CPS, signed provider artifact 또는 승인된 운영 문서에서 해결된다.
- 05의 release gate가 unresolved `OPEN-*`, stale dependency 또는 미완료 drill을 production blocker로 판정한다.

## 11. 근거 자료와 적용 snapshot

### 11.1 C2PA 원문

- [C2PA Certificate Policy v0.2](<../conformance-public/docs/v0.2/C2PA Certificate Policy.md>): Publication/Repository, Certificate Lifecycle, Facility/Operational/Technical Controls, TSA, CA/OCSP profiles, Audit/Privacy와 Dynamic Evidence
- [C2PA Conformance Program v0.2](<../conformance-public/docs/v0.2/C2PA Conformance Program.md>): CA/TSA Trust List 신청, certificate-profile·key-ceremony evidence, machine-readable list 운영
- [C2PA Generator Product Security Requirements v0.2](<../conformance-public/docs/v0.2/C2PA Generator Product Security Requirements.md>): Claim AL2 O.1~O.4의 제품 Reference Value 범위 확인용. CA hosting 직접 요구로 사용하지 않음
- [CPL schema](../conformance-public/schemas/conforming-products/conforming-products-list.schema.json): Claim `attestationMethods`의 현재 허용 enum
- [C2PA Trust List extension schema](../conformance-public/schemas/trust-list/c2pa-trust-list-extensions.schema.json): Trust List JSON gate. Release bundle은 11.3절의 ETSI base와 JWK `$ref` dependency까지 함께 고정

11절의 local link는 열람 편의용이며 snapshot 증거 자체가 아니다. 근거 수집·schema bundle 생성·digest 계산은 pinned commit의 Git object에서 수행한다. 관련 worktree가 commit과 다르면 그 checkout에서 얻은 line locator, hash와 validation result는 release evidence로 사용할 수 없다.

고정 commit에서 이 문서의 주요 control은 다음 원문 locator로 재검증한다. 줄 번호는 source 변경을 탐지하기 위한 snapshot locator이며, 규범 의미는 해당 heading의 전체 문맥과 대문자 `SHALL`/`MUST`/`SHOULD`를 함께 읽어 판정한다.

| 이 문서의 영역 | Primary source locator | 확인할 원문 범위 |
|---|---|---|
| Repository·identity·revocation·status | Certificate Policy 363–615 | issued-record 보존, 요청자 인증, lifecycle, revocation trigger, OCSP/CRL 선택 |
| 역할·변경·감사·복구·종료 | Certificate Policy 621–771 | separation of duties, change control, logging/archive, changeover, incident/backup, CA/RA termination |
| CA/Subscriber key와 network | Certificate Policy 773–905 | ceremony, HSM/module, backup/archive, activation data, host/network controls |
| TSA 운영 경계 | Certificate Policy 905–939 | General, Backend와 On-Device TSA의 key/time/runtime 요구 |
| CA·Leaf·OCSP profile | Certificate Policy 941–1394 및 11.2의 JSON schema | Root/ICA/Leaf extension·validity·path와 status profile |
| Audit assessment·privacy·warranty | Certificate Policy 1396–1564 | audit scope, incident report, confidentiality/privacy, 공개 status warranty |
| Dynamic Evidence·Claim AL2 | Certificate Policy 1684–1856 | O.1~O.4, challenge와 provider-specific guidance |
| Trust List 신청·운영 | Conformance Program 368–382, 408–422, 458–514 및 11.3 schema closure | CA agreement·profile/ceremony evidence, intake/list posting, shared Root 기재, schema validation, access control과 removal |

### 11.2 공식 CA·OCSP profile

- Root: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/rootCA.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/rootCA.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/rootCA.cert.yaml)
- First Intermediate: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/intermediateCA.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/intermediateCA.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/intermediateCa.cert.yaml)
- Claim Signing Issuing CA: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.yaml)
- TSA Issuing CA: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml)
- OCSP Responder: [CSR schema](../conformance-public/docs/v0.2/cert-profiles/ocspResponderLeaf.csr.schema.json), [certificate schema](../conformance-public/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.schema.json), [summary](../conformance-public/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.yaml)

`*.yaml`은 사람이 읽는 profile summary이고 JSON schema는 이 project가 release manifest에 고정하는 executable decoded-output gate다. 둘 다 CP 원문과 함께 검증하며, JSON이 CP/YAML보다 규범적으로 우선한다고 간주하지 않는다. 서로 충돌하면 4.2절처럼 더 엄격한 교집합을 적용하고 clarification을 추적한다. Schema PASS는 암호학적 signature/path/cross-object 검증을 대신하지 않는다.

아래 SHA-256은 `722b639fd140871eb8b8ff0322f2f6e0538dd50a`의 각 Git blob exact byte stream에 대해 계산한다. Validator release bundle도 같은 blob bytes로 구성하며 checkout 시 생성된 CRLF 파일이나 별도 newline-normalized 파일의 raw-byte hash를 사용하지 않는다.

| Profile | CSR Git-blob SHA-256 | Certificate Git-blob SHA-256 |
|---|---|---|
| Root CA | `b9957bd7c403ee1210fd614c2faddf262906e39b82bc6bfdd96a4ef60693352a` | `e900db38176319baa7900a34ad59e616d03aeba16455fd765c6f48e8d0011ce2` |
| First Intermediate CA | `26836ba390da8b39d9634e4117c1567193066b958cc5436516c6cd8bf230f645` | `036798fdedd1f44659532a7bcd556805519cab7cf23e6ea4e8d2a07c880bc8d8` |
| Claim Signing Issuing CA | `bd3f90b1f8688acd0929ca60b3719bdc503da91dbf8d0df8e9da3cd818a0a236` | `9b1e0953a5c5657d99fdf68e8d5418cea26e4b344699d30937aec5c726f18751` |
| TSA Issuing CA | `f68b60822c60c0827ddff25ba5c86944ef7441cdd40e1ad732917b623cabf35b` | `fe548cf85626e97dc5238f2942c1676f78b296b0147ed0f5ebb4d3b3c5493057` |
| OCSP Responder | `0f433fe402470b92eff00c94ca46255bb622eebd1c2f474c6ac29f99908f4e4e` | `8d267b5d8b553de619d07c84aff9480559698a330493a63a2769f4c74b9b9d23` |

### 11.3 Trust List schema dependency closure

아래 세 Git blob을 하나의 offline schema bundle로 고정한다. Validator는 extension schema의 relative `$ref`를 이 bundle 안에서만 해석하며 미고정 network/checkout fallback을 허용하지 않는다.

| Path | Git-blob SHA-256 |
|---|---|
| `schemas/trust-list/c2pa-trust-list-extensions.schema.json` | `ced08a72b46ae7428608615a6646aeb3f216d5fcc1f6b338401b75d74603280b` |
| `schemas/trust-list/ETSI-TS-119-602-schemas/v1.1.1/1960201_json_schema/1960201_json_schema.json` | `f16d60477359b936cefe0c74d5f1c598e3346daf84a6bad1846c712381ca36b4` |
| `schemas/trust-list/ETSI-TS-119-602-schemas/v1.1.1/1960201_json_schema/rfcs/rfc7517.json` | `02799ec31e4383eb39c93b86070e48022e665ac5996c14500a3da913a08c522c` |

이 snapshot의 extension schema는 current status 제약을 `ServiceInformation.ServiceInformation` 아래에 두지만 ETSI base의 실제 current object는 `TrustedEntityServices[*].ServiceInformation`이다. 또한 base schema는 current object에서 `ServiceName`과 `ServiceDigitalIdentity`만 required로 둔다. 따라서 schema PASS를 `ServiceStatus`/`StatusStartingTime` 준수 증거로 사용하지 않고 4.6절의 독립 semantic gate와 negative vector를 release blocker로 적용한다. Upstream이 수정되면 새 Git blob을 고정하고 이 보완 gate를 regression oracle로 유지한다.

### 11.4 RFC와 provider 원문

- [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161.html): TSP/TST profile과 TSA key cessation·compromise 시 token trust semantics(특히 §4)
- [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html): X.509 certificate/CRL profile, Basic Constraints, path validation과 CRL validation
- [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960.html): OCSP response, authorized responder, freshness와 acceptance
- [RFC 10007](https://www.rfc-editor.org/rfc/rfc10007.html): RFC 5280 CRL validation의 `cRLSign` 확인 update
- [RFC 9334](https://www.rfc-editor.org/rfc/rfc9334.html): Attester, Verifier, Endorser/Reference Value Provider 역할 구분. Provider onboarding protocol 자체를 정의하지는 않음
- [Android Key Attestation verification](https://developer.android.com/privacy-and-security/security-key-attestation): current root set, migration/overlap facts, chain/status, extension selection과 factory/RKP validity (2026-08-31 확인)
- [AOSP Key Attestation schema](https://source.android.com/docs/security/features/keystore/attestation): AuthorizationList tag와 version별 ASN.1 schema (2026-08-31 확인)

### 11.5 프로젝트 조사 자료의 사용 제한

- [AL2 Evidence Enrollment 조사](appendix/c2pa-attestation-evidence-enrollment-spec.md)와 [SAK Evidence 설계](appendix/c2pa-sak-attestation-evidence-design.md)는 provider registry와 custom Evidence 설계 입력이다. C2PA가 정한 wire format으로 인용하지 않는다.
- [On-Device TSA review draft](appendix/on-device-tsa-attestation-review-draft.md)는 `Superseded` historical review이므로 production profile 근거로 사용하지 않는다.
- Provider별 실제 root, OID, schema, status, Reference Value와 test vector는 승인된 provider 원문·signed deployment artifact가 이 문서보다 우선한다.

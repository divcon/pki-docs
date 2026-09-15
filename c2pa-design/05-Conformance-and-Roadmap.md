# 05 — Conformance and Roadmap

> 상태: Outline draft. 요구사항·시험·적합성·구현 순서와 production release 판정을 구체화하기 위한 목차 초안이다.

> **2026-09-02 TSA enrollment 정정:** Base TSA Leaf enrollment은 per-request Compound Evidence를 요구하지 않는다. TEE/key/purpose/single-active는 runtime/implementation/operations acceptance로 검증하고, Custom Attestation 및 staged activation 시험은 그 optional project/CPS mechanism을 채택한 범위에만 적용한다.

## 1. 문서 목적과 검증 범위

포함할 내용:

- Certificate Platform 구현 검증과 외부 runtime acceptance 검증의 분리
- Claim Signing enrollment, TSA enrollment, RFC 3161/C2PA 상호운용의 검증 범위
- Generator Product Conformance와 CA/TSA 운영·Trust List 준비의 분리
- production, pilot와 development 환경별 목표

## 2. Requirement Traceability

포함할 내용:

- requirement ID, 외부 원문 source/version/locator, 요구 수준과 owner
- design section, implementation, test, evidence와 상태의 연결
- C2PA/RFC 요구와 CA CPS·프로젝트 강화 정책의 구분
- CP 1522~1564의 Claim product-name control, Subject/Applicant Representative authorization, Claim certificate-information accuracy, Subscriber Agreement/Terms of Use, 24×7 status, revocation과 Root warranty를 02/04 enforcement point 및 발급별 evidence에 연결. Claim agreement gate를 TSA에 자동 확장하지 않음
- activation server transaction·signed artifact contract는 04, device-side acceptance는 03, end-to-end test/release evidence는 05로 owner를 고정
- not-applicable rationale, waiver와 미결정 source 처리
- C2PA/RFC 필수, 01 공통 불변조건, 04 mandatory fail-closed predicate와 provider/runtime production gate는 non-waivable이며 미충족 시 blocker로 남는다는 원칙
- architecture 문서를 사실 근거가 아닌 design locator로만 사용하는 원칙
- 상세 RTM baseline은 Phase 2 구현 착수 전에 승인할 하위 산출물로 작성

## 3. Verification Strategy

포함할 내용:

- Claim AL1/AL2 Leaf 발급 positive/negative/boundary/concurrency 시험
- Base TSA Leaf enrollment 시험과 runtime TEE/key/purpose/single-active acceptance 시험의 분리. Optional Custom Attestation·staged activation을 채택하면 signer/audience/key/certificate/freshness/counter/replay·rollback 시험 추가
- CSR/certificate profile regression과 CA/HSM failure 시험
- RFC 3161 및 C2PA 2.4 known-answer/interoperability 시험
- TSA key compromise 시 해당 certificate revocation과 해당 key의 과거·현재 TimeStampToken 전체 불신, incident 통지·acknowledgement 시험
- TSA non-compromise cessation에서 CRL reasonCode `unspecified(0)`/`affiliationChanged(3)`/`superseded(4)`/`cessationOfOperation(5)`와 revocationTime 경계를 시험하고, reasonCode absent/그 밖의 값이면 해당 key의 모든 TimeStampToken을 거부하는 RFC 3161 §4 negative 시험
- 24시간 online sync-attempt miss, declared-accuracy drift-stop, 공인 leap-second step/smear를 서로 분리한 trusted-time 시험
- Claim Subscriber Agreement/affiliated Terms of Use가 없거나 stale/wrong-version이고 Subject·대표자 권한 또는 certificate 정보가 부정확한 Claim 발급의 negative 시험
- Trust List schema PASS와 별개로 current/history service status의 필드 존재, exact C2PA status URI, RFC 3339 시각과 history 순서를 검증하고 missing/unknown URI/malformed time/rollback을 거부하는 negative 시험
- parser fuzzing, replay, tenant isolation, rollback, fault injection과 privacy 검증
- Evidence-required profile에서 provider `DISABLED`, stale/expired/rollback trust bundle 또는 hardware evidence 누락 시 그 profile의 요청 거부·CA/HSM 미호출 검증. Activation 계약 누락은 해당 runtime activation을, non-production artifact 유입은 production 사용을 차단
- 시험별 expected result, 발급 여부, audit와 cleanup 원칙

## 4. 적합성 Workstream

포함할 내용:

- Certificate Platform의 CP/CPS 준수와 PKI 운영 증거
- 외부 Generator Product의 Specification/GPSA/CPL 책임
- On-Device TSA operator의 TSA Practices와 runtime acceptance 증거
- Claim Signing Trust List와 TSA Trust List의 독립 준비
- certificate/token sample, interoperability와 audit 자료

## 5. Test Evidence와 재현성

포함할 내용:

- source/profile/build/harness/provider/reference-value version
- source Git commit/path/blob object ID/SHA-256, actual validator-loaded byte digest와 dirty-worktree rejection result
- fixture와 실행환경 digest, expected/actual result
- certificate/token/log/report artifact와 승인자
- warranty decision, Agreement/Terms version·digest·scope·effective interval, legal approval과 final-gate recheck 결과. Raw contract와 개인정보는 restricted legal repository 밖으로 복제하지 않음
- deviation·waiver·known issue 추적
- private key와 불필요한 개인정보를 evidence bundle에 포함하지 않는 원칙

## 6. 구현 Roadmap

### Phase 1 — 정책과 구조 확정

- CA topology, profile, identifier, provider, trusted-time·validity 정책 확정
- RTM baseline, OpenAPI/error contract, profile-conditional Evidence/provider schema, certificate-profile version pin과 DB/lifecycle invariant 승인

### Phase 2 — Enrollment 기반

- transaction, CSR verifier, policy engine과 certificate template 구현; Claim AL2/optional TSA profile에만 challenge/Evidence verifier 추가

### Phase 3 — Lifecycle과 운영

- re-enrollment, 04 contract에 따른 Certificate Platform의 activation resource/wire/orchestration/reconciliation, OCSP/CRL, revocation, audit, incident와 recovery 구현

### Phase 4 — 외부 provider/runtime acceptance

- TEE controls와 설계·시험·운영 evidence, RFC 3161/C2PA 상호운용 및 fault evidence 승인. Optional provider Evidence/activation을 채택하면 device verification·execution·authenticated observation도 추가

### Phase 5 — Production·적합성 준비

- HSM ceremony, CPS/TSA Practices, Trust List, security review와 운영 drill 완료

각 phase에는 owner, dependency, entry/exit criteria, test와 산출물을 연결한다.

## 7. Provider·deployment 결정 관리

포함할 내용:

- Claim AL2/optional TSA profile의 provider trust root, Evidence schema/identifier, Reference Value와 status source
- TSA TA/TEE 구조, TSU identity와 trusted-time 정책; Attestation Service/activation은 채택 여부와 범위
- certificate validity, key rotation, serial persistence와 Evidence retention
- 결정 owner, due date, 승인 상태, 영향 범위와 대안
- Optional Evidence profile에 필요한 증거가 승인되기 전 해당 provider/version을 비활성화하는 원칙. Base TSA profile까지 자동 차단하지 않음
- 현재 production `ENABLED` attestation provider는 없으며, 향후 승인된 provider registry/release artifact만 `DISABLED → ENABLED` 전환의 authoritative source가 됨

## 8. Release Gate

포함할 내용:

- architecture/정책/profile/API가 versioned·approved 상태인지
- pinned source Git blob과 release manifest digest가 재현되고 dirty checkout이 release input에서 거부되며, Trust List schema `$ref` closure와 독립 semantic status gate가 모두 통과하는지
- 요구 추적과 필수 시험·보안 review가 완료됐는지
- CA/HSM/status, incident, monitoring, privacy와 DR가 운영 가능한지
- Evidence-required profile이면 대상 provider의 trust/schema/reference/fault evidence가 승인됐는지
- Evidence-required profile의 미승인 provider·trust rollback은 그 profile의 발급을, activation evidence 누락은 해당 runtime activation을, non-production artifact는 production 사용을 fail-closed하는지
- Generator/TSA external acceptance와 Trust List 준비가 충족됐는지
- Claim Subscriber Agreement/Terms of Use와 certificate warranty evidence, Trust List 대상 ceremony evidence가 충족됐는지
- TSA key-compromise handoff, leap-second readiness와 activation contract E2E acknowledgement가 통과했는지
- Certificate Platform gate, provider activation gate와 외부 runtime acceptance gate를 각각 판정하는 방식

## 9. 향후 산출물과 완료 기준

포함할 내용:

- RTM, test plan/catalog, interoperability matrix와 evidence bundle 형식
- Conformance/Trust List checklist, roadmap와 decision backlog
- release checklist 및 blocker/waiver 기록
- 모든 필수 요구가 승인된 evidence로 추적되고 미결정 provider가 production에 진입하지 않는 완료 기준

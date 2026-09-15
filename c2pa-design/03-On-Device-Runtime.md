# 03 — External Runtime Acceptance 상세 설계

> 상태: 상세 설계 초안. 이 문서는 Certificate Platform의 납품물이 아닌 외부 Generator Product와 On-Device TSA가 발급 인증서를 올바르게 사용하는지 판정하는 device-side acceptance contract를 정의한다. 파일명은 기존 링크 호환을 위해 유지한다.

> **2026-09-02 TSA enrollment 정정:** 이 문서의 TEE/key/time/single-active 요구는 runtime/implementation acceptance다. C2PA는 그 상태를 TSA Leaf API마다 Compound Evidence로 제출하라고 요구하지 않는다. Signed observation, Custom Attestation과 staged activation은 채택한 project/CPS mechanism에만 적용한다.

## 1. 문서 목적과 범위

### 1.1 이 문서가 답하는 질문

이 문서는 다음 질문에 답한다.

1. 발급된 Claim Signing Leaf와 TSA Time-Stamp Signing Leaf를 어떤 키·컴포넌트가 사용할 수 있는가?
2. Asset, Assertion, Claim, COSE signature와 RFC 3161 TimeStampToken은 어떤 순서와 정확한 바이트 경계로 만들어지는가?
3. REE, Claim signing boundary, TSA TA/TEE와 외부 time/status source 사이에서 무엇을 신뢰하지 않아야 하는가?
4. On-Device TSA가 offline에서도 발급 가능한 조건과 즉시 중단해야 하는 조건은 무엇인가?
5. certificate validity, 외부 key state와 activation transaction을 어떻게 분리하는가?
6. 어떤 정적·동적·고장 주입 증거가 있어야 특정 provider/runtime version을 production에서 수용할 수 있는가?

이 문서의 통과는 외부 구현이 이 아키텍처의 acceptance contract를 만족한다는 뜻이다. 외부 runtime 코드, TEE OS, Trusted Application, secure storage, trusted-time service 또는 C2PA SDK가 Certificate Platform의 납품 범위에 편입된다는 뜻이 아니다.

### 1.2 명시적 비범위

Certificate Platform은 정상 runtime에서 다음 기능을 제공하지 않는다.

- Asset, Assertion, Claim, C2PA Manifest 또는 Manifest Store 생성
- `K_claim`을 이용한 C2PA Claim signature 생성
- v2 timestamp의 `ToBeSigned` 또는 `MessageImprint` 계산
- `K_tsu`를 이용한 RFC 3161 TimeStampToken 생성
- raw digest, arbitrary payload 또는 application message signing endpoint
- 단말 private key의 escrow, backup, export 또는 remote recovery
- 단말 trusted-time 또는 leap-second 처리 구현
- C2PA Validator 구현

Enrollment과 runtime의 경계는 다음과 같다.

```text
Enrollment
  device public key + CSR [+ profile-conditional Evidence]
      ──> Certificate Platform
      ──> Leaf certificate + chain

Normal runtime
  Asset/Claim ──> external K_claim ──> COSE claim signature
  v2 timestamp input ──> external TSA TA/K_tsu ──> TimeStampToken

  Certificate Platform signing endpoint: 없음
```

### 1.3 Canonical owner

| 주제 | Canonical owner | 이 문서의 책임 |
|---|---|---|
| Claim/TSA Leaf enrollment와 profile-conditional Evidence 판정 | [02 Certificate Enrollment](02-Certificate-Enrollment.md) | 발급 결과의 설치·사용 전 검증 |
| Activation server resource, signed artifact contract와 reconciliation | [04 Security and Operations](04-Security-and-Operations.md) | artifact의 장치 측 검증·실행과 실제 key-state observation |
| Certificate status, incident handoff와 운영 publication | 04 | 외부 runtime의 stop 적용과 acknowledgement |
| E2E 시험, 적합성 evidence와 release gate | [05 Conformance and Roadmap](05-Conformance-and-Roadmap.md) | runtime acceptance predicate와 필요한 시험 oracle 제공 |
| Provider-specific TEE/TA/time 구현 | 외부 provider/runtime owner | versioned profile과 검증 증거를 제출받아 수용 여부 판정 |

서버 state와 외부 장치 state 사이에 원격 원자 transaction이 있다고 주장하지 않는다. 서버는 서명된 device observation을 보유할 수 있지만 TEE 내부 상태의 권위 있는 소유자는 외부 TSA TA다.

## 2. 적용 기준과 요구 수준

### 2.1 Source snapshot

아래 원문을 기준으로 한다. `c2pa-design/` 아래 문서는 설계 일관성을 확인하는 locator일 뿐 표준·사실의 근거가 아니다.

| 원문 | 적용 범위 | 고정 기준 |
|---|---|---|
| [Content Credentials Specification 2.4](../specifications/build/site/specifications/2.4/specs/C2PA_Specification.html) | Claim/Assertion/content binding, COSE signature, `x5chain`, v2 timestamp와 validation | `specifications` commit `d776ab5a8627f8f5ac2f7f4f3aa20ab12783a878` |
| [C2PA Security Considerations 2.4](../specifications/build/site/specifications/2.4/security/Security_Considerations.html) | remote fetch privacy, parser/ingredient resource exhaustion, Generator threat boundary | 같은 commit |
| [C2PA Certificate Policy v0.2](<../conformance-public/docs/v0.2/C2PA Certificate Policy.md>) | Claim key 용도, General/On-Device TSA, TSA Leaf profile | `conformance-public` commit `722b639fd140871eb8b8ff0322f2f6e0538dd50a` |
| [Generator Product Security Requirements v0.2](<../conformance-public/docs/v0.2/C2PA Generator Product Security Requirements.md>) | key 보호, Claim Generator와 Asset/Assertion 경로, IPC·입력 통제 | 같은 commit |
| [RFC 3161](../rfc3161.txt) | TimeStampReq/Resp, TSTInfo, unique serial, nonce와 TSA compromise | RFC 3161 |
| [RFC 5816](../rfc5816.txt) | ESSCertIDv2와 SigningCertificateV2 | RFC 5816 |
| [RFC 8152](https://www.rfc-editor.org/rfc/rfc8152), [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949), [RFC 9360](https://www.rfc-editor.org/rfc/rfc9360) | C2PA 2.4가 참조하는 COSE, deterministic CBOR와 `x5chain` | 공개 RFC |

RFC 8152가 RFC 9052/9053으로 대체되었다는 이유로 C2PA 2.4가 직접 참조한 서명 바이트 계약을 임의로 바꾸지 않는다. 향후 C2PA 적용 version이 기준 RFC를 바꾸면 known-answer vector와 함께 migration한다.

Nested source checkout은 작업 중 EOL 또는 local modification이 존재할 수 있다. 규범 문언과 release evidence는 위 commit의 `git show <commit>:<path>` blob bytes 또는 인증된 upstream artifact로 재현해야 하며 dirty worktree의 내용만으로 확정하지 않는다.

### 2.2 요구 수준

| 표기 | 의미 |
|---|---|
| `C2PA-REQUIRED` | Content Credentials의 normative `shall` 또는 CP/GSPR의 대문자 `SHALL` 요구 |
| `C2PA-OBLIGATION` | CP가 lowercase `shall`로 서술하여 BCP 14 키워드는 아니지만 운영 baseline에서 이행하는 의무 |
| `C2PA-RECOMMENDED` | C2PA `should`/`SHOULD` 권고. 벗어나면 근거와 상호운용 증거 필요 |
| `RFC-REQUIRED` | RFC 3161/5816/8152/8949/9360의 규범 요구 |
| `CPS-REQUIRED` | CA/TSA practices가 C2PA 공통 기준보다 강화하여 강제하는 항목 |
| `ARCH-DECISION` | 이 프로젝트가 정한 runtime acceptance 불변조건 |
| `PROVIDER-BOUND` | 특정 TEE, TA, KeyMint/keystore, time/status source에 맞춰 승인할 값 |
| `OPEN` | owner와 검증 가능한 값이 확정되지 않아 production을 차단하는 항목 |

C2PA Specification은 대소문자와 관계없이 규범 키워드를 BCP 14로 해석하지만, C2PA Certificate Policy v0.2는 모두 대문자로 쓴 경우에만 BCP 14로 해석한다. 따라서 두 문서의 `shall`을 같은 방식으로 기계 분류하지 않는다.

### 2.3 규범과 강화 설계의 경계

| 항목 | 분류 | 경계 |
|---|---|---|
| Claim/Assertion/COSE/`sigTst2` 형식 | `C2PA-REQUIRED` | 프로젝트가 다른 바이트 입력으로 대체할 수 없음 |
| RFC 3161 request/token/nonce/serial 의미 | `RFC-REQUIRED` | C2PA의 추가 hash·저장 요구와 함께 적용 |
| On-Device TSA의 TEE 실행·TEE key 생성/보관·24시간 이내 online sync 시도 | `C2PA-REQUIRED` | provider 편의로 완화할 수 없음 |
| UTC(k) traceability | `C2PA-OBLIGATION` | CP lowercase 문언이나 TSA practices baseline에 포함 |
| Custom Compound Attestation과 staged activation | `OPTIONAL CPS EXTENSION`/`ARCH-DECISION` | C2PA/RFC 3161의 TSA Leaf enrollment wire가 아님 |
| `x5chain` root 제외와 integer label 33만 생성 | `ARCH-DECISION` | C2PA `SHOULD NOT`/`should`; validator는 legacy 입력도 처리 |
| successful-sync/status max-age와 miss 시 offline cutoff | `OPEN-RT-TIME-01` | CP의 24시간 **시도** 요구와 구분하여 04 `OPEN-TIME-01`/CPS에서 확정 |

## 3. Runtime 구성요소와 신뢰 경계

### 3.1 논리 구성요소

```text
Capture / Import pipeline
  └─ Asset + source metadata
       │
       ▼
REE Generator Product
  ├─ Assertion / Ingredient builder
  ├─ Claim + Manifest builder
  ├─ C2PA format embedder
  ├─ Runtime policy/status cache
  └─ TSA client
       │ TB-01                         │ TB-02
       ▼                               ▼
Claim signing boundary             TSA TA in TEE
  ├─ K_claim                           ├─ K_tsu
  ├─ caller/key ACL                    ├─ strict RFC 3161 parser
  └─ constrained sign operation        ├─ trusted-time engine
                                       ├─ serial/rollback state
                                       └─ activation verifier
                                               │ TB-03
                                               ▼
                                    Online time/status/control sources
```

| Component | 소유 상태 | 신뢰하지 않는 입력 | 필수 출력/통제 |
|---|---|---|---|
| Capture/Import pipeline | 원본 frame/stream/file와 capture metadata | 외부 파일, sensor/driver metadata, remote ingredient | immutable handoff 또는 변경 탐지 가능한 handle |
| REE Generator | Assertion, Claim, staging Manifest와 job state | imported Asset/Manifest, IPC 응답, local wall clock | deterministic serialization, exact binding, atomic commit |
| Claim signing boundary | `K_claim`, key authorization metadata | REE payload와 caller identity | 승인 caller의 Claim signing operation만 수행 |
| TSA client | v2 timestamp `ToBeSigned`, request correlation | TA 응답 전부 | request/response 결속 검증 후 `sigTst2` 전달 |
| TSA TA/TEE | `K_tsu`, trusted-time·serial·activation state | REE, wall clock, network, request policy와 server artifact | RFC 3161 token 또는 stable failure |
| Time/status/control adapter | 검증된 source artifact와 monotonic freshness | network response, DNS/TLS만 통과한 값, rollback cache | signature/path/audience/freshness가 검증된 input |

### 3.2 키와 credential domain

| 항목 | `K_claim` | `K_tsu` |
|---|---|---|
| 목적 | C2PA Claim signature | RFC 3161 TimeStampToken signature |
| 인증서 | Claim Signing Leaf | TSA Time-Stamp Signing Leaf |
| 실행 경계 | 승인된 Claim signing boundary | On-Device TSA TA가 실행되는 TEE |
| raw private key | Claim Generator가 AL별 보호조건 밖에서 획득 금지 | TEE 밖에 노출 금지 |
| 허용 operation | C2PA Claim에 한정된 signing | 검증된 RFC 3161 request에 대한 token 생성만 |
| activation | 별도 activation API 없음 | single-active invariant 필수; staged activation은 채택한 project mechanism에서만 적용 |
| trust path | C2PA Claim signer trust | 별도 C2PA TSA trust |

두 키의 SPKI, key handle, certificate와 authorization namespace를 공유하지 않는다. 한 키에 두 Leaf를 결속하거나 한 secure-world raw sign API가 caller parameter만으로 두 목적을 선택하게 하지 않는다.

### 3.3 신뢰 경계

| ID | 경계 | 공격 가능성 | Acceptance 통제 |
|---|---|---|---|
| `RT-TB-01` | REE ↔ Claim signing boundary | arbitrary signing, caller spoofing, payload 교체 | OS/hardware ACL, caller identity, key purpose, immutable job digest |
| `RT-TB-02` | REE ↔ TSA TA | malformed DER, oversized request, replay, policy/key 선택 주입 | strict DER, allowlist, bounded resource, TEE-owned time/serial/key |
| `RT-TB-03` | TEE ↔ time/status/control source | replay, stale/rollback, wrong audience/environment, forged stop/activation | signature/path, nonce, counter, expiry, tuple binding, sealed high-water mark |
| `RT-TB-04` | Asset/ingredient ↔ Generator | parser exploit, metadata spoof, TOCTOU, provenance grafting | type/size limits, validation, immutable snapshot, binding 재계산 |
| `RT-TB-05` | Runtime ↔ filesystem/media container | partial write, exclusion-range abuse, post-hash mutation | format-specific two-pass/preallocation, fsync/atomic replace, final self-validation |

### 3.4 공격자 가정

다음 능력을 가진 공격자를 가정한다.

- accepted·image-authenticated Generator TCB 밖의 REE peer, IPC caller, imported Asset/metadata, filesystem namespace와 scheduling을 통제한다.
- 이전의 정상 request/response, activation artifact, time/status evidence를 재전송한다.
- crash, reboot, storage rollback, power loss와 concurrent request를 유발한다.
- malformed CBOR/COSE/JUMBF/DER/CMS를 제공하고 parser의 CPU·memory·stack을 고갈시킨다.
- debug build, 다른 product/environment의 credential 또는 stale provider version을 production에 섞는다.
- Asset을 hash한 뒤 signing/embedding 전후에 교체한다.

이 acceptance의 TCB에는 승인·image-authenticated Generator build, immutable snapshot manager, Claim-sign authorization mediator와 final validator/committer가 포함된다. 이들 자체의 완전한 runtime compromise를 같은 REE 통제로 가정하면서 그 내부 self-check를 보안 증거로 사용하지 않는다. TCB compromise, image authentication 실패 또는 memory/IPC isolation 우회가 탐지·의심되면 affected output을 신뢰하지 않고 신규 signing/publication을 중단해 04 incident handoff로 넘긴다.

TEE, hardware Root of Trust와 승인된 source도 절대 안전하다고 가정하지 않는다. 그 compromise는 04의 provider/status/incident handoff로 처리하고 이 문서는 장치가 해당 결과를 적용했음을 증명한다.

## 4. End-to-end runtime 흐름

### 4.1 사전 readiness gate

Runtime은 Claim 생성·서명 readiness와 즉시 timestamp 발급 readiness를 서로 다른 predicate로 계산한다.

```text
CLAIM_READY =
  approved_product_environment_provider_build
  AND K_claim_matches_Claim_Leaf
  AND Claim_algorithm_KU_EKU_valid
  AND Claim_caller_authorized
  AND mandatory_Claim_status_control_fresh
  AND immutable_input_snapshot_available
  AND claim_job_and_audit_state_writable

TSA_ISSUANCE_READY =
  K_tsu_is_the_only_SIGNING_ACTIVE_key
  AND K_tsu_matches_TSA_Leaf
  AND TSA_algorithm_KU_EKU_profile_valid
  AND mandatory_TSA_status_control_fresh
  AND trusted_time_and_declared_accuracy_valid
  AND serial_activation_state_writable_and_nonrollback
```

- 모든 작업은 `CLAIM_READY`를 통과해야 한다.
- 이번 작업에서 timestamp를 즉시 발급할 때만 `TSA_ISSUANCE_READY`도 통과해야 한다.
- timestamp-required product profile은 `TSA_ISSUANCE_READY=false|unknown`을 publication 차단으로 연결한다.
- timestamp-optional/offline profile은 사전에 승인된 경우에만 `TIMESTAMP_PENDING` 또는 `TIMESTAMP_SKIPPED_BY_POLICY`로 진행할 수 있으며, timestamp가 완료된 것으로 표시하지 않는다.

Certificate `good`은 Claim signing caller authorization 또는 TSA key activation을 의미하지 않는다. 반대로 서버 projection이 `ACTIVE`여도 TEE가 실제 `SIGNING_ACTIVE`임을 뜻하지 않는다.

### 4.2 생성 순서

```text
1. Capture/import input을 검증하고 immutable job snapshot을 만든다.
2. source metadata와 사용자 선택을 policy에 따라 최소화·정규화한다.
3. ingredient가 있으면 기존 manifest를 검증하고 ingredient assertion을 만든다.
4. actions와 기타 assertion을 만들고 Assertion Store에 저장한다.
5. 최종 Asset layout에 맞는 hard binding을 계산한다.
6. assertion URI/hash, hard binding과 signature URI를 포함한 Claim을 만든다.
7. Claim을 deterministic CBOR로 serialize하고 COSE Sig_structure를 만든다.
8. Claim signing boundary가 K_claim으로 COSE signature를 생성한다.
9. timestamp branch를 선택한다.
   - 즉시 발급: v2 CounterSignature ToBeSigned를 hash하고 TSA TA에서 token을 받아 sigTst2에 결합한다.
   - 지연 발급: immutable request context를 durable queue에 저장하고 TIMESTAMP_PENDING으로 전환한다.
   - 정책상 생략: 명시적인 TIMESTAMP_SKIPPED_BY_POLICY로 전환한다.
10. Manifest Store를 Asset에 쓰고 독립 parser/validator로 결과를 재검증한다.
11. 성공한 완성본만 atomic commit하고 staging data를 정리한다.
```

캡처 세션의 byte 동결, sign-before-publish, atomic commit과 실패 결과 폐기는 이 프로젝트의 `ARCH-DECISION`이다. C2PA 원문에 같은 이름의 단일 MUST가 있다고 표현하지 않는다.

### 4.3 Job 상태와 원자성

```text
CREATED
  → INPUT_FROZEN
  → ASSERTIONS_BUILT
  → CLAIM_FROZEN
  → CLAIM_SIGNED
  → TIMESTAMPED | TIMESTAMP_PENDING | TIMESTAMP_SKIPPED_BY_POLICY
  → MANIFEST_EMBEDDED
  → SELF_VALIDATED
  → COMMITTED

어느 단계든 실패 → FAILED → staging 격리/정리
```

- `CLAIM_FROZEN` 뒤 Claim bytes 또는 protected header가 바뀌면 서명을 재사용하지 않고 새 job으로 돌아간다.
- `CLAIM_SIGNED` 뒤 timestamp가 실패했을 때 timestamp 없는 Manifest를 허용할지는 product policy가 사전에 결정한다. silent downgrade는 금지한다.
- Timestamp 없는 Manifest도 C2PA 형식상 가능하고 현재 validation time이 signing chain validity 안이면 valid일 수 있다. 다만 credential 만료·폐기 뒤 장기 유효성 이점이 없으므로 정책과 UX에서 구분한다.
- partially embedded Asset이나 self-validation에 실패한 Asset은 원본/최종 경로를 대체하지 않는다.
- retry는 같은 서명 또는 token을 우연히 중복 생성하지 않도록 단계별 idempotency key와 durable result를 사용한다.

### 4.4 Asset TOCTOU와 binding

Hard binding은 Manifest가 같은 Asset에 속하고 binding 대상 bytes가 변경되지 않았음을 검증하는 수단이다. Soft binding은 파생본·rendition 발견에 유용하지만 cryptographic integrity를 대체하지 않는다.

Runtime은 다음을 지킨다.

- standard manifest에는 정확히 하나의 hard binding assertion을 포함한다.
- format별 exclusion range, box layout, fragmented/streaming 규칙을 C2PA 2.4의 해당 Asset format 절과 함께 적용한다.
- 플랫폼이 content-immutable generation/version을 보증하는 object를 사용하거나, app-private snapshot copy를 만든 뒤 같은 snapshot handle 하나만 parse, hash, sign과 embed에 사용한다. 일반 file descriptor, identity와 length의 일치는 불변성 증거가 아니다.
- path, symlink 또는 content-provider URI를 다시 resolve해 이름만 같은 object를 서명하지 않으며 same-size in-place overwrite도 탐지한다.
- preallocation/two-pass flow에서는 placeholder와 exclusion range를 고정한 뒤 final bytes를 재검사한다.
- encoding, metadata injection, thumbnail 생성 등 Asset bytes를 바꾸는 작업은 binding 계산 전에 끝내거나 규격의 multiple-step 절차를 따른다.
- 최종 파일에서 hard binding을 다시 계산하고 Claim에 들어간 값과 일치한 뒤에만 commit한다.

### 4.5 Durable job·지연 queue

Nonce는 RFC 3161 응답 결속 수단일 뿐 operation의 side effect를 멱등하게 만들지 않는다. Claim signing job과 지연 timestamp queue는 다음 공통 계약을 갖는다.

```text
QUEUED → IN_FLIGHT → APPLIED
                  └→ RETRY_WAIT → IN_FLIGHT
                  └→ PERMANENT_FAILED | EXPIRED
```

- ledger lookup key는 `{product, environment, authenticatedCallerPrincipal, credential-or-TSU namespace, operationId}`이고 scope authorization을 terminal-result 조회보다 먼저 검증한다. `operationId` 자체도 random 또는 해당 scope 안에서만 유일한 identifier다.
- `requestDigest`는 canonical operation type, product/environment, authenticated caller, credential/TSU scope, immutable signing/timestamp input, algorithm, key ID와 policy를 결속한다.
- 같은 scope+`operationId`+같은 `requestDigest`는 durable terminal result를 반환한다. 같은 scope/ID+다른 digest 또는 다른 caller/product/environment/key scope의 replay는 `IDEMPOTENCY_CONFLICT`/`POLICY_DENIED`로 거부하고 기존 결과를 노출하지 않는다.
- worker는 CAS/lease로 한 record만 점유하고 lease expiry, duplicate delivery와 concurrent retry를 시험한다.
- Claim signature 또는 TimeStampToken 결과와 serial/result metadata를 durable commit한 뒤에만 caller에 성공을 반환한다. response loss 뒤에는 새 결과를 만들지 않고 저장한 결과를 돌려준다.
- retry에는 TTL, attempt count, exponential backoff+jitter와 per-product quota가 있고 만료·영구 실패 record와 민감 payload는 승인 retention 뒤 purge한다.
- queue는 app-private ACL, at-rest confidentiality와 integrity, rollback detection을 적용하며 raw Asset path나 불필요한 content-derived identifier를 저장하지 않는다.

## 5. C2PA Claim 생성·서명 acceptance

### 5.1 Assertion과 Claim 구성

`C2PA-REQUIRED` baseline은 다음과 같다.

- 모든 assertion을 Claim 확정 전에 Assertion Store에 저장한다.
- Claim에는 특정 Asset version을 고유하게 식별하는 `instanceID`, `claim_generator_info`, `signature`와 `created_assertions`를 포함한다. Asset에 XMP가 있으면 `xmpMM:InstanceID`를 사용하는 것이 `C2PA-RECOMMENDED`이고, XMP가 없으면 다른 unique identifier를 사용해야 한다(`C2PA-REQUIRED`). v2 `claim_generator_info` map에는 실제 non-human Generator Product를 나타내는 `name`을 포함한다.
- `claim_generator_info.specVersion`은 C2PA 권고에 따라 넣고, SemVer 형식으로 실제 적용 규격 version을 표시한다. 생략에는 상호운용 근거가 필요하다.
- Claim의 `created_assertions`와 선택적 `gathered_assertions`가 같은 Manifest의 Assertion Store에 실제 존재하는 assertion을 완전하게 참조한다.
- assertion hash/URI는 실제 serialized assertion과 일치하며 deprecated construct를 신규 생성하지 않는다.
- standard manifest의 `created_assertions`에는 current Asset의 hard binding이 포함된다.
- 모든 standard manifest에는 `created_assertions`에 actions assertion이 최소 하나 있고, 정확히 한 actions assertion에 `c2pa.created` 또는 `c2pa.opened` 중 하나가 있어야 하며 신규 생성은 `c2pa.actions.v2`를 사용한다. De novo 생성·캡처이면 첫 actions assertion의 첫 action은 `c2pa.created`이고 실제 inception에 맞는 `digitalSourceType`을 포함한다. 기존 `parentOf` ingredient를 열어 편집했으면 첫 action은 `c2pa.opened`이고 대응 `c2pa.ingredient.v3` hashed URI를 참조한다. 전체 manifest에서 두 action type은 합쳐 하나뿐이다.
- standard manifest의 `parentOf` ingredient assertion은 0개 또는 1개다.
- Claim의 `signature` field는 같은 Manifest에 생성될 Claim Signature box를 가리키는 absolute JUMBF URI다.
- v2 Claim CBOR은 RFC 8949 Core Deterministic Encoding Requirements를 만족한다.

`created_assertions`는 signer가 만든 assertion, `gathered_assertions`는 외부 source에서 모아 signer에게 귀속되지 않는 assertion이라는 의미를 유지한다. Assertion의 값이 사실이라는 보증과 assertion bytes가 서명 뒤 변하지 않았다는 보증을 혼동하지 않는다.

### 5.2 Ingredient, actions와 hashed URI

- 기존 Asset을 입력으로 사용하면 관계에 맞는 ingredient assertion을 기록한다. Derived는 `parentOf`, composition은 `componentOf`, computational input은 `inputTo`를 사용한다.
- current ingredient label은 `c2pa.ingredient.v3`이고 deprecated v1/v2를 신규 생성하지 않는다.
- ingredient의 C2PA Manifest가 있으면 lineage 전체를 recursive validation한다. `activeManifest`가 있으면 `validationResults` map에 전체 success/informational/failure 결과인 `activeManifest`와 배열 `ingredientDeltas`를 모두 넣고, 없으면 `validationResults`를 넣지 않는다. 중첩 대상이 없을 때도 `ingredientDeltas: []`를 포함한다. Manifest Store의 중첩 ingredient 중 `activeManifest`가 있는 각 항목에는 `ingredientDeltas` entry를 만들고, 그 entry에 `ingredientAssertionURI`와 status type/code/url 기준 delta인 `validationDeltas`를 기록한다.
- 기존 Ingredient Store의 validation된 manifest는 규격상 예외 또는 명시적 opt-out이 아니면 새 Manifest Store로 복사한다. active manifest를 복사하면 v3 ingredient에 그 manifest와 signature를 가리키는 `activeManifest`, `claimSignature` hashed URI를 모두 넣는다.
- embedded ingredient Manifest는 identifier collision을 C2PA 절차대로 처리하고 provenance grafting을 막는다.
- `c2pa.opened`는 `parentOf`, `c2pa.placed`는 `componentOf` ingredient hashed URI와 일치해야 한다.
- 캡처 inception의 first action과 `digitalSourceType`은 실제 capture pipeline에 맞게 선택한다. 현실 장면의 단일 digital capture에는 IPTC `digitalCapture`가 적절할 수 있지만 computational capture 등에는 제품별 mapping을 사용한다.
- `allActionsIncluded`는 일반적으로 실제 이력 완전성에 맞춰 설정한다. `c2pa.opened` 기록만을 위해 열고 다른 변경 없이 즉시 다시 저장한 경우에는 `true`로 설정한다.
- `c2pa.actions`/`c2pa.actions.v2`를 redact하지 않는다. update manifest를 만들 때 current Asset에 적용되는 hard binding도 redact하지 않는다.
- hashed URI는 C2PA가 정한 JUMBF box 범위를 hash하고, 가장 가까운 `alg` field를 사용한다. algorithm identifier가 없으면 Claim 값으로 fallback하되 어디에도 없으면 거부한다.

Remote ingredient/manifest 자체를 발견하는 initial fetch와, 그 Manifest가 참조하는 icon/cloud/external child data의 follow-on fetch를 구분한다. Content에서 유도된 모든 outbound category—manifest repository discovery, remote ingredient, claim-generator icon, cloud/external assertion·reference와 content-provided trust locator—에는 `ARCH-DECISION`으로 off-by-default를 적용한다.

- 동의가 없으면 initial discovery를 포함한 outbound request는 0이다.
- 명시적 user consent, privacy disclosure와 allowlist policy를 통과하면 initial manifest/ingredient를 bounded fetch하여 검증할 수 있다. Initial Claim이 reject되면 그 Claim에서 파생된 icon/external child follow-on request는 0이다.
- 승인 privacy relay는 consent와 relay가 알게 되는 viewing data/처리방식 disclosure를 우회하는 대안이 아니라 추가 transport다.
- insecure/non-allowlisted endpoint와 content-provided trust locator를 자동 trust-store 입력으로 사용하지 않는다.
- Cloud/hashed external payload는 parent Claim을 먼저 성공적으로 validation한 뒤에만 fetch한다. Optional payload fetch/validation 실패만으로 그 parent Claim을 reject하지 않는다.

Fetched category별 validation pipeline은 다음과 같다.

| Category | Application에 제공하기 전 gate |
|---|---|
| Remote manifest/ingredient | bounded temporary sink → sandboxed C2PA parse → Claim/signature/credential/binding validation. Outer hash가 없다는 이유만으로 거부하지 않으며 검증 전 provenance/UI에 expose하지 않음 |
| Cloud data/hashed external reference/icon hashed URI | declared size가 있으면 일치하고 hash algorithm/value를 검증한 뒤 expose. External data의 `dc:format`이 있을 때만 HTTP `Content-Type`과 비교하며 생략되면 content-type validation은 성공. Cloud data에서 `dc:format`이 없으면 `application/jumbf`를 사용하고 deprecated `content_type`은 무시 |
| Unhashed external reference | declared size가 있으면 검증하고 `dc:format`이 있을 때만 HTTP `Content-Type`과 비교하며, advisory로 표시. Application-dependent use 전에 독립 검증하지 않으면 trusted assertion으로 취급하지 않음 |

Missing/unknown required hash algorithm, wrong size/type/hash 또는 redirect 후 content 변경은 stable mismatch로 temporary data를 폐기한다. 모든 category는 scheme/host/IP/port, redirect와 aggregate budget을 적용한다.

모든 remote fetch에는 scheme/host/IP/port, redirect, compressed/uncompressed size, time, graph depth/width/node/edge/count와 aggregate-byte 제한을 적용한다. 재귀 ingredient graph는 cycle을 탐지하고 iterative traversal과 총 budget으로 stack/resource exhaustion을 막는다.

### 5.3 Hard·soft binding assertion 계약

`c2pa.hash.data`를 생성할 때 `hash`와 zero-filled `pad`를 포함하고, `pad2`가 있으면 역시 zero-filled로 둔다. Exclusion range는 `start` 오름차순이며 겹치지 않아야 한다. Logical-unit header/length를 침범하지 않고 규격이 허용한 free/pad 예외 외에는 Manifest Store 또는 Asset metadata만 제외한다. 제외된 bytes가 decoder의 Asset 해석을 바꾸거나 실행 가능한 숨은 payload를 만들 수 있으면 거부한다. `c2pa.hash.data`를 cloud-data/external-reference assertion 안에 넣거나 compressed manifest와 함께 사용하지 않는다.

Soft binding을 생성하면 current label `c2pa.soft-binding`, algorithm identifier와 하나 이상의 `blocks(scope,value)`를 포함한다. `pad`/`pad2`가 있으면 zero-filled이고 deprecated soft-binding algorithm으로 신규 manifest를 만들지 않는다. Soft binding으로 parent manifest를 발견해 ingredient로 넣으면 `softBindingsMatched=true`와 non-empty `softBindingAlgorithmsMatched`를 기록하고, located manifest의 모든 soft-binding assertion match를 검증한다. Soft binding은 hard binding이나 Claim signature를 대체하지 않는다.

### 5.4 COSE signature 입력

standard/update manifest 모두 다음 바이트 계약을 사용한다.

```text
claim_document = deterministic CBOR claim bytes

Sig_structure = [
  "Signature1",
  body_protected,
  external_aad = h'',
  payload = claim_document
]

COSE_Sign1_Tagged.payload = nil  // detached content mode
```

- `Sig_structure.payload`는 serialized Claim document이며 `nil`이 아니다.
- serialized `COSE_Sign1_Tagged`의 payload field만 detached mode를 나타내는 CBOR `nil`이다. zero-length `bstr`로 대체하지 않는다.
- `context`는 `Signature1`이고 `external_aad`는 길이 0의 `bstr`이다.
- COSE `alg`는 integer label `1`로 protected header에 있고 선택한 key/algorithm과 일치한다.
- 결과 `COSE_Sign1_Tagged`는 Claim Signature box에 쓴다.

Asset 전체, Claim의 JSON 표현, pre-hashed Claim digest 또는 C2PA SDK의 임시 object를 위 payload 대신 서명하지 않는다. Secure boundary가 pre-hash interface만 제공하면 COSE algorithm이 요구하는 hashing/encoding과 이중 hash 방지를 provider vector로 입증해야 한다.

### 5.5 Algorithm과 key 일치

Content Credentials 2.4 신규 Claim signature allowlist는 ES256/384/512, PS256/384/512와 Ed25519용 EdDSA다. Hash field의 allowlist는 SHA-256/384/512다. 실제 runtime은 다음 교집합만 활성화한다.

```text
C2PA 2.4 algorithm allowlist
AND issued Claim Leaf SPKI/profile
AND secure boundary가 실제로 강제하는 key parameters
AND provider/version interoperability evidence
```

- ECDSA key는 P-256/P-384/P-521 중 하나, RSA-PSS key는 2048 bit 이상, EdDSA는 Ed25519만 허용한다.
- COSE `alg`, Leaf SPKI, hardware authorization과 실제 signing primitive가 일치하지 않으면 서명하지 않는다.
- provider가 지원하지 않는 algorithm을 software fallback으로 조용히 전환하거나 private key를 export하지 않는다.
- key handle로 조회한 public key의 normalized SPKI digest를 설치 시점과 매 process start/readiness 시점에 Leaf SPKI와 비교한다.
- ECDSA의 COSE signature는 고정 길이 `R || S`다. Platform API가 ASN.1 DER ECDSA를 반환하면 strict parse하여 각 정수를 curve 길이의 unsigned big-endian으로 정규화하고, DER blob 자체를 COSE signature `bstr`에 넣지 않는다.

### 5.6 `x5chain`과 credential 처리

신규 Generator acceptance profile은 다음을 강제한다.

1. identity credential은 protected+unprotected 합집합에 정확히 한 개다.
2. `x5chain`은 COSE protected header에만 둔다.
3. header label은 integer `33`만 생성한다.
4. 첫 certificate는 `K_claim`의 signer Leaf이고 뒤에 issuer 순서로 모든 intermediate를 넣는다.
5. trust anchor/root certificate는 넣지 않는다.
6. self-signed 또는 header-supplied certificate를 trust store에 자동 등록하지 않는다.

C2PA compatibility validator는 legacy string `x5chain` label과 unprotected 위치를 읽을 수 있어야 한다. 그러나 신규 생성 acceptance를 그 legacy 형태로 완화하지 않는다. 두 label이 함께 있거나 같은 label이 protected/unprotected 양쪽에 중복된 경우에는 C2PA 2.4 규칙대로 처리하고 ambiguity를 정상화하여 서명하지 않는다.

### 5.7 Claim signing boundary contract

`K_claim` boundary는 최소 다음 logical input을 결속한다.

```text
ClaimSignRequest = {
  operation: "C2PA_CLAIM_SIGN",
  jobId,
  callerIdentity,
  product/environment,
  keyId + expectedSpkiDigest,
  coseAlgorithm,
  bodyProtectedDigest,
  claimBytes or provider-defined exact signing input,
  freshness/idempotency context
}
```

- OS/hardware가 강제하는 caller ACL과 application identity를 사용한다.
- `K_claim`으로 generic `sign(bytes)`를 다른 app 또는 debug interface에 제공하지 않는다.
- boundary가 C2PA semantics를 직접 파싱하지 못하는 platform keystore라면 이 한계를 명시하고 호출자 identity·verified boot·app integrity·key authorization과 runtime isolation의 결합으로 misuse risk를 다룬다.
- 사용자 생체인증을 쓰는지는 product UX 결정이며 C2PA 요구로 오인하지 않는다. background capture 요구와 key authorization timeout을 함께 시험한다.
- signing failure, caller mismatch, key invalidation 또는 rate-limit은 software key fallback 없이 실패한다.

### 5.8 서명 직후 검증과 상태 의미

Generator는 최소한 다음 self-check를 수행한다(`ARCH-DECISION`).

- 독립 COSE parser로 구조, protected header와 algorithm을 읽는다.
- `x5chain` 값이 단일 certificate `bstr`이면 1-element list로, array면 그대로 정규화한 뒤 첫 Leaf public key로 Claim signature를 검증한다.
- Claim bytes와 signature URI, assertion URI/hash를 재검증한다.
- Leaf와 intermediate path를 pinned trust configuration에 대해 검증하되 embedded chain을 trust anchor로 사용하지 않는다.
- ingredient, active manifest와 hard binding을 최종 Asset에서 재검증한다.
- trusted timestamp가 있으면 timestamp time을, 없으면 current validation time을 certificate validity 평가에 적용하는 C2PA 의미를 시험한다.

`Well-Formed ⊂ Valid ⊂ Trusted`를 유지한다. Soft-binding discovery success, signature cryptographic success 또는 local validator success 하나만으로 Asset이 Trusted라고 표시하지 않는다. 최소한 hard/soft binding, signature, credential trust, timestamp, ingredient와 overall manifest state를 직교한 결과로 보존한다.

## 6. C2PA v2 timestamp와 RFC 3161 acceptance

### 6.1 정확한 v2 timestamp 입력

C2PA 2.4 신규 Generator는 deprecated v1 timestamp를 만들지 않는다. v2 입력은 Claim CBOR나 Asset hash가 아니다.

```text
v2_payload = serialized CBOR bstr 전체인
             COSE_Sign1_Tagged.signature field의 값

CounterSignature_Sig_structure = [
  "CounterSignature",
  body_protected,
  external_aad = h'',
  payload = v2_payload
]

to_be_timestamped = CBOR-encoded CounterSignature_Sig_structure
MessageImprint.hashedMessage = HASH(to_be_timestamped)
```

`v2_payload`에는 signature byte string의 내용만이 아니라 CBOR major type과 length를 나타내는 serialized bytes도 포함된다. 동일 signed object에 대해 생성 측과 validation 측이 같은 exact byte vector를 재현해야 한다.

### 6.2 TimeStampReq 생성

C2PA 호출용 request는 다음을 만족한다.

| Field | Acceptance |
|---|---|
| `version` | RFC 3161 v1 |
| `messageImprint.hashAlgorithm` | SHA-256/384/512 중 TSA가 지원하는 OID |
| `messageImprint.hashedMessage` | OID에 맞는 길이이고 6.1의 exact input hash |
| `reqPolicy` | 생략하거나 allowlist의 TSA policy OID |
| `nonce` | RFC 3161에서는 선택이지만 이 프로젝트의 production C2PA requester profile에서는 필수. 충분히 큰 one-time unpredictable 값이며 bounded in-flight record에 결속 |
| `certReq` | `true`; signer certificate/chain을 응답에 포함시키기 위한 C2PA 추가 요구 |
| `extensions` | 명시적으로 지원·시험된 것만 |

Requester는 request send monotonic time, nonce, request digest와 허용 최대 대기시간을 bounded in-flight record에 저장한다. Nonce가 없거나 window를 넘긴 응답은 production profile에서 수용하지 않는다. RFC 3161 nonce는 응답 timeliness/replay detection을 돕지만 server-side idempotency를 보장하지 않는다. 같은 전송을 재시도할지 새 logical operation을 만들지는 별도 operation ID와 durable ledger로 구분한다.

### 6.3 TSA TA 입력 경계와 strict parsing

CP는 On-Device TSA application이 TEE에서 실행되고 외부에서 `MessageImprint`와 선택적 `nonce`를 받을 수 있다고 정한다. Production contract에서 REE는 time, accuracy, serial, active key 또는 token policy의 권위자가 아니다.

TSA TA는 다음 순서로 처리한다.

1. IPC caller, command/version과 input size를 확인한다.
2. DER을 단일 object로 strict parse하고 trailing data, indefinite/non-minimal/duplicate/overflow 표현을 거부한다.
3. request v1, MessageImprint OID와 digest length를 확인한다.
4. SHA-256/384/512 외 algorithm을 `badAlg`로 거부한다.
5. unsupported policy/extension을 해당 RFC failure로 거부한다.
6. C2PA production operation에서 `certReq != true` 또는 nonce가 없으면 project profile의 `badRequest`로 거부한다. 이는 RFC 3161 일반 TSA의 보편 요구가 아닌 강화 정책이다.
7. nonce를 응답에 exact value로 넣을 수 있도록 request에 결속한다.
8. time, certificate/status, activation과 single-active key readiness를 한 snapshot으로 판정한다.
9. serial을 crash-safe하게 reserve한 뒤 TSTInfo와 CMS를 TEE 내부에서 구성·서명한다.

REE가 완성한 TSTInfo/CMS bytes를 `K_tsu`로 raw sign하게 하지 않는다. 그 설계는 TEE-owned time, policy, serial과 RFC 3161 전용성을 우회하므로 거부한다.

### 6.4 TSTInfo와 TimeStampToken 생성

`RFC-REQUIRED`/`C2PA-REQUIRED` 조건은 다음과 같다. 별도 표시한 항목은 C2PA CP 또는 이 프로젝트가 RFC baseline을 강화한다.

- TSTInfo version은 v1이고 policy는 실제 적용한 policy OID다.
- MessageImprint algorithm/value는 검증된 request와 같다.
- `serialNumber`는 정한 TSA scope에서 유일하고 crash/reboot 뒤에도 재사용하지 않는다.
- `genTime`은 seconds를 포함한 UTC GeneralizedTime이며 DER 제한을 만족한다.
- intended accuracy는 C2PA CP의 강화 `C2PA-REQUIRED`에 따라 각 TSTInfo의 `accuracy`에 정의한다. 공개 TSA policy/practices는 추가 disclosure이며 token 내부 accuracy를 대체하지 않는다.
- request에 nonce가 있으면 같은 nonce를 반드시 포함한다.
- `tsa`가 있으면 signer certificate의 subject name 중 하나와 일치한다.
- TimeStampToken은 CMS SignedData이고 EncapsulatedContentInfo `eContentType`은 `id-ct-TSTInfo`(`1.2.840.113549.1.9.16.1.4`), `eContent`는 DER-encoded TSTInfo다.
- token에는 TSA signature 외 다른 signature가 없다.
- CMS signature algorithm은 C2PA 2.4의 allowed/deprecated validation 규칙과 발급된 TSA Leaf profile의 교집합이다. 신규 발급은 allowed algorithm만 사용한다.
- signer Leaf의 RFC 5280 path, key usage와 certificate profile을 검증하고, critical EKU에는 `id-kp-timeStamping`만 있어야 한다. Claim Signing Leaf나 extra/missing/non-critical time-stamping EKU certificate를 사용하지 않는다.
- TSA signer certificate identifier를 SigningCertificate 또는 SigningCertificateV2 signed attribute에 넣는다.
- certificate identifier에 SHA-1 외 hash를 사용하면 ESSCertIDv2/SigningCertificateV2를 사용한다.
- `certReq=true` 응답의 CMS `certificates`에는 ESS identifier가 가리키는 TSA signer Leaf를 넣는다(`RFC/C2PA-REQUIRED`). Offline path building을 위해 필요한 intermediate를 모두 넣고 root를 제외하는 것은 이 프로젝트의 `ARCH-DECISION`이며, 승인된 validator intermediate store로 완성하는 profile은 별도 상호운용 증거가 있어야 한다. CMS `CertificateSet`의 배열 순서를 path 의미로 사용하지 않는다.
- success status `0/1`에는 token이 있고 그 외 status에는 token이 없다.

TSA TA가 발급 결과를 반환하기 전에 자신의 signer certificate로 CMS signature algorithm, KU/EKU/path, `eContentType`, ESS certificate binding, MessageImprint, nonce, required accuracy, serial과 genTime encoding을 self-check한다.

### 6.5 `sigTst2` 결합과 requester 검증

Requester는 TA 응답을 신뢰하지 않고 다음을 검증한다.

1. RFC 3161 status/failure와 token presence의 조합이 유효하다.
2. CMS/TSTInfo가 strict DER이고 TSA signature가 유효하다.
3. CMS `eContentType=id-ct-TSTInfo`이고 CMS signature algorithm이 C2PA allowed/deprecated validation 규칙 안에 있다. 신규 발급 token에서 deprecated algorithm이면 수용하지 않는다.
4. ESSCertID/ESSCertIDv2가 실제 signer certificate를 식별한다.
5. signer certificate path, KU와 critical EKU exactly `id-kp-timeStamping`을 검증한다.
6. MessageImprint algorithm/value가 6.1에서 보낸 값과 같다.
7. response nonce가 request와 exact-match하고 bounded in-flight time window 안이다. Request에 `reqPolicy`가 있었으면 TSTInfo policy가 exact-match해야 하며, 생략했으면 응답의 mandatory policy가 승인된 TSA default/allowlist에 있어야 한다.
8. TSTInfo `accuracy`가 존재·유효하고 provider의 declared accuracy와 일치하며 `genTime`이 TSA Leaf와 intermediate의 validity 안에 있다.
9. TSA chain이 Claim signer trust와 별도의 TSA trust store로 이어진다.

통과한 v2 token은 `COSE_Sign1` unprotected header의 string label `sigTst2` 아래 `tstContainer`의 단일 `tstToken.val`로 저장한다. `val`은 `TimeStampResp` 전체가 아니라 DER-encoded `TimeStampToken`을 CBOR byte string으로 감싼 값이다. 한 Manifest에는 timestamp 하나만 생성한다.

### 6.6 Claim trust와 TSA trust의 분리

| 검증 | Trust input | 실패 영향 |
|---|---|---|
| Claim signature | Claim Leaf, intermediate, applicable Claim trust anchor configuration | Claim signature/manifest trust 실패 |
| TimeStampToken | TSA Leaf, intermediate, 별도 C2PA TSA Trust List | timestamp를 무시하고 timestamp 없는 Claim 규칙으로 진행할 수 있음 |
| Claim signing time | trusted/validated `genTime`; 없으면 current validation time | Claim certificate validity 판정 |
| TSA token time | TSA Leaf와 chain의 validity interval | timestamp 신뢰 실패 |

Timestamp의 성공은 Claim signature나 content binding 성공을 대신하지 않는다. 기기 wall clock/EXIF/action time은 metadata이고, COSE protected `iat`는 claimed time of signing일 뿐 trusted RFC 3161 time이 아니다. Claim trust anchor나 private credential store를 TSA trust로 재사용하지 않는다.

### 6.7 Stable failure mapping

| 조건 | TA/RFC 결과 | Runtime 결과 |
|---|---|---|
| unknown/weak hash | `rejection + badAlg` | timestamp 실패; 새 algorithm으로 새 request만 허용 |
| malformed DER/digest length | `rejection + badDataFormat` 또는 `badRequest` | parser metric과 bounded audit, token 없음 |
| unsupported policy | `rejection + unacceptedPolicy` | silent policy 변경 금지 |
| unsupported extension | `rejection + unacceptedExtension` | token 없음 |
| trusted time 불가/accuracy 이탈 | `rejection + timeNotAvailable` | `TIME_UNTRUSTED`, 신규 TST 중단 |
| no active key/certificate/state failure | `rejection + systemFailure` | activation/status recovery 필요 |
| nonce/MessageImprint/ESS mismatch | 반환 token 폐기 | security event; Manifest에 결합 금지 |
| unknown status/failInfo bit | 응답 오류 | fail-closed |

Human-readable `statusString`은 신뢰 판정, retry 또는 metric label에 사용하지 않고 redaction한 diagnostic으로만 취급한다.

### 6.8 Offline·지연 timestamp

Timestamp는 C2PA `SHOULD`이지 모든 Claim의 생성 전제는 아니다. Product가 offline capture를 허용하면 다음을 적용한다.

- timestamp 미완료를 `TIMESTAMP_PENDING`으로 명시하고 trusted time 완료로 표시하지 않는다.
- queue의 전용 encrypted vault에는 immutable COSE signature `bstr`, exact CounterSignature input/messageImprint, signer certificate scoped identifier/notAfter, random job/attempt ID와 nonce만 최소 저장한다. Asset은 raw path가 아니라 app-private opaque record key로 참조하고 승인 retention 뒤 함께 purge한다.
- retry 전에 immutable input digest를 재확인한다. Claim 또는 signature가 달라졌으면 기존 request/response를 폐기한다.
- network error/temporary failure는 bounded backoff+jitter를 사용하며 늦은 응답은 해당 attempt nonce와 operation에 맞을 때만 수용한다.
- deadline은 Claim signing chain 만료보다 앞서고, 만료·구제 불가능한 폐기 뒤에는 무한 retry하지 않는다.
- 사전 예약한 signature box에 `sigTst2`를 안전하게 넣을 수 있을 때만 원 Manifest를 보완한다.
- 이미 배포되었거나 layout/binding 불변성을 보장할 수 없으면 C2PA 2.4의 `c2pa.time-stamp` assertion을 **update manifest**에 추가한다. Timestamp는 대상 signing certificate가 만료되기 전에 추가되어야 한다.
- historical/deprecated Time-Stamp Manifest를 신규 생성하지 않는다. C2PA 2.4의 informative Guidance에 남은 예시보다 normative technical specification의 update-manifest 방식을 우선한다.

지연 timestamp용 update manifest는 다음 wire contract를 모두 만족한다.

- exactly one `c2pa.ingredient.v3` `parentOf` assertion이 대상 active manifest를 가리키며 `activeManifest`와 `claimSignature` hashed URI를 모두 포함한다.
- hard binding, multi-asset hash와 thumbnail assertion을 포함하지 않는다. actions assertion이 있으면 update manifest에 허용된 `c2pa.edited.metadata`, `c2pa.opened`, `c2pa.published`, `c2pa.redacted`만 사용한다.
- `c2pa.time-stamp` assertion은 대상 manifest label URN을 key로 하고 DER TimeStampToken CBOR `bstr`를 value로 하는 non-empty map이며 update manifest 하나에 최대 한 개다.
- 각 token의 v2 payload는 map key가 가리키는 대상 manifest의 serialized COSE signature-field `bstr`다. Update manifest 자신의 signature 또는 Asset hash에 잘못 결속하지 않는다.
- 대상 manifest ID, ingredient hashed URI, token과 update manifest 전체를 독립 validator로 self-validation한 뒤에만 commit한다.

<a id="6-trusted-time과-보호-상태"></a>

## 7. On-Device TSA의 trusted time과 보호 상태

### 7.1 발급 readiness state

```text
BOOTSTRAP
  → TIME_UNTRUSTED
  → TIME_TRUSTED
  → ISSUING_ALLOWED

어느 상태에서든
  accuracy 이탈 / rollback / stale mandatory source / revoked key
  → ISSUING_BLOCKED

검증된 recovery + 새 monotonic evidence
  → TIME_TRUSTED
  → ISSUING_ALLOWED
```

`ISSUING_ALLOWED`는 다음 predicate의 교집합이다.

```text
trusted_time_valid
AND declared_accuracy_maintained
AND leap_policy_ready
AND exactly_one_SIGNING_ACTIVE_K_tsu
AND TSA_leaf_matches_key
AND certificate_valid_now
AND status/provider/control_fresh
AND serial_state_writable_and_nonrollback
```

하나라도 `false` 또는 `unknown`이면 신규 TimeStampToken을 만들지 않는다. 이 stop은 TSA issuance에 적용되며 `K_claim` Claim signing까지 C2PA가 자동 중단하도록 요구한다고 확대 해석하지 않는다. Product가 timestamp-required 정책을 택했을 때만 전체 capture 결과 publication을 막는다.

### 7.2 Online synchronization과 holdover

- On-Device TSA는 UTC(k)에 추적 가능한 online time source와 최소 24시간마다 동기화를 **시도**한다(`C2PA-REQUIRED`).
- source는 CPS/provider profile이 지정하고 authentication, chain, nonce/request binding, freshness와 policy를 검증한다.
- 마지막 성공 sync의 trusted UTC, local monotonic reading, source evidence digest와 uncertainty를 sealed state로 저장한다.
- 현재 trusted time은 마지막 trusted sample과 rollback-resistant monotonic elapsed time으로 계산한다. REE wall clock이나 timezone 설정을 신뢰하지 않는다.
- oscillator drift, source accuracy, transport/asymmetric delay, quantization과 holdover를 합산해 보수적인 uncertainty bound를 계산한다.
- `uncertainty > declared accuracy`이거나 계산할 수 없으면 즉시 issuance를 중단한다(`C2PA-REQUIRED`).
- 정확히 24시간 경계의 inclusive/exclusive semantics, retry schedule과 solely-missed-attempt에 따른 기존 TSU cutoff는 `OPEN-RT-TIME-01`에서 CPS 값을 소비해 확정한다. 이 미결정 상태로 production activation하지 않는다.

### 7.3 Leap second와 time-source profile

CP는 appropriate body가 통지한 leap second에도 synchronization을 유지하도록 요구하지만 bulletin format, authority, step/smear 방식은 정하지 않는다. Provider profile은 최소 다음을 고정한다.

- bulletin authority, signature/path와 identifier/version
- event UTC, polarity, issue/effective/cancel time
- step, smear 또는 provider-specific 처리 mode
- source가 제공하는 UTC(k)와 mode의 호환성
- pre-event 준비 deadline, holdover와 recovery 절차
- replayed, superseded, cancelled, unknown-authority bulletin 처리

Step source를 smear profile로 또는 그 반대로 해석하지 않는다. event 전후 reboot, rollback, source switch 또는 bulletin conflict로 declared accuracy를 보장할 수 없으면 TST 발급을 중단하고 검증된 새 sample과 state reconciliation 전에는 재개하지 않는다.

<a id="311-serial-number와-동시성"></a>

### 7.4 Serial number와 동시성

RFC 3161은 given TSA의 모든 TimeStampToken serial이 유일하고 crash 뒤에도 그 속성을 유지하도록 요구한다. 이 프로젝트는 같은 TSA service Subject를 공유하는 모든 TSU와 모든 key rotation을 하나의 uniqueness scope로 강화한다(`ARCH-DECISION`).

권장 구조는 다음과 같다.

```text
serialNumber = positive_integer(
  server_assigned_64bit_serialNamespace ||
  TEE_rollback_safe_64bit_counter
)
```

- `serialNamespace`는 04의 server transaction이 TSU별로 한 번 배정하고 같은 TSU re-key에 유지한다.
- 다른 TSU에 namespace를 재사용하지 않고 production/non-production namespace를 분리한다.
- counter 증가는 TST 서명 전에 durable reservation하고 성공 여부와 관계없이 예약값을 재사용하지 않는다.
- concurrent request는 TEE lock 또는 atomic monotonic primitive로 직렬화한다.
- counter 저장 실패, rollback 탐지, wrap/exhaustion 또는 duplicate suspicion은 `ISSUING_BLOCKED`다.
- ordering을 `true`로 선언하려면 같은 TSA의 모든 token을 accuracy와 무관하게 `genTime`으로 정렬할 수 있음을 입증해야 한다. 그렇지 않으면 기본 `false`를 사용한다.

### 7.5 TEE 보호 상태

Rollback-resistant storage에 최소 다음을 결속한다.

| 상태 | 최소 field |
|---|---|
| Identity | provider/profile/version, environment, TSA service/TSU, TA measurement/version |
| Key | staged/active/retired key ID, SPKI digest, Leaf issuer+serial+digest, active-key count |
| Time | source/profile, last attempt/success, trusted UTC+monotonic sample, uncertainty/drift, leap bulletin |
| Serial | namespace, next/reserved high-water mark, last committed serial |
| Status | signer/source, certificate ID, this/next update 또는 CRL number, terminal revoked latch |
| Activation | transaction, epoch/counter, last authorization/receipt/finalization digest |
| Policy | allowed hash/policy, declared accuracy, offline cutoff와 emergency version |

Sealed blob의 confidentiality만으로 rollback 방지가 되지 않는다. hardware monotonic counter, replay-protected storage 또는 동등한 mechanism과 atomic update/fault evidence가 필요하다.

<a id="7-key-activation-rotation과-revocation"></a>

## 8. Key activation, rotation과 revocation

### 8.1 세 상태기계의 분리

```text
Certificate (CA authoritative)
  ISSUED_VALID → EXPIRED
               └→ REVOKED

External TSA key (TEE authoritative)
  STAGED_DISABLED → COMMITTED_DISABLED
                      → SIGNING_ACTIVE → RETIRED → DESTROYED

Activation transaction (server authoritative)
  PREPARED → COMMIT_AUTHORIZED → DEVICE_COMMITTED → SERVER_FINALIZED
              └───────────────────────────────→ RECOVERY_REQUIRED
```

- 발급된 TSA Leaf가 `good`이어도 staged key는 서명할 수 없다.
- `SIGNING_ACTIVE` observation은 certificate가 계속 valid/good임을 대신하지 않는다.
- Claim Leaf는 별도 activation transaction이 없고 설치·사용은 certificate acceptance다.
- certificate 상태를 `STAGED`, `ACTIVE` 또는 `RETIRED`로 표현하지 않는다.

### 8.2 Device-side activation acceptance

04가 정의한 authorization/receipt/finalization artifact를 TEE가 다음 순서로 처리한다.

1. artifact signature와 승인 signer key/path를 검증한다.
2. `artifactType+version`, audience, organization/operator, TSA service/TSU와 environment를 exact-match한다.
3. provider/profile, `K_tsu` SPKI digest, TSA Leaf issuer+serial+digest와 current/target key ID를 exact-match한다.
4. transaction/idempotency key, request/previous-artifact digest와 state transition을 확인한다.
5. `issuedAt/notBefore/expiresAt`, emergency/policy version을 trusted time으로 확인한다.
6. device epoch/monotonic counter가 stored high-water mark보다 뒤로 가지 않는지 확인한다.
7. hardware-enforced atomic transition으로 old/new key ACL과 counter를 갱신한다.
8. resulting state, active-key count, counter와 authorization digest를 device-authoritative receipt에 서명한다.
9. server finalization token을 검증하기 전에는 새 key를 `SIGNING_ACTIVE`로 전환하지 않는다.

Unknown version/signer, wrong tuple/key/certificate/environment, expiry/future artifact, replay, counter rollback, out-of-order transition 또는 concurrent two-key result는 `RECOVERY_REQUIRED`다. 운영자 UI의 수동 `PASS`로 우회하지 않는다.

### 8.3 Rotation과 retry

- re-key는 fresh key, fresh CSR과 새 Leaf를 사용하며 same-key renewal을 허용하지 않는다. Evidence는 선택한 profile이 요구할 때만 fresh하게 다시 검증한다.
- re-key 중 old key 하나만 active이고 new key는 staged/committed-disabled 상태다.
- commit은 old→`RETIRED`, new→`COMMITTED_DISABLED`를 하나의 rollback-safe transaction으로 수행한다.
- response loss 뒤 같은 authorization은 같은 durable receipt를 반환한다.
- finalization loss 뒤 server GET/reconciliation이 같은 signed token을 반환해야 한다.
- ambiguous state에서 old/new key 중 하나를 추정하여 활성화하지 않는다.
- abandoned staged/ambiguous key certificate는 04의 incident/status 정책으로 폐기한다.

### 8.4 Certificate·provider·time failure의 stop 조건

Runtime은 다음 상황에서 영향 키의 신규 서명을 중단한다.

- certificate not-yet-valid, expired 또는 authenticated status가 revoked
- `K_claim`/`K_tsu` 노출, 목적 외 사용 또는 caller ACL 우회 의심
- Generator/snapshot/validator TCB의 image authentication 실패, runtime compromise 또는 IPC·memory isolation 우회 의심
- provider Root/AK/SAK, TA measurement/version 또는 Reference Value의 emergency block
- debug/development lifecycle, verified boot/TCB downgrade 또는 승인 environment mismatch
- TSA declared accuracy 이탈, trusted-time rollback 또는 leap handling 불명확
- TSA active-key count가 1이 아님
- mandatory status/time/control artifact가 stale, unknown, invalid 또는 rollback됨
- serial uniqueness를 보장할 수 없음

Remote publication과 offline device stop 사이에는 지연이 있다. Certificate Platform이 연결 끊긴 단말을 즉시 중단할 수 있다고 주장하지 않고, CPS가 승인한 maximum refresh/offline deadline 안의 적용만 보장한다.

### 8.5 TSA cessation과 key compromise

RFC 3161 §4의 token trust 의미를 다음처럼 적용한다.

| 사건 | Authoritative status | 기존 token 판정 |
|---|---|---|
| `K_tsu` compromise | certificate revoked, reason이 있으면 `keyCompromise(1)` | 해당 key의 모든 token을 `genTime`과 무관하게 불신 |
| non-compromise cessation | certificate revoked, CRL reasonCode가 `0/3/4/5` 중 하나 | `genTime < revocationTime`만 유지 |
| non-compromise이나 reasonCode 없음 | revoked entry에 reason 없음 | 해당 key의 모든 token 불신 |
| 허용 집합 밖 reason | authenticated reason이 `1` 또는 그 밖의 값 | cutoff를 적용하지 않고 모든 token 불신 |

04의 signed compromise/cessation handoff는 key/SPKI, TSA Leaf, authoritative status source, revocation time/reason과 `allTokensUntrusted`를 결속한다. Runtime/validator owner는 signature, audience, environment, freshness와 key binding을 검증하고 cache/index에 적용한 acknowledgement를 반환한다. Replacement key는 compromised old-key token의 신뢰를 복구하지 않는다.

C2PA 2.4는 TSA certificate revocation status를 signing time에 capture하거나 validation time에 확인하도록 요구하지 않는다고 명시한다. 위 처리는 RFC 3161 §4와 이 프로젝트의 incident handoff를 적용하는 강화 acceptance이며, C2PA 기본 validator만 실행했다는 증거로 대체할 수 없다.

## 9. Provider/platform acceptance

### 9.1 Provider profile의 최소 계약

Provider별 profile은 최소 다음을 versioned signed artifact로 고정한다.

- production product/environment와 hardware/TEE implementation identity
- Claim signing boundary와 TSA TA의 component, process, UID/SELinux/domain, IPC diagram
- `K_claim`/`K_tsu` algorithm, key authorization, export/backup과 invalidation semantics
- 목표 Generator Product Assurance Level과 GSPR implementation class(Edge/Distributed/Backend), 그 판정에 필요한 static/dynamic evidence
- TA UUID/measurement/version, secure boot/TCB/lifecycle와 debug state
- Claim AL2 또는 optional TSA attestation을 쓰는 경우 Evidence schema, signature/path, subject-key/challenge/audience 위치
- trusted-time source, UTC(k) traceability, accuracy/drift/holdover와 leap profile
- rollback-resistant storage와 monotonic/counter primitive
- activation signer/path, deterministic wire encoding과 state transition
- request/response size, depth, rate, concurrency와 timeout limit
- compressed/uncompressed absolute size와 ratio, redirect/fetch aggregate, ingredient graph node/edge, file descriptor/TEE session과 cancel-cleanup limit
- status/emergency source, refresh/cutoff와 recovery
- positive/negative/fault vector와 알려진 제한

Profile의 `ENABLED`는 이 목록과 evidence가 현재 version에 대해 통과했다는 뜻이다. 비슷한 chipset, OS 또는 app의 통과를 다른 product/firmware/TA version에 상속하지 않는다.

### 9.2 GSPR Assurance Level acceptance

`K_claim` 보호와 Generator Product 전체의 Assurance Level을 hardware-backed key 한 항목으로 환원하지 않는다.

| Gate | Runtime acceptance |
|---|---|
| GSPR O.2 Level 1 | persistent key는 industry-best-practice encryption, volatile memory에서도 signing 준비를 위한 제한된 예외 외에는 encrypted 상태 유지. plaintext access는 least privilege·time-bound, key rotation 가능하며 예외 처리와 담당 component를 architecture evidence에 명시 |
| GSPR O.2 Level 2 | Level 1에 더해 Claim Generator보다 높은 privilege의 key environment에서 생성·저장·사용, authenticated caller만 사용, Claim Generator memory에 raw key 비노출, hardware-derived wrapping. Environment property의 static 입증에는 hardware Root-of-Trust artifact 또는 공인 독립 auditor evidence를 사용할 수 있음 |
| GSPR O.3 | Claim Generator SBOM/SCA, CRITICAL/HIGH 취약점 90일 내 fix/mitigation. Level 2이면 exploit countermeasure, static analysis, image/access control, patch/revision evidence와 external-input validation 추가 |
| GSPR O.4 | Asset/assertion 처리 software도 SBOM/SCA와 patch gate. Level 2이면 image authentication, source isolation, IPC·memory protection과 hardware-backed dynamic evidence 추가 |
| GSPR O.5 Level 1 | TLS 1.3 이상 또는 동등 protocol 요구는 Distributed/Backend subsystem 간 network channel에 적용하며 순수 on-device internal path에 무조건 일반화하지 않음 |
| GSPR O.5 Level 2 | Edge/Backend subsystem 내부에서 Asset/assertion을 전달하는 source process/thread를 kernel/OS 수준에서 격리하고 IPC channel을 보호하며 UID/account·필요 최소 IPC·ACL evidence로 입증 |

Distributed/Backend implementation은 O.2 Level 1부터 Edge/Backend와 key-management/Claim-Generator 경계의 상호 인증, counterpart role authorization을 각 channel에서 강제한다. Remote backend는 호출자가 유효한 Edge instance임을 확인한 뒤에만 Claim을 서명하며 TLS만으로 이 gate를 충족했다고 보지 않는다.

O.2 Level 2의 auditor evidence는 key environment property/static evidence의 대안일 뿐 automated enrollment의 Dynamic Evidence를 대체하지 않는다. 각 conforming instance는 `K_claim` possession을 확인하는 hardware Root-of-Trust-backed artifact를 CA에 반드시 제출하며 auditor-only enrollment를 거부한다.

Certificate의 `c2pa-al` 값은 CPL의 product Max Assurance Level 이하이고 enrollment 때 제출한 현재 instance Dynamic Evidence와 일치해야 한다. Platform API 이름, “hardware-backed” boolean 또는 Secure Enclave/StrongBox 사용 하나만으로 Level 2를 선언하지 않는다.

### 9.3 Android/Samsung 계열 적용 경계

Android Keystore/KeyMint와 StrongBox/TEE-backed key는 `K_claim`의 non-exportability, key authorization과 hardware-backed possession을 뒷받침할 수 있다. Android Key Attestation은 승인 root/status에 대한 chain 검증, attestation security level, authorization list, challenge와 attested SPKI 결속을 모두 검증한 경우에만 사용한다.

Production mapping은 다음을 문서화한다.

- `AndroidKeyStore`에서 device-local 생성하고 `PURPOSE_SIGN`, curve/digest/padding을 허용 교집합으로 제한한다.
- 가능한 경우 StrongBox를 요청하되 availability, resource/concurrency와 algorithm 제약을 다룬다.
- StrongBox 실패를 TEE 또는 software로 내릴지는 명시적 product policy, 목표 AL과 발급 profile로 결정하고 silent downgrade하지 않는다. 특히 software fallback은 GSPR O.2 Level 2 gate를 충족한다고 간주하지 않는다.
- local `KeyInfo` security level은 진단값이며 CA의 remote Evidence verdict를 대신하지 않는다.
- Android Key Attestation root set과 revocation status를 공식 source에서 갱신하고 RKP/legacy chain 차이를 처리한다.

그러나 다음 주장은 별도 증거 없이 성립하지 않는다.

- Android Keystore에 `K_tsu`가 있다는 사실만으로 TSA application 자체가 TEE에서 실행된다.
- Key Attestation의 `purpose=SIGN`만으로 RFC 3161 timestamp 전용성이 보장된다.
- package identity나 Play Integrity verdict만으로 TA measurement, trusted-time path 또는 subject-key binding이 증명된다.
- REE가 TSTInfo를 만들고 hardware key로 서명하는 구현이 On-Device TSA TEE requirement를 충족한다.

Play Integrity는 request hash/nonce에 결속된 app·deployment·device risk signal로 사용할 수 있지만 특정 `K_claim`/`K_tsu` possession attestation이 아니다. CP v0.2의 Play Integrity 세부 guidance도 아직 under development이므로 단독으로 AL2를 판정하지 않는다.

따라서 `K_tsu`의 dedicated TSA TA 내부 request parsing, time/serial/policy 결정과 전용 sign operation은 설계, TEE enforcement, conformance/negative test와 운영 audit로 보증해야 한다. Optional TSA attestation profile을 채택한 경우 Custom Compound Attestation을 추가 증거로 사용할 수 있다. Android Key Attestation 또는 Play Integrity는 그 optional compound evidence의 일부일 수 있지만 단독으로 runtime 적합성 전체를 증명하지 않는다.

### 9.4 다른 platform으로의 portability

Secure Enclave, keystore 또는 app-integrity service도 제품명이 아닌 capability 단위로 평가한다. Apple Secure Enclave와 App Attest를 예로 들면 별도 App Attest key의 app-instance attestation은 독립적으로 생성한 C2PA Claim key의 hardware possession 증명과 같지 않다. C2PA 2.4 허용 signature와 공개 hardware-backed API의 공통 경로로 P-256/ES256을 선택할 수 있지만, “Secure Enclave 전체가 P-256만 지원한다”거나 “Secure Enclave 사용=AL2”라고 일반화하지 않는다.

다음 질문에 각각 검증 가능한 증거가 있어야 한다.

1. 발급 대상 SPKI와 non-exportable private key가 결속되는가?
2. 누가 어떤 operation으로 key를 호출할 수 있는가?
3. C2PA Claim 또는 RFC 3161 timestamp 전용성을 어디서 강제하는가?
4. runtime/TA identity와 현재 security state를 어떤 설계·시험·운영 증거로 보증하며, optional remote attestation을 쓰면 signed scope가 무엇인가?
5. trusted-time, serial, activation과 rollback state가 같은 보호 경계에 있는가?

## 10. 오류, 관측성과 개인정보

### 10.1 오류 분류

| 범주 | 예 | Retry 원칙 |
|---|---|---|
| `INPUT_INVALID` | malformed Asset/CBOR/DER, unsupported format | 같은 입력 자동 retry 금지 |
| `POLICY_DENIED` | wrong product/environment/algorithm/caller | policy 변화 전 retry 금지 |
| `KEY_UNAVAILABLE` | invalidated/locked/mismatch/no active key | 새 key/activation 또는 사용자 action 필요 |
| `TIME_UNTRUSTED` | drift, rollback, source/leap failure | 검증된 resync/recovery 뒤만 |
| `STATUS_UNKNOWN` | stale/unknown/invalid OCSP·CRL/control | fresh authenticated source 뒤만 |
| `RESOURCE_EXHAUSTED` | size/rate/concurrency limit | bounded backoff; request 축소/격리 |
| `INTERNAL_INCONSISTENCY` | serial/receipt/job journal mismatch | 자동 재서명 금지, reconciliation/incident |

상위 API는 stable machine code와 stage를 반환하고 내부 parser/crypto 오류를 그대로 노출하지 않는다. 실패 의미는 다음처럼 명시한다.

| 의미 | 적용 | 결과 |
|---|---|---|
| `MANDATORY_FAIL_CLOSED` | key/caller, immutable input, Claim/assertion/binding/signature, embed/self-validation/commit 또는 profile이 필수화한 TSA | publication 금지; software fallback이나 silent downgrade 없음 |
| `DEGRADED_CONTINUE` | timestamp-optional profile에서 TSA outage/invalid timestamp | timestamp를 무시하고 `TIMESTAMP_PENDING`/명시적 no-timestamp 결과로만 진행; Trusted timestamp 표시 금지 |
| `OPTIONAL_SKIPPED` | 검증 완료 뒤의 optional external assertion payload, telemetry 등 | 핵심 Claim 판정을 바꾸지 않고 skip reason 기록 |

어떤 경로도 failure 또는 unknown 상태를 성공/Trusted로 정상화하지 않는다.

### 10.2 최소 audit event

| Event | 기록할 값 |
|---|---|
| Claim signing | random/scoped job ID, product/environment, scoped key·Leaf pseudonym, algorithm, result code |
| TSA request | scoped operation ID, hash OID, nonce 존재 여부, policy, result/failure; raw imprint/token digest 제외 |
| Time state | source/profile, attempt/success, uncertainty, leap version, state transition reason |
| Serial | namespace, reserved high-water mark, result; raw token content 제외 |
| Activation | scoped transaction/artifact pseudonym, counter, previous/result state, active-key count |
| Stop/recovery | status/provider/incident version, scoped affected-key pseudonym, acknowledgement |
| Final packaging | random job ID, self-validation result와 coarse commit result; raw path/content digest 제외 |

Audit time 자체가 RFC 3161 trusted time이라는 주장은 하지 않는다. Event는 monotonic sequence와 tamper-evident sink에 결속하고, device log loss/overflow가 security-critical operation을 숨기지 못하게 한다.

### 10.3 수집 금지와 redaction

- private key, key plaintext, keystore authentication secret, activation secret
- raw biometric/auth token
- full Asset, thumbnail, assertion payload 또는 user content
- 불필요한 IMEI, hardware serial, persistent cross-product device identifier
- raw Attestation Evidence, full certificate Subject/chain 또는 nonce를 일반 log/metric label에 기록하지 않는다.

Debug dump, crash report와 IPC tracing에도 같은 규칙을 적용한다. Operational metric은 coarse bucket과 stable error code만 사용한다. 필요한 correlation은 rotation되는 secret으로 만든 keyed pseudonym 또는 random job ID를 사용한다. Exact content/request/token digest나 Asset locator가 security audit 또는 durable retry에 꼭 필요하면 목적, 전용 encrypted vault, ACL, scope와 retention/purge를 별도로 승인하고 일반 log·metric으로 내보내지 않는다. 세부 보존·접근·삭제는 04의 privacy policy에 연결한다.

### 10.4 Runtime SLI

Provider acceptance와 운영에서 최소 다음을 관측한다.

- Claim/TST latency·success/failure와 stage별 rate
- parser rejection, caller denial, key invalidation과 SPKI mismatch
- last time sync attempt/success age, uncertainty/drift와 `TIME_UNTRUSTED` duration
- leap bulletin version/age와 next event readiness
- status/control freshness와 rollback rejection
- active-key count, activation receipt age와 `RECOVERY_REQUIRED`
- serial reservation gap, rollback/duplicate suspicion
- self-validation failure와 partial-file cleanup backlog

Certificate serial, device identifier, content-derived digest, path/locator 또는 nonce를 high-cardinality metric label로 사용하지 않는다.

## 11. Provider acceptance evidence와 시험

### 11.1 필수 evidence package

| Evidence | 최소 내용 |
|---|---|
| Architecture | component/privilege/IPC/data-flow, key와 state 위치, threat mapping |
| Build identity | production binary/TA/TEE/firmware version, signing identity, SBOM/SCA와 patch policy |
| GSPR mapping | implementation class, 목표 AL, O.2~O.5 requirement별 static/dynamic evidence와 negative test |
| Key controls | generation, SPKI binding, non-export, caller ACL, purpose separation, invalidation/rotation |
| Protocol | C2PA 2.4/COSE/RFC 3161 known-answer와 외부 implementation interoperability |
| Trusted time | UTC(k) trace, accuracy budget, drift/holdover, 24h attempt, leap handling |
| Persistence | serial, key state, time/status, activation counter의 crash/rollback evidence |
| Fault testing | power loss, reboot, storage corruption, concurrency, IPC fuzz와 source outage |
| Lifecycle | staged activation, single-active, re-key, revoke/compromise/cessation acknowledgement |
| Privacy/operations | log schema/redaction, retention, monitoring, recovery와 residual risk |

### 11.2 Claim/Manifest test catalog

최소 다음을 positive/negative/boundary vector로 실행한다.

- `RT-TEST-CM-01`: deterministic Claim CBOR과 assertion URI/hash exactness
- `RT-TEST-CM-02`: required·version-unique/XMP-derived `instanceID`, generator `name`/absolute signature URI, same-store assertion reference, standard-manifest exactly-one created/opened action·0/1 parent, de novo first `c2pa.created`/`digitalSourceType`, parent first `c2pa.opened`, opened-only resave의 `allActionsIncluded=true`
- `RT-TEST-CM-03`: `c2pa.hash.data` zero pad, ordered/non-overlap/allowed exclusion, format별 exclusion range와 decoder-semantics 변경, cloud/external 배치와 compressed-manifest 병용 거부
- `RT-TEST-CM-04`: immutable snapshot에서 parse/hash/embed가 완료됨을 확인하고 path/symlink/content-provider swap, same-size overwrite, truncate/rename, hash 중 mutation과 crash 시 old-or-new atomicity 검증
- `RT-TEST-CM-05`: ingredient embedded/remote/malformed/collision/lineage copy/`activeManifest`+`claimSignature`, activeManifest 유무별 `validationResults`, empty/non-empty `ingredientDeltas`와 entry별 `ingredientAssertionURI`/`validationDeltas` 처리
- `RT-TEST-CM-06`: category별 no-consent total outbound 0; consent+initial manifest/ingredient discovery는 bounded 1회, rejected Claim 뒤 child/icon/external follow-on 0; non-allowlisted endpoint 0, optional fetch 실패 비전파와 relay consent/disclosure
- `RT-TEST-CM-06A`: outer-hash 없는 remote manifest의 sandboxed internal validation, hashed data의 missing/unknown alg·wrong declared size/present `dc:format` 대비 Content-Type/hash·redirect content swap 폐기, external absent-format content-type success, cloud absent-format=`application/jumbf`와 deprecated `content_type` 무시, unhashed external advisory 처리
- `RT-TEST-CM-07`: soft-binding schema/padding/algorithm, discovery metadata와 all-assertion match; soft binding만으로 hard-binding 성공을 만들지 않음
- `RT-TEST-CM-08`: COSE detached payload의 `nil`과 in-memory Sig_structure payload 차이
- `RT-TEST-CM-09`: allowed/unknown/mismatched algorithm과 wrong key/curve/size, ECDSA DER 대 raw `R || S`
- `RT-TEST-CM-10`: `x5chain` single-bstr/array, order, missing intermediate, included root, label 33/string, protected/unprotected와 중복 credential
- `RT-TEST-CM-11`: unauthorized caller, debug build, wrong environment, key invalidation과 software fallback 거부
- `RT-TEST-CM-12`: timestamp absent/pending 정책과 timestamp failure 뒤 silent downgrade 거부
- `RT-TEST-CM-13`: delayed `c2pa.time-stamp` update manifest의 exactly-one parent ingredient, target manifest binding, assertion map schema와 금지 assertion
- `RT-TEST-CM-14`: final embed 뒤 독립 C2PA 2.4 validation과 atomic file commit
- `RT-TEST-CM-15`: job/queue response loss·reboot·duplicate delivery·lease expiry, same-ID/same-digest replay와 same-ID/different-digest conflict, 다른 caller/product/environment/key scope replay의 결과 비노출, TTL/quota/purge
- `RT-TEST-CM-16`: GSPR AL2 auditor-only enrollment 거부와 instance-bound hardware possession artifact, Distributed/Backend mutual-auth·role denial, O.5 L2 UID/IPC ACL isolation evidence
- `RT-TEST-TCB-01`: unapproved/corrupted Generator·snapshot manager·final validator image, missing/stale hardware artifact, memory/IPC isolation failure와 self-validator bypass 각각에서 `CLAIM_READY=false`, key invocation/commit 0, stable stop·incident event를 검증

### 11.3 RFC 3161/TSA test catalog

- `RT-TEST-TSA-01`: C2PA v2 `CounterSignature` exact bytes와 CBOR `bstr` length 포함 여부
- `RT-TEST-TSA-02`: SHA-256/384/512 positive와 wrong OID/length/unknown algorithm
- `RT-TEST-TSA-03`: production nonce present/mismatch/replay/absent와 bounded response age, request policy present exact-match/mismatch, request policy absent+default allowlist accept/reject
- `RT-TEST-TSA-04`: `certReq=true/false`, signer certificate/intermediate 누락과 ESSCertIDv2 mismatch
- `RT-TEST-TSA-05`: success/failure status와 token presence의 모든 잘못된 조합
- `RT-TEST-TSA-06`: TSTInfo v1, policy, MessageImprint, UTC GeneralizedTime, required accuracy absent/invalid/mismatch, ordering과 optional field
- `RT-TEST-TSA-07`: CMS `eContentType` missing/wrong, C2PA allowed/deprecated/unknown signature algorithm과 발급 profile mismatch
- `RT-TEST-TSA-08`: TSA Leaf wrong/missing/non-critical/extra EKU, wrong KU/purpose, Claim Leaf 대입과 separate trust-path 실패
- `RT-TEST-TSA-09`: serial concurrency, crash-before/after-sign, reboot/rollback, namespace collision과 exhaustion
- `RT-TEST-TSA-10`: arbitrary sign, REE-built TSTInfo sign, second active key와 staged key 사용 거부
- `RT-TEST-TSA-11`: C2PA TSA Trust List와 Claim trust store를 바꿔 끼우는 negative vector

### 11.4 Trusted-time·activation·incident fault catalog

- `RT-TEST-LC-01`: 마지막 online sync 시도 `24h-epsilon`, 정확히 경계와 `24h+epsilon`
- `RT-TEST-LC-02`: successful sync age, status age, uncertainty/accuracy deadline 중 가장 이른 cutoff
- `RT-TEST-LC-03`: backward/forward wall-clock 변경, monotonic reset과 sealed-state rollback
- `RT-TEST-LC-04`: source signature/nonce/path/freshness 실패, network outage와 captive/MITM 입력
- `RT-TEST-LC-05`: leap bulletin 정상/stale/replay/superseded/cancelled/wrong-authority 및 step/smear mismatch
- `RT-TEST-LC-06`: event 중 reboot, source switch, holdover exhaustion과 recovery
- `RT-TEST-LC-07`: activation wrong signer/audience/service/TSU/key/certificate/environment/version/time/counter
- `RT-TEST-LC-08`: concurrent activation, authorization/receipt/finalization response loss와 durable retry
- `RT-TEST-LC-09`: key compromise의 과거/현재 token 일괄 불신과 replacement-key 비복구
- `RT-TEST-LC-10`: cessation reason `0/3/4/5`, absent, `1`, unknown과 `genTime == revocationTime` 경계

### 11.5 Fuzzing과 resource limit

CBOR/COSE/JUMBF, Asset format parser, ASN.1 DER/CMS/RFC 3161과 IPC framing에 coverage-guided fuzzing을 적용한다. Provider profile은 최대 request/Asset/Manifest/assertion/certificate-chain 크기, compressed/uncompressed absolute bytes와 ratio, nesting depth, item/certificate 수, ingredient graph node/edge·aggregate bytes, redirect/fetch aggregate, file descriptor/TEE session, concurrent job, CPU/time budget과 rate를 수치화한다.

Malformed input에서 다음을 입증한다.

- `RT-TEST-FZ-01`: crash, panic, out-of-bounds, unbounded allocation/recursion 또는 TEE reset이 없다.
- `RT-TEST-FZ-02`: 실패 request가 serial, activation, time high-water mark를 rollback하지 않는다.
- `RT-TEST-FZ-03`: parser error가 raw input/secret을 log하지 않는다.
- `RT-TEST-FZ-04`: 한 product/TSU의 고갈이 다른 scope의 availability를 침해하지 않는다.
- `RT-TEST-FZ-05`: timeout/cancel/peer death 뒤 memory, file descriptor, network connection, lease와 TEE session이 deadline 안에 회수된다.
- `RT-TEST-FZ-06`: fixture의 PII/path/GPS/name/content hash가 log, metric, crash dump와 승인되지 않은 queue field에 나타나지 않는다.
- `RT-TEST-FZ-07`: profile의 각 size/ratio/depth/count/redirect/aggregate/CPU/session limit에 대해 `N-1/N/N+1`을 실행한다. Envelope/header에서 사전 판정 가능한 size 초과는 parser invocation 0이다. 구조 처리 중 발견하는 초과는 streaming/bounded validation parse가 threshold까지만 진행하고 이후 semantic materialization, child fetch, crypto/sign과 downstream application parse가 0이다. 모든 초과는 peak byte/CPU/read bound, stable `RESOURCE_EXHAUSTED`와 cleanup deadline을 만족한다. Decompression bomb, redirect loop, ingredient fan-out, oversized certificate chain과 nested graph fixture를 포함한다.

### 11.6 Acceptance 판정

Provider/runtime version은 다음을 모두 만족해야 `ACCEPTED`다.

```text
source-pinned requirement mapping complete
AND static architecture/build/key evidence approved
AND known-answer + negative + interoperability PASS
AND rollback/concurrency/power-loss/fuzz evidence PASS
AND residual risk explicitly accepted by owner
AND all OPEN production blockers resolved
```

`PASS_WITH_EXCEPTION`으로 C2PA/RFC 필수, private-key confinement, exact signing input, declared-accuracy drift-stop, single-active key, serial uniqueness 또는 activation anti-rollback을 우회하지 않는다.

## 12. Runtime 불변조건과 미결정 register

### 12.1 불변조건

| ID | 불변조건 |
|---|---|
| `RT-SCOPE-01` | 정상 Claim/TST signing은 Certificate Platform signing endpoint를 경유하지 않는다. |
| `RT-KEY-01` | `K_claim`과 `K_tsu`는 다른 key·Leaf·purpose·authorization domain이다. |
| `RT-KEY-02` | `K_tsu`는 TEE에서 생성·보관되고 RFC 3161 token 이외의 서명을 하지 않는다. |
| `RT-CLAIM-01` | Claim signature input은 deterministic Claim bytes를 payload로 한 C2PA COSE `Sig_structure`다. |
| `RT-CLAIM-02` | Asset/assertion의 signed snapshot과 최종 embedded Asset 사이 TOCTOU가 없어야 한다. |
| `RT-TCB-01` | 승인 Generator/snapshot/validator TCB의 image·isolation 무결성을 증명하지 못하면 그 self-check를 신뢰하지 않고 신규 signing/publication을 중단한다. |
| `RT-CRED-01` | 신규 `x5chain`은 protected integer 33에 Leaf+모든 intermediate 순서로 넣고 root를 제외한다. |
| `RT-TST-01` | v2 MessageImprint는 `COSE_Sign1_Tagged.signature`의 serialized `bstr`를 포함한 CounterSignature `ToBeSigned` hash다. |
| `RT-TST-02` | Requester는 status, allowed signature algorithm, TSA-only critical EKU/path, ESS binding, eContentType, imprint, nonce/policy/response age, required accuracy와 `genTime`을 검증한 token만 `sigTst2`에 넣는다. |
| `RT-TIME-01` | declared accuracy를 보장하지 못하면 TSU는 신규 TimeStampToken 발급을 중단한다. |
| `RT-SERIAL-01` | service-wide serial uniqueness는 crash, concurrency, rollback과 key rotation 뒤에도 유지된다. |
| `RT-ACT-01` | 한 TSU에는 정확히 하나의 `SIGNING_ACTIVE` key만 있고 server state를 device state로 간주하지 않는다. |
| `RT-ACT-02` | 새 `K_tsu`는 signed finalization을 검증하기 전에는 signing에 사용할 수 없다. |
| `RT-FAIL-01` | mandatory predicate의 unknown/stale/rollback/mismatch는 software fallback이나 silent downgrade 없이 fail-closed한다. Optional/degraded 경로도 실패를 Trusted로 표시하지 않는다. |
| `RT-IR-01` | TSA key compromise는 해당 key의 모든 token을 `genTime`과 무관하게 불신하고 replacement key로 복구하지 않는다. |
| `RT-PRV-01` | private key, content, raw Evidence와 불필요한 device identifier를 log/metric에 기록하지 않는다. |

### 12.2 Production 전 미결정 항목

| ID | 결정할 내용 | Owner | 미결정 시 |
|---|---|---|---|
| `OPEN-RT-FMT-01` | 대상 Asset format, streaming/multiple-step binding과 atomic commit 구현 | Generator Product Owner | 해당 format acceptance 금지 |
| `OPEN-RT-INPUT-01` | platform별 immutable input generation/snapshot primitive와 same-size mutation detection | Generator Product/Platform Owner | Claim signing acceptance 금지 |
| `OPEN-RT-02` | `K_claim`별 platform ACL/caller identity와 supported COSE algorithm | Product Security/Provider | Claim signing acceptance 금지 |
| `OPEN-RT-03` | TSA TA IPC schema, limit, error mapping과 idempotency | TSA/Provider Owner | TSA acceptance 금지 |
| `OPEN-RT-JOB-01` | Claim/queue canonical request digest, CAS lease, TTL/quota, durable result와 purge schema | Runtime/Storage Owner | offline·retry acceptance 금지 |
| `OPEN-RT-TIME-01` | 04 `OPEN-TIME-01`을 소비하여 device time source, declared accuracy, sync/status max-age와 offline cutoff 확정 | TSA/CPS/Provider Owner | TSA activation 금지 |
| `OPEN-RT-SERIAL-01` | serial namespace bit layout, allocation, counter primitive와 exhaustion | TSA/Certificate Platform Owner | TSA activation 금지 |
| `OPEN-RT-ACT-01` | 04 `OPEN-ACT-01` artifact를 소비하는 deterministic decoder, local counter/TTL와 recovery 확정 | Activation/Runtime Owner | staged activation 금지 |
| `OPEN-RT-IR-01` | 04 `OPEN-IR-01` handoff의 device transport, cache index와 acknowledgement SLO 확정 | Incident/Validator Owner | production TSA release 금지 |
| `OPEN-RT-PRV-01` | 04 `OPEN-PRV-01`에 따라 device audit/queue의 exact digest·locator 목적, vault/ACL, retention·redaction·deletion 확정 | Privacy/CPS Owner | raw 저장 금지, release 차단 |

## 13. 근거 locator

### 13.1 C2PA 2.4

- Technical overview and example: §1.3, `#_technical_overview`
- Assertion Store and hashed URI: §6.6, §8.4.2, `#_assertion_store`, `#_hashed_uris`
- Assertion redaction and cloud/external data retrieval: §6.8, §15.10.4, §18.11, §18.24, `#_redaction_of_assertions`, `#_external_data_validation`, `#_cloud_data`, `#_external_reference`
- Hard/soft bindings: §9, `#_binding_to_content`, `#_hard_bindings`, `#_soft_bindings`
- Claim creation/signing/time-stamp/multiple-step: §10.3~10.4, `#_creating_a_claim`, `#_signing_a_claim`, `#_time_stamps`, `#_multiple_step_processing`
- Manifest Store/types/embedding: §11.1~11.3, `#_c2pa_box_details`, `#_types_of_manifests`
- Update manifest and later timestamp: §11.2.3, §18.18, `#_update_manifests`, `#_time_stamps_2`
- Hash/signature algorithms and COSE: §13.1~13.2, `#_hashing`, `#_digital_signatures`
- Identity/validation state/X.509: §14.2~14.5, `#_identity_of_signers`, `#_validation_states`, `#x509_certificates`
- Claim/signature/timestamp/assertion/ingredient/content validation: §15.6~15.12, `#validating_the_claim`, `#_validate_the_signature`, `#_validate_the_time_stamp`, `#_validate_the_assertions`, `#_validate_the_ingredients`, `#_validate_the_assets_content`
- Data hash, soft binding, actions, ingredient, later timestamp: §18.5, §18.10, §18.15, §18.16, §18.18
- Official rendered source: <https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html>
- Pinned source: <https://github.com/c2pa-org/specifications/blob/d776ab5a8627f8f5ac2f7f4f3aa20ab12783a878/build/site/specifications/2.4/specs/C2PA_Specification.html>
- Security Considerations 2.4 remote access/resource/ingredient guidance: §4.2.2.4, §4.3.3, §4.3.4, <https://spec.c2pa.org/specifications/specifications/2.4/security/Security_Considerations.html>
- Pinned Security Considerations: <https://github.com/c2pa-org/specifications/blob/d776ab5a8627f8f5ac2f7f4f3aa20ab12783a878/build/site/specifications/2.4/security/Security_Considerations.html>

### 13.2 Conformance·TSA·platform

- C2PA CP v0.2, General/On-Device TSA와 platform guidance: <https://github.com/c2pa-org/conformance-public/blob/722b639fd140871eb8b8ff0322f2f6e0538dd50a/docs/v0.2/C2PA%20Certificate%20Policy.md>
- GSPR v0.2 O.2~O.5: <https://github.com/c2pa-org/conformance-public/blob/722b639fd140871eb8b8ff0322f2f6e0538dd50a/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md>
- RFC 3161 requester/TSA/token and operational security: §2.2~2.4, §4, <https://www.rfc-editor.org/rfc/rfc3161>
- RFC 5816 ESSCertIDv2/SigningCertificateV2: <https://www.rfc-editor.org/rfc/rfc5816>
- Android Keystore: <https://developer.android.com/privacy-and-security/keystore>
- Android Key Attestation: <https://developer.android.com/privacy-and-security/security-key-attestation>
- Android attestation schema: <https://source.android.com/docs/security/features/keystore/attestation>
- Play Integrity: <https://developer.android.com/google/play/integrity/overview>
- Apple Secure Enclave key protection: <https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave>
- Apple App Attest: <https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity>
- Provider 공식 문서 확인일: 2026-08-31 KST

CP v0.2의 Android 표는 `bootPatchLevel` tag를 718로 표기하지만 Android 공식 ASN.1 schema는 `vendorPatchLevel=718`, `bootPatchLevel=719`로 정의한다. Parser는 공식 schema의 719를 사용하고 이 upstream 불일치를 conformance clarification으로 추적한다.

## 14. 완료 기준

이 문서는 다음 조건을 만족할 때 구현 가능한 상세 설계로 완료된다.

1. 모든 `C2PA-REQUIRED`, `RFC-REQUIRED`와 강화 통제에 source locator와 test ID가 연결된다.
2. `OPEN-*`가 승인된 CPS/provider/runtime contract의 실제 값으로 닫힌다.
3. Claim/TSA private key가 목적별 경계를 벗어나지 않고 normal runtime에 server signing API가 없음을 증명한다.
4. C2PA 2.4 Claim, v2 `sigTst2`와 RFC 3161 known-answer가 최소 두 독립 implementation과 상호운용된다.
5. malformed/replay/rollback/concurrency/power-loss/time/status/activation negative test가 fail-closed한다.
6. drift, leap, serial, rotation, revocation과 compromise의 중단·복구·acknowledgement evidence가 재현 가능하다.
7. final Asset의 independent validation, atomic commit, audit redaction과 cleanup이 통과한다.
8. 승인 provider/version의 잔여 위험과 운영 owner가 기록되고 05 release gate에 연결된다.

이 조건의 충족은 외부 runtime acceptance를 뜻하며 Certificate Platform의 제품 경계나 납품 범위를 확장하지 않는다.

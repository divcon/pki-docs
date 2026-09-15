# Independent Audit Resolution

§1~§7은 2026-09-04 문서 작성 당시의 감사 계약·기록이다. 2026-09-11 Android 보강 감사는 §8, 2026-09-15 CSR/Key Attestation 필수 입력 감사는 §9에 별도로 기록하며, 과거 감사 결과를 현재 보강본의 통과 근거로 재사용하지 않는다.

## 1. Audit contract

메인 에이전트만 artifact를 수정한다. Standards, Enrollment/security, Coverage/consistency 감사자는 read-only이며 서로의 verdict를 근거로 사용하지 않는다. 각 round는 같은 allowlist, pinned source identity와 manifest SHA-256인 snapshot ID를 받는다. 감사 중 대상 파일과 ZIP을 변경하지 않고 결과 회수 뒤 같은 manifest를 재계산한다.

Finding은 severity, 정확한 target locator, `EXTERNAL-NORMATIVE`/`PROJECT-CONTRACT`/`MECHANICAL` basis, 재현 설명과 최소 수정 방향을 포함해야 한다.

## 2. Pre-edit ownership baseline

프로젝트 root는 Git repository가 아니므로 `/tmp/claim-signing-enrollment-pre-edit-baseline.txt`에 2026-09-04 15:05 KST path inventory와 SHA-256을 기록했다.

| path | pre-edit SHA-256 / state |
|---|---|
| `architecture/Overview.md` | `dc4b993204e98736f9a8006f2aeb9dc57531233c7035161ca17e80a01c022e15` |
| `architecture/01-Architecture-Foundation.md` | `be51b7c0861da3fa911c310bbe9ef9d387a0e1fe57e516da9f71cd8a868e3589` |
| `architecture/02-Certificate-Enrollment.md` | `da120340f25d255d23b8d2c17c4acbf3bbd55286e1228b8edfc3744150e8adf6` |
| `architecture/03-On-Device-Runtime.md` | `5431ab26f0e55d5a8855f9abe481f3023ae817dfc03858d0fbbe26318807f3d0` |
| `architecture/04-Security-and-Operations.md` | `3d0b5ce95a9621eae1f80159cf98f4b1eb4e5f1a1b39ba11aa0951d0ad55074f` |
| `architecture/05-Conformance-and-Roadmap.md` | `3b3e1d5fb0f808d26a317a1190d3e50f5c7318def402fbbb3e06159a19bb5089` |
| 신규 folder 5개 / ZIP | absent |

Appendix/부록은 내용을 열지 않았고 제외 path name inventory만 비교한다. `conformance-public`은 working tree가 아니라 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc` blob을 사용하며, `specifications`는 commit `9c58c8c27044e44e8601f6ab13f1bcac1376eb1f`다. 두 source repository는 수정하지 않는다.

## 3. User-directed scope correction

2026-09-04 KST에 사용자가 일반 API 설계가 필요 없다고 명확히 지시했다. 이에 따라 goal control document와 산출물 범위를 다음처럼 교정했다.

| scope item | current disposition |
|---|---|
| 인증 방식과 enrollment requirement | 유지·강화 |
| Enrollment request body field/format/cardinality | 유지 |
| HTTP endpoint와 URL | 제거 |
| Response schema | 제거 |
| Transaction/state machine | 제거 |
| Idempotency, retry와 stable error model | 제거 |
| API Explicit Validation Matrix | 제거하고 `Enrollment Request Body Matrix`로 교체 |

Scope 변경 전 snapshot의 API 설계 finding은 현재 계약의 미해결 finding으로 사용하지 않는다. 다만 외부 규범 정확성이나 인증·enrollment 보안에 직접 관련된 finding은 아래처럼 새 범위에 반영했다.

## 4. Artifact allowlist

| kind | path | status |
|---|---|---|
| control modified | `architecture/tmp/claim-signing-enrollment-goal-prompt.md` | API contract/matrix 요구 제거, request-body-only 범위로 수정 |
| new | `architecture/claim-signing-enrollment-request/README.md` | created |
| new | `architecture/claim-signing-enrollment-request/01-Enrollment-Request-Body.md` | created; prior API-contract file removed |
| new | `architecture/claim-signing-enrollment-request/02-CSR-and-Dynamic-Evidence-Requirements.md` | created |
| new | `architecture/claim-signing-enrollment-request/03-Server-Validation-Traceability-and-Gaps.md` | created |
| new | `architecture/claim-signing-enrollment-request/04-Subagent-Audit-Resolution.md` | created |
| existing modified | `architecture/Overview.md` | Claim enrollment terminology/evidence/source consistency only |
| existing modified | `architecture/01-Architecture-Foundation.md` | underdefined public-key identity assertion changed to fail-closed decision |
| existing modified | `architecture/02-Certificate-Enrollment.md` | Claim enrollment source/evidence consistency only |
| existing modified | `architecture/04-Security-and-Operations.md` | underdefined public-key identity assertion changed to fail-closed decision |
| package | `architecture/claim-signing-enrollment-request.zip` | exactly five new Markdown files |

`architecture/03-On-Device-Runtime.md`와 `05-Conformance-and-Roadmap.md` retain baseline hashes and are consistency inputs only.

## 5. Audit round register

| round | snapshot ID | result / status |
|---|---|---|
| Coordinator preflight | N/A | baseline, source identity와 exclusions fixed |
| Pre-scope round 1 | `f5d18e36fe358cfcf58c3ab8e07dbce7066ac9ae204b1b2a92608b474935380b` | 24 findings; old API-heavy contract에 대한 round이므로 final evidence로 사용하지 않음 |
| Pre-scope round 2 | `86a7254e8fee935351643dbcc0c25cea422077af3d7c3591cc4daa13a6fd1749` | 22 findings; 사용자 scope correction으로 superseded, 관련 normative/security finding만 §6에 이관 |
| Scope-reset round 1 | `8162b90ad69e9ad78775e2cbc1d5a16277fe4b20d3a599846c77ed3b57b71ad3` | Standards 3, Enrollment/security 3, Coverage 5 reports; 중복을 합친 8개 finding을 §6에서 수정. 변경 전 snapshot이므로 final closure evidence가 아님 |

최종 무지적 감사의 세 verdict와 unchanged snapshot ID는 감사 뒤 파일을 다시 바꾸지 않도록 최종 응답에만 기록한다.

## 6. Scope-reset resolution register

| ID / basis | validation | applied correction | closure |
|---|---|---|---|
| `SCOPE-01` / `PROJECT-CONTRACT` | 목표와 산출물이 endpoint·state·idempotency까지 확장됐음을 확인 | goal에서 API contract/matrix 삭제; 01을 request-body-only 문서로 교체 | 신규 문서 forbidden-scope 검색으로 검증 |
| `SCOPE-02` / `PROJECT-CONTRACT` | 인증이 단일 login처럼 읽히면 I/A/V, Agreement, GP instance, PoP와 attestation을 혼동 | 여섯 인증 predicate와 적용 시점/body 포함 여부를 분리 | README/01/03 cross-check |
| `SCOPE-03` / `EXTERNAL-NORMATIVE` | CP:10-12와 CP:1518-1558에서 pre-issuance Agreement는 uppercase BCP 14가 아님 | `NON-BCP14-OBLIGATION`으로 분류하고 CP:531-535 post-issuance acceptance `REQUIRED`와 분리 | source/modality 검색 `PASS/CLOSED` |
| `SCOPE-04` / `PROJECT-CONTRACT` | C2PA가 same-key 금지를 정하지만 cross-encoding identity algorithm은 정하지 않음 | 이전 custom normalized-key algorithm을 철회하고 `OD-KEY-01 TBD`; 승인 전 Claim/TSA issuance 전부 disabled | 01/02/03/Overview 검색 `PASS/CLOSED` |
| `SCOPE-05` / `EXTERNAL-NORMATIVE` | Certificate profile의 uppercase와 descriptive lowercase 문장을 한 modality로 묶을 수 없음 | field별 `REQUIRED/RECOMMENDED/PERMITTED`와 `NON-BCP14-OBLIGATION` 구분 유지 | 02 profile table과 traceability 검사 |
| `SCOPE-06` / `PROJECT-CONTRACT` | AL2 provider artifact count와 JSON wrapper count가 혼동될 수 있음 | C2PA count `NOT-SPECIFIED`, provider `PROVIDER-PROFILE-DEFINED`, project `1..N_p`를 별도 열로 유지 | 6-combination matrix 검사 |
| `SCOPE-07` / `PROJECT-CONTRACT` | Request body에 onboarding 원자료나 client 판정값이 복제될 수 있음 | body는 CPL reference, CSR와 조건부 Evidence만 최소화하고 authority state는 SG gate로 분리 | RB/SG traceability 검사 |
| `SCOPE-08` / `PROJECT-CONTRACT` | README에 discovery, transaction과 stable error 의미가 잔존 | profile enablement, unsupported RENEWAL body와 별도 명시적 AL1 request만 남김 | current-scope forbidden semantics 검색 |
| `SCOPE-09` / `PROJECT-CONTRACT` | Overview의 공용 enrollment API 표가 Claim profile을 포함 | 해당 절을 TSA-only로 한정하고 Claim profile row·API/state 서술을 제거; Claim은 인증 요구사항과 request body로만 연결 | Overview section/profile 검색 |
| `SEC-01` / `PROJECT-CONTRACT` | signed envelope 분기가 stale underlying attestation을 fresh하게 만들 수 있었음 | 모든 AL2 분기에 trusted freshness와 request-context/audience/key binding, replay identity를 함께 요구 | stale-artifact negative predicate 검색 |
| `TRACE-01` / `EXTERNAL-NORMATIVE` | AL2 GP instance locator가 table header에서 끝남 | AL1 `CP:1686-1695`, AL2 `CP:1712-1714`로 분리 | pinned CP line 확인 |
| `TRACE-02` / `PROJECT-CONTRACT` | AL1 GP 인증 timing에 미정의 `credential` 분류 사용 | 정의된 `WIRE + ISSUANCE-GATE`로 정정 | timing vocabulary 검사 |
| `TRACE-03` / `PROJECT-CONTRACT` | REKEY-only lifecycle과 AL2-only downgrade decision이 mixed row에 무조건 적용됨 | `[REKEY]`/`[AL2]` qualifier를 양방향 map에 추가하고 INITIAL body 의미는 승인된 `OD-BODY-01`에 귀속 | qualifier와 blocking-set 대조 |
| `TRACE-04` / `PROJECT-CONTRACT` | `OD-BODY-01` 및 `OD-CPL-01`의 선언 범위와 enforcement map 불일치 | 모든 RB field/cardinality 및 관련 SG에 body decision을 연결하고 CPL의 `RB-02` 관계를 양방향 추가 | decision↔RB/SG exact relation 검사 |
| `TRACE-05` / `EXTERNAL-NORMATIVE` | UUIDv7 및 CSR profile field의 직접 schema locator 누락 | `CPL schema:11-14`, `AL1/AL2 CSR:1051-1179`와 `683-1336` 추가 | pinned schema line 확인 |

## 7. Snapshot closure procedure

1. 모든 Markdown patch와 allowlist를 확정한다.
2. 정확히 다섯 신규 Markdown을 ZIP으로 생성하고 각 entry를 byte-compare한다.
3. Link/anchor, AL×operation/cardinality, decision↔RB/SG/RT, TBD fail-closed와 forbidden API-scope 검사를 수행한다.
4. Artifact와 pinned source identity를 정렬한 manifest의 SHA-256을 snapshot ID로 사용한다.
5. 같은 snapshot을 세 독립 read-only 감사자에게 제공하고 대상 파일을 freeze한다.
6. 결과 회수 뒤 manifest가 같지 않으면 verdict 전체를 폐기한다.
7. 유효 finding이 있으면 수정·기록·ZIP 재생성 뒤 새 snapshot에서 세 감사를 모두 반복한다.
8. 같은 최종 snapshot에서 세 감사자가 정확히 `NO FINDINGS`를 반환할 때만 완료한다.

## 8. 2026-09-11 Android provider 보강 감사

사용자는 Google/Android Key Attestation 확장을 provider로 지정하고, O.1~O.4 필드 매핑 누락을 서브에이전트가 다시 감사한 뒤 필요한 문서를 보강하도록 요청했다. Standards, Enrollment/security, Coverage/consistency의 세 독립 read-only 감사자가 동일한 수정 전 5개 문서와 고정 CP·Google/AOSP 원문을 대조했다. 세 감사 모두 누락을 확인했다. 이는 운영이 `DISABLED`인 구현 문서의 누락이며 실행 중인 서버의 취약점 발견을 뜻하지 않는다.

이번 변경 범위는 이 폴더의 5개 Markdown과 대응 ZIP이다. 변경 전 사본과 기계적 검증 도구·manifest는 `/tmp/c2pa-android-attestation-audit.oVzNcx/`에 보관했다. 수정 전 snapshot은 `bb355c9aaa235f44efdb245a85d5d6e3e76fa8de567f91d17fdc7d62e477da7c`이며 ZIP의 5개 entry와 문서 bytes가 일치함을 확인했다. CP commit과 기존 provider 원문 SHA-256은 README §6과 같고 원문 repository는 수정하지 않았다.

### 8.1 중복을 합친 findings와 보강

| ID / severity | 독립 감사 finding | source / 보강 위치 | 처리 |
|---|---|---|---|
| `ANDROID-AUDIT-01` / High | Android 필드 매핑 전체 누락; 이미 있는 가이드까지 일괄 TBD로 분류 | CP:1796-1816; 02 §13.1~13.2, README, 03 decisions/gaps | 21개 행·분류·값·locator를 추가하고 provider 선택과 운영 승인을 구분 |
| `ANDROID-AUDIT-02` / High | root-nearest 확장 선택과 선택 인증서→CSR 공개키 결속 누락 | Google `#verifying`; 01 §5.4, 02 §13.3 | `.17/.30` 위치 규칙, signed DER 인증서/체인 포장, 키 일치와 별도 PoP 명시 |
| `ANDROID-AUDIT-03` / High | softwareEnforced의 신뢰 전제와 shared UID·signer 집합 처리 누락 | AOSP `#keydescription-fields/#attestationapplicationid-schema`; 02 §13.3 | locked/Verified 조건, 전체 승인 package/version/signer 집합, 인증서 digest 의미 명시 |
| `ANDROID-AUDIT-04` / Medium | provider root/status 갱신 및 factory/RKP 유효기간 구분 누락 | Google `#root_certificate/#certificate_status/#expired_factory_keys`; 02 §13.3, OD-EVIDENCE/REVOCATION | root registry·체인 상태·캐시 검증과 예외 적용 범위를 명시, 운영값은 TBD 유지 |
| `ANDROID-AUDIT-05` / Medium | challenge 생성 시점과 요청 범위 결속 불명확 | CP:1768,1798; Android Builder; 01 §7, 02 §13.3 | 생성 전 challenge→새 키→CSR 의존, 128-byte provider 상한, CA context 및 미정 TTL 구분 |
| `ANDROID-AUDIT-06` / High | 필드 통과와 O.3/O.4 전체 component/revision 판정 사이 연결 누락 | CP:1720-1751,1766; 02 §13.4, OD-REFERENCE | 기존 전체 coverage 요구를 유지하고 검증된 release와 승인 inventory·취약점 조치의 연결 및 부족 시 거부 명시 |
| `ANDROID-AUDIT-07` / Medium | CP 태그 오기·버전/이름 차이·패치 월 경계 미처리 | CP:1797,1799-1801,1811,1816; AOSP; 02 §13.2, GAP-ANDROID-01/02 | boot `[719]`, version별 parser, 필수값 부재 거부, 예시 기반 월 해석안과 승인 경계 기록 |
| `ANDROID-AUDIT-08` / Medium | Android source→field→gate 및 decision 역방향 연결 누락 | CP Android/Google/AOSP; 03 §2~§3, §6.2 | REQ-AL2/ANDROID와 SG-06 연결, SOURCE/ALG 양방향 갱신 및 검증 반례 추가 |

위 처리는 문서 보강 내용을 기록한다. 02 §13.5의 암호·provider 반례는 향후 구현 검증 조건이며 이번 작업에서 실행한 verifier 테스트로 세지 않는다. Source 규칙과 제품별 미정 운영값을 구분하고 REST API, transaction/state 또는 retry 설계는 추가하지 않는다. `APPROVED` 3개 / `TBD` 14개 및 AL1/AL2 운영 발급 `DISABLED`를 유지한다.

### 8.2 보강본 재감사 절차

보강본의 local link/anchor, CP 21행 누락, 17개 decision 상태와 AL별 비활성 조건, ZIP entry/byte 일치를 기계적으로 확인하고 source/artifact SHA-256 manifest를 만든다. 같은 manifest를 세 감사자에게 전달한 뒤 파일과 ZIP을 freeze한다. Findings를 고치면 ZIP과 manifest를 다시 만들고 세 감사를 반복한다. 같은 최종 snapshot에서 세 감사자가 `NO FINDINGS`를 반환한 경우에만 완료로 보고하며, 최종 verdict와 snapshot ID는 감사 후 문서를 변경하지 않도록 최종 응답과 작업 일지에 기록한다.

## 9. 2026-09-15 CSR / Key Attestation 필수 입력 감사

사용자는 이 폴더 전체에서 CSR Input과 Key Attestation의 필수 필드·반드시 포함할 값을 서브에이전트가 감사하고, 메인 검토·수정·재감사를 지적이 없어질 때까지 반복하도록 요청했다. 과거 21개 Android 매핑 감사 통과를 더 세부적인 입력 명세의 완전성 근거로 재사용하지 않았다.

대상은 5개 Markdown과 대응 ZIP뿐이다. 변경 전 사본, 외부 RFC 사본, 검증 도구와 manifest는 `/tmp/c2pa-csr-attestation-audit.LnSvdV/`에 보관했다. 최초 동결 snapshot은 `728211b209b10158676ee57976497dfe66da75f28de52faead5300f9f9376ef7`이다. 세 독립 read-only 감사자의 초기 결과는 CSR standards 4건, Android security 3건(+조건부 RSA exponent 보충), cross-document coverage 4건이었다. 외부 원문과 대조해 확인한 중복 지적은 아래처럼 합쳤다.

| ID / severity | 누락 또는 모호성 | 근거 / 보강 위치 | 검토 후 조치 |
|---|---|---|---|
| `INPUT-AUDIT-01` / High | 필수 여섯 extension의 extnID/inner type와 선택 AIA/CDP의 세부 값 누락 | pinned CSR:881-1336, MIB, RFC 5280; 02 §3.3 | exact OID·DER 타입·criticality·값, CSR 선택 vs 최종 cert 필수를 분리 |
| `INPUT-AUDIT-02` / Medium | PKCS#10 실제 필드와 inspector JSON projection 혼동, extensionRequest OID/단일 value 미명시 | RFC 2986 §4, RFC 2985 §5.4.2; 02 §3.3 | 필수 member, attribute OID·SET 단일 값, DEFAULT의 DER 생략과 decoded false 구분 |
| `INPUT-AUDIT-03` / Medium | SPKI algorithm OID·parameters·키 내부 타입 누락 | pinned CSR:758-866, RFC 3279/5480/8410; 02 §3.4 | RSA NULL, EC namedCurve, Ed25519 absent 및 outer signature 분리 |
| `INPUT-AUDIT-04` / Medium | 최종 CPL DN 제약을 CSR schema 자체의 의무로 잘못 귀속 | CSR:692-740, CP:387-395; 02 §3.1/§3.3, 03 REQ-DN | CSR C/O/CN과 project 선검사를 분리; 검증 강도는 유지 |
| `INPUT-AUDIT-05` / Medium | KeyDescription 8개 필수 member/version 쌍, AppId 중첩 타입 누락 | AOSP schema/fields; 02 §13.6 | 순서·타입·version/HAL integer·uniqueId 빈 값·AppId 전체 집합과 SHA-256 길이 명시 |
| `INPUT-AUDIT-06` / Medium | verifiedBootHash의 구조상 필수와 제품 기준값 비교를 혼동 | AOSP versioned RootOfTrust; 02 §13.4/§13.6 | v1/v2의 세 member와 v3 이상 네 member를 구분; reference 비교 의무를 임의 생성하지 않음 |
| `INPUT-AUDIT-07` / Medium | purpose/digest/padding 집합 타입 및 RSA exponent 조건부 속성 불명확 | CP:1802-1807, AOSP schema/KeyMint Tag.aidl; 02 §13.2/§13.6 | SET/INTEGER·포함/부분집합·조건부 요구를 명시; 추가 원소·운영 algorithm 승인과 구분 |
| `INPUT-AUDIT-08` / Medium | JSON 필수 필드의 null/empty/type, Android chain 최소 수·원소 타입 미명시 | `PROJECT` body 계약; 01 §5/§5.4 | 존재와 타입·최소 개수·canonical base64를 명시; 최대 상한 TBD 유지 |
| `INPUT-AUDIT-09` / Medium | 예시 placeholder 안내가 고정 schemaVersion까지 미승인값처럼 설명 | `OD-BODY-01`, RB-01; 01 §3/§5.1 | 현재 `2026-09-04`와 고정 문자열·실제 provider placeholder를 구분 |

### 9.1 수정·재감사 루프

초기 11개 지적과 보충 사항을 메인이 외부 원문으로 검토한 뒤 위 내용을 반영했다. README의 source registry와 03의 requirement/gate 추적표도 함께 갱신했다. 운영 결정 `APPROVED` 3개 / `TBD` 14개 및 AL1/AL2 production `DISABLED`는 유지한다. 서술 누락 보강은 실서비스 운영 설정 승인이나 verifier 코드·암호 테스트 완료를 뜻하지 않는다.

| 재감사 | frozen snapshot | 독립 결과와 검토 후 처리 |
|---|---|---|
| 보강본 1차 | `9ab2bcd02de88ebb1799eec0b4eb635644889c30590319985716fcfaed7c3c92` | 기존 지적 모두 해소. Android security는 `NO FINDINGS`. CSR standards와 coverage가 같은 Low locator 오기 1건을 각각 보고. 메인이 pinned MIB를 확인해 02 §3.3 EKU 행의 `MIB:32-34`를 실제 정의가 있는 `MIB:34-37`로 정정. OID 값은 변경하지 않음 |

매 보강본은 ZIP의 정확한 5개 entry 및 bytes, local link/anchor, 21개 AK 행, decision 상태를 검사하고 manifest를 만든 뒤 freeze한다. 세 감사자는 동일 snapshot을 원문과 새로 대조한다. 유효 finding이 있으면 수정하고 세 감사를 모두 반복하며, **동일 최종 snapshot에서 세 감사자가 모두 `NO FINDINGS`일 때만 종료**한다. 최종 snapshot과 세 verdict는 감사 후 파일을 다시 바꾸지 않도록 최종 응답·작업 일지에 기록한다.

# TSA Leaf enrollment 독립 감사 및 정정 기록

## 1. 철회한 이전 결론

이전 감사에서는 architecture 내부 설계 문장을 전제로 삼아 다음을 TSA Leaf 발급의 mandatory gate로 유지했다.

- INITIAL/REKEY마다 `1..N` Compound Evidence
- TSA TA/TEE 상태의 per-enrollment attestation
- timestamp-only ACL과 active-key count의 signed observation
- staged activation 계약이 없으면 TSA Leaf issuance 자체 차단

이 결론은 architecture 산출물을 독립적인 규범 근거처럼 순환 참조한 오류가 있었다. 현재 문서는 이 결론을 철회하며, 이전 audit item 중 이를 전제한 finding/resolution은 superseded다.

## 2. 원문만 사용한 재판정

| 질문 | 재판정 |
|---|---|
| Compound Evidence가 TSA Leaf 요청마다 필수인가? | 아니오. TSA enrollment requirement로 찾지 못함 |
| TSA application의 TEE 실행은 필수인가? | 예. On-Device TSA runtime/implementation 의무 |
| TEE 실행의 signed proof를 매 enrollment에 제출해야 하는가? | 아니오 |
| timestamp-only key와 single-active-key는 필수인가? | 예. TSA runtime/운영 의무 |
| ACL/active count를 매 enrollment에 증명해야 하는가? | 아니오 |
| INITIAL에만 attestation이 필수인가? | 아니오. INITIAL/REKEY 모두 base profile에는 없음 |
| REKEY가 신규 신청과 같은 심사인가? | 예. identity validation과 key ownership/profile 심사를 다시 수행 |
| optional remote attestation을 둘 수 있는가? | 예. 명시적인 CA CPS/provider 확장으로 가능 |

## 3. 감사 기준

재감사는 다음만 사실 근거로 사용한다.

- `conformance-public/docs/v0.2`
- `conformance-public/docs/v0.2/cert-profiles`
- `specifications/build/site/specifications/2.4`
- RFC 2986/3161/5280 등 원문

`architecture/**`는 찾은 원문 결론과 일치하는지 점검할 피감사 산출물일 뿐 근거로 사용하지 않는다. Appendix는 감사 범위에서 제외한다.

## 4. 정정 원칙

1. Dynamic Evidence는 Generator Product의 Claim Signing Certificate/Assurance Level 문맥에 한정한다.
2. TSA 절의 TEE/key/dedicated/single-active 문장은 runtime/implementation/operations 요구로 분류한다.
3. TSA certificate issuance는 secure credential, key ownership 및 CA business practices의 I/A/V에 근거한다.
4. PKCS#10은 이 architecture가 선택한 PoP 방식이며 C2PA가 허용한 유일한 방식으로 표기하지 않는다.
5. Compound Evidence, challenge, provider profile 및 `x5chain`은 optional attested TSA profile에만 둔다.
6. staged activation은 single-active-key를 구현하는 project mechanism이며 TSA Leaf issuance의 C2PA 선행조건으로 표기하지 않는다.

## 5. 감사 상태

2026-09-02에 standards, API/security, coverage의 세 관점으로 수정→finding→재수정→closure 루프를 수행했다.

| 감사 관점 | 최초/중간 finding | 조치 | 최종 상태 |
|---|---|---|---|
| Standards | API에 동봉하는 evidence와 issuance/control gate를 README 표가 혼합; optional artifact와 underlying runtime property 표현 혼동 | wire/issuance/runtime 열 분리, artifact 자체는 optional임을 명시 | `PASS`, finding closed |
| API/security | base response의 challenge 모호성, attested REKEY freshness/profile migration, optional TSA failure의 C2PA 오표기, optional array 표현 모순 | base transaction과 challenge 분리, `attested-v1` INITIAL/REKEY fresh Evidence 고정, failure matrix 분리, `1..N` 명시 | `PASS`, finding closed |
| Coverage | Overview의 공통 failure/incident 문구가 base TSA를 오차단할 가능성, 배포 ZIP의 구버전, broken local links | base/Evidence/runtime gate와 영향 scope 분리, ZIP 재생성·byte 비교, 링크 교체 | `PASS`, High/Medium 0, broken link 0 |

2026-09-02 추가 재감사에서는 `Overview.md`의 일반 TSA Leaf 발급 시험이 optional attestation과 runtime activation gate를 다시 혼합한 사실을 발견했다. 보정 후 폐쇄 감사 라운드 1에서 standards와 API/security는 `NO FINDINGS`, coverage는 내용상 finding 없이 아래 상태 표기의 갱신만 Low로 요청했다. 그 기록 지적까지 다음과 같이 폐쇄했다.

| 추가 finding | 조치 | 상태 |
|---|---|---|
| TSA 발급 시험에 TA/TEE Evidence와 이중 active-key 차단이 무조건 적용됨 | base issuance, optional attested issuance, runtime/activation 시험으로 분리 | `PASS/CLOSED` |
| 시스템 그림의 무조건적 `CSR + Evidence` | `profile-conditional Evidence`와 Evidence-required component 범위 명시 | `PASS/CLOSED` |
| staged activation이 C2PA 필수처럼 보이는 표현 | single-active invariant와 optional project mechanism 분리 | `PASS/CLOSED` |
| 위 보정 상태가 `독립 재감사 대상`으로 남은 stale 기록 | 라운드 1 결과를 반영하고 상태를 `PASS/CLOSED`로 갱신 | `PASS/CLOSED` |

최종 공통 판정은 다음과 같다.

- Base TSA INITIAL/REKEY의 `attestationEvidence` cardinality는 `0`이다.
- `c2pa-on-device-tsa-attested-v1`을 선택한 경우에만 INITIAL/REKEY 모두 fresh Evidence `1..N`이 필수다.
- TEE 실행·TEE key 생성/보관·timestamp 전용·single-active-key는 runtime/implementation/operations 의무다.
- 위 runtime 속성은 설계·TEE enforcement·시험·배포 승인·모니터링·감사로 보증할 수 있다.
- Staged activation과 signed observation은 채택한 project mechanism의 gate이지 base TSA Leaf issuance의 C2PA prerequisite가 아니다.
- `TSA-REQ-GAP-04/05/06/12/15/16/17`은 base TSA Leaf issuance blocker가 아니다.

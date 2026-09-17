# 04. Conformance 등록 및 그 밖의 요구사항

이 문서는 공개 v0.2 문서에서 확인한 CA 신청·운영 증거를 정리한다. **인증서 lint 성공, HSM 사용, 이 조사 문서의 감사 완료는 C2PA 승인과 다르다.**

## CA/TSA 등록 절차와 직접 제출 증거

근거: [Program Certificate Policy, Process Requirements, CA Evidence Request][program].

| ID | 요구 / 상태 | 준비할 결과물과 확인 기준 |
|---|---|---|
| E01 | **필수** — CA로 Program 신청, 역할별 법적 계약 체결, Intake 작성 | 법인/역할 정보와 signed agreement. TSA-only 신청은 받지 않으며 CA 서비스를 함께 제공해야 함 |
| E02 | **필수** — 등록 희망 Root 및/또는 ICA 인증서의 CP profile 검증 증거 | role별 DER/PEM·profile 검사 보고서. 01의 필드·체인·키 일치 검증을 포함하는 것을 제안 |
| E03 | **필수** — 해당 등록 키의 독립 입회 ceremony와 signed key generation script | 제3장 「키 생성 세레모니 스크립트 요구사항」 C01–C10, 실제 public key/인증서와 증거의 연결 |
| E04 | **조건부 대체** — 적합한 ceremony·script를 입증하는 WebTrust for CA 보고서로 E03 면제 가능 | 보고서의 범위·해당 키/행사 포함 여부와 관리자 수용 확인. 모든 보고서가 자동 면제 증거는 아님 |
| E05 | 새 CA/TSA Root·Intermediate 인증서 **set마다** 별도 Intake 필요 | CA TL/TSA TL 등록 구분, 각 계층의 PEM 인증서를 빈 줄로 구분하여 제출. 등록 앵커와 제출 체인 구분 |
| E06 | test CA/test TSA entry는 수락하지 않음 | production 식별·인증서·서비스 준비를 입증. 시험용 입력을 실제 등록으로 제출하지 않음 |
| E07 | CA/TSA가 같은 Root로 연결되면 CA·TSA 양쪽 구역에 Root를 기록하도록 안내 | 어느 목록에 어느 anchor를 올릴지 명시. 한 목록 등록만으로 다른 목록의 trust를 얻었다고 판단하지 않음 |
| E08 | 관리자 증거 검토 → 별도 Approver 검토·보완 → Notice/공개 record | 승인·공개 record 확인을 별도 완료 조건으로 둠. 공개 목록 갱신의 2인 통제는 C2PA 관리 측 의무이며 CA 키의 2인 통제와 별개 |

Program은 CP 전체 준수를 계약으로 확약하도록 한다. 제출 목록이 짧다는 이유로 제2장 「관리·운영 요구사항」의 운영 통제가 면제되지는 않는다. 신청 당시 계약·비공개 checklist·추가 evidence 요청까지 충족해야 실제 통과를 판단할 수 있다.

E16 — **등록 유지·제거 대응**: C2PA는 CA TL/TSA TL에서 참여자를 제거할 수 있다. Program은 정식 통지 후 해당 참여자가 Conformance Task Force에 출석하여 위반 관련 증거 검토에 응하도록 요구하고, Task Force 권고 후 Steering Committee가 최종 결정하도록 한다. Governance는 철회된 record를 `revoked`로 표시한다고 설명한다. 이의 제기·mediation 및 미해결 시 계약상 arbitration 경로를 운영 절차에 연결한다. 이는 개별 인증서 폐지와 별개이며 공개 문서에 없는 대응 SLA를 만들지 않는다. [Program Removal / Dispute Mediation][program], [Governance Participant Revocation / Appeals][gov]

## Issuing CA 운영으로 연결되는 요구

| ID | 적용 | 요구와 근거 |
|---|---|---|
| E09 | Claim Issuing CA·RA | 조직·주소·대표자 권한·요청 정보를 확인하고 인증된 enrollment 및 key ownership/possession 검증. Subscriber 재인증 간격은 최대 **398일**. [CP Initial Identity Validation / Identification and Authentication][identity] |
| E10 | Claim Issuing CA | GP의 적합성 증거, DN, 허용 AL과 dynamic evidence 확인. CP는 signed Notice를 수령·검증하며 공개 CPL이 증거를 충족할 수 있다고도 명시. 공개 전 Notice 경로와 Program의 `status=conformant` CPL 문구가 함께 있어 발급 gate 해석을 확인(Q08). [CP Proof of Conformance][identity], [Program Machine-Readable List Operation / Notice][program] |
| E11 | Claim Issuing CA | AL은 CPL `maxAssuranceLevel`을 넘길 수 없고 해당 수준의 evidence로 결정. CP Maximum Assurance Level은 maxAL 이하 **모든 수준에 발급 SHALL**도 명시한다. 이 지원 의무와 개별 요청에서 하위 AL 평가 MAY의 적용 관계는 Q10으로 추적. AL1도 인증된 GP instance 확인 필요. AL2는 하드웨어 기반 GP 식별·키 보유/보호·secure boot·보안 패치/허용 버전·nonce를 검증. 검증 실패 시 해당 AL 인증서 발급 금지; 가능한 경우 하위 AL 평가 허용. [CP Dynamic Evidence][dynamic], [Certificate Issuance][issue] |
| E12 | Claim Issuing CA | Claim Signing 키는 Subscriber/허용 KMS가 생성하며 CA 생성 금지. CPL과 일치하는 ASCII DN, anonymous/pseudonymous 금지, 개별 device serial 등 instance 고유 식별 금지. leaf에 적절한 CP·EKU·AL·profile 적용. [CP Naming, Subscriber Generation, Claim Signing Leaf profiles][cp] |
| E13 | 모든 발급 CA | Subscriber Agreement/ToU, authorization·정보 정확성 검증, 기록·폐지·상태 서비스 운영. Root는 Issuing CA 수행·보증·CP 준수 책임. [CA Representations][warranty], 제2장 「관리·운영 요구사항」 O11·O21–O28 |

E11의 AL2 구체 검증은 claim generator뿐 아니라 GP TOE에서 asset/assertions를 처리하는 소프트웨어도 대상으로 한다. O.3/O.4 각각 플랫폼의 인증된 secure boot, HIGH/CRITICAL 취약점에 대한 탐지 후 90일 내 조치, 선택한 방식에 따른 최근 90일 patch 또는 CA에 양호 상태로 등록된 revision 검증을 구분한다. nonce는 CA가 발행한 challenge와 일치해야 하고 생성은 provider 권고를 따른다. 이는 Root 개인키의 보안 등급 요구로 대체하지 않는다. 플랫폼별 증거 포맷 구현은 별도 발급 시스템 설계 항목이다. [CP appendix][dynamic]

## TSA를 운영하는 경우

T01 — [CP Time-Stamping Authorities][tsareq]에 따라 RFC3161 TSA를 운영하고 TSA TL 등록을 신청할 수 있다. 다음은 **TSU/TSA의 조건부 요구**이며 Root·ICA HSM에 Level 3가 무조건 필요하다는 뜻이 아니다.

| 구분 | 조건부 필수 요구 |
|---|---|
| 공개 정책 | hash 알고리즘·timestamp signature 예상 수명·의무/제한·검증법·정확도·event logging/보존기간 공개 |
| 시각 | UTC(k) laboratory time 추적, 선언한 정확도에 동기화·leap second 유지, 오차 초과 탐지 시 발급 중지. 선언 정확도는 오차 1초 이하가 SHOULD |
| 서명키 | timestamp 전용 키, TSU마다 한 번에 하나의 활성 timestamp signing key |
| 요청 hash | SHA2-256·384·512만 수락 |
| Backend TSA | TSU signing key의 생성·저장은 EAL4+ 등 원문 인정 평가 또는 FIPS140-2/140-3 Level3 등 해당 절의 적격 secure device |
| On-device TSA | 최소 매 24시간 온라인 UTC(k) 추적 time source 동기화 **시도**, TSA app은 TEE 실행, TSU key는 TEE 생성·보관 |

TSA Issuing CA 인증서(EKU/pathLen/5479일)와 TSA **leaf/TSU 키** 요구를 분리한다. TSA leaf는 01 U04의 end-entity 제한과 [CP TSA leaf profile][cp]를 따르며 CA 인증서용 KU를 사용하지 않는다.

## 제품 심사와 공통 법무의 범위

E14 — [Additional Requirements][additional]의 `specVersion`, `allActionsIncluded`, 지정 actions의 `digitalSourceType`, 2.4 `c2pa.opened`의 digitalSourceType 금지, crJSON validation harness는 해당 GP/VP 역할의 추가 의무다. CA만 신청할 때 Root 인증서의 확장이나 ceremony 요건으로 옮기지 않는다. GP/VP도 신청한다면 별도의 계약·제품 evidence 경로가 필요하다. [GP Security Requirements][gp]도 product TOE 대상이다.

E15 — CP `Other Business and Legal Matters`에는 요금/재무, 업무정보 기밀성, 개인정보 목적·권리·법규, IP, 보증·책임, 계약·종료·통지·정책 변경·분쟁·준거법 관련 조건이 있다. CA 운영 주체가 공개 정책과 실제 계약에서 검토할 항목이며 암호 파라미터만으로 충족되지 않는다. 이번 결과는 해당 조항의 법률 자문이나 계약 검토 완료를 뜻하지 않는다. [CP][cp], [Governance Legal Agreements][gov]

## 구현·신청 시 사용할 evidence 묶음 제안

1. **정책**: 적용 버전, CP/CPS 대응표, CA 계층·책임, 공개 정책, 미확정 해석의 회신.
2. **키/인증서**: module assurance·설정, 키 inventory, DER/PEM, profile·서명·chain 검증, 생성 증거와 일치 기록.
3. **ceremony**: 승인된 script, 독립 입회, 수행 로그, sign-off, deviation, 필요시 인정 가능한 WebTrust 보고서.
4. **운영**: 다인 통제·접근/변경관리·backup/off-site·연간 검토·기록/폐지·OCSP/CRL·사고/종료 증거.
5. **등록**: signed agreement, Intake와 PEM set, 관리자 피드백/처리, 최종 Notice와 TL record.

위 구성은 제출을 쉽게 하는 제안이다. 실제 심사에서는 운영 환경에 대한 키·인증서·계약·승인 증거를 준비하여 제출해야 한다.

[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md
[identity]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L401-L485
[dynamic]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1684-L1768
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529
[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[warranty]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1520-L1564
[tsareq]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L905-L939
[additional]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md
[gp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md
[gov]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Governance%20Framework.md

# 04. Conformance 등록 및 그 밖의 요구사항

이 문서는 공개 v0.2 문서에서 확인한 CA 신청·운영 증거를 정리한다. **인증서 lint 성공, HSM 사용, 이 조사 문서의 감사 완료는 C2PA 승인과 다르다.**

ID별 원문 파일·고정 줄·절은 [원문 위치 대응표](06-source-map.md)에 있다.

## CA/TSA 등록 절차와 직접 제출 증거

아래 표는 신청자가 충족할 요건과 준비할 증거를 구분한다. 실제 공개 목록의 갱신·승인 권한은 C2PA Program 측에 있다.

| ID | 요구 / 상태 | 준비할 결과물과 확인 기준 |
|---|---|---|
| E01 | **필수** — Expression of Interest로 CA 역할 신청 → 역할별 법적 계약 → Intake 작성. TSA-only 신청은 받지 않음 | 법인/역할 정보, signed agreement, Intake. TSA도 신청하면 CA 서비스를 함께 제공해야 함. [Program §6.6.1–3][application] |
| E02 | **필수** — 등록 희망 Root 및/또는 ICA 인증서의 CP profile 검증 증거 | role별 DER/PEM·profile 검사 보고서. 01의 필드·체인·키 일치 검증을 포함하는 것을 제안. [Program §6.4][program-policy], [CA Evidence Request][ca-evidence] |
| E03 | **필수** — 해당 등록 키의 독립 입회 ceremony 증거와 signed key generation script | 제3장 C01–C10, 실제 public key/인증서와 증거의 연결. scripted process는 C2PA 검토가 가능해야 함. [Program §6.4][program-policy], [CA Evidence Request][ca-evidence] |
| E04 | **조건부 대체** — 적합한 ceremony·script를 입증하는 WebTrust for CA 보고서로 E03의 직접 증거 제출 요구를 대체할 수 있음 | 대상 키·행사·script·적용 기준 및 관리자 수용 확인. CP 생성 통제가 면제되는 근거가 아니며, 별도 CA Evidence Request의 검토자료 제공 범위까지 자동 면제하지 않음(Q07). [Program §6.4][program-policy] |
| E05 | 새 CA/TSA Root·Intermediate 인증서 **set마다** 별도 Intake 필요 | CA TL/TSA TL 등록 구분, 상위로 연결되는 각 CA의 PEM 인증서를 빈 줄로 구분하여 제출. 등록 앵커와 제출 체인을 구분. [Program §6.6.3][intake] |
| E06 | test CA/test TSA entry는 수락하지 않음 | 제출 set이 시험용 등록이 아님을 확인. production 식별·서비스 준비 자료는 증거 제안. [Program §6.6.3][intake] |
| E07 | CA/TSA가 같은 Root로 연결되면 CA·TSA 양쪽 구역에 Root를 기록하도록 안내(소문자 should) | 각 목록의 등록 anchor를 명시. 한 목록 등록만으로 다른 목록의 trust를 얻었다고 판단하지 않음. [Program §6.6.3][intake] |
| E08 | 관리자 증거 검토 → 별도 Approver 검토·보완 → Notice/공개 record | 승인·공개 record 확인을 별도 완료 조건으로 둠. 공개 목록 갱신의 2인 통제·multi-party approval은 C2PA 관리 측 의무이며 CA 키의 2인 통제와 별개. [Program §6.6.5–8][approval], [§6.7.2][list-controls] |

Program은 CP 준수를 계약으로 확약하도록 한다. 제출 목록이 짧다는 이유로 제2장 「관리·운영 요구사항」의 운영 통제가 면제되지는 않는다. 관리자는 비공개 checklist·도구·assessment spreadsheet도 사용한다. 신청 당시 계약과 요청받은 보완 증거를 충족하고 최종 승인을 받아야 실제 통과로 판단한다. [Program §6.4][program-policy], [§6.6.4–6][assessment]

E16 — **등록 유지·제거 대응**: C2PA는 CA TL/TSA TL에서 참여자를 제거할 수 있다. Program은 정식 통지 후 해당 참여자가 Conformance Task Force에 출석하여 위반 관련 증거 검토에 응하도록 요구하고, Task Force 권고 후 Steering Committee가 최종 결정하도록 한다. Governance는 철회된 record를 `revoked`로 표시한다고 설명하며 두 표현의 실제 목록 처리 범위는 Q18로 추적한다. 이의 제기·mediation 및 미해결 시 계약상 arbitration 경로를 운영 절차에 연결한다. 이는 개별 인증서 폐지와 별개이며 공개 문서에 없는 대응 SLA를 만들지 않는다. [Program §6.7.3–4][removal], [Governance Participant Revocation / Appeals][gov-removal]

## Issuing CA 운영으로 연결되는 요구

| ID | 적용 | 요구와 근거 |
|---|---|---|
| E09 | Claim Issuing CA·RA | 조직·주소·대표자 권한·요청 정보를 확인하고 인증된 enrollment 및 key ownership/possession 검증. 신청 정보의 완전성·정확성을 검토하고, 승인 후 신규/기존 secure access credentials를 승인 Subscriber에 연결. Subscriber 재인증 간격은 최대 **398일**. [CP Initial Identity Validation / Identification and Authentication][identity], [Certificate Application / Processing / CA Access Credentials][subscriber-application] |
| E10 | Claim Issuing CA | GP 적합성 증거·DN·CPL record number·요청 AL을 확인. AL이 요구하면 CPL에 등록된 `attestationMethods`로 증거를 만들 수 있고 CA가 해당 format을 해독·처리할 수 있음을 신청 시 확인. signed Notice 수령·검증 SHALL과 공개 CPL로 proof를 충족할 수 있다는 MAY, 공개 전 Notice 경로와 Program의 `status=conformant` CPL 문구 관계는 Q08로 추적. [CP Proof of Conformance][conformance], [Certificate Application / Processing][subscriber-application], [Program Notice][notice] / [List Operation][list-use] |
| E11 | Claim Issuing CA | AL은 CPL `maxAssuranceLevel`을 넘길 수 없고 해당 수준의 evidence로 결정. CP Maximum Assurance Level은 maxAL 이하 **모든 수준에 발급 SHALL**도 명시한다. 이 지원 의무와 개별 요청에서 하위 AL 평가 MAY의 적용 관계는 Q10으로 추적. AL1도 인증된 GP instance 확인 필요. AL2는 하드웨어 기반 GP 식별, hardware-backed platform keystore 또는 KMS 안에서의 **키 생성·저장 및 GP instance의 키 보유**를 hardware-backed artifact로 검증하며 secure boot·보안 패치/허용 버전·nonce도 검증. 검증 실패 시 해당 AL 인증서 발급 금지; 가능한 경우 하위 AL 평가 허용. [CP Dynamic Evidence][dynamic], [Certificate Issuance][issue] |
| E12 | Claim Issuing CA | Claim Signing 키는 Subscriber/허용 KMS가 생성하며 CA 생성 금지. CPL과 일치하는 ASCII DN, anonymous/pseudonymous 금지, 개별 device serial 등 instance 고유 식별 금지. [제1장 P06–P07](01-key-and-certificate-requirements.md)의 leaf 발급정책 적용. [CP Naming][naming], [Subscriber Generation][subscriber-keys], [Claim Signing Leaf profiles][claim-leaf] |
| E13 | 모든 발급 CA | 제품명 사용권/통제, 발급권한·대표자 권한, 인증서 정보 정확성의 검증 절차를 수행하고 CA CP/CPS에 정확히 기술(Q17의 대체 공개 수단 관계 확인). 비계열 Subscriber와 유효한 Subscriber Agreement, 동일 조직/계열이면 대표자의 ToU 인정. 기록·폐지·상태 서비스 운영. Root는 Issuing CA 수행·보증·CP 준수·책임을 자신의 발급처럼 부담. [CA Representations][warranty], 제2장 O11·O21–O28 |

E11의 AL2 구체 검증은 claim generator뿐 아니라 GP TOE에서 asset/assertions를 처리하는 소프트웨어도 대상으로 한다. O.3/O.4 각각 플랫폼의 인증된 secure boot, **NIST CVSS v3 이상 기준 HIGH/CRITICAL** 취약점에 대한 탐지 후 90일 내 조치, 선택한 방식에 따른 최근 90일 patch 또는 CA에 양호 상태로 등록된 revision 검증을 구분한다. nonce는 CA가 발행한 challenge와 일치해야 하고 생성은 provider 권고를 따른다. 이는 Root 개인키의 보안 등급 요구로 대체하지 않는다. 플랫폼별 증거 포맷 구현은 별도 발급 시스템 설계 항목이다. [CP appendix][dynamic]

**Revision 방식을 선택한 GP Applicant**는 등록 가능한 최소 revision과 HIGH/CRITICAL 취약점으로 탐지 후 90일이 지나면 부적격이 되는 revision을 CA에 알리는 절차를 설계·수행해야 한다(SHALL). CA는 통지된 정보를 CP의 good-standing revision 검증에 연결해야 한다. 허용목록 변경의 책임자·승인·증거보존은 후속 운영 정책으로 정하고, 원문에 없는 통지 SLA를 추가하지 않는다. [GP O.3 Level 2][gp-revision-claim], [GP O.4 Level 2][gp-revision-toe]

## TSA를 운영하는 경우

T01 — [CP Time-Stamping Authorities][tsareq]에 따라 RFC3161 TSA를 운영하고 TSA TL 등록을 신청할 수 있다. 다음은 **TSU/TSA의 조건부 요구**이며 Root·ICA HSM에 Level 3가 무조건 필요하다는 뜻이 아니다.

| 구분 | 원문 강도와 TSA 운영 조건 |
|---|---|
| 발급 검증 | Time Stamping Certificate 발급은 CA의 업무관행에 문서화한 식별·인증·검증 절차를 따라야 함(SHALL). Claim GP용 CPL/AL 심사를 자동 적용하지 않음. [CP Certificate Issuance 3][tsa-issuance] |
| TSA 관행 공개 | CA는 hash 알고리즘·timestamp signature 예상 수명·Subscriber/Relying Party 의무(있다면)·사용 제한·검증법·정확도·event logging/보존기간을 공개해야 함(SHALL). [CP General TSA Requirements 1][tsa-general] |
| 시각·정확도 | 각 time-stamp에 intended accuracy를 명시하고 해당 정확도에 동기화·leap second 동기화를 유지해야 함(SHALL). **TSA는 선언 정확도를 벗어나는 오차를 탐지해야 하며(SHALL), 이 경우 TSU는 발급을 중지해야 함(SHALL)**. 1초 이하 정확도는 SHOULD. UTC(k) laboratory time 추적은 별도 문장의 **소문자 shall**. [CP General TSA Requirements 2–4][tsa-general] |
| 서명키 | timestamp 전용 키를 쓰고 TSU마다 한 번에 하나의 활성 timestamp signing key를 가져야 함(SHALL). [CP General TSA Requirements 5][tsa-general] |
| 요청 hash | SHA2-256·384·512만 수락해야 함(SHALL). [CP General TSA Requirements 6][tsa-general] |
| Backend TSA | TSU signing key 생성·저장은 ISO/IEC15408 EAL4+ 또는 동등 국제 평가, FIPS140-2/140-3 Level3+, 또는 적절한 CC PP/ST EAL4+ 등 해당 절이 인정하는 적격 secure device를 사용해야 함(SHALL). [CP Backend TSA][tsa-backend] |
| On-device TSA | 최소 매 24시간 온라인 UTC(k) 추적 time source 동기화 **시도**가 SHALL. TSA app의 TEE 실행, TSU key의 TEE 생성·보관도 각각 SHALL로 작성됨. Backend TSA를 time source로 쓰는 문장 뒤 조건부 연결 표현의 범위는 Q16으로 추적하며, TEE 보호의 면제 근거로 사용하지 않음. [CP On-Device TSA][tsa-on-device] |

TSA Issuing CA 인증서(EKU/pathLen/5479일)와 TSA **leaf/TSU 키** 요구를 분리한다. TSA leaf는 [제1장 U04·P08](01-key-and-certificate-requirements.md)과 [CP TSA leaf profile][tsa-leaf]를 따른다. OCSP responder leaf의 발급정책은 같은 장 P09에 별도로 연결한다.

## 제품 심사와 공통 법무의 범위

E14 — 아래 Additional 요구는 해당 GP/VP 역할의 추가 의무다. CA만 신청할 때 Root 인증서의 확장이나 ceremony 요건으로 옮기지 않는다.

| 요구 | 적용 조건·원문 |
|---|---|
| `claim_generator_info.specVersion` | GP가 주장한 Spec 2.4 이상. Intake·CPL의 주장 버전과 일치하고 제출 sample에도 포함. [Additional specVersion][additional-spec] |
| `allActionsIncluded` | Spec 2.2/2.4 GP의 `actions-map-v2`에 true/false 중 하나를 기록. [Additional allActionsIncluded][additional-actions] |
| `digitalSourceType` | Spec 2.2/2.4의 created assertions 안 pre-defined actions에 적절한 값 기록. 원문이 열거한 예외 actions는 이 의무에서 제외. 예외가 곧 기록 금지는 아님. [Additional selected actions][additional-dst] |
| `c2pa.opened`의 `digitalSourceType` 금지 | Spec 2.4. [Additional c2pa.opened][additional-opened] |
| crJSON harness/결과 제출 | 모든 Spec 버전의 VP 또는 검증기능을 갖춘 GP. asset·test CA TL·test TSA TL·RFC3339 validation time 입력으로 crJSON 결과를 제공. [Additional validation][additional-validation] |

GP/VP도 신청한다면 역할별 계약과 제품 증거가 필요하다. GP는 지정 Markdown GPSA template·구현 유형과 주장 media type별 sample 증거를 제출한다. 제품 CPL record 또는 GP Security 준수에 material change가 발생하면 재신청하고 새 CPL record ID를 받아야 한다(SHALL). 이 제품 재심사 조건을 CA의 주기적 재등록 요건으로 확장하지 않는다. [Program Product Evidence][product-evidence], [Material Change][material-change]. [GP Security Requirements][gp]는 product TOE 대상이며, 해당되는 static/dynamic evidence는 둘 중 선택하는 것이 아니다.

E15 — CP `Other Business and Legal Matters`의 요금 공개, 업무정보 공유 제한, 개인정보 목적, 공식 서면 통지·연락처 유지, 중대 CP 변경 통지, 계약 관계·준거법 조건을 CA 공개 정책과 실제 계약에 연결한다. 재무·IP·보증·책임 관련 조항도 함께 검토한다. CP의 dispute 절, 일부 disclaimer/liability/indemnity 및 termination 세부 절은 `No stipulation`이며 구체 의무가 있다고 가정하지 않는다. C2PA와 참여자 간 mediation/arbitration은 E16의 Program 근거다. [CP Business and Legal][business], [Governance Legal Agreements][gov-legal]

## 정책 확정·신청 시 사용할 evidence 묶음 제안

1. **정책**: 적용 버전, CP/CPS 대응표, CA 계층·책임, 공개 정책, 미확정 해석의 회신.
2. **키/인증서**: module assurance·설정, 키 inventory, DER/PEM, profile·서명·chain 검증, 생성 증거와 일치 기록.
3. **ceremony**: 승인된 script, 독립 입회, 수행 로그, sign-off, deviation, 필요시 인정 가능한 WebTrust 보고서.
4. **운영**: 다인 통제·접근/변경관리·backup/off-site·연간 계획 검토·기록 종류별 보존정책·폐지·OCSP/CRL·사고/종료 증거. 독립 감사·보고서 권고와 사고보고 SHALL의 구분은 O19/O27을 적용.
5. **등록**: signed agreement, Intake와 PEM set, 관리자 피드백/처리, 최종 Notice와 TL record.

위 구성은 제출을 쉽게 하는 제안이다. 실제 심사에서는 운영 환경에 대한 키·인증서·계약·승인 증거를 준비하여 제출해야 한다.

[application]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L402-L416
[program-policy]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L368-L382
[ca-evidence]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L458-L460
[intake]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L414-L422
[approval]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L462-L478
[list-controls]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L504-L508
[assessment]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L430-L470
[removal]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L510-L518
[gov-removal]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Governance%20Framework.md#L444-L450
[identity]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L401-L485
[subscriber-application]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L489-L509
[conformance]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L457-L467
[notice]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L472-L474
[list-use]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L486-L502
[dynamic]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1684-L1768
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529
[gp-revision-claim]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md#L510-L518
[gp-revision-toe]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md#L586-L594
[naming]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L379-L399
[subscriber-keys]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L815-L823
[claim-leaf]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1204-L1332
[warranty]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1520-L1564
[tsareq]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L905-L939
[tsa-issuance]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L517
[tsa-general]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L915-L927
[tsa-backend]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L929-L931
[tsa-on-device]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L933-L939
[tsa-leaf]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1334-L1386
[additional-spec]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md#L14-L34
[additional-actions]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md#L36-L52
[additional-validation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md#L54-L78
[additional-dst]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md#L80-L99
[additional-opened]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md#L101-L117
[product-evidence]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L438-L456
[material-change]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L482-L484
[gp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md#L234-L328
[business]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1456-L1682
[gov-legal]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Governance%20Framework.md#L472-L474

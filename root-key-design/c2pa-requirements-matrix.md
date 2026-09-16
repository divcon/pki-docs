# C2PA 요구사항 대응표

2026-09-16 KST. 공식 Conformance 문서 v0.2, commit `7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50`를 기준으로 한다. 아래 근거는 공식 원문이고, 설계 링크는 그 요구를 반영한 위치다. 버전·취득 이력은 [자료 목록](../references/root-key-sources.md)을 따른다.

이 표는 이번 Root/First 운영 설계에서 검토한 항목을 추적한다. CP 전체 조항의 완전한 심사 목록이나 준수 선언이 아니다. **문서 반영은 설계에 조건을 적었다는 뜻이며, 실제 운영·구현·등록의 검증 완료를 뜻하지 않는다.** 조직명과 담당자 지정은 요구사항 R11에 따라 보류한다.

## 조건과 남은 증빙

| ID | 원문 조건·근거 | 설계 반영 위치 | 현재 상태와 남은 작업 |
|---|---|---|---|
| M01 | [Certificate Profiles][CP-PROFILES], [Key Pair and Certificate Usage][CP-USAGE]: 용도별 CA·leaf 프로파일과 허용 키 사용을 준수 | [계층](operating-model.md#hierarchy), [발급 검사](operating-model.md#issuance) | 문서 반영. 실제 인증서의 알고리즘·확장·pathLen·체인 프로파일 검사 필요. TSA 계층은 V02 미확인 |
| M02 | [Certificate Issuance][CP-ISSUANCE], [Procedural Controls][CP-PROCEDURAL]: Root의 모든 인증서 서명은 2인 참여, 그중 1인의 명시적 실행 명령. CA 인증서 발급은 문서화된 다인 통제·split knowledge 원칙 적용 | [2인 통제 대안](dual-control-options.md) | 문서 반영. HSM quorum과 절차의 조합이 단독 서명·관리·복구 우회를 막는지 V03 PoC 필요. 2-of-3은 설계 후보 |
| M03 | [CA 키 생성][CP-KEYGEN] 및 [Program의 Certificate Policy][PROGRAM-CP]: ceremony script와 생성 증빙. 등록 대상은 독립 입회·서명된 script 또는 명시된 WebTrust 예외 조건 | [생성·등록 증빙](dual-control-options.md#c2pa-controls) | 문서 보완. 실제 ceremony·프로파일 검증·등록 증빙 미작성. CP의 기록만으로 Program의 독립 입회를 대체하지 않음 |
| M04 | [Certificate Renewal][CP-RENEWAL], [Re-key][CP-REKEY], [Modification][CP-MODIFICATION]: 해당 CA가 이미 발급한 키로 새 인증서 발급 금지. Subscriber re-key는 신규 검증, 발급 인증서 수정 금지 | [새 키로 교체](operating-model.md#rekey), [신뢰 앵커 교체](trust-anchor-migration.md) | 문서 보완. 동일 키 재발급 거부, 같은 인증서 재전달, 새 키 교체, 불확정 서명 복구 시험 필요 |
| M05 | [Repositories][CP-REPOSITORIES]: 모든 발급 인증서의 serial·subject·유효기간·확장과 값·폐지 상태를 만료 후 최소 1년 보존. 보관소 접근 통제·정기 감사 | [기록 보존](operating-model.md#records) | 문서 보완. 저장·보존·검색·삭제 정책과 복원 시험 필요. 조기 폐지로 보존 기산점을 앞당기지 않음 |
| M06 | [Certificate Status Services][CP-STATUS]: Claim OCSP는 필수 기록 보존 기간까지 제공. 하위 CA·TS 인증서는 OCSP가 없으면 CRL 필요 | [OCSP 운영](operating-model.md#ocsp) | 문서 보완. 만료·CA 교체·운영 종료 후에도 유효한 응답을 제공할 원장·응답자 교체·이관 검증 필요. CRL 미사용 결정 유지 |
| M07 | [Key Pair and Certificate Usage][CP-USAGE], [응답자 프로파일][OCSP-PROFILE], [RFC 6960 §4.2.2.2][RFC-OCSP]: 발급 CA가 직접 위임한 응답자 leaf가 해당 issuer 인증서의 상태를 응답 | [OCSP 위임](operating-model.md#ocsp) | 문서 반영. 일반 OCSP ICA 대신 issuer별 직접 위임. 외부 검증기의 NoCheck·stapling·앵커 처리 시험 필요 |
| M08 | [Key Backup and Recovery][CP-KEYBACKUP]: 공식 계획의 연간 검토, 모든 CA 키 백업의 원본과 같은 다인 통제, off-site 사본, 평문 반출 금지 | [백업 계획](operating-model.md#backup), [다인 통제](dual-control-options.md#c2pa-controls) | 문서 보완. CloudHSM 백업 위치·권한·복구 후 통제 및 실제 연간 검토 증빙 필요 |
| M09 | [Key Archival][CP-KEYARCHIVAL], [Compromise and Disaster Recovery][CP-RECOVERY]: CA 개인키 아카이빙 금지. 중요 데이터 백업·복구 계획 유지 | [백업·복구와 파기](operating-model.md#backup) | 문서 보완. 운영 복구용 백업과 기록 아카이브의 분리, 파기·잔여 의무 처리 검증 필요. 복구 시험 연 1회는 설계 제안 |
| M10 | [Audit Logging Procedures][CP-AUDIT], [Records Archival][CP-ARCHIVAL]: 작업 주체·시각·행위·관련 정보 기록, 로그 보호·정기 검토, 기록별 보존·검색·복원 정책 | [기록 정책](operating-model.md#records) | 문서 보완. 로그 저장소·변경 권한 분리·검토 절차와 유형별 최종 보존 기간 필요. 모든 로그에 CP가 같은 1년 규칙을 정한 것은 아님 |
| M11 | [Publication][CP-PUBLICATION]: 사업 관행 고지는 공개 CPS 또는 C2PA와 협의한 다른 방법으로 이행 | [공개 정책](operating-model.md#records) | 문서 보완. CPS 등 실제 고지 문서와 운영 절차 작성·일치 확인 필요 |
| M12 | [Certificate Issuance][CP-ISSUANCE], [Certificate Acceptance][CP-ACCEPTANCE], [Subscriber 키 생성][CP-SUBSCRIBER]: Claim 발급 자격·해당 Assurance Level 증빙·Subscriber 동의·키 생성 및 사용 조건 | [하위 CA 인계](operating-model.md#issuance) | 인계 조건 보완. Phone/TV의 제품·Subscriber·attestation·leaf 발급 증빙 필요. 중앙이 claim-signing 키를 생성하는 흐름은 사용하지 않음 |
| M13 | [Certificate Revocation][CP-REVOCATION]: 제품 revoked 상태, 검증된 기관/Subscriber 요청, 침해·해당 시 attestation 실패·키 노출·CP 미준수·오용에 대한 폐지 | [폐지 접수·처리](operating-model.md#revocation) | 문서 보완. 제품 상태·사고 통보 연동, 처리 시간, 요청 검증·OCSP 반영·통보 훈련 필요 |
| M14 | [General TSA Requirements][CP-TSA-GENERAL]: 시간의 UTC(k) 추적성, 선언 정확도와 윤초 동기화, 정확도 초과 탐지 시 발급 중단, 전용 키·단일 활성 키·허용 해시, TSA 관행 공개 | [TSA 공통 인계](operating-model.md#tsa-handoff) | 인계 조건 보완. 시간 소스·정확도·중단 시험과 운영 정책을 플랫폼이 증빙. 1초 이내 정확도는 SHOULD |
| M15 | [On-Device TSA][CP-TSA-DEVICE]: 적어도 24시간마다 온라인 동기화 시도, TSA 애플리케이션의 TEE 실행과 TSU 키의 TEE 내 생성·보관 | [Phone/TV on-device 인계](operating-model.md#tsa-handoff) | 인계 조건 보완. Phone 및 해당 TV의 TEE·시도 기록·오프라인 오차 시험 필요. 24시간마다 성공해야 한다는 요구로 바꾸지 않음 |
| M16 | [Backend TSA][CP-TSA-BACKEND]: TSU 키 생성·보관 장치에 별도 평가 기준 적용 | [TV backend 인계](operating-model.md#tsa-handoff) | 해당 형태 선택 시 적용. 실제 장치의 평가·인증과 배포 구성 확인 필요. CA용 HSM 조건만으로 대체 불가 |
| M17 | [Key Changeover][CP-CHANGEOVER], [CA or RA Termination][CP-TERMINATION]: 문서화된 키 교체, 종료 절차 및 긴급 사고 예외를 제외한 Subscriber 사전 통보 | [수명주기](operating-model.md#lifecycle), [앵커 교체](trust-anchor-migration.md) | 문서 보완. 제품별 FOTA·신뢰 저장소·독립 업데이트 권한 조사와 전환 시험 필요. 종료 후 보존·상태 제공 의무도 추적 |

## 아직 확정할 수 없는 판단

| 항목 | 현재 판단 | 종료에 필요한 근거 |
|---|---|---|
| V01: 미등록 상위 G0의 C2PA 적용 범위 | First가 검증 경로의 신뢰 앵커라는 사실과 G0 운영 의무 면제는 별개의 문제다. 검토한 CP/Program에서 포괄적 면제는 확인하지 못했으며, 의무 전부의 적용도 단정하지 않는다. | 적용되는 공식 문구·참가 조건 또는 C2PA의 해당 계층에 대한 해석. 그전에는 [운영 모델](operating-model.md#hierarchy)의 공통 통제 채택 방침 유지 |
| V02: TSA First→TSA Issuing ICA | TSA Issuing CA [프로파일][TSA-PROFILE]의 Issuer Name과 AKI 설명에 차이가 있다. pathLen 값만으로 공식 적합성을 확정하지 않는다. | 선택한 프로파일·계층에 대한 공식 정합성 확인과 실제 프로파일 검증 |
| V03: CloudHSM 기반 2인 통제 | 설계 대안과 실패 기준이 있으며 실환경 PoC는 수행하지 않았다. | [PoC 기준](dual-control-options.md)에 따른 단독 서명·관리자 우회·복구·승인 대상 결합·알고리즘별 결과 |
| V04/V05: 단말 교체·PQC | 갱신·복구 구조 제안은 있으나 단말 저장 위치·알고리즘·부팅 권한은 조사하지 않았다. | [교체 설계](trust-anchor-migration.md)의 제품별 능력 조사, 실제 검증기·HSM·C2PA 프로파일 지원 확인 |

## 상세 운영 문서로 이어질 항목

이 대응표로 CP 전체 심사를 완료했다고 판단하지 않는다. 물리·네트워크·인력 보안, 역할 분리와 교육·권한 검토, 변경 관리, 세부 인증서 프로파일과 발급 자격 검증, 공개 CPS·계약·등록 자료 등은 적용 범위별 상세 절차와 실제 증빙을 추가해야 한다. 관련 원문은 [Facility, Management, and Operational Controls][CP-OPERATIONS]와 [Program][PROGRAM]에서 이어서 확인한다.

운영 전에는 각 해당 항목에 정책/절차 버전, 역할, 증빙 위치, 수행일, 검토 결과와 결함 조치를 연결한다. 조직명·인명 배정은 이후에 해도 되지만 문서에 필요한 역할과 통제 자체를 삭제하지 않는다. 인계 대상의 미충족 조건은 인증서 발급 또는 운영 시작을 보류하는 조건으로 처리한다.

이 설계의 응답 유효기간 24시간·재생성 6시간, 응답자 인증서 30일, HSM quorum 2-of-3, 복구 목표 1영업일 및 복구 시험 연 1회 제안은 CP의 의무 수치와 구분한다. 반면 발급 기록의 만료 후 최소 1년, 백업 계획의 연간 검토, on-device TSA의 적어도 24시간마다 동기화 시도는 이 버전의 원문 조건이다.

[CP-PROFILES]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-profiles
[CP-USAGE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage
[CP-ISSUANCE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-issuance
[CP-PROCEDURAL]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#procedural-controls
[CP-KEYGEN]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[CP-RENEWAL]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-renewal
[CP-REKEY]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-re-key
[CP-MODIFICATION]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-modification
[CP-REPOSITORIES]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#repositories
[CP-STATUS]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-status-services
[CP-KEYBACKUP]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-backup-and-recovery
[CP-KEYARCHIVAL]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-archival
[CP-RECOVERY]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#compromise-and-disaster-recovery
[CP-AUDIT]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#audit-logging-procedures
[CP-ARCHIVAL]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#records-archival
[CP-PUBLICATION]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#publication
[CP-ACCEPTANCE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-acceptance
[CP-SUBSCRIBER]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-subscribers
[CP-REVOCATION]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-revocation
[CP-TSA-GENERAL]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#general-tsa-requirements
[CP-TSA-DEVICE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#on-device-tsa
[CP-TSA-BACKEND]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#backend-tsa
[CP-CHANGEOVER]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#key-changeover
[CP-TERMINATION]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#ca-or-ra-termination
[CP-OPERATIONS]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md#facility-management-and-operational-controls
[PROGRAM-CP]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Conformance%20Program.md#certificate-policy
[PROGRAM]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Conformance%20Program.md
[OCSP-PROFILE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.yaml
[TSA-PROFILE]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml
[RFC-OCSP]: https://www.rfc-editor.org/rfc/rfc6960.html#section-4.2.2.2

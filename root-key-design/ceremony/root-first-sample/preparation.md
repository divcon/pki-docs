# Root와 First ICA 세레모니 — 준비 현황 샘플

**모두 가상 준비 기록입니다. 실제 프로젝트의 준비 완료·시험·외부 승인을 뜻하지 않습니다.** [행사 스크립트](script.md)의 조건부 가정을 설명합니다. 실제 자료가 없으면 S00에서 보류합니다.

## 먼저 정할 사항

| ID | 결정할 내용 | 반영할 문서 | 담당·기한 | 상태·결정 근거 |
|---|---|---|---|---|
| P01 | 테스트 환경, Root·First 생성/발급, 적용 범위 | script.md | P / 09-29 | 모의 확정, approved/scope.md |
| P02 | 역할 겸임 없음, A+B 본문 승인·O+A+B 토큰, W 첫날 입회 | script.md, settings.md | P/V / 09-29 | 모의 확정, personnel·witness |
| P03 | 가상 HSM 모델·모드, 공동 생성·관리 통제 | settings.md | H1/H2/V / 09-29 | 구현·적격성·우회 시험이 해결됐다는 가정 |
| P04 | Root/First 필드·발급 권한·프로파일 차이 | settings.md | P/A/B/V / 09-29 | 외부 차이 해결을 가정, 실제 회신은 없음 |
| P05 | 가상 실행기·독립 검사기·중단/재개 | runbook.md | O/V / 09-29 | 모의 정의, 실제 명령 구현 아님 |
| P06 | 로그·백업·off-site·보존·증거·운영 인수 | settings.md, evidence-index.md | C/V/R / 09-29 | 모의 계획 확정, 신규 키 백업은 현장 확인 |
| P07 | 리허설·거부/장애·복구·미비점 해소 | 이 문서 | P/O/V / 09-29 | 사전 해결을 전제로 하는 작성 예시 |

## 준비와 승인 자료

| 항목 | 내용 |
|---|---|
| 승인본 | DEMO-PACK-01 v2.0 / 아래 승인본 목록의 경로·버전·H 참조. 승인 스크립트와 수행 사본을 분리 |
| 준비 증거 | `approved/readiness.md` v1.0: 09-29 성공·거부·장애·복구 리허설 시나리오, W 입회 범위, 신규 키 백업 확인과 증거 보관 계획 |
| B00 선행 설정 인수 | `approved/bootstrap.md` v1.0: H1/H2 admin, O/A/B CU·승인키 등록·소유 증명, 임시 초기 접근 회수, 관리 quorum 2/2, 생성 통제와 단독 우회 시험 인수 |
| 역할 적격성 | `approved/personnel.md` v1.0: P/O/A/B/V/R/W/C/H1/H2 임명·적격성·교육 확인을 가정, 확인자 모의 인사보안담당01 / 09-29. 개인정보 원본은 제외 |

행사 수행 승인자는 [script.md의 행사 정보](script.md#행사-정보)에 기록합니다. 아래 `approved/` 경로는 고정 사본의 가상 보관 위치입니다. 이 폴더에 별도 파일이 있다는 뜻이 아닙니다.

## 리허설과 통제 시험

| 대상 | 확인할 내용 | 실행·검토 담당 | 결과·증거·미해결 사항 |
|---|---|---|---|
| 전체 순서 | 테스트 키 S00–S07, 보류·S00-R·인수·종료 | O/P/V/R/C, W 관찰 범위 검토 / 09-29 | 모의 완료 가정, approved/readiness.md |
| 생성 통제 T01 | 단독 생성 거부, 공동 개방, 각 키 검사·회수 | O/A/B/V / 09-29 | 기대 허용·거부 일치 가정, control-tests.json |
| 승인과 우회 T02–T05 | 정족수 부족·중복·다른 키/세션/본문, 관리자 교체·복구·코드 변경 | O/A/B/H1/H2/C/V / 09-29 | [권한표](settings.md#사람과-권한의-연결)의 모든 경로를 시험했다는 가정 |
| 서명과 검사 | Root 자기서명·First CSR·First 인증서, 고정 입력과 독립 검사 | O/A/B/V / 09-29 | 모의 완료 가정, 실제 프로파일 차이 해결 증거는 별도 필요 |
| 장애와 재개 T06 | 요청 전·전송 후·응답 유실·조립/저장 실패·중복 실행 | O/V/R / 09-29 | [장애 판정](runbook.md#작업-원장과-장애-판정)의 5개 경계 시험 가정 |
| 백업과 기록 | 격리 복구·현행 권한·off-site·로그·후속 서명·마지막 판정 보관 | H1/H2/C/V/R / 09-29 | 사전 시험 가정; 실제 신규 키 포함 검사는 회차별 기록에서 별도 판정 |

위 결과는 모두 작성 예시입니다. 실제 시험 증거를 만들거나 완료 상태로 옮기지 않습니다.

## 승인본 목록

승인본 목록도 가상입니다. 각 문서의 해시는 서명된 `approved/manifest.json`에 기록하고, 목록 자신의 해시·승인 서명은 별도 `approved/signatures.json`에서 연결하는 예시입니다.

| 승인본 구성 | 경로 / 버전 | 해시 참조·내용 |
|---|---|---|
| 행사 승인 원본 | `approved/script.md` / 2.0 | H(approved/script.md), 메인 진행 스크립트의 사전 승인본 |
| 문서 묶음·빈 기록 양식 | `approved/settings.md`, `approved/preparation.md`, `approved/records/record-template.md`, `approved/evidence-index.md` / 각 1.0 | 파일별 H; 승인 시점의 설정·준비 현황·빈 수행/증거 양식 |
| 설정·프로파일·범위 | `approved/config.json`, `approved/profile-review.md`, `approved/scope.md` / 각 1.0 | 파일별 H; [설정](settings.md)과 원문/schema 차이 검토 |
| 실행·검사 정의 | `approved/runbook.md`, `approved/tool-lock.json` / 각 1.0 | 파일별 H; CMD·G·Q·B·X 절차와 실행/검사 도구별 버전·해시·위치 |
| 준비·등록·인원 | `approved/readiness.md`, `approved/bootstrap.md`, `approved/personnel.md` / 각 1.0 | 파일별 H; 전제 확인, 시험, 개인별 권한 |
| 요청·승인 공개키 | `approved/request.json`, `approved/approvers/`의 개인별 SPKI DER / 각 등록 버전 1 | 파일별 H; 요청 권한·발급 승인과 O/A/B/H1/H2 등록키 대응, 개인키 제외 |
| 통제·장애·입회 | `approved/control-tests.json`, `approved/recovery.md`, `approved/witness.md` / 각 1.0 | 파일별 H; 이 문서의 시험 항목, 복구 경계, 독립성·관찰 범위 |
| 백업·보존·인계 | `approved/backup.md`, `approved/retention.md`, `approved/handover.md` / 각 1.0 | 파일별 H; 보관 위치·접근·기간·복구·운영 제한 |
| 공통 CloudHSM 절차 | `approved/cloudhsm-options.md` / 모의 승인 사본 1.0 | H(approved/cloudhsm-options.md); 프로젝트 [실행 부록](../cloudhsm-options.md)의 B00/G/Q/B01/X01 대응 |

이 폴더의 script/settings/runbook/preparation과 빈 records/record-template·evidence-index를 승인 시점에 고정 사본으로 내보냅니다. `approved/config.json` 등은 그 문서에 연결된 기계 입력·시험·원문 자료의 가상 참조입니다. session-01/session-02와 작성 후 evidence-index는 사후 기록이므로 사전 승인 완료로 소급하지 않습니다. 준비 문서 자신의 H는 별도 manifest에만 기록합니다.

## 시작 전 확인

사례에서는 P/V가 09-30에 P01–P07·준비 자료·시험 결과·승인 묶음을 확인하고 P가 16:00에 가상 행사 수행을 승인한 것으로 설정합니다. 현장에서는 S00에서 다시 대조합니다. **현재 프로젝트의 실제 미결정·미실시 상태는 [실제 행사 준비 현황](../root-first-001/preparation.md)에 남겨 둡니다.**

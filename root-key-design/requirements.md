# 요구사항과 확정 범위

## 확정 사항

| ID | 결정 | 적용 범위 |
|---|---|---|
| R01 | 서비스·기기 플랫폼의 ICA를 발급하는 공통 Root를 운영한다. 첫 대상은 C2PA다. | 콘텐츠 서명과 CA 서명 분리 |
| R02 | Global과 CN은 같은 Root를 사용한다. CN에 CloudHSM을 구축하지 않는다. | 중앙에서 서명하고 공개 인증서를 전달. 개인키를 CN에 복제하지 않음 |
| R03 | CA 발급은 저빈도이며 일상 발급에서 중앙 Root와 CN의 실시간 연결에 의존하지 않는다. | CSR·인증서 비동기 전달, 상태·신뢰 목록 배포 별도 |
| R04 | Root·공용 First 개인키를 Global AWS CloudHSM에 보관한다. | 같은 클러스터 사용은 검토 방향이며 미확정. 하위 CA 키 보관은 인계 대상 |
| R05 | Root → 공용 First ICA 하나 → 하위 Issuing ICA → leaf 구조를 사용한다. | 우리 측 Trust List 등록 인증서를 하나로 유지하는 목표. Claim/TSA 목록별 적용은 확인 필요 |
| R06 | C2PA CP를 공통 운영 정책의 주요 참고 자료로 사용한다. | 범용 Root의 자율 채택 통제와 C2PA 참여 CA의 의무 구분 |
| R07 | Root·First의 ICA 발급은 최소 2인이 통제한다. 두 키는 같은 담당자 그룹이 사용하고 그중 한 명이 실행한다. | N/M, 실행자의 승인 포함 여부, 실제 권한 설정은 미정. 개인별 계정 사용 |
| R08 | TSA ICA를 받은 운영 조직이 TSA 구현·운영을 맡는다. | 중앙은 인증서 발급·인계·증빙 조건 정의 |
| R09 | CRL을 발행하지 않고 OCSP를 사용한다. | 발급 CA별 응답자 위임·상태 배포·장애 처리 필요 |
| R10 | 단말의 신뢰 앵커 교체와 향후 PQC 전환을 설계한다. 현재 갱신 수단은 FOTA다. | 갱신·복구 상세는 별도 설계 |
| R11 | First는 중앙에서 운영한다. 중앙 운영팀이 있다면 그 팀이 맡는다. | 실제 조직명·담당자·승인 역할 배정은 보류 |
| R12 | 공용 First 아래 하위 ICA의 부서·용도별 구분을 고려한다. | 단말은 C2PA Trust List 기반으로 신뢰. 단말별 부서 허용 정책은 요구하지 않음 |
| R13 | 이번 ceremony에서 Root·First를 모두 신규 생성한다. | 하위 Issuing ICA는 이번 생성·감사 범위 밖이며 시스템 관리 대상 |

## 원문 검토로 추가한 필수 조건

아래는 C2PA CP v0.2와 Program에서 도출한 적용 조건이다. C2PA 참여 CA·제품에 해당하는 범위에 적용한다. 범용 G0에 공통 정책으로 채택한 항목은 [운영 모델](operating-model.md)에 별도로 표시하며, G0의 공식 적용 범위(V01)를 확정한 것으로 취급하지 않는다.

| ID | 조건 | 설계 위치 |
|---|---|---|
| N01 | 해당 CA가 이미 인증서를 발급한 키 쌍으로 새 인증서를 발급하지 않는다. Subscriber re-key는 신규 신청과 같은 검증을 거친다. | [새 키로 교체](operating-model.md#rekey) |
| N02 | CP 아래 발급한 모든 인증서의 기록을 각 인증서 만료 후 최소 1년 보존한다. serial·subject·유효기간·확장과 값·폐지 상태를 포함한다. | [기록 보존](operating-model.md#records) |
| N03 | Claim 인증서의 OCSP 응답은 필수 기록 보존 기간까지 제공한다. CRL을 사용하지 않으므로 하위 CA·TSU 인증서에도 OCSP를 제공한다. | [OCSP 운영](operating-model.md#ocsp) |
| N04 | 공식 CA 키 백업·복구 계획을 매년 검토한다. 모든 백업을 원본과 같은 다인 통제로 보호하고 off-site 사본을 유지한다. CA 개인키의 장기 아카이빙은 하지 않는다. | [백업·복구](operating-model.md#backup) |
| N05 | TSA의 시간 추적성·선언 정확도·오차 초과 시 발급 중단·전용 키·허용 해시를 적용한다. On-device는 TEE 실행·키 생성·보관 및 적어도 24시간마다 온라인 동기화 시도가 필요하다. Backend는 별도의 TSU 암호 장치 기준을 따른다. | [TSA 인계](operating-model.md#tsa-handoff) |
| N06 | 발급·폐지·접근·해당 시 attestation 검증 등을 감사하고, 기록 보호·정기 검토·검색·복원 절차를 둔다. 사업 관행은 공개 CPS 또는 C2PA와 협의한 다른 방법으로 고지한다. | [기록·공개 정책](operating-model.md#records) |
| N07 | Claim 발급의 제품 자격·Assurance Level·해당 시 Dynamic Evidence, Subscriber 식별·동의 및 키 생성·용도 제한을 하위 CA에 인계한다. CP의 폐지 사유를 처리할 경로를 둔다. | [발급 인계](operating-model.md#issuance), [폐지](operating-model.md#revocation) |
| N08 | Trust List 등록 증빙에는 인증서 프로파일 검증과 독립 입회한 키 생성 ceremony의 서명된 script를 준비한다. Program의 WebTrust 대체 증빙 예외는 해당 조건이 확인된 경우에만 사용한다. | [생성·등록 증빙](key-ceremony.md#생성-전-확인) |

근거 조항과 실제로 남은 검증은 [C2PA 요구사항 대응표](c2pa-requirements-matrix.md)에 연결한다. 위 목록은 CP 전체 의무를 빠짐없이 열거한 목록이 아니다.

## 남은 확인

| ID | 확인할 내용 | 관리 위치 |
|---|---|---|
| V01 | 미등록 상위 Root의 조항별 C2PA 적용·증거 범위. 포괄적인 의무 면제는 확인되지 않음 | [운영 모델](operating-model.md#hierarchy), [요구사항 대응표](c2pa-requirements-matrix.md) |
| V02 | First → TSA Issuing 계층의 issuer/AKI 해석과 Claim·TSA 신뢰 목록별 등록 조건 | [하위 ICA 설계](operating-model.md#subordinate-scope) |
| V03 | 생성·서명·관리자 우회·복구 통제, CLI 연동·알고리즘별 인증서 검증 | [다인 통제](dual-control-options.md#검증-기준) |
| V04 | 단말 신뢰 저장소·검증·갱신·오프라인·롤백·FOTA와 복구 권한 | [신뢰 앵커 교체](trust-anchor-migration.md) |
| V05 | PQC의 HSM·C2PA 프로파일·단말 검증기·업데이트 경로 지원 | [PQC 전환](trust-anchor-migration.md#7-양자내성-전환) |

Ceremony의 도구·프로파일·담당자·증거 관련 미정 사항은 [ceremony의 남은 결정](key-ceremony.md#남은-결정과-운영-인계)에서 관리한다. CA 앱은 작은 앱으로 구현하는 방향이며 서버/스크립트 형태·언어·DB·API는 미정이다. EC2·Lambda·S3·웹 승인 포털은 확정 구성이 아니다.

중앙은 Root/First 운영, 하위 CA 인계, 발급 인증서의 상태 제공, 기록·감사·복구와 신뢰 전환을 담당한다. 적용 조항별 절차·담당·증거 연결과 실제 구현 검증은 남아 있다.

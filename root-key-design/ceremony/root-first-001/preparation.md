# Root와 First ICA 세레모니 — 준비 현황

작성 중 · 실제 환경·담당자·일정·명령·리허설·승인은 미확정입니다. 행사별 준비 상태는 이 문서에서 관리합니다. 공통 확인 항목은 [준비 체크리스트](../preparation-checklist.md), 작성 방법은 [가이드](../script-writing-guide.md)를 참고합니다.

## 먼저 정할 사항

| ID | 결정할 내용 | 반영할 문서 | 담당·기한 | 상태·결정 근거 |
|---|---|---|---|---|
| P01 | 행사 범위·운영/테스트 구분·적용 원문 버전·등록 대상 | [script.md 행사 정보](script.md#행사-정보) | 미정 | 기준 결정 — 사용자 지정에 따라 운영용 행사·목적·범위·제외 대상·First 등록 계획·Program v0.2를 반영. 관련 CP v0.2·프로파일·schema 원문을 확인하고 아래 고정본으로 식별. 세부 통제·프로파일 해석 검토와 행사 수행 승인은 후속 항목에서 진행 |
| P02 | 참여자·겸임·정족수·대체자·독립 입회·승인 권한 | script.md 참여자, settings.md 권한표 | 미정 | 일부 결정 — 서명은 O·A·B의 `2 of 3` 확정. 이번 요청으로 키 관리도 같은 집합의 `2 of 3`, 관리자 user·quorum·cluster는 별도 관리자 3명의 `2 of 3` 기본안을 잠정 반영. [관리 통제](settings.md#키-관리와-관리자-통제) 참조. 실명·계정·승인키·겸임·대체자와 생성/AWS API 등의 정족수는 미정 |
| P03 | AWS/HSM 환경·모듈 적격성·생성 및 관리 통제 | [settings.md 환경과 보호 항목](settings.md#승인-설정) | 미정 | 일부 결정 — 모델·FIPS 모드·Level 3 및 N01 유지. 키 관리·관리자 quorum과 별도 통제 방향 잠정 반영. 생성 다인 승인 방향은 반영하되 상세 구현·정족수는 미확정(N02). 실제 인증 대응·구축·우회 시험 증거는 미완료 |
| P04 | 키·인증서 필드·First 요청·프로파일 차이 처리 | settings.md | 미정 | 일부 결정 — Root·First는 별도 EC P-384, ECDSA + SHA-384. 서명 전용·일반 반출 금지·보호 속성에 `modifiable=false`·`destroyable=false` 기본안을 잠정 추가. [N03](settings.md#n03-속성-잠금과-폐기-검증-조건)의 폐기 계획·잠금 시험 완료 전 운영 생성 금지. 라벨·인증서 필드·입력/조립·검사 결과는 미정 |
| P05 | 실제 명령·도구·입출력·검사·중단/재개 방법 | [runbook.md](runbook.md#실행-환경과-작업-흐름) | 미정 | 일부 결정 — 사용자 지정에 따라 작업자의 CLI 키 생성, 같은 전용 EC2의 별도 애플리케이션을 통한 요청·본문 작성, 작업자의 EC2 내부 파일 확인 후 CLI 서명 흐름을 반영. 작업 디렉터리·파일명·접근 권한·입력 대조 방법·조립 도구·실제 명령·버전·검사·장애 시험은 미정 |
| P06 | 로그·백업·복구·보존·증거 저장소·운영 인수 | settings.md, evidence-index.md | 미정 | 일부 결정 — 암호화된 클러스터 백업과 원본 같은 다인 통제. 복원/복사/삭제/보존 변경은 별도 승인 실행으로 설계하고 복원 후 현재 명단·quorum·잠금·접속 정책 대조 전 사용 금지. off-site·구체 정족수·권한·복원/폐기 시험·보존·인수 상세 미정 |
| P07 | 리허설·거부/장애 시험·미비점 해소·최종 행사일 | 이 문서, script.md | 미정 | 미정 |

결정한 값은 반영 문서에 한 번 기록하고, 이 표에는 위치와 결정·승인 근거를 연결합니다. 원문 요구·프로젝트 선택·외부 확인 필요 항목을 구분합니다.

## 특이사항과 보류 항목

| ID | 내용과 결정 위치 | 상태 |
|---|---|---|
| N01 | CP의 키 생성·저장 조항 사이 FIPS 판본 문구 차이와 선택 근거: [settings.md](settings.md#n01-cp의-fips-판본-문구-차이) | 특이사항 기록 완료. 모델·모드·보안 수준 선택 완료. 실제 인증 대응과 외부 해석·수용 근거는 미확인 |
| N02 | 키 생성 요청 자체의 승인과 생성된 키의 이후 quorum을 구분: [settings.md](settings.md#n02-키-생성-승인과-생성-시-quorum-설정의-구분). [키 생성 승인 검토안](key-generation-control-review.md) 참조 | 별도 다인 승인 실행의 방향 반영 / 정족수·인증 수단·구현 미확정. 기존 제안의 3인 승인 숫자는 미확정 |
| N03 | 속성 잠금과 폐기·복구 제약: [settings.md](settings.md#n03-속성-잠금과-폐기-검증-조건). 근거·대안·재검토 기록은 [키 관리 재검토 문서](key-management-control-review.md) 참조 | `modifiable=false`·`destroyable=false` 잠정 반영 / 폐기 계획·잠금 시험 미완료. 완료 전 운영 생성 금지 |

이번 요청으로 관리 권장안 전체를 초안에 반영했으나 실제 설정·시험·수행 승인은 아니다. M01–M08의 검토 책임자·기한과 판정은 [별도 재검토 기록](key-management-control-review.md#다시-검토할-항목과-판정-기록)에 남긴다. 기존 생성 검토안의 3인 승인 숫자나 AWS API 작업의 정족수를 자동 확정하지 않는다.

## 적용 원문 고정본

2026-10-11에 공식 공개본의 Program·CP 버전이 v0.2임을 확인했습니다. 이번 행사의 기준 판본은 사용자가 지정한 Program v0.2와 이에 대응하는 CP v0.2이며, 두 문서의 발행일은 2026-07-31입니다. 실제 검토·검사에 사용할 원문은 기존에 확보한 공식 저장소 `c2pa-org/conformance-public`의 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`, `docs/v0.2/` 아래 파일로 고정합니다.

이 commit은 사용한 원문 사본의 식별 정보입니다. Program·CP에서 규격 자료의 commit을 행사 문서에 기재하도록 요구하는 조항은 확인하지 못했으며, 여기서는 이후 같은 원문으로 검토를 재현하기 위한 프로젝트 관리 방식으로 기록합니다. SHA-256은 해당 commit의 파일 바이트에 대해 계산했고, 프로젝트 루트의 `conformance-public/`에 있는 로컬 사본과 바이트가 일치함을 확인했습니다. 원문 식별·해시 계산 완료와 행사 수행 승인은 별도로 관리합니다.

| 기준 자료 | 공식 원문 고정 링크 | SHA-256 |
|---|---|---|
| Conformance Program v0.2 | [C2PA Conformance Program.md][program-source] | `23c8dedd6e39238b3f4d0b8b2ba0bad38fe717a683146440f6354c6a58e50586` |
| Certificate Policy v0.2 | [C2PA Certificate Policy.md][cp-source] | `124fad3e3d578f40867557719f5599110a57be010e6aa4d3a3408695afdae77b` |
| Root CA 프로파일 | [rootCA.cert.yaml][root-profile-source] | `09152450a95f436fe46263db9d93bd8b35cc197a24236288565d52825fe7107d` |
| First Intermediate CA 프로파일 | [intermediateCa.cert.yaml][first-profile-source] | `0162741e4f074e498416570f975ec0a7dd4c48daf89fd99958990b1978765586` |
| Root 인증서 검사 schema | [rootCA.cert.schema.json][root-schema-source] | `e900db38176319baa7900a34ad59e616d03aeba16455fd765c6f48e8d0011ce2` |
| First 인증서 검사 schema | [intermediateCA.cert.schema.json][first-schema-source] | `036798fdedd1f44659532a7bcd556805519cab7cf23e6ea4e8d2a07c880bc8d8` |
| First CSR 검사 schema | [intermediateCA.csr.schema.json][first-csr-source] | `26836ba390da8b39d9634e4117c1567193066b958cc5436516c6cd8bf230f645` |

[program-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md
[cp-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[root-profile-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml
[first-profile-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml
[root-schema-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json
[first-schema-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCA.cert.schema.json
[first-csr-source]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCA.csr.schema.json

## 준비와 승인 자료

| 항목 | 내용 |
|---|---|
| 승인본 | {{스크립트_설정_명령_코드_도구_버전과_해시_목록}} |
| 준비 증거 | {{리허설_통제시험_입회_백업_증거보관_계획_참조}} |
| B00 선행 설정 인수 | 관리자 user·quorum·cluster 최종값 각각 `2`, 개인별 등록키·계정, 키 관리 집합 O·A·B, 생성/별도 통제·MFA·직접 우회 시험 / {{B00_실제설정과_시험증거}} |
| 역할 적격성 | {{역할임명_적격성확인_교육_유효상태_확인자와_일자}} |

실제 자료는 아래 목록과 [증거 목록](evidence-index.md)에 연결합니다. 행사 수행 승인자·시각·기록은 [메인 스크립트의 행사 정보](script.md#행사-정보)에 남깁니다.

## 리허설과 통제 시험

| 대상 | 확인할 내용 | 실행·검토 담당 | 결과·증거·미해결 사항 |
|---|---|---|---|
| 전체 순서 | 테스트 키로 S00–S07, 보류 후 S00-R, 인수·접근 종료 | 미정 | 미실시 |
| 생성 통제 | 생성 계획·명령 다인 승인과 제한된 CLI 실행, 직접 CLI·다른 호스트/SDK·관리자·코드 변경 우회 차단. 생성 시 quorum 설정과 생성 요청 승인을 구분 | 미정 | 방향 반영 / 정족수·인증 수단·구현 미정 / 미실시 |
| 서명 quorum | S02/S04/S05의 키별 사용 quorum `2`와 승인 가능 집합 O·A·B 조회. 테스트 키로 O+A·O+B·A+B 승인 성공, 승인 0명·1명·동일인 중복·집합 밖 승인으로 인원 충족 시 거부 확인 | 미정 | `2 of 3` 결정 / 실제 설정·시험 미실시 |
| 개인키 용도·추출 | 생성 직후 서명 전용·`extractable=false`·`sensitive=true`·`token=true` 조회. 정상 세션과 충분한 승인 조건에서도 일반 wrap/export·금지 용도 거부 확인 | 미정 | 기존 정책 유지 / 실제 설정·시험 미실시 |
| 키 관리 quorum / M01·M03 | 사용/관리 각각 `2`와 O·A·B 명단·소유/공유·등록키 조회. 2명 승인 허용, 단독·중복·집합 밖 승인 거부, 소유자 전용 권한 확인, 공유 감소·추가와 다른 SDK 우회 시험 | 미정 | 기본안 잠정 반영 / 미실시 |
| 속성 잠금·삭제·폐기 / M02·M07 | 테스트 키의 `modifiable=false`·`destroyable=false` 조회, 충분한 승인에서도 잠긴 속성 변경 거부, 소유자 삭제 거부. 키·백업/사본 폐기 경로와 공유 클러스터 영향 검증 | 미정 | 기본안 잠정 반영 / 폐기 계획 미정·미실시 / 운영 생성 전 필수 |
| 관리자 quorum / M04 | 모든 HSM의 user·quorum·cluster 최종값 `2`와 관리자 3명·등록키 대조. 단독 사용자·비밀번호/MFA·정족수·mTLS 변경 거부와 2명 승인 허용. 초기 설정 보호 확인 | 미정 | 기본안 잠정 반영 / 관리자 미정·미실시 |
| 등록키·별도 실행 통제 / M05·M08 | 승인 공개키 등록/교체의 신원·지문·명단 전후 대조. IAM/SCP/호스트 권한과 승인 실행 연결, 직접 API·권한 정책·승인 검사 코드 변경 우회 차단 | 미정 | 방향 반영 / 정족수·구현 미정·미실시 |
| 복원과 승인자 교체 / M03·M06 | 잠긴 키의 공유·공유 해제·승인자 교체 동작. 백업 포함·복원 후 동일 공개키·잠금·현재 승인 집합/등록키·두 키 quorum·관리자 서비스·접속 정책 확인. 대조 전 사용 차단 | 미정 | 미실시 |
| 승인과 우회 | 승인 부족·동일인 중복·관리자/승인키 변경·직접 접속·호스트/코드 변경 | 미정 | 미실시 |
| 서명과 검사 | Root·First 공개키의 EC P-384 확인. Root 자기서명·First CSR·First 인증서의 ECDSA + SHA-384, 입력/키 일치, raw/digest에 따른 단일 해싱, 서명 DER 변환·식별자·프로파일 검사. 입력 변경·키/프로파일 불일치 시 중단 | 미정 | 알고리즘 선택 완료 / 실제 설정·시험 미실시 |
| 장애와 재개 | 요청 전·전송 후·응답 유실·저장 실패·중복실행, 같은 응답에서 복구 | 미정 | 미실시 |
| 백업과 기록 | 신규 키·최종 권한·off-site·복구·전체 로그·후속 서명·마지막 판정 보관 | 미정 | 미실시 |

## 승인본 목록

문서·설정·명령·검증 도구와 참조 부록을 하나의 승인 묶음으로 고정합니다. 아래는 **목록 양식**이며 아직 승인이나 해시 계산을 수행하지 않았습니다.

| 대상 | 파일 또는 보관 위치 | 버전·commit | SHA-256 | 검토·승인 기록 |
|---|---|---|---|---|
| 메인 스크립트 | [script.md](script.md) | 미정 | 미계산 | 미승인 |
| 설정 | [settings.md](settings.md) | 미정 | 미계산 | 미승인 |
| 실행 절차 | [runbook.md](runbook.md) | 미정 | 미계산 | 미승인 |
| 준비·리허설 | 이 문서의 승인 직전 고정 사본과 연결된 시험 자료 | 미정 | 미계산 | 미승인 |
| 수행 기록 양식 | [records/record-template.md](records/record-template.md) | 미정 | 미계산 | 미승인 |
| 증거 목록 양식 | [evidence-index.md](evidence-index.md) | 미정 | 미계산 | 미승인 |
| 관리 통제 재검토 기준 | [key-management-control-review.md](key-management-control-review.md)의 고정 사본과 M01–M08 검토·시험·판정 자료 | 미정 | 미계산 | 기본안 잠정 반영 / 재검토·시험 미완료 |
| 생성 통제 검토 기준 | [key-generation-control-review.md](key-generation-control-review.md)의 후속 확정 사본과 구현·시험 자료 | 미정 | 미계산 | 방향 반영 / 정족수·구현 미확정 |
| 실행 코드·CLI·검증 도구·설정 파일 | runbook.md에서 정할 실제 파일/패키지별 항목 추가 | 미정 | 미계산 | 미승인 |
| 공통 CloudHSM 부록 | [cloudhsm-options.md](../cloudhsm-options.md)의 승인 대상 고정 사본 | 미정 | 미계산 | 미승인 |
| 적용 원문·프로파일·검사 기준 | [적용 원문 고정본](#적용-원문-고정본)의 7개 파일 | 위 고정본 참조 | 위 파일별 계산값 참조 | 원문 식별 완료 / 세부 적용 검토·행사 승인 묶음 편입 미완료 |

승인 시 목록을 별도 고정 파일로 내보내고 서명은 그 목록의 해시를 참조합니다. 목록에 자기 해시나 이후 서명 파일을 넣지 않습니다. 이 문서의 해시가 필요하면 승인 직전 고정 사본을 대상으로 하여 결과를 별도 목록에 기록합니다. 승인 후 변경은 영향 검토·필요한 재시험·재승인과 새 버전으로 관리합니다.

## 시작 전 확인

- [ ] 행사 전 확정 항목에 미정 값이나 가상 참조가 없습니다.
- [ ] 담당자·정족수·입회 범위·역할 자격과 시작/중단/재개 권한을 확인했습니다.
- [ ] 환경·설정·실제 명령·검증 도구를 정하고 리허설 결과를 확인했습니다.
- [ ] 단독 우회·입력 변경·장애·백업 복구 시험의 미비점을 해소했습니다.
- [ ] M01–M08의 재검토·시험 결과를 확인했고, 폐기 경로·공유 클러스터 영향과 잠금/삭제 거부 검증을 완료했습니다. 잠금 기본안 변경은 근거·재시험·변경 승인에 연결했습니다.
- [ ] 키 사용/관리·관리자 quorum의 최종값과 개인별 승인 집합을 대조하고, 생성·AWS API·호스트/코드·등록키의 별도 승인 실행·직접 우회 차단을 확인했습니다.
- [ ] 적용 범위와 발급에 영향을 주는 프로파일 해석·외부 확인을 완료했습니다.
- [ ] 기록·증거 저장소·백업·보존·조회·인수 준비를 확인했습니다.
- [ ] 승인 묶음의 버전과 해시를 고정하고 참가자에게 같은 버전을 배포했습니다.

수행 결과·서명·심사 통과를 미리 완료로 표시하지 않습니다. 실제 행사는 [script.md](script.md), 수행 후 판정은 [회차별 기록](records/record-template.md#확인-서명과-최종-판정)에서 관리합니다.

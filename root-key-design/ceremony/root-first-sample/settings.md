# Root와 First ICA 세레모니 — 설정 샘플

조건부 가상 값입니다. 행사·참여자는 [script.md](script.md), 승인본은 [preparation.md](preparation.md#승인본-목록)에서 식별합니다.

## 승인 설정

| 항목 | Root | First ICA |
|---|---|---|
| 키 알고리즘·곡선 | EC P-384 | EC P-384, Root와 별개 키 |
| 키 라벨·속성·소유·공유 | example-root-g1 / 아래 공통 속성 / O 소유, A/B 공유 | example-first-g1 / 같은 공통 속성 / O 소유, A/B 공유 |
| Subject / Issuer DN | C=KR, O=Example Platform, CN=Example Platform Root CA G1 / Subject와 동일 | C=KR, O=Example Platform, CN=Example Platform First ICA G1 / Root Subject |
| 서명 알고리즘·입력 형식 | ECDSA with SHA-384 / 고정 TBSCertificate DER를 raw 입력 | ECDSA with SHA-384 / CSR은 CRI DER, 인증서는 TBS DER를 raw 입력 |
| 유효기간 UTC | 2026-10-01 00:00:00–2036-10-01 00:00:00 | 2026-10-01 00:00:00–2031-10-01 00:00:00 |
| Serial 생성·중복 방지 규칙 | CSPRNG 16바이트, 양수·비영 확인, issuer별 원장에 원자적 예약 / [첫 회차의 현장 예시 값](records/session-01.md#실제-수행-기록) | 같은 규칙 / Root issuer의 원장에서 중복 검사·예약 |
| SKI / AKI | SKI: RFC 5280 Method 1 / AKI: Root SKI의 keyIdentifier / 모두 non-critical | SKI: First 공개키의 Method 1 / AKI: Root SKI의 keyIdentifier / 모두 non-critical, 해석 조건은 아래 참조 |
| KU / EKU | critical keyCertSign·cRLSign / EKU 생략 | critical keyCertSign·cRLSign / EKU 생략 |
| Basic Constraints / pathLen | critical, CA=TRUE / 2 | critical, CA=TRUE / 1 |
| 정책 OID | Certificate Policies 생략 | non-critical, 1.3.6.1.4.1.62558.1.1, qualifier 없음 |
| AIA / CDP | 모두 생략 | non-critical AIA: OCSP `http://ocsp.example.com/root`, caIssuers `http://pki.example.com/root-g1.cer` / CDP 생략 |
| 기타 확장·critical 여부 | v3; 위에 없는 확장은 없음 | v3; 위에 없는 확장은 없음, CSR 요청 확장을 자동 복사하지 않음 |

공통 속성의 **가상 선택값**은 개인키의 영구 보관·민감 속성·서명 허용, 비추출, 파생 금지, 변경/삭제 허용(별도 다인 승인 경로로 제한), 사용·관리 quorum 각 3입니다. 공개키는 영구 보관·검증 허용입니다. 실제 옵션 이름·지원 조합은 선정한 HSM/CLI에서 검증해 `approved/config.json`과 runbook에 고정해야 합니다. 이 표는 실제 제품에서 이 조합을 시험했다는 뜻이 아닙니다.

설정 원본은 `approved/config.json` v1.0, 해시는 H(approved/config.json)입니다. 증거용 파일 해시·SPKI 지문은 SHA-256이고, 인증서 SKI의 SHA-1 및 서명용 SHA-384와 구분합니다.

프로파일 검토는 `approved/profile-review.md` v1.0입니다. [Root 프로파일][root-profile]과 [First 프로파일][first-profile] 및 같은 commit의 schema를 대조합니다. First AKI의 원문 표현과 발급자 Root SKI를 사용하는 해석의 차이는 실제 외부 확인 대상입니다. **이 샘플의 전체 흐름은 그 확인이 사전에 끝난 상황을 가정할 뿐, 현재 확인 완료나 C2PA의 수용을 주장하지 않습니다.** 실제 회신·해결 근거가 없으면 S00에서 중단하고 S05를 실행하지 않습니다. 실패 항목을 제외해 프로파일 통과로 바꾸지 않습니다.

| 환경과 보호 항목 | 승인값 또는 근거 |
|---|---|
| AWS 계정·리전·클러스터·HSM 모델·모드·적격성 | 가상 계정 DEMO-AWS-01, ap-northeast-2, DEMO-CLUSTER-01, 노드 DEMO-HSM-A/B / 모델 DEMO-MODEL-A·모드 DEMO-MODE-F의 가상 적격성 자료를 B00에서 대조하는 설정. 실제 AWS 모델명·인증 번호·지원 여부를 대신하지 않음 |
| 실행 호스트·접근·네트워크·코드·검증 도구 | 실행 DEMO-HOST-O, 독립 검사 DEMO-HOST-V, 승인 단말 DEMO-DEVICE-A/B/O / 격리망·개인 접속 / 도구는 [실행 작업 정의](runbook.md#실행-작업) |
| 생성 통제·사용/관리 정족수·우회 시험 | A+B가 승인된 코드·설정·O 계정·작업 ID에 한정한 생성 접근을 열고 V 확인 후 O 실행 / 사용·관리 3/3 / [T01–T06 사전 시험](preparation.md#리허설과-통제-시험) |
| 개인 계정·승인 키·활성화 재료 | 각 CU/admin의 자격과 승인키는 본인 장치의 별도 보호영역. 공개키 지문만 B00에 연결. 개인 접속 MFA 사용을 가정, HSM 사용자 MFA 기능은 이 사례에서 미채택으로 명시 |
| 입회·시간·로그·증거 보존·접근 통제 | W가 첫날 생성·서명·검사를 직접 관찰, 비밀 입력 구간은 기록 차단 / UTC 원천을 KST로 표시, 모의 허용 시각 차 ±1초 / 증거는 R 추가·V 검사·C 보관 |
| 로그 수집·검토 | HSM별 관리, AWS 관리, 호스트, 실행기 요청/응답, 개인 승인 기록을 작업 ID·계정·키·시각으로 대조. 모의 수집 지연 허용 15분, 초과 시 완료 보류 / V 검토 |
| 인증서 발급 기록 보존 | Root 원장은 2037-10-01 00:00 UTC 이후, First 원장은 2032-10-01 00:00 UTC 이후까지. 만료 후 최소 1년을 반영한 예시; 폐기 전 추가 의무 재검토 |
| 기타 기록 보존 | 이 사례는 스크립트·수행·승인·일탈·증거·감사로그·도구 사본을 행사 종료부터 2037-10-02 03:00 UTC까지 보존하는 모의 정책 채택. C 관리, P/V 승인 없는 수정·삭제 차단. 조회·복구 확인은 E06b/E07. 이는 C2PA가 모든 기록에 정한 단일 기간이 아님 |
| 생성 직후 보호·백업·off-site·복구 | C가 각 생성 직후 보호 인수. 신규 두 키와 최종 권한 포함을 확인한 암호화 백업 및 DEMO-SITE-B 사본. off-site 적합성과 원본 수준의 다인 통제를 사전 검증했다는 가정; 백업 상태명만으로 완료 처리하지 않음 |
| 키 외 중요 자료 백업 | 원장·설정·로그·승인·도구·증거 목록을 E06b에서 확인하고, 이후 서명·종료·최종 판정은 E07 후속 보관까지 확인 |
| 종료 시 접근 유지·회수 | HSM O/A/B 계정·키 소유/공유·quorum은 유지. 임시 생성/서명 접근, 실행 세션, 작업 토큰, 임시 호스트/IAM 권한은 회수. C도 단독 서명 권한 없음 |
| First 요청 권한·발급 허가 | `approved/request.json` v1.0: 모의 플랫폼 조직의 First 요청, P 신원·권한 검토, A+B 발급 승인 / H(approved/request.json) |
| 장소 보안·행사 후 물리 보관 | HSM 현장 물리 보관 항목은 클라우드 가정으로 비적용 근거 기록. 통제실 출입·화면 노출은 P 관리, 개인 승인 장치는 각자 보관. 클라우드 자격·승인키 보호는 계속 적용 |

## 사람과 권한의 연결

| 사람·역할 | CU 또는 admin 계정·승인 공개키 지문 | Root와 First 소유·공유 | 허용 작업·승인 집합 | 등록·교체·복구 권한과 부정 시험 |
|---|---|---|---|---|
| O 실행 | demo-cu-o / H(approved/approvers/o.spki.der) | 두 개인키 소유 | 공동 접근 후 생성; O+A+B 사용/관리 승인 1표와 실행 | 본인 등록 절차만, 타인 키 교체 불가 / T01·T02·T03 |
| A 승인 | demo-cu-a / H(approved/approvers/a.spki.der) | 두 개인키 공유 | A+B 본문 승인, 생성 접근 1표, O+A+B 사용/관리 1표 | 타인 자격·배포·복구 권한 없음 / T01·T02·T03 |
| B 승인 | demo-cu-b / H(approved/approvers/b.spki.der) | 두 개인키 공유 | A와 동일하되 별도 개인 | A와 비밀·장치 공유 안 함 / T01·T02·T03 |
| H1/H2 관리자 | demo-admin-1·2 / 각각 H(approved/approvers/h1.spki.der), H(approved/approvers/h2.spki.der) | CA 키 소유/공유 없음 | 관리자 user/quorum 각각 2, 복구·설정 변경 공동 수행 | 한 명의 사용자·승인키 교체, quorum 저하, 복구로 권한 우회 거부 / T03·T04 |
| P/V/R/W/C | demo-p·v·r·w·c / CA 승인키 없음 | 없음 | 진행/검사/기록/입회/보관만, C는 복구 요청 가능 | CU/admin 자격 대행·단독 복구·서명 불가 / T04·T05 |

| 통제 행위 | 각자 보유·보호할 재료와 권한 | 단독으로 수행할 수 없는 이유 | 허용·거부 시험 및 당일 확인 |
|---|---|---|---|
| 생성·생성 접근 활성화 | O 개인 CU 접근, A/B 각각 별도 생성 접근 승인 수단 | 가상 접근 중개기가 A+B의 동일 작업·설정 승인을 확인해야 O의 제한된 실행 경로를 개방. 임의 셸·직접 접속·관리자 변경 경로도 별도 공동 통제 대상으로 둠 | T01: O·A·B 각 단독 접속/생성 거부, A+B 승인 후 O의 지정 작업만 허용 / G01 확인, G05 회수·재접속 거부 |
| 서명·키 관리 | O/A/B 각각 개인 승인키, 본문은 A+B가 별도로 승인 | 3명 토큰 승인과 승인 본문 재대조가 필요. 공유 CU의 직접 서명·관리 경로도 시험 | T02: 1/2명, 동일인 중복, 다른 키·세션·본문 모두 거부; 3명 정상 조합만 허용 / 매 Q02–Q06 |
| 관리자·승인키 등록/교체 | H1/H2 각 개인 관리자 자격과 승인키, CU는 본인 소유 증명 | H1/H2 공동 통제 및 사람-계정-키 원장 변경 검토, 초기 접근 회수. 승인키 자체에 대한 사후 교체 경로도 검증 | T03: 단독 등록/교체/quorum 저하와 초기 자격 재사용 거부 / B00와 S00 |
| 백업 복원·삭제·호스트 변경 | C 복구 요청, H1/H2 공동 복구 접근, A+B 코드·설정 승인 | 복구 환경은 격리하고 현행 사람/키/quorum 대조 전 업무 접근 금지. 배포·호스트·백업 삭제도 단독 변경 경로를 차단하는 가정 | T04: 과거 권한 복원·단독 백업 삭제 거부, T05: 승인되지 않은 호스트/코드 변경 거부 / B01·X01 |

위의 접근 중개기와 공동 변경 통제는 **가상 구현의 동작 정의**이며 AWS 기본 기능만으로 제공된다는 설명이 아닙니다. 지식 분리는 한 사람이 타인의 승인키·접근·복구 재료를 확보하지 못하도록 하는 보관·권한 분리로 설명하고 `approved/control-tests.json`에 검토 근거를 연결합니다. CA 개인키를 세 조각으로 나눴다는 뜻이 아닙니다. 노드 A/B의 복제 확인과 사람 O/A/B의 승인 정족수는 별개입니다.


## 최종 보관 기준

최종 자료와 마지막 판정까지의 보존·복제 계약은 `approved/retention.md`와 `approved/backup.md`입니다. 추가 자료는 새 버전/후속 항목으로 기록하고 기존 서명 대상을 변경하지 않습니다. 최종 저장·복제 결과를 확인할 수 없으면 완료 대신 `최종 기록 보관 대기`로 남깁니다.

[root-profile]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml
[first-profile]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml

# CA 앱 기능 목록

- 상태: **기능 검토안 — 서버·스크립트 형태와 구현 기술 미정**
- 범위: Root·공용 First 생성·발급, 승인·증거 관리, 이후 하위 ICA 관리

CA 앱은 아래 기능을 제공한다. 직접 구현할 부분과 기존 라이브러리·CloudHSM·외부 시스템에 연결할 부분은 구현 단계에서 정한다.

구성요소는 CloudHSM, 발급 앱과 실행 호스트, 승인·발급 원장, 증거 저장소다. 앱은 인증서 내용을 결정하고 HSM 서명 결과로 인증서를 완성한다. 호스트·네트워크·저장소의 구체적인 제품과 배치는 미정이다.

## 1. 작업을 준비한다

| 기능 | 앱이 해야 할 일 | 잘못됐을 때 |
|---|---|---|
| **A01. 작업·설정 등록** | 작업 ID, 생성/발급 목적, 대상 CA, 정책·프로파일·스크립트·도구 버전과 입력값을 기록한다. 승인된 설정 변경도 이력으로 남긴다. | 필수값·적용 기준이 미정이면 실행하지 않는다. |
| **A02. 시작 전 확인·리허설** | 테스트/운영 환경, 연결할 HSM, 참여자·입회 준비, 시간·기록 저장·보호 설정과 사전 확인 증거를 대조한다. 테스트 키로 사전 연습할 수 있게 한다. | 환경·증거 수집·필수 통제 준비가 안 되면 키 생성/서명을 막는다. |
| **A03. 사용자·권한 확인** | 개인별 신원을 확인하고 실행·승인·조회·관리 권한을 검사한다. MFA와 권한 부여·회수 기록은 외부 인증 체계와 연결할 수 있다. | 권한 없는 실행·승인·설정 변경을 거부한다. |

동일 담당자 그룹을 사용하더라도 개인별 계정과 작업별 역할을 구분한다. 앱 밖에서 HSM에 직접 접근해 통제를 우회할 수 없도록 하는 것은 HSM·실행 환경의 책임이며, A02에서 확인 결과를 연결한다.

## 2. 키와 발급 요청을 준비한다

| 기능 | 앱이 해야 할 일 | 잘못됐을 때 |
|---|---|---|
| **A04. 키 생성·식별** | 생성 요청·설정의 승인과 다인 통제를 확인한 뒤 HSM에 생성을 요청한다. 공개키·지문·키 식별자·속성·권한을 기록하고 Root와 First가 다른 키인지 확인한다. | 승인·통제 부족, 잘못된 환경·키·설정이면 사용을 보류한다. 결과 불명 시 기존 키부터 확인한다. |
| **A05. CSR 생성·요청 검사** | First CSR 생성과 필요한 키 사용 승인을 거친 서명을 연결한다. 접수 CSR의 형식·서명·공개키·요청값과 요청 권한·발급 허락·정보 확인 증거를 검사한다. | CSR 오류, 권한·근거 누락, 예정된 키와 불일치하면 거부한다. |
| **A06. 발급 규칙·인증서 내용 결정** | 발급 CA와 인증서 종류를 확인하고 승인된 프로파일로 이름·기간·serial·알고리즘·확장 필드를 결정한다. CSR 값을 무조건 복사하지 않는다. | 금지된 용도·계층, 부적격 발급 CA, 미해결 프로파일이면 서명을 막는다. |

Root 자기서명에는 외부 CSR이 필요하지 않다. 키는 라벨만으로 구분하지 않고 실제 공개키와 대조한다. 앱은 **임의 데이터 서명, 개인키 평문 반출, HSM 장애 시 로컬 개인키 대체** 기능을 제공하지 않는다.

## 3. 승인받고 발급한다

| 기능 | 앱이 해야 할 일 | 잘못됐을 때 |
|---|---|---|
| **A07. 승인 수집·실행 연결** | 생성은 대상 HSM·키 설정, 서명은 사람이 확인한 내용·실제 서명 본문·키를 승인 대상으로 고정한다. 승인자의 자격·개별 신원·승인 수·유효성을 확인하고 실행 통제와 연결한다. | 승인 부족·중복 계수·취소·만료·재사용을 거부한다. 내용·키·프로파일·실행 설정 변경 시 기존 승인을 무효화한다. |
| **A08. 서명·인증서 완성·검증** | 승인된 작업에 대해 HSM 서명을 요청한다. 인증서를 조립하고 서명·공개키·승인 내용·프로파일·인증 경로를 검사한다. | 오류·불일치가 있으면 완료나 배포로 처리하지 않는다. |

A07은 키 생성·CSR 서명·인증서 서명 **각 작업 전에 적용하는 공통 기능**이다. 생성 시 다인 통제와 생성된 키의 사용 quorum은 서로 다른 통제다. 작업을 실행하는 한 명과 필요한 승인 인원은 구분하며, 한 번의 행사 시작 승인이 모든 키 사용 승인을 대신하지 않는다. Root·First의 허용 용도만 사용하며 First에서 Claim Signing·TSA leaf를 직접 발급하지 않는다.

서명 입력과 승인의 연결, CLI 세션, 승인용 키·관리자·퇴사 통제는 [다인 통제](dual-control-options.md)를 따른다. HSM의 승인 인원 검사가 인증서 내용 검증을 대신하지 않는다.

## 4. 상태와 증거를 남긴다

| 기능 | 앱이 해야 할 일 | 잘못됐을 때 |
|---|---|---|
| **A09. 발급 원장·중복 방지** | 발급 CA+serial, 공개키, 인증서 원본, subject·기간·확장값·상태를 저장·조회한다. 이미 발급한 키와 중복 요청을 확인하고 동시 실행을 통제한다. | 중복 serial, 동일 키에 대한 금지된 새 인증서 발급, 발급 인증서 수정을 막는다. |
| **A10. 중단·결과 확인·재개** | HSM 호출 전에 작업 상태를 저장한다. 연결 단절, 프로세스 종료, 서명/키 생성 후 저장 실패를 구분하고 기존 HSM 결과·원장·증거를 대조해 재개 판단을 기록한다. | 결과가 불명확하면 자동 재생성·재서명하지 않는다. 원래 결과 확인 또는 승인된 후속 처리가 필요하다. |
| **A11. 감사 기록·보호·조회** | 성공·실패·거부·접근 시도·권한/설정 변경의 수행자·시각·입력·결과를 기록한다. 원장·로그·증거를 보호해 저장하고 검색·조회·내보내기를 제공한다. | 기록 저장이나 무결성 확인 실패 시 작업을 보류한다. 비밀번호·개인키·승인 비밀은 저장하지 않는다. |
| **A12. Ceremony 완료·인계** | 승인된 스크립트, 환경·키 생성·입회·발급·검증 기록, 일탈 처리와 참여자/입회자 서명을 모은다. 결과물 전달과 인수, 접근 종료를 기록한다. | 필수 증거·확인 서명이 빠지면 완료·배포를 막는다. ceremony·운영 준비·감사·등록 상태를 따로 표시한다. |

발급 인증서 기록은 **만료 후 최소 1년** 보관한다. 다른 로그·증거의 보존 기간은 별도 정책을 적용한다. 무단 변경·삭제 방지는 저장소 권한·보호 기능까지 연결해야 한다. 기존에 완성한 인증서를 다시 내려받는 것은 새 인증서 발급과 구분한다.

## 5. 생성 이후에도 관리한다

하위 ICA도 관리 대상이다. 아래 기능은 사용을 시작하는 시점까지 준비하며, 이번 Root·First 생성 행사에 하위 키 생성을 추가하지 않는다.

| 기능 | 앱이 해야 할 일 | 외부 시스템·절차와의 경계 |
|---|---|---|
| **A13. 하위 ICA 등록·관리·발급** | CA·인증서·공개키·상위 관계·운영 조직·담당자·적용 정책·상태·준수 증빙·미해결 과제를 관리한다. 이후 하위 발급은 A05~A12의 검사·승인·기록을 사용한다. | 하위 개인키를 중앙에서 생성·보관한다고 가정하지 않는다. 하위 유형별 프로파일 확정 전 발급은 보류한다. |
| **A14. 폐지 요청·상태 반영** | 폐지 사유·요청 권한·검증 시각·처리 기한을 기록하고 승인된 상태 변경을 원장에 반영한다. 상태 제공 시스템에 전달하고 공개 반영·오류·재처리를 추적한다. | OCSP 응답 서버는 별도로 둘 수 있다. 외부 전달만으로 공개 반영 완료를 표시하지 않는다. |
| **A15. OCSP 응답자 인증서 관리** | 발급 CA에 맞는 OCSP 응답자 CSR·프로파일·승인·발급·만료/교체를 관리한다. A05~A12의 공통 기능을 사용한다. | 상태 서비스 운영에 필요한 조건부 작업. 이번 Root·First만 생성하는 행사에 자동 추가하지 않는다. OCSP 응답 서명은 응답자 서비스가 수행한다. |
| **A16. 만료·교체·사용 중지** | 키·인증서의 상태를 확인해 중지·침해·폐지·만료된 CA의 신규 발급을 차단한다. 교체·운영 종료 시 영향받는 하위 CA·상태 서비스·인계 과제를 추적한다. | 새 키·새 인증서와 기존 이력을 연결한다. Root 신뢰 제거·등록 변경·단말 배포는 외부 절차로 인계한다. |
| **A17. 백업·복구 확인** | 원장·설정·로그·증거를 보호된 백업에 연결하고 복구 후 상태 일치를 확인한다. HSM 키 백업의 식별·보관 위치·책임·검증 결과를 참조한다. | CA 키 백업·복구는 HSM 운영이 담당한다. 원본과 같은 다인 통제·평문 반출 금지·보관 조건을 확인하며, 키 장기 archive 기능과 혼동하지 않는다. |

## 6. 이 앱과 별도로 책임을 정할 일

| 대상 | 별도 책임 | 앱이 연결할 것 |
|---|---|---|
| **생성 당시 통제** | 실제 독립 입회, HSM 적격성·환경 보호, 인력 자격·역할 분리, 운영 승인 | A02·A12에서 당시 증거와 확인 결과 연결 |
| **지속 보안 운영** | 권한 정기 검토, 로그 점검, 업데이트·변경 승인·네트워크 보호, 사고 대응·운영 종료 | A01·A03·A11·A16·A17에서 설정·이력·조치·인계 기록 연결 |
| **OCSP 상태 서비스** | 상태 응답 생성·서명·공개·가용성 운영 | A14·A15에서 상태 원장·응답자 인증서·반영 결과 연결 |
| **Claim Signing·TSA leaf 발급/서비스** | 가입·계약·제품 적합성·해당 Assurance Level 증거 검증·재인증, TSA 운영 | A13에 책임 조직·적용 정책·증빙·인계 과제 연결 |
| **감사·Trust List 등록** | 적용 조항 판단, 심사·증빙 제출·시정 | A11·A12에서 자료와 제출 상태 제공 |

## 7. 준비 시점

| 시점 | 필요한 기능·외부 준비 |
|---|---|
| 운영 키 생성 전 | A01~A04·A07·A09~A12의 생성 경로, 실제 다인 통제·적격 모듈·권한/MFA·입회·기록 준비 |
| 인증서 서명 전 | A05~A10의 발급 경로, 확정 프로파일·상태 조회 주소. 검사 항목은 [ceremony 설정표](ceremony/certificate-issuance.md#certificate-settings) 적용 |
| 생성 직후부터 | 키·원장·로그·증거 보호와 A17의 백업 책임 |
| 상태 서비스 제공 전 | A14·A15와 외부 OCSP 서비스 연동 |
| 하위 ICA 발급 전 | A13의 운영 조직·프로파일·준수 증빙, A05~A12·A14~A17 재사용 및 인계 |

Subscriber/C2PA 폐지 요청은 요청자 인증과 유효성 검증 완료 후 72시간 이내 처리한다. 앱은 검증 시각·기한과 실제 공개 반영을 추적한다. 미만료 인증서 상태 저장소의 24×7 공개와 Claim OCSP의 필수 기록 보존 기간까지 제공은 외부 서비스의 책임으로 연결한다. [CP 요청 검증][revocation-request] · [CA 책임][representations] · [상태 서비스][status]

Claim 하위 서비스의 가입·제품 자격·Assurance Level·조건부 Dynamic Evidence·최대 398일 내 재인증, TSA의 시각·전용 키·토큰 발급은 [운영 인계 조건](operating-model.md#issuance)을 적용한다. 이 앱이 Claim 개인키를 생성하거나 leaf 발급 업무 전체를 수행하지 않는다.

<a id="기능-검증"></a>

## 8. 기능 검증

구현 후 테스트 키로 수행할 기준이다. HSM·관리자 우회 시험은 [다인 통제 검증](dual-control-options.md#검증-기준)에서 관리한다.

| 사례 | 기대 결과 |
|---|---|
| 잘못된 환경·같은 라벨의 다른 키·Root/First 혼동 | 공개키·환경 대조에서 차단 |
| 권한 없는 요청·잘못된 CSR 서명·비허용 필드·부적격 issuer | HSM 서명 전에 거부 |
| 승인 후 본문·키·프로파일·실행 설정 변경 | 기존 승인 무효화·재승인 |
| 동일인 중복·다른 작업·만료/취소/재사용 승인 | 승인 인원에 포함하지 않고 차단 |
| 동시 요청·중복 serial·이미 발급한 키의 새 인증서 요청 | 중복·금지된 재발급 차단 |
| 생성/서명 중 단절·HSM 성공 후 저장 실패 | 결과 불명으로 보류, 기존 결과·원장 대조 전 재실행 금지 |
| 검사 실패·증거 누락·기록 저장 실패 | 완료·배포 차단, 상태·원인 보존 |
| 기존 인증서 재조회·전달 | 새 서명 없이 같은 인증서 반환 |
| 폐지 전달 실패·외부 확인 누락 | 미반영 상태·처리 기한 유지, 재처리 가능 |
| 복구 후 HSM·원장·외부 상태 불일치 | 대조 전 신규 생성·발급·상태 변경 보류 |
| 중지·침해·폐지·만료된 CA의 발급 요청 | 신규 발급 차단 |

## 9. 기능별 원문 대응

기준은 Conformance v0.2 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`다. 아래 조항은 통제·발급·보존 요구의 근거이고, A01~A17의 앱 구성과 상태 처리 방식은 설계안이다.

| 기능 | 원문 조항 |
|---|---|
| A01~A03 준비·권한 | [절차·변경 관리][procedures], [인력][personnel], [컴퓨터 보안][computer] |
| A04 생성, A07 승인, A12 완료 | [CA 키 생성][generation], [CA 키 보호][keys], [인증서 발급][issuance], [등록 증거][program-policy] |
| A05~A08 요청·발급·검증 | [CA 책임][representations], [발급][issuance], [허용 용도][usage], [프로파일][profiles] |
| A09 원장·중복 | [저장소][repositories], [동일 키 갱신 금지][renewal], [수정 금지][modification] |
| A10~A11 중단·기록 | [수명주기 보안][lifecycle], [감사 로그][logging], [기록 보존][archival], [복구][recovery] |
| A13 하위 관리 | [발급][issuance], [용도][usage], [CA 책임][representations] |
| A14~A15 폐지·OCSP | [폐지 요청][revocation-request], [폐지][revocation], [상태 제공][status], [응답자 프로파일][ocsp-profile] |
| A16~A17 교체·백업 | [키 교체][changeover], [종료][termination], [복구][recovery], [CA 키 보호][keys] |

[program-policy]: ../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md#certificate-policy
[procedures]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#procedural-controls
[generation]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[personnel]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#personnel-controls
[computer]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#computer-security-controls
[keys]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys
[issuance]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-issuance
[representations]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#ca-representations
[profiles]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-profiles
[usage]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage
[lifecycle]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#lifecycle-security-controls
[repositories]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#repositories
[renewal]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-renewal
[modification]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-modification
[logging]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#audit-logging-procedures
[archival]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#records-archival
[recovery]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#compromise-and-disaster-recovery
[revocation-request]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#identification-and-authentication-for-revocation-requests
[revocation]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-revocation
[status]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-status-services
[ocsp-profile]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#ocsp-responder-leaf-certificates
[changeover]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-changeover
[termination]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#ca-or-ra-termination

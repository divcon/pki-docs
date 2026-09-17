# 02. 관리·운영 요구사항

범위: Root·ICA 운영 조직과 CA 서비스. 특정 cloud vendor, offline Root, 정해진 m-of-n 수치나 운영 담당 조직은 원문이 지정하지 않는다. 표의 증거는 **설계 제안**이다.

## 통제·인력·시스템

| ID | 원문 강도와 요구 | 설계에서 준비할 증거 | 원문 |
|---|---|---|---|
| O01 | **필수** — 공개 CPS 또는 C2PA와 협의한 다른 방식으로 업무 관행 공개. 모든 운영 절차를 최신 문서로 유지 | CPS/공개 정책, 문서 소유자·변경 이력 | [Publication][publish], [Documented Procedures][facility] |
| O02 | **필수** — CA 인증서 발급은 문서화된 절차, trusted roles, multiple-person control 및 split knowledge. Root의 모든 인증서 서명은 trusted roles 최소 2명, 그중 한 명의 명시적 서명 명령 | 발급 요청·승인·실행 대장, HSM 기록 | [Certificate Issuance 1–2][issue] |
| O03 | **필수** — 주요 기능(발급·폐지·attestation 검증 등) 직무 분리. 장비 물리 접근 및 해당 CA 작업 접근에 dual control. 키의 물리·논리 단독 접근 차단 | 역할표, 접근정책, 권한 변경·복구·자동화 우회 점검 | [Separation of Duties][facility], [CA Key Access Control][storage] |
| O04 | **필수** — 주요 시설 접근 통제, 민감 구역 권한자만 접근 및 MFA, 중요 장비 보호 | 물리/클라우드 책임 분담, 공급자 증거와 고객 설정 | [Physical Security Controls][facility] |
| O05 | **필수** — trusted/non-trusted roles의 배경조사(background checks) 및 보안인가(clearance) 정책·절차. permanent staff 지원 시 verification checks, trusted roles는 매 5년 재확인. 정기 교육·재교육, PKI 중대 변경 시 교육 | 확인·교육 기록(민감 원문은 별도 접근 통제) | [Personnel Controls][facility] |
| O06 | **필수** — 최소 권한, need-to-know, 강한 비밀번호 정책·MFA·정기 권한 검토 | 계정·접근 검토와 퇴직/변경 처리 | [Access Control][facility] |
| O07 | **필수** — 변경관리, 시행 전 시험·승인, rollback 및/또는 roll-forward 계획 | 버전 관리, 변경 승인·복구 시나리오 | [Change Management][facility] |
| O08 | **필수** — 안전한 코딩·코드서명·정기 보안 업데이트 등 보안조치, CA 시스템 MFA, 발급·폐지 변조 방지, 수명주기 기밀성·무결성·가용성 | 배포·패치·서명·접근 통제 증거 | [Computer / Lifecycle Security Controls][system] |
| O09 | **필수** — 안전한 통신, 원격 접속 및 CA가 원격 시스템으로 나가는 연결 인증, diagnostic port 통제, 방화벽, 서비스 제한·보안속성 문서, routing 통제, 네트워크 장비 물리 보호·설정 감사, 불신망 민감정보 암호화 | 네트워크 구성·연결 정책·설정 감사 기록 | [Network Security Controls 1–11][system] |
| O10 | **필수** — activation data 기밀성·암호/물리 접근 통제 | HSM 활성화·복구 재료 custody 기록 | [Activation Data][system] |

승인 UI가 두 명의 승인을 받는 것만으로 O02/O03/K05가 입증되지는 않는다. 서명 계정·HSM 관리·키 공유·backup 복구·비상 접근을 통해 한 명이 단독 사용 가능한지 검증하는 것을 설계 시험으로 제안한다. Cloud HSM이라는 이유로 이 통제를 생략할 수 없다.

## 기록·백업·교체·종료

| ID | 원문 강도와 요구 | 증거 제안 | 원문 |
|---|---|---|---|
| O11 | **필수** — 모든 발급 인증서의 안전한 내부 기록 저장소, **만료 후 최소 1년** 보존. serial·subject·기간·확장값·폐지상태 포함, 접근 통제·정기 감사 | 발급 DB·보존 설정·접근/감사 결과 | [Repositories][publish] |
| O12 | **필수** — 발급·폐지·attestation·접근 시도 등 사용자/시스템 활동 상세 audit logs. 요청 Subscriber·시스템·인력 식별자, 시간·행동·관련 parameter 포함. 무단 열람·수정·삭제 방지 및 정기 검토 | logging 목록, 무결성·보호·검토 기록 | [Audit Logging Procedures][logs] |
| O13 | **필수** — 기록 종류·보존기간·보호/검색을 정한 archival 정책, 관련 법규 준수, 안전한 저장과 문서화된 retrieval | 보존표·복원/열람 절차. 모든 로그의 기간이 O11과 같다고 단정하지 않음 | [Records Archival][logs] |
| O14 | **필수** — CA 키 backup/recovery 정식 계획의 **연간 검토**. backup 사본 전부 추적, 원본과 동일 다인 통제, CA 개인키 최소 한 사본 off-site, 평문 반출·보관 금지 | 보호된 backup inventory·위치·custody·검토 기록 | [Key Backup and Recovery][storage] |
| O15 | **필수** — 인증서 DB·키 재료·설정·로그 등 모든 중요 데이터의 안전한 backup 및 문서화된 복구 계획. 중요 데이터 backup의 off-site 보관 및 정기 복구 시험은 이 절에서 소문자 should | backup 범위·복구 절차·시험 증거 | [Compromise and Disaster Recovery][rotation] |
| O16 | **필수** — CA 개인키 archival 금지. `Key Destruction`에는 구체 stipulation 없음 | backup과 archive 구분, 종료 후 폐기 절차는 설계로 결정 | [Key Archival / Key Destruction][storage] |
| O17 | **필수** — 주기적인 CA 키 rotation의 안전하고 문서화된 절차. Subscriber disruption 최소화·chain of trust 유지는 소문자 should. Subscriber의 rotation agility와 사전 통지는 **SHOULD** | rollover·신뢰 배포·이전 키 종료 계획. CA 수명/교체 주기의 고정 숫자는 별도 결정 | [Key Changeover][rotation] |
| O18 | **금지** — 동일 키로 인증서 renewal, 이미 인증서를 발급한 키 쌍에 새 인증서 발급, 인증서 modification. Subscriber re-key는 신규 신청과 동일 검증 | 중복 키 검출·신규 키 생성·재발급 정책. cross-cert 예외는 자의적으로 만들지 않음(Q06) | [Renewal / Re-key / Modification][renew] |
| O19 | **필수** — 침해·키 손상·재해·중단 대응 계획. 역할·책임·communication/escalation 및 정기 drills/exercises는 소문자 should. incident review에서 원인·영향·재발방지 action 도출, 보고서를 Steering Committee와 Conformance Task Force에 공유 | 사고 보고·복구·폐지/교체 증거 | [Incident Response Plan][rotation], [Other Assessments][audit] |
| O20 | **필수** — CA 종료·RA 위임 철회 절차. 민감 데이터·키·장비의 안전한 취급·처분은 소문자 should. 사고의 신속 조치 예외 외에는 Subscriber 사전 통지 | 종료·서비스 이전·잔여 상태 서비스 계획 | [CA or RA Termination][rotation] |

CP `Key Escrow and Recovery`의 미지원 문구를 CA backup 금지로 확대하지 않는다. 별도의 CA 통제는 backup을 명시적으로 요구한다. 양자의 범위 차이와 키 archival 금지를 정책에서 구분한다. [CP][cp]

## 폐지·상태 제공

| ID | 요구 | 적용 / 근거 |
|---|---|---|
| O21 | 폐지 사유: GP CPL status가 `revoked`로 시작, 인증된 C2PA/Subscriber 요청, GP compromise 의심·확정 또는 해당 attestation 실패, 확인된 개인키 노출, CP 위반, 인증서 오용 | CA 발급 서비스 / [Certificate Revocation][status] |
| O22 | Subscriber/C2PA 폐지 요청은 요청자·진위·유효성 검증 후 **72시간 이내** 폐지 | 요청 검증 완료가 기산점. 모든 사고의 발견 시점부터 72시간이라는 일반 SLA로 확장하지 않음 / [Identification and Authentication for Revocation Requests][identity] |
| O23 | Claim Signing 인증서 OCSP는 필수이고 최소 기록 보존기간까지 제공. 즉 만료 후 최소 1년까지 필요 | [Certificate Status Services][status], [Repositories][publish] |
| O24 | subordinate CA·TSA 인증서는 OCSP 허용. 해당 인증서에 OCSP를 제공하지 않으면 CRL **필수**. Claim CRL은 필수 OCSP에 추가하는 선택 | `CRL Profile`의 일반적 선택 표현만 보고 조건부 의무를 누락하지 않음 / [Certificate Status Services][status] |
| O25 | OCSP는 RFC6960 minimum profile, 구현하는 CRL은 RFC5280 §5 minimum profile | [CP CRL / OCSP Profiles][cp]. CRL의 status 제공과 C2PA manifest stapling은 다른 경계 |
| O26 | 유효기간 내 모든 인증서의 현재 valid/revoked 상태를 담는 24×7 공개 repository | [CA Representations — Status][warranty]. 내부 발급 DB와 공개 저장소를 구분 |

Root 인증서에 AIA/CDP가 금지되어도 Root가 발급한 **ICA 인증서**의 상태 제공 의무가 없어지지 않는다. self-signed trust anchor의 제거/교체와 subordinate 폐지를 별도로 설계한다. CA TL/TSA TL 업데이트를 CA가 독자적으로 수행할 수 있다고 가정하지 않는다. 등록 후 목록 제거·이의 제기 절차는 제4장 「Conformance 등록 및 그 밖의 요구사항」 E16에 별도로 정리했다.

## 감사와 운영 책임

O27 — 독립된 적격 제3자 compliance audit, 보고서 제공·영문 또는 전문 번역·시정, 취약점 진단·침투시험은 해당 절에서 **SHOULD**다. 권고 감사 범위는 발급·갱신·폐지, attestation, CA/제품 키 관리, 논리·절차 통제, 인력·교육, 사고·재해복구다. 감사 주기는 위험·assurance에 따라 정하도록 SHALL이며 최소 연간은 권고다. 따라서 ‘연례 WebTrust 인증 필수’라고 바꾸지 않는다. [CP Compliance Audits / Other Assessments][audit]

O28 — Root CA는 Issuing CA의 수행·보증·CP 준수·관련 책임을 자신의 발급처럼 부담한다는 문구가 있다. 법적 효력의 개별 판단과 별도로, ICA만 등록한다는 이유로 Root 통제를 제외하는 설계 근거로 삼을 수 없다. [CA Representations 마지막 문단][warranty]

[publish]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L363-L375
[facility]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L625-L691
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529
[storage]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L827-L857
[system]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L863-L903
[logs]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L693-L729
[rotation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L731-L771
[renew]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L573-L585
[audit]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1396-L1454
[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[status]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L587-L609
[identity]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L401-L485
[warranty]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1520-L1564

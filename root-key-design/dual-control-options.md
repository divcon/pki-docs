# Root·First ICA 다인 통제

한 사람이 Root·First 키를 단독으로 생성·사용하거나 승인 체계를 바꿔 우회할 수 없도록 한다. 두 키는 같은 담당자 그룹이 사용하고 그중 한 명이 실행한다. 승인 인원 N/M과 실행자의 승인 포함 여부는 미정이다.

**CloudHSM CLI quorum을 이용한 서명을 검토 중이며, 실제 HSM 시험은 수행하지 않았다.** 특히 키 생성 통제와 관리자 우회 방지는 운영 키 생성 전에 해결해야 한다.

<a id="c2pa-controls"></a>

## 작업별 통제

| 작업 | 적용할 통제 | 구현 상태 |
|---|---|---|
| Root·First 키 생성 | 신뢰 역할 담당자의 다인 통제·지식 분리, 승인된 스크립트, 입회/기록·로그 | 생성용 계정·호스트·코드 변경 통제 미정 |
| Root 인증서 서명 | 매 서명에 신뢰 역할 담당자 최소 2명 참여, 한 명의 명시적 실행 | CLI key-usage quorum과 인증서 내용 승인 연동 검토 중 |
| First CSR·하위 인증서 서명 | 키 사용 승인과 서명할 내용 확인 | First 키에도 사용 quorum 적용을 검토 |
| 사용자·키·quorum 설정 변경 | 관리자 또는 키 관리 작업의 다인 통제, 승인용 키 보호 | 명령별 지원 범위·우회 여부 시험 필요 |
| 백업·복구 | 원본과 같은 다인 통제, 복구한 키·권한·원장 대조 | [백업 설계](operating-model.md#backup)에서 실제 구성 검증 필요 |

C2PA는 생성·발급·키 접근에 다인 통제를 요구하지만 AWS 구현이나 고정된 2-of-3 값을 지정하지 않는다. HSM quorum은 여러 사용자의 승인 조건이며 CA 개인키를 사람들에게 분할하는 기능과는 다르다. [CP 키 생성][generation] · [발급][issuance] · [키 보호][keys]

## 서명 실행 방식

CA 앱은 CSR·요청 권한을 검사하고 인증서 본문을 구성한다. CloudHSM은 키 보관과 서명을 담당한다. CLI 실행은 다음 두 방식 중 결정한다.

| 방식 | 실행 책임 |
|---|---|
| 작업자가 CLI 실행 | 앱이 작업 파일을 준비하고, 작업자가 세션·명령·입력·결과 전달을 관리 |
| 앱/스크립트가 CLI 실행 | 실행 프로세스가 승인 수집부터 서명까지 세션을 유지하고 중복 실행·결과 저장을 관리 |

CLI quorum 토큰은 현재 로그인 세션의 한 작업에만 유효하다. 작업 성공 후 소모되며 로그아웃·연결 단절 시 무효가 된다. 다른 애플리케이션에서는 사용할 수 없다. 따라서 CLI 토큰을 일반 PKCS#11/OpenSSL provider에 넘기거나, 종료된 Lambda 호출의 세션을 다음 호출에서 이어 쓰는 구성은 사용하지 않는다. 접수·조회·승인 기록에 Lambda를 사용하는 것은 별도 선택이다. [AWS 토큰 제약][aws-use]

### 승인한 내용과 서명 입력을 연결한다

1. 앱은 요청 권한·CSR·프로파일·중복 발급 여부를 검사하고 최종 인증서 본문인 `TBSCertificate` DER를 만든다.
2. 작업 ID, 본문 DER와 해시, 사람이 읽을 내용, 발급 키 지문, 프로파일·도구 버전, 승인 기한을 고정한다. 내용·키·설정이 바뀌면 기존 승인을 무효화한다.
3. 승인자들은 같은 자료를 확인한다. 같은 사람이 여러 계정으로 승인 인원을 채우지 못하도록 개인별 자격을 검사한다.
4. CLI 세션에서 키 사용 토큰을 만들고 개인별 승인 서명을 수집한다. 실행기는 승인 자료와 실제 입력을 다시 대조한 뒤 HSM 서명을 요청한다. Root 인증서 서명에는 담당자의 명시적 실행 지시를 받는다.
5. 앱은 결과 인증서를 조립해 승인 본문·서명·공개키·체인·프로파일을 검증하고 원장과 증거를 저장한다. 중단과 결과 불명은 [ceremony 중단 처리](ceremony/certificate-issuance.md#증거-보관과-중단-처리)를 따른다.

HSM 토큰의 키 사용 승인만으로 인증서 본문의 모든 바이트가 승인에 묶인다고 가정하지 않는다. 본문 대조를 수행하는 실행기의 변경·접근 권한도 통제해야 한다. 실행기 관리자에 의한 바꿔치기를 예방하는지, 사후 탐지만 가능한지 시험 결과로 구분한다. 잘못된 서명은 배포 중단과 함께 CA 사고로 처리한다.

## 생성·관리자·승인 키 보호

**키 생성은 별도 통제가 필요하다.** 공개된 quorum 지원 작업에는 생성 명령 자체가 없다. 생성 시 설정하는 quorum은 생성된 키의 이후 사용·관리 조건이다. 생성용 CU 자격증명, 호스트 접근, 도구·설정 변경과 관리자 초기화를 통제하고, 승인 없는 직접 생성을 차단하는지 시험한다. 티켓이나 입회 기록만으로 이 통제가 완성되지는 않는다. [AWS 지원 작업][aws-services]

| 경로 | 필요한 설계·검증 |
|---|---|
| 사용자 생성·암호/MFA 변경 | 지원되는 관리자 quorum 적용. 한 명이 다른 승인자 계정을 장악할 수 없는지 확인 |
| quorum 값·키 공유·속성 변경 | 해당 관리 작업의 승인 보호. 서명 승인 수만 설정하고 관리 우회를 남기지 않음 |
| 승인용 키 등록·교체 | 각 승인자는 CA 키와 별개의 개인키로 토큰에 서명하고 공개키를 HSM에 등록. 보관 장치·인증·형식 호환성·회수 방식 확정 |
| 실행기·AWS 자원·복구 권한 | 코드 교체·다른 호스트·백업 복구로 우회하지 못하도록 권한 분리. IAM 권한과 HSM 내부 CU/admin 권한을 각각 확인 |
| 퇴사·분실 | 공동 승인 아래 접근 회수·후임 계정과 승인 키 등록. 기존 세션·토큰, CA 키 소유 관계와 정족수 유지 확인 |
| 키·HSM·백업 삭제 | HSM quorum 보호 여부를 명령별로 확인하고 AWS/IAM·운영 권한도 검토 |

승인용 개인키를 앱 서버 한 곳에 모으거나 퇴사자의 키를 후임자에게 넘기는 구성을 사용하지 않는다. 관리자 한 명에게 계정 초기화·승인 키 사용·코드 변경 권한이 집중되어도 안 된다. 실제 보관 수단과 권한표는 미정이다. [AWS 승인 설정][aws-setup] · [관리자 승인][aws-admin]

## 검증 기준

테스트 키로 수행할 수용 기준이다. 선택한 HSM 모델·모드·CLI 버전과 시험 결과를 함께 기록한다.

| 시험 | 통과 조건 |
|---|---|
| 승인 없는 생성, 직접 CU 접속·다른 호스트·코드 변경 | 생성 통제 우회 불가 |
| 승인 부족·동일인 중복, CLI 밖 SDK 직접 서명 | 단독 서명 불가 |
| 승인 후 본문·issuer 키·프로파일 변경 | 실행 차단·재승인 |
| 토큰 재사용·다른 세션·단절·재로그인 | 기존 토큰 사용 거부. 결과 확인 뒤 새 토큰·승인으로 재개 |
| 관리자 단독 quorum 완화·승인자 교체 | 승인 체계 우회 불가 |
| 퇴사·분실·후임자 등록 | 기존 접근 회수와 정족수·키 소유 관계 유지 |
| 백업 복구 | 키 지문·권한·quorum·원장 일치, 단독 서명 거부 |
| RSA/ECDSA 인증서 조립 | raw/digest·해시·ECDSA raw/DER 처리 확인, 별도 도구의 서명·프로파일 검사 통과 |
| 실행기 관리자에 의한 입력 교체 | 예방·탐지 범위와 남은 위험 확인. 미해결 단독 발급 경로가 있으면 도입 보류 |

앱의 중복 요청·저장 실패·결과 재조회 시험은 [CA 앱 기능 검증](ca-software-requirements.md#기능-검증)에 둔다.

## 원문

C2PA는 Conformance v0.2 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`, AWS는 2026-10-07 확인한 공식 문서 기준이다.

[generation]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[issuance]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-issuance
[keys]: ../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys
[aws-use]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html
[aws-services]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-service-names.html
[aws-setup]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html
[aws-admin]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-admin.html

# C2PA CP v0.2와 글로벌 기업의 Root CA 보안 운영 사례

조사일: 2026-10-11. 상태: 검토용 샘플.

이 문서는 C2PA의 요구사항, 기업이 공개한 CA 운영 정책, AWS CloudHSM에 적용할 설정 제안을 구분한다. 기업 사례는 공개 CP/CPS에 명시한 운영 방침을 비교한 것이며, 비공개 내부 시스템이나 실제 이행 여부를 조사한 감사 결과는 아니다. TLS CA 사례의 인증서 필드나 수명은 C2PA 인증서에 그대로 적용하지 않는다.

## 1 결론

AWS CloudHSM 신규 구축에 대한 샘플은 **hsm2m.medium, FIPS 모드, FIPS 140-3 Level 3 인증 근거**를 출발점으로 삼는다. 여기에 키 반출 제한, 다인 승인, 평상시 접근 차단, 백업 복구 통제와 증적 보존을 붙인다. 모델과 모드만 선택해서 C2PA 적합성이 완성되는 것은 아니다.

C2PA CP v0.2는 AWS 모델명을 지정하지 않는다. 키 생성에 요구하는 최소 인증 수준과 키 저장 조항의 표현에도 차이가 있다. 아래 2절의 문구 차이를 검토한 뒤 실제 행사 기준에 반영해야 한다.

## 2 C2PA가 요구하는 것

기준 원문은 [C2PA Certificate Policy v0.2](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md)이다. 해당 커밋의 원문을 읽어 아래 표를 작성했다. 커밋은 이번 조사에서 읽은 파일을 식별하는 값이며, CP가 커밋 해시 기록을 의무화했다는 뜻은 아니다.

| 확인 항목 | 원문 요구사항 | 우리 환경에서 확인할 것 |
|---|---|---|
| HSM 모델 | 특정 제조사나 제품 모델을 지정하지 않음 | 서비스 타입, 실제 모듈 및 인증 근거를 연결해 기록 |
| 키 생성 보안 수준 | FIPS 140-2 Level 2 이상, FIPS 140-3 Level 2 이상, 또는 적절한 CC PP/ST에 대한 EAL4 이상 | 인증서 번호, 적용 하드웨어·펌웨어, 승인 모드와 알고리즘 확인 |
| 생성 장소와 절차 | 물리적 또는 클라우드 보안 환경, 신뢰 역할 담당자의 다인 통제와 지식 분할, 상세 행사 스크립트 | 참여자별 인증 수단 분리, 승인, 실행 순서, 로그, 서명 및 일탈 기록 |
| 입회와 기록 | 독립 당사자 입회 및/또는 기록, 생성 활동 로그 | 입회·기록 방법과 제출할 증적 확정 |
| 키 저장 | Key Storage 조항은 FIPS 140-2 Level 2 이상이라는 표현을 사용하며, 데이터센터 또는 상용 클라우드 HSM 환경을 기술 | 140-3 모듈을 이 조항에 어떻게 대응시킬지 해석·수용 근거 확보 |
| 키의 평문 노출 | 암호 모듈 경계 밖에 CA 개인키 평문 존재 금지 | 파일로 개인키 생성·저장하는 경로를 차단하고 HSM 내부 생성 확인 |
| 키 사용 | Root 및 Intermediate 서명키에 대한 단독 물리적·논리적 접근 방지, 모듈 내부에서 개인키 사용 | 서명뿐 아니라 권한 변경·복구 등 우회 경로 검토 |
| Root 인증서 서명 | 모든 Root CA 인증서 서명에 신뢰 역할 담당자 최소 2명 참여 | CLI 승인과 사람의 검토를 증적으로 연결 |
| 백업 | 연 1회 검토하는 복구 계획, 모든 키 백업 목록화, 원본과 같은 다인 통제, 최소 1개 오프사이트 사본, 평문 반출 금지 | 백업 위치와 권한, 보존 정책, 복구 후 통제 상태 확인 |
| 시스템 접근과 로그 | 최소 권한, MFA, 접근 검토, 활동 로그와 무단 변경·삭제 방지 | EC2·HSM·AWS 관리 권한과 로그 저장소를 함께 설계 |

표의 근거 조항은 원문의 `Procedural Controls / Separation of Duties`, `Personnel Controls / Access Control`, `Audit Logging Procedures`, `Key Pair Generation and Installation by CAs`, `Controls for CA Keys`, `Computer Security Controls`이다.

**문구 차이:** 키 생성 조항은 140-3을 명시적으로 허용하지만, `Controls for CA Keys / Key Storage`에는 140-2만 적혀 있다. 따라서 “Level 3이므로 저장 조항까지 자동 충족”이라고 결론 내리지 않는다. hsm2m.medium을 채택할 때는 이 차이에 대한 C2PA 측 해석 또는 수용 근거를 사전 확인 항목으로 남긴다. 원문을 임의로 140-3까지 포함하도록 바꾸지 않는다.

고정된 `2 of 3` 또는 `3 of 3`, 모든 Root의 물리적 오프라인 운영, AWS의 특정 키 속성 이름은 위 조항에서 지정하지 않는다. 다인 통제와 키 보호는 필수이고, 이를 구현하는 구체적인 수치·접근 차단 방식은 설계 결정이다.

## 3 글로벌 기업 사례

### Google Trust Services

열람한 판본은 TLS CP/CPS 6.2, 2025-10-03이다. 이 판본은 CA 키에 FIPS 140-2 Level 3 이상 또는 CC EAL4+를 규정하고, 원본과 백업의 물리적·논리적 접근 모두에 여러 신뢰 역할 담당자의 참여를 요구한다. CA 서버의 물리적 접근에는 2인 통제를, 직접 발급을 유발할 수 있는 계정에는 MFA를 명시한다. [원문 5.1.2, 6.2.1, 6.2.2, 6.5.1](https://pki.goog/repo/cp-cps-tls/6.2/GTS-CP-CPS-TLS.html)

적용할 교훈은 **서명 시점뿐 아니라 백업과 접근 경로에도 다인 통제를 유지하는 것**이다. 이 열람 범위에서 특정 HSM 모델이나 고정된 승인 정족수는 확인하지 못했다. 공식 아카이브에는 더 새로운 6.10이 표시되지만 본문을 확보하지 못했으므로, 위 내용은 6.2의 공개 사례로 한정한다. [공식 아카이브](https://pki.goog/archive/)

### Microsoft PKI Services

Public TLS CPS 3.3.7, 2026-09-11은 CA 키를 FIPS 140-2 또는 140-3 Level 3 하드웨어 모듈에서 생성·보호하도록 규정한다. 활성화, 서명, 백업, 복구에는 여러 신뢰 역할 담당자가 참여한다. 활성화에는 스마트카드와 MFA를 사용한다. Root 발급은 권한 있는 사람이 명령을 직접 내려 수행하고, 서명 전 인증서 본문을 검사한다. [원문 4.3.1.1, 4.3.1.2, 6.2.1, 6.2.2, 6.2.8](https://www.microsoft.com/pkiops/Docs/Content/policy/Microsoft_PKI_Services_public_tls_CPS_v3.3.7.pdf)

적용할 교훈은 **애플리케이션이 만든 본문을 검토한 뒤 사람이 승인하여 서명하는 절차**이다. 스마트카드는 이 회사의 구현 방식이며 CloudHSM의 필수 옵션은 아니다. 공개 문구만으로 특정 제조사·모델이나 승인 인원수를 확정하지 않는다.

### Amazon Trust Services

CP/CPS 2.7, 2026-08-19은 FIPS 140-1/140-2 Level 3 이상, ISO/IEC 19790 Level 3 이상 또는 지정된 CC 인증 경로를 기술한다. 오프사이트 키 백업 접근에는 최소 2명이 필요하고, 복구에도 같은 다인 통제를 적용한다. Root 개인키는 오프라인으로 보관하며, 미사용 시 로그아웃과 HSM 저장 파티션에서의 제거를 기술한다. [원문 6.2.1, 6.2.2, 6.2.9, 6.7](https://www.amazontrust.com/repository/ats-cp-cps-2.7.pdf)

적용할 교훈은 **평상시 Root를 사용 가능한 상태로 두지 않고, 다시 활성화할 때 통제를 복원하는 것**이다. Amazon의 CA라는 이유로 AWS CloudHSM을 사용한다고 추정할 수 없다. 파티션에서 키를 제거하는 방법도 CloudHSM에 그대로 복사할 설정이 아니다.

### 비교와 해석

| 사례 | 공개 문서에서 드러난 특징 | 이번 설계에 가져올 원칙 |
|---|---|---|
| Google | 원본·백업 모두 다인 접근, 발급 계정 MFA | 백업이 단독 접근의 우회 경로가 되지 않도록 설계 |
| Microsoft | Level 3, 다인 활성화·서명·복구, 명시적 Root 명령, 서명 전 검사 | 파일 검토와 서명 승인을 연결 |
| Amazon | 오프라인 Root, 미사용 시 비활성화, 백업 접근 최소 2명 | 행사 사이의 사용 가능 상태를 줄이고 재활성화 통제 |

이 세 사례는 Level 3과 다인 통제를 검토할 근거를 제공한다. 다인 통제·MFA·보호된 백업은 C2PA에도 이미 요구되므로 선택 사항으로 분류하지 않는다. **Level 3 채택, 구체적 정족수, 별도 Root 클러스터, 물리적 오프라인 운영** 등이 요구사항을 구현하거나 강화하는 설계 선택이다. 세 사례만으로 모든 글로벌 기업의 보편적인 구현이나 특정 제품 점유율을 주장하지 않는다.

## 4 AWS 모델과 모드 검토

| 항목 | 확인 결과 | 샘플에 반영 |
|---|---|---|
| hsm1.medium | 신규 클러스터 생성 지원 종료. AWS는 hsm2m.medium 이동을 권고 | 신규 구축 후보에서 제외 |
| hsm2m.medium | FIPS 또는 non-FIPS 모드 지원. Client SDK 5.9.0 이상 호환 | hsm2m.medium 사용, 실제 SDK 판본 고정 |
| FIPS 모드 | FIPS 승인 키·알고리즘을 사용하는 모드 | FIPS 인증 근거를 사용할 샘플의 기본 선택 |
| 인증 근거 | AWS는 hsm2m.medium을 FIPS 140-3 Level 3, CMVP 4703에 연결 | 인증서와 실제 제공 모듈·펌웨어의 대응 증적 확보 |
| 모드 변경 | 생성 후 모드 변경 불가, 백업 복구에도 모드 제약 존재 | 클러스터 생성 전에 모드 결정 |

근거: [AWS HSM 타입](https://docs.aws.amazon.com/cloudhsm/latest/userguide/hsm-types.html), [AWS 인증 안내](https://docs.aws.amazon.com/cloudhsm/latest/userguide/fips-validation.html), [AWS 클러스터 모드](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cluster-hsm-types.html).

[NIST CMVP 4703](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4703)은 Marvell LS2 HSM Family의 FIPS 140-3 Overall Level 3 인증이다. 조사 시점 상태는 Active이며, 승인 모드와 Security Policy 11절의 설치·초기화·구성 조건을 전제로 한다. 제품명이나 AWS 콘솔의 모드 표시만으로 실제 배포의 모든 조건을 입증하지 않는다.

## 5 Root와 First ICA 설정 샘플

아래는 사용자가 정한 CloudHSM, jumphost, 전용 EC2, 같은 EC2의 본문 작성 애플리케이션, CLI 서명 방식을 전제로 만든 제안이다. 실제 행사 문서에 채택한 확정값은 아니다.

### 기본 구성

| 항목 | 샘플 값 또는 방식 | 분류와 이유 |
|---|---|---|
| HSM | AWS CloudHSM hsm2m.medium | 신규 구축 제품 선택 |
| 보안 모드 | FIPS | 인증의 승인 모드 조건에 대응 |
| 보안 수준 | FIPS 140-3 Level 3, CMVP 4703 대응 확인 | 생성 조항의 Level 2보다 강화. 저장 조항 해석 확인 필요 |
| Region | us-west-2 후보 | 사용자가 말한 UW2에 대한 잠정 해석 |
| HSM 수 | 서로 다른 AZ에 2개 | 가용성 제안. 사람의 승인 정족수와 별개 |
| 클라이언트 | Client SDK 5.9.0 이상 중 리허설에서 검증한 정확한 판본 | 설치 패키지와 해시 기록, 가용성 검사 유지 |
| 실행 환경 | 외부 작업자 → jumphost → private subnet의 전용 EC2 → HSM | 작업자별 계정과 MFA, 최소 권한으로 접근 |
| 알고리즘 | Root와 First 각각 별도 EC P-384 키, ECDSA SHA-384 서명 | 프로파일이 허용하는 조합 중 선택한 샘플 |
| 서명 정족수 | 키 소유자 O와 공유 사용자 A·B의 3 of 3 | 세 사람 모두 참여하도록 선택. CP의 고정 수치가 아님 |
| 관리 정족수 | 같은 키에 대해 3 of 3 | 지원되는 공유·속성 변경 등의 단독 수행 방지 |
| 본문 검토 | 앱이 만든 TBS/CRI 파일을 승인자가 검토하고 해시를 기록한 뒤 CLI 서명 | 승인한 파일과 실제 입력의 일치 확인 |
| 행사 종료 | CLI 로그아웃, 임시 권한 회수, EC2 정지와 네트워크 접근 차단 | 평상시 접근 축소. 물리적 오프라인과는 구분 |
| 백업 | 암호화된 서비스 백업 목록화, 별도 Region 사본, 복구 권한 분리 | 오프사이트와 재해 복구에 대응하는 제안 |
| 증적 | HSM·CLI·호스트·AWS 관리 작업 로그와 승인 기록을 보호된 저장소로 수집 | 실행자가 단독으로 증적을 변경·삭제하지 못하도록 설계 |

Root와 First의 허용 키는 RSA 3072 이상 또는 EC P-384/P-521이다. RSA 4096도 대안이다. 이 표의 P-384는 선택 예시이며 필수 알고리즘이 아니다. [Root 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml), [First 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml).

SDK 5의 key availability quorum은 새 키가 최소 2개 HSM에 존재하는지 확인하는 내구성 통제다. `3 of 3` 사람 승인과는 다르다. [AWS 키 내구성 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/working-client-sync.html)

### 개인키 속성

| 속성 | 샘플 | 목적 |
|---|---|---|
| token | true | 세션 종료 후에도 유지하는 키 |
| private | true | 인증된 사용자 접근으로 제한 |
| sensitive | true | 민감한 키 자료 접근 제한 |
| extractable | false | 일반 키 반출·wrap 경로 제한 |
| sign | true | 서명 허용 |
| decrypt, derive, unwrap | false | CA 서명에 필요하지 않은 기능 제한 |
| modifiable | true, 지원되는 변경에는 관리 quorum 적용 | 공유·수명주기 관리 가능성을 유지하며 변경 통제 |
| destroyable | 별도 결정 | 삭제를 막을지와 최종 폐기 방법을 함께 검토 |

AWS CLI의 `extractable` 기본값은 true이므로 생성 시 false를 명시한다. `modifiable=false`는 다시 true로 바꿀 수 없으므로 행사 편의를 위해 무조건 잠그지 않는다. 이 표는 개인키 속성이며 공개키의 verify 등은 별도로 정한다. [AWS 지원 키 속성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html)

### 정족수와 승인 수단

샘플의 O·A·B는 서로 다른 사람과 CU 계정이다. 키 소유자 O도 연결 사용자 수에 포함되므로, 생성 시 A·B에게 공유하고 사용·관리 정족수를 각각 3으로 설정한다. 2 of 3은 한 명 부재 시에도 진행할 수 있는 대안이지만 어떤 조합이 승인할 수 있는지 정책을 다시 정해야 한다. [AWS CU 정족수 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html)

각 승인자의 quorum 토큰 서명키와 인증 수단을 서로 분리해 보호한다. 세 사람의 승인 개인키·비밀번호를 전용 EC2 한 계정에 모아두면 한 사람이 승인자를 모두 가장할 수 있다. 본문 작성 앱이 같은 EC2에서 동작한다는 결정은 승인자의 비밀까지 그 EC2에 모은다는 뜻이 아니다.

CLI 토큰은 한 번의 성공한 작업에 유효하고 현재 로그인 세션에 한정된다. 다른 앱의 인증에는 사용할 수 없다. 따라서 앱은 본문을 작성하고 CLI가 실제 서명을 수행하는 경계를 유지한다. 토큰이 승인한 파일의 모든 의미를 자동 검증한다고 가정하지 않고, 파일 내용·해시 검토를 따로 남긴다. [AWS quorum 사용](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

## 6 옵션을 추가할 때 확인할 한계

| 옵션 | 적용 판단 | 확인할 한계 |
|---|---|---|
| 별도 Root 클러스터 | 평상시 Root를 더 강하게 격리해야 한다면 검토 | 공유 클러스터에서는 First 사용을 위해 열어 둔 접속 경로가 Root에도 도달할 수 있음. 계정·키별 통제가 필요 |
| Root 전용 HSM 자원 제거 후 백업에서 재활성화 | 추가 대안으로 검토 | AWS가 공개한 구성 예시가 있으나 복구 통제·비용·지연을 리허설로 검증해야 함. 이번 기본 샘플의 종료 절차에는 채택하지 않음 |
| modifiable=false | 공유·교체·복구 절차 검증 후 검토 | 속성을 다시 변경할 수 없으므로 승인자 변경 계획과 충돌 가능 |
| destroyable=false | 제품에서 필요한 폐기·복구 방법 검증 후 검토 | 삭제 방지와 안전한 최종 폐기를 함께 설계해야 함 |
| 불변 로그 저장 | 실행자에 의한 증적 변경 방지에 권장 | 보존 기간, 조회 권한, 저장소 관리자와 실행자의 역할 분리 필요 |

전용 EC2를 정지하는 것만으로 CloudHSM 안의 Root 키가 비활성화되거나 물리적으로 오프라인이 되는 것은 아니다. 다른 호스트·복구 클러스터·관리자가 접근을 다시 열 수 있는 경로도 통제해야 한다. AWS는 HSM 자원을 제거하고 암호화 백업을 유지했다가 재활성화하는 별도 예시를 공개했다. [AWS portable Root CA 예시](https://aws.amazon.com/blogs/security/create-a-portable-root-ca-using-aws-cloudhsm-and-acm-private-ca/)

AWS의 지원 quorum 작업 목록에는 키 서명과 공유·속성 변경 등이 있지만 **키 생성과 키 삭제는 열거되어 있지 않다**. 이 목록을 근거로 해당 작업까지 HSM quorum이 보호한다고 쓰지 않는다. 생성 행사, 키 삭제, AWS IAM 정책 변경, 클러스터·백업 삭제·복원은 각각 별도의 승인·접근·감시 통제를 설계한다. [AWS quorum 지원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html)

CloudHSM 서비스 백업은 HSM 내부에서 암호화되고 평문으로 밖에 나가지 않는다. 일반 키 반출 금지와 서비스 백업은 구분해서 관리하며, `extractable=false`를 백업 불필요의 근거로 삼지 않는다. 기본 백업은 원래 Region에 저장되므로 오프사이트 대응은 위치·재해 분리·접근 통제를 설명해야 한다. 별도 Region 복사본과 복구 리허설을 샘플로 제안한다. [AWS 백업 보안](https://docs.aws.amazon.com/cloudhsm/latest/userguide/backups.html), [Region 간 백업 복사](https://docs.aws.amazon.com/cloudhsm/latest/userguide/copy-backup-to-region.html)

## 7 리허설에서 확보할 증적

| 검증 | 기대 결과 또는 남길 기록 |
|---|---|
| 모델·모드·인증 대응 | 클러스터 타입·모드, HSM 정보, 적용 인증서 및 보안 정책의 대응 기록 |
| 저장 조항 해석 | CP의 140-2 저장 문구와 140-3 배포 선택에 대한 수용 근거 |
| HSM 내부 생성 | 생성 로그와 공개키, 생성 직후 개인키 속성·소유자·공유 사용자·정족수 조회 결과 |
| 다인 서명 | O 단독 또는 일부 승인으로 실패, O·A·B 승인으로 성공, 결과 서명 검증 |
| 관리 변경 | 단독 공유·속성 변경 시도 실패 및 승인된 변경 기록 |
| 승인 수단 분리 | 한 계정·호스트·관리자만으로 세 승인자를 가장할 수 없는지 확인 |
| 다른 API 경로 | 선택한 SDK/API로 quorum 보호 키를 단독 사용할 수 없는지 확인 |
| 반출 방지 | 해당 키에 대한 금지된 반출 시도 실패. 운영키에 파괴적인 검증을 수행하지 않도록 시험키로 선행 검증 |
| 입력 일치 | 승인한 TBS/CRI 해시와 실제 CLI 입력 해시 일치, 조립 후 CSR·인증서의 서명 및 프로파일 검증 |
| 행사 종료 | 로그인 세션 종료, 권한 회수, 접속 차단 후 단독 재접근·재활성화 가능 여부 확인 |
| 백업 복구 | 시험 클러스터에서 키 대응 확인과 검증용 서명, 속성·사용자·정족수·MFA 상태 재확인, 시험 자원 종료 및 기록 |
| 관리 권한과 로그 | 클러스터·백업·IAM·호스트 관리 변경의 승인 경로와 감사 로그 확인 |

## 8 다음에 실제 문서에 반영할 결정

먼저 **HSM 타입과 FIPS 모드, 적용 인증 근거**를 확정하고 저장 조항의 해석 확인 항목을 등록한다. 이후 **서명·관리 정족수와 승인자 인증 수단의 보관 방식**, **행사 종료 후 Root 접근 차단과 백업 복구 방식**을 결정한다. 각각 settings와 preparation에 값·책임자·검증 방법을 연결하면 된다.

이 조사에서 행사 실행, 운영키 생성, 외부 등록 신청은 수행하지 않았다.

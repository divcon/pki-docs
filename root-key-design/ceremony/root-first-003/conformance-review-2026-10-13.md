# Root 및 First ICA 키 생성 세레모니 모의 적합성 심사

**종합 판정은 현재 버전 실행 승인 불가, 보완 후 재심사입니다.** 기본 구성은 갖췄지만 Quorum 등록·사용자 생성·키 생성·인증서 서명을 이어 주는 실행 절차에 차단 사항 네 건이 있습니다. 실제 C2PA 적합성 승인도 현재 제출된 스크립트만으로는 내릴 수 없습니다.

검토일은 2026-10-13 KST이며, 대상은 [script.md](script.md) v0.1입니다. 문서상 실행 예정일은 2026-10-15입니다. 세 분야를 별도 AI 심사 에이전트가 독립 검토하고 주심이 원문 대조와 의견 조정을 수행했습니다. 실제 C2PA Administrator나 Approver의 공식 심사 결과가 아닙니다. AWS 계정·HSM에 접속하거나 키 생성·발급 명령을 실행하지 않았습니다.

## 심사 범위와 판정 기준

대상은 Platform Root 키 생성과 자체서명 CA 인증서, C2PA First Intermediate 키 생성과 Root의 ICA 인증서 발급, 그 과정의 통제·증적입니다. 하위 Issuing CA·운영 인증서가 없다는 이유로 이 세레모니 자체를 부적합 처리하지 않습니다. CA 전체 등록에는 별도 CP/CPS·운영 통제·신청 자료가 필요합니다.

규범 기준은 스크립트가 지정한 C2PA Certificate Policy v0.2 및 Conformance Program v0.2입니다. `conformance-public`의 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`에 있는 Git 원문을 사용했습니다. AWS 명령·제품 제약은 검토일 공식 웹 문서와 대조했습니다. 이 고정본이 향후 실제 신청에 수용될 기준 버전인지는 신청 시 확정해야 합니다. 설계 산출물은 심사대상으로만 사용했습니다.

대상 파일 SHA-256: `44c04e3d1a06642080b7a53782766e67778f8a0edabd53fbef3537d9891db754`. 아래 행 번호는 이 파일에 대응합니다.

| 분류 | 의미 |
|---|---|
| 실행 차단 | 기재된 명령·순서·연동으로는 승인된 실행 절차가 성립하지 않음 |
| 중대 보완 | 필수 통제의 설계 또는 입증이 미완성이라 승인할 수 없음 |
| 최종 증적 미제출 | 계획은 있으나 실제 시행·검증 결과를 아직 심사할 수 없음 |
| 정정·확인 | 문서 모순이나 실행 기준을 고쳐야 함 |

이 분류는 이번 모의 심사의 분류이며 C2PA 공식 등급표가 아닙니다. 템플릿의 빈 명단·서명·시각을 실제 운영 위반으로 간주하지 않습니다.

## 심사위원별 의견

| 심사위원 | 판단 | 코멘트 |
|---|---|---|
| A 규정과 입회 증적 | 승인 보류 | 역할·승인·입회·서명·편차의 구조는 적절합니다. 다자 통제의 실제 실행 방법과 서명된 완료 스크립트가 필요합니다. |
| B CloudHSM과 KMS | 실행 승인 불가 | 등록 토큰, 사용자 생성 승인, 키 생성 시 공유, PKCS#11 서명 연결을 먼저 고쳐야 합니다. |
| C 인증서와 검증 | 검증 승인 보류 | 주요 확장 설정은 기준과 맞는 방향입니다. 검증기·실제 인증서가 없고, 실패 후 동일 키 재발급 문구도 수정해야 합니다. |
| 주심 통합 판단 | 보완 후 재심사 | 현재 버전 그대로의 본 세레모니 진행을 승인하지 않습니다. 실행 가능한 확정본과 리허설 결과를 먼저 심사하고, 시행 후 증적으로 최종 판단해야 합니다. |

## 실행 승인 차단 사항

### F01 공개키 등록에 다른 종류의 토큰을 사용함

위치: 5.4.4–5.4.7 및 5.4.11, 230–244행. **실행 차단.**

등록 토큰을 `--service user`로 생성하면서 결과를 `tokens[].unsigned`와 `tokens[].signed` 구조로 처리합니다. 공식 admin 및 CU 공개키 등록은 `--service registration`을 사용합니다. `user`는 사용자 관리 작업 승인용이고 토큰 구조도 다릅니다. [AWS admin 등록 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html), [AWS CU 등록 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html).

**심사 코멘트:** KMS 서명 형식 리허설에 앞서 토큰 종류부터 수정해야 합니다. CU의 공개키 등록은 공식 지원 기능이므로 지원 여부 대신 실제 버전에서의 등록 성공을 검증하십시오.

종료 조건: admin/CU별 등록 토큰 생성·서명·등록 명령을 확정하고, KMS 공개키 대응 및 전체 등록 성공 결과를 제출합니다. 등록 토큰과 이후 작업 승인 토큰은 별도 절차로 기록합니다.

### F02 사용자 Quorum 설정 뒤 CU 생성 승인이 빠짐

위치: 5.4.9–5.4.10, 240–242행. **실행 차단.**

`user` Quorum을 M≥2로 설정한 뒤 세 CU를 `user create`만으로 생성합니다. 공식 절차는 각 작업에 승인된 토큰을 `--approval`로 전달해야 하며, 성공한 작업의 토큰은 재사용할 수 없습니다. [AWS Quorum 적용 후 사용자 관리](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-admin.html).

**심사 코멘트:** Quorum을 켰다는 체크와 그 아래 작업이 승인되었다는 체크는 다릅니다. 현재 명령으로 기대 결과인 CU 3명 생성을 입증할 수 없습니다.

종료 조건: CU 생성마다 새 토큰, 승인자, 승인 수, 실행 결과를 남깁니다. 생성 시점의 admin 로그인 전환도 명시합니다.

### F03 키 생성과 Quorum 공유 순서가 성립하지 않음

위치: 5.5.1 및 5.6.1, 262·286행. **실행 차단.**

M≥2인 키를 생성하려면 생성 시점부터 소유자와 공유 CU를 합한 연관 사용자 수가 해당 Quorum 값을 충족해야 합니다. 현재 절차는 Quorum 옵션을 미정으로 남기고 생성 후 `key share`를 수행합니다. 공식 EC 생성에는 `--share-crypto-users`, `--use-private-key-quorum-value`, `--manage-private-key-quorum-value`가 있습니다. [AWS CU Quorum 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html), [AWS EC 키 생성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html).

별도 공유 명령의 `--username cu_kc1,cu_kc2`도 단일 사용자 인수 문법에 맞지 않으며 필수 `--role`이 빠져 있습니다. [AWS key share](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-share.html).

**심사 코멘트:** Root와 ICA의 M/N을 각각 확정하십시오. Root 예시 3-of-5와 실제 세 CU·세 Custodian 구성이 자동으로 일치하지 않습니다. `extractable:false`는 Quorum 설정의 증거가 아닙니다.

종료 조건: 필요한 공유를 생성 명령에 포함하고 소유자·공유 사용자·사용/관리 Quorum 값·키 참조·공개키를 출력으로 확인합니다. 승인 인원 수는 HSM 계정 수뿐 아니라 서로 다른 실제 인원과 연결합니다.

### F04 CLI 승인 토큰과 OpenSSL 서명 경로가 연결되지 않음

위치: 250행, 5.5.3·5.6.3·5.6.5, 266·290·294행. **핵심 실행 차단.**

스크립트는 키 사용 Quorum을 설정하고 실제 Root 자체서명, ICA CSR, ICA 발급에는 OpenSSL/PKCS#11을 사용합니다. 그러나 AWS는 해당 토큰을 동일 CloudHSM CLI 로그인 세션의 한 작업에만 사용할 수 있고 다른 애플리케이션에 사용할 수 없다고 명시합니다. ‘토큰 공급 방법은 리허설 확인’이라는 문구로 이 제약을 해결할 수 없습니다. [AWS 키 사용 Quorum](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html).

**심사 코멘트:** 실제 서명 경로 하나를 완성해야 합니다. `crypto sign`으로 바꾸는 경우에도 인증서/CSR의 서명 대상 구성, 서명 인코딩과 결과 조립, 독립 검증까지 필요합니다. 단순 명령 이름 교체로 끝나지 않습니다. CU 비밀번호 분할은 별도의 통제 설계이며 CLI 토큰을 PKCS#11에서 쓰게 하는 방법이 아닙니다.

종료 조건: 세 서명 작업 각각의 완성된 실행 경로와 리허설 결과를 제출합니다. 선택한 다자 통제로 단독 사용을 막는다는 증거가 필요합니다. C2PA가 특정 제품의 native Quorum만을 유일한 구현으로 지정한 것은 아닙니다. [CP의 CA 키 사용 통제][cp-controls].

## 통제와 최종 증적 보완 사항

### F05 생성부터 복구까지 단독 키 사용을 막는 통제를 입증해야 함

위치: 5.4.9, 5.5–5.6, 6장, 240·262–294·374–380행. **중대 보완.**

CP의 CA 키 생성 조항은 multiple-person control 및 split knowledge를 요구하고, CA 키 사용 조항은 어느 개인도 Root·Intermediate 서명키에 단독 접근하지 못하도록 요구합니다. Root의 모든 인증서 서명에는 trusted role인 두 명 이상이 필요합니다. 현재 Root 자체서명에는 승인 절차가 없고, 키 생성에도 참여자별 통제 동작이 확정되지 않았습니다. [CP 키 생성][cp-generation], [CP 키 접근 통제][cp-controls], [CP Certificate Issuance][cp-issuance].

관리자 통제도 확인해야 합니다. 5.4.9는 `quorum` 서비스 설정을 권장으로 남깁니다. `user` 서비스와 설정 변경용 `quorum` 서비스의 값·변경 절차를 모두 확정하십시오. KMS 관리자의 `Sign` 금지 선언만으로 키 정책 변경·grant 생성·Custodian 역할 인수 권한까지 막혔다고 판단할 수 없습니다. [AWS Quorum 값 변경](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-min-value.html), [AWS KMS 키 관리자 권한](https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-default.html).

**심사 코멘트:** 입회자가 보고 있었다는 사실과 운영자 단독 사용을 방지하는 통제는 구별해야 합니다. 여러 CloudTrail principal도 서로 다른 사람이 각각 통제한다는 증거와 연결해야 합니다. 현재 자료만으로 실제 우회 가능성을 확정한 것은 아닙니다.

종료 조건: Root/ICA 생성·서명·관리·복구 경로별 인원과 권한, 실제 IAM/KMS/SCP 정책 및 역할 신뢰관계, 세션 종료 절차를 제출합니다. 승인 부족·다른 세션·토큰 재사용·단독 정책 변경 실패 시험은 이를 확인하기 위한 심사 권고 시험입니다.

### F06 프로파일 검증 결과를 재현할 자료가 없음

위치: 3.3, 5.6.4·5.6.7, 5.7, 부록 A·B, 110·292·298·312–314·438행 이후. **중대 보완 및 최종 증적 미제출.**

제출 폴더에는 스크립트만 있고 별도 검증기와 발급 인증서가 없습니다. `verify_[profile.py](http://profile.py)`는 실행 가능한 파일 경로가 아니며, 설정 예시에는 이스케이프된 코드 펜스와 HTML 엔터티가 있습니다. 현재 문서 그대로 복사한 명령·설정으로 `ALL CHECKS PASSED`를 재현할 수 없습니다. Program은 Trust List에 올릴 인증서가 CP 프로파일에 맞는다는 검증 증거를 요구합니다. [Program Certificate Policy][program-cp].

**심사 코멘트:** 일반 체인 검증의 `OK`만으로 C2PA 프로파일 적합성을 판정하지 않습니다. CSR 육안 확인과 해시 기록 역시 CSR 서명·키 대응 검증 전체를 대체하지 않습니다.

종료 조건: 확정된 `root.cnf`, `ica.cnf`, 검증기와 도구 버전·해시, 실제 Root/ICA PEM·CSR 및 검사 결과를 제출합니다. 버전·serial·서명 알고리즘·DN·유효기간·SPKI·critical flag·KU·BC·SKI/AKI·policy·AIA/CDP를 검사하고 Root 자체서명과 전체 체인을 검증합니다. HSM 공개키, CSR, 인증서의 공개키를 같은 형식으로 추출해 비교하는 명령도 확정합니다. [CP Root/First Intermediate 프로파일][cp-profiles].

### F07 모든 실패에 동일 키 재발급을 허용하는 문구는 수용하기 어려움

위치: 5.7 뒤의 실패 처리, 322행. **규범과 충돌할 수 있는 중대 절차 결함.**

‘키는 유지하고 인증서만 재발급 가능’은 조건이 없습니다. CP의 Certificate Renewal은 이미 인증서를 발급한 키 쌍에 새 인증서를 발급하지 못하도록 규정하고 Certificate Modification도 금지합니다. 검증 실패·미게시라는 사실만으로 같은 키 재발급 예외가 생긴다고 볼 근거는 확인되지 않았습니다. [CP Certificate Renewal][cp-renewal], [CP Certificate Modification][cp-modification].

**심사 코멘트:** 이미 발급된 인증서의 수정·재발급과 발급 전 실패를 구분해야 합니다. 전자는 위 금지 조항과 직접 충돌할 수 있습니다. 후자의 처리 및 ‘발급 완료’ 경계는 CP/CPS와 승인된 절차에서 확정하십시오. 모든 서류 누락을 자동 키 재생성 사유로 보는 것도 적절하지 않습니다.

종료 조건: 발급 전 실패, 발급 후 프로파일 불일치, 키 생성 통제 실패, 개인키/활성화 자료 노출을 구분한 중단·격리·재개·재생성 판단 절차와 승인자를 지정합니다. 실제 중복 발급이 발생했다고 판정한 것은 아닙니다.

### F08 백업과 재가동 통제를 READY 및 0 HSM으로만 확인함

위치: 5.8·5.9.1, 6장, 334–352·380행. **중대 보완.**

CP는 연례 검토되는 정식 키 백업·복구 계획, 모든 백업의 계수와 원키와 동일한 다자 통제, 적어도 한 off-site 사본, 평문 반출 금지를 요구합니다. 현재는 최신 백업 `READY`와 HSM 삭제 여부만 확인하며 대상 키를 포함하는 백업 식별·복구 절차가 없습니다. [CP Key Backup and Recovery][cp-backup].

AWS의 `RestoreBackup`은 삭제 대기 백업의 복원이며, 실행 가능한 클러스터 복원은 `CreateCluster`의 source backup 및 `CreateHsm` 경로와 관계됩니다. 이 재가동 경로가 현재 사후 통제 목록에서 빠져 있습니다. [AWS RestoreBackup](https://docs.aws.amazon.com/cloudhsm/latest/APIReference/API_RestoreBackup.html), [AWS 백업으로 클러스터 생성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster-from-backup.html).

**심사 코멘트:** `Hsms: []`를 지속적인 단독 사용 방지 증거로 취급하지 마십시오. 백업 생성 시각·ID와 최종 키/사용자/Quorum 상태의 대응이 필요합니다. off-site를 무조건 다른 리전이라는 요구로 확대하지 않습니다. AWS는 같은 리전의 서비스 관리 S3에 암호화 백업을 저장하므로 실제 배치와 보호가 CP 요구에 어떻게 대응하는지 설명해야 합니다. [AWS 백업 특성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/backups.html).

종료 조건: 키와 백업 ID의 대응 목록, 보존·삭제·복사·재가동 권한 및 승인, 승인된 복구 계획을 제출합니다. 삭제 전 복구 가능성 확인과 복구 후 동일 공개키·Quorum 확인을 운영 승인 조건으로 권고합니다. AWS가 마지막 백업을 자동 삭제하지 않는다는 점도 반영하십시오. [AWS 백업 보존](https://docs.aws.amazon.com/cloudhsm/latest/userguide/manage-backup-retention.html).

### F09 독립 입회와 완료 서명은 계획과 실제 증거를 구별해야 함

위치: 2장·4.2–4.4·7장, 59–69·122–126·388–408행. **최종 증적 미제출.**

CP 키 생성 조항은 독립 입회 및/또는 녹화를 허용하지만 Program은 등록 대상 인증서의 독립 입회 증거와 서명된 key generation script를 요구합니다. 해당 세레모니와 스크립트의 적합성을 확인하는 WebTrust for CA 보고서는 예외 근거가 될 수 있습니다. [CP 키 생성][cp-generation], [Program Certificate Policy][program-cp], [Program CA Evidence Request][program-evidence].

**심사 코멘트:** IW와 녹화를 모두 배치한 방향은 적절합니다. 예정 템플릿의 공란은 위반이 아니지만 최종 승인 자료도 아닙니다. IW가 반드시 특정 외부 회계법인이어야 한다거나 WebTrust가 무조건 필수라는 추가 조건은 부과하지 않습니다.

종료 조건: 실제 신원·trusted role 지정·IW 독립성 설명, 승인된 최종본과 해시, 수행 시각, 참가자/IW 서명, 모든 편차를 제출합니다. Trust List에 넣을 대상이 Root인지 First ICA인지도 명시합니다. 후자만 등록한다고 상위 Root 통제 책임이 자동 면제된다고 전제하지 않습니다.

### F10 로그의 존재와 해시만으로는 감사 추적이 완성되지 않음

위치: 5.4.12, 5.9.2–5.9.6, 6장, 246·354–362·382행. **중대 증적 보완.**

CP는 인증서 작업 관련 인원·시각·동작·관련 데이터가 있는 상세 감사 로그와 보호·정기 검토, 기록 종류·보존 기간·검색 절차가 정해진 보관 정책을 요구합니다. 발급 인증서 상세 기록에는 만료 후 최소 1년 보관 요구가 있습니다. 이 기간을 모든 녹화와 로그에 일률 적용한다는 뜻은 아닙니다. [CP Audit Logging Procedures][cp-logging], [CP Records Archival][cp-archive], [CP Repositories][cp-repositories].

**심사 코멘트:** KMS `Sign`은 승인키 사용 기록입니다. 그것만으로 CA 키 생성·인증서 서명·발급 결과 전체를 입증할 수 없습니다. CloudHSM 로그도 기록하는 작업의 범위가 있으므로 HSM 생성 로그와 명령/애플리케이션의 발급 기록을 연결해야 합니다. [AWS HSM 감사 로그 참조](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm-audit-log-reference.html).

종료 조건: 단계·인원·승인·키 참조·CSR/인증서 fingerprint·로그 시각을 연결한 증거 목록, 보관 정책 ID/기간, 실제 Object Lock·접근권한·조회 검증을 제출합니다. 단말 입력/화면 녹화가 분할 비밀번호를 합쳐 노출하지 않도록 수집과 열람 통제도 확정합니다.

## 추가 정정과 확인 코멘트

| 위치 | 코멘트와 필요한 조치 |
|---|---|
| 2장 및 5.4.4–5.4.11 | KC의 CLI 입력 금지와 KC 직접 로그인·등록이 충돌합니다. 자기 승인키 등록·토큰 서명에 허용할 조작을 명확히 정하십시오. |
| 2장 및 5.3.2·5.6.4 | IW의 모든 조작 금지와 명령 담당 표기가 충돌합니다. CO가 실행하고 IW가 관찰하는지, 읽기 검증만 직접 하는지 명시하십시오. |
| 8장 | 편차를 5.x.y에 한정하면 승인·사전 조건·사후 보관의 편차를 적을 수 없습니다. 모든 적용 단계의 편차를 기록할 수 있어야 합니다. [CP 키 생성][cp-generation]. |
| 3.1 및 부록 A | CMVP 번호가 부록 A에 있다고 하지만 실제 부록은 OpenSSL 설정입니다. HSM 인증서와 배포 모델·모드·버전을 연결하십시오. hsm2m.medium 선택 자체를 부적합으로 보지는 않습니다. [AWS FIPS 검증](https://docs.aws.amazon.com/cloudhsm/latest/userguide/fips-validation.html). |
| 5.3.2·5.3.4 | CSR Subject에 Cluster ID가 포함된다는 기대는 공식 예시의 HSM ID/PARTN과 다릅니다. API 응답·CSR·대상 HSM의 대응을 확인하십시오. 초기화 호출 직후와 완료 상태도 나눠 대기·실패 조건을 정해야 합니다. [AWS 초기화](https://docs.aws.amazon.com/cloudhsm/latest/userguide/initialize-cluster.html). |
| 5.1.1 및 전체 명령 | `curl` 명령과 검증기 경로의 링크 문법을 고치십시오. 한 외부 URL 접속 실패만으로 네트워크 격리 전체가 입증되지는 않습니다. 필요한 AWS 접근 경로와 차단 정책을 사전 확인하는 것이 합리적입니다. |
| 5.9.4 | owner key의 KMS 이관 또는 봉인 매체 중 실제 방식을 확정하십시오. 이관 후 사용/복구 확인과 단말·임시본 삭제 기준이 필요하며 `shred` 성공만으로 모든 저장 매체의 잔존 사본 삭제를 보증하지 마십시오. |

## 부적합으로 판정하지 않은 사항

| 항목 | 판단 |
|---|---|
| P-384, SHA-384 | Root/First ICA 프로파일이 허용하는 선택입니다. 실제 출력 인증서는 별도 검증해야 합니다. |
| Root pathLen 2, First ICA pathLen 1 | 해당 계층의 프로파일과 맞습니다. First ICA를 leaf 발급용 마지막 CA로 해석하지 않았습니다. |
| critical BC/KU, SKI/AKI, ICA policy OID | 설정 의도는 프로파일과 맞습니다. ICA AKI는 발급자 Root SKI와 대응하는지 확인해야 합니다. |
| Root에 AIA/CDP 없음 | 프로파일에 맞습니다. Root policy OID는 선택이므로 누락만으로 위반이 아닙니다. |
| First ICA에 OCSP/AIA와 HTTP CDP | 두 경로를 기재한 자체는 오류가 아닙니다. 실제 URI 및 발급자 상태정보와의 연결은 확정해야 합니다. |
| Root 9131일, First ICA 5479–7305일 | Root 20년·First ICA 5년은 이 원문의 typical 예시입니다. 이 값만을 강제 상한으로 읽어 위반 판정하지 않습니다. 장기 수명에 대한 CPS 근거·교체·상태서비스 계획은 별도 확인 대상입니다. |

위 인증서 판단의 근거는 [CP Root/First Intermediate 프로파일][cp-profiles] 및 [공식 Root YAML][root-yaml], [공식 Intermediate YAML][ica-yaml]입니다. `<5479~7305>`는 실제 실행 시 하나의 승인된 값으로 확정해야 합니다.

CloudHSM owner 인증서의 EC P-384도 AWS가 허용합니다. C2PA 체인 밖의 초기화용 키를 CA 키와 동일한 프로파일로 심사하지 않았습니다. KMS `DIGEST` 선택 역시 등록 토큰의 디코딩 값이 이미 SHA-256 digest라는 정의와 맞는 방향입니다. [AWS 초기화 알고리즘](https://docs.aws.amazon.com/cloudhsm/latest/userguide/initialize-cluster.html), [AWS KMS Sign](https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html).

키를 HSM 안에서 생성하고 `extractable=false`를 설정하며 공개 CSR/인증서만 이동하는 방향은 적절합니다. Root/ICA 클러스터 분리, 역할 분리, IW·녹화·해시·Object Lock도 유용한 통제입니다. 이 설계 의도와 실제 설정·시행의 적합성 입증은 별도로 확인해야 합니다.

## 재심사 제출 조건

1. **실행 전:** F01–F04를 해소한 확정 명령·설정·도구·M/N·참가자·역할표·편차/실패 절차를 승인합니다. 미정 대안 문구를 남기지 않습니다.
2. **리허설:** 두 클러스터의 초기화부터 Root 자체서명·ICA CSR·발급·프로파일 검증까지 재현합니다. 선택한 다자 통제의 정상/거부 사례와 백업·복구 후 동일 키/통제 확인 결과를 제출합니다.
3. **본 세레모니 후:** 실제 PEM·CSR·키 속성·검증 출력·서명된 script·IW 증거·편차·증거 목록·백업 식별·보존 정책을 하나의 심사 묶음으로 제출합니다.
4. **최종 심사:** 등록할 인증서와 적용 기준 버전을 명시하고, ceremony 밖의 CA 운영 자료를 연결합니다. 모든 쟁점이 해소되었는지는 C2PA Administrator와 Approver가 최종 판단합니다. [Program Application Approval][program-approval].

이 조건은 현재 지적을 해소하기 위한 제출 기준이며 통과를 보장하는 사전 인증은 아닙니다.

[cp-generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[cp-controls]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys
[cp-issuance]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-issuance
[cp-profiles]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-profiles-for-certification-authorities
[cp-renewal]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-renewal
[cp-modification]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-modification
[cp-backup]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#key-backup-and-recovery
[cp-logging]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#audit-logging-procedures
[cp-archive]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#records-archival
[cp-repositories]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#repositories
[program-cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#certificate-policy
[program-evidence]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#certification-authority-evidence-request
[program-approval]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#application-approval
[root-yaml]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml
[ica-yaml]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml

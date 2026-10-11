# Root와 First ICA 세레모니 — 설정

작성 중 · 행사 기준은 [메인 스크립트](script.md)입니다. 실제 값과 선택 근거를 채우고, 승인된 버전을 [승인본 목록](preparation.md#승인본-목록)에 고정합니다. 샘플의 가상 값은 복사하지 않습니다.

행사 일정·참여자 명단은 `script.md`에서 관리하고, 이 문서에서는 그 역할과 실제 계정·키·권한을 연결합니다. 선택값을 다른 문서에 반복해서 쓰기보다 이 표를 참조합니다.

## 승인 설정

| 항목 | Root | First ICA |
|---|---|---|
| 키 알고리즘·곡선 | EC / NIST P-384 (`secp384r1`), ECDSA 서명용 | EC / NIST P-384 (`secp384r1`), ECDSA 서명용. Root와 별도 키 쌍 |
| 키 라벨·속성·소유·공유 | 개인키는 서명 전용. `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false`, `extractable=false`, `sensitive=true`, `token=true`. 잠금 기본안은 `modifiable=false`, `destroyable=false`. 사용·관리 quorum 각각 `2`, 승인 집합 O·A·B. 폐기 계획·잠금 시험 완료 전 운영 키 생성 금지. 라벨·계정 매핑: {{Root_키_설정}} | 개인키는 서명 전용. `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false`, `extractable=false`, `sensitive=true`, `token=true`. 잠금 기본안은 `modifiable=false`, `destroyable=false`. 사용·관리 quorum 각각 `2`, 승인 집합 O·A·B. 폐기 계획·잠금 시험 완료 전 운영 키 생성 금지. 라벨·계정 매핑: {{First_키_설정}} |
| Subject / Issuer DN | {{Root_DN}} | {{First_DN과_issuer}} |
| 서명 알고리즘·입력 형식 | ECDSA + SHA-384 (`ecdsa-with-SHA384`). S02/S05의 TBSCertificate DER. CLI raw/digest 전달 방식은 미정 | ECDSA + SHA-384 (`ecdsa-with-SHA384`). S04의 CertificationRequestInfo DER. CLI raw/digest 전달 방식은 미정 |
| 유효기간 UTC | {{Root_notBefore_notAfter}} | {{First_notBefore_notAfter}} |
| Serial 생성·중복 방지 규칙 | {{Root_serial_규칙}} | {{First_serial_규칙}} |
| SKI / AKI | {{Root_SKI_AKI}} | {{First_SKI_AKI}} |
| KU / EKU | {{Root_KU_EKU}} | {{First_KU_EKU}} |
| Basic Constraints / pathLen | {{Root_BC}} | {{First_BC}} |
| 정책 OID | {{Root_정책_OID}} | {{First_정책_OID}} |
| AIA / CDP | {{Root_AIA_CDP}} | {{First_AIA_CDP}} |
| 기타 확장·critical 여부 | {{Root_전체_확장_정의}} | {{First_전체_확장_정의}} |

설정 원본과 버전: {{설정_원본}}. 프로파일 차이의 처리: {{해석_검사_수용_근거}}. 공개키 지문·파일 해시 방식: {{해시_대상과_알고리즘}}.

| 환경과 보호 항목 | 승인값 또는 근거 |
|---|---|
| AWS 계정·리전·클러스터 | AWS CloudHSM 사용. 리전 후보는 사용자 표기 `UW2`를 `us-west-2`(US West / Oregon)로 해석하며, 최종 확정은 미완료. AWS 계정·클러스터 ID는 미정 |
| HSM 모델·모드·보안 수준 | 사용자 결정: `hsm2m.medium`, 클러스터 `FIPS` 모드, FIPS 140-3 Level 3 인증 모듈 사용. AWS가 제시한 인증 근거는 CMVP 4703. 실제 배포 모듈·펌웨어·승인 모드와 인증 조건의 대응 증거는 구축 후 확인. CP 저장 조항의 문구 차이는 아래 N01에 기록 |
| HSM 환경 준비 상태 | 현재 미구축이며 신규 구축 예정. 리허설과 실제 운영용 키 생성 행사에서는 구축된 환경을 사용할 계획. 구축·초기 설정·접속 확인의 실제 결과, 리허설/운영 환경 분리와 클러스터 구성은 미확정 |
| 실행 호스트·접근·네트워크·코드·검증 도구 | 명령 실행용 전용 EC2 사용. 외부 작업자 단말 → VPC 내 jumphost → 전용 EC2로 접속하며, 전용 EC2의 작업자 접속은 작업자 계정으로 제한. 작업자가 CloudHSM CLI로 키 생성·서명을 요청. EC2 식별자·OS·인증 방식·네트워크 허용 규칙·CLI/SDK 버전·코드·검증 도구의 버전과 해시는 미정. [실행 환경과 역할 분담](#실행-환경과-역할-분담) 참조 |
| 키 생성 통제 | 별도의 다인 승인과 승인된 명령만 실행하는 통제 방향을 잠정 반영. 키 생성 명령 자체에 HSM quorum이 적용된다고 간주하지 않는다. 정족수·인증 수단·접근 활성화·제한된 실행·우회 시험은 미확정. 기존 생성 검토안의 3인 승인 숫자는 미확정. 아래 N02 참조 |
| 서명 quorum | 사용자 결정: S02/S04/S05에 AWS CloudHSM의 키별 `key-usage` quorum 사용. 작업자 O와 승인자 A·B, 서로 다른 3명 중 2명이 승인하는 `2 of 3`. O의 자기승인 허용. 키 사용 quorum 값은 `2`. 실명·CU 계정·승인키·실제 명령·시험은 미정. [서명 quorum 결정](#서명-quorum-결정) 참조 |
| 키 관리 quorum·우회 시험 | 잠정 반영: Root·First 개인키 각각 `key-management` 값 `2`, O·A·B 중 서로 다른 2명 승인. 서명 quorum과 별도 토큰 사용. 실제 계정·공유·등록키·권한·잠금 상태의 관리 시험은 미완료. [키 관리와 관리자 통제](#키-관리와-관리자-통제) 참조 |
| HSM 관리자 quorum | 잠정 반영: 서로 다른 3명의 개인 관리자 계정, `user`·`quorum`·`cluster` 각 값 `2`. CU 계정·승인키와 관리자 역할을 구분. 실명·계정·등록키·초기 설정·시험은 미정 |
| 속성 잠금·개별 키 삭제·폐기 | 개인키 생성 시 `modifiable=false`, `destroyable=false`를 적용하는 기본안을 잠정 반영. 키 삭제 자체는 네이티브 quorum 대상이 아님. 폐기 경로·백업 처리·공유 클러스터 영향과 잠금/삭제 거부 시험 완료 전 운영 키 생성 금지. [N03](#n03-속성-잠금과-폐기-검증-조건) 참조 |
| 별도 통제할 AWS API·실행 환경·승인키 변경 | 백업 복원·복사·삭제·보존 변경, HSM/클러스터 삭제, EC2/jumphost/네트워크/실행 코드 변경, 승인키 등록·교체는 별도 다인 승인 실행과 권한 분리로 설계. IAM/SCP만으로 다인 승인이 구현된 것으로 보지 않음. 정족수·정책·실행 경로·우회 시험은 미정 |
| 개인 계정·승인 키·활성화 재료 | {{목록_관리자_보호_위치_참조}} |
| 입회·시간·로그·증거 보존·접근 통제 | {{입회와_기록_정책}} |
| 로그 수집·검토 | {{HSM별로그_CloudTrail_호스트_실행기_승인기록_원천과_사람계정연결_시각오차_검토자}} |
| 인증서 발급 기록 보존 | CP 적용 인증서의 만료 후 최소 1년 이상 / {{구체_종료일_권한_복구검사}} |
| 기타 기록 보존 | {{스크립트_승인_로그_영상별_기산점_기간_권한_조회방법}} |
| 생성 직후 보호·백업·off-site·복구 | 개인키의 일반 반출을 차단하고 CloudHSM의 암호화된 클러스터 백업으로 복구하는 방향 확정. 원본과 같은 다인 통제 적용. off-site 위치·보존·복원 권한·신규 키 포함 확인·복구 시험·책임자: {{보호_계획_복구시험_책임자}} |
| 키 외 중요 자료 백업 | {{원장_설정_감사로그_승인_증거목록의_백업과_복원검사}} |
| 종료 시 접근 유지·회수 | {{남길_HSM계정공유와_회수할_임시접근_세션_토큰_검사}} |
| First 요청 권한·발급 허가 | {{요청_검증과_허가_기록}} |
| 장소 보안·행사 후 물리 보관 | {{적용_여부_근거와_해당시_절차}} |

## 키와 서명 알고리즘 결정

사용자의 “전부 ecd 384”는 **Root와 First ICA 모두 ECDSA 서명용 P-384 키를 사용하는 결정**으로 반영한다. 두 CA는 같은 알고리즘을 사용하되 각각 별도의 키 쌍을 생성한다. 해시는 P-384에 맞춰 SHA-384를 선택하며, 이는 이번 행사의 프로젝트 선택이다.

| 대상 | 사용할 키 | 서명 알고리즘·해시 |
|---|---|---|
| S02 Root 자기서명 인증서 | Root P-384 키 | ECDSA + SHA-384 |
| S04 First CSR | First P-384 키 | ECDSA + SHA-384 |
| S05 First 인증서 | Root P-384 키. 인증서에는 First P-384 공개키 수록 | ECDSA + SHA-384 |

C2PA v0.2의 [Root 공식 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml)과 [First 공식 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml)은 ECC 곡선 P-384와 ECDSA SHA-2 계열 서명을 허용한다. P-384는 허용된 곡선 중 이번 행사에서 선택한 값이며, 모든 프로파일 검사나 적합성 심사가 완료되었다는 뜻은 아니다.

CloudHSM의 [EC 생성 명령](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html)에는 `--curve secp384r1`, [ECDSA 서명 명령](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html)에는 `--hash-function sha384`를 반영한다. 실제 명령은 키 속성·계정·입출력·CLI 버전을 정한 뒤 완성하고 시험한다.

인증서·CSR의 서명 식별자는 `ecdsa-with-SHA384` (`1.2.840.10045.4.3.3`)를 사용한다. AlgorithmIdentifier의 parameters는 생략한다. [RFC 5758 §3.2](https://www.rfc-editor.org/rfc/rfc5758.html#section-3.2)

CLI raw/digest 입력 방식과 변환 도구는 미정이다. 어느 방식을 선택하든 고정 본문에 대해 SHA-384를 한 번 적용한 ECDSA 서명이 되도록 정의한다. CloudHSM의 원본 `r||s` 서명 응답은 보존하고 인증서·CSR 조립에 필요한 ASN.1 DER 형식으로 변환한다. [AWS 서명 입력·출력 정의](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html)

이 선택은 CA 키와 위 세 서명 작업에 적용한다. 증거 파일의 SHA-256 식별 해시와 AWS quorum 토큰의 승인키·서명 규칙은 별도로 관리한다. AWS CU quorum 초기 설정 문서의 승인키는 RSA 2048이며 이를 CA용 P-384 키로 대체하지 않는다. [AWS quorum 승인키 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html)

## 개인키 용도와 추출 검토

사용자 결정: **Root·First 개인키는 서명 전용으로 사용하고, 일반 반출은 `extractable=false`로 금지한다.** 복호화·키 파생·다른 키 unwrap을 금지하고, 개인키로 암호화·검증·다른 키 wrap을 수행하는 용도도 허용하지 않는다. `sensitive=true`, `token=true`로 보호·영구 보관을 설정한다. 공개키 출력·공개키의 서명 검증과 승인된 백업·관리는 별도 절차를 따른다.

| 항목 | 확정 정책과 남은 작업 |
|---|---|
| 확정한 용도 속성 | `sign=true`, `decrypt=false`, `derive=false`, `unwrap=false` |
| 그 밖의 용도 | 실제 개인키 조회에서 암호화·검증·wrap 용도가 활성화되지 않았는지 확인. private key에서 생성 인자로 지원하지 않는 속성은 전달하지 않음 |
| 개인키의 모듈 밖 평문 존재 | C2PA CP가 금지. 실제 개인키를 EC2 파일·메모리에서 평문으로 사용하는 방식 금지 |
| 일반 개인키 반출 | `extractable=false`를 생성 시 적용. 일반 wrap/export를 통한 암호화 반출도 차단. CP가 이 AWS 속성값 자체를 지정하는 것은 아니며, 사용자 요청으로 권고 채택 |
| 보호·영구 보관 | 생성 시 `sensitive=true`, `token=true` 적용. 세션 키로 생성하지 않음 |
| 백업·복원 | CloudHSM의 암호화된 클러스터 백업을 사용하도록 설계. 원본과 같은 다인 통제 적용. off-site 위치·권한·보존·백업 포함/복원 시험은 미정 |

CP는 평문 반출을 금지하면서 보호된 백업과 off-site 사본을 요구한다. 모든 암호화 반출을 일괄 금지하는 요구로 해석하지 않는다. 이번 일반 반출 차단은 실제 개인키 파일이 필요 없는 운영 흐름과 HSM 안의 `2 of 3` 서명 통제를 유지하려는 프로젝트 선택이다. 근거·백업과의 구분·이식성의 대가는 [개인키 추출 조사](../../../references/cloudhsm-ca-key-extraction-2026-10-11.md)에 정리했다. 사용자 요청에 따라 이 권고를 채택했으며, 실제 설정·시험 완료와 구분한다.

원문: [CP의 CA 키 저장·사용·백업 통제](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys), [AWS 키 속성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html), [AWS 백업 보안](https://docs.aws.amazon.com/cloudhsm/latest/userguide/data-protection-backup-security.html).

CloudHSM에서 `extractable=false`는 나중에 `true`로 되돌릴 수 없으므로, 일반 반출로 다른 공급자의 HSM에 키를 이전하는 경로는 사용하지 않는다. 실제 속성·백업 포함·복원 후 보호 유지 여부는 테스트 키로 검증한다. 키 관리 quorum·속성 잠금과 별도 통제의 기본안은 아래에 잠정 반영했다. `modifiable=false`·`destroyable=false`의 적용은 폐기 계획과 시험 확인을 운영 생성의 선행 조건으로 둔다.

## 키 관리와 관리자 통제

사용자의 “일단 전부 반영하고 나중에 재검토” 요청에 따라 다음 기본안을 행사 초안에 반영한다. 구현·시험 완료나 운영 수행 승인은 아니다. 선택 이유·공식 근거·대안·재검토 질문은 [별도 재검토 기록](key-management-control-review.md)에 보관한다.

| 통제 | 기본안과 적용 범위 | 시행 전에 확인할 조건 |
|---|---|---|
| 개인키 관리 quorum | Root·First 각각 값 `2`. 키 소유자와 공유 CU를 서로 다른 O·A·B에 대응시키고 O+A·O+B·A+B 허용. O의 자기승인은 유효한 개인 토큰 서명이 있을 때만 계산 | 소유 CU만 수행할 수 있는 관리 작업의 실행자 지정, 현재 승인 집합·등록키와 작업 전후 조회, 단독·중복·집합 밖 승인 거부 |
| 속성 잠금 | 생성 시 `modifiable=false`. 관리 승인을 충족해도 금지한 기능을 켜거나 속성 잠금을 해제하지 않음 | 잠금 동작, 공유·공유 해제·승인자 교체의 별도 동작, 폐기 방법과 잠금 해제 불가 영향 검증 |
| 개별 키 삭제 차단 | 생성 시 `destroyable=false`. 삭제 자체에 관리 quorum이 붙는다고 기록하지 않음 | 소유자의 직접 삭제 거부 확인, 관련 백업·복사본을 포함한 폐기 계획과 공유 클러스터 영향 확인 |
| 관리자 user·quorum·cluster | 개인별 관리자 계정 3개와 독립 보호한 승인키, 각 서비스 값 `2` | 모든 HSM의 최종값 인수, 관리자 변경·정족수 낮추기·MFA·mTLS 변경 단독 거부, 초기 설정 중간값과 최종값 구분 |
| 승인자 명단·등록키 | 공유 변경을 승인자 집합 변경으로 취급. O·A·B 외 추가는 현재 정책에서 금지. 교체는 명단·정책·등록키를 함께 변경 승인 | 신원·공개키 지문·중복 소유 확인, 단독 등록/교체·관리자 우회와 복원 후 과거 승인키 부활 시험 |
| 키 생성·AWS API·호스트/코드 | 별도 작업 계획 다인 승인과 제한된 실행 경로. 권한 정책·승인 검사 코드의 변경도 분리 | 직접 CLI/API·다른 호스트/SDK·관리자·정책/코드 변경 우회 차단. 정족수·계정·실제 프로그램은 후속 확정 |

관리 quorum은 공유·공유 해제·속성 변경·wrap·unwrap을 지원한다. 이 중 금지한 암호 연산은 quorum 승인으로 허용하지 않는다. 토큰에는 해당 `key-management` 서비스를 사용하고 키 사용 토큰과 혼용하지 않는다. 관리자 `quorum` 서비스는 관리자 서비스 값 변경 보호이며 개인키의 사용·관리 값 설정과 구분한다. [AWS 지원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html), [관리자 값 변경](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm-token-set-qm.html)

현재값·변경값·명령·대상 키·승인자 명단·기한을 별도 작업 계획으로 고정한다. AWS 토큰만으로 특정 변경값과 명령 전체가 고정된다고 가정하지 않으며, 실행 직전 대조와 사후 조회를 기록한다. `modifiable=false`가 공유나 승인키 등록까지 잠근다고 단정하지 않고 실제 동작을 시험한다. [관리 quorum 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

AWS API 작업의 접근 권한은 IAM 및 필요 시 SCP로 제한하고 별도 승인 실행 경로에 연결한다. 승인 기록만 있고 직접 실행 권한이 남아 있으면 통제 완료로 보지 않는다. 복원한 환경은 백업 시점 사용자·설정·정책을 현재 명단·등록키·quorum·속성·접속 정책과 대조하기 전 사용하지 않는다. [IAM 작업 목록](https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudhsm.html), [백업 복원](https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster-from-backup.html)

공개키에는 AWS 개인키 quorum이 적용되지 않으며, 공개키 출력·검증·보관은 별도 관리한다. 위 잠금 설정은 CA 개인키에 대한 기본안이며 공개키 세부 속성은 실제 명령 작성 시 확정한다.

## 보안 선택과 특이사항

### N01 CP의 FIPS 판본 문구 차이

CP v0.2의 `Key Pair Generation and Installation by CAs`는 키 생성에 FIPS 140-2 또는 140-3 Level 2 이상을 허용한다. 반면 `Controls for CA Keys / Key Storage`는 FIPS 140-2 Level 2 이상으로만 표현한다. [고정 CP 원문](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md)

이 차이를 특이사항으로 기록하고, 이번 행사는 현행 FIPS 140-3의 Level 3 인증 모듈과 FIPS 모드를 사용하는 보안 방향으로 결정한다. Level 2 최소 등급보다 높은 인증 등급을 선택하는 프로젝트 결정이며, 저장 조항의 문구를 임의로 바꾸거나 외부 적합성 수용이 완료되었다고 기록하지 않는다. 문구 차이에 대한 외부 해석·수용 근거는 아직 확보하지 않았다.

AWS는 `hsm2m.medium`을 FIPS 140-3 Level 3 및 CMVP 4703에 연결한다. 해당 인증은 승인 모드와 정해진 설치·초기화·구성 조건을 전제로 하므로, 구축 후 실제 모듈·펌웨어·모드의 대응 자료를 준비한다. [AWS 인증 안내](https://docs.aws.amazon.com/cloudhsm/latest/userguide/fips-validation.html), [NIST CMVP 4703](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4703)

### N02 키 생성 승인과 생성 시 quorum 설정의 구분

AWS의 CloudHSM CLI quorum 지원 작업 목록에는 키 서명과 일부 키 관리 작업이 있으나 키 생성 명령은 열거되어 있지 않다. 생성 시 지정하는 키 사용·관리 quorum 값은 **생성된 키의 이후 사용·관리에 적용되는 값**이며, 생성 요청 자체에 여러 사람의 HSM 토큰 승인이 적용된다는 뜻이 아니다. [AWS quorum 지원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html)

서명 quorum은 작업자 O를 포함한 O·A·B 중 2명 승인으로 결정했다. 이번 요청으로 키 생성에는 별도 다인 승인과 승인된 명령만 실행하는 방향을 잠정 반영한다. 정족수·인증 수단·우회 차단 구현의 상세 설계는 미확정이다. 기존 S01/S03 및 G01/G05는 구현·시험 완료를 뜻하지 않는다. CP의 생성 다인 통제·지식 분할 요구를 면제하거나 단독 생성을 승인한 것으로 해석하지 않는다.

검토 자료는 [키 생성 승인 검토안](key-generation-control-review.md)에 연결한다. 계획 승인 검사와 제한된 CLI 호출의 방향을 반영하되 기존 제안의 3인 승인 숫자·계정·인증 수단·실제 구현은 아직 결정하지 않았다. 계획 승인 서명과 생성된 CA 키를 사용하는 AWS 서명 quorum을 구분한다.

### N03 속성 잠금과 폐기 검증 조건

`modifiable=false`·`destroyable=false`를 생성 시 적용하는 기본안을 잠정 반영한다. AWS에서 `modifiable`은 false에서 true로 되돌릴 수 없으며, 개별 객체 삭제 허용 여부는 `destroyable`과 구분한다. 관리 quorum 승인은 속성 잠금을 해제하는 수단이 아니다. [AWS 속성 정의](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html), [PKCS #11 객체 속성](https://docs.oasis-open.org/pkcs11/pkcs11-base/v2.40/pkcs11-base-v2.40.html)

잠금·소유자 삭제 거부·승인자 교체와 복구를 테스트 키로 검증하고, 키·관련 백업/복사본의 폐기 경로 및 공유 클러스터의 다른 키 영향을 확인해야 한다. 완료 전 운영 키 생성은 금지한다. 실패하면 값을 임의로 완화하지 않고 재검토·변경 승인·필요한 재시험을 거친다. 전체 HSM·클러스터·백업 삭제는 이 속성의 보호 대상이 아니므로 별도 다인 통제가 필요하다. 검토 기준과 기록란은 [별도 재검토 기록](key-management-control-review.md#다시-검토할-항목과-판정-기록)에 연결한다.

## 서명 quorum 결정

사용자 결정: **작업자 O를 포함한 서로 다른 3명 O·A·B 중 2명이 승인한다(`2 of 3`).** O는 CLI 실행자이면서 승인자일 수 있고, 자신의 승인용 개인키로 토큰에 서명한 경우에만 승인 1명으로 센다. CLI 명령을 실행했다는 사실만으로 승인 수에 포함하지 않는다.

| 항목 | 확정한 규칙 |
|---|---|
| 적용 작업 | S02 Root 자기서명, S04 First CSR 서명, S05 Root 키의 First 인증서 서명 |
| 승인 가능한 사람 | 작업자 O, 승인자 A, 승인자 B의 3명. 실제 신원·개인 CU 계정·등록 승인키 지문은 추후 작성 |
| 필요한 승인 | 서로 다른 2명의 유효한 토큰 승인 서명 |
| 허용 조합 | O+A, O+B, A+B. 세 명 모두 승인해도 충족 |
| 실행 담당 | O. A+B가 승인한 경우에도 O가 CLI로 실행하며, 이 경우 O의 토큰 승인 서명은 필수가 아님 |
| AWS 키 설정 | Root·First 개인키의 사용 quorum 값 `2`. 키별 소유·공유 CU와 등록 승인키를 O·A·B에 대응시키고, 승인 가능한 집합이 이 3명과 일치하는지 확인 |
| 거부 조건 | 승인 0명·1명, 동일인의 중복 승인, 집합 밖 승인으로 인원 충족, 만료·작업/키 불일치 |
| 기록할 내용 | 승인 가능 집합, 실제 승인자와 조합, 개인별 승인키 지문·시각·검사, 실행자와 명시적 실행 지시 |

각 작업의 실제 승인자는 같은 고정 본문을 검토하고 본문 승인과 토큰 승인을 작업 ID로 연결한다. 검증자 V의 독립 검사·발급 허가·입회 등 다른 역할은 해당 절차를 따른다. 서명 결정은 생성 승인 검토안의 3인 승인을 확정하지 않는다. 키 관리 quorum은 별도 선택으로 [키 관리와 관리자 통제](#키-관리와-관리자-통제)에 잠정 반영한다.

설정·명령 작성과 시험은 아직 미완료다. [공통 Q01–Q08](runbook.md#공통-서명-절차-q01부터-q08)과 [리허설과 통제 시험](preparation.md#리허설과-통제-시험)에 연결한다. 요청자의 자기승인 가능 여부는 [AWS quorum 설명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli.html)을 근거로 한다.

## 실행 환경과 역할 분담

사용자가 지정한 구성 방향이며, 구축·접근 제한·통제 시험 완료를 뜻하지 않습니다.

| 구성 요소 | 역할과 사용 방식 |
|---|---|
| 외부 작업자 단말 | 작업자가 jumphost를 거쳐 전용 EC2에 접속하는 단말 |
| jumphost | 외부에서 VPC 내 전용 EC2로 접속하는 경유 호스트 |
| 명령 실행용 전용 EC2 | 작업자 계정만 작업자 접속을 허용. 작업자가 CloudHSM CLI를 실행해 Root·First 키 생성과 CSR·인증서 서명을 요청 |
| 요청·본문 작성 애플리케이션 | CloudHSM CLI와 같은 전용 EC2에서 별도 애플리케이션으로 실행. CSR·인증서 발급 요청과 서명할 본문을 작성해 EC2 내부의 작업 파일로 저장하고, 작업자가 확인한 파일을 CLI 서명 입력으로 사용 |
| AWS CloudHSM | 전용 EC2의 CLI 요청을 받아 지정된 키를 생성하거나 서명을 수행 |

애플리케이션에서 준비한 요청·본문을 CLI 실행 입력으로 연결하는 흐름은 [runbook.md](runbook.md#실행-환경과-작업-흐름)에 기록합니다. 같은 EC2 내부의 파일로 연결하며, 실제 작업 디렉터리·파일명·접근 권한·입력 대조 방법은 미정입니다. 서명값을 반영한 CSR·인증서 조립 도구, 승인·독립 검사·기록 방법은 후속 상세 정의에서 확정합니다. 전용 EC2의 작업자 접속 제한과 HSM 키 사용에 필요한 승인·정족수는 각각 설정·시험합니다.

## 사람과 권한의 연결

| 사람·역할 | CU 또는 admin 계정·승인 공개키 지문 | Root와 First 소유·공유 | 허용 작업·승인 집합 | 등록·교체·복구 권한과 부정 시험 |
|---|---|---|---|---|
| O — 작업자 겸 서명·관리 승인자 | {{O_개인_CU_계정과_등록키_지문}} | {{O_Root_First_소유공유_관계}} | CLI 실행. 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함, 유효한 토큰 자기승인 허용. 소유자 전용 명령의 실행 권한은 계정 매핑 후 확정 | {{O_등록교체복구_권한과_시험참조}} |
| A — 서명·관리 승인자 | {{A_개인_CU_계정과_등록키_지문}} | {{A_Root_First_소유공유_관계}} | 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함 | {{A_등록교체복구_권한과_시험참조}} |
| B — 서명·관리 승인자 | {{B_개인_CU_계정과_등록키_지문}} | {{B_Root_First_소유공유_관계}} | 서명·관리 각각 O·A·B의 `2 of 3` 집합에 포함 | {{B_등록교체복구_권한과_시험참조}} |
| 관리자 3명 — 실명 미정 | {{개인별_admin_계정과_등록키_지문}} | CU의 소유/공유와 별도 역할 | user·quorum·cluster 각각 `2 of 3`. 같은 사람이 CU와 겸임하더라도 계정·역할별 재료를 구분하고 한 사람이 다른 사람의 재료까지 보유하지 않음 | {{관리자_등록교체복구_권한과_시험참조}} |
| {{기타_사람과_역할}} | {{계정과_등록키_지문}} | {{키별_관계}} | {{기타_허용작업과_승인집합}} | {{등록교체_권한과_시험참조}} |

| 통제 행위 | 각자 보유·보호할 재료와 권한 | 단독으로 수행할 수 없는 이유 | 허용·거부 시험 및 당일 확인 |
|---|---|---|---|
| 생성·생성 접근 활성화 | {{생성_분리_재료권한}} | {{생성_우회차단}} | {{생성_시험과_G01_G05}} |
| 서명 | O·A·B 각자의 승인용 개인키, 개인 CU 계정·등록키와 연결. 보관·교체·복구 상세는 미정 | 사용 quorum `2`와 승인 가능 집합 3명으로 서로 다른 2명의 승인을 요구. 실제 설정·우회 차단은 구현·시험 필요 | O+A·O+B·A+B 성공, 단독·중복·집합 밖 승인 거부 / {{서명_직접SDK_우회시험과_Q절차}} |
| 키 관리 | O·A·B 각자의 CU 승인키. 소유 CU의 실행 권한과 공유 CU의 승인 권한 구분 | 관리 quorum `2`. 공유 전후 명단 대조. 잠긴 속성과 금지 연산은 승인 수 충족으로 허용하지 않음 | 관리 단독·중복·집합 밖 승인 거부, 2명 승인 허용, 잠금 상태의 공유 변경 / {{관리_시험참조}} |
| 관리자·승인키 등록/교체 | 개인별 admin 계정·승인키. 승인 공개키 등록/교체는 별도 신원·지문·명단 변경 승인 | user·quorum·cluster 각 `2`. 등록/교체까지 자동 보호된다고 가정하지 않고 단독 교체 경로를 별도 통제 | {{관리자_등록교체_단독거부_시험과_B00}} |
| 백업 복원·삭제·호스트 변경 | 별도 다인 승인 실행 경로와 분리한 IAM/호스트/코드 변경 권한. 구체 정족수 미정 | 직접 실행·권한 정책·승인 검사 코드 변경 우회 차단. 복원 후 과거 사용자·승인키·정책 대조 전 사용 금지 | {{별도통제_시험과_B01_X01}} |

지식 분리의 적용 설명과 검토 근거: {{지식분리_설명과_검토}}. 사람 승인 quorum과 HSM 노드 가용성 quorum은 별도로 확인합니다.

## 최종 보관 기준

최종 자료와 마지막 판정까지의 보존·복제 계약: {{최종_보관_절차와_완료기준}}.

위 보존 정책에 따라 승인본, 실제 수행 기록, 확인 서명, 종료·최종 판정과 그 저장 확인까지 보관합니다. 실제 보관 결과는 [수행 기록](records/record-template.md)에 남기고 파일별 위치와 해시는 [증거 목록](evidence-index.md)에 연결합니다.

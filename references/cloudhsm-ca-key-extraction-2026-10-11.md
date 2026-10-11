# Root·First ICA 개인키의 서명 전용 사용과 추출 정책 검토

조사일: 2026-10-11. 대상: AWS CloudHSM `hsm2m.medium`, FIPS 모드에서 생성할 Root·First ICA의 ECDSA P-384 개인키.

상태: 공식 원문 확인과 프로젝트 판단. 조사 후 사용자가 반영을 요청하여 서명 전용·`extractable=false`·`sensitive=true`·`token=true` 정책과 CloudHSM 암호화 클러스터 백업을 통한 복구 방향을 채택했다. 이는 프로젝트 결정 기록이며, 실제 환경 설정·반출 거부·백업 복원 시험은 수행하지 않았다.

## 1 결론

**CA 개인키의 평문 반출은 C2PA CP v0.2가 명시적으로 금지한다. 그러나 암호화된 백업까지 금지하지는 않으며, 오히려 백업과 off-site 사본을 요구한다.** CP가 AWS의 `extractable` 속성값을 직접 지정하지는 않는다.

이번 구성에서는 **Root·First 개인키를 서명 전용으로 사용하고, 일반 키 반출은 `extractable=false`로 차단하며, 복구는 CloudHSM의 암호화된 클러스터 백업으로 설계하는 것을 권고한다.** 이는 CP의 평문 금지를 구현하면서 불필요한 반출 경로를 추가로 줄이는 프로젝트 판단이다.

## 2 C2PA 원문에서 확인한 요구

사용한 원문은 공식 저장소 `c2pa-org/conformance-public`의 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`, `docs/v0.2/C2PA Certificate Policy.md`다. 로컬 원문 사본의 HEAD와 수정 없음 상태를 확인했다. 아래 내용은 설계 산출물이나 프로젝트 출처 목록이 아닌 이 원문을 근거로 한다.

| CP 조항 | 요구 | 이번 설계에서의 의미 |
|---|---|---|
| Controls for CA Keys / Key Storage, 항목 2 | CA 개인키가 암호 모듈 경계 밖에서 평문으로 존재해서는 안 됨 | EC2 파일·메모리에 실제 개인키를 평문으로 꺼내는 경로 금지 |
| Key Usage and Access Control, 항목 1·2 | Root·Intermediate 키에 단독 접근을 막는 다인 통제를 적용하고, 개인키 사용은 암호 모듈 안에서 수행 | HSM 밖 소프트웨어 서명 금지. 복원 환경도 단독 사용 가능 상태로 만들지 않음 |
| Key Backup and Recovery, 항목 1·2 | 매년 검토하는 공식 복구 계획, 백업의 식별·관리, 원본과 같은 다인 통제 | 암호화되었다는 이유만으로 단독 복원·사용을 허용하지 않음 |
| Key Backup and Recovery, 항목 3·4 | CA 개인키의 off-site 사본 최소 하나, 백업 개인키의 모듈 밖 평문 반출·저장 금지 | 암호화된 백업을 유지하면서 별도 위치의 사본과 복원 통제를 설계 |
| Key Archival | CA 개인키 아카이빙 금지 | 운영 복구용 백업과 사용 종료 후 아카이브를 혼용하지 않음 |

원문: [Key Storage와 백업·사용 통제](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys).

Root 키의 서명도 모든 문서를 대상으로 허용되는 것은 아니다. CP는 Root 자기서명 인증서, 하위·교차 CA 인증서, OCSP 응답자 인증서, CRL로 용도를 제한한다. 이번 행사의 Root 서명은 자기서명과 First 인증서에 한정한다. First CSR 서명은 기존 행사 범위를 따른다. [Key Pair and Certificate Usage](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage)

## 3 추출이라는 말의 구분

| 작업 | CP에 따른 해석 | 이번 구성에 대한 권고 |
|---|---|---|
| 실제 개인키를 평문 파일·메모리로 반출 | 명시적 금지 | 금지 |
| 암호화해 개인키를 일반 파일로 반출하는 key wrap | 모든 암호화 반출을 일괄 금지하는 문구는 확인하지 못함. 평문 노출 방지·모듈 안 사용·다인 통제 등 충족 여부를 별도 검토해야 함 | 별도 필요가 없어 차단. 암호화됐다는 이유만으로 허용하지 않음 |
| CloudHSM의 암호화된 클러스터 백업·복원 | 백업 요구에 대응할 수 있는 구현 후보. 실제 다인 통제·off-site·복원 결과를 입증해야 함 | 이 경로를 복구 설계의 기본 후보로 사용 |
| 공개키·CSR·인증서 출력 | CA 개인키의 비밀 반출과 다른 작업 | 행사에 필요한 출력 유지 |

**`extractable=false`는 사용자가 일반 키 반출 명령으로 개인키를 꺼내지 못하게 하는 설정이다. 백업을 없애겠다는 뜻이 아니다.**

## 4 AWS 기능과 속성의 의미

CloudHSM CLI의 `extractable` 기본값은 `true`다. 선택한 `hsm2m.medium`에서는 `true`에서 `false`로 변경할 수 있지만 반대 방향은 허용되지 않는다. 따라서 반출을 금지하려면 생성 시점부터 `false`를 명시하는 편이 맞다. [AWS CLI 속성 표](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html)

AWS의 CLI AES-GCM wrap 명령은 **반출할 대상 키의 `extractable=true`**를 요구한다. 따라서 암호화한 파일로 반출하는 기능도 이 속성과 관계가 있다. CA 키 자신의 `wrap=false`는 다른 키를 감싸는 용도를 금지하는 것이고, CA 키가 다른 wrapping key에 의해 반출되는 것과는 다르다. 반출 차단에 `wrap=false`만 의존하면 안 된다. [AWS CLI wrap 요구](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-wrap-aes-gcm.html)

HSM이 처음에는 키를 암호화해 내보내더라도 호스트에서 풀어 실제 개인키가 평문이 될 수 있다. AWS의 KMU `exportPrivateKey` 설명이 이러한 경로를 명시하며 추출 가능한 개인키를 전제로 한다. 이 자료는 위험 경로를 설명하는 근거이고, SDK 3 도구를 이번 `hsm2m.medium`의 실행 도구로 채택한다는 뜻은 아니다. [AWS 평문 개인키 export 설명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key_mgmt_util-exportPrivateKey.html)

CloudHSM 서비스 백업은 사용자가 실행하는 일반 key wrap과 다른 경로다. AWS는 HSM이 데이터를 내부에서 암호화하고, 백업에 사용자·키·설정을 포함하며, 복원 HSM에 원래 보호·접근 통제가 복원된다고 설명한다. [백업 보안](https://docs.aws.amazon.com/cloudhsm/latest/userguide/data-protection-backup-security.html), [클러스터 백업](https://docs.aws.amazon.com/cloudhsm/latest/userguide/manage-backups.html)

이 공식 설명을 근거로 **일반 반출 차단과 서비스 백업은 분리해서 설계할 수 있다**고 판단한다. 다만 이번 SDK·모델·FIPS 모드에서 `extractable=false`로 생성한 테스트 키의 백업 포함·복원·속성 유지까지 검증한 것은 아니다. 운영 행사 전 시험해야 하며, 확인되지 않은 복구 성공을 완료로 기록하지 않는다.

## 5 불허를 권고하는 이유와 대가

| 판단 근거 | 의미 |
|---|---|
| 이번 운영 흐름에 실제 개인키 파일이 필요 없음 | 애플리케이션은 공개키로 본문을 만들고 CLI는 HSM 안에서 서명하므로 개인키 반출을 켤 기능적 이유가 없음 |
| 평문 금지의 구현 경로를 단순하게 유지 | 반출 파일, wrapping key, 호스트 복호화, 다른 모듈로의 재반입까지 보호할 부담을 줄임 |
| 기존 `2 of 3` 서명 통제의 보호 범위를 유지 | 반출·재반입이 허용되면 목적지에서도 같은 다인 통제를 보장해야 함. 반출을 차단하면 이 추가 경로를 줄일 수 있음 |
| 복구는 별도 서비스 기능으로 설계 가능 | 일반 키 반출을 켜지 않고 암호화된 클러스터 백업·복원을 검토할 수 있음 |

대가는 이식성이다. `extractable=false`로 생성한 키는 나중에 일반 wrap/export로 다른 공급자의 HSM에 옮기는 방식에 사용할 수 없다. CloudHSM 백업도 AWS가 정한 HSM 복원 범위에 제한된다. 따라서 향후 이전에는 새 CA 키·인증서 체계로 전환하는 계획이 필요할 수 있다. 이런 이식성 요구가 현재 명시되지 않았으므로, 이번에는 반출 경로 축소를 우선하는 판단이다. [AWS 속성 제한](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html), [백업 복원 범위](https://docs.aws.amazon.com/cloudhsm/latest/userguide/data-protection-backup-security.html)

## 6 서명 전용 속성에 반영할 내용

| 항목 | 값·정책 | 상태 |
|---|---|---|
| 개인키 서명 | `sign=true` | 사용자 결정 |
| 복호화·파생·다른 키 unwrap | `decrypt=false`, `derive=false`, `unwrap=false` | 사용자 결정에 따른 금지 |
| 그 밖의 개인키 암호 연산 | 암호화·검증·다른 키 wrap 용도도 허용하지 않음 | 생성 템플릿과 실제 조회에서 지원 여부·금지 상태 확인 |
| 일반 개인키 반출 | `extractable=false` | 조사 권고를 사용자 요청으로 채택. 생성 시 적용할 정책 확정 |
| 평문 속성 노출 방지·영구 보관 | `sensitive=true`, `token=true` | 보호·백업 설계에 반영. 실제 생성 명령·시험은 후속 작성 |
| 속성 변경·삭제·관리 quorum | 별도 설계 필요 | 기존 미정 상태 유지 |

AWS CLI 속성 표는 private key의 `wrap`을 생성 시 설정할 수 없는 항목으로 표시한다. 따라서 `wrap=false`를 개인키 생성 인자에 기계적으로 넣지 않는다. 해당 클래스가 지원하는 속성만 명령에 전달하고, 지원하지 않는 용도는 실제 조회와 거부 시험으로 확인한다. 공개키의 서명 검증과 공개키 출력은 개인키의 서명 전용 정책에 포함해 금지하지 않는다. [AWS CLI 속성 표](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html)

HSM의 `sign=true`는 서명 가능한 키라는 뜻이며 C2PA가 허용한 문서 종류까지 HSM이 판별한다는 뜻은 아니다. 고정 본문·작업 종류·키 대조와 승인 절차를 함께 적용한다.

## 7 운영 전에 확인할 사항

1. 테스트 키 생성 직후 `sign=true`, 서명 외 용도 금지, 선택한 `extractable`·`sensitive`·`token`과 사용 quorum `2`를 조회한다.
2. 유효한 승인·세션을 갖춘 테스트에서도 복호화·파생·unwrap 등 금지된 개인키 용도가 거부되는지 확인한다. 단순한 로그인 실패를 키 속성에 의한 거부로 기록하지 않는다.
3. 채택한 `extractable=false`에 따라 실제 반출 명령이 키 속성 때문에 거부되는지 확인한다. 정책에 맞는 wrapping key와 필요한 승인을 준비한 시험으로 원인을 구분한다.
4. 테스트 키의 백업 포함, 복원 후 동일 공개키·속성·O/A/B 승인 집합·`2 of 3` 서명 통제 유지, 승인 부족 시 거부를 확인한다.
5. 백업 복사·복원·삭제 권한과 복원된 사용자/승인키를 단독으로 우회할 수 있는 관리 경로를 검토한다. HSM 서명 quorum만으로 AWS 관리 API까지 보호된다고 간주하지 않는다.
6. off-site 후보로 별도 Region의 암호화된 백업 사본을 검토한다. 목적지·보존·다인 관리·복원 시험은 아직 미정이며, CP의 off-site 수용을 완료로 기록하지 않는다. [AWS Region 간 백업 복사](https://docs.aws.amazon.com/cloudhsm/latest/userguide/copy-backup-to-region.html)

## 8 행사 문서와 연결

서명 전용·추출 불허의 채택 상태는 [행사 설정](../root-key-design/ceremony/root-first-001/settings.md#개인키-용도와-추출-검토)에 연결한다. 해당 파일은 설계 반영 위치이며 이 조사의 사실 근거로 사용하지 않았다.

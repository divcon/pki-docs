# Root와 First ICA 키 관리·속성 잠금 재검토 기록

기록일: 2026-10-11. 상태: 사용자 요청에 따라 권장안을 행사 초안에 잠정 반영했다. 나중에 재검토할 기준이며, 실제 HSM 설정·구현·시험·행사 수행 승인은 완료하지 않았다.

**서명과 키 관리는 각각 AWS quorum으로 보호하고, 금지할 기능은 속성으로 막는다. 키 생성·삭제·백업·실행 환경은 별도 통제가 필요하다.** 운영 설정은 [settings.md](settings.md#키-관리와-관리자-통제), 실행 정의는 [runbook.md](runbook.md#관리와-별도-통제-절차), 검증 상태는 [preparation.md](preparation.md#리허설과-통제-시험)에서 관리한다.

이 문서는 프로젝트의 선택과 미해결 사항을 기록한 설계 산출물이다. AWS 기능과 C2PA 요구의 근거는 아래 연결한 공식 원문이며, 이 문서 자체를 표준이나 구현 증거로 사용하지 않는다.

## 이번에 반영한 선택

| 대상 | 잠정 반영한 내용 | 아직 필요한 일 |
|---|---|---|
| Root·First 개인키 서명 | 기존 Key Custodians 중 2명 승인 유지 | 실명·개인 CU·승인키·실제 명령·시험 |
| Root·First 개인키 관리 | 같은 Key Custodians 집합의 2명 승인. 사용 quorum과 별도로 관리 quorum 값 2 | 소유자와 공유 CU 매핑, 잠긴 키의 공유 변경 가능 여부와 거부 시험 |
| HSM 관리자 | 서로 다른 3명의 관리자 계정. user·quorum·cluster 각 서비스의 값 2 | 관리자 지정·승인키·초기 설정·변경 절차·시험 |
| 개인키 속성 잠금 | modifiable=false, destroyable=false를 생성 시 적용하는 기본안 | 폐기 경로·공유 클러스터 영향·실제 잠금 동작을 검증한 뒤 운영 키 생성 허용 |
| 키 생성 | AWS quorum 밖의 별도 생성 계획 승인 Key Custodians의 2 of 3 채택 | 인증 수단·우회 차단 구현·시험은 후속 작성 |
| AWS API·실행 환경 | 권한 분리와 별도 다인 승인 실행 경로 | IAM/SCP 적용 범위·실행 프로그램·코드 변경·복구 권한·시험 |

2 of 3과 위 AWS 속성값은 프로젝트 선택이다. CP가 모든 관리 작업에 이 정족수나 특정 AWS 속성값을 지정한다고 해석하지 않는다. C2PA CP는 CA 키 생성의 다인 통제·지식 분할, CA 키 단독 접근 방지, 백업의 동일한 다인 통제 등을 요구한다. `Key Destruction`은 `No stipulation`이며 이 문서의 폐기 검증 조건은 잠금 선택에 따른 프로젝트 운영 조건이다. [고정 CP 원문](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md)

## AWS quorum이 보호하는 범위

| 서비스 | 공식 지원 작업 | 이번 적용 |
|---|---|---|
| key-usage / CU | key sign | S02·S04·S05의 서명 승인 |
| key-management / CU | key wrap·unwrap·share·unshare·set-attribute | 공유·공유 해제 및 허용된 관리. 금지한 암호 연산이나 잠긴 속성 변경은 승인 수를 충족해도 허용하지 않음 |
| user / admin | user create·delete·change-password·change-mfa | 사용자 관리 승인 |
| quorum / admin | quorum token-sign set-quorum-value | 관리자 서비스의 승인 기준 변경 보호 |
| cluster / admin | cluster mtls register-trust-anchor·deregister-trust-anchor·set-enforcement | hsm2m.medium의 mTLS 설정 변경 보호 |

위 범위의 원문은 [AWS quorum 지원 목록](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm.html)이다. 키 생성과 키 삭제는 이 목록에 없다. 관리자 값 변경 명령의 대상은 user·quorum·cluster이며, 이를 CA 개인키의 사용·관리 quorum 변경 명령과 혼동하지 않는다. [관리자 quorum 설정 명령](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-qm-token-set-qm.html)

서명과 관리에는 각각 해당 서비스의 토큰을 사용한다. 토큰은 성공한 한 작업과 현재 CLI 로그인 세션에 유효하며 다른 애플리케이션에서 인증에 사용할 수 없다. 토큰 승인과 실제 작업의 허용 조건을 모두 충족해야 한다. [AWS 키 관리·사용 quorum 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

키 속성 변경은 원칙적으로 소유 CU가 실행한다. 공유 CU의 승인 서명이 유효해도 그 사람이 소유자 전용 명령을 실행할 권한까지 얻는 것은 아니다. 관리자 계정과 CU 계정도 별도 역할이다. [속성 변경 권한](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-set-attribute.html), [키 공유 권한](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-share.html)

## 승인자 명단과 작업 내용도 관리해야 한다

quorum 값 2는 승인 가능한 사람이 항상 세 명이라는 뜻이 아니다. 키 소유자와 공유 CU가 연결 사용자 집합이므로, 공유 변경은 승인자 집합 변경으로 관리한다. Key Custodians 외 CU 추가는 현재 정책에서 허용하지 않으며, 승인자 교체는 정책·명단·등록키를 함께 검토하고 변경 승인을 받아야 한다. 사용자 수·신원·등록키를 작업 전후 대조한다. [AWS CU quorum 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html)

AWS 토큰 문서는 서비스와 키의 연결을 설명한다. 특정 변경값이나 명령 전체를 고정하는 보장으로 확대 해석하지 않는다. 별도 작업 계획에 작업 ID, 대상 키, 현재값·변경값, 명령, 승인자 명단, 기한을 고정하고 실행 직전 대조와 사후 조회를 수행한다. 이 연결 방법과 우회 차단은 아직 구현하지 않았다.

Crypto Officer의 자기승인은 개인 승인키로 유효한 토큰 서명을 남긴 경우에만 1명으로 센다. 명령 실행 자체는 승인으로 세지 않는다. 같은 사람이 여러 계정·승인키를 관리하여 두 명으로 계산되는 경로를 차단해야 한다. 관리자 승인키도 개인별로 보호하고 CU 승인과 구분한다.

## 속성 잠금의 목적과 대가

개인키의 기존 sign=true, decrypt=false, derive=false, unwrap=false, extractable=false, sensitive=true, token=true에 modifiable=false와 destroyable=false를 추가한다. 개인키 생성 인자로 지원하지 않는 wrap 속성은 전달하지 않으며, 조회에서 서명 외 용도가 활성화되지 않았는지 검사한다. 공개키 출력·검증은 개인키 추출과 구분한다.

| 선택 | 보호 목적 | 재검토할 제약 |
|---|---|---|
| extractable=false | 일반 개인키 반출 차단 | 선택한 hsm2에서는 true로 되돌릴 수 없어 일반 반출을 통한 다른 공급자 이전이 제한됨 |
| modifiable=false | 서명 외 용도를 나중에 켜는 속성 변경 차단 | true로 되돌릴 수 없음. 속성 변경 승인 quorum은 잠금을 해제하는 수단이 아님 |
| destroyable=false | 소유자 단독의 개별 키 삭제 차단 | 키 삭제 자체에 quorum이 붙는 것은 아님. modifiable=false와 조합하면 삭제 허용으로 바꾸는 경로도 제한됨 |

AWS는 세 속성의 생성 시 설정을 지원하고 extractable·modifiable의 변경 방향을 명시한다. [AWS 속성 표](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html) 객체의 변경 가능 여부와 C_DestroyObject 허용 여부는 [PKCS #11 객체 속성 정의](https://docs.oasis-open.org/pkcs11/pkcs11-base/v2.40/pkcs11-base-v2.40.html)의 서로 다른 속성이다. 실제 CloudHSM CLI의 삭제 거부와 잠금 동작은 테스트 키로 확인한다.

**폐기 계획과 잠금 시험이 미완료이면 이 기본안으로 운영 키를 생성하지 않는다.** 개별 키를 폐기할 수 있는 경로, HSM·클러스터 단위 폐기 필요 여부, 같은 클러스터의 다른 키 영향, 관련 백업·복사본·복원 가능한 사본의 처리와 증거를 정해야 한다. HSM·클러스터 삭제만으로 모든 백업까지 폐기되었다고 판단하지 않는다.

modifiable=false가 공유·공유 해제·승인키 등록·교체까지 잠근다고 단정하지 않는다. 잠긴 키에서 승인자 교체와 복구가 가능하고 정책이 유지되는지 별도로 검증한다. 실패하면 값을 임의로 완화하지 않고 재검토·변경 승인·필요한 재시험을 수행한다. 대안인 modifiable=true는 폐기·속성 변경의 유연성을 남기지만 승인 후 금지 기능을 켤 여지도 남는다는 대가가 있다.

## 별도 통제가 필요한 작업

| 작업 | AWS 네이티브 보호의 한계 | 반영한 통제 방향 |
|---|---|---|
| 키 생성 | 생성 요청에 --approval이 없음 | 계획·명령 다인 승인, 제한된 실행 경로, 직접 CLI·다른 호스트/SDK·관리자 우회 차단 |
| 개별 키 삭제 | key delete에 --approval이 없고 소유 CU가 실행 | destroyable=false 차단과 별도 폐기 계획. 삭제 자체를 관리 quorum 지원으로 기록하지 않음 |
| 백업 복원·복사·삭제·보존기간 변경 | AWS API/IAM 영역 | 작업자 직접 권한 제한, 별도 다인 승인 실행, 승인 경로·권한 정책 변경도 분리 |
| HSM·클러스터 삭제 | 개별 키 속성으로 보호되지 않음 | 파괴 권한 분리, 다인 승인, 백업·사본 처리와 결과 확인 |
| EC2·jumphost·네트워크·실행 프로그램 변경 | HSM quorum 대상이 아님 | 변경 권한과 승인 권한 분리, 승인한 코드·명령·설정의 버전과 해시 확인 |
| 승인 공개키 등록·교체 | 지원 목록에서 직접 보호 여부를 확정할 수 없음 | 본인 확인·공개키 지문 대조·명단 변경 승인·전후 확인·단독 교체 거부 시험 |

공식 명령: [EC 키 생성](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html), [키 삭제](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-delete.html). AWS API 영역은 [CloudHSM IAM 작업 목록](https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudhsm.html)을 근거로 한다. HSM 내부 작업은 IAM 사용자 대신 별도 HSM 사용자로 인증한다. [사용자 구분](https://docs.aws.amazon.com/cloudhsm/latest/userguide/hsm-users.html)

IAM/SCP는 권한을 제한하는 도구이며 그 자체로 2인 승인을 검사하는 기능이라고 기록하지 않는다. 승인 기록만 남기고 같은 명령을 직접 실행할 수 있으면 우회 가능하다. 승인 검사와 제한된 실행 권한을 연결하고, 한 사람이 그 검사·정책·코드를 바꿀 수 있는 경로도 차단해야 한다. AWS API 작업의 구체 정족수·역할은 후속 결정한다. 생성은 별도 정책으로 Key Custodians의 2 of 3을 채택했으며 이를 다른 작업에 자동 적용하지 않는다.

백업 복원은 당시의 사용자·키·설정·정책도 복원한다. 복원한 환경은 현재 승인자·등록키·공유·quorum·속성·접속 정책과 대조하기 전 사용하지 않는다. 과거 퇴직자나 폐기한 승인키가 되살아나는 경로도 검사한다. [AWS 복원 설명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster-from-backup.html)

## 다시 검토할 항목과 판정 기록

모든 시험은 리허설용 환경·키로 수행한다. 운영 키에 파괴 시험을 수행하지 않는다.

| ID | 사람이 확인할 질문·필요한 증거 | 현재 상태 |
|---|---|---|
| M01 | Key Custodians와 키 소유/공유·등록키가 일치하는가? 관리 승인 0명·1명·중복·집합 밖 승인은 거부되고 Key Custodians가 허용되는가? | 계정 미정 / 미실시 |
| M02 | modifiable=false에서 충분한 승인으로도 금지 속성을 켤 수 없는가? destroyable=false에서 소유자의 직접 삭제가 거부되는가? | 미실시 |
| M03 | 잠긴 키의 공유·공유 해제와 승인자 교체를 관리할 수 있는가? 공유 감소·추가·다른 SDK 경로가 승인 기준을 우회하지 않는가? | 미실시 |
| M04 | 관리자 user·quorum·cluster의 최종값이 모두 2인가? 단독 변경·승인 기준 낮추기·계정/MFA/mTLS 변경이 거부되는가? | 관리자 미정 / 미실시 |
| M05 | 승인키 등록·교체와 실행 코드·IAM 정책 변경을 한 사람이 우회할 수 없는가? | 구현 미정 / 미실시 |
| M06 | 백업 복원 후 동일 공개키·잠금·현재 승인 명단·quorum·접속 정책을 확인하고 사용을 허용할 수 있는가? | 미실시 |
| M07 | 잠긴 키와 관련 백업·사본을 실제로 폐기할 수 있는가? 공유 클러스터의 다른 키에 미치는 영향은 수용 가능한가? | 폐기 계획 미정 / 운영 생성 전 필수 |
| M08 | 생성·AWS API의 별도 다인 승인 실행이 직접 CLI/API·다른 호스트·관리자·코드 변경으로 우회되지 않는가? | 생성 2 of 3 확정 / AWS API 정족수·구현 상세 미정 / 미실시 |

검토 책임자·기한: {{관리통제_재검토_책임자와_기한}}. 자료는 준비 현황과 승인본 목록에 연결한다.

| 검토일·검토자 | 대상 ID와 실제 결과·증거 | 유지·변경·보류 판단과 이유 | 변경 문서·버전·재시험·승인 |
|---|---|---|---|
| {{재검토_일자와_검토자}} | {{재검토_항목과_증거}} | {{재검토_판단과_이유}} | {{재검토_변경과_승인}} |

검토 시 초안 반영과 실제 설정 완료를 구분한다. 잠금을 완화하거나 승인자·정족수를 바꾸려면 근거·영향·재시험과 승인 버전을 남긴다. 운영 키 생성 후에는 되돌릴 수 없는 속성을 문서 수정만으로 바꿀 수 있다고 가정하지 않는다.

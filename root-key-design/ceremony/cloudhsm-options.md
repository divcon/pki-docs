# CloudHSM 키 생성 추가 옵션

[Key Ceremony](README.md)의 수행 절차가 확정된 뒤, 구현 단계에서 검토할 설정이다. 현재 선택한 키 알고리즘은 Root·First 모두 EC이며 곡선은 미정이다.

아래 값은 구현 후보다. `제안`은 승인 전 후보, `미정`은 구현 시 결정할 값이며 `비적용`은 현재 알고리즘에서 사용하지 않는 옵션이다. 실제 운영 키 생성 전에는 선택한 설정으로 검증을 마친다.

## 설정 항목과 선택값

아래는 CLI의 생성 인자와 키 속성이다. C2PA가 지정한 옵션 이름·고정값이 아니며, 선택한 HSM 모델·모드·CLI 버전에서 지원 여부를 확인한다. 속성의 `공개키`·`개인키` 표시는 각각 `--public-attributes`·`--private-attributes`에 해당한다. [AWS EC 생성 명령][aws-ec] · [키 속성][aws-attributes]

| 설정 항목 | 의미·선택 조건 | Root 선택값 | First 선택값 |
|---|---|---|---|
| 대상 클러스터 `--cluster-id` | 실행할 클러스터 식별자 | 미정 | 미정. 같은 클러스터 사용 검토 중 |
| 공개키·개인키 라벨 `--public-label`, `--private-label` | 사람이 구분할 이름. 키 지문도 함께 기록 | 미정: Root용 두 이름 | 미정: First용 두 이름 |
| 키 ID `id` | 선택적 관리 식별자. hsm2m에서 설정 가능 | 미정 | 미정 |
| RSA 공개 지수 `--public-exponent` | RSA에만 필요. AWS 허용값은 65537 이상 홀수 | 비적용: EC 선택 | 비적용: EC 선택 |
| 영구 보관 `token`·`--session` | `--session` 키는 세션 종료 시 사라짐 | 제안: `token=true`, `--session` 미사용 | 제안: 동일 |
| 개인키 `private`, `sensitive` | 개인키 접근·민감 속성 | 제안: 둘 다 `true` | 제안: 둘 다 `true` |
| 개인키 `extractable` | 암호화된 키 반출도 제한하는 비추출 설정. 기본값은 `true` | 제안: `false` | 제안: `false` |
| 개인키 `sign` | HSM 서명 허용. RSA/EC 기본값은 `false` | 제안: `true` | 제안: `true` |
| 공개키 `verify` | HSM 안에서 검증할 때 사용 | 제안: `true` | 제안: `true` |
| 암호화·복호화·키 파생·래핑 용도 | `encrypt`, `decrypt`, `derive`, `wrap`, `unwrap` 중 해당 키·모델에서 설정 가능한 속성 | 제안: 모두 `false` | 제안: 모두 `false` |
| 속성 변경 `modifiable` | `false`로 바꾸면 `true`로 되돌릴 수 없음 | 미정: 향후 관리 절차 확인 | 미정: 향후 관리 절차 확인 |
| 삭제 허용 `destroyable` | 키 삭제 가능 여부 | 미정: 폐기 절차 확인 | 미정: 폐기 절차 확인 |
| 생성 계정·키 소유자 | 생성 명령을 실행할 개인별 CU 계정 | 미정: 계정명 | 미정: 계정명 |
| 공유 사용자 `--share-crypto-users` | 키를 공유할 CU 목록 | 미정: 같은 담당자 그룹의 계정 목록 | 미정: 같은 담당자 그룹의 계정 목록 |
| 사용 승인 수 `--use-private-key-quorum-value` | 이후 서명 등 키 사용에 필요한 승인 수 | 미정: 최소 2인 통제를 충족할 N/M | 미정: 최소 2인 통제를 충족할 N/M |
| 관리 승인 수 `--manage-private-key-quorum-value` | 지원되는 키 공유·속성 변경 등 관리 작업의 승인 수 | 미정: 관리 권한표와 함께 결정 | 미정: 관리 권한표와 함께 결정 |

키 소유자와 공유 사용자 수가 사용·관리 quorum 중 큰 값 이상이어야 한다. AWS가 제공하는 quorum 값의 범위는 0~8이지만, 단독 사용을 허용하는 값을 운영안으로 채택하지 않는다. 실행자를 승인 인원에 포함할지와 실제 사람별 N/M 계산은 미정이다. 이 값들은 **생성된 키의 사용·관리 조건**이며 생성 명령 자체의 다인 승인이 아니다. HSM 사용자 관리자의 quorum도 별도다. [AWS quorum 설정][aws-quorum-setup] · [지원 작업][aws-services]

`extractable=false`는 평문 반출 금지보다 강한 구현 제안이다. C2PA는 통제된 백업을 요구하므로 실제 HSM 백업·복구와 이 설정의 관계를 검증한다. 암호화 반출을 허용하는 대안을 검토한다면 래핑 키·`wrap-with-trusted`·반출 권한도 별도로 정한다. [CP 키 보호][keys] · [AWS 키 속성][aws-attributes]

## 구현 시 확인

생성 후에는 실제 알고리즘·크기/곡선·속성·소유/공유 사용자·quorum을 선택값과 대조하고, HSM 키 식별자와 공개키 지문을 기록한다. `local` 같은 조회 속성은 생성 결과로 확인한다.

HSM의 `sign=true`만으로 인증서 발급 용도가 제한되지는 않으므로 앱의 [허용 용도 검사][usage]도 필요하다.

## 원문

CloudHSM 옵션은 2026-10-08 확인한 AWS 공식 문서, C2PA는 Conformance v0.2 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc` 기준이다. 구현할 때 선택한 모델·모드·CLI 버전의 지원 범위를 다시 확인한다.

[keys]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys
[aws-services]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-service-names.html
[usage]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage
[aws-ec]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html
[aws-attributes]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html
[aws-quorum-setup]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html

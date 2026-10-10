# CloudHSM 세레모니 준비와 실행 절차

[Key Ceremony](README.md)에서 CloudHSM을 선택할 때 확정할 설정과, 행사 스크립트에 연결할 공통 수행 절차다. 현재 입력값은 Root·First 모두 EC P-384이며, 이 문서의 계정·권한·quorum·운영 구성은 아직 미정이다.

**실제 CloudHSM 실행 코드와 리허설 결과는 아직 없다.** 아래 절차를 적었다는 사실만으로 생성 통제·다인 승인·백업·복구가 구현되었다고 판단하지 않는다. `제안`은 승인 전 후보, `미정`은 행사 승인 전에 결정할 값, `비적용`은 현재 알고리즘에서 사용하지 않는 옵션이다.

스크립트에서는 “승인을 확보한다”로 줄이지 않고 아래 ID를 호출한다. 각 ID에 실제 담당자, 실행 위치, 명령 파일·도구 버전·해시, 입력·출력, 통과·중단 기준과 증거 위치를 연결한다. 현재 ID는 수행 절차 식별자이며 실행 가능한 명령이 아니다.

| 행사 단계 | 연결할 절차 | 수행 기록에 남길 것 |
|---|---|---|
| 행사 전 준비와 S00 | [B00](#b00) | 초기 설정 인계, 실제 권한·정족수·등록·환경 조회와 통제 시험 |
| S01 Root 생성, S03 First 생성 각각 | [G01–G05](#g01) | 공동 접근 활성화부터 생성·조회·공개키 추출·접근 회수까지 |
| S02 Root 자기서명, S04 First CSR, S05 First 인증서 각각 | [Q01–Q08](#q01) | 서로 다른 작업 ID·본문·토큰·승인·서명 응답·독립 검사 |
| 생성 후 보호와 S06 | [B01](#b01) | 실제 신규 키를 포함한 백업 확인, 보류 조건, 복구 권한 |
| 중단·행사 종료와 S07 | [X01](#x01) | 세션·토큰·임시 접근 종료와 남는 운영 접근 인계 |

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

## B00 · 초기 설정과 통제의 인계

<a id="b00"></a>

이 절차는 최초 설정을 매 행사마다 반복하라는 뜻이 아니다. 별도 준비 작업에서 완료한 설정·시험을 S00에서 실제 상태와 대조한다. 설정이 없거나 증거와 현재 상태가 다르면 키 생성을 시작하지 않는다.

1. **환경 담당자와 검증자**가 AWS 계정·리전·클러스터 ID, 각 HSM ID·모델·모드·상태, 모듈 적격성 자료, CLI/SDK·호스트·연결 설정·실행 코드 버전을 확인한다. 일부 HSM 장애, 사용자·키 동기화 미완료, 다른 클러스터 선택 시의 중단 기준을 확정한다. 사람의 승인 quorum과 HSM 복제 가용성 quorum을 구분한다. [AWS 키 내구성][aws-durability]
2. **진행 책임자**가 실제 사람과 개인 CU/admin 계정, 승인 공개키 지문, Root/First 키 소유·공유 관계, 허용 승인 집합, 대체자·겸임을 대조한다. 한 사람의 여러 계정을 여러 승인자로 세지 않는다. 공유받은 CU의 실제 키 사용 권한까지 포함한다.
3. **각 승인자**의 CA 키와 별개인 RSA 2048 승인키 생성·개인 보관·등록 증거를 확인한다. 준비 작업에는 registration token 발급, 해당 개인키의 소유 증명, 본인 CU/admin으로 공개키 등록, 등록 상태 조회가 포함되어야 한다. 실제 장치와 도구가 AWS 승인 서명 형식을 지원하는지 시험한다. 승인 개인키·비밀번호를 실행 호스트나 증거 묶음으로 모으지 않는다. `user list`의 quorum 등록 상태만으로 등록 공개키 지문과 실제 사람 연결을 모두 증명했다고 보지 않는다. [AWS CU 초기 설정][aws-quorum-setup]
4. **HSM 관리자와 검증자**가 `quorum token-sign list-quorum-values`로 관리자 `user`와 `quorum` 서비스 값을 각각 확인한다. 초기 설정 인계에는 최초 관리자 접근 통제, 개인별 관리자·승인키 등록, 두 값의 설정, 초기 자격의 회수, 관리자 단독 변경 거부 시험이 있어야 한다. AWS 초기 예시의 `user=2, quorum=1`을 최종 상태로 복사하지 않는다. 실제 선택값과 변경 절차를 검증하며, AWS 변경 안내의 `user <= quorum` 조건도 대조한다. hsm2m에서 mTLS를 사용하면 관련 `cluster` 서비스 통제도 확인한다. [관리자 초기 설정][aws-admin-setup] · [quorum 값 변경][aws-quorum-change] · [지원 서비스][aws-services]
5. **생성 통제 담당자**가 G01/G05에서 실행할 공동 활성화·회수 수단을 제시한다. CU 자격증명, 직접 HSM 접속, 호스트·네트워크·코드 변경, AWS 관리자·복구 경로에서 한 사람이 우회하지 못하는지 시험한 결과를 인계한다. 승인 티켓이나 입회만 있다면 기술적 차단이 구현됐다고 기록하지 않는다. 키 생성 자체는 AWS quorum 지원 작업에 포함되지 않는다. [지원 서비스][aws-services]
6. **검증자**가 허용 승인 집합을 확인한다. AWS CU는 자기 토큰에도 승인할 수 있다. 따라서 “실행자 O 제외, A/B 모두 승인” 같은 정책을 선택한다면 숫자 2만 설정해서 자동 보장되지 않는다. 본문 승인자와 HSM 토큰 승인자를 구분하고, 승인된 집합·필요수에 맞춰 실행기 승인자 검사, 승인키 등록·교체 경로, 직접 CLI 우회를 함께 시험해야 한다. MFA를 선택한 경우 AWS가 설명하는 승인키와 MFA 키의 관계도 확인한다. [CU quorum 주의점][aws-quorum-notes]
7. **기록·보관 담당자**가 로그 수집, 시간 동기화, 원본 응답 저장, 변경 방지·접근·보존, 백업·복구 권한을 확인한다. CloudWatch HSM 관리 로그, 실행기/CLI 기록, AWS 관리 작업 기록, 본문 승인·입회 기록을 구분하고 각 기록의 담당자와 수집 완료 기준을 정한다.

**통과·증거:** 승인된 환경·사람/계정/키 대응표, 실제 조회 결과, 초기 설정 기록, 우회·장애·복구 시험 결과를 E00에 연결한다. 실제 값이나 시험 결과가 미정이면 통과하지 않는다. 테스트 키를 사용한 승인 부족·자기승인·동일인 중복·관리자 변경 시험을 운영 키에서 무계획하게 반복하지 않는다.

## G01–G05 · 키 생성과 생성 직후 보호

Root와 First 각각 수행한다. 운영 생성 명령의 옵션을 현장에서 즉흥적으로 보완하지 않는다.

<a id="g01"></a>

### G01 · 생성 접근을 공동 활성화한다

진행 책임자가 대상 키·클러스터·승인 설정을 선언하고, 승인자들이 실제 생성 명령·옵션과 생성 통제 범위를 확인한다. 지정 담당자들이 B00에서 검증한 수단으로 임시 생성 접근을 활성화한다. 실행자는 자신의 CU로 접속하고 검증자는 활성화 시각·허용 계정·호스트·유효시간을 기록한다.

**통과·증거:** 승인 기록과 실제 활성화 결과가 일치한다. 단독 CU 접속만 확보되고 공동 통제 수단이 없는 경우 “공동 활성화 완료”로 적지 않는다. 실패 시 생성 요청을 보내지 않고 X01에 따라 접근을 회수한다.

<a id="g02"></a>

### G02 · 보호 설정을 포함해 키를 생성한다

실행자는 승인된 `key generate-asymmetric-pair ec` 호출 정의를 사용한다. 곡선, 공개키/개인키 라벨, `--cluster-id`, 영구 키 여부, 공개키/개인키 속성, `--share-crypto-users`, 사용·관리 quorum을 생성 시점에 지정한다. 생성 결과의 원본 응답을 보존한다. 생성 후 나중에 quorum·비추출 속성을 붙이겠다는 보호 공백을 두지 않는다. 생성 명령 자체에 존재하지 않는 quorum 승인 옵션을 만들어 사용하지 않는다. [EC 생성 명령][aws-ec]

속성은 선택한 모델·모드·CLI가 허용하는 조합을 리허설한다. `modifiable=false`처럼 되돌릴 수 없는 설정은 관리·폐기 절차를 확정한 뒤 사용한다. `extractable`, `sign`, 세션 키 여부를 기본값에 맡기지 않는다. 모든 옵션을 무조건 적용하라는 뜻은 아니며, 적용 불가 항목은 검증한 근거와 대체 통제를 남긴다. [키 속성][aws-attributes]

**통과·증거:** 승인된 생성 요청 한 건과 반환된 공개키·개인키 식별자, CLI 결과가 연결된다. 응답 유실·부분 실패·저장 실패 시 자동 재생성하지 않는다. 원래 키의 존재와 보호 상태를 조사하고, 확인할 수 없으면 결과 불명으로 보류한다.

<a id="g03"></a>

### G03 · 실제 키와 클러스터 반영 상태를 조회한다

검증자는 라벨만으로 키를 선택하지 않고 생성 결과의 정확한 key-reference와 클래스·공개키 연결을 확인한다. `key list`의 검증된 필터·상세 조회 절차로 곡선, `local`, 영구 보관, 비추출·용도·변경·삭제 속성, 소유자·공유자·사용/관리 quorum과 coverage를 승인값에 대조한다. 공개키와 개인키의 quorum을 혼동하지 않는다. `key list` 실행 정의에는 한 키만 선택했는지 확인하는 기준도 둔다. [EC 생성 결과][aws-ec] · [CLI 명령 참조][aws-cli]

**통과·증거:** 승인값과 실제 조회값, 예정된 HSM·사용자에 대한 반영 상태가 일치한다. 일부 HSM이나 사용자에서만 확인되면 사전 승인한 장애 기준에 따라 중단한다. 생성 성공 문자열만으로 이 단계를 통과하지 않는다.

<a id="g04"></a>

### G04 · 공개키를 추출하고 지문을 고정한다

실행자는 리허설한 공개키 추출·인코딩 절차로 SPKI DER를 만든다. **이 공개키 추출 명령·변환 도구는 아직 선정·검증되지 않았다.** HSM 조회의 EC point를 SPKI DER와 동일한 바이트로 취급하지 않으며, 개인키 반출이나 소프트웨어 대체 키 생성으로 처리하지 않는다. 검증자는 추출 공개키가 G03의 키 쌍·곡선과 연결되는지 확인하고 SPKI DER SHA-256을 계산한다. First에서는 Root와 다른 공개키인지도 검사한다.

**통과·증거:** 공개키 파일·형식·해시, 양쪽 HSM 키 식별자와 도구 버전·검사 결과를 E01 또는 E03에 남긴다. 공개키 연결을 확인하지 못하면 인증서/CSR 본문을 만들지 않는다.

<a id="g05"></a>

### G05 · 생성 접근을 회수하고 보호 상태를 인계한다

G01 담당자들이 임시 생성 접근을 회수하고 검증자는 직접 재접속·추가 생성 경로에 대한 사전 검증된 확인 절차를 수행한다. 서명용 접근이 필요하면 별도로 승인된 범위만 유지한다. 생성 CU가 키 소유자라는 이유로 계정을 무조건 삭제하거나 후임에게 개인 자격증명을 넘기지 않는다.

**통과·증거:** 생성 접근 회수, 유지할 서명·관리 권한, 신규 키 보호 책임자와 B01 백업 상태를 기록한다. 회수 실패 시 후속 서명을 중단하고 키 보호를 유지한다.

## Q01–Q08 · 매 서명에 적용할 승인과 실행

S02는 Root 키로 TBSCertificate를, S04는 First 키로 CertificationRequestInfo를, S05는 Root 키로 First의 TBSCertificate를 서명한다. 세 작업에 서로 다른 작업 ID와 토큰을 사용한다. 관리 작업에는 별도 서비스와 절차가 필요하며 key-usage 토큰으로 대신하지 않는다.

<a id="q01"></a>

### Q01 · 최종 본문을 준비하고 승인한다

실행자가 승인 프로파일로 최종 DER와 사람이 읽을 필드 목록을 준비하고 검증자가 DN·기간·serial·공개키·확장·발급 허가를 확인한다. 승인자들은 같은 작업 ID·DER SHA-256·서명 키 SPKI 지문·서명 알고리즘·프로파일/도구 버전·승인 기한을 확인한다. CSR도 최종 CertificationRequestInfo DER를 고정한다.

**통과·증거:** 승인한 DER와 본문 표시·키·승인 기록을 변경 없이 연결한다. 증거용 SHA-256과 ECDSA SHA-384 서명용 digest를 구분한다. 토큰에 서명했다는 사실만으로 인증서 본문 전체를 승인했다고 간주하지 않는다.

<a id="q02"></a>

### Q02 · CLI 세션과 실제 서명 키를 확인한다

실행자는 승인된 호스트에서 CLI 세션을 열어 본인 CU로 로그인한다. 검증자는 대상 클러스터, 로그인 주체, 키 식별자·공개키 지문, 사용 quorum·공유자·속성을 대조한다. 세션을 누가 유지하고 승인 중 잠금·단절을 어떻게 감지할지 정한다. 비밀번호를 명령 기록·화면 녹화·증거 파일에 남기지 않는 입력 방식을 리허설한다.

**통과·증거:** 작업과 실행 세션·CU·키가 연결된다. CLI 토큰을 별도 OpenSSL provider/PKCS#11 애플리케이션이나 종료된 실행 프로세스에 전달하면 된다고 가정하지 않는다. CLI 안에서의 실제 서명 호출까지 연결되어야 한다. [AWS 토큰 제약][aws-quorum-use]

<a id="q03"></a>

### Q03 · 해당 작업의 사용 토큰을 발급한다

실행자는 같은 CLI 세션에서 `quorum token-sign generate`의 `--service key-usage`, `--token`, 정확한 키를 선택하는 `--filter`를 사용한 검증된 호출로 토큰을 발급한다. 검증자는 토큰의 service·key_reference, 토큰 해시와 발급 시각을 작업 ID에 연결한다. 아직 서명되지 않은 토큰 원본은 접근 제한된 임시 승인 저장소에 보존한다. 사용 가능한 토큰·승인 묶음은 일반 증거 폴더나 제출본에 복사하지 않으며, 증거에는 식별 해시·승인자·상태를 연결한다. [AWS 토큰 생성][aws-quorum-use]

**통과·증거:** 토큰 대상과 Q02의 키가 일치한다. `quorum token-sign list`의 `minimum-token-count`는 클러스터에서 사용 가능한 토큰 수이며 승인자 수가 아니다. 이를 “승인 두 명 완료”의 판정값으로 쓰지 않는다.

<a id="q04"></a>

### Q04 · 승인자가 각자의 승인키로 서명하고 전달한다

각 승인자는 본문 승인 묶음과 작업 ID, 토큰 해시·대상 키·서비스를 확인한 뒤 본인 장치에서 승인 토큰을 서명한다. 전달 대상·경로·무결성 검사·서명 파일 형식과 반환 담당자를 확정한다. 개인키는 전달하지 않는다. 토큰 서명은 CA 개인키가 아닌 등록된 개인별 RSA 승인키를 사용한다. [AWS 승인 절차][aws-quorum-use]

`token` 필드는 approval_data를 해시한 값이므로 전체 JSON이나 본문 DER를 대신 서명하지 않는다. Base64 해제·digest 입력·서명 형식·인코딩은 선택 도구의 정확한 절차로 고정하고 등록 공개키로 검증한다. 승인자가 다시 해시해서 서명하는 등 AWS가 검증할 바이트와 달라지는 일을 리허설에서 잡는다. 본문 승인 기록과 토큰 승인 서명은 각각 보존하고 같은 작업 ID로 연결한다.

**통과·증거:** 각 승인자의 본문 확인과 토큰 서명이 본인·등록키·대상 작업에 연결된다. 전달 오류, 승인키 분실, 승인자의 관찰 불가 상태에서는 다른 사람의 승인키로 대행하지 않는다.

<a id="q05"></a>

### Q05 · 승인 집합과 시간·세션 조건을 검사한다

실행기와 검증자는 서명자 CU·공개키 지문·실제 사람, 승인된 토큰 승인 집합·필요수, 서명 검증, 원본 토큰과의 일치, 본문 승인 기한과 세션 유지를 확인한다. 본문 승인과 토큰 승인의 담당자·필요수가 다르면 각각 검사한다. 예를 들어 토큰에 A/B만 허용하는 정책이라면 O+A 조합을 허용하지 않는 검사·접근 통제가 필요하다. AWS 자기승인 허용을 역할표 한 줄로 바꾸지는 못한다. [CU quorum 주의점][aws-quorum-notes]

**통과·증거:** 승인 검사 결과·서명자·기한을 기록한다. AWS 안내의 기본 10분 만료를 준비 시간에 반영하고 선택 버전의 실제 동작을 시험한다. 만료·로그아웃·단절·본문 변경이면 이전 승인을 새 토큰에 복사하지 않는다. 결과 상태를 확인하고 Q02 또는 Q03부터 새 토큰과 승인을 확보한다.

<a id="q06"></a>

### Q06 · 실제 입력을 재대조하고 명시적으로 서명을 실행한다

검증자는 CLI가 읽을 최종 파일 바이트 또는 digest가 Q01 승인 DER와 연결되고 서명 키·알고리즘이 일치하는지 확인한다. 담당자의 명시적 실행 지시를 남긴 뒤 실행자가 `crypto sign ecdsa`의 검증된 호출을 실행한다. 실행 정의에는 `--cluster-id`, 정확한 `--key-filter`, `--hash-function sha384`, `--data-type raw` 또는 `digest` 중 선정값, 입력 경로, 서명된 토큰의 `--approval` 경로가 포함되어야 한다. [AWS ECDSA 명령][aws-ecdsa]

**통과·증거:** 요청 전에 작업·입력·키·승인을 원장에 저장하고 실제 호출과 연결한다. token 사용 승인에는 본문 바이트 결합이 자동 제공된다고 가정하지 않는다. 승인 뒤 파일·실행 코드 교체를 막는 통제와 직접 CLI 우회를 함께 검증한다. 구현이 사후 검사로만 바꿔치기를 찾는다면 예방에 성공했다고 기록하지 않는다.

<a id="q07"></a>

### Q07 · 원본 응답을 보존하고 토큰 상태를 기록한다

실행기는 CLI 결과·반환 키 식별자·서명 원본을 손실되지 않는 저장소에 기록하고 저장 성공을 확인한다. 검증자는 요청한 키와 응답의 키를 대조하고 토큰의 사용 후 상태를 수집한다. 토큰은 성공한 한 작업에 사용되며, 실패·취소·세션 종료 때의 처리도 리허설한 절차를 따른다. 살아 있는 승인 토큰은 행사 외부 제출물로 배포하지 않는다. [AWS 사용 절차][aws-quorum-use]

**중단·증거:** 요청 시작 후 응답이나 저장 결과가 불명이면 원장에 결과 불명으로 남기고 자동 재서명하지 않는다. HSM 감사 로그의 부재는 서명하지 않았다는 증명이 아니다. AWS의 공개 감사 로그 표는 일반 ECDSA 서명 결과 조회 수단을 제시하지 않는다. 원본 응답이 있으면 조립·검사·저장을 재개할 수 있지만, 없으면 별도 재수행 판단과 새 승인 없이 완료·미실행으로 바꾸지 않는다. [AWS 감사 로그 범위][aws-audit]

<a id="q08"></a>

### Q08 · 결과를 조립하고 독립 검사한다

실행기는 Base64 서명 응답을 해제하고 ECDSA raw `r||s`를 인증서/CSR에 필요한 ASN.1 DER 서명 값으로 변환해 조립한다. **이 조립 코드와 독립 검사 명령은 아직 구현·검증되지 않았다.** `--data-type`의 raw/digest 차이, SHA-384 처리, r/s 길이·정수 부호·DER 인코딩, 알고리즘 식별자와 파라미터를 테스트 벡터와 별도 도구로 확인한다. [AWS ECDSA 출력 형식][aws-ecdsa]

검증자는 승인 DER가 결과 안에 그대로 들어갔는지, 서명과 공개키·프로파일이 맞는지 검사한다. Root는 자기서명 자체, CSR은 First 키의 소유 증명, First 인증서는 Root 서명과 CSR 공개키 연결을 확인한다.

**통과·증거:** 원본 응답·완성 DER/PEM·각 해시·검사 보고서·원장 저장이 연결되어야 한다. 파일 존재나 CLI 성공만으로 발급 완료로 판정하지 않는다. 검사 실패 때 토큰을 다시 받아 재서명하기 전에 입력·조립·키·승인 중 무엇이 잘못됐는지 조사한다.

## B01 · 신규 키의 백업과 복구 권한 확인

<a id="b01"></a>

보관 담당자는 기존 테스트 키의 복구 시험 결과와 이번 행사 키의 실제 백업 확인을 구분한다. Root·First 생성과 최종 권한 설정을 포함하는 backup ID·상태·시각, 원본 클러스터, 별도 장애 영역의 복제 ID, 보호·보존·복구 책임자를 기록한다. API의 백업 존재만으로 원하는 키와 최종 설정의 포함이 입증된다고 가정하지 않고, 선정한 확인 방법과 리허설 근거를 붙인다.

AWS 자동 백업은 최소 24시간마다 수행되며 즉시 백업을 지시하는 일반 명령은 없다. 클러스터 변경으로 백업을 유발할 수 있지만, 백업만을 위해 HSM을 임의 추가·제거하지 않는다. 생성·최종 설정 시점과 백업을 대조하고 미확보 시 대기한다. 타 리전 복사를 선택하면 대상 backup ID와 `READY` 상태를 확인한다. off-site를 반드시 타 리전으로만 구현해야 한다는 뜻은 아니다. [백업 주기][aws-backup-cycle] · [리전 복사][aws-backup-copy]

복구하면 백업 시점의 사용자·키·설정·정책도 돌아온다. 복구 클러스터를 업무에 연결하기 전에 현행 승인키·퇴사자 회수·권한·quorum·원장 상태와 대조하는 절차가 필요하다. 과거 백업, 다른 리전 복사본, 다른 계정 공유와 복구 권한까지 관리한다. 암호화 백업이라는 사실만으로 원본과 같은 다인 통제가 증명되는 것은 아니다. [백업 복구][aws-restore] · [백업 사용][aws-backups] · [백업 공유][aws-backup-sharing]

**통과·증거:** 실제 신규 키의 백업 확인과 원본 수준의 보호·복구 절차를 기록한다. 백업 생성·복제·검증이 대기 중이면 S06 완료로 적지 않고, 키 보호 담당자·대기 기한·재확인 방법을 남겨 보류 인계한다. 실제 운영 키를 무조건 현장에서 복구하라는 뜻은 아니며 운영 키 복구가 필요한 검증은 별도 승인된 통제 아래 계획한다.

## X01 · 세션·임시 접근 종료와 보호 인계

<a id="x01"></a>

실행자와 운영 인수자는 활성 CLI 세션·미완료 토큰, 행사 호스트·네트워크·AWS 임시 권한, 승인 장치와 임시 파일의 목록을 대조한다. 세션 종료·토큰 무효화와 접근 회수를 검증한 수단으로 수행하고 검증자가 결과를 확인한다. 토큰 파일을 삭제한 사실만으로 HSM 안의 승인이 종료됐다고 간주하지 않는다.

행사 후 유지할 CU·키 소유·공유·서명/관리 권한은 책임자와 사용 통제를 명시해 인계한다. 로그아웃이 계정·공유 권한 회수와 같지는 않다. 키 삭제는 공개된 key-management quorum 목록에 없으므로, 사용 quorum 설정만으로 소유자의 삭제를 막는다고 가정하지 않는다. 키·클러스터·백업 삭제와 속성 잠금은 별도로 검증한 폐기·관리 절차에 따른다. [AWS 키 삭제][aws-delete] · [키 속성][aws-attributes]

**통과·증거:** 종료·회수 결과, 유지되는 운영 접근, 미완료 작업·백업·로그 수집 상태와 보호 책임자를 E07에 남긴다. HSM별 로그 스트림은 서로 다를 수 있으므로 생성·동기화·세션 종료 사건을 한 스트림에서 모두 찾는다고 가정하지 않는다. 서명된 S06 증거 목록은 보존하고 종료 후 추가 자료는 별도 목록과 확인 서명으로 연결한다. [AWS HSM별 로그][aws-log-flow]

## 원문

CloudHSM은 2026-10-10 확인한 AWS 공식 문서, C2PA는 Conformance v0.2 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc` 기준이다. B/G/Q/X 단계·역할·증거 구성은 프로젝트의 보강 절차이며 AWS나 C2PA가 지정한 공식 양식이 아니다. 구현할 때 선택한 모델·모드·CLI 버전의 지원 범위를 다시 확인한다.

[keys]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#controls-for-ca-keys
[aws-services]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-service-names.html
[usage]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-and-certificate-usage
[aws-ec]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-generate-asymmetric-pair-ec.html
[aws-attributes]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-key-attributes-table.html
[aws-quorum-setup]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html
[aws-quorum-use]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html
[aws-quorum-notes]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli.html
[aws-admin-setup]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html
[aws-quorum-change]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-min-value.html
[aws-ecdsa]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html
[aws-cli]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-reference.html
[aws-durability]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/working-client-sync.html
[aws-audit]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm-audit-log-reference.html
[aws-log-flow]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/get-audit-logs-from-cloudwatch.html
[aws-restore]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/create-cluster-from-backup.html
[aws-backups]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/backups-using.html
[aws-backup-sharing]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/sharing.html
[aws-delete]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/manage-keys-cloudhsm-cli-delete.html

[aws-backup-cycle]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/manage-backups.html
[aws-backup-copy]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/copy-backup-to-region.html

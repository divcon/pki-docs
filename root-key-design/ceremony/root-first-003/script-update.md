# Samsung C2PA Key Generation Ceremony Script

- 템플릿 버전: v0.2 (003 개정본, 변경 내역은 부록 D)
- 문서 번호: KGC-C2PA-2026-001
- Ceremony 목적: **Samsung Cloud Service Platform Root CA G1** 및 **Samsung C2PA Intermediate CA G1** 신규 생성
- 본 Script의 범위: 위 두 CA의 키 생성, 인증서 발급, 검증, 보관. 그 외 CA 및 운영 인증서는 본 Script 범위 밖
- 기준: [C2PA Certificate Policy v0.2][cp] *Key Pair Generation and Installation by CAs*, *Controls for CA Keys*, *Certificate Issuance*, *Certificate Profiles* (commit `2466172`)

---

## 목차

1. 승인 및 기본 정보
2. 역할 및 참가자
3. 자재 및 HSM/KMS 명세
4. 사전 조건 확인
5. 실행 단계
   - 5.1 환경 격리 확인
   - 5.2 CloudHSM 클러스터 소유 증명 인증서 생성
   - 5.3 클러스터 초기화 (Root·C2PA)
   - 5.4 활성화 및 KMS 기반 Quorum 설정 (Root·C2PA)
   - 5.5 Platform Root CA 키 생성 및 자체서명 인증서
   - 5.6 C2PA ICA 키 생성 및 발급
   - 5.7 프로파일 자동 검증
   - 5.8 백업 확인 및 두 클러스터 오프라인화
   - 5.9 로그 보존 확인 및 정리
6. 사후 보관 및 접근 통제
7. 참가자 서명
8. 편차 기록 (단계 열에는 5.x.y 형식만 기재)
- 부록 A 설정 / 부록 B 도구 / 부록 C Fingerprint 기록표 / 부록 D 개정 내역

---

## 1. 승인 및 기본 정보

| 항목 | 내용 |
|---|---|
| 일시 | `{{YYYY-MM-DD HH:MM}}` KST |
| 장소 | `<건물/층/룸>` |
| 승인자(경영진) | 성명 / 직책 / 서명 / 일자 |
| 승인자(보안책임자) | 성명 / 직책 / 서명 / 일자 |
| Script 승인 버전 | v`<x>` / SHA-256 `<hash>` — Ceremony 중 변경 불가 |
| C2PA 해석 확인 | 키 생성 다인 통제 방식(생성 시 사용·관리 Quorum 지정 + 독립 입회)에 대한 C2PA 서면 답변: `<보낸 사람/일자/문서ID>` |

## 2. 역할 및 참가자

| 역할 | 성명 | 소속 | 허용 행위 | 금지 행위 |
|---|---|---|---|---|
| Ceremony Administrator (CA-Admin) | | | 단계 호명, 체크, 서명 실행 지시 | CLI/AWS 조작 |
| Crypto Officer (CO) | | | CloudHSM CLI 입력, `cert_tool.py` 실행 | Custodian/Witness 겸임, KMS Quorum 키 사용 |
| AWS IAM Operator (IAM-Op) | | | CloudHSM/KMS 리소스 생성·설정 API | CO 겸임, kms:Sign |
| Key Custodian #1~#3 (KC) | | | 자기 KMS 키로 Quorum 토큰 서명 | CLI 입력, CloudHSM 관리 API |
| Independent Witness (IW) | | | 관찰, 확인 서명, 최종 봉인 | 모든 조작 |

Quorum: 두 클러스터 모두 admin 2-of-3(kc1~kc3), CA 키 사용·관리 2-of-3(cu_kc1~cu_kc3).

## 3. 자재 및 HSM/KMS 명세

### 3.1 CloudHSM

| 항목 | Root 클러스터 (Platform Root 키) | C2PA 클러스터 (C2PA ICA 키) |
|---|---|---|
| 계정 / 리전 | | |
| off-site 백업 리전 | `<DR_REGION>` | `<DR_REGION>` |
| Cluster ID / HSM ID | (4.9 기록) | (4.9 기록) |
| HSM Type / **Mode** | hsm2m.medium / **FIPS** | hsm2m.medium / **FIPS** |
| admin Quorum | 2-of-3 (`user`·`cluster`·`quorum`) | 2-of-3 (`user`·`cluster`·`quorum`) |
| 키 사용·관리 Quorum | 2-of-3 (cu_kc1~cu_kc3) | 2-of-3 (cu_kc1~cu_kc3) |
| CMVP 인증서 번호 / 펌웨어 | | |
| Client SDK 버전 | | |

> Platform Root는 플랫폼 공용 루트이므로 C2PA ICA와 클러스터를 분리한다.

### 3.2 KMS (Custodian Quorum 키)

| Custodian | KMS Key ARN | KeySpec | 허용 IAM Principal | MFA |
|---|---|---|---|---|
| KC1 | `arn:aws:kms:...:key/...` | RSA_2048 SIGN_VERIFY | `<KC1 user/role>` | 필수 |
| KC2 | | | | |
| KC3 | | | | |

### 3.3 소프트웨어

| 항목 | 버전 | SHA-256 |
|---|---|---|
| CloudHSM CLI | | |
| OpenSSL | | |
| AWS CLI | | |
| `cert_tool.py` (부록 B) | | |
| `verify_profile.py` (부록 B) | | |
| `root.cnf`, `ica.cnf` (부록 A) | | |

## 4. 사전 조건 확인

| # | 항목 | 확인자 | ☐ | 시각 |
|---|---|---|---|---|
| 4.1 | 1장 승인 서명 완료 | CA-Admin | ☐ | |
| 4.2 | 전원 출석·신분 확인, 무선기기 반입 금지(KC 서명 단말·MFA 장치는 등록 목록에 한해 허용) | IW | ☐ | |
| 4.3 | 룸 녹화 시작 (`__:__`) | CA-Admin | ☐ | |
| 4.4 | 터미널 세션 녹화 시작 `script -a ceremony_<YYYYMMDD>.log` | CO | ☐ | |
| 4.5 | KMS 키 3개 생성·키정책 적용 완료, 공개키 PEM 추출 완료 (사전 작업, 부록 C fingerprint 대조) | IAM-Op/IW | ☐ | |
| 4.6 | 리허설 결과서 확인: ① Quorum 토큰 서명 형식 호환 ② 토큰 없이 CA 키 서명 시 `Quorum Failed` ③ 부록 A 설정으로 만든 테스트 Root·ICA 인증서와 ICA CSR이 공식 schema PASS ④ `crypto sign` 서명값 조립 후 서명 검증 PASS | CA-Admin | ☐ | |
| 4.7 | 부록 A 설정 파일·부록 B 도구 해시 대조 | IW | ☐ | |
| 4.8 | **사전 프로비저닝(IAM-Op, 세리머니 전 완료)**: Root/C2PA 클러스터 `create-cluster --mode FIPS`, `create-hsm` 각 1개, Private Subnet·보안그룹, 관리 단말에 CLI·도구 설치. 초기화(initialize)·활성화(activate)는 수행하지 않음 | IAM-Op | ☐ | |
| 4.9 | 개시 시 검증: `aws cloudhsmv2 describe-clusters --filters clusterIds=<ROOT>,<C2PA>` → 각각 **`Mode: FIPS`**, `State: UNINITIALIZED`, HSM `State: ACTIVE`. Cluster ID·HSM ID를 3.1에 기록, 출력 인쇄 첨부 | IAM-Op / IW | ☐ | |

## 5. 실행 단계

### 5.1 환경 격리 확인

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.1.1 | CO | 외부 인터넷 차단 확인 | `curl -m 5 https://example.com` | 실패(외부 차단) | ☐ | |
| 5.1.2 | CO | AWS 자격 역할 확인 | `aws sts get-caller-identity` | Ceremony 전용 역할 ARN | ☐ | |
| 5.1.3 | CO | 단말 시각 확인 | `date -u && chronyc tracking` | Amazon Time Sync 기준, UTC ±1초 | ☐ | |
| 5.1.4 | CO | 도구 바이너리·설정 해시 대조 | `sha256sum <cloudhsm-cli> <openssl> cert_tool.py verify_profile.py root.cnf ica.cnf` | 3.3 일치 | ☐ | |

### 5.2 CloudHSM 클러스터 소유 증명 인증서 생성

> AWS CloudHSM 초기화(`initialize-cluster`)에 필요한, 클러스터 CSR 서명용 고객 자체서명 인증서. C2PA 인증서 체인과 무관하며 Trust List·manifest에 포함되지 않는다. 개인키는 CA 키에 준하여 보호한다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.2.1 | CO | 소유 증명 키 생성 | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -aes256 -out hsm-owner.key` | 패스프레이즈를 KC1·KC2가 분할 입력 | ☐ | |
| 5.2.2 | CO | 소유 증명 인증서 생성 | `openssl req -new -x509 -days 3652 -key hsm-owner.key -subj "/C=KR/O=<Org>/CN=<Org> CloudHSM Cluster Owner" -out hsm-owner.crt` | PEM 생성 | ☐ | |
| 5.2.3 | CO | 소유 증명 fingerprint 기록 | `openssl x509 -in hsm-owner.crt -noout -fingerprint -sha256` | 부록 C 기록 | ☐ | |

### 5.3 클러스터 초기화 (Root → C2PA 순으로 각각 수행)

> 클러스터·HSM 생성은 4.8에서 사전 완료, 4.9에서 검증됨. 아래 행을 `<CLUSTER>`=ROOT로 먼저 수행하고 Root 열에 체크, 이어 `<CLUSTER>`=C2PA로 수행하고 C2PA 열에 체크한다. hsm-owner 인증서는 두 클러스터에 동일하게 사용.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |
|---|---|---|---|---|---|---|
| 5.3.1 | IAM-Op | 클러스터 CSR 추출 | `aws cloudhsmv2 describe-clusters --filters clusterIds=<CLUSTER> --query 'Clusters[0].Certificates.ClusterCsr' --output text > <cluster>.csr` | CSR 파일 | ☐ | ☐ |
| 5.3.2 | IW | CSR 내용 확인 | `openssl req -in <cluster>.csr -noout -subject` | Cluster ID 포함 | ☐ | ☐ |
| 5.3.3 | CO | CSR 서명 | `openssl x509 -req -days 3652 -in <cluster>.csr -CA hsm-owner.crt -CAkey hsm-owner.key -CAcreateserial -out <cluster>-signed.crt` | 성공 | ☐ | ☐ |
| 5.3.4 | IAM-Op | 클러스터 초기화 | `aws cloudhsmv2 initialize-cluster --cluster-id <CLUSTER> --signed-cert file://<cluster>-signed.crt --trust-anchor file://hsm-owner.crt` | `INITIALIZED` | ☐ | ☐ |
| 5.3.5 | CO | CLI 연결 확인 | 관리 단말에 hsm-owner.crt 배치, `cloudhsm-cli interactive --cluster-id <CLUSTER>` | 연결 성공 | ☐ | ☐ |

### 5.4 활성화 및 KMS 기반 Quorum 설정 (Root → C2PA 순으로 각각 수행)

> 공식 절차: [Quorum 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html), [CU 키 Quorum](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)
>
> 등록 토큰은 **등록 대상 사용자 본인으로 로그인**해 생성·등록한다. Custodian의 승인 능력은 HSM 비밀번호가 아니라 KMS 개인키 보유로 성립한다.
>
> **사용자를 모두 만든 뒤(5.4.3) Quorum 값을 설정한다(5.4.11).** Quorum 값을 먼저 설정하면 이후 사용자 생성마다 admin 승인이 필요하다. KMS 공개키 추출(5.4.4)은 1회만.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |
|---|---|---|---|---|---|---|
| 5.4.1 | CO | 클러스터 활성화 | `cluster activate` | 초기 admin 비밀번호 설정(KC1·KC2 분할 입력) | ☐ | ☐ |
| 5.4.2 | CO | Custodian admin 계정 생성 | `login --username admin --role admin` → `user create --username kc1 --role admin` (kc2, kc3 반복; 비밀번호는 각 KC가 직접 입력) | `user list`에 admin 4명 | ☐ | ☐ |
| 5.4.3 | CO | Crypto User 생성 | `user create --username cu_<cluster> --role crypto-user` (서명 실행용: cu_root / cu_c2pa, CO가 비밀번호 입력) 및 `cu_kc1`, `cu_kc2`, `cu_kc3` (승인용, 각 KC가 비밀번호 입력) → `logout` | CU 4명 | ☐ | ☐ |
| 5.4.4 | IAM-Op | KMS 공개키 추출 (1회) | `aws kms get-public-key --key-id alias/c2pa-quorum-kc1 --output text --query PublicKey \| base64 -d > kc1.der && openssl rsa -pubin -inform DER -in kc1.der -out kc1_pub.pem` (kc2, kc3 반복) | PEM 3개, SPKI SHA-256 부록 C 대조 | ☐ | — |
| 5.4.5 | KC1 (CO 단말, 본인 로그인) | KC1 등록 토큰 생성 | `login --username kc1 --role admin` → `quorum token-sign generate --service registration --token kc1.token` | 토큰 파일(`tokens[].unsigned` 포함) | ☐ | ☐ |
| 5.4.6 | KC1 (자기 단말, MFA) | KC1 KMS 토큰 서명 | `unsigned` 값을 받아 `echo -n '<unsigned>' \| base64 -d > kc1.bin` → `aws kms sign --key-id alias/c2pa-quorum-kc1 --message fileb://kc1.bin --message-type DIGEST --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 --output text --query Signature > kc1.sig.b64` | base64 서명. **DIGEST 모드 필수** (`unsigned`가 이미 SHA-256 값) | ☐ | ☐ |
| 5.4.7 | KC1 (CO 단말, 본인 로그인 유지) | KC1 공개키 등록 | `kc1.sig.b64` 내용을 `kc1.token`의 `tokens[].signed`에 기입 → `user change-quorum token-sign register --public-key kc1_pub.pem --signed-token kc1.token` → `logout` | `error_code: 0` | ☐ | ☐ |
| 5.4.8 | KC2, KC3 | KC2·KC3 등록 반복 | 5.4.5~5.4.7 반복 (각자 로그인·서명·등록) | 등록 성공 ×2 | ☐ | ☐ |
| 5.4.9 | KC1~KC3 | 승인용 CU 공개키 등록 | cu_kc1~cu_kc3로 각자 로그인해 5.4.5~5.4.7과 동일하게 같은 KMS 공개키 등록 | 등록 성공 ×3 | ☐ | ☐ |
| 5.4.10 | CO | 등록 상태 확인 | `user list` | kc1~kc3, cu_kc1~cu_kc3에 `quorum: [{strategy: token-sign, status: enabled}]` | ☐ | ☐ |
| 5.4.11 | CO | Quorum 값 설정 | `login --username admin --role admin`(KC1·KC2 분할 입력) → `quorum token-sign set-quorum-value --service user --value 2` → `... --service cluster --value 2` → `... --service quorum --value 2` (**quorum은 마지막**) → `quorum token-sign list-quorum-values` → `logout` | `user: 2`, `cluster: 2`, `quorum: 2` | ☐ | ☐ |
| 5.4.12 | IW | CloudTrail 서명 이벤트 확인 | CloudTrail에서 5.4.6·5.4.8·5.4.9의 `kms:Sign` 이벤트가 KC별로 서로 다른 principal로 기록됐는지 확인 | 이벤트 존재 | ☐ | ☐ |

> **CA 키 서명 방식:** 사용 Quorum이 걸린 키는 CloudHSM CLI에서만 쓸 수 있다("You can only use a CloudHSM token within the CloudHSM CLI", AWS 문서). 따라서 5.5·5.6의 서명은 OpenSSL PKCS#11이 아니라 다음 순서로 한다.
> `cert_tool.py`로 본문 생성 → KC 2명 본문 확인 → `quorum token-sign generate --service key-usage` → KC 2명 승인 → `crypto sign ecdsa --approval` → `cert_tool.py`로 조립.
> 승인자는 토큰의 `token` 값을 5.4.6과 같은 방법으로 서명하고, `signatures` 배열에 `{"username": "cu_kcN", "role": "crypto-user", "signature": "<b64>"}` 항목을 추가한다.

### 5.5 Platform Root CA 키 생성 및 자체서명 인증서

> 키 생성 다인 통제: 생성 명령에서 사용·관리 Quorum 2를 지정하고(5.5.1), IW가 5.5.2에서 직접 확인한다. C2PA 해석 확인(1장)에 따른다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.5.1 | CO(cu_root) | Root 키 생성 | `cloudhsm-cli interactive --cluster-id <ROOT>` → `login --username cu_root --role crypto-user` → `key generate-asymmetric-pair ec --curve secp384r1 --public-label platform-root-pub --private-label platform-root-priv --public-attributes verify=true token=true --private-attributes sign=true extractable=false sensitive=true token=true --share-crypto-users cu_kc1 cu_kc2 cu_kc3 --use-private-key-quorum-value 2 --manage-private-key-quorum-value 2` | 생성 | ☐ | |
| 5.5.2 | CO / IW | Root 키 속성 확인 | `key list --filter attr.label=platform-root-priv attr.class=private-key --verbose` | **extractable:false**, sign:true, secp384r1, 공유 cu_kc1~3, **사용·관리 Quorum 2** (IW 직접 확인) | ☐ | |
| 5.5.3 | CO | Root 공개키 추출 | `key generate-file --encoding pem --path platform-root-pub.pem --filter attr.label=platform-root-pub attr.class=public-key` → `openssl pkey -pubin -in platform-root-pub.pem -outform DER \| sha256sum` | 부록 C 기록 | ☐ | |
| 5.5.4 | CO / CA-Admin | Root 인증서 본문 생성 | `python3 cert_tool.py tbs --config root.cnf --extensions root_ca_ext --pubkey platform-root-pub.pem --days 7305 --out platform-root.tbs` → `python3 cert_tool.py show platform-root.tbs` → `sha256sum platform-root.tbs` | Subject·기간·확장이 부록 A와 일치. IW가 해시 기록 | ☐ | |
| 5.5.5 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 5.5.4 출력과 해시 확인 | 승인자·해시 기록 | ☐ | |
| 5.5.6 | CO | 사용 토큰 생성 | `quorum token-sign generate --service key-usage --token root-sign.token --filter attr.label=platform-root-priv attr.class=private-key` | 토큰 파일 | ☐ | |
| 5.5.7 | KC 2명 (자기 단말, MFA) | 토큰 승인 | 5.4 하단 서명 방식대로 서명 → CO가 `signatures`에 기입 | 서로 다른 KC 2명, 만료 전 | ☐ | |
| 5.5.8 | CA-Admin → CO | Root 서명 (**1회만**) | CA-Admin이 `sha256sum platform-root.tbs`로 5.5.4와 대조 후 지시 → `crypto sign ecdsa --key-filter attr.label=platform-root-priv attr.class=private-key --hash-function sha384 --data-type raw --data-path platform-root.tbs --approval root-sign.token` | `error_code: 0`, 서명값. 출력을 `root-sign.json`로 저장(CLI 대화형 모드는 리디렉션 불가, 세션 로그에서 복사) | ☐ | |
| 5.5.9 | CO | Root 인증서 조립·확인 | `python3 cert_tool.py assemble --tbs platform-root.tbs --sig root-sign.json --out platform-root.crt` → `openssl verify -check_ss_sig -CAfile platform-root.crt platform-root.crt` → `openssl x509 -in platform-root.crt -noout -text` | `OK`. `CA:TRUE, pathlen:2`(critical), KU `Certificate Sign, CRL Sign`(critical), SKI 존재, **AKI = SKI**, AIA/CRL 없음 | ☐ | |
| 5.5.10 | CO | Root fingerprint 기록, 로그아웃 | `openssl x509 -in platform-root.crt -noout -fingerprint -sha256` → `logout` | 부록 C 기록 | ☐ | |

### 5.6 C2PA ICA (First Intermediate) 키 생성 및 발급

> 키와 CSR은 **C2PA 클러스터**에서, 인증서는 **Root 클러스터**의 Platform Root 키로 발급한다. 두 클러스터 간에는 CSR과 인증서(공개 정보)만 오간다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.6.1 | CO(cu_c2pa) | ICA 키 생성 | `cloudhsm-cli interactive --cluster-id <C2PA>` → `login --username cu_c2pa --role crypto-user` → 5.5.1과 동일 (label `c2pa-ica-*`) | 생성 | ☐ | |
| 5.6.2 | CO / IW | ICA 키 속성 확인 | `key list --filter attr.label=c2pa-ica-priv attr.class=private-key --verbose` | 5.5.2와 동일 기준 (IW 직접 확인) | ☐ | |
| 5.6.3 | CO | ICA 공개키 추출 | `key generate-file --encoding pem --path c2pa-ica-pub.pem --filter attr.label=c2pa-ica-pub attr.class=public-key` → `openssl pkey -pubin -in c2pa-ica-pub.pem -outform DER \| sha256sum` | Root와 다름. 부록 C 기록 | ☐ | |
| 5.6.4 | CO / CA-Admin | ICA CSR 본문 생성 | `python3 cert_tool.py cri --subj "/C=KR/O=<Org>/CN=Samsung C2PA Intermediate CA G1" --config ica.cnf --reqexts ica_req_ext --pubkey c2pa-ica-pub.pem --out c2pa-ica.cri` → `show` → `sha256sum` | Subject·공개키·요청 확장(BC·KU·CP) 확인. IW가 해시 기록 | ☐ | |
| 5.6.5 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 5.6.4 출력과 해시 확인 | 승인자·해시 기록 | ☐ | |
| 5.6.6 | CO | 사용 토큰 생성 | `quorum token-sign generate --service key-usage --token ica-csr.token --filter attr.label=c2pa-ica-priv attr.class=private-key` | 토큰 파일 | ☐ | |
| 5.6.7 | KC 2명 | 토큰 승인 | 5.5.7과 동일 | 서로 다른 KC 2명 | ☐ | |
| 5.6.8 | CA-Admin → CO | CSR 서명 (**1회만**) | 해시 대조 후 지시 → `crypto sign ecdsa --key-filter attr.label=c2pa-ica-priv attr.class=private-key --hash-function sha384 --data-type raw --data-path c2pa-ica.cri --approval ica-csr.token` | `error_code: 0`. 출력을 `ica-csr-sign.json`로 저장 | ☐ | |
| 5.6.9 | CO / IW | CSR 조립·확인, 로그아웃 | `python3 cert_tool.py assemble --cri c2pa-ica.cri --sig ica-csr-sign.json --out c2pa-ica.csr` → `openssl req -in c2pa-ica.csr -verify -noout -text` → `python3 verify_profile.py c2pa-ica.csr first_ica_csr` → `sha256sum c2pa-ica.csr` → `logout` | `verify OK`, CSR schema PASS. IW가 CSR SHA-256 기록 | ☐ | |
| 5.6.10 | CO / CA-Admin | ICA 인증서 본문 생성 (Root 클러스터) | `cloudhsm-cli interactive --cluster-id <ROOT>` → `login --username cu_root --role crypto-user` → `sha256sum c2pa-ica.csr`(5.6.9와 대조) → `python3 cert_tool.py tbs --config ica.cnf --extensions first_ica_ext --csr c2pa-ica.csr --issuer platform-root.crt --days 1826 --out c2pa-ica.tbs` → `show` → `sha256sum` | Issuer=Root Subject, AKI=Root SKI, 공개키=CSR, AIA(OCSP·caIssuers), **CDP 없음**. IW가 해시 기록 | ☐ | |
| 5.6.11 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 5.6.10 출력과 해시 확인 | 승인자·해시 기록 | ☐ | |
| 5.6.12 | CO | Root 사용 토큰 생성 | `quorum token-sign generate --service key-usage --token ica-issue.token --filter attr.label=platform-root-priv attr.class=private-key` | 토큰 파일 | ☐ | |
| 5.6.13 | KC 2명 | 토큰 승인 | 5.5.7과 동일 | 서로 다른 KC 2명 | ☐ | |
| 5.6.14 | CA-Admin → CO | Root로 ICA 발급 (**1회만**) | 해시 대조 후 지시 → `crypto sign ecdsa --key-filter attr.label=platform-root-priv attr.class=private-key --hash-function sha384 --data-type raw --data-path c2pa-ica.tbs --approval ica-issue.token` | `error_code: 0`. 출력을 `ica-issue-sign.json`로 저장 | ☐ | |
| 5.6.15 | CO | ICA 조립·체인 검증, 로그아웃 | `python3 cert_tool.py assemble --tbs c2pa-ica.tbs --sig ica-issue-sign.json --out c2pa-ica.crt` → `openssl verify -CAfile platform-root.crt c2pa-ica.crt` → `logout` | OK | ☐ | |
| 5.6.16 | CO | ICA 공개키 대조 | `openssl x509 -in c2pa-ica.crt -pubkey -noout` vs `c2pa-ica-pub.pem` | 일치 | ☐ | |
| 5.6.17 | CO | ICA fingerprint 기록 | `openssl x509 -in c2pa-ica.crt -noout -fingerprint -sha256` | 부록 C 기록 | ☐ | |

### 5.7 프로파일 자동 검증

| 단계 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|
| 5.7.1 | Root 프로파일 검증 | `python3 verify_profile.py platform-root.crt root` | ALL CHECKS PASSED | ☐ | |
| 5.7.2 | ICA 프로파일 검증 | `python3 verify_profile.py c2pa-ica.crt first_ica` | ALL CHECKS PASSED | ☐ | |
| 5.7.3 | 체인 검증 | `openssl verify -CAfile platform-root.crt c2pa-ica.crt` | OK | ☐ | |
| 5.7.4 | 검증 결과 서명 | IW 출력 인쇄본 서명 | 서명 | ☐ | |

> **FAIL 시:** 중단하고 8장에 기록한다. 해당 인증서는 배포하지 않는다. **같은 키로 인증서를 다시 발급하지 않는다.** 별도 승인을 받아 키를 삭제하고 새 키로 다시 생성한다 (CP *Certificate Renewal*·*Certificate Modification*). 5.5.8·5.6.8·5.6.14의 `crypto sign`은 결과가 불명확해도 재실행하지 않으며, 서명 응답이 저장돼 있으면 조립만 다시 한다.

### 5.8 백업 확인 및 두 클러스터 오프라인화

> 5.8.1의 조건을 만족하지 않으면 HSM을 삭제하지 않는다(5.8.4 이후 보류, 8장 기록).

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.8.1 | IAM-Op / IW | 백업 상태·시점 확인 | `aws cloudhsmv2 describe-backups --filters clusterIds=<ROOT>` / `<C2PA>` | 각 최신 백업 `READY`이고 `CreateTimestamp`가 5.6.17 이후 | ☐ | |
| 5.8.2 | IAM-Op | 백업 만료 방지 | `aws cloudhsmv2 modify-backup-attributes --backup-id <ID> --never-expires` (두 백업) | `NeverExpires: true` | ☐ | |
| 5.8.3 | IAM-Op | off-site 사본 | `aws cloudhsmv2 copy-backup-to-region --destination-region <DR_REGION> --backup-id <ID>` (두 백업) → 대상 리전 `READY` 확인, 사본에 5.8.2 적용 | 사본 2개 `READY` | ☐ | |
| 5.8.4 | IAM-Op | Root 클러스터 HSM 삭제 | `aws cloudhsmv2 delete-hsm --cluster-id <ROOT> --hsm-id <HSM>` | 삭제, 클러스터·백업 유지 | ☐ | |
| 5.8.5 | IAM-Op | C2PA 클러스터 HSM 삭제 | `aws cloudhsmv2 delete-hsm --cluster-id <C2PA> --hsm-id <HSM>` | 삭제, 클러스터·백업 유지 | ☐ | |
| 5.8.6 | IAM-Op | 0-HSM 상태 확인 | describe (둘 다) | `Hsms: []` | ☐ | |

### 5.9 로그 보존 확인 및 정리

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.9.1 | IAM-Op | CloudHSM 감사 로그 확인 | CloudWatch Logs `/aws/cloudhsm/<id>` 이벤트 확인 | 존재 | ☐ | |
| 5.9.2 | IAM-Op | CloudTrail 이벤트 확인 | CloudTrail: CreateCluster, InitializeCluster, kms:Sign×N, CopyBackupToRegion, DeleteHsm | 존재 | ☐ | |
| 5.9.3 | IW | 서명 승인 이벤트 확인 | CloudTrail에서 5.5.7·5.6.7·5.6.13의 `kms:Sign` | 서명마다 서로 다른 KC principal 2개 | ☐ | |
| 5.9.4 | CO | 소유 증명 키 이관·삭제 | hsm-owner.key를 KMS(Import) 또는 봉인 매체로 이관 후 `shred -u hsm-owner.key` | 삭제 | ☐ | |
| 5.9.5 | CO | 세션 녹화 종료·해시 | 세션 녹화 종료, `sha256sum ceremony_<YYYYMMDD>.log` | 부록 C | ☐ | |
| 5.9.6 | CA-Admin | 룸 녹화 종료·해시 | 룸 녹화 종료(`__:__`), 파일 해시 | 부록 C | ☐ | |

## 6. 사후 보관 및 접근 통제

| 자산 | 통제 |
|---|---|
| Custodian KMS 키 | 키정책: 해당 Custodian만 kms:Sign(MFA), 관리자 Deny, 삭제 7일+ 대기, CloudTrail 알림 |
| admin·CU 비밀번호 | 분할본·봉인 사본은 KC별·CO 봉인 보관, 금고, 출입 명부 |
| 클러스터 소유 증명 키 | KMS 또는 봉인 매체, 이중 통제 |
| CloudHSM 백업(원본·`<DR_REGION>` 사본) | `NeverExpires`. RestoreBackup/CopyBackupToRegion/DeleteBackup/CreateHsm/DeleteCluster에 승인 절차, SCP로 원본·DR 리전 외 금지 |
| 로그·녹화·Script | 해시 기록, S3 Object Lock |
| 인증서 PEM | 공개, 저장소 |

## 7. 참가자 서명

서명 문구: "본인은 본 Ceremony가 승인된 Script v`<x>`에 따라 수행되었음을 보증하며, 편차는 8장에 모두 기록되었습니다."

| 역할 | 성명 | 서명 | 일시 |
|---|---|---|---|
| Ceremony Administrator | | | |
| Crypto Officer | | | |
| AWS IAM Operator | | | |
| Key Custodian #1 / #2 / #3 | | | |
| Independent Witness | | | |

## 8. 편차 기록

> 단계 열에는 실행 단계 번호(5.x.y)만 기재. 사소한 재입력·재시도도 모두 기록.

| # | 시각 | 단계(5.x.y) | 상황 | 조치 | IW |
|---|---|---|---|---|---|
| | | | | | |

---

## 부록 A. 설정

`cert_tool.py`가 아래 OpenSSL 형식 설정을 읽어 본문을 만든다. 유효기간: Root 7305일(20년), ICA 1826일(5년).

### root.cnf

```ini
[ req ]
distinguished_name = dn
prompt = no

[ dn ]
C = KR
O = <Org>
CN = Samsung Cloud Service Platform Root CA G1

[ root_ca_ext ]
basicConstraints = critical, CA:TRUE, pathlen:2
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
```

### ica.cnf

```ini
[ ica_req_ext ]   # CSR 요청 확장 (First CSR schema 필수)
basicConstraints = critical, CA:TRUE, pathlen:1
keyUsage = critical, keyCertSign, cRLSign
certificatePolicies = 1.3.6.1.4.1.62558.1.1

[ first_ica_ext ] # 인증서 확장. CDP는 넣지 않는다 (First schema allOf/5 oneOf)
basicConstraints = critical, CA:TRUE, pathlen:1
keyUsage = critical, keyCertSign, cRLSign
certificatePolicies = 1.3.6.1.4.1.62558.1.1
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
authorityInfoAccess = OCSP;URI:http://<ocsp>/, caIssuers;URI:http://<pki>/platform-root.crt
```

## 부록 B. 도구

| 도구 | 기능 |
|---|---|
| `cert_tool.py tbs` | 설정·공개키(·CSR·Issuer 인증서)로 TBSCertificate DER 생성. serial은 CSPRNG 159-bit 양수 |
| `cert_tool.py cri` | CertificationRequestInfo DER 생성 (`extensionRequest` 포함) |
| `cert_tool.py show` | 본문의 모든 필드·확장·critical 출력 |
| `cert_tool.py assemble` | 본문 + `crypto sign` 서명값 → 인증서/CSR. 서명값을 DER ECDSA-Sig-Value로 변환, 조립 후 서명 자체 검증 |
| `verify_profile.py <파일> <root\|first_ica\|first_ica_csr>` | 공식 schema(commit `2466172`의 `rootCA.cert.schema.json`, `intermediateCA.cert.schema.json`, `intermediateCA.csr.schema.json`) 검사 + SKI Method 1·AKI 대응 검사 |

실행 전 SHA-256을 3.3과 대조한다.

## 부록 C. Fingerprint 기록표 (SHA-256, 대문자, 구분자 없음)

| 대상 | SHA-256 | 기록자 | IW |
|---|---|---|---|
| hsm-owner.crt | | | |
| KC1 / KC2 / KC3 공개키 (SPKI SHA-256) | | | |
| Platform Root 공개키 / 인증서 | | | |
| C2PA ICA 공개키 / CSR / 인증서 | | | |
| 터미널 세션 로그 / 룸 녹화 / cert_tool.py / verify_profile.py | | | |

## 부록 D. 개정 내역 (v0.1 → v0.2)

근거: [C2PA 심사](c2pa-review-2026-10-13.md), [AWS CU 키 Quorum](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

| # | 변경 | 위치 | 근거 |
|---|---|---|---|
| 1 | CA 키 서명을 OpenSSL PKCS#11에서 `crypto sign --approval` + `cert_tool.py` 조립으로 변경. 서명마다 본문 확인·토큰·KC 2명 승인 단계 추가 | 5.4 하단, 5.5.4–5.5.9, 5.6.4–5.6.15, 부록 B | K4. Quorum 토큰은 CloudHSM CLI에서만 사용 가능 |
| 2 | 키 생성 명령에 사용·관리 Quorum 2와 공유 사용자 지정. IW 직접 확인. C2PA 해석 확인 항목 추가 | 1장, 5.5.1–5.5.2, 5.6.1–5.6.2 | K4, C2PA 답변 |
| 3 | 승인용 CU를 3명(cu_kc1~3)으로. Quorum을 두 클러스터 모두 2-of-3으로 통일 | 2장, 3.1, 5.4.3, 5.4.9 | M3. KC 1명 상실 시에도 키 사용 가능 |
| 4 | 사용자 생성 후 Quorum 설정으로 순서 변경. `cluster`·`quorum` 서비스 필수, `quorum`은 마지막 | 5.4.3, 5.4.11 | M3 |
| 5 | 등록 토큰 서비스명 `user` → `registration` | 5.4.5 | AWS 문서 |
| 6 | Root AKI `keyid` → `keyid:always` | 부록 A, 5.5.9 | K2 (OpenSSL 3 자체서명 시 AKI 누락) |
| 7 | ICA CDP 삭제 | 부록 A, 5.6.10 | K1 (First schema oneOf) |
| 8 | ICA CSR에 요청 확장 추가 | 부록 A `ica_req_ext`, 5.6.4, 5.6.9 | M1 |
| 9 | 유효기간 Root 9131 → 7305일, ICA 범위값 → 1826일 | 부록 A, 5.5.4, 5.6.10 | M2 (승인된 20년/5년) |
| 10 | FAIL 시 "인증서만 재발급" → 같은 키 재발급 금지, 새 키로 재생성. 서명 재실행 금지 | 5.7 하단 | K3 |
| 11 | 오프라인화 전 백업 시점 확인, 만료 방지, off-site 사본. "[권장]" 표기 삭제 | 5.8, 3.1, 6장 | M4 |
| 12 | 미확정 문구("[템플릿 전용]", "[리허설 확인]") 삭제, 리허설 확인 항목을 4.6으로 이동 | 4.6, 5.4 | K5 |
| 13 | 문서 손상 복구(표, 코드 블록, 자동 링크), CP 인용을 조항 제목으로 | 전체 | K5, m1 |

이번 개정에서 반영하지 않은 항목(심사 Major/Minor 중 필수 요건이 아닌 것): IW 독립성 기준(M5), 신뢰 역할 적격성 확인(M6), 활성화 자재 목록(M7), CMVP 해석(M8), 단말·MFA 정의(M9), 서명 문구의 준수 여부 표시(m7) 등.

[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md

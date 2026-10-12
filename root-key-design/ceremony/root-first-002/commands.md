# root-first-002 실행 명령

초안 · [스크립트](script.md)의 실행 부록 · 리허설·승인 전

실행자가 행사 당일 위에서부터 순서대로 따라 입력하는 명령이다. 각 단계는 **누가**, **입력**, **확인**, **저장** 순서로 적었다. 확인 항목이 하나라도 맞지 않으면 다음으로 넘어가지 않고 진행자에게 알린다.

실행자는 EC2에 터미널 두 개를 열어 둔다.

- **터미널 1 (CLI):** `aws-cloudhsm >`로 시작하는 줄을 입력한다. HSM 명령 전용이다.
- **터미널 2 (셸):** `$`로 시작하는 줄을 입력한다. 파일 생성·확인·검사용이다.
- `{{…}}`는 행사 전에 실제 값으로 바꿔 둔다. 당일에는 고친 명령을 그대로 입력한다.
- `{{현장_…}}`는 해당 단계에서 확인한 ID·시각을 넣는다.

## 행사 전에 채울 값

| 값 | 내용 |
|---|---|
| `{{CLUSTER_ID}}` | CloudHSM 클러스터 ID |
| `{{ROOT_LABEL}}` / `{{FIRST_LABEL}}` | Root·First 키 라벨 |
| `{{CO_CU}}` | 실행자(Crypto Officer)의 CU 계정 |
| `{{KC2_CU}}` / `{{KC3_CU}}` | Custodian 2·3의 CU 계정 |
| `{{DIR}}` | 회차 폴더 절대경로 |
| `{{tool}}` | 본문 생성·조립·비교 도구 |
| `{{verifier}}` | C2PA 프로파일·schema 검사 도구 |

이 파일을 승인할 때 도구 버전과 SHA-256을 스크립트 「승인 자료 목록」에 적는다.

## 시작하기 전에

- 비밀번호는 프롬프트가 나올 때만 입력한다. 명령이나 파일에 적지 않는다.
- 두 터미널의 입력과 출력은 `session-cli.log`, `session-shell.log`에 자동으로 남는다. **저장**에 적힌 파일은 출력 부분을 복사해 `evidence/`에 따로 저장한다.
- 키를 지정할 때는 항상 라벨과 `attr.class`를 함께 쓴다. 조회 결과가 1건이 아니면 멈춘다.
- 명령이 실패하거나 결과를 알 수 없으면 **다시 실행하지 않는다.** 진행자에게 알리고 스크립트 「중단과 재개」를 따른다.

---

## A1 시작 확인

### 1. 로그 기록을 시작한다

**누가:** 실행자

터미널 1과 터미널 2에서 각각 입력한다.

```
터미널 1:
$ cd {{DIR}} && mkdir -p evidence
$ script -f evidence/session-cli.log

터미널 2:
$ cd {{DIR}}
$ script -f evidence/session-shell.log
```

**확인:** 두 로그 파일이 생겼다. 이후 작업은 모두 이 두 터미널 안에서 한다.

진행자는 증거 목록에 두 로그의 ID·경로를 등록한다. 해시 칸에는 `기록 중`을 적고 A4에서 로그를 닫은 뒤 최종 해시로 바꾼다.

### 2. 버전과 시각을 확인한다

```
$ date -u
$ /opt/cloudhsm/bin/cloudhsm-cli --version
$ openssl version
$ {{tool}} --version
$ {{verifier}} --version
$ sha256sum $(which {{tool}}) $(which {{verifier}})
```

**확인:** 버전과 해시가 승인 자료 목록과 같다.

### 3. 클러스터 상태를 확인한다

```
$ aws cloudhsmv2 describe-clusters --filters clusterIds={{CLUSTER_ID}}
```

**확인:** 클러스터가 `ACTIVE`다. HSM 수와 모델(`hsm2m.medium`), 상태가 승인한 구성과 같다.
**저장:** 출력 → `evidence/A1-cluster.json`

### 4. CLI에 로그인해 사용자와 키를 확인한다

```
$ /opt/cloudhsm/bin/cloudhsm-cli interactive
aws-cloudhsm > login --username {{CO_CU}} --role crypto-user
aws-cloudhsm > user list
aws-cloudhsm > quorum token-sign list-quorum-values
aws-cloudhsm > key list --filter attr.label={{ROOT_LABEL}}
aws-cloudhsm > key list --filter attr.label={{FIRST_LABEL}}
```

**확인:**
- `user list`의 사용자와 승인키 등록 상태가 참여자 명단과 같다.
- 관리자 quorum 값이 승인한 설정과 같다.
- 두 라벨 모두 키가 0건이다. 이미 같은 이름의 키가 있으면 멈춘다.

**저장:** `user list` 출력 → `evidence/A1-users.json`, quorum 값 → `evidence/A1-quorum.json`

CLI는 A4까지 로그인한 상태로 둔다.

---

## A2 Root 생성·발급

### A2.1 Root 생성 승인

**누가:** 승인자 2명 이상, 접근 담당자

1. 승인자들이 승인 앱에서 Root 생성 계획(아래 「키 생성 명령」 포함)을 확인하고 서명한다.
2. 진행자가 앱의 서명 검증 결과를 확인한다.
3. 접근 담당자가 생성 접근을 연다.

```
{{생성_접근_활성화_명령}}
```

**저장:** 계획 → `evidence/A2.1-plan.json`, 승인 서명 → `evidence/A2.1-plan-approvals`, 접근 활성화 결과 → `evidence/A2.1-access-open.txt`

### A2.2 Root 키 생성

**누가:** 실행자

**1) 키를 만든다.** 아래 명령은 한 줄로 입력한다.

```
aws-cloudhsm > key generate-asymmetric-pair ec --curve secp384r1 --public-label {{ROOT_LABEL}} --private-label {{ROOT_LABEL}} --public-attributes verify=true token=true --private-attributes sign=true decrypt=false derive=false unwrap=false extractable=false sensitive=true token=true {{잠금_속성}} --share-crypto-users {{KC2_CU}} {{KC3_CU}} --use-private-key-quorum-value 2 {{관리_quorum_인자}}
```

**확인:** 성공 응답과 공개키·개인키의 key-reference가 나왔다.
**저장:** 출력 → `evidence/A2.2-generate.json`

**2) 만든 키를 조회한다.**

```
aws-cloudhsm > key list --filter attr.label={{ROOT_LABEL}} attr.class=private-key --verbose
```

**확인:**
- 1건이다.
- 곡선 `secp384r1`, `sign=true`, `extractable=false`, `sensitive=true`, `token=true`
- 공유 사용자에 `{{KC2_CU}}`, `{{KC3_CU}}`가 있다.
- 사용 quorum이 `2`다.

**저장:** 출력 → `evidence/A2.2-key.json`

**3) 공개키를 꺼내고 지문을 계산한다.**

```
aws-cloudhsm > key generate-file --encoding pem --path {{DIR}}/evidence/A2.2-root-pub.pem --filter attr.label={{ROOT_LABEL}} attr.class=public-key
```

```
$ openssl pkey -pubin -in evidence/A2.2-root-pub.pem -text -noout
$ openssl pkey -pubin -in evidence/A2.2-root-pub.pem -outform DER | sha256sum
```

**확인:** `NIST CURVE: P-384`. 마지막 값이 Root 공개키 지문이다.
**저장:** `evidence/A2.2-root-pub.pem`이 생성됐다. 지문은 수행 기록에 적는다.

**4) 생성 접근을 닫는다.**

**누가:** 접근 담당자

```
{{생성_접근_회수_명령}}
{{회수_확인_명령}}
```

**확인:** 생성 접근이 닫혔고, 다시 생성하려 하면 거부된다.
**저장:** 결과 → `evidence/A2.2-access-close.txt`

### A2.3 Root 인증서 서명

**1) serial을 예약하고 서명할 본문을 만든다.**

**누가:** 실행자

```
$ {{tool}} serial reserve --ledger {{원장}}
$ {{tool}} tbs root --config root.conf --pubkey evidence/A2.2-root-pub.pem --serial {{현장_serial}} --out evidence/A2.3-root-tbs.der
$ {{tool}} show evidence/A2.3-root-tbs.der > evidence/A2.3-root-tbs.txt
$ sha256sum evidence/A2.3-root-tbs.der
```

**확인 (진행자):** 원장에 같은 serial이 없다. `A2.3-root-tbs.txt`의 Subject·기간·확장이 스크립트 Appendix B와 같다.

**2) 승인자가 본문을 승인한다.**

**누가:** 승인자 2명 이상

`A2.3-root-tbs.txt`와 위 SHA-256을 확인하고 본문 승인 기록에 서명한다.
**저장:** `evidence/A2.3-body-approval`

**3) Root 키의 사용 토큰을 만든다.**

**누가:** 실행자

```
aws-cloudhsm > key list --filter attr.label={{ROOT_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > quorum token-sign generate --service key-usage --token {{DIR}}/A2.3-token.json --filter attr.label={{ROOT_LABEL}} attr.class=private-key
```

**확인:** 키 조회 결과가 A2.2와 같다. 토큰 파일이 생겼다.

작업용 토큰은 회차 폴더에 두고 실행자와 승인자만 접근한다. 서명에 실제 사용한 `*-token-signed.json`은 HSM 작업 성공 후 `evidence/`에 원문 그대로 복사해 승인 증거로 보관한다. 실패·결과 불명으로 중단한 경우에도 원문을 보존하고, 세션 종료를 확인하기 전에는 작업용 파일을 삭제하지 않는다.

**4) 승인자가 토큰에 서명한다.**

**누가:** 승인자 2명 이상 → 실행자

「토큰 승인 방법」에 따라 각자 서명하고, 실행자가 `A2.3-token-signed.json`으로 모은다.

**확인 (진행자):** 서로 다른 Custodian 2명 이상이 서명했다. 토큰이 만료되지 않았다.

**5) HSM으로 서명한다.**

**누가:** 진행자 → 실행자

진행자가 본문 SHA-256을 다시 계산해 1)과 같은지 확인하고 실행을 지시한다.

```
$ sha256sum evidence/A2.3-root-tbs.der
aws-cloudhsm > crypto sign ecdsa --key-filter attr.label={{ROOT_LABEL}} attr.class=private-key --hash-function sha384 --data-type raw --data-path {{DIR}}/evidence/A2.3-root-tbs.der --approval {{DIR}}/A2.3-token-signed.json
```

**확인:** 성공 응답과 서명값이 나왔다.
**저장:** 출력 → `evidence/A2.3-sign-response.json`. **저장을 확인하기 전에는 다음으로 넘어가지 않는다.**

```
$ cp A2.3-token-signed.json evidence/A2.3-token-signed.json
$ cmp A2.3-token-signed.json evidence/A2.3-token-signed.json
```

**확인:** `cmp`가 차이 없이 성공했다. 진행자는 보관본을 열어 실제 승인자를 확인하고 증거 목록에 등록한다. A3.3·A3.5에서도 같은 방식으로 확인한다.

**6) 인증서를 완성한다.**

```
$ {{tool}} assemble --tbs evidence/A2.3-root-tbs.der --sig evidence/A2.3-sign-response.json --out evidence/A2.3-root.der
```

**확인:** `evidence/A2.3-root.der`가 생겼다.

조립이 실패하면 이 명령만 다시 한다. 5)의 HSM 서명은 반복하지 않는다.

### A2.4 Root 인증서 검사

**누가:** 진행자

```
$ openssl x509 -in evidence/A2.3-root.der -inform DER -out evidence/A2.3-root.pem
$ openssl verify -check_ss_sig -CAfile evidence/A2.3-root.pem evidence/A2.3-root.pem
$ openssl x509 -in evidence/A2.3-root.pem -noout -text
$ {{tool}} compare --tbs evidence/A2.3-root-tbs.der --cert evidence/A2.3-root.der --pubkey evidence/A2.2-root-pub.pem
$ {{verifier}} root evidence/A2.3-root.der
$ {{tool}} ledger record --cert evidence/A2.3-root.der
```

**확인:**
- `openssl verify`가 `OK`다.
- `compare`: 승인한 본문과 같고, 공개키가 HSM 공개키와 같다.
- `verifier`: Root 프로파일과 schema 검사를 모두 통과한다.
- 원장에 기록됐다.

**저장:** 검사 출력 → `evidence/A2.4-verify.txt`

---

## A3 First 생성·CSR·발급

### A3.1 First 생성 승인

A2.1과 같다. **First 생성 계획**으로 승인받는다.

**저장:** `evidence/A3.1-plan.json`, `evidence/A3.1-plan-approvals`, `evidence/A3.1-access-open.txt`

### A3.2 First 키 생성

A2.2의 1)–4)를 `{{ROOT_LABEL}}` 대신 `{{FIRST_LABEL}}`로 실행한다. 공개키 파일은 `evidence/A3.2-first-pub.pem`으로 저장한다.

```
aws-cloudhsm > key generate-asymmetric-pair ec --curve secp384r1 --public-label {{FIRST_LABEL}} --private-label {{FIRST_LABEL}} --public-attributes verify=true token=true --private-attributes sign=true decrypt=false derive=false unwrap=false extractable=false sensitive=true token=true {{잠금_속성}} --share-crypto-users {{KC2_CU}} {{KC3_CU}} --use-private-key-quorum-value 2 {{관리_quorum_인자}}
aws-cloudhsm > key list --filter attr.label={{FIRST_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > key generate-file --encoding pem --path {{DIR}}/evidence/A3.2-first-pub.pem --filter attr.label={{FIRST_LABEL}} attr.class=public-key
$ openssl pkey -pubin -in evidence/A3.2-first-pub.pem -outform DER | sha256sum
```

**추가 확인:** First 공개키 지문이 Root 지문과 다르다.
**저장:** `evidence/A3.2-generate.json`, `evidence/A3.2-key.json`, `evidence/A3.2-first-pub.pem`, `evidence/A3.2-access-close.txt`

### A3.3 First CSR 서명

**1) CSR 본문을 만든다.**

```
$ {{tool}} cri first --config first.conf --pubkey evidence/A3.2-first-pub.pem --out evidence/A3.3-first-cri.der
$ {{tool}} show evidence/A3.3-first-cri.der > evidence/A3.3-first-cri.txt
$ sha256sum evidence/A3.3-first-cri.der
```

**확인 (진행자):** Subject·공개키·요청 확장이 Appendix B와 같다.

**2) 승인자가 CSR 본문을 승인한다.**

승인자 2명 이상이 `evidence/A3.3-first-cri.txt`와 위 DER 본문의 SHA-256을 확인하고 서명한다.
**저장:** `evidence/A3.3-body-approval`

**3) 실행자가 First 키의 새 토큰을 만든다.**

```
aws-cloudhsm > key list --filter attr.label={{FIRST_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > quorum token-sign generate --service key-usage --token {{DIR}}/A3.3-token.json --filter attr.label={{FIRST_LABEL}} attr.class=private-key
```

**확인:** 키 조회 결과가 A3.2와 같다.

**4) 승인자가 토큰에 서명한다.**

승인자 2명 이상이 「토큰 승인 방법」에 따라 `A3.3-token.json`에 서명한다. 실행자는 결과를 `A3.3-token-signed.json`으로 모은다. 진행자는 서로 다른 승인자 2명 이상과 토큰의 세션·유효 기한을 확인한다.

**5) HSM으로 서명한다.**

진행자가 본문 SHA-256을 다시 계산해 1)의 승인 대상과 같은지 확인하고 실행을 지시한다.

```
$ sha256sum evidence/A3.3-first-cri.der
aws-cloudhsm > crypto sign ecdsa --key-filter attr.label={{FIRST_LABEL}} attr.class=private-key --hash-function sha384 --data-type raw --data-path {{DIR}}/evidence/A3.3-first-cri.der --approval {{DIR}}/A3.3-token-signed.json
```

**확인:** 성공 응답과 서명값이 나왔다.
**저장:** 출력 → `evidence/A3.3-sign-response.json`. 다음 명령으로 사용한 토큰도 보관한다. 응답·토큰 저장을 확인하기 전에는 다음으로 넘어가지 않는다.

```
$ cp A3.3-token-signed.json evidence/A3.3-token-signed.json
$ cmp A3.3-token-signed.json evidence/A3.3-token-signed.json
```

**6) CSR을 완성한다.**

```
$ {{tool}} assemble --tbs evidence/A3.3-first-cri.der --sig evidence/A3.3-sign-response.json --out evidence/A3.3-first.csr.der
```

**저장:** `evidence/A3.3-body-approval`, `evidence/A3.3-sign-response.json`, `evidence/A3.3-first.csr.der`

### A3.4 CSR 검사와 발급 허가

**누가:** 진행자, 발급 허가자

```
$ openssl req -in evidence/A3.3-first.csr.der -inform DER -verify -noout -text
$ {{tool}} compare --tbs evidence/A3.3-first-cri.der --csr evidence/A3.3-first.csr.der --pubkey evidence/A3.2-first-pub.pem
$ {{verifier}} csr evidence/A3.3-first.csr.der
```

**확인:**
- `verify OK`
- 승인한 본문·공개키와 같다.
- CSR schema를 통과한다.
- 요청자 신원과 발급 권한을 확인하고 발급 허가자가 허가했다.

**저장:** 검사 출력 → `evidence/A3.4-verify.txt`, 허가 기록 → `evidence/A3.4-authorization`

### A3.5 First 인증서 서명

**1) serial을 예약하고 본문을 만든다.**

```
$ {{tool}} serial reserve --ledger {{원장}}
$ {{tool}} tbs first --config first.conf --csr evidence/A3.3-first.csr.der --issuer evidence/A2.3-root.der --serial {{현장_serial}} --out evidence/A3.5-first-tbs.der
$ {{tool}} show evidence/A3.5-first-tbs.der > evidence/A3.5-first-tbs.txt
$ sha256sum evidence/A3.5-first-tbs.der
$ {{OCSP_확인_명령}}
```

**확인 (진행자):**
- serial 중복이 없다.
- 공개키가 CSR과 같다.
- Issuer가 Root Subject와 같고, AKI가 Root SKI와 같다.
- AIA의 OCSP 주소가 응답한다.

**저장:** OCSP 확인 결과 → `evidence/A3.5-ocsp-ready.txt`

**2) 승인자가 인증서 본문을 승인한다.**

승인자 2명 이상이 `evidence/A3.5-first-tbs.txt`와 위 DER 본문의 SHA-256을 확인하고 서명한다. CSR에서 쓴 승인은 다시 쓰지 않는다.
**저장:** `evidence/A3.5-body-approval`

**3) 실행자가 Root 키의 새 토큰을 만든다.**

```
aws-cloudhsm > key list --filter attr.label={{ROOT_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > quorum token-sign generate --service key-usage --token {{DIR}}/A3.5-token.json --filter attr.label={{ROOT_LABEL}} attr.class=private-key
```

**확인:** 키 조회 결과가 A2.2와 같다.

**4) 승인자가 토큰에 서명한다.**

승인자 2명 이상이 「토큰 승인 방법」에 따라 `A3.5-token.json`에 서명한다. 실행자는 결과를 `A3.5-token-signed.json`으로 모은다. 진행자는 서로 다른 승인자 2명 이상과 토큰의 세션·유효 기한을 확인한다.

**5) HSM으로 서명한다.**

진행자가 본문 SHA-256을 다시 계산해 1)의 승인 대상과 같은지 확인하고 실행을 지시한다.

```
$ sha256sum evidence/A3.5-first-tbs.der
aws-cloudhsm > crypto sign ecdsa --key-filter attr.label={{ROOT_LABEL}} attr.class=private-key --hash-function sha384 --data-type raw --data-path {{DIR}}/evidence/A3.5-first-tbs.der --approval {{DIR}}/A3.5-token-signed.json
```

**확인:** 성공 응답과 서명값이 나왔다.
**저장:** 출력 → `evidence/A3.5-sign-response.json`. 다음 명령으로 사용한 토큰도 보관한다. 응답·토큰 저장을 확인하기 전에는 다음으로 넘어가지 않는다.

```
$ cp A3.5-token-signed.json evidence/A3.5-token-signed.json
$ cmp A3.5-token-signed.json evidence/A3.5-token-signed.json
```

**6) 인증서를 완성한다.**

```
$ {{tool}} assemble --tbs evidence/A3.5-first-tbs.der --sig evidence/A3.5-sign-response.json --out evidence/A3.5-first.der
```

**저장:** `evidence/A3.5-body-approval`, `evidence/A3.5-sign-response.json`, `evidence/A3.5-first.der`

### A3.6 First 인증서 검사

**누가:** 진행자

```
$ openssl x509 -in evidence/A3.5-first.der -inform DER -out evidence/A3.5-first.pem
$ openssl verify -CAfile evidence/A2.3-root.pem evidence/A3.5-first.pem
$ openssl x509 -in evidence/A3.5-first.pem -noout -text
$ {{tool}} compare --tbs evidence/A3.5-first-tbs.der --cert evidence/A3.5-first.der --csr evidence/A3.3-first.csr.der
$ {{verifier}} intermediate evidence/A3.5-first.der
$ {{tool}} ledger record --cert evidence/A3.5-first.der
```

**확인:**
- `openssl verify`가 `OK`다.
- 승인한 본문과 같고, 공개키가 CSR과 같다.
- First 프로파일과 schema를 통과한다.
- 원장에 기록됐다.

**저장:** 검사 출력 → `evidence/A3.6-verify.txt`

---

## A4 종료

**1) 상태 서비스와 최종 키·권한을 확인한다.**

**누가:** 진행자, 실행자

```
$ {{OCSP_조회_명령}}
aws-cloudhsm > key list --filter attr.label={{ROOT_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > key list --filter attr.label={{FIRST_LABEL}} attr.class=private-key --verbose
aws-cloudhsm > user list
```

**확인:**
- First serial의 OCSP 응답이 `good`이다.
- Root·First 키 ID, 보호 속성·소유자·공유 사용자·quorum과 사용자 구성이 최종 승인값과 같다. 진행자가 마지막 키·권한 변경 시각을 적는다.

**저장:** `evidence/A4-ocsp.txt`, `evidence/A4-root-key.json`, `evidence/A4-first-key.json`, `evidence/A4-users.json`

**2) 세션을 끝낸다.**

**누가:** 실행자

```
aws-cloudhsm > logout
aws-cloudhsm > quit
```

**확인:** `logout`이 성공했다. 실패·결과 불명이면 접근 담당자와 세션 종료를 확인하고 그 결과를 남긴다. 확인 전에는 종료 완료로 표시하지 않는다.

key-usage 토큰은 작업 성공 시 해당 토큰이 무효화되며, 로그아웃하면 그 세션의 토큰도 무효화된다. 파일 삭제로 무효화를 대신하지 않는다. [AWS 토큰 수명 설명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)

**저장:** 로그아웃 응답 → `evidence/A4-logout.txt`

실행자는 서명에 사용한 세 토큰의 `evidence/` 보관본이 원문과 같고 증거 목록에 등록됐는지 다시 확인한다. 진행자가 세션 종료와 증거 보관을 확인한 뒤 **회차 폴더의 작업용 사본만** 삭제한다.

```
$ cmp A2.3-token-signed.json evidence/A2.3-token-signed.json
$ cmp A3.3-token-signed.json evidence/A3.3-token-signed.json
$ cmp A3.5-token-signed.json evidence/A3.5-token-signed.json
$ rm -- A2.3-token.json A2.3-token-signed.json A3.3-token.json A3.3-token-signed.json A3.5-token.json A3.5-token-signed.json
```

비교 실패 시 삭제하지 않는다. 중단·토큰 재발급으로 다른 파일이 생겼다면 파일별 승인·실행 여부와 보관본을 확인한 뒤 삭제 대상을 확정한다. 승인자도 전달받은 작업용 사본을 정리한다. `evidence/`의 승인 증거는 삭제하지 않는다.

**누가:** 접근 담당자

```
{{임시_접근_종료_확인_명령}}
```

**확인:** 해당 세션의 토큰이 무효화됐고 임시 접근이 종료됐다. 유지하는 권한이 승인 목록과 같다. 예상하지 않은 키·권한 변경이 있으면 종료 완료를 보류하고 스크립트 「중단과 재개」를 따른다.
**저장:** `evidence/A4-access.txt`

**3) 백업·off-site 사본·보호 상태·감사 로그를 확인한다.**

**누가:** 백업 인수자, 접근 담당자 → 진행자. AWS 조회는 승인된 읽기 계정으로 터미널 2에서 실행한다.

```
$ aws cloudhsmv2 describe-backups --filters clusterIds={{CLUSTER_ID}} --output json > evidence/A4-backups.json
$ {{offsite_사본_조회_명령}}
$ {{백업_보호설정_조회_명령}}
$ aws logs filter-log-events --log-group-name "/aws/cloudhsm/{{CLUSTER_ID}}" --start-time {{현장_행사시작_epoch_ms}} --end-time {{현장_세션종료후_epoch_ms}} --output json > evidence/A4-hsm-audit.json
```

off-site·보호설정 조회 명령과 아래 판정 기준은 스크립트 Appendix A의 백업 계획에 맞춰 행사 전에 확정한다. 조회 명령은 대상 위치·계정·백업 ID와 접근·복원·삭제 통제, 보존 설정을 확인할 수 있어야 한다.

| 확인할 것 | 확인·인계할 내용 | 증거 파일 |
|---|---|---|
| 신규 키·최종 권한 포함 | 두 키 생성과 최종 권한 변경 이후의 대상 클러스터 백업 ID·시각·`READY` 확인. 최종 키·사용자 조회, 변경·동기화 감사 로그와 백업 시각을 승인된 포함 확인 기준으로 대조한다. `READY`만으로 포함 확인을 완료하지 않는다 | `A4-backups.json`, `A4-root-key.json`, `A4-first-key.json`, `A4-users.json`, `A4-hsm-audit.json` |
| off-site 사본 | 승인된 보관 위치의 사본 ID·상태와 위 원본 백업의 대응 관계 확인. 사본이 없으면 행사 전에 이 단계에 확정한 복사 명령을 수행한 뒤 다시 조회한다 | `A4-offsite.json` |
| 보호·복구 준비 | 원본·사본의 보호 방식, 접근·복원·삭제 권한과 승인 통제, 보존 설정이 승인 계획과 일치하는지 확인. 적용 가능한 사전 복구 시험 결과와 인수자 확인 | `A4-backup-protection.txt`, 사전 복구 시험 증거 ID |
| 감사 로그 | 행사 시작부터 세션 종료까지 전체 HSM의 로그를 확인. 생성·동기화·권한 변경·로그인/종료 결과를 실행 기록과 대조하고 누락·지연 여부 확인 | `A4-hsm-audit.json` |

**저장:** 조회 출력은 표의 파일명으로 `evidence/`에 저장한다. 진행자는 수행 기록의 「종료 확인」에 각 판정·담당자·확인 시각·증거 ID를 적는다. HSM 백업 원본은 내려받지 않는다.

미확인 항목이 있으면 **후속 확인 대기**로 기록하고 담당자·기한을 정한다. 후속 확인은 별도 작업 폴더에 `evidence/`와 새 세션 로그를 준비한 뒤 이 단계의 조회·대조를 수행한다. 원래 회차의 키·권한 증거를 참조하고, 새 출력은 후속 폴더에 저장한다. 로그를 닫은 뒤 새 증거·로그의 해시와 확인 결과를 후속 기록으로 넘긴다. 기존 증거·서명본은 덮어쓰지 않는다. 진행자는 모든 미완료 항목이 해소됐는지 확인하고 후속 기록에 완료 판정·성명·시각을 남긴다.

백업 조회 필드와 감사 로그 범위: [AWS 백업 조회](https://docs.aws.amazon.com/cli/latest/reference/cloudhsmv2/describe-backups.html), [HSM별 감사 로그](https://docs.aws.amazon.com/cloudhsm/latest/userguide/understand-audit-logs.html).

**4) 로그를 닫고 해시를 확정한다.**

모든 당일 증거 저장을 마친 뒤 두 터미널의 기록을 종료한다. 터미널 1의 종료가 끝났는지 확인한 다음 터미널 2를 종료하고 해시를 계산한다.

```
터미널 1:
$ exit

터미널 2:
$ exit
$ sha256sum evidence/* > A4-sha256.txt
```

**확인 (진행자):**

1. 두 로그가 닫혀 더 이상 기록되지 않는다. `A4-sha256.txt`에서 로그의 최종 해시를 가져와 증거 목록의 `기록 중`을 바꾼다.
2. 이미 확정한 나머지 파일의 해시를 대조한다. 불일치하면 원인을 확인하며, 값을 덮어써 맞추지 않는다.
3. 모든 증거 파일의 최종 해시·경로가 일치하는지 확인한 뒤 수행 기록을 확정하고 `signoff.md`에 서명한다. `A4-sha256.txt`는 대조용이며 서명 대상 증거 목록을 대신하지 않는다.

---

## 토큰 승인 방법

A2.3, A3.3, A3.5의 4)에서 승인자가 따르는 절차다.

1. 실행자에게서 토큰 파일을 받는다.
2. 토큰의 대상 키와 작업이 지금 승인할 본문과 맞는지 확인한다.
3. 본인 장치에서 본인 승인키로 서명한다.

   ```
   {{승인_서명_명령}}
   ```

4. 서명 결과를 실행자에게 돌려준다. 승인키나 비밀번호는 넘기지 않는다.

토큰은 기본 10분 후 만료된다. 만료되면 실행자가 새 토큰을 만들고 처음부터 다시 서명한다.

## 아직 정해지지 않은 것

리허설 전에 정하고 위 명령에 반영한다.

| 항목 | 들어갈 곳 |
|---|---|
| 관리 quorum과 잠금 속성. 검토안은 `--manage-private-key-quorum-value 2`, `modifiable=false destroyable=false`. 생성 후 되돌릴 수 없으므로 승인 전에는 행사를 시작하지 않는다 | `{{관리_quorum_인자}}`, `{{잠금_속성}}` |
| 생성 접근을 열고 닫는 방법. 키 생성은 AWS quorum으로 막을 수 없으므로 별도 통제가 필요하다 | A2.1, A2.2 4), A3.1, A3.2 |
| 본문 생성·조립·비교 도구와 C2PA 검사 도구 | `{{tool}}`, `{{verifier}}` |
| 승인자의 토큰 서명 명령과 전달 방법 | 「토큰 승인 방법」 |
| CLI 출력을 증거 파일로 저장하는 방법 | 「시작하기 전에」 |
| OCSP 확인·조회 명령, 임시 접근 종료 확인 명령 | A3.5, A4 |
| 백업 포함 판정 기준·인수자, off-site 사본 조회·필요시 복사 명령, 보호설정 조회 명령·기준, AWS 조회 계정·리전 | A4 3). 사전 복구 시험 결과와 연결하고 실제 명령을 이 부록에 기입 |

리허설에서는 특히 `key generate-file`로 꺼낸 공개키가 실제 HSM 키와 맞는지, `crypto sign ecdsa`의 `--data-type raw` 서명이 조립 후 검증을 통과하는지 테스트 키로 확인한다.

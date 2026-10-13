# Samsung C2PA Key Generation Ceremony Script

- 문서 번호: KGC-C2PA-2026-001 / 행사 관리명 `root-first-004`
- Script 버전: `{{버전}}` (초안 · 승인 전)
- 오늘 할 일: **Samsung Cloud Service Platform Root CA G1**(Root)과 **Samsung C2PA Intermediate CA G1**(C2PA ICA)의 키를 만들고, 인증서를 발급·검사하고, 안전하게 보관한다.
- 오늘 하지 않는 일: 하위 Issuing CA·leaf·OCSP 응답자 인증서 발급, 서비스 개시, Trust List 신청
- 따르는 기준: [C2PA Certificate Policy v0.2][cp](CP), [Conformance Program v0.2][program], 공식 저장소 commit `2466172`의 인증서 프로파일과 schema. CP 조항은 제목으로 적는다.
- `{{항목}}`은 승인 전에 채울 값, `{{현장_항목}}`은 행사 중에 채울 값이다. 부록 D에 미결 항목이 남아 있으면 이 Script는 승인하지 않는다.

> **이 행사의 세 가지 원칙**
> 1. **혼자서는 CA 키를 쓸 수 없다.** CA 키는 만드는 명령에서부터 사용·관리에 KC 2명의 승인이 필요하도록 만든다. 그래서 키가 생긴 순간부터 서명·공유·속성 변경은 모두 KC 2명이 각자 승인해야 한다.
> 2. **서명은 한 번만 한다.** HSM 서명 명령은 다시 실행하지 않는다. 결과가 검사에 실패하면 같은 키로 다시 발급하지 않고 키를 새로 만든다.
> 3. **모든 것을 남긴다.** 화면 입출력은 세션 로그에, 결과 파일은 `evidence/`에 남긴다. 입회자가 처음부터 끝까지 지켜본다.

---

## 목차

1. 승인 및 기본 정보
2. 역할 및 참가자
3. 준비물 (HSM·계정·KMS·비밀번호·단말·소프트웨어)
4. 시작 전 확인
5. 실행 단계
   - 5.0 진행 방법과 멈춤 규칙
   - 5.1 시작 확인
   - 5.2 클러스터 소유 증명서 만들기
   - 5.3 클러스터 초기화 (Root → C2PA)
   - 5.4 활성화, 계정, 승인 규칙 설정 (Root → C2PA)
   - 5.5 Root 키와 자체서명 인증서 만들기
   - 5.6 C2PA ICA 키, CSR, 인증서 만들기
   - 5.7 결과 종합 확인
   - 5.8 백업하고 HSM 잠그기
   - 5.9 마무리
6. 행사 후 보관과 접근 통제
7. 참가자 확인 서명
8. 편차 기록
- 부록 A 인증서·CSR 설정 / 부록 B 도구 / 부록 C 지문 기록표 / 부록 D 승인 전 확정 목록 / 부록 E 승인자 안내

---

## 1. 승인 및 기본 정보

| 항목 | 내용 |
|---|---|
| 일시 | `{{일시}}` KST |
| 장소 | `{{건물/층/룸}}` |
| 수행 승인 (경영진) | 성명 / 직책 / 서명 / 일자 |
| 수행 승인 (보안책임자) | 성명 / 직책 / 서명 / 일자 |
| 승인 Script | `script.md` v`{{버전}}` / SHA-256 `{{해시}}`. 행사 중에는 바꾸지 않는다 |
| C2PA 해석 확인 | 키 생성 다인 통제 방식(생성 시 사용·관리 Quorum 지정 + 독립 입회)에 대한 C2PA 서면 확인: `{{보낸 사람_일자_문서ID}}` |
| 함께 승인한 자료 | 부록 A 설정 파일, 부록 B 도구, 리허설 결과서의 ID·버전·SHA-256: `{{목록}}` |
| 기록 보관 위치 | 회차 폴더 `{{DIR}}`(세션 로그, `evidence/`), 최종 보관소 `{{위치_권한_보존정책}}` |
| 백업·복구 계획 | 매년 검토하는 키 백업·복구 계획 `{{문서ID_버전}}` (CP *Key Backup and Recovery* 1) |

비밀번호, 비밀번호 분할본, CA 개인키, KC 개인키는 이 문서·수행 기록·증거 파일 어디에도 적지 않는다.

## 2. 역할 및 참가자

| 역할 | 성명 | 소속 | 하는 일 | 하지 않는 일 |
|---|---|---|---|---|
| 진행자 (CA-Admin) | | | 단계를 부르고, 결과를 기대 출력과 맞춰 보고, 서명 실행을 지시하고, 기록한다 | CLI·AWS 조작, 승인, 비밀번호 보유 |
| 실행자 (CO) | | | HSM 명령과 도구를 입력한다. 키 소유 계정(`cu_root`·`cu_c2pa`)으로 로그인한다 | 승인, KMS 키 사용, AWS 리소스 변경 |
| AWS 담당 (IAM-Op) | | | 클러스터·백업 같은 AWS 작업, KMS 공개키 조회, 로그 조회를 한다 | HSM 로그인, `kms:Sign`, 비밀번호 보유 |
| 승인자 KC1 | | | 자기 KMS 키로 승인한다. `kc1`·`cu_kc1` 비밀번호를 입력한다 | 명령 입력, AWS 리소스 변경, 키 소유 계정 비밀번호 보유 |
| 승인자 KC2, KC3 | | | 자기 KMS 키로 승인한다. `kcN`·`cu_kcN` 비밀번호를 입력한다 | 명령 입력, AWS 리소스 변경, 키 소유 계정 비밀번호 보유 |
| 입회자 (IW) | | | 처음부터 끝까지 지켜보고, 해시·지문을 함께 기록하고, 마지막에 확인 서명한다 | 모든 조작, 승인, 비밀번호 보유 |

- **한 사람이 두 역할을 맡지 않는다.** 승인자 3명을 포함해 모두 7명이 참석한다.
- **입회자는 독립적이어야 한다.** CA 운영 조직의 지휘·평가 라인 밖에 있고, 이 CA의 키·권한·승인 재료를 갖지 않는다. 4.3에서 소속·담당 업무·실행팀과의 관계를 기록한다.
- **승인 규칙(Quorum):** 두 클러스터 모두 계정·규칙 변경은 admin 3명 중 2명, CA 키 사용은 승인자 CU 3명 중 2명이 승인해야 한다.

| 작업 | 꼭 있어야 하는 사람 | 근거 (CP) |
|---|---|---|
| CA 키 만들기 | CO(실행) + 입회자. 만드는 명령에서 사용·관리 승인 2명을 지정하고 5.5.3·5.6.3에서 확인한다 | *Key Pair Generation by CAs* 3.2 (C2PA 해석 확인, 1장) |
| CA 키로 서명하기 | CO(실행) + KC 2명(승인), 입회자 | *Certificate Issuance* 1·2, *Separation of Duties* 2·3, *Key Usage and Access Control* 1 |
| HSM 계정·승인 규칙 바꾸기 | admin 2명(KC) | *Separation of Duties* 2 |

## 3. 준비물

### 3.1 HSM

| 항목 | Root 클러스터 | C2PA 클러스터 |
|---|---|---|
| 들어갈 키 | Root 키 | C2PA ICA 키 |
| 계정 / 리전 | `{{ACCOUNT}}` / `{{REGION}}` | `{{ACCOUNT}}` / `{{REGION}}` |
| Cluster ID / HSM ID | `{{ROOT}}` / 5.1.6에서 기록 | `{{C2PA}}` / 5.1.6에서 기록 |
| 모델 / 모드 | hsm2m.medium / **FIPS** | hsm2m.medium / **FIPS** |
| 인증 | FIPS 140-3 Level 3, CMVP `{{번호}}`, 펌웨어 `{{버전}}` | 같음 |
| 계정·규칙 변경 승인 | admin 3명 중 2명 (`user`·`cluster`·`quorum` 서비스) | 같음 |
| 키 사용 승인 | 승인자 CU 3명 중 2명 | 같음 |
| 백업 사본 리전 | `{{DR_REGION}}` | `{{DR_REGION}}` |

> Root는 플랫폼 공용 루트라서 C2PA ICA와 클러스터를 나눈다. 두 클러스터 사이에는 CSR과 인증서(공개 정보)만 오간다.

### 3.2 HSM 계정

| 계정 | 종류 | 비밀번호를 아는 사람 | 쓰임 |
|---|---|---|---|
| `admin` | admin | KC1·KC2가 반씩 | 활성화, 계정 만들기, 승인 규칙 설정 |
| `kc1`, `kc2`, `kc3` | admin | 각 KC | 계정·규칙 변경 승인 |
| `cu_root` | CU | CO | Root 키를 소유하고, 만들고, 서명을 실행. 키 사용·관리에는 KC 2명 승인 필요 |
| `cu_c2pa` | CU | CO | C2PA ICA 키를 소유하고, 만들고, 서명을 실행. 키 사용·관리에는 KC 2명 승인 필요 |
| `cu_kc1`, `cu_kc2`, `cu_kc3` | CU | 각 KC | 키 사용 승인 |

### 3.3 승인자 KMS 키

| 승인자 | KMS 키 (ARN / alias) | 종류 | 서명할 수 있는 사람 | MFA | 공개키 지문 |
|---|---|---|---|---|---|
| KC1 | `{{ARN}}` / `alias/c2pa-quorum-kc1` | RSA_2048 서명용 | `{{KC1 principal}}` | 필수 | 부록 C |
| KC2 | `{{ARN}}` / `alias/c2pa-quorum-kc2` | RSA_2048 서명용 | `{{KC2 principal}}` | 필수 | 부록 C |
| KC3 | `{{ARN}}` / `alias/c2pa-quorum-kc3` | RSA_2048 서명용 | `{{KC3 principal}}` | 필수 | 부록 C |

KC마다 KMS 키 하나로 admin(`kcN`) 승인과 CU(`cu_kcN`) 승인을 모두 한다.

### 3.4 비밀번호와 봉투

| 비밀 | 만드는 단계 | 아는 사람 | 봉투 번호 |
|---|---|---|---|
| hsm-owner 개인키 패스프레이즈 (반씩) | 5.2.1 | KC1 / KC2 | `{{현장}}` |
| 초기 `admin` 비밀번호 (반씩) | 5.4.1 | KC1 / KC2 | `{{현장}}` |
| `cu_root`, `cu_c2pa` 비밀번호 | 5.4.3 | CO (봉인 사본 1부) | `{{현장}}` |
| `kcN`, `cu_kcN` 비밀번호 | 5.4.2, 5.4.3 | 각 KC (봉인 사본 1부) | `{{현장}}` |
| KMS 키 사용 권한 (IAM + MFA 장치) | 사전 | 각 KC | 해당 없음 |

> 비밀을 만들면 그 자리에서 보유자가 봉투에 넣어 봉인한다. 진행자가 봉투 번호를 적고, 입회자가 봉인을 확인한다. 봉투는 마지막에 이중 통제 금고(`{{ID}}`)에 넣는다.

### 3.5 단말

| 단말 | 쓰는 사람 | 연결 | 인증 | 반입 |
|---|---|---|---|---|
| 행사용 EC2 (CLI·도구) | CO | 작업자 단말 → `{{SSM 또는 jumphost}}` → private subnet. 인터넷 차단, VPC endpoint만 | `{{IAM 역할 + MFA}}` | 해당 없음 |
| CO 작업자 단말 | CO | 행사용 EC2 접속 전용 | `{{SSO + MFA}}` | 허용(목록 등록) |
| KC 단말 ×3 | KC1~KC3 | AWS KMS | 본인 IAM + MFA | 허용(목록 등록) |
| IAM-Op 단말 | IAM-Op | AWS 콘솔·CLI | `{{SSO + MFA}}` | 허용(목록 등록) |
| 관찰 화면 | 진행자·입회자 | CO 화면 미러링 | 해당 없음 | 허용(목록 등록) |

이 목록에 없는 무선기기는 들여오지 않는다. KC의 MFA 장치는 목록에 등록한 경우에만 들여온다.

### 3.6 소프트웨어

| 항목 | 버전 | SHA-256 |
|---|---|---|
| CloudHSM CLI / Client SDK | `{{}}` | `{{}}` |
| AWS CLI | `{{}}` | `{{}}` |
| OpenSSL (검증용) | `{{}}` | `{{}}` |
| `{{tool}}` (본문 만들기·조립·비교, 부록 B) | `{{}}` | `{{}}` |
| `{{verifier}}` (프로파일·schema 검사, 부록 B) | `{{}}` | `{{}}` |
| 설정 파일 `root.conf`, `first.conf` (부록 A) | `{{}}` | `{{}}` |

## 4. 시작 전 확인

진행자가 하나씩 확인한다. 하나라도 안 되면 시작하지 않는다.

| # | 확인할 것 | 확인자 | ☐ | 시각 |
|---|---|---|---|---|
| 4.1 | 수행 승인 서명이 있고, 오늘 쓰는 Script와 자료의 해시가 1장에 적힌 값과 같다 | 진행자 / IW | ☐ | |
| 4.2 | 부록 D의 미결 항목이 하나도 없다 | 진행자 | ☐ | |
| 4.3 | 전원이 출석했고 신분을 확인했다. 전원이 신뢰 역할로 지정돼 있고 배경 확인(채용 시, 5년 이내)과 교육 기록이 있다. 입회자의 독립성을 기록했다 | 진행자 / IW | ☐ | |
| 4.4 | 들여온 단말이 3.5 목록과 같고, 목록에 없는 무선기기가 없다 | IW | ☐ | |
| 4.5 | KMS 키 3개와 키 정책(6장)이 준비됐고, 공개키 지문이 부록 C의 사전 기록값과 같다 | IAM-Op / IW | ☐ | |
| 4.6 | 리허설 결과서에서 테스트 키로 다음 6가지가 모두 통과했다. ① 토큰 서명 형식이 맞다 ② **토큰 없이 CA 키로 서명하면 거부된다** ③ **admin 1명이 승인 규칙을 바꾸려 하면 거부된다** ④ 부록 A 설정으로 만든 테스트 Root·ICA 인증서와 CSR이 공식 schema를 통과한다 ⑤ 서명 결과를 조립한 인증서가 서명 검증을 통과한다 ⑥ 백업으로 복원한 클러스터에 키·계정·승인 규칙이 그대로 있다 ⑦ **키 소유 CU 혼자서는 키 공유·속성 변경이 거부된다** | 진행자 | ☐ | |
| 4.7 | 사전 준비(IAM-Op, 행사 전): 두 클러스터를 FIPS 모드로 만들고(`create-cluster --mode FIPS`) HSM을 1개씩 붙였다. private subnet·보안그룹과 행사용 EC2의 도구 설치도 끝났다. 초기화·활성화는 하지 않은 상태다 | IAM-Op | ☐ | |
| 4.8 | 봉투, 봉인 테이프, 금고를 준비했고 봉투 번호 목록을 만들었다 | 진행자 | ☐ | |

## 5. 실행 단계

### 5.0 진행 방법과 멈춤 규칙

**진행 방법**

1. 진행자가 단계 번호와 작업을 읽으면 담당자가 수행한다. 진행자는 결과를 기대 출력과 맞춰 보고 ☐에 체크하고 시각을 적는다.
2. 명령 앞 표시로 입력 위치를 구분한다. `$`는 행사용 EC2 셸, `aws-cloudhsm >`는 CloudHSM CLI, `[KC 단말]`·`[IAM-Op]`는 해당 사람의 단말이다.
3. 비밀번호는 프롬프트가 나올 때만 입력한다. 두 사람이 반씩 입력할 때(hsm-owner 패스프레이즈, 초기 `admin`)는 앞 절반 다음 뒤 절반 순서로 한다. 입력하는 사람 외에는 화면과 키보드를 보지 않는다.
4. 토큰은 서명할 때마다 새로 만든다. 토큰 파일은 `{{TOKEN_XFER}}`로 주고받고, 주기 전과 받은 후의 SHA-256을 맞춰 본다.

> **멈춤 규칙: 아래 중 하나라도 생기면 바로 멈추고 8장에 기록한다.**
> 1. 결과가 기대 출력과 다르다.
> 2. **HSM 서명(`crypto sign`)의 결과를 알 수 없다.** 다시 실행하지 않는다. 응답 파일이 남아 있으면 조립과 검사만 다시 한다.
> 3. **서명 후 검사(5.5.10, 5.6.10, 5.6.19)가 실패했다.** 그 인증서는 배포하지 않는다. 같은 키로 다시 발급하지 않고, 별도 승인을 받아 키를 지운 뒤 새로 만든다. (CP *Certificate Renewal*·*Certificate Modification*의 보수적 해석)
> 4. 입회자가 지켜볼 수 없는 상황이 생겼다.
>
> 멈출 때는 열린 HSM 세션을 로그아웃하고 마지막 상태를 그대로 보존한다. 원인과 영향을 확인하고 승인을 받은 뒤, 입회 하에 다시 시작한다.

> **2인 승인 서명의 흐름 (5.5.5–5.5.10, 5.6.5–5.6.10, 5.6.13–5.6.18에서 반복)**
> 본문 만들기(CO) → 본문 확인(KC 2명, 입회자) → 토큰 만들기(CO) → 토큰 승인(KC 2명) → 서명(진행자 지시, CO 실행, **한 번만**) → 조립·검사.
> 본문 확인을 따로 하는 이유: HSM 토큰은 "이 키를 한 번 쓴다"는 승인일 뿐, 무엇에 서명하는지까지 묶어 주지 않기 때문이다.

### 5.1 시작 확인

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.1.1 | CO | 화면 기록 시작 (행사용 EC2) | `$ cd {{DIR}} && mkdir -p evidence && script -f evidence/session.log` | `evidence/session.log`가 생긴다. 진행자가 기록에 등록한다 | ☐ | |
| 5.1.2 | CO | 인터넷이 막혀 있는지 확인 | `$ curl -sS -m 5 https://example.com` | 연결 실패가 나온다 | ☐ | |
| 5.1.3 | CO | 맞는 AWS 역할로 접속했는지 확인 | `$ aws sts get-caller-identity` | 3.5에 적은 행사용 EC2 역할이 나온다 | ☐ | |
| 5.1.4 | CO | 시계가 맞는지 확인 | `$ date -u && chronyc tracking` | 기준이 Amazon Time Sync(169.254.169.123)이고 오차가 1초 미만이다 | ☐ | |
| 5.1.5 | CO | 도구와 설정 파일이 승인본인지 확인 | `$ sha256sum $(which cloudhsm-cli aws openssl {{tool}} {{verifier}}) root.conf first.conf` | 모든 값이 3.6과 같다 | ☐ | |
| 5.1.6 | IAM-Op | 두 클러스터 상태 확인 | `[IAM-Op] $ aws cloudhsmv2 describe-clusters --filters clusterIds={{ROOT}},{{C2PA}} > evidence/5.1.6-clusters.json` | 둘 다 `Mode: FIPS`, `State: UNINITIALIZED`, HSM 1개가 `ACTIVE`다. HSM ID를 3.1에 적는다 | ☐ | |

### 5.2 클러스터 소유 증명서 만들기

> HSM 클러스터를 우리 소유로 등록할 때 쓰는 자체서명 증명서다. C2PA 인증서 체인과는 관계없고 Trust List나 manifest에도 들어가지 않는다. 두 클러스터에 같은 증명서를 쓴다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.2.1 | CO, KC1·KC2 | 소유 증명 키 만들기 | `$ openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -aes256 -out hsm-owner.key` | 패스프레이즈를 KC1이 앞 절반, KC2가 뒤 절반 입력. 각자 바로 봉인 | ☐ | |
| 5.2.2 | CO, KC1·KC2 | 소유 증명서 만들기 | `$ openssl req -new -x509 -days 3652 -key hsm-owner.key -subj "/C=KR/O={{ORG}}/CN={{ORG}} CloudHSM Cluster Owner" -out evidence/hsm-owner.crt` | 패스프레이즈 입력 후 `hsm-owner.crt`가 생긴다 | ☐ | |
| 5.2.3 | CO / IW | 증명서 지문 기록 | `$ openssl x509 -in evidence/hsm-owner.crt -noout -fingerprint -sha256` | 입회자가 지문을 부록 C에 함께 적는다 | ☐ | |

### 5.3 클러스터 초기화 (Root → C2PA 순)

> 아래 표를 Root 클러스터로 먼저 하고 Root 칸에 체크한다. 이어서 C2PA 클러스터로 한 번 더 하고 C2PA 칸에 체크한다. `<C>`는 Cluster ID(`{{ROOT}}` / `{{C2PA}}`), `<c>`는 파일 이름(`root` / `c2pa`)이다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |
|---|---|---|---|---|---|---|
| 5.3.1 | IAM-Op | 클러스터 CSR 꺼내기 | `[IAM-Op] $ aws cloudhsmv2 describe-clusters --filters clusterIds=<C> --query 'Clusters[0].Certificates.ClusterCsr' --output text > evidence/<c>-cluster.csr` | CSR 파일이 생긴다 | ☐ | ☐ |
| 5.3.2 | IW | 그 클러스터의 CSR이 맞는지 확인 | `$ openssl req -in evidence/<c>-cluster.csr -noout -subject` | Subject에 해당 Cluster ID가 들어 있다 | ☐ | ☐ |
| 5.3.3 | CO, KC1·KC2 | 소유 증명 키로 CSR 서명 | `$ openssl x509 -req -days 3652 -in evidence/<c>-cluster.csr -CA evidence/hsm-owner.crt -CAkey hsm-owner.key -CAcreateserial -out evidence/<c>-signed.crt` | 패스프레이즈 입력 후 성공 | ☐ | ☐ |
| 5.3.4 | IAM-Op | 클러스터 초기화 | `[IAM-Op] $ aws cloudhsmv2 initialize-cluster --cluster-id <C> --signed-cert file://evidence/<c>-signed.crt --trust-anchor file://evidence/hsm-owner.crt` | 잠시 뒤 describe-clusters에서 `INITIALIZED`가 나온다 | ☐ | ☐ |
| 5.3.5 | CO | CLI로 접속 | hsm-owner.crt를 `<C>`의 trust anchor로 배치한 뒤 `$ cloudhsm-cli interactive --cluster-id <C>` | `aws-cloudhsm >` 프롬프트가 나온다 | ☐ | ☐ |

### 5.4 활성화, 계정, 승인 규칙 설정 (Root → C2PA 순)

> 5.3처럼 Root 클러스터로 먼저 하고 C2PA 클러스터로 한 번 더 한다. KMS 공개키 꺼내기(5.4.4)는 처음 한 번만 한다. 참고: [AWS 공식 절차](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html)
>
> **계정을 모두 만든 뒤 마지막에 승인 규칙 값(5.4.10)을 설정한다.** 순서를 바꾸면 계정을 하나 만들 때마다 admin 2명의 승인이 필요해진다.
>
> 승인키 등록(5.4.5–5.4.7)은 이렇게 진행한다. KC가 CO 화면에서 본인 계정으로 로그인해 등록 토큰을 받고, 자기 단말에서 KMS로 서명하고, 다시 CO 화면에서 등록한다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |
|---|---|---|---|---|---|---|
| 5.4.1 | CO, KC1·KC2 | 클러스터 활성화 | `aws-cloudhsm > cluster activate` | 초기 `admin` 비밀번호를 KC1이 앞 절반, KC2가 뒤 절반 입력. 각자 봉인 | ☐ | ☐ |
| 5.4.2 | CO, KC1~KC3 | admin 계정 3개 만들기 | `aws-cloudhsm > login --username admin --role admin` (KC1·KC2 입력) → `user create --username kc1 --role admin` (kc2, kc3도 같은 방법) | 각 비밀번호는 해당 KC가 직접 입력. 3개 모두 성공 | ☐ | ☐ |
| 5.4.3 | CO, KC1~KC3 | CU 계정 4개 만들기 | `aws-cloudhsm > user create --username cu_<c> --role crypto-user` → `user create --username cu_kc1 --role crypto-user` (cu_kc2, cu_kc3도 같은 방법) → `user list` → `logout` | `cu_<c>`는 CO가, `cu_kcN`은 각 KC가 입력하고 각자 봉인 사본을 만든다. 목록에 admin 4개, CU 4개가 보인다 | ☐ | ☐ |
| 5.4.4 | IAM-Op / IW | KC 공개키 꺼내기 (처음 한 번만) | `[IAM-Op] $ aws kms get-public-key --key-id alias/c2pa-quorum-kc1 --output text --query PublicKey \| base64 -d > evidence/kc1.der && openssl pkey -pubin -inform DER -in evidence/kc1.der -out evidence/kc1_pub.pem` (kc2, kc3도 같은 방법) → `sha256sum evidence/kc*.der` | PEM 3개가 생기고, 지문이 부록 C의 사전 기록값과 같다 | ☐ | — |
| 5.4.5 | KC1 (CO 화면, 본인 로그인) | KC1 등록 토큰 받기 | `aws-cloudhsm > login --username kc1 --role admin` → `quorum token-sign generate --service registration --token kc1.token` | 토큰 파일이 생긴다 (`tokens[].unsigned` 포함) | ☐ | ☐ |
| 5.4.6 | KC1 (자기 단말, MFA) | 토큰에 KMS로 서명 | `[KC1 단말] $ echo -n '<unsigned 값>' \| base64 -d > kc1.bin` → `aws kms sign --key-id alias/c2pa-quorum-kc1 --message fileb://kc1.bin --message-type DIGEST --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 --output text --query Signature > kc1.sig.b64` | base64 서명값이 나온다 | ☐ | ☐ |
| 5.4.7 | KC1 (CO 화면) | 승인키 등록 | 서명값을 `kc1.token`의 `tokens[].signed`에 넣고 `aws-cloudhsm > user change-quorum token-sign register --public-key evidence/kc1_pub.pem --signed-token kc1.token` → `logout` | `error_code: 0` | ☐ | ☐ |
| 5.4.8 | KC2, KC3 | KC2·KC3도 같은 방법으로 등록 | 5.4.5–5.4.7을 `kc2`, `kc3`로 반복 | 2번 모두 성공 | ☐ | ☐ |
| 5.4.9 | KC1~KC3 | 승인자 CU에도 같은 키 등록 | 각 KC가 `login --username cu_kcN --role crypto-user`로 로그인한 뒤 5.4.5–5.4.7과 같은 방법으로 **같은 KMS 키**를 등록 | 3번 모두 성공 | ☐ | ☐ |
| 5.4.10 | CO, KC1·KC2 | 승인 규칙 값 설정 | `aws-cloudhsm > login --username admin --role admin` (KC1·KC2 입력) → `quorum token-sign set-quorum-value --service user --value 2` → `quorum token-sign set-quorum-value --service cluster --value 2` → `quorum token-sign set-quorum-value --service quorum --value 2` (**`quorum`은 마지막에**. 먼저 걸면 나머지 설정에도 승인이 필요해진다) → `quorum token-sign list-quorum-values` | `user: 2`, `cluster: 2`, `quorum: 2`가 보인다 | ☐ | ☐ |
| 5.4.11 | CO | 등록 상태 확인 | `aws-cloudhsm > user list` → 출력을 `evidence/5.4.11-<c>-users.json`에 저장 → `logout` | kc1~kc3, cu_kc1~cu_kc3 모두 `token-sign: enabled` | ☐ | ☐ |
| 5.4.12 | IAM-Op / IW | 승인 기록 확인 | CloudTrail에서 5.4.6–5.4.9의 `kms:Sign` 조회 → `evidence/5.4.12-<c>-trail.json` | 6건이 있고, KC마다 다른 사람(principal)으로 기록돼 있다 | ☐ | ☐ |

### 5.5 Root 키와 자체서명 인증서 만들기 (Root 클러스터)

> CO가 Root 키 소유 계정으로 로그인해 키를 만든다. 키를 만드는 명령에 사용·관리 승인 2명을 함께 지정하므로, 키는 생긴 순간부터 KC 2명의 승인 없이는 쓰거나 바꾸거나 지울 수 없다. **5.5.3의 확인 결과가 키 생성 다인 통제의 핵심 증거**이므로 입회자가 직접 확인한다. 이 방식은 C2PA로부터 다인 통제로 인정받았다(1장 "C2PA 해석 확인").
>
> 자체서명은 위의 "2인 승인 서명의 흐름"을 따른다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.5.1 | CO | Root 키 소유 계정 로그인 | `$ cloudhsm-cli interactive --cluster-id {{ROOT}}` → `aws-cloudhsm > login --username cu_root --role crypto-user` | 로그인 성공 | ☐ | |
| 5.5.2 | CO | Root 키 만들기 | `aws-cloudhsm > key generate-asymmetric-pair ec --curve secp384r1 --public-label platform-root --private-label platform-root --public-attributes verify=true token=true --private-attributes sign=true decrypt=false derive=false unwrap=false extractable=false sensitive=true token=true --share-crypto-users cu_kc1 cu_kc2 cu_kc3 --use-private-key-quorum-value 2 --manage-private-key-quorum-value 2` | 성공 응답과 key-reference 2개가 나온다 → `evidence/5.5.2-generate.json` | ☐ | |
| 5.5.3 | CO / 진행자 / IW | 키가 의도대로 만들어졌는지 확인 (다인 통제 증거) | `aws-cloudhsm > key list --filter attr.label=platform-root attr.class=private-key --verbose` | 딱 1건. `secp384r1`, `sign=true`, `extractable=false`, `sensitive=true`, 공유 사용자 cu_kc1~3, **사용·관리 승인 2명**. 입회자가 화면에서 직접 확인한다 → `evidence/5.5.3-key.json` | ☐ | |
| 5.5.4 | CO / IW | 공개키를 꺼내고 지문 기록 | `aws-cloudhsm > key generate-file --encoding pem --path evidence/root-pub.pem --filter attr.label=platform-root attr.class=public-key` → `$ openssl pkey -pubin -in evidence/root-pub.pem -outform DER \| sha256sum` | P-384 공개키. 지문을 부록 C에 적는다 | ☐ | |
| 5.5.5 | CO / 진행자 | 서명할 인증서 본문 만들기 | `$ {{tool}} tbs root --config root.conf --pubkey evidence/root-pub.pem --out evidence/root-tbs.der` → `{{tool}} show evidence/root-tbs.der > evidence/root-tbs.txt` → `sha256sum evidence/root-tbs.der` | 진행자가 Subject·기간·serial·확장을 부록 A와 맞춰 본다. 입회자가 해시를 적는다 | ☐ | |
| 5.5.6 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 `root-tbs.txt` 화면과 해시를 본다 | 승인자 이름과 확인한 해시를 수행 기록에 적는다 | ☐ | |
| 5.5.7 | CO | Root 키 사용 토큰 받기 | `aws-cloudhsm > quorum token-sign generate --service key-usage --token root-sign.token --filter attr.label=platform-root attr.class=private-key` | 토큰 파일이 생긴다 | ☐ | |
| 5.5.8 | KC 2명 (자기 단말, MFA) | 토큰 승인 | 부록 E 순서대로 각자 서명 → CO가 `root-sign.token`의 `signatures` 배열에 두 사람의 항목을 넣는다 | 서로 다른 KC 2명이 서명했고 토큰이 만료되지 않았다 | ☐ | |
| 5.5.9 | 진행자 → CO | HSM으로 서명 (**한 번만**) | 진행자가 `$ sha256sum evidence/root-tbs.der`로 5.5.5 값과 같은지 보고 "서명 실행"이라고 말한다 → `aws-cloudhsm > crypto sign ecdsa --key-filter attr.label=platform-root attr.class=private-key --hash-function sha384 --data-type raw --data-path evidence/root-tbs.der --approval root-sign.token` | 성공 응답과 서명값이 나온다 → `evidence/5.5.9-sign.json`. 쓴 토큰도 `evidence/`에 보관 | ☐ | |
| 5.5.10 | CO / 진행자 | 인증서 조립하고 검사 | `$ {{tool}} assemble --tbs evidence/root-tbs.der --sig evidence/5.5.9-sign.json --out evidence/root.der` → `openssl x509 -inform DER -in evidence/root.der -out evidence/root.pem` → `openssl verify -check_ss_sig -CAfile evidence/root.pem evidence/root.pem` → `{{tool}} compare --tbs evidence/root-tbs.der --cert evidence/root.der --pubkey evidence/root-pub.pem` → `{{verifier}} root evidence/root.der` | `OK`, 본문·공개키 일치, `ALL CHECKS PASSED`(SKI 있음, AKI=SKI, AIA·CDP 없음 포함) → `evidence/5.5.10-verify.txt`. **실패하면 멈춤 규칙 3** | ☐ | |
| 5.5.11 | CO / IW | Root 지문 기록하고 로그아웃 | `$ openssl x509 -in evidence/root.pem -noout -fingerprint -sha256` → `aws-cloudhsm > logout` | 지문을 부록 C에 적었고 로그아웃 성공 | ☐ | |

### 5.6 C2PA ICA 키, CSR, 인증서 만들기

> 키를 만들고 CSR에 서명하는 일은 **C2PA 클러스터**에서 한다(5.6.1–5.6.11). 인증서 서명은 **Root 클러스터**로 옮겨 Root 키로 한다(5.6.12–5.6.18).

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.6.1 | CO | ICA 키 소유 계정 로그인 (C2PA) | `$ cloudhsm-cli interactive --cluster-id {{C2PA}}` → `aws-cloudhsm > login --username cu_c2pa --role crypto-user` | 로그인 성공 | ☐ | |
| 5.6.2 | CO | ICA 키 만들기 | 5.5.2와 같은 명령, label만 `c2pa-ica`로 바꾼다 | 성공 → `evidence/5.6.2-generate.json` | ☐ | |
| 5.6.3 | CO / 진행자 / IW | 키가 의도대로 만들어졌는지 확인 (다인 통제 증거) | `aws-cloudhsm > key list --filter attr.label=c2pa-ica attr.class=private-key --verbose` | 5.5.3과 같은 기준 → `evidence/5.6.3-key.json` | ☐ | |
| 5.6.4 | CO / IW | 공개키를 꺼내고 지문 기록 | `aws-cloudhsm > key generate-file --encoding pem --path evidence/ica-pub.pem --filter attr.label=c2pa-ica attr.class=public-key` → `$ openssl pkey -pubin -in evidence/ica-pub.pem -outform DER \| sha256sum` | P-384이고 Root 지문과 다르다. 부록 C에 적는다 | ☐ | |
| 5.6.5 | CO / 진행자 | 서명할 CSR 본문 만들기 | `$ {{tool}} cri first --config first.conf --pubkey evidence/ica-pub.pem --out evidence/ica-cri.der` → `{{tool}} show evidence/ica-cri.der > evidence/ica-cri.txt` → `sha256sum evidence/ica-cri.der` | Subject·공개키·요청 확장(Basic Constraints, Key Usage, Certificate Policies)이 부록 A와 같다. 입회자가 해시를 적는다 | ☐ | |
| 5.6.6 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 `ica-cri.txt` 화면과 해시를 본다 | 승인자 이름과 해시를 수행 기록에 적는다 | ☐ | |
| 5.6.7 | CO | ICA 키 사용 토큰 받기 | `aws-cloudhsm > quorum token-sign generate --service key-usage --token ica-csr.token --filter attr.label=c2pa-ica attr.class=private-key` | 토큰 파일이 생긴다 | ☐ | |
| 5.6.8 | KC 2명 | 토큰 승인 | 5.5.8과 같다 | 서로 다른 KC 2명 | ☐ | |
| 5.6.9 | 진행자 → CO | HSM으로 CSR 서명 (**한 번만**) | 진행자가 해시를 다시 보고 "서명 실행" → `aws-cloudhsm > crypto sign ecdsa --key-filter attr.label=c2pa-ica attr.class=private-key --hash-function sha384 --data-type raw --data-path evidence/ica-cri.der --approval ica-csr.token` | 성공 → `evidence/5.6.9-sign.json`, 토큰 보관 | ☐ | |
| 5.6.10 | CO / 진행자 | CSR 조립하고 검사 | `$ {{tool}} assemble --tbs evidence/ica-cri.der --sig evidence/5.6.9-sign.json --out evidence/ica.csr.der` → `openssl req -inform DER -in evidence/ica.csr.der -verify -noout` → `{{tool}} compare --tbs evidence/ica-cri.der --csr evidence/ica.csr.der --pubkey evidence/ica-pub.pem` → `{{verifier}} csr evidence/ica.csr.der` | `verify OK`, 일치, CSR schema 통과 → `evidence/5.6.10-verify.txt`. **실패하면 멈춤 규칙 3** | ☐ | |
| 5.6.11 | IW / CO | CSR 해시 기록하고 로그아웃 | `$ sha256sum evidence/ica.csr.der` → `aws-cloudhsm > logout` | 입회자가 해시를 수행 기록에 적는다 | ☐ | |
| 5.6.12 | CO | Root 클러스터로 옮겨 로그인 | `$ cloudhsm-cli interactive --cluster-id {{ROOT}}` → `aws-cloudhsm > login --username cu_root --role crypto-user` | 로그인 성공 | ☐ | |
| 5.6.13 | CO / 진행자 | 서명할 ICA 인증서 본문 만들기 | `$ sha256sum evidence/ica.csr.der` (5.6.11과 같은지 확인) → `{{tool}} tbs first --config first.conf --csr evidence/ica.csr.der --issuer evidence/root.der --out evidence/ica-tbs.der` → `{{tool}} show evidence/ica-tbs.der > evidence/ica-tbs.txt` → `sha256sum evidence/ica-tbs.der` | Issuer가 Root Subject와 같고, AKI가 Root SKI와 같고, 공개키가 CSR과 같다. AIA에 OCSP·caIssuers가 있고 **CDP는 없다**. 기간·serial이 부록 A와 같다. 입회자가 해시를 적는다 | ☐ | |
| 5.6.14 | KC 2명 / IW | 본문 확인 | 승인할 KC 2명이 `ica-tbs.txt` 화면과 해시를 본다 | 승인자 이름과 해시를 수행 기록에 적는다 | ☐ | |
| 5.6.15 | CO | Root 키 사용 토큰 받기 | `aws-cloudhsm > quorum token-sign generate --service key-usage --token ica-issue.token --filter attr.label=platform-root attr.class=private-key` | 토큰 파일이 생긴다 | ☐ | |
| 5.6.16 | KC 2명 | 토큰 승인 | 5.5.8과 같다 | 서로 다른 KC 2명 | ☐ | |
| 5.6.17 | 진행자 → CO | HSM으로 ICA 인증서 서명 (**한 번만**) | 진행자가 해시를 다시 보고 "서명 실행" → `aws-cloudhsm > crypto sign ecdsa --key-filter attr.label=platform-root attr.class=private-key --hash-function sha384 --data-type raw --data-path evidence/ica-tbs.der --approval ica-issue.token` | 성공 → `evidence/5.6.17-sign.json`, 토큰 보관 | ☐ | |
| 5.6.18 | CO | 인증서 조립하고 로그아웃 | `$ {{tool}} assemble --tbs evidence/ica-tbs.der --sig evidence/5.6.17-sign.json --out evidence/ica.der` → `openssl x509 -inform DER -in evidence/ica.der -out evidence/ica.pem` → `aws-cloudhsm > logout` | 파일이 생기고 로그아웃 성공 | ☐ | |
| 5.6.19 | 진행자 | ICA 인증서 검사 | `$ openssl verify -CAfile evidence/root.pem evidence/ica.pem` → `{{tool}} compare --tbs evidence/ica-tbs.der --cert evidence/ica.der --csr evidence/ica.csr.der --pubkey evidence/ica-pub.pem` → `{{verifier}} first evidence/ica.der` | `OK`, 본문·CSR·HSM 공개키 일치, `ALL CHECKS PASSED` → `evidence/5.6.19-verify.txt`. **실패하면 멈춤 규칙 3** | ☐ | |
| 5.6.20 | CO / IW | ICA 지문 기록 | `$ openssl x509 -in evidence/ica.pem -noout -fingerprint -sha256` | 부록 C에 적는다 | ☐ | |

### 5.7 결과 종합 확인

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.7.1 | 진행자 | 검사 결과 모아 보기 | 5.5.10, 5.6.10, 5.6.19 출력 확인 | 셋 다 통과 | ☐ | |
| 5.7.2 | IAM-Op / IW | 서명 승인 기록 확인 | CloudTrail에서 5.5.8·5.6.8·5.6.16의 `kms:Sign` 조회 → `evidence/5.7.2-trail.json` | 서명 3번 각각에 서로 다른 KC 2명의 기록이 있다 | ☐ | |
| 5.7.3 | IW | 검사 출력에 확인 서명 | 인쇄본에 서명 | 서명 완료 | ☐ | |

### 5.8 백업하고 HSM 잠그기

> 키가 백업에 들어갔는지 확인하고, 다른 리전에 사본을 만든 뒤, HSM을 지워 오프라인으로 둔다. **5.8.2가 확인되지 않으면 5.8.3부터는 하지 않는다.** 8장에 기록하고, 나중에 별도 입회 하에 이 표를 다시 수행한다.

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.8.1 | IAM-Op | 백업 목록 보기 | `[IAM-Op] $ aws cloudhsmv2 describe-backups --filters clusterIds={{ROOT}},{{C2PA}} > evidence/5.8.1-backups.json` | 목록이 나온다 | ☐ | |
| 5.8.2 | 진행자 / IW | 키를 만든 뒤의 백업인지 확인 | 각 클러스터의 최신 백업 `CreateTimestamp`를 5.6.20 시각과 비교 | 두 클러스터 모두 `READY`이고, 5.6.20 이후에 만들어졌다 | ☐ | |
| 5.8.3 | IAM-Op | 백업이 만료되지 않게 설정 | `[IAM-Op] $ aws cloudhsmv2 modify-backup-attributes --backup-id <ID> --never-expires` (두 백업 모두) | `NeverExpires: true` | ☐ | |
| 5.8.4 | IAM-Op | 다른 리전에 사본 만들기 | `[IAM-Op] $ aws cloudhsmv2 copy-backup-to-region --destination-region {{DR_REGION}} --backup-id <ID>` (두 백업 모두) → 대상 리전에서 `READY` 확인, 사본에도 5.8.3 적용 → `evidence/5.8.4-offsite.json` | 사본 2개가 `READY`, `NeverExpires: true` | ☐ | |
| 5.8.5 | IAM-Op | Root 클러스터 HSM 지우기 | `[IAM-Op] $ aws cloudhsmv2 delete-hsm --cluster-id {{ROOT}} --hsm-id <HSM>` | 삭제됨. 클러스터와 백업은 남아 있다 | ☐ | |
| 5.8.6 | IAM-Op | C2PA 클러스터 HSM 지우기 | `[IAM-Op] $ aws cloudhsmv2 delete-hsm --cluster-id {{C2PA}} --hsm-id <HSM>` | 삭제됨. 클러스터와 백업은 남아 있다 | ☐ | |
| 5.8.7 | IAM-Op / IW | HSM이 모두 지워졌는지 확인 | describe-clusters (두 클러스터) → `evidence/5.8.7-clusters.json` | 둘 다 `Hsms: []` | ☐ | |

### 5.9 마무리

| 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |
|---|---|---|---|---|---|---|
| 5.9.1 | IAM-Op | HSM 감사 로그 확인 | CloudWatch Logs `/aws/cloudhsm/<cluster>`에서 행사 시간대 조회 → `evidence/5.9.1-hsm-audit.json`. 보존 기간 `{{기간}}`과 S3 Object Lock 내보내기 설정 확인 | 키 생성·서명·계정 변경·로그인 기록이 있다 | ☐ | |
| 5.9.2 | IAM-Op | AWS 작업 기록 확인 | CloudTrail에서 InitializeCluster, `kms:Sign`, CopyBackupToRegion, DeleteHsm 조회 → `evidence/5.9.2-trail.json` | 기록이 있다 | ☐ | |
| 5.9.3 | CO, KC1·KC2 | 소유 증명 키 보관 후 원본 지우기 | 암호화된 `hsm-owner.key`를 봉인 매체 2개에 복사하고 해시 대조 → `$ shred -u hsm-owner.key` | 매체 2개 봉인, 원본 삭제 | ☐ | |
| 5.9.4 | CO | 작업 파일 정리 | 토큰·서명 작업 파일 중 `evidence/`에 같은 파일이 있는 것(`cmp`로 확인)만 지운다 | `evidence/` 밖에 토큰이 남아 있지 않다 | ☐ | |
| 5.9.5 | CO / 진행자 | 화면 기록 끝내고 해시 남기기 | `$ exit` → `sha256sum evidence/* > evidence-sha256.txt` | 세션 로그 해시를 부록 C에 적는다 | ☐ | |
| 5.9.6 | 진행자 / IW | 봉투 확인하고 금고에 넣기 | 3.4의 봉투 번호와 실제 봉투를 대조, 금고 입고 | 번호가 모두 맞다 | ☐ | |

## 6. 행사 후 보관과 접근 통제

| 대상 | 통제 |
|---|---|
| KC KMS 키 | 해당 KC만 `kms:Sign` 가능(MFA 조건), 키 관리자의 Sign 거부, 삭제 대기 `{{7일 이상}}`, `kms:Sign`이 생기면 알림 |
| 비밀번호 봉투 | 봉투 번호 관리, 이중 통제 금고, 출입·개봉 대장 |
| 클러스터 소유 증명 키 | 암호화된 봉인 매체 2개, 이중 통제 금고 |
| CloudHSM 백업 (원본·사본) | 만료 없음. RestoreBackup, CopyBackupToRegion, DeleteBackup, CreateHsm, DeleteCluster는 승인 절차를 거친 IAM 역할만 할 수 있다. 복원한 클러스터도 같은 계정·승인 규칙으로 보호된다(4.6 ⑥) |
| CA 키를 다시 쓸 때 (OCSP 응답자 인증서 발급 등) | IAM-Op의 HSM 생성 + CO 로그인 + KC 2명 승인 + 입회가 모두 필요하다. 별도 행사 Script로 한다 |
| 세션 로그·증거·서명본 | 해시 목록 보관, S3 Object Lock, 인증서 만료 후 최소 1년 보존 |
| 인증서 (Root, ICA) | 공개 저장소에 게시 |

## 7. 참가자 확인 서명

서명 대상: 이 Script v`{{버전}}` (SHA-256 `{{해시}}`), 수행 기록, 증거 해시 목록 `evidence-sha256.txt` (SHA-256 `{{현장}}`).

확인 문구: "본인은 아래에 적은 본인의 실제 수행·관찰 범위에서, 이 행사가 위 Script대로 수행되었는지 확인하였습니다. 일탈, 수행하지 않은 일, 관찰하지 못한 부분은 8장에 기록되었습니다."

| 역할 | 성명 | 내가 수행·관찰한 범위 | 준수 여부 (준수 / 일탈 있음: 8장 # / 확인 불가) | 서명 | 일시 |
|---|---|---|---|---|---|
| 진행자 | | | | | |
| 실행자 | | | | | |
| AWS 담당 | | | | | |
| 승인자 KC1 | | | | | |
| 승인자 KC2 | | | | | |
| 승인자 KC3 | | | | | |
| 입회자 | | | | | |

## 8. 편차 기록

> 단계 칸에는 5.x.y 번호만 적는다. 다시 입력한 일, 다시 시도한 일, 중단한 일도 모두 적는다.

| # | 시각 | 단계(5.x.y) | 무슨 일이 있었나 | 어떻게 했나 | IW |
|---|---|---|---|---|---|
| | | | | | |

---

## 부록 A. 인증서·CSR 설정

`root.conf`, `first.conf`는 아래 값을 `{{tool}}` 입력 형식으로 옮긴 파일이다. 리허설(4.6 ④)에서 공식 schema를 통과한 해시본만 쓴다.

| 항목 | Root | C2PA ICA |
|---|---|---|
| 키·서명 | P-384, ECDSA-with-SHA384 | 별도 P-384 키. CSR은 ICA 키로, 인증서는 Root 키로 ECDSA-with-SHA384 서명 |
| 형식 | X.509 v3, DER | X.509 v3, DER |
| Subject | `C=KR, O={{ORG}}, CN=Samsung Cloud Service Platform Root CA G1` | `C=KR, O={{ORG}}, CN=Samsung C2PA Intermediate CA G1` |
| Issuer | Subject와 같음 | Root Subject |
| 유효기간 | 20년. notBefore `{{UTC}}` / notAfter `{{UTC}}` | 5년. notBefore `{{UTC}}` / notAfter `{{UTC}}` (Root 만료 전) |
| Serial | CSPRNG 159-bit 양수, 0 제외, 20 octets 이하 | 같음 |
| SKI | non-critical, RFC 5280 Method 1 (SHA-1) | 같음 |
| AKI | non-critical, keyIdentifier = 자기 SKI | non-critical, keyIdentifier = Root SKI |
| Key Usage | critical, `keyCertSign`·`cRLSign`만 | 같음 |
| Basic Constraints | critical, `cA=true`, `pathLenConstraint=2` | critical, `cA=true`, `pathLenConstraint=1` |
| Certificate Policies | 넣지 않음 | non-critical, `1.3.6.1.4.1.62558.1.1` |
| AIA | 넣지 않음 | non-critical, OCSP `{{http://OCSP_URL}}`, caIssuers `{{http://ROOT_CERT_URL}}` |
| CDP | 넣지 않음 | **넣지 않음** (공식 First schema `allOf/5`가 `oneOf`라서 AIA와 함께 넣으면 실패한다) |
| EKU·기타 확장 | 넣지 않음 | 넣지 않음 |

**ICA CSR:** PKCS #10 DER, version 0. Subject와 공개키는 위 값과 같아야 한다. `extensionRequest`에는 Basic Constraints(critical, cA, pathLen 1), Key Usage(critical, keyCertSign·cRLSign), Certificate Policies(non-critical, C2PA OID)를 넣는다. AIA·CDP·SKI·AKI는 CSR에 넣지 않는다. 인증서를 발급할 때 CSR의 확장을 그대로 복사하지 않고 위 표의 값으로 만든다.

## 부록 B. 도구

| 명령 | 하는 일 | 요구 사항 |
|---|---|---|
| `{{tool}} tbs root\|first` | 설정·공개키(·CSR·Issuer 인증서)로 인증서 본문(TBSCertificate DER)을 만든다 | 부록 A 값만 사용, serial은 CSPRNG |
| `{{tool}} cri first` | CSR 본문(CertificationRequestInfo DER)을 만든다 | `extensionRequest` 포함 |
| `{{tool}} show` | 본문을 사람이 읽을 수 있게 보여 준다 | 모든 필드·확장·critical 표시 |
| `{{tool}} assemble` | 본문과 `crypto sign` 응답을 합쳐 인증서/CSR DER을 만든다 | 서명값을 DER ECDSA-Sig-Value로 변환, 조립 후 서명 자체 검증 |
| `{{tool}} compare` | 본문·인증서·CSR·공개키가 서로 같은지 비교한다 | 바이트 단위 비교 |
| `{{verifier}} root\|first\|csr` | 공식 schema와 의미를 검사한다 | commit `2466172`의 Root·First 인증서 schema, First CSR schema. SKI Method 1 재계산, AKI–Issuer SKI 대응, Issuer–Subject 대응, 서명 검증 |

두 도구는 행사 전에 코드 리뷰와 서명된 빌드를 거치고 3.6에 해시를 적는다. (CP *Computer Security Controls* 1, *Change Management*)

## 부록 C. 지문 기록표 (SHA-256, 대문자, 구분자 없이)

| 대상 | SHA-256 | 기록자 | IW |
|---|---|---|---|
| hsm-owner.crt (5.2.3) | | | |
| KC1 / KC2 / KC3 KMS 공개키 — 사전 기록 | | | |
| KC1 / KC2 / KC3 KMS 공개키 — 5.4.4 | | | |
| Root 공개키 (5.5.4) | | | |
| Root 인증서 (5.5.11) | | | |
| C2PA ICA 공개키 (5.6.4) | | | |
| C2PA ICA CSR (5.6.11) | | | |
| C2PA ICA 인증서 (5.6.20) | | | |
| 세션 로그 / `evidence-sha256.txt` (5.9.5) | | | |

## 부록 D. 승인 전 확정 목록

아래가 모두 정해져 본문에 반영되기 전에는 이 Script를 승인하지 않는다. 행사 당일 4.2에서 0건인지 확인한다.

| # | 정할 것 | 정하는 방법 | 반영 위치 |
|---|---|---|---|
| D1 | `{{tool}}`, `{{verifier}}` 구현·리뷰·서명 빌드 | 개발·리뷰, 4.6 ④⑤ | 3.6, 부록 B |
| D2 | ~~등록 토큰 서비스명과 KMS 서명 방식~~ **해결:** AWS 문서상 `--service registration`, 서명 대상은 SHA-256 해시값(→ KMS `DIGEST` + `RSASSA_PKCS1_V1_5_SHA_256`). 리허설 4.6 ①에서 실제 동작만 확인 | AWS 문서 | 5.4.5–5.4.6 |
| D3 | ~~key-usage 토큰의 서명 형식~~ **해결:** 승인자는 토큰의 `token` 값에 서명하고, `signatures` 배열에 `{username, role, signature}` 항목을 추가한다 ([AWS 문서](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html)) | AWS 문서 | 5.5.8, 부록 E |
| D4 | **일부 해결:** AWS 문서상 관리 Quorum(`key-management`)은 key share·unshare·set-attribute·wrap·unwrap에 적용되고 **key delete는 포함되지 않는다**. 리허설 4.6 ⑦에서 공유·속성 변경 거부를 확인하고, 키 소유 CU가 혼자 키를 지울 수 있다는 점을 위험으로 승인받는다(README 남은 위험) | 4.6 ⑦, 결정 | 5.5.2, README |
| D5 | ~~Quorum 값을 지정할 서비스~~ **해결:** admin 서비스는 `user`, `quorum`, `cluster`(hsm2m.medium 전용) 세 가지. 모두 2로 설정하고 `quorum`을 마지막에 설정한다 | AWS 문서 | 5.4.10 |
| D6 | 토큰 전달 경로 `{{TOKEN_XFER}}` | 설계·리허설 | 5.0, 부록 E |
| D7 | 행사용 EC2 접속 경로·MFA, 반입 단말 목록 | 보안 검토 | 3.5 |
| D8 | ICA의 OCSP·caIssuers URL, OCSP 응답자 인증서를 발급할 후속 Root 행사 일정 | 운영 결정 | 부록 A, 6장 |
| D9 | `{{ORG}}`, notBefore/notAfter, 사본 리전, 로그 보존 기간 | 결정 | 부록 A, 3.1, 5.9.1 |
| D10 | 참가자 실명, 입회자 독립성 근거, 신뢰 역할 기록 | 인사·보안 확인 | 2장, 4.3 |
| D11 | 키를 만든 뒤 자동 백업이 언제 만들어지는지 | 4.6 ⑥에서 관찰 | 5.8.2 |
| D12 | FIPS 140-3 Level 3 모듈에 CP *Key Storage*("FIPS 140-2 Level 2 or higher")를 어떻게 적용할지 | C2PA 측 확인 | 3.1 |
| D13 | 키 생성 다인 통제 방식에 대한 C2PA 답변 원문을 확보하고, 답변이 CP *Key Pair Generation by CAs* 3.2를 기준으로 한 것인지와 키 종류(Root·ICA)를 한정하지 않았는지 확인한다 | C2PA 서면 답변 | 1장, 2장 |

## 부록 E. 승인자 안내 (KC용)

토큰 승인(5.5.8, 5.6.8, 5.6.16)을 할 때 승인자가 보는 순서다.

| 순서 | 할 일 | 명령 | 확인 |
|---|---|---|---|
| 1 | 본문을 먼저 본다 | 진행자가 보여 주는 `*-tbs.txt` 또는 `*-cri.txt` 화면과 해시 | 무엇에 서명하는지 이해했다. 이해가 안 되면 승인하지 않아도 된다 |
| 2 | 토큰 파일을 받는다 | `{{TOKEN_XFER}}` → `[KC 단말] $ sha256sum <토큰 파일>` | CO가 알려 준 해시와 같다 |
| 3 | 토큰이 가리키는 키를 확인한다 | 토큰 파일 내용 확인 | 진행자가 말한 키(`platform-root` 또는 `c2pa-ica`)다 |
| 4 | 자기 단말에서 서명한다 | `[KC 단말] $ echo -n '<토큰의 token 값>' \| base64 -d > token.bin` → `aws kms sign --key-id alias/c2pa-quorum-kcN --message fileb://token.bin --message-type DIGEST --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 --output text --query Signature > token.sig.b64` | MFA 로그인 후 서명값이 나온다 |
| 4-1 | 서명 항목을 만든다 | `{"username": "cu_kcN", "role": "crypto-user", "signature": "<token.sig.b64 내용>"}` | CO가 이 항목을 토큰 파일의 `signatures` 배열에 넣는다 |
| 5 | 서명값만 돌려준다 | `{{TOKEN_XFER}}` | 비밀번호, MFA 코드, 자격 증명은 절대 넘기지 않는다 |
| 6 | 만료되면 처음부터 | — | 토큰은 기본 10분 뒤 만료된다. 만료되면 CO가 새 토큰을 만들고 1번부터 다시 한다 |

[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#certificate-policy

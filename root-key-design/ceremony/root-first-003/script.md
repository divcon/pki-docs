# Samsung C2PA Key Generation Ceremony Script (Template)

- 템플릿 버전: v0.1

  
- 문서 번호: KGC-C2PA-2026-001
- Ceremony 목적: \*\*Samsung Cloud Service Platform Root CA G1\*\* 및 \*\*Samsung C2PA Intermediate CA G1\*\* 신규 생성
- 본 Script의 범위: 위 두 CA의 키 생성, 인증서 발급, 검증, 보관. 그 외 CA 및 운영 인증서는 본 Script 범위 밖
- 기준: C2PA Certificate Policy v0.2 §6.1.1, §6.2.1, §6.3, §7.1.1



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
   - 5.8 두 클러스터 오프라인화
   - 5.9 백업·로그 보존 확인 및 정리
6. 사후 보관 및 접근 통제
7. 참가자 서명
8. 편차 기록 (단계 열에는 5.x.y 형식만 기재)
   - 부록 A OpenSSL 설정 / 부록 B 검증 스크립트 / 부록 C Fingerprint 기록표
   ---
   ## 1. 승인 및 기본 정보

   | 항목 | 내용 |

   |---|---|

   | 일시 | 2026-10-15 `<HH:MM>` KST |

   | 장소 | `<건물/층/룸>` |

   | 승인자(경영진) | 성명 / 직책 / 서명 / 일자 |

   | 승인자(보안책임자) | 성명 / 직책 / 서명 / 일자 |

   | Script 승인 버전 | v`<x>` — Ceremony 중 변경 불가 |
   ## 2. 역할 및 참가자

   | 역할 | 성명 | 소속 | 허용 행위 | 금지 행위 |

   |---|---|---|---|---|

   | Ceremony Administrator (CA-Admin) | | | 단계 호명, 체크 | CLI/AWS 조작 |

   | Crypto Officer (CO) | | | CloudHSM CLI 입력 | Custodian/Witness 겸임, KMS Quorum 키 사용 |

   | AWS IAM Operator (IAM-Op) | | | CloudHSM/KMS 리소스 생성·설정 API | CO 겸임, kms:Sign |

   | Key Custodian #1\~#3 (KC) | | | 자기 KMS 키로 Quorum 토큰 서명 | CLI 입력, CloudHSM 관리 API |

   | Independent Witness (IW) | | | 관찰, 확인 서명, 최종 봉인 | 모든 조작 |

   Quorum: Root 클러스터 `<M_root>`-of-`<N_root>` / C2PA 클러스터 `<M>`-of-`<N>`. Custodian 명단이 클러스터별로 다를 경우 2장에 각각 기재.
   ## 3. 자재 및 HSM/KMS 명세
   ### 3.1 CloudHSM

   | 항목 | Root 클러스터 (Platform Root 키) | C2PA 클러스터 (C2PA ICA 키) |

   |---|---|---|

   | 계정 / 리전 | | |

   | Cluster ID / HSM ID | (4.9 기록) | (4.9 기록) |

   | HSM Type / \*\*Mode\*\* | hsm2m.medium / \*\*FIPS\*\* | hsm2m.medium / \*\*FIPS\*\* |

   | Quorum | `<M_root>`-of-`<N_root>` (예: 3-of-5) | `<M>`-of-`<N>` (예: 2-of-3) |

   | CMVP 인증서 번호 | 부록 A | 부록 A |

   | Client SDK 버전 | | |

   &gt; Platform Root는 플랫폼 공용 루트이므로 C2PA ICA와 클러스터를 분리한다.
   ### 3.2 KMS (Custodian Quorum 키)

   | Custodian | KMS Key ARN | KeySpec | 허용 IAM Principal | MFA |

   |---|---|---|---|---|

   | KC1 | `arn:aws:kms:...:key/...` | RSA\_2048 SIGN\_VERIFY | `<KC1 user/role>` | 필수 |

   | KC2 | | | | |

   | KC3 | | | | |
   ### 3.3 소프트웨어

   | 항목 | 버전 | SHA-256 |

   |---|---|---|

   | CloudHSM CLI | | |

   | OpenSSL / PKCS#11 Provider | | |

   | AWS CLI | | |

   | verify\_[profile.py](http://profile.py) | | |
   ## 4. 사전 조건 확인

   | # | 항목 | 확인자 | ☐ | 시각 |

   |---|---|---|---|---|

   | 4.1 | 1장 승인 서명 완료 | CA-Admin | ☐ | |

   | 4.2 | 전원 출석·신분 확인, 무선기기 반입 금지 | IW | ☐ | |

   | 4.3 | 룸 녹화 시작 (`__:__`) | CA-Admin | ☐ | |

   | 4.4 | 터미널 세션 녹화 시작 `script -a ceremony_20261015.log` | CO | ☐ | |

   | 4.5 | KMS 키 3개 생성·키정책 적용 완료, 공개키 PEM 추출 완료 (사전 작업, 부록 C fingerprint 대조) | IAM-Op/IW | ☐ | |

   | 4.6 | 리허설 결과서 확인(Quorum 토큰 서명 형식 호환 PASS) | CA-Admin | ☐ | |

   | 4.7 | 부록 A OpenSSL 설정 파일 해시 대조 | IW | ☐ | |

   | 4.8 | \*\*사전 프로비저닝(IAM-Op, 세리머니 전 완료)\*\*: Root/C2PA 클러스터 `create-cluster --mode FIPS`, `create-hsm` 각 1개, Private Subnet·보안그룹, 관리 단말에 CLI·PKCS#11 설치. 초기화(initialize)·활성화(activate)는 수행하지 않음 | IAM-Op | ☐ | |

   | 4.9 | 개시 시 검증: `aws cloudhsmv2 describe-clusters --filters clusterIds=<ROOT>,<C2PA>` → 각각 \*\*`Mode: FIPS`\*\*, `State: UNINITIALIZED`, HSM `State: ACTIVE`. Cluster ID·HSM ID를 3.1에 기록, 출력 인쇄 첨부 | IAM-Op / IW | ☐ | |



 

 ## 5. 실행 단계

 

 ### 5.1 환경 격리 확인

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.1.1 | CO | 외부 인터넷 차단 확인 | `curl -m 5 [https://example.com](https://example.com`)` | 실패(외부 차단) | ☐ | |

 | 5.1.2 | CO | AWS 자격 역할 확인 | `aws sts get-caller-identity` | Ceremony 전용 역할 ARN | ☐ | |

 | 5.1.3 | CO | 단말 시각 확인 | `date -u` | UTC ±1분 | ☐ | |

 | 5.1.4 | CO | 도구 바이너리 해시 대조 | `sha256sum <cloudhsm-cli> <openssl> verify_[profile.py](http://profile.py)` | 3.3 일치 | ☐ | |

 

 ### 5.2 CloudHSM 클러스터 소유 증명 인증서 생성

 

 &gt; AWS CloudHSM 초기화(`initialize-cluster`)에 필요한, 클러스터 CSR 서명용 고객 자체서명 인증서. C2PA 인증서 체인과 무관하며 Trust List·manifest에 포함되지 않는다. 개인키는 CA 키에 준하여 보호한다.

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.2.1 | CO | 소유 증명 키 생성 | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-384 -aes256 -out hsm-owner.key` | 패스프레이즈를 KC1·KC2가 분할 입력 | ☐ | |

 | 5.2.2 | CO | 소유 증명 인증서 생성 | `openssl req -new -x509 -days 3652 -key hsm-owner.key -subj "/C=KR/O=<Org>/CN=<Org> CloudHSM Cluster Owner" -out hsm-owner.crt` | PEM 생성 | ☐ | |

 | 5.2.3 | CO | 소유 증명 fingerprint 기록 | `openssl x509 -in hsm-owner.crt -noout -fingerprint -sha256` | 부록 C 기록 | ☐ | |

 

 ### 5.3 클러스터 초기화 (Root → C2PA 순으로 각각 수행)

 

 &gt; 클러스터·HSM 생성은 4.8에서 사전 완료, 4.9에서 검증됨. 아래 행을 `<CLUSTER>`=ROOT로 먼저 수행하고 Root 열에 체크, 이어 `<CLUSTER>`=C2PA로 수행하고 C2PA 열에 체크한다. hsm-owner 인증서는 두 클러스터에 동일하게 사용.

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |

 |---|---|---|---|---|---|---|

 | 5.3.1 | IAM-Op | 클러스터 CSR 추출 | `aws cloudhsmv2 describe-clusters --filters clusterIds=<CLUSTER> --query 'Clusters[0].Certificates.ClusterCsr' --output text > <cluster>.csr` | CSR 파일 | ☐ | ☐ |

 | 5.3.2 | IW | CSR 내용 확인 | `openssl req -in <cluster>.csr -noout -subject` → Cluster ID 포함 | 일치 | ☐ | ☐ |

 | 5.3.3 | CO | CSR 서명(봉인) | `openssl x509 -req -days 3652 -in <cluster>.csr -CA hsm-owner.crt -CAkey hsm-owner.key -CAcreateserial -out <cluster>-signed.crt` | 성공 | ☐ | ☐ |

 | 5.3.4 | IAM-Op | 클러스터 초기화 | `aws cloudhsmv2 initialize-cluster --cluster-id <CLUSTER> --signed-cert file://<cluster>-signed.crt --trust-anchor file://hsm-owner.crt` | `INITIALIZED` | ☐ | ☐ |

 | 5.3.5 | CO | CLI 연결 확인 | 관리 단말에 hsm-owner.crt 배치, `cloudhsm-cli --cluster-id <CLUSTER>` 연결 | 연결 성공 | ☐ | ☐ |

 

 ### 5.4 활성화 및 KMS 기반 Quorum 설정 (Root → C2PA 순으로 각각 수행)

 

 &gt; 공식 절차: [https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html)

 &gt; 등록 토큰은 **등록 대상 사용자 본인으로 로그인**해 생성·등록한다. Custodian의 승인 능력은 HSM 비밀번호가 아니라 KMS 개인키 보유로 성립한다.

 &gt; 5.3과 같이 Root 클러스터에 대해 전 행을 수행한 뒤 C2PA 클러스터에 대해 반복한다. Quorum 값과 Custodian 명단은 클러스터별로 다를 수 있다(3.1 참조). KMS 공개키 추출(5.4.3)은 1회만.

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | Root ☐ / 시각 | C2PA ☐ / 시각 |

 |---|---|---|---|---|---|---|

 | 5.4.1 | CO | 클러스터 활성화 | `cloudhsm-cli cluster activate` | 초기 admin 비밀번호 설정(KC1·KC2 분할 입력) | ☐ | ☐ |

 | 5.4.2 | CO | Custodian admin 계정 생성 | `user create --username kc1 --role admin` (kc2, kc3 반복; 비밀번호는 각 KC가 직접 입력) | `user list`에 admin 4명 | ☐ | ☐ |

 | 5.4.3 | IAM-Op | KMS 공개키 추출 | `aws kms get-public-key --key-id alias/c2pa-quorum-kc1 --output text --query PublicKey \| base64 -d > kc1.der && openssl rsa -pubin -inform DER -in kc1.der -out kc1_pub.pem` (kc2, kc3 반복) | PEM 3개, SPKI SHA-256 부록 C 대조 | ☐ | ☐ |

 | 5.4.4 | KC1 (CO 단말, 본인 로그인) | KC1 등록 토큰 생성 | `login --username kc1 --role admin` → `quorum token-sign generate --service user --token kc1.token` | 토큰 파일(`tokens[].unsigned` 포함) | ☐ | ☐ |

 | 5.4.5 | KC1 (자기 단말, MFA) | KC1 KMS 토큰 서명 | `unsigned` 값을 받아 `echo -n '<unsigned>' \| base64 -d > kc1.bin` → `aws kms sign --key-id alias/c2pa-quorum-kc1 --message fileb://kc1.bin --message-type DIGEST --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 --output text --query Signature > kc1.sig.b64` | base64 서명. **DIGEST 모드 필수** (RAW 아님) | ☐ | ☐ |

 | 5.4.6 | KC1 (CO 단말, 본인 로그인 유지) | KC1 공개키 등록 | `kc1.sig.b64` 내용을 `kc1.token`의 `tokens[].signed`에 기입 → `user change-quorum token-sign register --public-key kc1_pub.pem --signed-token kc1.token` | `error_code: 0` | ☐ | ☐ |

 | 5.4.7 | KC2, KC3 | KC2·KC3 등록 반복 | 5.4.4~5.4.6 반복 (각자 로그인·서명·등록) | 등록 성공 ×2 | ☐ | ☐ |

 | 5.4.8 | CO | 등록 상태 확인 | `user list` | kc1~kc3에 `quorum: [{strategy: token-sign, status: enabled}]` | ☐ | ☐ |

 | 5.4.9 | CO | Quorum 값 설정 | `quorum token-sign set-quorum-value --service user --value <M>` → `quorum token-sign list-quorum-values` | user=`<M>` (quorum 서비스도 동일 설정 권장) | ☐ | ☐ |

 | 5.4.10 | CO | Crypto User 생성 | `user create --username cu_<cluster> --role crypto-user` (서명용: cu_root / cu_c2pa) 및 `cu_kc1`, `cu_kc2` (키 사용 승인용 CU) | CU 3명 | ☐ | ☐ |

 | 5.4.11 | KC1, KC2 | 승인용 CU 공개키 등록 | cu_kc1/cu_kc2로 로그인해 5.4.4~5.4.6과 동일하게 KMS 공개키 등록 (CU 등록 가능 여부 **[리허설 확인]**) | 등록 성공 | ☐ | ☐ |

 | 5.4.12 | IW | CloudTrail 서명 이벤트 확인 | CloudTrail에서 5.4.5·5.4.7·5.4.11의 `kms:Sign` 이벤트가 서로 다른 principal로 기록됐는지 확인 | 이벤트 존재 | ☐ | ☐ |

 

 &gt; **[템플릿 전용 — 리허설 후 확정 문장으로 교체 또는 삭제]** 5.5·5.6의 키 생성 시 키 사용 Quorum 옵션(`<M>`, 옵션명은 SDK 버전 확인)을 지정하고 cu_kc1/cu_kc2에 `key share`하면 `key-usage(key sign)`에 Quorum이 적용된다. OpenSSL/PKCS#11 경로 서명에 승인 토큰을 공급하는 방법은 **[리허설 확인]**; 불가 시 `cloudhsm-cli crypto sign` 기반으로 서명 단계를 대체하거나 CU 비밀번호 분할로 보완.

 

 ### 5.5 Platform Root CA 키 생성 및 자체서명 인증서

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.5.1 | CO(cu_root) | Root 키 생성·공유 | `cloudhsm-cli key generate-asymmetric-pair ec --curve secp384r1 --public-label platform-root-pub --private-label platform-root-priv --public-attributes verify=true --private-attributes sign=true extractable=false` + 키 사용 Quorum 옵션(`<M>`, 리허설 확정 문법) → `key share --filter attr.label=platform-root-priv --username cu_kc1,cu_kc2` | 생성, 공유 | ☐ | |

 | 5.5.2 | CO | Root 키 속성 확인 | `cloudhsm-cli key list --filter attr.label=platform-root-priv --verbose` | **extractable:false**, sign:true, secp384r1 | ☐ | |

 | 5.5.3 | CO | Root 자체서명 인증서 생성 | `openssl req -new -x509 -provider pkcs11 -key "pkcs11:object=platform-root-priv;type=private" -config root.cnf -extensions root_ca_ext -days 9131 -sha384 -out platform-root.crt` | PEM | ☐ | |

 | 5.5.4 | CO | Root 인증서 내용 확인 | `openssl x509 -in platform-root.crt -noout -text` | `CA:TRUE, pathlen:2`(critical), KU `Certificate Sign, CRL Sign`(critical), AIA/CRL 없음 | ☐ | |

 | 5.5.5 | CO | Root fingerprint 기록 | fingerprint → 부록 C | 기록 | ☐ | |

 

 ### 5.6 C2PA ICA (First Intermediate) 키 생성 및 발급

 

 &gt; 키는 **C2PA 클러스터**에서 생성하고, 인증서는 **Root 클러스터**의 Platform Root 키로 발급한다. 두 클러스터 간에는 CSR과 인증서(공개 정보)만 오간다.

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.6.1 | CO(C2PA 클러스터, cu_c2pa) | ICA 키 생성·공유 | 5.5.1과 동일 (label `c2pa-ica-*`, 키 사용 Quorum `<M>`, cu_kc1/cu_kc2 공유) | 생성, 공유 | ☐ | |

 | 5.6.2 | CO(C2PA) | ICA 키 속성 확인 | `cloudhsm-cli key list --filter attr.label=c2pa-ica-priv --verbose` | **extractable:false**, sign:true, secp384r1 | ☐ | |

 | 5.6.3 | CO(C2PA) | ICA CSR 생성 | `openssl req -new -provider pkcs11 -key "pkcs11:object=c2pa-ica-priv;type=private" -subj "/C=KR/O=<Org>/CN=Samsung C2PA Intermediate CA G1" -sha384 -out c2pa-ica.csr` | CSR | ☐ | |

 | 5.6.4 | IW | ICA CSR 확인 | `openssl req -in c2pa-ica.csr -noout -text` Subject·공개키 육안 확인, CSR SHA-256 기록 | 일치 | ☐ | |

 | 5.6.5 | CO(Root, cu_root 분할 로그인) | Root로 ICA 발급 | `sha256sum c2pa-ica.csr` 5.6.4 값과 대조 후 **Quorum 하에** `openssl x509 -req -provider pkcs11 -CA platform-root.crt -CAkey "pkcs11:object=platform-root-priv;type=private" -in c2pa-ica.csr -extfile ica.cnf -extensions first_ica_ext -days <5479~7305> -sha384 -out c2pa-ica.crt` | 성공 | ☐ | |

 | 5.6.6 | CO | ICA 체인 검증 | `openssl verify -CAfile platform-root.crt c2pa-ica.crt` | OK | ☐ | |

 | 5.6.7 | CO(C2PA) | ICA 인증서 배치·키 대조 | c2pa-ica.crt를 C2PA 클러스터 관리 단말에 배치, 공개키가 c2pa-ica-pub와 일치 확인 (`openssl x509 -pubkey` vs `key list`) | 일치 | ☐ | |

 | 5.6.8 | CO | ICA fingerprint 기록 | fingerprint → 부록 C | 기록 | ☐ | |

 

 ### 5.7 프로파일 자동 검증

 

 | 단계 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|

 | 5.7.1 | Root 프로파일 검증 | `python3 verify_[profile.py](http://profile.py) platform-root.crt root` | ALL CHECKS PASSED | ☐ | |

 | 5.7.2 | ICA 프로파일 검증 | `python3 verify_[profile.py](http://profile.py) c2pa-ica.crt first_ica` | ALL CHECKS PASSED | ☐ | |

 | 5.7.3 | 체인 검증 | `openssl verify -CAfile platform-root.crt c2pa-ica.crt` | OK | ☐ | |

 | 5.7.4 | 검증 결과 서명 | IW 출력 인쇄본 서명 | 서명 | ☐ | |

 

 FAIL 시 8장 기록 후 원인 분석. 키는 유지하고 인증서만 재발급 가능.

 

 ### 5.8 두 클러스터 오프라인화 \[권장, 리허설 검증 후\]

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.8.1 | IAM-Op | 백업 상태 확인 | `aws cloudhsmv2 describe-backups --filters clusterIds=<ROOT>` / `<C2PA>` | 각 최신 백업 `READY` | ☐ | |

 | 5.8.2 | IAM-Op | Root 클러스터 HSM 삭제 | `aws cloudhsmv2 delete-hsm --cluster-id <ROOT> --hsm-id <HSM>` | 삭제, 클러스터·백업 유지 | ☐ | |

 | 5.8.3 | IAM-Op | C2PA 클러스터 HSM 삭제 | `aws cloudhsmv2 delete-hsm --cluster-id <C2PA> --hsm-id <HSM>` | 삭제, 클러스터·백업 유지 | ☐ | |

 | 5.8.4 | IAM-Op | 0-HSM 상태 확인 | describe (둘 다) | `Hsms: []` | ☐ | |

 

 ### 5.9 백업·로그 보존 확인 및 정리

 

 | 단계 | 담당 | 작업 | 명령 | 기대 출력 | ☐ | 시각 |

 |---|---|---|---|---|---|---|

 | 5.9.1 | IAM-Op | 백업 보존 확인 | describe-backups (Root/C2PA) | READY | ☐ | |

 | 5.9.2 | IAM-Op | CloudHSM 감사 로그 확인 | CloudWatch Logs `/aws/cloudhsm/<id>` 이벤트 확인 | 존재 | ☐ | |

 | 5.9.3 | IAM-Op | CloudTrail 이벤트 확인 | CloudTrail: CreateCluster, InitializeCluster, kms:Sign×N, DeleteHsm | 존재 | ☐ | |

 | 5.9.4 | CO | 소유 증명 키 이관·삭제 | hsm-owner.key를 KMS(Import) 또는 봉인 매체로 이관 후 `shred -u hsm-owner.key` | 삭제 | ☐ | |

 | 5.9.5 | CO | 세션 녹화 종료·해시 | 세션 녹화 종료, `sha256sum ceremony_20261015.log` | 부록 C | ☐ | |

 | 5.9.6 | CA-Admin | 룸 녹화 종료·해시 | 룸 녹화 종료(`__:__`), 파일 해시 | 부록 C | ☐ | |

 

 ## 6. 사후 보관 및 접근 통제

 

 | 자산 | 통제 |

 |---|---|

 | Custodian KMS 키 | 키정책: 해당 Custodian만 kms:Sign(MFA), 관리자 Deny, 삭제 7일+ 대기, CloudTrail 알림 |

 | CO/CU 비밀번호 분할본 | KC별 봉인 보관, 금고, 출입 명부 |

 | 클러스터 소유 증명 키 | KMS 또는 봉인 매체, 이중 통제 |

 | CloudHSM 백업(S3) | RestoreBackup/CopyBackupToRegion/DeleteCluster에 승인 절차, SCP 리전 제한 |

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

 

 &gt; 단계 열에는 실행 단계 번호(5.x.y)만 기재. 사소한 재입력·재시도도 모두 기록.

 

 | # | 시각 | 단계(5.x.y) | 상황 | 조치 | IW |

 |---|---|---|---|---|---|

 | | | | | | |

 

 ---

 

 ## 부록 A. OpenSSL 설정

 

 ### root.cnf

 \`\`\`ini

 [ req ]

 distinguished_name = dn

 prompt = no

 [ dn ]

 C = KR

 O = &lt;Org&gt;

 CN = Samsung Cloud Service Platform Root CA G1

 [ root_ca_ext ]

 basicConstraints = critical, CA:TRUE, pathlen:2

 keyUsage = critical, keyCertSign, cRLSign

 subjectKeyIdentifier = hash

 authorityKeyIdentifier = keyid

 \`\`\`

 

 ### ica.cnf

 \`\`\`ini

 [ first_ica_ext ] # C2PA ICA (First Intermediate)

 basicConstraints = critical, CA:TRUE, pathlen:1

 keyUsage = critical, keyCertSign, cRLSign

 certificatePolicies = 1.3.6.1.4.1.62558.1.1

 subjectKeyIdentifier = hash

 authorityKeyIdentifier = keyid

 authorityInfoAccess = OCSP;URI:http://&lt;ocsp&gt;/, caIssuers;URI:http://&lt;pki&gt;/platform-root.crt

 crlDistributionPoints = URI:http://&lt;pki&gt;/c2pa-ica.crl

 \`\`\`

 

 ## 부록 B. 검증 스크립트

 `verify_[profile.py](http://profile.py) <cert.pem> <root|first_ica>` — 별도 파일. 실행 전 SHA-256을 3.3과 대조.

 

 ## 부록 C. Fingerprint 기록표 (SHA-256, 대문자, 구분자 없음 — CP 8.6)

 

 | 대상 | SHA-256 | 기록자 | IW |

 |---|---|---|---|

 | hsm-owner.crt | | | |

 | KC1 / KC2 / KC3 공개키 (SPKI SHA-256) | | | |

 | Samsung Cloud Service Platform Root CA G1 | | | |

 | Samsung C2PA Intermediate CA G1 | | | |

 | 터미널 세션 로그 / 룸 녹화 / verify\_[profile.py](http://profile.py) | | | |
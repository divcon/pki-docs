# Root/First ICA의 2인 통제 대안

2026-09-16 KST 검토 초안. 실계정·HSM에서 검증한 결과가 아닌 문서 기반 설계 비교다. 조직·담당자 지정은 보류하며, 인원수와 역할 조합은 제안이다.

## 1. 달성할 성질

최소한 한 명만으로 Root/First 키를 사용해 인증서를 발급할 수 없어야 한다. 추가 목표는 승인한 발급 내용과 실제 서명 내용의 일치, 권한·quorum 완화와 복구 경로의 우회 방지, 요청에서 결과까지 연결되는 증적이다.

[CP]의 Certificate Issuance, Procedural Controls, CA Key Generation, Private Key Protection 조항은 다인 통제·역할 분리·키 생성 증빙·보호된 백업을 다룬다. 특정 AWS 서비스나 단일 구현 방식을 지정하지는 않는다. 이 요구와 실제 구성·검증 결과를 대조해야 C2PA 충족 근거가 된다.

다음 세 개념을 구분한다.

- **다인 승인:** 서로 다른 사람이 동의하는 업무 절차.
- **HSM quorum:** 여러 사용자의 승인이 있어야 HSM 키 사용 등을 허용하는 기술 통제.
- **비밀 분할/threshold 서명:** 비밀 조각 또는 분산 연산으로 키를 통제하는 별도 방식. HSM quorum을 사용한다고 Root 개인키가 사람들에게 분할되는 것은 아니다. [NIST-KM] §8.1.5.2.1

## 2. 대안 비교

| 대안 | 실제 서명 경로 | 2인 통제의 근거 | 부담·한계 | 판단 |
|---|---|---|---|---|
| A. 작업 단위 ceremony + HSM quorum | 작업 시 시작하는 격리된 EC2 등의 실행 환경에서 CloudHSM CLI 사용 | 사람의 독립 확인과 HSM의 key-usage quorum을 결합 | 작업 일정과 세션 유지 필요. 실행 환경 신뢰와 서명 대상 보호는 별도 필요 | **저빈도 Root/First 작업의 우선안** |
| B. 승인 포털 + HSM quorum 실행기 | 포털에서 준비·검토하고, 승인자가 준비되면 전용 실행기가 CLI 세션을 유지해 서명 | A와 같은 HSM 통제를 자동화하고 발급 내용 승인을 연결 | CLI 세션·토큰 만료·중복 처리·승인자 키 연동 개발 필요 | 작업량 증가 시 확장안 |
| C. 업무 승인 + 일반 SDK 서명 | 승인 DB를 검사한 Lambda/서비스가 PKCS#11 등으로 서명 | 애플리케이션·배포·권한 절차의 다인 통제 | HSM에 단독 서명 가능한 계정이 남으면 승인 서버 우회 위험. SDK에서 CLI 토큰을 쓸 수 있다고 가정할 수 없음 | 현재는 Root/First의 단독 보호 수단으로 권고하지 않음 |

AWS는 CLI의 key-usage quorum을 통해 서명을 제어하는 기능을 문서화한다. 토큰은 한 작업·현재 로그인 세션에 제한되고, 기본 만료 시간도 있으므로 사람의 장시간 결재를 활성 토큰으로 기다리지 않는다. CLI 토큰을 다른 애플리케이션에서 그대로 사용하는 구성은 지원된 것으로 간주하지 않는다. [AWS-QUORUM], [AWS-USE]

일반적인 오프라인 HSM ceremony도 비교 가능한 방식이나, 현재 확정된 CloudHSM 보관 방향을 바꿔야 하므로 본 구현 대안에서는 제외했다. 네트워크 HSM 앞의 실행기를 필요 시에만 가동하는 것은 물리적인 오프라인 Root와 같지 않다.

## 3. 권고안 A의 구체적 흐름

### 준비 단계

1. 요청 ID, issuer 키 지문, CSR·공개키 지문, subject, serial, validity, pathLen, KU/EKU, 정책 OID, AIA를 확인한다. CSR이 제안한 확장을 그대로 복사하지 않는다. [새 키로 교체하는 규칙](operating-model.md#rekey)에 따라 같은 issuer가 이미 발급했던 키인지 확인하고, 동일 키의 새 인증서 발급은 거부한다.
2. 프로파일 버전과 서명 알고리즘을 적용하여 최종 `TBSCertificate` DER를 만든다. 사람이 읽을 표시와 DER digest를 함께 고정한다.
3. 승인 대상에는 요청 ID, DER digest, issuer 키 지문, 작업 종류, 만료 시각, nonce를 포함한다. 인증서 내용을 바꾸면 새 승인을 받도록 한다.
4. 독립된 권한자 2인이 같은 자료를 검토한다. 후보 quorum은 2-of-3이다. 요청자가 승인자에 포함될 수 있는지는 정책 선택이지만, 동일한 사람이 두 계정으로 정족수를 채우지 못하게 해야 한다.

### 실행 단계

1. 승인된 버전의 서명 도구와 작업 패키지만 있는 실행 환경을 시작한다. 평상시에는 Root 키에 접근할 서명 프로세스를 두지 않는다.
2. HSM 사용자·key-use/key-management quorum·키 속성·클러스터 일치 여부를 확인한다. Root 개인키를 실행 환경으로 내보내지 않는다.
3. 참여자가 준비된 뒤 같은 CLI 세션에서 작업 토큰을 만든다. 각 승인자는 별도로 보호한 승인 키로 토큰을 승인한다. 승인 키를 실행기 한 곳에 함께 저장하지 않는다.
4. 실행기는 승인된 발급 자료를 다시 검사하고 quorum과 함께 서명한다. 단일 작업이 끝나면 토큰을 재사용하지 않는다. 중단·만료·재로그인은 새 ceremony 실행으로 처리한다.
5. 결과 인증서를 조립하고 공개키 검증, 원래 DER와 내용 일치, 프로파일 검사, 체인 검증을 수행한다. ECDSA raw/DER 변환, digest 중복 해싱 여부는 구현 시험 대상이다. CLI의 ECDSA 서명도 `--approval`을 제공한다. [AWS-ECDSA]
6. 결과·승인·HSM 및 실행 기록을 원장에 연결한 뒤에만 인증서를 배포한다. 실행 환경을 종료한다.

### 보장 범위

HSM quorum의 공개 문서는 사용 키·서비스에 대한 승인을 설명한다. 이것만으로 승인 토큰이 특정 `TBSCertificate`의 모든 바이트에 암호학적으로 묶인다고 보장할 수 없다. **키 사용에 대한 2인 통제와 특정 인증서 내용에 대한 2인 승인은 별도로 검증**한다.

후자는 변경 통제가 된 실행기, 고정된 작업 패키지, 별도 승인 검증, 실행 환경 관리자 접근 통제로 보강한다. 실행기 전체를 장악한 공격자까지 고려하면 애플리케이션의 digest 검사만으로는 충분하지 않다. HSM의 메시지 결합 승인 지원 여부 또는 더 강한 실행 환경 보호가 확인되기 전에는 그 공격자에 대한 완전한 예방을 주장하지 않는다. 결과 검사에서 잘못된 서명이 발견되면 배포 중단에 그치지 않고 CA 사고로 처리한다.

## 4. 서명 외의 통제

| 경로 | 제안 |
|---|---|
| Root/First 생성 | 2인 검토한 script, 독립 입회/기록, 생성 시 key-use 및 key-management quorum 설정. Trust List 등록 대상은 아래 Program 증빙 기준도 적용. 올바른 quorum 없이 생성한 키는 운영에 쓰지 않음 |
| HSM 사용자 변경 | 관리자 quorum 적용. 사용자 생성·암호/MFA 변경이 우회 통로가 되지 않는지 확인 |
| quorum 정책 변경 | 사용자 관리 quorum뿐 아니라 quorum 값 변경 서비스 자체를 보호. AWS 예제의 `user=2, quorum=1`을 그대로 운영 설정으로 채택하지 않음 |
| 승인 키 등록/재등록 | 동일인이 여러 승인자를 대체할 수 없는지 검증하고 다인 작업으로 관리 |
| 키 공유·속성·반출 | key-management quorum 및 반출 제한. 데이터 서명 키와 백업/관리 권한 분리 |
| 서명 도구 배포·실행 접근 | 서명 도구 변경과 운영 접근을 별도 승인. 하나의 관리자 계정이 검증 로직을 바꾸고 곧바로 서명하지 못하도록 함 |
| CloudHSM 백업 복구 | AWS 관리 API의 복구 승인은 HSM 서명 quorum과 별개. 모든 백업을 목록화하고 원본과 같은 다인 통제로 보호. 공식 계획을 매년 검토하고 복구 접근·구성 변경·복구된 키의 통제를 재검증 |
| 키·HSM·백업 삭제 | 지원 서비스 목록만 보고 모든 삭제가 HSM quorum으로 보호된다고 가정하지 않음. AWS/IAM 및 운영 권한을 별도 검토 |
| 응답자 leaf 키 사용 | 상시 OCSP 서명은 전용 서비스 계정으로 자동화. 응답자 인증서를 발급하는 Root/First 작업에는 동일 ceremony 적용 |

설정 범위의 근거는 [AWS-SETUP], [AWS-ADMIN]이다. CloudHSM 관리 plane, HSM 사용자 plane, 서명 실행기, 승인자의 키 보관, 로그 저장소를 하나의 관리자에게 모두 맡기는 구성을 피한다. 조직명은 나중에 배정한다.

## 5. Lambda 배치

Lambda는 CSR 접수, 요청 내용 검증, 승인 기록 수집, 작업 상태 알림, 발급 결과 배포에 사용할 수 있다. 실제 서명은 A 또는 B의 실행기에 맡기는 안을 우선한다. 이는 Lambda에서 CloudHSM을 사용할 수 없다는 뜻이 아니다. Client SDK 5의 Lambda 지원은 공식적으로 문서화되어 있다. [AWS-LAMBDA]

실제 서명을 Lambda에 넣는 대안을 선택하려면 사람이 승인하는 동안의 토큰·로그인 세션 유지, 타임아웃, 실행 재시도, 승인 키 취급 및 quorum 경로를 검증해야 한다. SDK 연결 성공만으로 2인 통제까지 구현됐다고 판정하지 않는다.

<a id="c2pa-controls"></a>

## 6. C2PA 통제와 권고안의 대응

| CP의 통제 영역 | A안에 포함할 구현·증빙 | 아직 검증할 부분 |
|---|---|---|
| Root 인증서 서명의 2인 참여, CA 발급의 다인 통제 | 서명 작업 입회·승인 기록과 HSM key-use quorum | 사용자 계정이 실제 별도 인물인지, 실행 경로 우회 여부 |
| CA 키 생성 절차·독립 입회/기록 | 버전 고정 ceremony script, 참여 역할·승인·장치·단계·편차·참여자 및 입회자 sign-off, 공개키·속성·quorum 결과 | 실제 생성 ceremony 수행 및 등록용 증빙 |
| HSM 내 키 생성·보관·사용 | 평문 개인키 반출 금지, 적합한 모듈 사용 | 선택한 HSM 모델·모드의 해당 FIPS 등 인증과 배포 구성 |
| Root/Intermediate 단독 접근 방지 | 키 사용·관리·사용자·quorum 정책의 다인 통제 | 관리자·복구·승인 키 교체 경로 |
| 원래 키와 같은 다인 통제의 백업, off-site 사본, 공식 계획의 연간 검토 | 백업 목록·보호된 보존·다른 Global 장애 영역 복구안, 연간 검토 기록 | AWS 백업·계정·리전 경계의 충족 근거와 실제 복원·검토 증빙 |
| 감사 기록 보호 | 요청·승인·발급·관리 작업 기록, 분리된 보관 권한 | 누락·변조·삭제 방지 및 복구 후 원장 일치 |

[CP]의 키 생성 조항은 독립 입회 및/또는 기록을 요구하지만, [PROGRAM]의 Certificate Policy는 Trust List에 올릴 인증서에 대해 **독립 입회한 ceremony와 서명된 key generation script** 증빙을 요구한다. 따라서 녹화만으로 등록 증빙을 충족했다고 판단하지 않는다. Program에 명시된 WebTrust for CA 보고서에 의한 면제는 그 보고서가 ceremony와 script의 적합성을 증명하는 조건을 확인한 경우에만 적용한다.

표의 대응만으로 적합성 인증을 받았다고 판단하지 않는다. C2PA 참여 CA에 적용되는 통제와 범용 G0에 자율 채택하는 통제의 경계는 [운영 모델](operating-model.md)의 범위 해석을 따른다. 보존·TSA 등 다른 의무는 [C2PA 요구사항 대응표](c2pa-requirements-matrix.md)에서 추적한다.

## 7. PoC 합격 기준

운영 키를 생성하기 전에 테스트 키·별도 계정/클러스터에서 수행할 검증이다. 지금 실행하거나 통과한 시험이 아니다.

| 시험 | 기대 결과 |
|---|---|
| 1인 서명, 같은 승인자 중복 | HSM에서 정족수 부족으로 거부 |
| CLI 이외 SDK로 quorum 키 직접 사용 | 승인 없이 서명 성공하지 않음. 불명확하면 도입 보류 |
| 다른 키·다른 요청·변조된 TBSCertificate | 승인 검증에서 차단. HSM이 내용까지 결합하는지는 별도 결과 기록 |
| 서명 실행기 관리자에 의한 대상 바꿔치기 | 위 보장 범위와 실제 통제 한계를 확인. 예방/탐지 구분 |
| 토큰 재사용·만료·네트워크 단절·재로그인 | 재사용 실패, 불확정 작업 조회 후 새 승인/토큰 처리 |
| 단독 관리자에 의한 quorum 완화/승인자 교체 | 우회 서명 불가 또는 도입을 막는 결함으로 기록 |
| 백업에서 다른 환경으로 복구 | 원래 키 지문·quorum·사용자 정책 유지, 1인 서명 거부 |
| 요청 재시도·서명 후 원장 장애 | 외부 전달된 인증서 중복·누락을 식별, 임의 serial 재사용 금지 |
| 동일 키에 새 serial·유효기간을 요청 | 서명 전에 거부. 기존 인증서의 재전달은 가능하며 새 키 요청은 신규 검증 후 처리 |
| ECDSA/RSA 인증서 조립 | 독립 공개키 검증 및 C2PA 프로파일 검사 성공 |

[CP]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md
[PROGRAM]: https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Conformance%20Program.md
[NIST-KM]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf
[AWS-QUORUM]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli.html
[AWS-USE]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html
[AWS-SETUP]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html
[AWS-ADMIN]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html
[AWS-ECDSA]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html
[AWS-LAMBDA]: https://docs.aws.amazon.com/cloudhsm/latest/userguide/sdk8-serverless.html

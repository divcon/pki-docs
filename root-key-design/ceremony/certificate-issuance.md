# Root·First CA 인증서 발급

[키 생성 절차](key-generation.md)에서 만든 Root·First 키로 Root 자기서명 인증서와 First 인증서를 발급한다. Root 키로 두 인증서에 서명하며, First 키는 자신의 CSR에 서명한다. 하위 Issuing ICA 발급은 이번 범위 밖이다.

이 문서는 [전체 ceremony](README.md)의 인증서 발급 부분이다. 키 생성 문서와 같은 작업 ID를 사용한다. 입력은 Root·First의 HSM 키 식별자·공개키·지문과 생성 검사·입회 기록이다. 키의 보호 책임은 생성 직후부터 유지한다.

## 발급 전 준비

운영 담당자는 아래 설정을 생성 계획 승인 시점에 작성한다. 실제 서명 전에는 프로파일·본문·발급 키·요청 권한·상태 제공 주소를 확정하고, 테스트 키로 발급·실패 처리를 검증한다. 미정 값이나 미해결 프로파일로 운영 인증서를 발급하지 않는다.

<a id="certificate-settings"></a>

### 인증서 설정표

| 항목 | 결정·검사할 내용 |
|---|---|
| 인증서 서명 방식 | 현재 선택한 EC 키에 맞는 ECDSA SHA-2. 해시·서명 파라미터와 HSM·발급 도구 호환성 확정 |
| 이름·기간·일련번호 | Root/First의 C·O·CN, 유효기간, 양의 serial 최대 20 octets. Root 20년·First 5년은 원문의 예시이며 확정값이 아님 |
| 인증서 확장 | X.509 v3, SKI/AKI, KU/EKU, Basic Constraints, 정책 OID, 확장별 critical 여부. 계층 설계는 Root pathLen=2, First=1 |
| 상태 조회 | Root의 AIA/CDP는 금지. First는 OCSP 전용 운영에 맞는 HTTP AIA 주소와 서비스 책임 확정. CRL 미사용이어도 프로파일의 cRLSign 비트 유지 |
| CSR·발급 요청 | PKCS#10 인코딩, 요청자 권한·발급 허락·정보 확인 자료, 공개키·CSR 서명 검증, 허용 확장 목록. CSR 확장을 그대로 복사하지 않음 |
| 검사 결과 | 승인 본문·공개키·서명·issuer·체인·기간·확장을 독립 검증. 정책과 schema 차이는 검사 결과와 함께 기록 |

[Root 프로파일][root-profile]과 [First 프로파일][first-profile]을 기준으로 값을 확정한다. Root AKI의 선택/필수 차이, First AKI 문구, AIA의 caIssuers 검사 차이는 [분석의 해석 확인 사항](../conformance-analysis/05-design-inputs-and-open-questions.md)에 남아 있다. Claim/TSA 하위 적용은 [운영 모델](../operating-model.md#hierarchy)에서 확인한다. 미해결 프로파일로 운영 인증서를 발급하지 않는다.

발급 도구·승인 자료·원장·증거 저장소를 준비하고 [앱 기능 시험](../ca-software-requirements.md#기능-검증)을 수행한다. 승인과 실제 입력의 연결, CLI 세션과 승인용 키는 [다인 통제](../dual-control-options.md)를 따른다.

## 진행 절차

### 1. Root 자기서명 인증서를 발급한다

1. CA 앱은 Root 인증서 본문을 구성한다.
2. 승인자들은 인증서 내용과 사용할 Root 키를 확인한다.
3. 승인자들은 Root 인증서 서명을 승인한다.
4. 실행자는 Root 서명 명령을 명시적으로 내린다.
5. HSM은 Root 키로 인증서 본문에 서명한다.
6. 앱은 서명 결과를 결합해 Root 인증서를 조립한다.
7. 앱은 Root 인증서의 자기서명을 검증한다.

Root 인증서 서명에는 신뢰 역할 담당자 최소 두 명이 참여해야 한다. [CP Certificate Issuance][issuance]

- 필요한 기능: 인증서 구성, 승인, HSM 서명, 결과 검증.
- 남길 것: 승인 본문과 서명 기록, Root 인증서·검사 결과.

### 2. First CSR을 생성한다

1. 앱은 First CSR의 본문을 구성한다.
2. 승인자들은 CSR 서명을 위한 First 키 사용을 승인한다.
3. 앱은 HSM에 First 키로 CSR 서명을 요청한다.
4. HSM은 First 키로 CSR 본문에 서명한다.
5. 앱은 서명 결과를 결합해 First CSR을 완성한다.
6. 앱은 CSR 서명·공개키·요청 내용을 검사한다.

- 필요한 기능: CSR 구성, 키 사용 승인, HSM 서명, CSR 검증.
- 남길 것: First 키 사용 승인·서명 기록, CSR·검사 결과.

### 3. First 인증서를 발급한다

1. 앱은 First 인증서의 최종 본문을 구성한다.
2. 승인자들은 First 인증서 내용과 사용할 Root 키를 확인한다.
3. 승인자들은 Root 키를 통한 First 인증서 서명을 승인한다.
4. 실행자는 Root 서명 명령을 명시적으로 내린다.
5. HSM은 Root 키로 First 인증서 본문에 서명한다.
6. 앱은 서명 결과를 결합해 First 인증서를 조립한다.
7. 앱은 First 인증서의 서명을 검증한다.
8. 앱은 Root → First 연결을 검증한다.

Root 서명에는 Root 자기서명 인증서 발급과 동일한 최소 2인 참여·명시적 실행 통제를 적용한다.

- 필요한 기능: 인증서 구성, 승인, HSM 서명, 인증서·체인 검증.
- 남길 것: 승인 본문과 서명 기록, First 인증서·체인 검사 결과.

### 4. 최종 결과를 확인한다

1. 검증 담당자는 승인한 내용과 결과 인증서가 일치하는지 확인한다.
2. 검증 담당자는 생성 로그와 공개키가 일치하는지 확인한다.
3. 참여자·입회자는 실제 수행 결과와 절차 이탈을 확인한다.

- 필요한 기능: 증거 취합, 결과 대조, 일탈 처리.
- 남길 것: 증거 목록, 최종 검사 결과, 일탈 처리 기록.

필수 검사나 증거가 빠지면 완료·배포를 보류한다.

<a id="sign-off"></a>

### 5. 전체 수행 결과에 확인 서명을 남긴다

1. 참여자·입회자는 키 생성과 인증서 발급의 단계별 결과·증거·절차 이탈을 확인한다.
2. 참여자는 전체 수행 기록에 확인 서명을 남긴다.
3. 입회자는 전체 수행 기록에 확인 서명을 남긴다.

- 필요한 기능: 수행 기록 취합, 결과 확인 서명.
- 남길 것: 키 생성·인증서 발급 문서 버전과 수행 기록을 식별한 참여자·입회자의 확인 서명.

확인 서명은 승인된 절차대로 수행했는지를 기록한다. 두 문서로 나누었다고 과정마다 별도 스크립트와 확인 서명을 요구하는 것은 아니다. 키 생성 당시의 입회·로그는 [키 생성 절차](key-generation.md)에서 확보한다. [CP 키 생성][generation] · [Program][program]

### 6. 운영에 인계한다

1. 운영 담당자는 키·기록·백업의 관리 책임을 인수한다.

- 필요한 기능: 보관·운영 인계.
- 남길 것: 인수 기록.

### 7. 작업 접근을 종료한다

1. 운영 담당자는 임시 권한을 회수한다.
2. 운영 담당자는 세션을 종료한다.

- 필요한 기능: 권한 회수, 세션 종료.
- 남길 것: 접근 종료 기록.

Ceremony 완료, 운영 준비, 감사, Trust List 등록은 각각 확인한다.

## 증거 보관과 중단 처리

키 생성의 작업 ID에 CSR·인증서 지문, 승인한 인증서 본문·해시, 프로파일·serial, 승인·서명·검사 기록, 일탈 처리와 최종 확인 서명을 연결한다. 비밀번호·개인키·승인용 비밀은 기록하지 않는다. 발급 기록과 나머지 증거는 [기록 정책](../operating-model.md#records)을 따른다.

| 상황 | 처리 |
|---|---|
| 권한·CSR·프로파일 오류, 승인 부족 | 서명 전에 거부하고 원인 기록 |
| 승인 후 본문·키·설정 변경 | 기존 승인 무효화, 재검토 |
| 세션 종료·단절, 승인 기한 경과 | 중단 후 작업 상태 확인. 재개 승인과 필요한 새 토큰 확보 |
| 서명 결과 불명, HSM 성공 후 저장 실패 | 기존 결과·원장 대조 전 자동 재서명 금지 |
| 인증서 불일치·필수 증거 누락 | 완료·배포·등록 제출 보류, 원인과 일탈 처리 |
| 발급 후 인증서 내용 오류 | [동일 키 재발급 금지](../operating-model.md#rekey)를 확인한 뒤 후속 처리 판단 |

생성 기록의 결함과 생성 후 중단은 [키 생성의 중단 처리](key-generation.md#증거-보관과-중단-처리)를 따른다.

## 남은 결정과 운영 인계

| 항목 | 정할 내용 |
|---|---|
| 발급 도구·저장소 | 서버/스크립트 형태, CLI 실행 주체, 원장·증거 저장 방식 |
| 프로파일·요청 계약 | 위 설정표의 실제 값, 상태 조회 주소, 요청·검사 규칙과 원문 차이의 처리 |
| 수행·완료 | 서명 실행·승인·검증·완료·운영 인수 역할, 중단·재개 책임, 최종 기록·확인 서명 형식 |
| 운영·감사·등록 | 조항별 적용·담당·절차·증거·미비점 연결, 공개 정책·OCSP·백업·등록 자료의 완료 시점 |

발급·폐지·상태 제공, 인력·권한·변경 관리, 기록 검토, 백업·복구와 등록 준비는 [운영 모델](../operating-model.md)과 [요구사항 대응표](../c2pa-requirements-matrix.md)로 인계한다.

## 원문

Conformance v0.2 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc` 기준이다. 단계·양식·내부 판정 방식은 설계안이다.

[generation]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#key-pair-generation-and-installation-by-cas
[issuance]: ../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md#certificate-issuance
[program]: ../../conformance-public/docs/v0.2/C2PA%20Conformance%20Program.md#certificate-policy
[root-profile]: ../../conformance-public/docs/v0.2/cert-profiles/rootCA.cert.yaml
[first-profile]: ../../conformance-public/docs/v0.2/cert-profiles/intermediateCa.cert.yaml

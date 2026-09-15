# C2PA AL2 인증서 발급 Attestation 요구사항

## 1. 적용 범위

기준 문서는 현재 저장소의 C2PA Conformance Program v0.2 자료다. 적용 범위는 다음과 같다.

- Manifest(Claim) Signing Leaf 및 Issuing CA(ICA) 인증서 발급 시 Attestation 필요 여부
- TSA Signing Leaf 및 TSA Issuing CA 인증서 발급 시 Attestation 필요 여부
- Assurance Level 2(AL2) Dynamic Evidence 검증 항목
- Device, Application, Key Attestation의 관계
- CSR 공개키와 하드웨어 보호 개인키를 연결하여 검증하는 방법
- Attestation challenge와 RFC 3161 TSA nonce의 차이

C2PA 문서의 공식 용어는 `C2PA Claim Signing Certificate`이다. 이 문서의 `Manifest Signing Leaf`는 해당 Claim Signing Leaf 인증서를 가리킨다.

## 2. 인증서 유형별 요구사항

Attestation 및 challenge 적용 범위는 인증서 유형과 Claim Signing Leaf의 Assurance Level에 따라 구분된다.

| 발급 대상 | Attestation | Challenge | 주요 필수 통제 |
|---|---|---|---|
| Manifest Signing Leaf AL1 | 필수 아님 | 필수 아님 | 안전한 enrollment 인증 및 키 소유 증명 |
| Manifest Signing Leaf AL2 | 하드웨어 기반 Dynamic Evidence 필수 | 사용하는 Attestation 방식이 challenge를 요구하면 검증 필수 | 제품, 키, 플랫폼 및 콘텐츠 처리 환경 검증 |
| Manifest Signing ICA | C2PA 표준상 일괄 필수 아님 | 일괄 필수 아님 | 문서화된 CA 발급 절차, trusted role, 다중 통제 |
| TSA Signing Leaf | C2PA 표준상 일괄 필수 아님 | 인증서 발급 challenge는 일괄 필수 아님 | CA의 신원·권한·키 소유 검증 및 TSA 인증서 프로파일 준수 |
| TSA Issuing CA | C2PA 표준상 일괄 필수 아님 | 일괄 필수 아님 | 문서화된 CA 발급 절차와 TSA ICA 프로파일 준수 |

CA의 CPS(Certificate Practice Statement) 또는 사업 정책은 C2PA 공통 요구사항보다 강한 추가 검증 절차를 정의할 수 있다.

## 3. AL2에서 요구하는 Dynamic Evidence

AL2 인증서 발급 시 CA가 평가하는 Dynamic Evidence는 O.1부터 O.4까지 네 보안 목표를 대상으로 한다.

### 3.1 O.1: Generator Product 인스턴스 식별

CA는 C2PA Conformance Administrator가 서명한 Notice of Conformance와 그 안의 Conforming Products List(CPL) record를 검증한다. 공개 CPL record도 적합성 증거로 사용할 수 있으나, 공개 시점은 Notice 발급 및 인증서 발급보다 늦을 수 있다.

검증 대상의 예시는 다음과 같다.

- 패키지명 또는 애플리케이션 식별자
- 앱 버전 또는 승인된 revision
- 앱 코드 서명 인증서 digest
- 바이너리 hash 또는 플랫폼이 제공하는 동등한 식별 정보
- 필요한 경우 허용된 제조사, 브랜드 또는 단말 모델

### 3.2 O.2: Claim Signing 개인키 보호

CA는 발급 대상 Leaf 인증서의 공개키와 대응하는 개인키의 하드웨어 기반 Keystore/KMS 생성·보관 속성을 확인한다.

- TEE, StrongBox, HSM 또는 동등한 하드웨어 보호 영역에서의 개인키 생성
- 개인키의 non-exportable 속성
- `GENERATED` key origin
- C2PA 인증서 프로파일에 부합하는 purpose, algorithm, key size, digest 및 padding
- 발급 요청자의 개인키 소유 증명
- CSR 기반 Android Key Attestation 흐름에서의 Attestation 공개키와 CSR 공개키 일치

CSR과 인증서에는 공개키가 포함된다. 하드웨어 보호 및 비밀성 요구사항은 해당 공개키와 짝을 이루는 개인키에 적용된다.

### 3.3 O.3: Claim Generator 실행 환경 보호

CA는 Claim Generator가 실행되는 플랫폼의 이미지 인증, 부팅 상태 및 보안 패치 상태를 확인한다. Claim Generator의 패치 최신성 증거는 Applicant가 선택한 방식에 따라 패치 적용 시점 또는 CA에 등록된 revision 중 하나를 사용한다.

- 인증된 이미지 기반 secure boot 또는 verified boot
- 정책에 부합하는 부트로더 또는 단말 잠금 상태
- CRITICAL/HIGH 취약점에 대한 정책 기한 내 OS 및 플랫폼 패치 적용
- Claim Generator의 90일 이내 패치 적용 시점 또는 CA가 허용한 revision

### 3.4 O.4: Asset 및 Assertion 처리 환경 보호

O.4 검증 범위에는 Asset 또는 Assertion을 생성·변경하는 GP TOE 내부 소프트웨어의 무결성이 포함된다. 해당 소프트웨어의 패치 최신성 증거는 Applicant가 선택한 방식에 따라 패치 적용 시점 또는 CA에 등록된 revision 중 하나를 사용한다.

- 콘텐츠 및 Assertion 처리 소프트웨어의 이미지 인증
- CRITICAL/HIGH 취약점에 대한 정책 기한 내 플랫폼 패치 적용
- 관련 소프트웨어의 90일 이내 패치 적용 시점 또는 CA가 허용한 revision
- 처리 과정의 비인가 코드에 의한 콘텐츠 또는 Assertion 변조 방지

AL2 Dynamic Evidence의 검증 영역은 다음과 같다.

```text
승인된 제품(O.1)
  + 하드웨어 보호 서명 키(O.2)
  + 안전한 Claim Generator(O.3)
  + 안전한 콘텐츠/Assertion 처리 환경(O.4)
  = AL2 발급을 위한 Dynamic Evidence
```

## 4. Device, Application, Key Attestation 관계

검증 목적은 일반적으로 세 영역으로 나눌 수 있다.

| 구분 | 증명하는 내용 |
|---|---|
| Key Attestation | 키가 하드웨어에서 생성·보관되는지, 키 속성과 공개키가 무엇인지 |
| Device/Platform Attestation | Verified Boot, 부트로더 잠금, OS·Vendor·Boot 패치 수준 등 |
| Application Attestation | 패키지명, 앱 버전, 앱 서명 인증서 및 승인된 앱 인스턴스인지 |

하나의 Attestation artifact가 Key, Device/Platform, Application 영역의 증거를 함께 포함할 수 있으며, 플랫폼에 따라 여러 artifact를 조합할 수 있다.

예를 들어 Android Key Attestation에는 키 정보뿐 아니라 다음 정보가 함께 포함될 수 있다.

- Attestation 및 KeyMint security level
- challenge
- 애플리케이션 패키지명, 버전 및 서명 인증서 digest
- 키 origin과 키 사용 속성
- device locked 및 verified boot 상태
- OS, Vendor 및 Boot patch level

각 artifact가 제공하는 속성을 O.1~O.4 요구사항에 매핑한다. C2PA v0.2는 Google Play Integrity를 integrity attestation 방법으로 열거하지만 구체적인 검증값과 O.1~O.4 매핑은 아직 정의하지 않는다. AL2 판정에 사용하는 evidence type은 해당 제품의 CPL `attestationMethods`와 CA의 검증 절차 또는 CPS에 정의되어야 한다.

## 5. Android AL2 검증 예시

현재 저장소의 C2PA Certificate Policy는 Android Key Attestation에 다음 검증 기준을 제시한다.

### 5.1 Attestation 신뢰성과 freshness

- Attestation 인증서 체인이 신뢰할 수 있는 제조사/플랫폼 root로 연결되는지 검증
- Attestation 서명 및 인증서 상태 검증
- `attestationChallenge`가 CA가 해당 enrollment에 발급한 challenge와 일치하는지 검증
- challenge가 만료되지 않았고 이전 요청에서 재사용되지 않았는지 검증

### 5.2 키 보안 속성

- `attestationSecurityLevel`: `TrustedEnvironment` 또는 `StrongBox`
- `keyMintSecurityLevel`: `TrustedEnvironment` 또는 `StrongBox`
- `origin`: `GENERATED`
- `purpose`: `SIGN`
- RSA 또는 EC 알고리즘과 허용된 key size/curve 사용
- 허용된 SHA-2 digest 사용
- RSA인 경우 RSA-PSS 조건 확인

### 5.3 제품 및 앱 식별

- `package_name`이 CA에 등록된 Generator Product와 일치
- 앱 `version`이 CA의 허용 목록에 포함
- 앱 서명 인증서의 SHA-256 digest가 등록값과 일치
- 특정 OEM brand로 제한된 제품의 경우 brand 및 manufacturer가 등록값과 일치
- 특정 OEM model로 제한된 제품의 경우 model이 등록값과 일치

### 5.4 플랫폼 무결성

- `deviceLocked = true`
- `verifiedBootState = Verified`
- OS patch level이 CSR 제출 월 기준 허용 범위 내에 있음
- Vendor 및 Boot patch level이 CSR 제출일 기준 허용 범위 내에 있음

현재 정책의 Android 지침은 OS patch level을 CSR 제출 월 기준 허용된 네 월 값 이내로, Vendor 및 Boot patch level을 CSR 제출일 기준 90일 이내로 규정한다. 세 patch level 모두 CSR 제출 시점보다 미래일 수 없다. 적용값은 C2PA 정책 버전 및 CA CPS와 함께 관리한다.

## 6. CSR 기반 Key Attestation의 키 바인딩

CA는 인증서 발급을 요청한 키 쌍의 소유를 검증한다. 서명된 CSR 검증은 키 소유 증명 방법 중 하나이며, 관리형 KMS 구성 검사는 대안이 될 수 있다. CSR 기반 Android Key Attestation 흐름에서는 CSR의 `subjectPublicKeyInfo`와 Attestation leaf 인증서의 공개키를 비교한다.

CSR 기반 흐름의 공개키 바인딩 관계는 다음과 같다.

```text
CSR.subjectPublicKeyInfo
    == Key Attestation Leaf Certificate.subjectPublicKeyInfo
    == 발급된 Manifest Signing Leaf Certificate.subjectPublicKeyInfo
```

CSR 기반 Android AL2 Leaf 발급 흐름은 다음과 같이 구성할 수 있다.

```text
1. CA가 enrollment별 일회성 challenge 발급
2. 단말이 TEE/StrongBox에서 Claim Signing KeyPair 생성
3. 단말이 challenge가 포함된 Key Attestation 체인 획득
4. 같은 개인키로 CSR 서명
5. 단말이 CSR + Attestation evidence를 CA에 제출
6. CA가 CSR 서명, Attestation 체인, challenge 및 AL2 정책 검증
7. CA가 CSR 공개키와 Attestation 공개키가 동일한지 검증
8. 모든 검증 성공 시 같은 공개키로 AL2 Leaf 인증서 발급
```

CSR 기반 흐름의 키 검증 항목은 다음과 같다.

- CSR 자체 서명의 유효성
- CSR 공개키와 Attestation 공개키의 일치
- Attestation에 의한 해당 키의 하드웨어 생성 속성 증명
- 개인키의 non-exportable 및 서명 용도 제한 속성
- challenge와 현재 enrollment에 발급된 값의 일치
- 최종 인증서와 CSR 공개키의 일치

CSR과 Attestation 공개키의 일치 검증은 정상 Attestation artifact와 별도 CSR 키를 조합하는 공격을 차단한다.

## 7. Challenge의 역할

Attestation challenge는 evidence의 freshness를 제공하고 해당 evidence를 현재 enrollment에 대응시킨다. CSR의 키 바인딩은 CSR 서명에 의한 키 소유 증명과 CSR 공개키-Attestation 공개키 일치 검증으로 별도 수행한다.

```text
CA가 예측 불가능한 challenge 발급
        ↓
플랫폼이 challenge를 포함한 Attestation 생성
        ↓
CA가 제출된 challenge를 대조
        ↓
일치하고 미사용 상태인 경우에만 다음 검증 진행
```

Challenge는 다음 공격을 방지한다.

- 과거 정상 단말에서 발급받은 Attestation의 재사용
- 다른 인증서 발급 요청에서 얻은 Attestation의 전용

CA는 challenge를 충분한 엔트로피의 난수로 생성하고 enrollment ID에 연결하며, 만료 시간과 일회성 사용 정책을 적용한다.

## 8. RFC 3161 TSA Nonce와의 차이

Attestation challenge와 RFC 3161 `TimeStampReq.nonce`는 목적과 사용 위치가 다르다.

| 항목 | Attestation Challenge | RFC 3161 TSA Nonce |
|---|---|---|
| 사용 시점 | AL2 인증서 enrollment | 타임스탬프 토큰 요청 |
| 목적 | Attestation freshness 및 enrollment 대응 | 타임스탬프 응답의 요청 대응 및 replay 탐지 |
| 포함 위치 | Attestation report 또는 Attestation 인증서 확장 | `TimeStampReq`와 `TimeStampToken` |
| C2PA 인증서 발급과의 관계 | AL2 Attestation 흐름에서 검증 | TSA 인증서 발급과 직접 관계없음 |
| RFC 3161 필수 여부 | 해당 없음 | 요청 필드는 `OPTIONAL` |

RFC 3161 타임스탬프 요청 nonce는 TSA Leaf 또는 ICA 인증서 enrollment의 Device/Key Attestation 증거로 사용되지 않는다.

`TimeStampReq.nonce` 필드는 OPTIONAL이며 replay 탐지를 위해 사용이 RECOMMENDED된다. 요청에 nonce가 포함되면 `TSTInfo.nonce`도 존재해야 하고 요청값과 동일해야 하며, 불일치 응답은 거부된다. RFC 3161 적합 TSA 서버는 nonce 처리를 지원해야 한다.

## 9. CA API 및 데이터 모델 권장안

Attestation artifact는 Key, Platform, Application 검증 영역을 복수로 포함할 수 있다. 증거 목록과 검증 목적을 분리한 데이터 모델은 플랫폼별 artifact 구성을 표현할 수 있다.

다음은 데이터 모델 예시다.

```json
{
  "enrollmentId": "...",
  "challengeId": "...",
  "csr": "...",
  "evidence": [
    {
      "type": "android-key-attestation",
      "covers": ["key", "platform", "application"],
      "artifact": "...",
      "certificateChain": ["..."]
    },
    {
      "type": "platform-attestation",
      "covers": ["platform", "application"],
      "artifact": "..."
    }
  ]
}
```

요청자가 제출한 `covers` 값은 판정 근거로 사용하지 않는다. 플랫폼별 검증기가 artifact를 검증하고 O.1~O.4 충족 여부를 내부적으로 판정한다.

내부 판정 모델은 다음 상태를 사용할 수 있다.

```text
O.1 productEligibility      = PASS / FAIL / NOT_PROVEN
O.2 keyProtection          = PASS / FAIL / NOT_PROVEN
O.3 claimGeneratorSecurity = PASS / FAIL / NOT_PROVEN
O.4 contentPathIntegrity   = PASS / FAIL / NOT_PROVEN
```

AL2 인증서는 적용 대상 항목이 모두 `PASS`인 경우 발급된다. AL2 증거가 충족되지 않은 경우 CA는 C2PA Certificate Policy에 따라 다음으로 낮은 Assurance Level의 요구사항을 평가할 수 있다.

## 10. 구현 체크리스트

### 공통 Enrollment

- [ ] 안전한 사용자/Subscriber 인증
- [ ] 요청 키 쌍의 소유 검증(서명된 CSR 검증 또는 KMS 구성 검사 등)
- [ ] CSR 기반 흐름의 CSR 형식과 서명 검증
- [ ] 요청된 인증서 프로파일 검증
- [ ] 키 소유 증명(Proof of Possession)
- [ ] CA CPS 및 발급 권한 검증

### Manifest Signing Leaf AL2

- [ ] 서명된 Notice of Conformance와 포함된 CPL record 검증
- [ ] 일회성 challenge 발급 및 대조
- [ ] Attestation 서명과 인증서 체인 검증
- [ ] CSR 기반 흐름의 CSR 공개키와 Attestation 공개키 일치
- [ ] 하드웨어 기반 키 생성·보관 및 non-exportability 검증
- [ ] 앱 패키지명, 버전 및 코드 서명 인증서 검증
- [ ] Verified Boot와 단말 잠금 상태 검증
- [ ] OS, Vendor 및 Boot patch 기준 검증
- [ ] Applicant가 선택한 패치 적용 시점 또는 허용 revision 검증
- [ ] 콘텐츠와 Assertion 처리 소프트웨어 무결성 검증
- [ ] CSR 기반 흐름의 최종 Leaf 인증서와 CSR 공개키 일치

### ICA 및 TSA 인증서

- [ ] Attestation을 C2PA 공통 필수값으로 강제하지 않음
- [ ] CA 자체 CPS가 요구하는 추가 검증 여부 확인
- [ ] CA 인증서 발급 시 trusted role과 다중 통제 적용
- [ ] TSA Leaf/ICA의 Key Usage, Extended Key Usage 및 Certificate Policy 확인
- [ ] RFC 3161 nonce를 인증서 enrollment challenge와 혼동하지 않음

## 11. 저장소 내 근거 자료

- [C2PA Certificate Policy v0.2](../../conformance-public/docs/v0.2/C2PA%20Certificate%20Policy.md)
  - Notice of Conformance 및 CPL record 검증: 457행 부근
  - Certificate enrollment 인증 및 키 소유 검증: 469행 부근
  - 인증서 발급과 Dynamic Evidence: 511행 부근
  - AL1/AL2 Dynamic Evidence 요구사항: 1686행 부근
  - Platform-specific Attestation challenge: 1766행 부근
  - Android Key Attestation 검증값: 1792행 부근
- [C2PA Generator Product Security Requirements v0.2](../../conformance-public/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md)
  - AL2 제품 식별 증거: 364행 부근
  - 키 보호 및 키 소유 증거: 378행 부근
  - Claim Generator 보호: 474행 부근
  - 콘텐츠/Assertion 처리 환경 보호: 560행 부근
- [Claim Signing Leaf AL2 Certificate Profile](../../conformance-public/docs/v0.2/cert-profiles/claimSigningLeaf.al2.cert.yaml)
- [Claim Signing Issuing CA Certificate Profile](../../conformance-public/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.yaml)
- [TSA Leaf Certificate Profile](../../conformance-public/docs/v0.2/cert-profiles/tsaLeaf.cert.schema.yaml)
- [TSA Issuing CA Certificate Profile](../../conformance-public/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml)
- [RFC 3161](../../rfc3161.txt)
  - `TimeStampReq.nonce` OPTIONAL 정의: 233행 부근
  - 요청/응답 nonce 일치 요구사항: 267행 및 428행 부근
  - TSA 서버의 nonce 지원 요구사항: 440행 부근
  - replay 탐지를 위한 nonce 사용 권고: 847행 부근

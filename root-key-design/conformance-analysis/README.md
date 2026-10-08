# Root·ICA 키의 C2PA 요구사항 분석 보고서

원문 기준: **C2PA Conformance v0.2·Technical Specification 2.4의 고정 커밋**. 최초 조사일은 2026년 9월 17일이며, 2026년 10월 8일 원문 대조 감사를 수행했다. 요구사항별 적용 대상, 의무 수준, 증거와 해석 확인 사항을 제시한다. 이번 감사가 최신 공개판이나 실제 신청 시점의 적용 버전을 확정하는 것은 아니다.

## 보고서 구성

| 구분 | 내용 |
|---|---|
| [조사 기준 및 범위](00-sources-and-scope.md) | 적용 버전·조항·출처 |
| [키·인증서](01-key-and-certificate-requirements.md) | 알고리즘·보호·프로파일·용도 |
| [관리·운영](02-management-and-operations.md) | 인력·접근·기록·백업·폐지 |
| [Ceremony 스크립트](03-ceremony-script-requirements.md) | 생성·발급의 적용 범위, 생성 통제와 스크립트 필수 항목 |
| [Conformance 등록](04-conformance-and-evidence.md) | 등록·제출 증거와 CA·제품 책임 |
| [해석 확인 사항](05-design-inputs-and-open-questions.md) | 원문 차이와 적용 범위 확인 |
| [원문 위치 대응표](06-source-map.md) | 모든 요구사항·해석 ID의 고정 원문 파일·줄·절, PDF 페이지와 재현 방법 |
| [반복 감사 기록](07-audit-log.md) | 회차별 범위·교정·교차 검증·남은 제한 |

## 핵심 구분

- **키 재료**에는 알고리즘·강도·생성 환경·사용 통제가 적용된다. DN, KU, EKU, pathLen, 정책 OID, AIA/CDP는 그 공개키를 담는 **인증서**의 요구다.
- **Root**, **First Intermediate CA(pathLen=1)**, **Claim Signing Issuing CA(pathLen=0)**, **TSA Issuing CA**(pathLen=0)를 구분한다. 이 문서에서 ICA는 세 subordinate CA 역할을 포괄하되 개별 요구에는 정확한 역할을 표시한다.
- **CA TL**(C2PA Trust List)과 **TSA TL**(C2PA TSA Trust List)은 별도다. Trust anchor는 Root 또는 subordinate CA일 수 있다. ICA를 앵커로 등록하는 것과 상위 Root의 운영 책임이 면제되는 것은 별개다. [CP Glossary][cp], [Program][program]
- CA 키 생성·보관 통제와 등록할 인증서의 입회 증거는 범위가 다르다. CP의 생성 입회/기록 조건만으로 Program의 독립 입회·서명 script 제출 조건을 충족했다고 판단하지 않는다.
- **키 생성 세레모니**와 **CA 인증서 발급 절차**에는 각각의 통제가 적용된다. ICA 키 생성과 상위 CA의 인증서 서명·발급을 한 행사에 묶는 것은 설계 선택이며, 별도로 진행해도 발급 통제는 적용된다. [제3장](03-ceremony-script-requirements.md), [정책 인계](05-design-inputs-and-open-questions.md)

## 표기

**필수**는 원문의 SHALL/MUST/금지 및 프로파일 명시 제약, **권고**는 SHOULD/RECOMMENDED, **허용**은 MAY/OPTIONAL이다. CP는 대문자에만 BCP 14를 적용하고 Spec은 대소문자에 관계없이 적용한다. CP의 소문자 표현·서술형 요구·예시는 해당 위치에서 구분하며, 소문자라는 이유만으로 문맥상 요구를 삭제하거나 대문자 SHALL로 바꾸지 않는다. **설계 제안**은 정책 결정·증빙 방법에 대한 우리 제안이며 표준 의무를 새로 만드는 것이 아니다. **확인 필요**는 원문 간 차이 또는 해석 공백이다. 각 표의 ID는 후속 설계에서 추적하기 위한 프로젝트 식별자이며 [원문 위치 대응표](06-source-map.md)로 찾을 수 있다.

모든 요구사항은 공식 원문에 근거하며, 해석이 확정되지 않은 항목은 별도로 표시한다. 설계·운영 환경의 실제 적합성과 C2PA 승인 여부는 구현 증거 및 심사 결과에 따라 판단한다.

[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md

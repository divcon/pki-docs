# Root·ICA 키의 C2PA 요구사항 분석 보고서

조사 기준일: **2026년 9월 17일**. C2PA Conformance v0.2와 Technical Specification 2.4에 근거하여 Root·ICA 설계에 반영할 요구사항을 정리한다. 요구사항별 적용 대상, 의무 수준, 증거와 해석 확인 사항을 제시한다.

## 보고서 구성

| 구분 | 내용 |
|---|---|
| 조사 기준 및 범위 | 어느 버전과 조항을 조사했는가? |
| 제1장 「키 자체와 인증서 요구사항」 | 어떤 키를 만들고 인증서에 무엇을 넣어야 하는가? |
| 제2장 「관리·운영 요구사항」 | 생성 이후 무엇을 통제하고 보존해야 하는가? |
| 제3장 「키 생성 세레모니 스크립트 요구사항」 | 대본과 실제 수행 증거에 무엇이 필요한가? |
| 제4장 「Conformance 등록 및 그 밖의 요구사항」 | 무엇을 제출하고 추가로 입증해야 하는가? |
| 제5장 「설계 반영 후보와 해석 확인 사항」 | 바로 반영할 요구와 확정 전 확인할 항목은 무엇인가? |
| 제6장 「검토 결과와 보완 내역」 | 누가 무엇을 대조했고 피드백을 어떻게 처리했는가? |

## 핵심 구분

- **키 재료**에는 알고리즘·강도·생성 환경·사용 통제가 적용된다. DN, KU, EKU, pathLen, 정책 OID, AIA/CDP는 그 공개키를 담는 **인증서**의 요구다.
- **Root**, **First Intermediate CA(pathLen=1)**, **Claim Signing Issuing CA(pathLen=0)**, **TSA Issuing CA**(pathLen=0)를 구분한다. 이 문서에서 ICA는 세 subordinate CA 역할을 포괄하되 개별 요구에는 정확한 역할을 표시한다.
- **CA TL**(C2PA Trust List)과 **TSA TL**(C2PA TSA Trust List)은 별도다. Trust anchor는 Root 또는 subordinate CA일 수 있다. ICA를 앵커로 등록하는 것과 상위 Root의 운영 책임이 면제되는 것은 별개다. [CP Glossary][cp], [Program][program]
- CA 키 생성·보관 통제와 등록할 인증서의 입회 증거는 범위가 다르다. CP의 생성 입회/기록 조건만으로 Program의 독립 입회·서명 script 제출 조건을 충족했다고 판단하지 않는다.

## 표기

**필수**는 원문의 SHALL/MUST/금지 및 프로파일 명시 제약, **권고**는 SHOULD/RECOMMENDED, **허용**은 MAY/OPTIONAL이다. 소문자 표현이나 예시는 별도로 표시한다. **설계 제안**은 증빙 또는 구현 방법에 대한 우리 제안이며 표준 의무를 새로 만드는 것이 아니다. **확인 필요**는 원문 간 차이 또는 해석 공백이다. 각 표의 ID는 후속 설계에서 추적하기 위한 프로젝트 식별자다.

모든 요구사항은 공식 원문에 근거하며, 해석이 확정되지 않은 항목은 별도로 표시한다. 설계·운영 환경의 실제 적합성과 C2PA 승인 여부는 구현 증거 및 심사 결과에 따라 판단한다.

[cp]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md
[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md

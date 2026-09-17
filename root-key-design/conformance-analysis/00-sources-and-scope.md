# 00. 조사 기준 및 범위

## 기준 문서

본 보고서는 C2PA Conformance Program v0.2와 C2PA Technical Specification 2.4를 기준으로 Root 및 Intermediate CA의 키·인증서, 운영 통제, 키 생성 세레모니와 등록 증거 요구사항을 분석한다. 조사 기준일은 **2026년 9월 17일**이다.

| 공식 문서 | 기준 버전 | 주요 검토 범위 |
|---|---|---|
| [C2PA Certificate Policy](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md) | v0.2, 2026-07-31 | CA 키 생성·보호·사용, 인증서 프로파일, 운영 통제, 폐지·상태 제공, CA 책임 |
| [C2PA Conformance Program][program] | v0.2, 2026-07-31 | CA/TSA 신청, 프로파일 검증·세레모니 증거, 신뢰 목록 등록·제거 |
| [C2PA Governance Framework](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Governance%20Framework.md) | v0.2, 2026-07-31 | 참여자 역할, 계약, 승인·철회·이의 제기 |
| [CA 및 관련 인증서 프로파일](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/) | Conformance v0.2 부속 자료 | Root·First ICA·Claim Issuing·TSA Issuing 프로파일, CA 인증서·CSR 검사 schema, 관련 leaf 프로파일 |
| [Additional Conformance Requirements](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/Additional%20Conformance%20Requirements%20Against%20the%20Content%20Credentials%20Specification.md) | v0.2, 2026-07-31 | GP/VP 추가 의무와 CA 요구사항의 적용 경계 |
| [Generator Product Security Requirements](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Generator%20Product%20Security%20Requirements.md) | v0.2, 2026-07-31 | 제품 보안 수준과 발급 CA가 확인해야 할 증거의 접점 |
| [C2PA Technical Specification][spec] | 2.4 | §13.2, §14.4–14.5, §15.9: 알고리즘, 인증서, 신뢰 목록·체인, 폐지 검증 |

Conformance v0.2는 Spec 2.2와 2.4를 지원한다. 본 보고서는 **Conformance v0.2와 Spec 2.4의 조합**을 분석하며, Spec 2.2에 그대로 적용되는 것으로 해석하지 않는다. 실제 신청 시에는 지원 버전·변경 공지·계약 조건을 확인해야 한다. [Program Versioning and Grace Period][program]

## 출처와 인용 기준

버전명이 같더라도 공개 자료가 수정될 수 있으므로, 인용 대상은 공식 저장소의 [Conformance 자료 개정본](https://github.com/c2pa-org/conformance-public/commit/2466172859fad1215f7aaf7e3768b41a0ac29abc)과 [Specifications 자료 개정본](https://github.com/c2pa-org/specifications/commit/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f)으로 고정했다. 각 인용은 해당 개정본의 문서와 조항으로 직접 연결한다. Spec 2.4는 [공식 열람본](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)에서도 확인할 수 있다.

요구사항의 근거는 공식 정책·사양·부속 프로파일이다. 본 보고서와 개별 시스템의 설계 문서는 이를 해석·적용한 자료이며 독립적인 규범 근거로 사용하지 않는다.

## 원문별 요구사항 추적 범위

| 원문 묶음 | 조사 결과 위치 |
|---|---|
| CP Publication, Identification/Authentication, Certificate Life-Cycle | 02의 O01/O02/O11/O18/O21–O26, 04의 E09–E13 |
| CP Facility/Management/Operational Controls | 02의 O01–O20, O27–O28 |
| CP Technical Security Controls | 01의 K01–K06, 02의 O08–O10/O14–O16, 03의 C01–C10, 04의 T01 |
| CP Certificate/CRL/OCSP Profiles 및 별도 CA YAML/schema | 01의 P01–P05/U01–U06, 02 O23–O25, 05 Q02–Q04/Q11–Q12 |
| CP Compliance Audit, CA Representations, Other Business/Legal | 02 O27–O28, 04 E13/E15 |
| CP Dynamic Evidence·GP Security Requirements의 CA 접점 | 04 E09–E12, 제품 자체 통제와 CA 검증 책임 구분 |
| Program·Governance | 03 등록 키 입회 증거, 04 E01–E08/E16, 05 Q05/Q07/Q08 |
| Additional Requirements | 04 E14, GP/VP와 Root·ICA 적용 경계 |
| Spec 2.4 §13.2/§14.4–14.5/§15.9 | 01의 K01–K02/P05/U04, 02 상태 제공 경계, 05 Q09/Q12 |

## 근거의 적용 방법

CP 본문·내장 YAML·별도 YAML·JSON schema·Spec을 함께 대조한다. JSON schema는 디코딩된 JSON 검사 도구이며 그 통과가 DER 서명, 체인, 실제 키 생성, HSM 통제, 입회 증거를 입증하지 않는다. CSR 검사 schema도 최종 인증서 검증의 대체물이 아니다. 원문 사이의 차이는 임의의 우선순위를 정해 없애지 않고 제5장 「설계 반영 후보와 해석 확인 사항」에 남긴다.

CP에는 규범 단어 정의가 있고 Spec에는 별도의 Standard Terms가 있다. 두 문서의 대소문자 관행을 기계적으로 섞지 않는다. 절 번호가 없는 CP/Program은 **영문 절 제목과 공식 개정본의 해당 위치**, Spec은 **버전·절 번호**로 추적한다.

## 범위 경계

- Root/ICA 운영에 적용되는 CP 통제는 등록 인증서 제출 요건보다 넓게 조사했다. 미등록 상위 Root에 대한 포괄 면제는 확인되지 않았다.
- Claim Signing/OCSP/TSA leaf는 CA의 허용 사용, 발급 책임, 폐지 서비스 경계를 설명하는 범위에서 포함했다.
- GP 보안 수준(AL1/AL2)의 제품 구현 세부사항은 Root 키 자체 요구가 아니다. 발급 CA가 확인해야 할 접점은 04에 정리했다.
- 법률·개인정보·재무 조항은 운영 주체의 별도 의무로 식별한다. 공개 자료 밖의 실제 서명 계약, 비공개 심사 체크리스트, 관리자의 개별 유권해석은 확보하지 않았다. 따라서 문서 조사 완료와 실제 심사 통과는 별도다.

[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md
[spec]: https://github.com/c2pa-org/specifications/blob/9c58c8c27044e44e8601f6ab13f1bcac1376eb1f/build/site/specifications/2.4/specs/C2PA_Specification.html

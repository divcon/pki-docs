# 07. 반복 감사 기록

감사일: **2026-10-08 KST**. 서브에이전트 3명과 **총 3회 감사·교차 검증**을 수행했다. 고정 원문 대조에서 발견한 문서 오류를 교정했으며 최종 대조 범위에 미해소 문서 오류는 없다. 원문 자체의 불일치·해석 공백·정책 결정은 Q01–Q20으로 남겼다. 대상은 `root-key-design/conformance-analysis/`의 모든 분석 문서와 출처·추적 자료이며, 실제 key ceremony나 PKI 환경의 적합성 승인을 뜻하지 않는다.

## 원문과 판정 방법

- Conformance: `2466172859fad1215f7aaf7e3768b41a0ac29abc`; Specifications: `9c58c8c27044e44e8601f6ab13f1bcac1376eb1f`. checkout 수정 표시가 있는 자료는 그대로 신뢰하지 않고 `git show` 원문으로 대조했다.
- CP·Program·Governance·Additional·GP Security, CA/leaf YAML, 관련 certificate/CSR schema, Spec 2.4 §4·§13.2·§14.4–14.5·§15.9를 각 적용 범위에서 확인했다. CP/Program의 핵심 ceremony·등록 조항은 동일 커밋 PDF로 절·쪽을 교차 확인했다.
- 설계 산출물은 감사 대상이며 독립 규범 근거로 사용하지 않았다. 시작 시 수정되어 있던 `../key-ceremony.md`는 이번 교정 대상에서 제외했다. 감사 중 이 파일의 별도 내용 변화와 `../cloudhsm-key-options.md`의 추가를 관찰했으며, 두 파일을 덮어쓰거나 이 감사의 완료 범위에 포함하지 않았다.
- **주요 위반(major)**은 허용되지 않는 키 생성·사용·발급을 적합하다고 판단하게 하거나 핵심 통제·등록 조건을 반대로 설명하는 문제로 분류했다. 그 외 정책 주체·조건·의무 누락은 보완 대상으로 기록했다. 원문 간 불일치를 이 보고서의 위반 건수와 혼합하지 않았다.
- 한 회차는 분담 대조, 부모의 종합 및 해당 발견의 교정까지다. 다음 회차에서는 담당을 교체하여 수정된 내용을 다시 원문과 대조했다. 사용자가 지정한 상한은 주요 위반이 없는 한 **5회**다.

## 회차별 범위와 결과

| 회차 | 담당·범위 | 결과 |
|---|---|---|
| 1차 | `profiles_audit`: 01·관련 Q / `ceremony_audit`: 02·03·관련 Q / `enrollment_audit`: 04·관련 Q / 부모: 기준·원문 식별·05 통합 | 주요 위반 0. 재발급 금지의 발급자 한정, 감사 대응 세부조건, backup·종료 책임, 발급 전 검증과 TSA 요구, schema 차이 범위·leaf 정책 인계를 교정 |
| 2차 | `enrollment_audit`: 01 / `profiles_audit`: 02·03 / `ceremony_audit`: 04 / 각 담당의 Q 교차 대조, 부모: 전체 통합·위치 대응 | 주요 위반 0. 02·03 추가 교정 없음. 01·04의 아래 보완을 부모가 반영하고 교차 감사자가 실제 수정 문장을 재대조하여 모두 해소 확인 |
| 3차 | `ceremony_audit`: 01·관련 Q 29개 ID / `enrollment_audit`: 02·03·관련 Q 43개 ID / `profiles_audit`: 04·관련 Q 24개 ID / 부모: README·00·05 전체 정책 인계·출처·최종 검사 | 96개 ID의 현재 내용과 모든 대응 원문을 검증. First ICA의 `oneOf` 차이와 절/줄 표기를 추가 교정하고 반영 확인. 주요 위반 0, 미해소 문서 오류 0으로 종료. 원문 해석·수용 미확정은 아래 한계와 Q에 유지 |

담당을 교체하여 각 정책 묶음을 세 서브에이전트가 모두 읽었다. 3차에서 새로 찾은 사항까지 같은 회차의 교정·재확인으로 닫았으며, 주요 위반이 없어 5회 상한을 넘는 추가 회차는 수행하지 않았다.

## 주요 교정 사항

각 ID를 [원문 위치 대응표](06-source-map.md)에서 조회하면 독립 원문으로 바로 이동할 수 있다. 아래는 발견을 정책 단위로 묶은 기록이며 같은 발견의 중복 집계가 아니다.

| 회차 | 교정 대상 | 이전 요약의 문제 → 교정 결과 |
|---|---|---|
| 1차 | O17/O18, Q06 | rotation agility의 권고 주체를 CA의 장려 행위로 복원. 이미 발급된 키에 대한 금지는 **해당 CA가 발급했던 키**라는 주어를 보존하여 다른 CA의 cross-sign까지 일률적으로 금지하지 않음 |
| 1차 | O14/O16/O20, Q13/Q14/Q19/Q20 | 기타 키 backup의 조건부 보호를 추가. CA 파기 절의 No stipulation과 Subscriber 종료 시 파기 SHALL을 구별. 종료 통지 예외를 CA/RA 보안사고로 한정하고 충분한 전환 시간 조건을 복원 |
| 1차 | O19/O27 | 요청 시 감사보고서 제공 대상, 부적합·개선사항 명시·영문/전문번역·시정, GP 플랫폼/attestation 서비스 평가·remediation 권고를 명시. 사고 분석·보고 SHALL과 일반 독립감사 SHOULD를 분리 |
| 1차 | C01–C10, E03/E04, Q07/Q15 | CP 상세 script 구성의 `includes`와 상위 SHALL 연결, PDF 4(a)–(h)와 Markdown 목록 차이를 표시. CP 입회 및/또는 기록과 Program 독립 입회·signed script 제출, 제한적인 WebTrust 증거 대체를 구별 |
| 1차 | P06–P09, Q04/Q12 | leaf 수명·KU/EKU criticality·AL/CPL 확장을 발급 정책으로 명시. documentSigning OID 차이가 Claim Issuing뿐 아니라 AL1/AL2 certificate·CSR까지 총 6개 schema에 있음을 반영 |
| 1차 | E09–E13 | CPL record·attestationMethods·CA 증거 해독/처리 능력과 승인 Subscriber 접근 자격의 연결을 명시. revision 방식을 선택한 GP Applicant의 통지 책임과 CA 발급 검증을 연결 |
| 1차 | T01 | time-stamp 자체에 정확도를 정의하는 의무와 TSA 인증서 발급 시 공개 업무관행에 따른 식별·인증·검증을 추가. UTC(k) 소문자 shall과 on-device 조건 문장의 해석 공백을 별도 표시 |
| 1차 | E14/E15/E16, Q16–Q18 | GP/VP 추가 요구의 역할·버전 조건 및 material change 재신청을 CA 요건과 분리. No stipulation인 법무 절을 구체 의무처럼 취급하지 않음. 목록 removal/record revoked 표현 차이 기록 |
| 2차 | K02/P05 | 인증서 서명 해시를 SHA-256/384/512로 명시. Claim·timestamp·OCSP 응답의 세 목적 중 최대 하나에만 유효해야 하는 leaf 조건을 명시 |
| 2차 | Q04, P02–P04/P06–P08 | caIssuers SHOULD를 강제하는 certificate schema의 영향 범위를 세 ICA에서 Claim AL1/AL2·TSA leaf까지 6개로 확대. CDP 우회는 ICA/TSA leaf에 있고 Claim leaf에는 없음을 구분. CSR 6개에 같은 accessMethod 강제가 없음을 별도 확인 |
| 2차 | E11/T01 | AL2 키가 hardware-backed keystore/KMS에서 생성·저장되었는지와 GP instance 보유를 검증하는 의무를 명시. NIST CVSS v3 이상 기준을 보존. TSA 오차 탐지 SHALL과 TSU 발급중지 SHALL을 각각 명시 |
| 3차 | Q04/P02, 근거 표기 | First ICA schema의 `oneOf` 때문에 OCSP+caIssuers AIA와 CDP를 모두 넣으면 실패하는 차이를 추가. CP/YAML의 동시 포함 허용을 금지로 바꾸지 않음. T01 §4.4(3)·CA Representations §9.6.1 및 Program 마지막 줄 531의 링크 범위를 정정 |

## schema 차이의 재현 범위

원문에서 관련 JSON Schema 제약을 추출하여 Python `jsonschema`의 Draft 2020-12 validator로 확인했다. 이는 **제약 조각의 동작 확인**이다. 완전한 certificate/CSR JSON, 실제 DER, 서명·체인, 공식 C2PA checker, 실제 CA/HSM을 검증한 결과가 아니다. 예시에서 AIA의 critical=false와 HTTP URI 등 다른 관련 필드는 맞춘다. [schema-probe-results.json](schema-probe-results.json)에 고정 원문 버전·검증기 버전·입력 구성·정확한 JSON 제약 경로 및 **74개 사례**의 결과를 남겼다(2차 68개, 3차 동시 포함 6개 추가). 이 사례들이 schema의 모든 가능한 차이를 열거하거나 모든 입력을 검증한 것은 아니다.

| 대상·관련 입력 | 확인한 결과 | 원문 위치 |
|---|---|---|
| ICA 3종·Claim AL1/AL2·TSA leaf certificate: OCSP-only AIA | caIssuers의 필수 `contains` 때문에 실패. YAML에서는 caIssuers SHOULD | [Q04](06-source-map.md#q04) |
| 같은 certificate 6종: OCSP+caIssuers AIA, CDP 없음 | 관련 AIA 제약 통과 | [Q04](06-source-map.md#q04) |
| 같은 certificate 6종: OCSP+caIssuers AIA와 CDP 모두 포함 | **First ICA만 `oneOf` 때문에 실패**, 다른 다섯 종류는 해당 제약 통과. CP/YAML의 동시 포함 금지가 아님 | [Q04](06-source-map.md#q04) |
| ICA 3종·TSA leaf certificate: CDP + caIssuers-only AIA | 관련 AIA/CDP 제약 통과하지만 YAML AIA의 OCSP MUST를 충족하지 않음 | [Q04](06-source-map.md#q04) |
| Claim AL1/AL2 certificate: CDP + caIssuers-only AIA | 별도 OCSP 필수 제약 때문에 실패. ICA/TSA leaf와 결과가 다름 | [Q04](06-source-map.md#q04) |
| 위 6개 역할의 CSR schema | 구조 대조에서 AIA non-critical·HTTP URI 형식 검사와 accessMethod 강제 부재를 확인. certificate와 같은 검증이라 하지 않음 | [Q04](06-source-map.md#q04) |
| Claim Issuing·AL1·AL2 certificate/CSR: c2pa-kp-claimSigning + 표준 documentSigning | EKU 제약 실패. 잘못된 private OID를 표준 OID의 동의어로 인정하지 않음 | [Q12](06-source-map.md#q12) |
| 같은 EKU 제약: c2pa-kp-claimSigning + emailProtection | 해당 EKU 제약 통과 | [Q12](06-source-map.md#q12) |
| Root certificate의 AKI | `contains` 구조 대조 및 해당 조각 검사에서 AKI 부재는 실패·존재는 통과. YAML의 OPTIONAL과 차이. 실제 키 일치나 전체 profile 충족을 입증하지 않으며 CSR에 같은 차이가 있다고 확장하지 않음 | [Q11](06-source-map.md#q11) |

다른 감사자는 위 표의 입력과 06의 정확한 제약 위치로 같은 판단을 재현할 수 있다. schema 실패를 CP 위반과 자동 동일시하지 않으며 schema 통과도 CP 준수의 충분조건이 아니다.

## 최종 검증과 요청 범위 대응

| 요청·확인 대상 | 완료 근거 |
|---|---|
| 원본 반영의 정확성·반복 교차 감사 | 01–05의 전체 요구사항 및 비표 형식 문단을 분담·담당 교체로 3회 대조. 위 교정표와 최종 96개 ID 대응에 결과 반영. README·00의 정의·버전·범위도 원문 대조 |
| 정책 우선, 의무·권고·허용·설계 제안 구분 | CP 대문자 규칙과 Spec 대소문자 규칙, script `includes`, 소문자 must/shall/should, 조건부 의무를 구별. 특정 vendor·고정 quorum·코드·도구 선택은 정책 의무로 추가하지 않음 |
| 원문 모호성 별도 기록 | 05의 Q01–Q20과 적용되는 정책 확정 시점·확인할 사항. 이미 범위로 구별 가능한 내용과 외부 수용 확인·자체 정책 결정을 분리 |
| Ceremony·키 관리·감사 대응 | K01–K06, O01–O28, C01–C10, E01–E16/T01의 통제·증거·책임·예외를 대조. 05의 정책 인계표로 연결 |
| 즉시 찾을 수 있는 독립 근거 | 06과 JSON에 **96개 ID, Git 원문 251개 줄 묶음 + 보충 RFC 참조 1개**. 모든 줄 묶음의 위치·SHA-256·URL과 주장/확인점을 검증 |
| 자료·문서 구조 검사 | 원문 **33개**의 Git blob ID·SHA-256·크기·텍스트 줄 수 일치. CA/leaf 내장·별도 YAML **8쌍** 일치. 9개 Markdown의 참조 정의·로컬 링크/ID anchor·고정 GitHub 줄 범위·표 구조 및 `git diff --check` 통과 |
| schema 동작 확인의 한계 | 74개 **제약 조각** 사례 결과와 정확한 JSON 경로 보존. 이것으로 전체 checker·DER·서명·체인·운영 환경의 적합성을 주장하지 않음 |

## 남은 정책 판단과 감사의 한계

[Q01–Q20](05-design-inputs-and-open-questions.md)은 자료 불일치, 축약 문구, 적용 범위 구분, 수용 조건 또는 프로젝트 정책 결정으로 분류했다. Q03의 발급자 SKI 규칙은 Spec의 RFC 규범 참조로 확인했고 Q09는 CA 상태 서비스·claim generator의 적용 범위를 구분했다. 이런 항목을 모두 동일한 미해결 표준 충돌로 보지 않는다.

생성·보관 모듈 인정 범위, 상위 미등록 CA 책임, TSA 계층, 독립 입회/증거 대체 수용, cloud off-site와 backup/archive·retired key 경계, 종류별 증거 보존기간 등은 선택한 운영 형태에 맞춰 확정해야 한다. 이번 감사가 공개되지 않은 심사기준이나 C2PA의 수용 결정을 대신하지 않는다.

고정 원문의 정확한 반영과 실제 신청·운영의 적합성은 별도다. 최신판 조사, 계약 서명·등록 신청, 실제 key ceremony, HSM/복구 시험, PKI 구현은 수행하지 않았다.

## 감사 후 범위 명확화 — 2026-10-08

키 세레모니가 ICA 키 생성과 인증서 발급 중 어디까지 포함하는지에 관한 후속 검토에서, 주 담당자가 동일 고정 커밋의 CP §4.4(L511–515)·§6.1.1(L779–813), Program L378–382·L458–460을 재대조했다. 앞선 3회 교차 감사와 구분되는 설명 보완이다.

- 제3장에 ICA 키 생성과 상위 CA의 인증서 서명·발급을 구분하고, C10의 “함께 발급한다면”을 생성과 별도로 진행하는 CA 인증서 발급에도 적용되도록 명확히 했다. 기존 O02와 원문에 있던 적용 범위를 그대로 드러낸 것이다.
- 기존 Root 키 사용 시 생성 대상은 새 ICA 키이며, Root에는 매 서명의 발급 통제가 적용된다는 해석을 표시했다. Program의 등록 키 생성 입회·signed script를 모든 후속 인증서 서명의 독립 입회 의무로 확대하지 않았다.
- 제5장에 키 생성·CSR·발급·검증을 연결하는 절차와 증거 인계를 프로젝트 정책 제안으로 추가했다. 단일 행사·동일 날짜·장소를 C2PA 필수로 만들지 않았다. README에도 단계별 구분을 반영했다.
- 기존 C01–C10·O02–O03·E02–E04의 원문 대응을 사용하며 새 규범 요구사항이나 해석 질문 ID를 만들지 않았다.
- 보완 후 원문 33개·96개 ID·251개 원문 줄 묶음의 식별·대응, 9개 Markdown의 링크 482개·표 구조 및 `git diff --check`를 확인했다. 구조 검사 오류는 없었다. 인증서·schema·HSM 실행 시험을 추가한 결과는 아니다.

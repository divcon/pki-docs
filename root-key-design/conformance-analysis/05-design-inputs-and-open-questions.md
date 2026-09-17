# 05. 설계 반영 후보와 해석 확인 사항

이 문서는 후속 설계 반영의 입력이다. 기존 설계 요구사항의 확정·승인이나 실제 적합성 선언은 아니다.

## 바로 요구사항으로 추적할 후보

| 설계 분야 | 원문 기반 요구사항 | 연결 ID |
|---|---|---|
| CA topology·용도 | Root/First/Claim Issuing/TSA Issuing 역할 분리, pathLen·허용 서명 용도·CA와 leaf 구분 | P01–P05, U01–U06 |
| 키·모듈 | CA 알고리즘 최소값, 적합 모듈 생성·보관, 평문 경계 이탈 금지, 단독 접근 차단 | K01–K05 |
| 발급 | 문서화·trusted roles 다인 통제·split knowledge, Root의 매 인증서 서명 2명 및 명시적 실행 | O02–O03 |
| ceremony | CP 8개 script 항목, 생성 실통제, 등록 키의 독립 입회·signed script | C01–C10, E02–E04 |
| lifecycle | protected backup·off-site·연간 계획 검토·private key archive 금지, rotation·새 키, 변경·종료 절차 | K06, O07, O14–O20 |
| 운영 기록 | 만료+1년 발급기록, 상세 audit·보호·검토, 종류별 archive 정책 | O11–O13 |
| 폐지·가용성 | Claim OCSP 보존기간, ICA/TSA OCSP 또는 CRL, 72시간 요청 처리 조건, 24×7 상태 저장소 | O21–O26 |
| 조직·책임 | 공개 관행, MFA·배경조사·보안인가·교육·직무 분리·보안 통제·Root 책임 | O01, O03–O10, O28 |
| 심사 | production 인증서·PEM set·profile 및 ceremony 증거·계약·Intake·승인 | E01–E08, E16 |
| Issuing/TSA 인계 | GP conformance·AL·attestation·398일 재인증, 별도 TSU 보안·시간 요구 | E09–E13, T01 |

후속 설계의 각 요구사항에 위 ID, 원문 URL/버전, 구현 책임 주체, 증거 위치, 검증 상태를 함께 붙일 것을 제안한다. 구현 책임 조직 이름이나 특정 cloud vendor는 이번 조사로 확정하지 않는다.

## 원문 충돌·해석 질문

| ID | 관찰한 원문과 불확실성 | 설계에 미치는 영향 / 확인할 질문 |
|---|---|---|
| Q01 | [CA generation][generation]은 FIPS140-2 L2+/140-3 L2+/CC EAL4+ 대안을 쓰지만 [Key Storage][storage]는 FIPS140-2 L2+와 `3-tier data center`/commercial cloud 표현을 씀 | 140-3-only/CC 모듈을 저장·사용에도 인정하는지, First ICA 포함 범위·provider/시설 증빙은 무엇인지 C2PA에 확인. `3-tier`를 임의로 Uptime Tier III 인증 필수라고 번역하지 않음 |
| Q02 | [TSA Issuing YAML][tsa]의 Issuer는 Root Subject, AKI 설명은 Root 또는 Intermediate | First → TSA Issuing 계층이 허용되는지, 승인할 profile과 issuer 규칙은 무엇인지 확인. 직접 Root 발급 예시로 이 차이가 사라진 것처럼 보고하지 않음 |
| Q03 | [First ICA YAML][first]의 AKI는 ‘matching Subject Key Identifier’라 대상이 명확하지 않음 | Spec §14.5.1.1이 참조하는 RFC5280 AKI와 실제 issuer key를 기준으로 발급자 SKI를 대조하되, checker가 이를 검증하는지 확인. 자기 SKI 복사로 해석하지 않음 |
| Q04 | ICA YAML AIA의 caIssuers는 SHOULD인데 JSON schema에는 `contains` 제약이 있으며 description은 informational이라고 씀 | 실제 schema validator에서 SHOULD가 강제되는지 확인. JSON 검사의 성공·실패와 CP 요건을 각각 보고하고 공식 checker 버전/처리 방침 확보 |
| Q05 | Trust anchor로 subordinate 등록 가능. [CA Representations][warranty]는 Root의 Issuing CA 책임을 명시 | 미등록 상위 platform Root/First에 CP 운영통제가 적용되는 정확한 범위와 심사 증거 범위 확인. 포괄 면제는 가정하지 않음 |
| Q06 | [Usage][use]는 cross-certified CA 인증서 서명을 허용하지만 [Renewal][renew]은 이미 발급한 키 쌍의 새 인증서 발급을 금지 | 동일 키 cross-sign·정책 변경 재발급·CA 재인증 예외 여부 확인. 확인 전 예외를 설계에 넣지 않음 |
| Q07 | Program은 독립 입회·signed script 또는 적합한 WebTrust 보고서 대체를 명시하나 세부 수용 형식은 공개 문서에 없음 | 입회자 독립성, 원격 입회, sign-off 포맷, 기존 ceremony report 인정 범위 및 증거 보존·제출 방식 확인 |
| Q08 | [CP Proof of Conformance][identity]/Program Notice는 CPL 공개 전 서명 Notice 경로를 명시. Program 목록 운영에는 conformant CPL record만 발급하도록 표현 | 사전 공개 GP 발급 시 authoritative record와 DN/maxAL/status 검증 방법 확인. 모든 production 발급을 공개 CPL 뒤로만 제한하거나 무조건 Notice-only로 허용하지 않음 |
| Q09 | CP Certificate Status Services의 조건부 CRL 의무와 CRL Profile의 일반적 ‘not require’ 문구, Spec §14.5.2의 claim generator CRL 금지는 서로 다른 범위 | CA status는 조건부 의무를 적용하고 C2PA manifest는 OCSP 사용. 공식 checker/validator가 지원하는 경로와 장애 동작 확인 |
| Q10 | [CP Maximum Assurance Level][identity]은 maxAL 이하 모든 수준 발급 SHALL, [Certificate Issuance][issue]는 요청 AL evidence 실패 시 하위 AL 평가 MAY | 낮은 AL 지원 의무와 개별 요청 downgrade 선택의 관계 확인. evidence 미충족 상태로 발급하라는 의미로 해석하지 않음 |
| Q11 | [Root YAML][root]은 AKI OPTIONAL이나 [Root certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json#L1013-L1045)는 AKI를 필수 `contains`로 검사 | CP의 선택 요건은 유지하면서 schema 불일치를 보고. AKI 생략 인증서의 수용 여부와 공식 checker 수정/예외 적용 방침 확인 |
| Q12 | [Claim Issuing certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.cert.schema.json#L1129-L1155) 및 [CSR schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/claimSigningIssuingCA.csr.schema.json#L980-L1006)의 documentSigning 분기는 `1.2.840.113583.1.1.5`, Spec §14.4.1은 `1.3.6.1.5.5.7.3.36` | 표준 documentSigning-only 조합의 schema 실패를 숨기지 않음. 다른 OID를 동의어로 취급하지 않고 발급 profile/공식 checker 수용 방침 확인 |

이 항목들은 **공식 문서 간 차이 또는 적용 범위의 불확실성**을 정리한 것이다. 관련 설계를 확정하기 전에 C2PA의 해석과 심사 시 수용 조건을 확인하고, 그 결과를 요구사항과 검증 기준에 반영한다.

## C2PA 필수로 오인하지 않을 설계 선택

- offline Root, air gap, 2-of-3/3-of-5 같은 고정 수치, 특정 HSM vendor·region·OS·CLI, Lambda 사용/금지는 공개 원문이 지정하지 않는다.
- Root 20년·First ICA 5년은 예시다. Claim Issuing 1827일·TSA Issuing 5479일은 최대치다.
- 전체 CA의 연례 WebTrust 감사는 의무로 쓰지 않는다. 일반 compliance audit는 SHOULD, CA backup/recovery 계획의 연간 검토는 SHALL이다.
- m-of-n dual control과 split knowledge를 애플리케이션 승인 두 개 또는 threshold signature 알고리즘 하나로 자동 충족했다고 선언하지 않는다. 수단 선택과 우회 방지 검증은 설계 과제다.
- key destruction 방식·고정 log 보존연수·구체 RTO/RPO·긴급 복구 운영 수치는 본문에서 확정하지 않는다. 선택하면 프로젝트 정책으로 표시한다.
- 양자내성 CA 알고리즘이나 범용 firmware signing을 C2PA CA 키의 허용 용도로 추가하지 않는다. 별도 용도/키 분리는 후속 설계 결정이다.

[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[storage]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L827-L857
[tsa]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml
[first]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/intermediateCa.cert.yaml
[warranty]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L1520-L1564
[use]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L539-L571
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529
[renew]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L573-L585
[identity]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L401-L485

[root]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.yaml

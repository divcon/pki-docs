# 05. 설계 반영 후보와 해석 확인 사항

이 문서는 후속 설계 반영의 입력이다. 기존 설계 요구사항의 확정·승인이나 실제 적합성 선언은 아니다. 각 ID의 근거 파일·고정 줄·절은 [원문 위치 대응표](06-source-map.md)에 있다. 아래의 질문은 원문 오류를 임의로 수정하거나 예외를 승인한 결과가 아니다.

## 바로 요구사항으로 추적할 후보

| 설계 분야 | 원문 기반 요구사항 | 연결 ID |
|---|---|---|
| CA topology·용도 | Root/First/Claim Issuing/TSA Issuing 역할별 프로파일, pathLen·허용 서명 용도·CA와 leaf 구분. 전용 First ICA를 반드시 두라는 뜻은 아님 | P01–P09, U01–U06 |
| 키·모듈 | CA 알고리즘 최소값, 적합 모듈 생성·보관, 평문 경계 이탈 금지, 단독 접근 차단 | K01–K05 |
| 발급 | 문서화·trusted roles 다인 통제·split knowledge, Root의 매 인증서 서명 2명 및 명시적 실행 | O02–O03 |
| ceremony | CP 8개 script 항목, 생성 실통제, 등록 키의 독립 입회·signed script | C01–C10, E02–E04 |
| lifecycle | protected backup·off-site·연간 계획 검토·private key archive 금지, rotation·새 키, 변경·종료 절차 | K06, O07, O14–O20 |
| 운영 기록 | 만료+1년 발급기록, 상세 audit·보호·검토, 종류별 archive 정책 | O11–O13 |
| 폐지·가용성 | Claim OCSP 보존기간, ICA/TSA OCSP 또는 CRL, 72시간 요청 처리 조건, 24×7 상태 저장소 | O21–O26 |
| 조직·책임 | 공개 관행, MFA·배경조사·보안인가·교육·직무 분리·보안 통제·Root 책임 | O01, O03–O10, O28 |
| 심사 | production 인증서·PEM set·profile 및 ceremony 증거·계약·Intake·승인 | E01–E08, E16 |
| Issuing/TSA 인계 | GP conformance·AL·attestation·398일 재인증, 별도 TSU 보안·시간 요구 | E09–E13, T01 |

후속 정책의 각 요구사항에 위 ID, 원문 URL/버전, 책임 주체, 승인·보존할 증거, 검증 상태를 함께 붙일 것을 제안한다. 구체 조직 이름이나 특정 cloud vendor는 이번 조사로 확정하지 않는다.

## 원문 충돌·해석 질문

**자료 불일치**는 원문 사이의 차이가 확인된 상태, **해석 미확정**은 문구의 적용 범위·수용 조건이 정해지지 않은 상태, **범위로 구분**은 모순처럼 보이던 내용을 적용 대상에 따라 구별할 수 있는 상태다. **정책 결정 필요**는 원문이 수치·방법·경계를 정하지 않아 운영 주체가 정해야 하는 항목이다. 모든 질문을 동등한 표준 위반으로 집계하지 않는다.

| ID | 관찰한 원문과 불확실성 | 설계에 미치는 영향 / 확인할 질문 |
|---|---|---|
| Q01 | **해석 미확정** — [CA generation][generation]은 FIPS140-2 L2+/140-3 L2+/CC EAL4+ 대안을 쓰지만 [Key Storage][storage]는 FIPS140-2 L2+와 `3-tier data center`/commercial cloud 표현을 씀 | 140-3-only/CC 모듈을 저장·사용에도 인정하는지, First ICA 포함 범위·provider/시설 증빙은 무엇인지 C2PA에 확인. `3-tier`를 임의로 Uptime Tier III 인증 필수라고 번역하지 않음 |
| Q02 | **자료 불일치** — [TSA Issuing YAML][tsa]의 Issuer는 Root Subject, AKI 설명은 Root 또는 Intermediate | First → TSA Issuing 계층이 허용되는지, 승인할 profile과 issuer 규칙은 무엇인지 확인. 직접 Root 발급 예시로 이 차이가 사라진 것처럼 보고하지 않음 |
| Q03 | **축약 문구** — [First ICA YAML][first]의 AKI는 ‘matching Subject Key Identifier’라 대상이 명확하지 않음 | Spec §14.5.1.1이 참조하는 RFC5280 AKI와 실제 issuer key를 기준으로 발급자 SKI를 대조한다. 자기 SKI 복사로 해석하지 않음. YAML 문구와 checker의 관계 검증 범위를 구별 |
| Q04 | **자료 불일치** — 세 ICA·Claim AL1/AL2·TSA leaf의 YAML에서 caIssuers는 SHOULD이나 **certificate schema 6개**는 AIA가 있으면 강제. 세 ICA·TSA leaf는 CDP+caIssuers-only AIA의 OCSP 누락을 검출하지 못하나 Claim leaf는 실패. **First ICA만 `oneOf`로 완전한 OCSP+caIssuers AIA와 CDP 동시 포함을 거부**하며 CP/YAML은 이 조합을 금지하지 않음. 같은 역할의 CSR에는 이 accessMethod 강제가 없음 | 관련 제약 조각을 표준 JSON Schema 검증으로 재현했다(07 감사 기록). schema 통과가 CP 충족을 입증하지 않으며, 권고 미채택이나 CP가 허용하는 두 status 경로의 동시 포함을 CP 위반으로 바꾸지 않음. certificate/CSR 차이와 공식 checker 수용 방침을 구분 |
| Q05 | **해석 미확정** — Trust anchor로 subordinate 등록 가능. [CA Representations][warranty]는 Root의 Issuing CA 책임을 명시 | 미등록 상위 platform Root/First에 CP 운영통제가 적용되는 정확한 범위와 심사 증거 범위 확인. 포괄 면제나 상위 키의 모든 용도에 대한 일률적 적용을 확정하지 않음 |
| Q06 | **해석 미확정** — [Usage][use]는 cross-certified CA 인증서 서명을 허용하고 [Renewal][renew]은 동일 키 renewal 금지 및 **해당 CA가 이미 인증서를 발급한** 키 쌍에 새 인증서 발급 금지를 명시(`for which it had previously issued`) | 다른 CA의 최초 cross-sign까지 모두 금지한다고 확대하지 않음. 자기서명 Root renewal, 같은 발급 CA의 동일 키 재발급, 다른 CA의 cross-sign을 구별하여 실제 시나리오의 수용 범위 확인. cross-sign 허용을 renewal 예외로도 사용하지 않음 |
| Q07 | **해석 미확정** — Program L382는 독립 입회·signed script 제출 증거를 적합한 WebTrust 보고서로 대체 가능하다고 쓰고, L460은 독립 입회·scripted process·C2PA 검토 가능성을 다시 요구 | 보고서가 다루는 키·행사·script·심사기준, 추가 원자료 검토 범위, 입회자 독립성·원격 입회·sign-off 수용 형식 확인. 실제 ceremony 수행·CP 통제·script 보유까지 면제하지 않음 |
| Q08 | **해석 미확정** — CP L461은 signed Notice 수령·검증 SHALL, L463은 공개 CPL로 proof 충족 MAY. Program L474는 공개 전 production 발급 경로, L498은 conformant CPL record에만 발급 MUST | 공개 전 Notice 속 CPL record의 권위와 DN/maxAL/status 검증 방법, 공개 후 CPL만으로 Notice 수령·검증을 대체할 수 있는지 확인. 공개 전 발급 전면 금지나 무조건 Notice-only 허용을 새 정책으로 단정하지 않음 |
| Q09 | **범위로 구분** — CP Certificate Status Services의 조건부 CRL 의무와 CRL Profile의 일반적 ‘not require’, Spec §14.5.2의 claim generator CRL 금지는 적용 대상이 다름 | CA는 Claim OCSP 필수 및 ICA/TSA에 OCSP가 없을 때 CRL 필수. claim generator의 stapling 정책은 OCSP SHOULD·CRL 금지이며 CA의 조건부 CRL 의무를 없애지 않음. 실제 검증기의 경로 지원은 별도 검증 |
| Q10 | **해석 미확정** — CP L467은 maxAL 이하 모든 수준 발급 SHALL, L521은 maxAL에 따른 dynamic evidence SHALL, L529는 요청 AL 실패 시 하위 AL 평가 MAY. 부록 AL2는 증거 실패 시 `a certificate` 발급 금지로 서술 | AL2 제품의 AL1 요청에 요구할 증거 범위, 낮은 AL 지원 의무와 개별 downgrade 재평가의 관계 확인. 해당 AL의 증거를 충족하지 못한 상태로 발급하라는 의미로 해석하지 않음 |
| Q11 | **자료 불일치** — [Root YAML][root]은 AKI OPTIONAL이나 [Root certificate schema](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/cert-profiles/rootCA.cert.schema.json#L1013-L1045)는 AKI를 필수 `contains`로 검사 | CP의 선택 요건은 유지하면서 schema 불일치를 보고. AKI 생략 인증서의 수용 여부와 공식 checker 수정/예외 적용 방침 확인 |
| Q12 | **자료 불일치** — Claim Issuing 및 Claim leaf AL1/AL2의 certificate·CSR **6개 schema**의 documentSigning 분기는 `1.2.840.113583.1.1.5`, Spec §14.4.1은 `1.3.6.1.5.5.7.3.36` | 필수 c2pa-kp-claimSigning과 표준 documentSigning만 있는 조합은 해당 schema 조건을 만족하지 못함. 다른 OID를 동의어로 취급하지 않고 발급 profile/공식 checker 수용 방침 확인. 01·06에 6개 위치를 매핑 |
| Q13 | **정책 결정 필요** — CP L843–849는 backup 전부 추적·원본과 동일 다인 통제·최소 한 사본 off-site를 요구하지만 cloud에서 site의 경계·거리·region·계정 기준을 정하지 않음 | 백업 위치·장애 영역·custody·복구 접근의 범위를 정책에 정하고 준수 근거를 남김. 같은 provider의 자동 복제만으로 off-site 충족을 선언하거나 multi-region을 원문 필수로 만들지 않음 |
| Q14 | **정책 결정 필요** — CP L843–853은 CA backup 의무와 private key archival 금지를 함께 규정하나 둘의 경계·retired key 종료 시점을 정의하지 않음. L857 Key Destruction은 No stipulation. L717–729 기록 보존정책과 L375 발급기록 만료+1년은 별도 | 활성·복구·퇴역 키의 사용 가능 기간과 backup 종료·폐기 기준, script·입회·로그·감사보고서의 보존기간을 정함. 모든 증거가 만료+1년이면 충분하다고 단정하지 않으며 archival 금지를 backup 생략 근거로 쓰지 않음 |
| Q15 | **해석 미확정** — CP L793은 독립 입회 및/또는 recorded, L811은 participants and witnesses sign-off를 열거. recorded의 형식과 recording-only일 때 witness sign-off 처리가 구체적이지 않음 | CP 범위에서 recording-only를 택할 때 기록 형식·서명자 수용 조건 확인. Program 등록 대상 키는 E03/E04의 별도 입회·증거 경로를 따름. 영상만으로 등록 증거를 완료했다고 하지 않음 |
| Q16 | **편집상 해석 미확정** — CP L935의 Backend TSA time source 선택 뒤 `In such a case ... following procedure:`가 있고, L937–939에 on-device TEE 실행·키 생성/저장 SHALL이 이어짐 | 뒤 두 항의 적용 범위인지 누락된 절차인지 확인. 이를 근거로 on-device TEE 보호를 면제하지 않음. T01의 UTC(k) 추적은 CP L919의 소문자 shall임도 별도 표시 |
| Q17 | **해석 미확정** — CP L371은 공개 CPS 또는 C2PA 협의 대체수단 허용, L1540/L1548/L1556은 검증 절차를 CA CP/CPS에 기술했다는 보증 | 합의한 대체 문서가 보증 조항의 문서화도 충족하는지 확인. 대체 공개수단을 업무관행 공개 의무 면제로 해석하지 않음 |
| Q18 | **표현 차이·수용 확인** — Program L512–514는 CA/TSA 목록 removal, Governance L444–450은 revoked record 표시·이의 제기 | CA TL/TSA TL의 실제 제거·상태표시·이력 보존은 관리자 수용 절차와 연결. trust anchor 제거와 개별 인증서 폐지는 별도이며, 원문에 없는 처리 SLA를 생성하지 않음 |
| Q19 | **범위로 구분·잔여 해석** — CP L617은 escrow/recovery 미지원의 대상을 직접 명시하지 않고 L619는 Subscriber 책임을 규정. 별도 L843–849는 CA backup/recovery를 명시적으로 요구 | CA 자체 backup/recovery를 금지한다고 해석할 수 없음. Subscriber escrow 서비스와 CA 운영 복구를 구분하고, 기타 키의 backup은 허용된 경우에만 원 모듈과 일관된 보호를 적용. 모든 recovery를 포괄 허용하는 결론도 내리지 않음 |
| Q20 | **정책 결정 필요** — CP L485의 72시간은 Subscriber/C2PA 요청의 인증·유효성 검증 완료 후 시작. 그 검증 자체의 소요시간이나 L589–603의 다른 폐지 사유별 고정 SLA, 종료 후 상태 서비스 인계 방식은 여기서 정하지 않음 | 요청 검증 지연·사고 대응·키 접근·폐지·상태 서비스 연속성의 내부 책임과 기한을 정함. 원문 72시간을 검증 지연의 허가나 모든 사고에 대한 공통 면책시간으로 쓰지 않음. CA 종료로 O23/O24 의무가 자동 소멸하지 않음 |

이 항목들은 **공식 문서 간 차이, 적용 범위의 불확실성 또는 원문이 정하지 않은 정책 결정**이다. 외부 해석·심사 수용이 필요한 항목은 관련 설계 확정 전에 C2PA 확인 결과를 반영한다. 운영 주체가 정할 정책은 책임자의 승인과 선택 근거를 남기고, 원문 의무나 확인되지 않은 C2PA 승인과 구분한다.

## 정책 확정과 ceremony 인계

다음은 **프로젝트 정책 제안**이다. 실제 해당되는 질문을 결정 대장에 연결하여 책임자·판정일·적용 버전·답변 또는 선택 근거를 남긴다. 이 감사에서 운영 환경이나 C2PA 수용을 승인하지 않는다.

신규 ICA 구성 절차는 **`ICA 키 생성 → CSR 생성 → 상위 CA의 인증서 서명·발급 → 발급 인증서 검증`**까지 연결해 관리하는 것을 제안한다. 키 생성과 발급을 한 행사에 묶을지, 일정·조직에 따라 나눌지는 프로젝트 정책으로 정한다. 인용한 CP 조항은 이를 같은 날짜·장소의 단일 ceremony로 수행하도록 지정하지 않는다. 분리하는 경우에도 생성한 ICA 공개키·CSR·발급 인증서와 각 단계의 승인·수행 증거를 연결하도록 설계한다. 단계별 원문 의무는 [제3장](03-ceremony-script-requirements.md)의 구분을 따르며, 전체 순서를 하나의 “키 생성 세레모니”로 묶는 것 자체를 C2PA 필수로 표시하지 않는다. 추적: C01–C10, O02–O03, E02–E04.

| 확정 시점 | 결정할 정책과 증거 | 추적 ID |
|---|---|---|
| 키 생성 승인 전 | CA 역할·용도, 공개 업무관행, trusted roles와 단독 접근 방지, 생성·보관 모듈 인정 범위, 등록 대상 여부와 독립 입회/대체 증거 경로 | K01–K05, O01–O03, C01–C10, E02–E04, Q01/Q05/Q07/Q15/Q17 |
| backup·복구 정책 승인 전 | 원본과 backup 다인 통제, off-site 판단 근거, 연간 계획 검토, 퇴역·보관·폐기 및 증거 종류별 보존정책 | K06, O11–O16, Q13/Q14/Q19 |
| 인증서 발급 정책 승인 전 | 역할별 profile·기간·키 재사용 제한, schema 차이 처리, CA 발급의 다인 통제·생성 증거와 발급 증거의 연결, GP 승인·AL·TSA 발급검증 및 상태 서비스 | P01–P09, U01–U06, C10, O02–O03/O18/O21–O26, E09–E12, T01, Q02–Q04/Q06/Q08–Q12/Q16 |
| 등록·운영 인계 전 | 키와 실제 ceremony 증거의 연결, script sign-off·deviation, 제출 set·Intake, 요청받을 감사보고서와 시정·사고보고·목록 제거 대응 책임 | C07–C10, E01–E08/E16, O19/O27/O28, Q07/Q14/Q18/Q20 |

미확정 질문이 있다는 이유만으로 모든 설계를 중단할 필요는 없다. 선택한 계층·모듈·서비스·증거 경로에 영향을 주는 질문은 해당 정책의 확정 조건으로 남기고, 적용되지 않는 항목은 적용 제외 근거를 기록한다. 원문 의무를 줄이는 임시 해석은 채택하지 않는다.

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

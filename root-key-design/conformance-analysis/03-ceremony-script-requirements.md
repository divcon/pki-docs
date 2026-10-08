# 03. 키 생성 세레모니 스크립트 요구사항

CP v0.2 §6.1.1의 CA 키 생성 통제와 상세 스크립트 구성 항목을 추적한다. 이 절은 PDF 본문 21–22쪽(PDF 파일의 24–25쪽)의 “Key Pair Generation and Installation by CAs”에 해당한다. 실제 수행 순서·생성 전 확인·기록·중단 처리는 [Key Ceremony](../ceremony/README.md)에서 관리한다.

ID별 원문 파일·고정 줄·절은 [원문 위치 대응표](06-source-map.md)에 있다.

## 의무의 두 층

**모든 CA 키 생성**은 [CP Key Pair Generation and Installation by CAs][generation]의 상세 스크립트·공개 관행·통제를 따른다. CP는 독립 입회 **및/또는** 기록을 명시한다.

**CA TL/TSA TL에 올릴 Root 및/또는 ICA 인증서의 키**에는 [Program Certificate Policy][program-policy]가 독립 입회한 ceremony 증거와 **서명된 key generation script**를 요구한다. [Certification Authority Evidence Request][program-evidence]는 scripted process와 C2PA 검토 가능성도 요구한다. 따라서 영상만 있는 경우를 등록 증거의 충분조건으로 취급하지 않는다. 다만 적합한 ceremonies/scripts를 입증하는 **WebTrust for CA 보고서**를 제시하면 Program은 이 제출 요구를 면제할 수 있다고 한다. 모든 CA에 WebTrust 취득을 의무화하거나 다른 CP 통제까지 면제하는 조항이 아니다.

## 키 생성과 ICA 인증서 발급의 경계

새 ICA를 구성할 때의 **ICA 키 쌍 생성**과 **상위 CA의 ICA 인증서 서명·발급**은 적용 조항이 다른 작업이다. 같은 행사에서 수행하는지와 관계없이 각 단계의 통제를 적용한다.

| 단계 | 작업과 적용 요구사항 |
|---|---|
| ICA 키 쌍 생성 | 새 ICA의 개인키·공개키를 생성한다. [CP §6.1.1][generation]의 key generation ceremony 대상이며, 승인·생성·기록·sign-off·종료 후 보관 등 적용되는 C01–C09를 따른다. 등록 대상 키에는 위 Program 증거 요건도 적용한다. |
| ICA 인증서 서명·발급 | 상위 CA의 개인키로 **ICA 공개키를 담은 인증서**에 서명한다. [CP §4.4][issue]의 CA 인증서 발급 통제(C10, 제2장 O02)를 적용한다. ICA 개인키 자체에 서명한다는 뜻이 아니다. |

기존 Root 키로 새 ICA 인증서를 발급하는 경우, 새 키 생성 대상은 ICA 키이며 Root의 매 인증서 서명에는 발급 통제를 적용한다. 위 조항은 하위 CA 인증서를 발급할 때마다 기존 Root 키를 다시 생성하거나 그 키의 최초 생성 세레모니를 반복하도록 요구하지 않는다. 이는 **생성 대상과 서명에 사용하는 키를 구분한 적용 해석**이다. [CP 키 생성][generation], [CP 인증서 발급][issue]

Program의 독립 입회·signed key generation script는 **등록할 인증서에 포함된 키의 생성 증거**에 관한 요건이다. 이를 모든 후속 인증서 서명 작업의 독립 입회 의무로 확대하지 않는다. 생성 script의 수행 확인 서명과 상위 CA가 ICA 인증서에 하는 암호학적 서명도 서로 다른 증거·작업이다. [Program Certificate Policy][program-policy], [CA Evidence Request][program-evidence]

## CP가 직접 열거한 스크립트 항목

[CP §6.1.1(4)(a)–(h)][script]의 목록을 빠짐없이 대응시켰다. 이는 PDF 표기이며 Markdown에서는 목록 4의 하위 1–8이다. 같은 절 (2)는 상세 스크립트의 정의된 절차에 따라 키가 생성된다는 합리적 보장을 제공할 통제를 유지하도록 **SHALL**을 쓴다. (4)는 그 스크립트가 포함하는(`includes`) 구성을 열거하며 각 하위 항목에 SHALL을 반복하지 않는다.

| ID | 스크립트에 포함할 내용 | 적용 조건 / 제안하는 기록 형태 |
|---|---|---|
| C01 | 역할과 참여자 책임 정의 | operator·trusted approver·witness 등 역할과 담당자 식별 |
| C02 | 키 생성 ceremony 수행 승인 | 승인자·승인 일시·대상 키·승인된 script 버전 |
| C03 | 필요한 암호 하드웨어(Cloud HSM 포함)와 activation materials | 모듈·보안 경계·활성화 재료 inventory. 비밀값 자체를 스크립트에 넣지 않음 |
| C04 | ceremony에서 수행할 구체적 단계 | 명령·입력·검증·기대 결과·중단 조건을 정의하는 방식 제안 |
| C05 | ceremony 장소의 물리 보안 요구 | **Cloud HSM을 쓰지 않는 경우** 명시 항목. 일반 CA 보안 통제까지 면제되지 않음 |
| C06 | 종료 후 암호 하드웨어와 activation materials의 안전한 보관 절차 | **Cloud HSM을 쓰지 않는 경우** 명시 항목. 클라우드 activation 보호와 backup 의무는 여전히 적용 |
| C07 | 상세 script에 맞게 수행했는지에 대한 참여자·입회자 sign-off | 실제 수행 결과에 대한 서명. 계획서 승인만으로 대체하지 않음 |
| C08 | 상세 script에서 벗어난 사항 기록 | deviation과 처리 결정. 무편차라면 해당 사실도 남기는 것을 제안 |

C09 — 생성 환경·trusted roles·다인 통제·split knowledge·적합 모듈·입회/기록·logging은 스크립트의 목차만으로 충족되지 않는다. **실제로 수행하고 증거를 남겨야 하는 필수 조건**이다. [CP 1–3][generation]

C10 — **CA 인증서 발급에는 키 생성과 함께 수행하는지와 관계없이** [CP Certificate Issuance][issue]를 적용한다. 모든 CA 인증서 발급은 문서화된 절차와 trusted roles의 multiple-person control·split knowledge를 따른다(SHALL). Root의 모든 인증서 서명에는 trusted roles 최소 두 명(SHALL)과 그중 한 명의 deliberate command(원문 소문자 `must`)가 명시되어 있다. 생성 입회와 발급 승인, HSM 사용 승인을 한 종류의 서명으로 자동 치환하지 않는다. independent witness를 trusted role 수행 인원과 자동으로 동일시하지 않는다.

## 수용 조건 확인

독립 입회자의 자격·독립성, 원격 입회, 확인 서명의 형식과 증거 제출 방식은 공개 원문에 구체적인 형식이 없다. [해석 확인 사항 Q07](05-design-inputs-and-open-questions.md)에서 신청 시 수용 조건을 확인한다.

[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[script]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L783-L813
[program-policy]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L378-L382
[program-evidence]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md#L458-L460
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529

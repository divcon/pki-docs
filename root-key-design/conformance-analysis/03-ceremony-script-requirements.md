# 03. 키 생성 세레모니 스크립트 요구사항

CP v0.2 §6.1.1의 필수 항목을 추적한다. 이 절은 PDF 본문 21–22쪽의 “Key Pair Generation and Installation by CAs”에 해당한다. 실제 수행 순서·생성 전 확인·기록·중단 처리는 [Key Ceremony](../key-ceremony.md)에서 관리한다.

## 의무의 두 층

**모든 CA 키 생성**은 [CP Key Pair Generation and Installation by CAs][generation]의 상세 스크립트·공개 관행·통제를 따른다. CP는 독립 입회 **및/또는** 기록을 명시한다.

**CA TL/TSA TL에 올릴 Root 및/또는 ICA 인증서의 키**에는 [Program Certificate Policy][program]가 독립 입회한 ceremony 증거와 **서명된 key generation script**를 요구한다. `Certification Authority Evidence Request`는 scripted process와 C2PA 검토 가능성도 요구한다. 따라서 영상만 있는 경우를 등록 증거의 충분조건으로 취급하지 않는다. 다만 적합한 ceremonies/scripts를 입증하는 **WebTrust for CA 보고서**를 제시하면 Program은 이 제출 요구를 면제할 수 있다고 한다. 모든 CA에 WebTrust 취득을 의무화하거나 다른 CP 통제까지 면제하는 조항이 아니다.

## CP가 직접 열거한 스크립트 항목

[CP 해당 조항 4.1–4.8][generation]의 목록을 빠짐없이 대응시켰다.

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

C10 — CA 인증서를 함께 발급한다면 [CP Certificate Issuance][issue]도 적용한다. Root 인증서 서명마다 trusted roles 최소 두 명과 한 명의 deliberate command가 필요하다. 생성 입회와 발급 승인, HSM 사용 승인을 한 종류의 서명으로 자동 치환하지 않는다. independent witness를 trusted role 수행 인원과 자동으로 동일시하지 않는다.

## 수용 조건 확인

독립 입회자의 자격·독립성, 원격 입회, 확인 서명의 형식과 증거 제출 방식은 공개 원문에 구체적인 형식이 없다. [해석 확인 사항 Q07](05-design-inputs-and-open-questions.md)에서 신청 시 수용 조건을 확인한다.

[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529

# 03. 키 생성 세레모니 스크립트 요구사항

## 의무의 두 층

**모든 CA 키 생성**은 [CP Key Pair Generation and Installation by CAs][generation]의 상세 스크립트·공개 관행·통제를 따른다. CP는 독립 입회 **및/또는** 기록을 명시한다.

**CA TL/TSA TL에 올릴 Root 및/또는 ICA 인증서의 키**에는 [Program Certificate Policy][program]가 독립 입회한 ceremony 증거와 **서명된 key generation script**를 요구한다. `Certification Authority Evidence Request`는 scripted process와 C2PA 검토 가능성도 요구한다. 따라서 영상만 있는 경우를 등록 증거의 충분조건으로 취급하지 않는다. 다만 적합한 ceremonies/scripts를 입증하는 **WebTrust for CA 보고서**를 제시하면 Program은 이 제출 요구를 면제할 수 있다고 한다. 모든 CA에 WebTrust 취득을 의무화하거나 다른 CP 통제까지 면제하는 조항이 아니다.

## CP가 직접 열거한 대본 항목

[CP 해당 조항 4.1–4.8][generation]의 목록을 빠짐없이 대응시켰다.

| ID | 대본에 포함할 내용 | 적용 조건 / 제안하는 기록 형태 |
|---|---|---|
| C01 | 역할과 참여자 책임 정의 | operator·trusted approver·witness 등 역할과 담당자 식별 |
| C02 | 키 생성 ceremony 수행 승인 | 승인자·승인 일시·대상 키·승인된 script 버전 |
| C03 | 필요한 암호 하드웨어(Cloud HSM 포함)와 activation materials | 모듈·보안 경계·활성화 재료 inventory. 비밀값 자체를 대본에 넣지 않음 |
| C04 | ceremony에서 수행할 구체적 단계 | 명령·입력·검증·기대 결과·중단 조건을 정의하는 방식 제안 |
| C05 | ceremony 장소의 물리 보안 요구 | **Cloud HSM을 쓰지 않는 경우** 명시 항목. 일반 CA 보안 통제까지 면제되지 않음 |
| C06 | 종료 후 암호 하드웨어와 activation materials의 안전한 보관 절차 | **Cloud HSM을 쓰지 않는 경우** 명시 항목. 클라우드 activation 보호와 backup 의무는 여전히 적용 |
| C07 | 상세 script에 맞게 수행했는지에 대한 참여자·입회자 sign-off | 실제 수행 결과에 대한 서명. 계획서 승인만으로 대체하지 않음 |
| C08 | 상세 script에서 벗어난 사항 기록 | deviation과 처리 결정. 무편차라면 해당 사실도 남기는 것을 제안 |

C09 — 생성 환경·trusted roles·다인 통제·split knowledge·적합 모듈·입회/기록·logging은 대본의 목차만으로 충족되지 않는다. **실제로 수행하고 증거를 남겨야 하는 필수 조건**이다. [CP 1–3][generation]

C10 — CA 인증서를 함께 발급한다면 [CP Certificate Issuance][issue]도 적용한다. Root 인증서 서명마다 trusted roles 최소 두 명과 한 명의 deliberate command가 필요하다. 생성 입회와 발급 승인, HSM 사용 승인을 한 종류의 서명으로 자동 치환하지 않는다. independent witness를 trusted role 수행 인원과 자동으로 동일시하지 않는다.

## 설계에 사용할 대본 골격

아래 항목 구성과 증거 기록 형식은 **설계 제안**이다. 구체적인 HSM 명령과 운영 파라미터는 사용하는 HSM과 운영 절차에 맞춰 확정한다.

| 단계 | 대본에서 결정할 사항 | 통과 기준·증거 제안 | 연결 요구 |
|---|---|---|---|
| 1. 사전 고정 | 생성 키 역할, 등록할 TL, 알고리즘·강도, issuer/subject, profile, 유효기간, 적용 정책·프로파일 버전, script 버전 | 승인된 parameter sheet, 대상 역할·인증서 식별 | K01–K03, P01–P05, C01–C03 |
| 2. 환경 확인 | HSM 모델/서비스·firmware·승인 모드·모듈 검증 범위, 역할·MFA·시간·logging 상태 | 유효한 모듈 증거와 실제 구성, 다인 통제 확인. 실패 시 중단 | K03–K05, O03–O10 |
| 3. 접근·활성화 | 참여자/입회자 확인, 승인, activation custody | 실제 누가 무엇을 했는지 추적. 비밀/PIN/token 노출 금지 | C01–C03, O10 |
| 4. HSM 내부 키 생성 | 승인된 파라미터로 생성, handle/public key 식별, 필요한 backup 가능 속성 | 개인키 평문이 밖에 없음을 확인할 구성 증거. 공개키 fingerprint 연결 | K01, K03–K06, C04 |
| 5. CSR·인증서 발급 | CSR 서명·키 소유 및 public key 일치, 발급자 확인, profile 검사, Root 발급 승인·명령 | DER 서명·체인·KU/EKU·BC·기간·AKI/SKI·AIA/CDP 검증. CA 승인 보고서 | P01–P05, O02, C10 |
| 6. 백업·복구 인계 | 보호된 backup, 사본 식별·off-site 배치·다인 custody, 복구 절차 | backup 목록과 위치, 검증 기록. recovery 시험 방법은 별도 승인된 절차 | K06, O14–O16 |
| 7. 종료·증거 봉인 | 접근 종료, 재료 보관, key inventory 등록, 로그·입회 기록 수집, deviation 검토 | C07 sign-off, C08 deviation, 결과 인증서와 생성 이벤트의 연결 | C05–C09, O11–O13 |
| 8. 제출 패키지 | 등록별 PEM과 profile 검사, 서명 script·독립 입회 증거 또는 인정된 WebTrust 대체 자료 | 증거와 **실제로 등록할 공개키/인증서**의 일치 확인 | E01–E04(04 문서) |

## 기록 양식 제안

```text
ceremony_id / date_time_timezone / script_version_and_digest
source_versions / key_role / target_trust_list
approval_record / participants_and_roles / witness_independence
module_identity_and_assurance / activation_material_inventory_refs
approved_parameters / step_number / operator / action / actual_result
public_key_fingerprint / csr_fingerprint / certificate_fingerprint
backup_inventory_refs / offsite_location_ref / custody_refs
log_record_refs / witness_record_refs / deviations_and_disposition
participant_signoffs / witness_signoffs / conformance_statement
```

어느 단계에서든 실패·일탈하면 작업 중단, 재개 승인, 생성된 키의 취급, 재실행 시 새 ceremony와 연결하는 절차를 설계할 것을 제안한다. 원문은 구체적인 video 포맷, sign-off의 전자서명 알고리즘, 증거 파일명, 독립 입회자의 자격·독립성 상세 기준을 정하지 않는다. 이를 임의로 C2PA 필수 형식이라고 쓰지 않고 신청 담당자와 확인한다(Q07).

이미 생성된 키라면 나중에 script를 작성한 사실만으로 과거 독립 입회가 입증되지 않는다. 당시 증거와 허용 대체 보고서의 적합성을 확인하고, 부족하면 재생성 필요성을 판단하도록 설계한다.

[generation]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L779-L813
[program]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md
[issue]: https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md#L511-L529

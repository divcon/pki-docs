# Root Key 설계

Global과 CN이 공유하는 플랫폼 Root를 운영하고 C2PA를 첫 적용 대상으로 삼는다. 구조는 **Root → 공용 First ICA → 하위 Issuing ICA → leaf**다.

Root와 First를 새로 만드는 절차는 [Key Ceremony](ceremony/README.md)에서 시작한다. 현재는 설계안이며 생성 통제·운영 파라미터·참여자와 도구 검증이 남아 있다.

무엇부터 준비할지 검토하려면 [세레모니 준비 체크리스트](ceremony/preparation-checklist.md)를 먼저 읽는다. 스크립트는 [완성 샘플](ceremony/ceremony-script-sample.md), [작성용 템플릿](ceremony/ceremony-script-template.md), [작성 가이드](ceremony/script-writing-guide.md)로 나누었다.

| 문서 | 내용 |
|---|---|
| [Ceremony](ceremony/README.md) | 준비·스크립트 작성, CloudHSM 실행 절차, 감사 결과와 남은 검증 |
| [CA 앱 기능](ca-software-requirements.md) | 구현할 기능, 외부 책임, 준비 시점, 수용 시험과 원문 대응 |
| [다인 통제](dual-control-options.md) | 생성·서명·관리자 통제, CLI 세션과 승인 키, 우회 시험 |
| [요구사항과 확정 범위](requirements.md) | 확정된 구성·운영 조건과 해석 확인 사항 |
| [운영 모델](operating-model.md) | CA 계층, 하위 ICA 관리·인계, Global/CN 발급, OCSP·기록·백업 |
| [신뢰 앵커 교체](trust-anchor-migration.md) | 단말 신뢰 갱신, 침해 복구와 PQC 전환 |
| [C2PA 요구사항 대응표](c2pa-requirements-matrix.md) | 원문 요구의 설계 반영 위치와 남은 운영·감사 증빙 |
| [Conformance 분석](conformance-analysis/README.md) | 원문 조항별 키·프로파일·운영·ceremony·등록 요구와 해석 차이 |

정책 근거는 [conformance-public](../conformance-public/docs/v0.2/README.md)과 [specifications](../specifications/README.md)의 원문으로 확인한다. 출처·버전은 [자료 목록](../references/root-key-sources.md)과 [분석의 조사 기준](conformance-analysis/00-sources-and-scope.md)에 있다.

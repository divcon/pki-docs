# C2PA Claim Signing Certificate Enrollment

## 1. 결론과 문서 경계

원문의 공식 용어는 **C2PA Claim Signing Certificate**다. 이 프로젝트에서 먼저 사용한 “Manifest Signing Certificate”는 C2PA Manifest 안의 Claim을 서명하는 같은 자격증명을 가리키는 사용자 표현일 뿐, 별도 certificate profile이 아니다. Certificate Policy(CP)는 인증서를 conforming Generator Product의 특정 instance에 발급하고 그 제품을 Subject로 명명한다(`conformance-public@2466172:docs/v0.2/C2PA Certificate Policy.md:56-58`).

이 문서 집합의 핵심 결론은 다음과 같다.

1. C2PA는 enrollment JSON wrapper나 공통 Evidence container를 정하지 않는다. [Request body](01-Enrollment-Request-Body.md)의 field와 cardinality는 C2PA 의미를 운반하기 위한 `PROJECT` 선택이다. 이 문서 집합은 endpoint, response, state, idempotency, retry와 오류 체계를 설계하지 않는다.
2. AL1 automated enrollment의 C2PA semantic evidence는 적격 Generator Product instance가 CA의 secure credential로 인증됐다는 사실이다. AL2의 hardware-backed O.1~O.4 artifact를 AL1에 전이하지 않는다(CP:1686-1695; GSPR:330-376).
3. AL2는 O.1 product instance, O.2 requested key possession/protection, O.3 Claim Generator image/patch-or-revision, O.4 content/assertion-processing software image/patch-or-revision을 hardware Root of Trust가 뒷받침하는 artifact로 입증해야 한다(CP:1712-1751). O.5와 O.6은 AL2 issuance Dynamic Evidence 표에서 `No stipulation`이다(CP:1753-1759).
4. C2PA가 AL2 provider artifact 개수나 공통 wire array 개수를 정하지 않는다. 프로젝트 wrapper는 AL2에서 `evidenceItems`를 `1..N_p`로 요구하며, `N_p`와 한 item이 담는 provider artifact 의미는 승인된 provider profile이 정한다. profile이 없으면 AL2 production 경로는 비활성화한다.
5. PKCS#10 CSR signature는 requested private key의 PoP다. CSR PoP는 attestation이 말하는 platform/key property를 대신하지 않고, 반대도 마찬가지다(RFC 2986 §3, §4.2; CP:471-473).
6. 같은 key의 certificate renewal은 금지된다. CP의 re-key는 certificate issuance authentication과 key ownership/PoP를 새 신청과 동일하게 적용한다(CP:479-481, 573-579). 기존 조직·대표자 원자료를 매 re-key마다 다시 받는다는 뜻은 아니며, 저장된 identity approval은 398일 재인증 기한과 변경 trigger를 만족해야 한다. `INITIAL`과 `REKEY`는 `PROJECT` request-body 구분자이고 `RENEWAL` body는 처리하지 않는다.
7. Subscriber I/A/V, Agreement와 Notice/CPL 승인은 onboarding에서 재사용할 수 있지만, request 처리와 issuance 직전에는 저장된 승인·398일 재인증 기한·current CPL/status·requested AL 상한을 다시 확인한다. 원자료를 body에 재제출시키지 않는다.
8. 미승인 운영 결정에 의존하는 production profile은 비활성화한다. 현재 초기 상태에서는 [Operations Decision Register](03-Server-Validation-Traceability-and-Gaps.md#6-operations-decision-register)의 production-blocking `TBD` 때문에 AL1/AL2 production issuance가 모두 비활성화되어 있다.
9. CA가 수용한 product에는 CPL maximum 이하의 모든 Claim AL 요청 경로를 제공해야 한다(CP:465-467; Program:440-445). 따라서 max-AL2 product의 AL1/AL2는 한 enablement unit이며 어느 한쪽이 미준비이면 둘 다 비활성화한다. 이는 한 요청에서 두 인증서를 자동 발급한다는 뜻이 아니다.
10. GSPR O.5 AL2는 general applicability rule상 Edge, Backend와 Distributed 모두에 적용하는 runtime/static 의무다(GSPR:324-328,658-680). CP issuance Dynamic Evidence의 O.5 `No stipulation`과는 별개다(CP:1753-1759).
11. 2026-09-11에 사용자가 선택한 AL2 provider는 Google 신뢰 루트 기반 **Android Key Attestation**이다. CP:1796-1816에는 O.1~O.4 및 key profile의 21개 필드 가이드가 이미 있다. [Android 상세 매핑과 검증](02-CSR-and-Dynamic-Evidence-Requirements.md#android-key-attestation)에 이 누락을 보강했다. Provider 선택·원문 매핑 확인과 운영 profile 승인은 별개이며 실제 제품 기준값·지원 범위·freshness 정책 등의 `TBD`는 유지한다.
12. 2026-09-15 필드 단위 감사에서 누락된 [CSR DER 필드·OID·필수 값](02-CSR-and-Dynamic-Evidence-Requirements.md#csr-input-fields)과 [Android 필수 ASN.1 구조·타입](02-CSR-and-Dynamic-Evidence-Requirements.md#android-asn1-input)을 보강했다. JSON의 존재/null/타입, 고정 schema version과 placeholder도 분리했다. 구조상 필수 필드, C2PA profile의 값 가이드, 조건부 provider 요구와 미정 운영 승인값은 서로 대체하지 않는다.

### 1.1 인증 방식 요약

Enrollment의 “인증”은 단일 login 방식이 아니라 서로 다른 대상을 확인하는 계층이다.

| 계층 | 무엇을 증명하는가 | 재사용/재검사 |
|---|---|---|
| Subscriber I/A/V | 신청 조직의 identity와 대표자 authority | onboarding 결과 재사용 가능; ≤398일 재인증과 변경 시 갱신 |
| Agreement/Terms | 발급 범위에 대한 legally valid 계약/acknowledgement | 발급 전 current version/status 확인 |
| Secure enrollment credential | 현재 요청자가 승인된 Subscriber 측 주체임 | 모든 enrollment request에서 유효성 확인; 구체 방식은 CA CPS 결정 |
| GP instance authentication | 요청자가 적격 Generator Product의 실제 instance임 | INITIAL/REKEY마다 확인; 일반 Subscriber login만으로 대체 금지 |
| CSR signature/PoP | 요청 공개키의 private key를 보유·사용할 수 있음 | INITIAL/REKEY의 각 새 CSR에서 cryptographic verification |
| AL2 attestation | GP identity, hardware-backed requested key와 O.3/O.4 software 상태 | AL2 INITIAL/REKEY마다 fresh provider-signed Evidence 검증 |

이 계층들은 서로 대체되지 않는다. 상세 source와 body 포함 여부는 [Request Body §2](01-Enrollment-Request-Body.md#2-인증-방식은-하나가-아니다)에 있다.

## 2. 적용 범위와 request operation 의미

| request operation | 정의 주체 | 의미 | C2PA lifecycle 대응 |
|---|---|---|---|
| `INITIAL` | `PROJECT` | 서버가 인증된 GP instance에 부여한 `issuanceLineageId`에서 과거 발급·확정 successor가 전혀 없는 새 key의 첫 발급 | initial certificate issuance/application |
| `REKEY` | `PROJECT` | 새 key와 새 CSR로 기존 certificate를 교체하기 위한 발급 | CP re-key; 신규 신청과 같은 검증 |
| `RENEWAL` | `PROJECT` | same-key renewal을 뜻하는 구분자 | CP renewal은 금지; 해당 request body를 지원하지 않음 |

`REKEY` 발급만으로 기존 certificate가 자동 폐기되거나 즉시 사용 중단된다고 C2PA는 정하지 않는다. 구·신 certificate overlap, cutover와 추가 revocation은 운영 정책이며, 미결정이면 re-key production 경로를 비활성화한다.

## 3. AL × operation 전수 매트릭스

`CSR`은 PKCS#10 DER 한 개다. “semantic requirement”는 C2PA가 증명하라고 한 사실이고, “provider artifact 수”와 “project wire cardinality”는 서로 다른 축이다.

| AL / operation | CSR | C2PA semantic enrollment evidence | provider artifact 수 | project `evidenceItems` | freshness / binding | 결과 |
|---|---|---|---|---|---|---|
| AL1 / `INITIAL` | `1` | secure credential로 적격 GP instance 인증 | `NOT-SPECIFIED`; hardware artifact 의무 없음 | `0`(필드 금지) | credential과 PoP를 request·Subscriber·CPL에 서버가 결속 | 허용 가능 |
| AL1 / `REKEY` | `1`, 새 SPKI | AL1 instance 인증 + 새 신청과 같은 issuance auth/PoP; 저장된 I/A/V currentness 재검사 | `NOT-SPECIFIED`; hardware artifact 의무 없음 | `0`(필드 금지) | current approval 재검사; 이전/모든 발급 key와 다름 | 허용 가능 |
| AL1 / `RENEWAL` | `0` | 적용 없음 | `0` | `0` | same-key renewal은 CP가 금지 | 지원하지 않음 |
| AL2 / `INITIAL` | `1` | AL1 + hardware-backed O.1, O.2, O.3, O.4 전체 | `NOT-SPECIFIED`; 선택 profile에서는 `PROVIDER-PROFILE-DEFINED` | `1..N_p` | challenge를 쓰는 flow는 CA 값 exact-match; provider profile은 audience/CPL/AL/CSR SPKI 결속과 replay 방지를 요구 | provider profile 승인 시 허용 |
| AL2 / `REKEY` | `1`, 새 SPKI | AL2 O.1~O.4 전체를 새 issuance에 다시 평가 | `NOT-SPECIFIED`; 선택 profile에서는 `PROVIDER-PROFILE-DEFINED` | `1..N_p` | 새 request; challenge flow면 fresh challenge/Evidence; 새 CSR SPKI와 key artifact 일치 | provider profile 승인 시 허용 |
| AL2 / `RENEWAL` | `0` | 적용 없음 | `0` | `0` | same-key renewal은 CP가 금지 | 지원하지 않음 |

근거: AL은 CPL `maxAssuranceLevel` 이하일 수 있고 instance Dynamic Evidence에 따라 더 낮아질 수 있다(CP:36-42, 465-467). 다만 이 프로젝트는 silent downgrade를 하지 않으며 AL2 실패 뒤 AL1을 원하면 별도의 명시적 AL1 request가 필요하다.

## 4. 적용 시점 분류

| 요구 | 시점 | authority | modality / profile | 실행 지점 | 근거 |
|---|---|---|---|---|---|
| secure access credential | `WIRE` + `ISSUANCE-GATE` | `C2PA` | `REQUIRED`, `BASE` | transport credential 검증, `ISSUANCE-EXPLICIT` | CP:469-473, 507-509 |
| PKCS#10 CSR와 signature/PoP | `WIRE` + `ISSUANCE-GATE` | `RFC` + `C2PA` | RFC 2986 syntax; CP `REQUIRED`, `BASE` | `REQUEST-BODY-VALIDATION`, `ISSUANCE-EXPLICIT` | RFC 2986 §3/§4; CP:473 |
| Subscriber 조직·대표자 I/A/V | `ONBOARDING` + `ISSUANCE-GATE` | `C2PA` | `REQUIRED`, `BASE` | `ONBOARDING-REUSABLE`; current reference는 request/issuance에서 명시 검사 | CP:401-477, 491-509 |
| 발급 전 Subscriber Agreement/Terms | `ONBOARDING` + `ISSUANCE-GATE` | `C2PA` | `NON-BCP14-OBLIGATION`, `BASE` | legally valid/current agreement state를 request/issuance에서 명시 검사 | CP:1518-1558; CP:10-12의 대소문자 규칙 |
| 발급 후 certificate acceptance | `RUNTIME` | `C2PA` | `REQUIRED`, `BASE` | post-issuance 설치·사용에 의한 acceptance를 추적; 발급 전 Agreement gate를 대체하지 않음 | CP:531-535 |
| Notice/CPL, `generatorProduct`, DN, record ID, status, Max AL | `ONBOARDING` + `ISSUANCE-GATE` | `C2PA` | `REQUIRED`, `BASE` | `ONBOARDING-REUSABLE`, server currentness, `ISSUANCE-EXPLICIT` | CP:457-467, 519-527; Program:472-498 |
| AL1 GP instance authentication | `WIRE` + `ISSUANCE-GATE` | `C2PA` | `REQUIRED`, `AL1` | credential verdict와 server binding, `ISSUANCE-EXPLICIT` | CP:1686-1695; GSPR:338-358 |
| AL2 O.1~O.4 Dynamic Evidence | `WIRE` + `ISSUANCE-GATE` | `C2PA` | `REQUIRED`, `AL2` | `REQUEST-BODY-VALIDATION`, `ISSUANCE-EXPLICIT` | CP:1712-1751; GSPR:360-636 |
| provider schema, signer chain, artifact 수/format | `WIRE` + `ISSUANCE-GATE` | `C2PA` platform guidance + `PROVIDER` + `PROJECT` | `PROFILE-CONDITIONAL` | 운영 승인 후 body/issuance 검증; Android 필드 매핑은 02 §13 | CP:1764-1816; Google/AOSP의 §6 pinned 원문; CPL schema:88-105 |
| key generation/storage/use, O.1~O.6 implementation controls | `RUNTIME` | `C2PA` | `REQUIRED` 또는 원문 `No stipulation`; AL/class별 | `RUNTIME-ENFORCED`, conformance assessment | GSPR:324-744 |
| key rotation, same-key reuse 금지, revocation/status | `RUNTIME` + `ISSUANCE-GATE` | `C2PA` + `PROJECT` | CP `REQUIRED`; cutover는 `NOT-SPECIFIED` | issuance key history + operations/runtime | CP:539-609 |
| JSON request wrapper | `WIRE` | `PROJECT` | `REQUIRED`, `BASE` project contract | `REQUEST-BODY-VALIDATION`, `OPERATIONS-DECISION` | C2PA/RFC에는 JSON wrapper 없음 |

`WIRE`는 client가 보내는 값이라는 뜻이다. Current CPL status처럼 server-authoritative인 값은 body field가 아니지만 request 평가와 pre-issuance에서 명시 검사한다.

## 5. 집행 지점 요약

| 집행 지점 | 핵심 predicate | 상세 owner |
|---|---|---|
| Request body | profile/operation, CPL reference, CSR, AL별 Evidence field/cardinality와 binding | [Enrollment Request Body Matrix](01-Enrollment-Request-Body.md#5-enrollment-request-body-matrix) |
| issuance 직전 | credential/instance, I/A/V·Agreement, CPL/provider/reference, CSR/key history와 final TBS/profile/issuer/status currentness | [Server validation gates](03-Server-Validation-Traceability-and-Gaps.md#3-server-validation-gates) |
| operations decision | 인증 방식, algorithm 교집합, validity, provider/trust/reference, freshness, retention, revocation/cutover | [Operations Decision Register](03-Server-Validation-Traceability-and-Gaps.md#6-operations-decision-register) |
| runtime | private-key boundary/least privilege, claim-only use, rotation, O.3~O.6 controls, certificate/status refresh, incident stop/revocation | [CSR·Dynamic Evidence·runtime 경계](02-CSR-and-Dynamic-Evidence-Requirements.md) |

## 6. 원문 snapshot

로컬 원문은 working tree가 아니라 아래 commit blob이다. `conformance-public` working tree에는 EOL 차이와 CP line 1793의 별도 오염이 있어 기준에서 배제했다. Locator shorthand는 다음 exact identity를 뜻한다.

- `CP`: `conformance-public@2466172859fad1215f7aaf7e3768b41a0ac29abc:docs/v0.2/C2PA Certificate Policy.md:line`
- `Program`: 같은 commit의 `docs/v0.2/C2PA Conformance Program.md:line`
- `GSPR`: 같은 commit의 `docs/v0.2/C2PA Generator Product Security Requirements.md:line`
- `AL1 CSR` / `AL2 CSR`, `AL1 cert` / `AL2 cert`: 같은 commit의 각 `docs/v0.2/cert-profiles/claimSigningLeaf.al{1,2}.{csr,cert}.schema.json:line`
- `CSR:line`: 위 AL1/AL2 CSR schema 양쪽에서 동일한 line의 공통 제약. AL 값이 다른 행은 해당 AL의 schema를 각각 적용한다.
- `CPL schema` / `Guide` / `MIB`: 같은 commit의 `schemas/conforming-products/conforming-products-list.schema.json:line`, `schemas/conforming-products/Companion Guide for the C2PA Conforming Products List.md:line`, `schemas/mib/oid.txt:line`
- `Spec 2.4 HTML`: `specifications@9c58c8c27044e44e8601f6ab13f1bcac1376eb1f:build/site/specifications/2.4/specs/C2PA_Specification.html:line`

| source | version / identity | exact-byte SHA-256 |
|---|---|---|
| C2PA Certificate Policy | v0.2, 2026-07-31, `conformance-public@2466172` | `124fad3e3d578f40867557719f5599110a57be010e6aa4d3a3408695afdae77b` |
| C2PA Conformance Program | v0.2, 2026-07-31, same commit | `23c8dedd6e39238b3f4d0b8b2ba0bad38fe717a683146440f6354c6a58e50586` |
| Generator Product Security Requirements | v0.2, 2026-07-31, same commit | `4275064eebf01025ac0d7596f1a25a207b90d8cb921f3cbcd3327f7ec78c3a95` |
| GPSA Document Template | same commit | `bf5d92841415a1a5d31536685f05dfc70dcc1f0f8e0c46e4ded9de892537d1e2` |
| AL1 CSR schema | same commit; JSON Schema 2020-12 | `89487e5ae29099f1c4f799dee03f1a363c582b8eb8912150702ffe2b8d5c7919` |
| AL1 certificate schema / summary | same commit; JSON Schema 2020-12 / YAML summary | `8e7470d0a4f282ba88d017a3b3d864c757e4104e7d4b77657c560beaa0e4a50b` / `bc83f33e1b7947f6cd40a1a715ccd737f9c52cfccdb11af22810b74c3f7c1831` |
| AL2 CSR schema | same commit; JSON Schema 2020-12 | `5bbb03a4ca7614e66c6d15d3fb2ef2e767b523bb2b23f6e019ffa0c984258b44` |
| AL2 certificate schema / summary | same commit; JSON Schema 2020-12 / YAML summary | `c0971eae5df9724b3c1c8bc51af809eb462f07540833c0bd30d8c442ab212e06` / `b2d5ac631e4aeaa92f08840d5d9c6446584e28d6a6234d35f19902d648ce840a` |
| CPL schema | same commit; JSON Schema draft-07 | `6664f41092dd8e0c798f52d4f8cc24de66585312e179fcbd881f8c016caa8cfb` |
| CPL Companion Guide | same commit | `7dd9cec9b79e8f8182e9708af8e1a25f150be0ca5ab9458e2203c293729dcab9` |
| C2PA MIB/OID registry | same commit | `f66386f8b9b2e298a6a72bbf38f982e879908632ab58e7f32ca2b56fe4bf9b1a` |
| Content Credentials Specification 2.4 HTML | `specifications@9c58c8c27044e44e8601f6ab13f1bcac1376eb1f` | `d55caebd96206f0de667962a4bab7098c6b6468fba68f8b55bcdd3a12d1ed26d` |
| Security Considerations 2.4 HTML | same commit | `5f2ea5ca80b5b59b38be59017807742255dd573217d31976a957835bf8d85805` |
| RFC 2986 text | RFC Editor, November 2000, retrieved 2026-09-04 | `9f93627442b9fa03b24336646ffdfb3f33ed8cfd575e6b984fddab5fe88d03c0` |
| RFC 5280 text | RFC Editor, May 2008, retrieved 2026-09-04 | `a2f2628c0a83b873fc4786abd921f9b2c02395954b655d190bf16b831633345d` |
| RFC 2985 text | RFC Editor, November 2000, retrieved 2026-09-15 | `0a7a760f5becd036f11a17d5a4b4ba831ef76b29d6f74922c320139bead580f1` |
| RFC 3279 text | RFC Editor, April 2002, retrieved 2026-09-15 | `6d3f19f18e17fa1c68da5aaf4021327748fabca840d7300443b77357a1fc1614` |
| RFC 5480 text | RFC Editor, March 2009, retrieved 2026-09-15 | `593bf29fd0da2ff8b903c3ebf1c9d189a770039159e2ba46a0c3b91355037f26` |
| RFC 8410 text | RFC Editor, August 2018, retrieved 2026-09-15 | `90a0ff0b3dd661d3e26e1873f40f2ca8b41709a7bbd755a1ed3599c4746313d2` |
| RFC 6960 text | RFC Editor, June 2013, retrieved 2026-09-04 | `7e63ffa1ea2ce2737d9aaf895a63776e9105ddbdfc97b8ae4029e3e825b4cdea` |
| RFC 3161 text | local original, August 2001 | `39fd17644ff2d654bc83814a78b1c5b5e7517f496741f34ead5064943eb98240` |
| RFC 5816 text | local original, March 2010 | `9a3eba6ecf14afc7820c51034a608d54d188344a43e9189b0e023d4a6a98f649` |
| Android hardware-backed key attestation | official Android Developers, updated 2026-07-09 UTC, retrieved 2026-09-04 | `c6376c5dd00a6fa4bdd641b9c3cbcc3e1659f803132437c7f4acf824c1eae1f0` |
| AOSP Key and ID attestation | official AOSP, updated 2026-08-24 UTC, retrieved 2026-09-04 | `aa023c7a52af2e560d9e74766e609c2fb0ae36abd2d93222687524f5a895384c` |
| Android `KeyGenParameterSpec.Builder` | official Android API reference, updated 2026-08-03 UTC, retrieved 2026-09-04 | `78d5b385555c95c3f38a7d42a41f04a75ae2de0c40782e31d060fe003bd39f01` |

Remote pinned URLs: `https://www.rfc-editor.org/rfc/rfc2986.txt`, `https://www.rfc-editor.org/rfc/rfc5280.txt`, `https://www.rfc-editor.org/rfc/rfc6960.txt`, `https://developer.android.com/privacy-and-security/security-key-attestation`, `https://source.android.com/docs/security/features/keystore/attestation`, `https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder`. 감사 입력은 `/tmp/c2pa-claim-signing-sources/`의 exact-byte 고정 사본이다. RFC 3161/5816은 project root의 local original을 사용한다. Android sources는 기존 가이드 및 02 §13의 parser·체인·필드 의미에 `PROVIDER` authority로 적용한다. CP:1770-1816의 Android 전용 값 가이드는 별도의 `C2PA` 근거이며, 이를 모든 provider에 공통인 요구로 승격하지 않는다. 2026-09-11 보강에서는 기존 Android source SHA-256을 재검증하고 관련 규칙을 원격 공식 문서와 재대조했으며 원문 파일은 수정하지 않았다.

2026-09-15의 CSR 입력 보강에서는 [RFC 2985](https://www.rfc-editor.org/rfc/rfc2985.txt), [RFC 3279](https://www.rfc-editor.org/rfc/rfc3279.txt), [RFC 5480](https://www.rfc-editor.org/rfc/rfc5480.txt), [RFC 8410](https://www.rfc-editor.org/rfc/rfc8410.txt)의 위 exact-byte 사본을 `/tmp/c2pa-csr-attestation-audit.LnSvdV/sources/`에 고정했다. 조건부 RSA exponent의 추가 provider 근거는 [AOSP KeyMint Tag.aidl](https://android.googlesource.com/platform/hardware/interfaces/+/28e04e62213887d2ce572c80498b26bc3e12b709/security/keymint/aidl/android/hardware/security/keymint/Tag.aidl)의 `RSA_PUBLIC_EXPONENT` 주석/정의다. 이 원문은 remote commit `28e04e62213887d2ce572c80498b26bc3e12b709`, Git blob SHA-1 `e56c19307b84130163f36556c7b79307e6b85b34`로 고정하며 위 표의 local SHA-256 사본과 구분한다. 기존 C2PA/Android source bytes는 바꾸지 않았다.

원격 source locator는 다음 section/anchor로 고정한다.

| source | exact locator used |
|---|---|
| RFC 2986 | §§1, 3, 4.1, 4.2 in the pinned RFC Editor text |
| RFC 5280 | §§4.1, 4.1.2.2, 4.1.2.4, 4.2 (특히 4.2.1.3/4/9/12/13, 4.2.2.1), 5, 6 in the pinned RFC Editor text |
| RFC 2985 | §5.4.2, Appendix A: extensionRequest syntax, single value와 OID |
| RFC 3279 / RFC 5480 / RFC 8410 | 각각 §2.3.1 / §§2.1.1, 2.2 / §§3, 4: SPKI OID·parameters·public-key encoding |
| AOSP KeyMint Tag.aidl | 위 commit/blob의 `RSA_PUBLIC_EXPONENT` (file lines 161-172); KeyMint 조건부 provider 요구 |
| RFC 6960 | §§2.2, 3.2, 4.2.1-4.2.2 in the pinned RFC Editor text |
| Android hardware-backed key attestation | `#verifying`, `#root_certificate`, `#certificate_status`, `#expired_factory_keys` |
| AOSP Key and ID attestation | `#attestation-extension`, `#schema`, `#keydescription-fields`, `#authorizationlist-fields`, `#rootoftrust-fields`, `#attestationapplicationid-schema`, `#how-app-developers-use-attestation`, `#provisioninginfo_extension` |
| Android `KeyGenParameterSpec.Builder` | `#setAttestationChallenge(byte[])` |

CP는 BCP 14를 all-caps keyword에만 적용한다고 선언한다(CP:10-12). Conformance Program과 GSPR은 별도 BCP 14 선언이 없으므로 이 문서 집합은 그 대문자 `SHALL`을 C2PA requirement text로 보존하되, lowercase 문장은 `NON-BCP14-OBLIGATION`으로 구분한다.

## 7. 남은 clarification과 fail-closed 상태

표준 차원의 핵심 gap은 다음과 같고, 추측으로 메우지 않는다.

- C2PA 공통 Evidence wire format·artifact count·provider freshness upper bound가 없다. Android의 ASN.1 schema와 CP 필드 가이드는 존재하며 02 §13에 명시했다.
- CPL schema는 `attestationMethods`를 generator record의 required field로 만들지 않으며 provider별 semantic profile도 제공하지 않는다.
- CP는 re-key 뒤 구 certificate overlap/cutover/자동 revocation을 정하지 않는다.
- CP leaf profile은 Ed25519 certificate signature를 열어 두지만 conforming Claim Signing Issuing CA profile의 issuer SPKI는 RSA/EC만 허용한다.
- signed Notice와 공개 CPL 사이의 갱신·충돌·currentness protocol, raw Evidence retention과 구체 provider freshness profile은 정하지 않는다.
- Android CP 표의 boot 태그 오기는 AOSP `[719]`로 정정해 기록했다. OS patch의 월 문구/예시 경계와 제품별 O.3/O.4 coverage는 02 §13 및 `OD-REFERENCE-01`에서 명시적으로 다룬다.

각 gap의 영향, owner, 해소 조건과 fail-closed 동작은 [traceability와 gap register](03-Server-Validation-Traceability-and-Gaps.md)에 있다. 현재 미승인 항목을 임의 default로 채우지 않았으며, 그 항목에 의존하는 production 경로는 명시적으로 `DISABLED`다.

## 8. 문서 지도

- [01 — Enrollment Request Body](01-Enrollment-Request-Body.md)
- [02 — CSR and Dynamic Evidence Requirements](02-CSR-and-Dynamic-Evidence-Requirements.md)
- [Android — O.1~O.4 필드 매핑·체인·CSR 결속](02-CSR-and-Dynamic-Evidence-Requirements.md#android-key-attestation)
- [03 — Server Validation, Traceability and Gaps](03-Server-Validation-Traceability-and-Gaps.md)
- [04 — Independent Audit Resolution](04-Subagent-Audit-Resolution.md)

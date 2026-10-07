# Root Key 설계 원문 자료 목록

확인일: 2026-09-16 KST. 이 문서는 출처 안내다. 요구사항·사실의 근거는 아래 원문이며 설계 산출물 자체를 독립적인 근거로 취급하지 않는다.

## C2PA

이번 검토는 공식 Conformance 저장소 commit `7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50`의 v0.2 문서를 기준으로 한다. v0.2 발행일은 2026-07-31이다. 기존 `conformance-public/` 로컬 checkout을 변경하지 않았다. 아래 파일은 `gh api`로 해당 commit을 지정해 읽었다. 다운로드한 원문은 `/tmp` 검토 사본이며 영구 보관을 전제하지 않는다.

| 자료 | 원문 | 적용 범위 |
|---|---|---|
| C2PA Certificate Policy v0.2 | [CP](https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Certificate%20Policy.md) | Certificate Issuance, Certificate Usage, Certificate Status Services, Procedural Controls, CA Key Generation, Controls for CA Keys, TSA, Certificate Profiles, CA Representations |
| C2PA Conformance Program v0.2 | [Program](https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Conformance%20Program.md) | Certificate Policy, Certification Authority Evidence Request, Program Intake Form |
| C2PA Governance Framework v0.2 | [Governance](https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/C2PA%20Governance%20Framework.md) | 범위·참여자·신뢰 목록 정의 확인 |
| TSA Issuing CA 프로파일 | [YAML](https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/cert-profiles/tsaIssuingCA.cert.yaml) | pathLen=0, TSA EKU, issuer/AKI 설명 차이 |
| OCSP Responder leaf 프로파일 | [YAML](https://github.com/c2pa-org/conformance-public/blob/7b2fcb3ca5f60bbd4c6dfc6ccfaccaaa5ff9fc50/docs/v0.2/cert-profiles/ocspResponderLeaf.cert.yaml) | CA=false, OCSPSigning, NoCheck, AIA/CDP 제한 |
| C2PA Technical Specification 2.4 | [공식 게시본](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html) | §14 신뢰 모델, §15.9 OCSP 검증 |

취득한 파일 바이트의 SHA-256:

```text
124fad3e3d578f40867557719f5599110a57be010e6aa4d3a3408695afdae77b  C2PA Certificate Policy.md
23c8dedd6e39238b3f4d0b8b2ba0bad38fe717a683146440f6354c6a58e50586  C2PA Conformance Program.md
e9bbfe720250c1189b9364807817cc2a094fe7e2994a6da0d7644bb30a6ec0d5  tsaIssuingCA.cert.yaml
c55cc538ef1dd174d38f2187cbbb118e1b2bc2bb86a3e1316c1403c0ae8cfc6c  ocspResponderLeaf.cert.yaml
```

CP/Program/Governance의 확인 범위에서 미등록 상위 Root에 대한 포괄적인 운영 책임 면제 문구를 발견하지 못했다. 이는 다른 공식 해석이나 참가 계약의 존재를 부정하는 결론은 아니다. CA 참가 계약 PDF는 다운로드했으나 본문을 읽지 못했으므로 본 설계의 근거로 사용하지 않았다.

## 2026-10-07 — Ceremony와 감사 준비 추가 확인

§6.1.1의 번호·본문 대조에는 공식 저장소의 기존 로컬 Git 객체에서 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`를 지정해 읽은 v0.2 PDF와 Markdown을 사용했다(`git show <commit>:<path>`). 작업 트리의 Markdown 수정·줄바꿈 상태를 해당 commit 원문으로 간주하지 않았다. 이전 절의 다른 commit을 대체하거나 신청 기준 버전을 새로 확정한 것은 아니다.

| 자료 | 공식 원문·로컬 위치 | 확인 범위 |
|---|---|---|
| C2PA Certificate Policy v0.2 PDF | [PDF](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.pdf), `conformance-public/docs/v0.2/C2PA Certificate Policy.pdf` | §6.1.1 본문 21–22쪽(PDF 24–25번째 페이지), §6.2.1·6.3–6.5의 연계 통제 |
| C2PA Certificate Policy v0.2 Markdown | [원문](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Certificate%20Policy.md) | 같은 제목의 §6.1.1 대응 내용, Publication·Certificate Renewal·Certificate Modification·Compliance Audits |
| C2PA Conformance Program v0.2 PDF/Markdown | [PDF](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.pdf), [Markdown](https://github.com/c2pa-org/conformance-public/blob/2466172859fad1215f7aaf7e3768b41a0ac29abc/docs/v0.2/C2PA%20Conformance%20Program.md), 로컬 `conformance-public/docs/v0.2/` | Certificate Policy, 독립 입회·서명된 스크립트/조건부 WebTrust 대체 증거(PDF 14번째 페이지), CA Evidence Request·Evidence Assessment(PDF 17번째 페이지) |

해당 commit의 PDF 바이트 SHA-256:

```text
bfae1e17c501dd33099f2c03e0c6f921ba310d481b23b6881948d56aaa6a2715  C2PA Certificate Policy.pdf
d1d4b932320866479fc78abbcd81c35234bdb6f666ca8138fbca71b8bbdf198a  C2PA Conformance Program.pdf
```

§6.1.1과 Program의 위 확인 범위에서 서류 누락마다 자동 재생성을 명령하는 조항은 확인되지 않았다. 생성 당시 통제·증거를 입증할 수 없으면 재생성이 필요할 수 있다는 설명은 해당 원문에서 도출한 설계 위험 판단이며, 실제 수용 여부나 재생성 명령을 받은 사실이 아니다.

## 2026-10-07 — CA 소프트웨어 기능 분류 확인

위와 같은 commit `2466172859fad1215f7aaf7e3768b41a0ac29abc`의 CP·Program Markdown을 로컬 `git show`로 읽었다. CP의 Publication·Repositories, Identification and Authentication, Certificate Life-Cycle, Facility/Management/Operational Controls, Technical Security Controls, Certificate Profiles, Compliance Audits, Dynamic Evidence 부록과 Program의 CA 등록 증거 조항을 확인했다. 기능 분류는 원문 요구의 구현상 해석이며 표준이 지정한 제품 구성으로 취급하지 않는다.

제품 종류·도구의 역할은 다음 공식 온라인 문서로 확인했다. 특정 제품 선정, C2PA 적합성이나 quorum 연동 실증의 근거가 아니다.

| 원문 | 확인 범위 |
|---|---|
| [EJBCA Cloud AWS](https://docs.keyfactor.com/ejbca-cloud/latest/ejbca-cloud-aws) | CA 계층·발급·관리 기능, CloudHSM 연동 안내 |
| [Microsoft AD CS CA 역할](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certification-authority-role) | Windows Server의 인증서 발급·폐지·관리, CA 유형 |
| [OpenSSL ca](https://docs.openssl.org/master/man1/openssl-ca/) | 기본 CA 명령의 인증서 처리와 상태 원장 기능 |
| [AWS quorum 사용](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html) | 제품의 HSM 지원과 구분해야 하는 CLI 토큰의 작업·세션·애플리케이션 제한 |

2026-10-07 앱 기능 감사에서는 같은 고정본의 CA Representations, OCSP Responder Leaf Profile, 키 백업·복구·archive 구분, 기록 보관과 폐지 요청 처리 기한도 대조했다. 구현 기능·거부 사례는 원문 요구에서 도출한 설계이며 원문이 지정한 애플리케이션 구조로 취급하지 않는다.

## RFC·키 관리·업데이트·PQC

| 자료 | 원문 | 읽은 범위·사용 목적 |
|---|---|---|
| RFC 5280, 2008-05 | [PKIX](https://www.rfc-editor.org/rfc/rfc5280.html) | §6 신뢰 앵커 입력과 인증 경로 구분 |
| RFC 6960, 2013-06 | [OCSP](https://www.rfc-editor.org/rfc/rfc6960.html) | §2.2/§2.6/§4.2.2.2 응답 서명과 직접 위임 |
| RFC 6024, 2010-10, Informational | [Trust Anchor Management Requirements](https://www.rfc-editor.org/rfc/rfc6024.html) | §3.4/§3.8/§3.10/§3.11 권한 이전·인증·replay·복구 |
| RFC 9124, 2022-01, Informational | [SUIT manifest information model](https://www.rfc-editor.org/rfc/rfc9124.html) | §3/§4 메타데이터·순서·호환성·설치 보안 요구의 설계 참고 |
| NIST SP 800-57 Part 1 Rev.5, 2020 | [원문 PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf) | §5.6 침해 복구, §8.1.5.2.1 split knowledge. 범용 운영 참고 자료 |
| TUF specification 1.0.36, 2026-08-05 | [공식 명세](https://theupdateframework.github.io/specification/latest/) | §2 역할, §5.3/§6.1 업데이트 키 전환. 확인일 이후 latest 변경 가능 |
| NIST FIPS 204, 2024-08-13 | [ML-DSA 표준 소개 및 원문](https://csrc.nist.gov/pubs/fips/204/final) | PQC 서명 알고리즘 후보의 표준 상태 |

## AWS

아래는 확인일의 공식 온라인 문서다. 고정된 SDK 버전이나 HSM 모델에 대한 실험 결과가 아니며 실제 배포 버전의 지원 여부는 별도 검증한다.

| 원문 | 사용 목적 |
|---|---|
| [CloudHSM key quorum](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli.html) | 서명·키 관리 quorum, 승인자 수·토큰 기본 만료 |
| [Quorum key usage](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-crypto-user.html) | 단일 작업·로그인 세션·CLI 범위 제한 |
| [Crypto-user 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/key-quorum-auth-chsm-cli-first-time.html) | 키 생성 시 key-use/key-management quorum |
| [Admin 설정](https://docs.aws.amazon.com/cloudhsm/latest/userguide/quorum-auth-chsm-cli-first-time.html) | user/quorum 서비스의 관리 통제 구분 |
| [ECDSA CLI 서명](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cloudhsm_cli-crypto-sign-ecdsa.html) | approval 옵션·raw/digest 입력 |
| [Client SDK 5 serverless 지원](https://docs.aws.amazon.com/cloudhsm/latest/userguide/sdk8-serverless.html) | Lambda 지원과 quorum 설계 적합성의 구분 |
| [PKCS#11 mechanisms](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pkcs11-mechanisms.html) | ML-DSA 기재 확인. C2PA/모듈인증/CLI quorum까지 보장하는 근거로 사용하지 않음 |
| [AWS 중국 서비스 목록](https://www.amazonaws.cn/en/about-aws/regional-product-services/) | 앞선 검토에서 CloudHSM이 목록에 없음을 확인. 이번 설계는 CN 미구축이라는 사용자 결정을 적용 |

## 증거의 한계

클라우드 계정·HSM·Phone/TV 단말에 대한 연결이나 PoC는 수행하지 않았다. C2PA 등록을 신청하거나 외부 담당자에게 문의하지 않았다. 문서 해석 미확인 항목과 구현 시험을 설계의 완료 조건에 포함했으며, 설계안 작성과 적합성 검증 완료를 구분한다.

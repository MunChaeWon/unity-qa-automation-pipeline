# Unity QA Automation Pipeline

## 1. 프로젝트 개요

Unity 2D Platformer Microgame을 대상으로 QA 자동화 테스트 환경을 구축한 프로젝트

본 프로젝트는 Unity Test Framework, AltTester, pytest, Allure, Jira, Excel을 연동하여 테스트 실행부터 결과 리포트 생성, 이슈 등록, TC 결과 관리까지 자동화하는 것을 목표로 한다.

## 2. 주요 사용 도구

| 도구 | 용도 |
|---|---|
| Unity Test Framework | Unity PlayMode/EditMode 테스트 실행 |
| AltTester | Unity 실행 환경 대상 자동화 테스트 |
| pytest | Python 기반 AltTester 테스트 실행 |
| Allure | 테스트 결과 리포트 생성 |
| Jira | 테스트 결과 기반 Task/Bug 이슈 생성 |
| Excel | TC 실행 결과 및 History 관리 |
| GitHub | 프로젝트 형상 관리 |

## 3. 테스트 범위

AltTester 자동화 테스트는 Player 조작 기능을 대상으로 함.

| TC ID | 테스트 항목 |
|---|---|
| TC-MJ-001 | 좌측 이동 |
| TC-MJ-002 | 우측 이동 |
| TC-MJ-003 | 이동 정지 |
| TC-MJ-004 | 좌우 방향 전환 |
| TC-MJ-005 | 기본 점프 |
| TC-MJ-006 | 이동 중 점프 |
| TC-MJ-007 | 공중 추가 점프 제한 |
| TC-MJ-008 | 좌우 동시 입력 안정성 |

## 4. 자동화 방식

AltTester의 press_key 방식은 Unity Editor PlayMode 환경에서 기존 Input Manager 기반 PlayerController까지 안정적으로 입력이 전달되지 않았음.

따라서 실제 A/D/Space 입력 가능 여부는 수동 테스트로 확인하고, 자동화에서는 TestInputBridge를 통해 이동 및 점프 입력값을 PlayerController에 직접 주입하는 방식으로 검증함.

## 5. 실행 방법

Unity에서 AltTester Play in Editor를 실행한 뒤 아래 BAT 파일을 실행함.

```bat
D:\funity\Test1\alt-tests\run_alt_allure.bat
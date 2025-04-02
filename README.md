# Process Scheduling Simulator
- 마감일: 5/9(금) 23:59
- 시연,발표: 5/12, {5/13, 5/14}(세부 일정은 추후 공지)
- 언어: Python


## 프로세스 매니저 team
- 박종범
- 조윤재
- 김도헌
- 한윤수


## 진척도

- 전반 기능
    - ✅ Arrival  BT  Remaining  ST  WT  TT  NTT 확인가능
    - ✅ 소비전력 확인가능
    - ❌ 프로세서 코어 종류별 성능차이 구현


- scheduling
    - ✅base scheduling(추상)
    - ❌FCFS
    - ❌RR
    - ❌FCFS
    - ❌SPN
    - ❌SRTN
    - ❌HRRN
    - ❌Custom-algorithm 
    - ✅test scheduling


- ❌시각화




## 책임 분담
| 책임            | 담당 팀원  |
| ----------------- | ---------- |
| 프로젝트 전반      | 박종범     |
| FCFS              | 박종범     |
| RR                | 조윤재     |
| SPN               | 한윤수     |
| SRTN              | 김도헌     |
| HRRN              | 김도헌     |
| Custom-algorithm  | 한윤수    |
| 시각화            | 조윤재    |




## 기여법

__주의__: main 브랜치에는 직접 commit이나 push하지 말고, 반드시 별도의 브랜치를 생성하여 작업하세요.

### 1. 로컬 클론
공동 저장소를 로컬에 복제합니다.
```bash
git clone <공동_저장소_URL>
```

### 2. 새로운 브랜치 생성
새로운 기능 개발 시 feature 브랜치를 생성합니다.
```bash
git checkout -b feature-<기능명> #브런치를 생성하고 이동하는 명령어
# 예시: git checkout -b feature-FCFS
```

### 3. 최신화 (다른 기능이 main에 추가될 때마다)
현재 작업 중인 feature 브랜치에 main 브랜치의 최신 변경 사항을 병합합니다.
```bash
git checkout main               #메인브런치로 이동
git pull origin main            #업데이트된 메인브런치를 가져옴
git checkout feature-<기능명>   #내 작업중인 브런치로 이동
git merge main                  #내 제작중인 코드에 최신화
```

### 4. 변경사항 커밋 및 PR(Pull Request) 생성
기능 개발이 완료되면 GitHub에서 PR을 생성합니다.
GitHub 웹 인터페이스에서 해당 브랜치로 PR을 생성하고, 리뷰를 요청하세요.
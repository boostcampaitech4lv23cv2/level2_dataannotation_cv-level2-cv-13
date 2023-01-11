# Data Annotation Competition CV-13

## 🕵️Members

<table>
    <th colspan=5>📞 TEAM 031</th>
    <tr height="160px">
        <td align="center">
            <a href="https://github.com/LimePencil"><img src="https://avatars.githubusercontent.com/u/71117066?v=4" width="100px;" alt=""/><br /><sub><b>신재영</b></sub></a>
        </td>
        <td align="center">
            <a href="https://github.com/sjz1"><img src="https://avatars.githubusercontent.com/u/68888169?v=4" width="100px;" alt=""/><br /><sub><b>유승종</b></sub></a>
        </td>
        <td align="center">
            <a href="https://github.com/SangJunni"><img src="https://avatars.githubusercontent.com/u/79644050?v=4" width="100px;" alt=""/><br /><sub><b>윤상준</b></sub></a>
        </td>
        <td align="center">
            <a href="https://github.com/lsvv1217"><img src="https://avatars.githubusercontent.com/u/113494991?v=4" width="100px;" alt=""/><br /><sub><b>이성우</b></sub></a>
        </td>
         <td align="center">
            <a href="https://github.com/0seob"><img src="https://avatars.githubusercontent.com/u/29935109?v=4" width="100px;" alt=""/><br /><sub><b>이영섭</b></sub></a>
        </td>
    </tr>
</table>



## 🔤OCR task를 위한 Data Annotation 
스마트폰으로 카드를 결제하거나, 카메라로 카드를 인식할 경우 자동으로 카드 번호가 입력되는 경우가 있습니다. 또 주차장에 들어가면 차량 번호가 자동으로 인식되는 경우도 흔히 있습니다. 이처럼 OCR (Optimal Character Recognition) 기술은 사람이 직접 쓰거나 이미지 속에 있는 문자를 얻은 다음 이를 컴퓨터가 인식할 수 있도록 하는 기술로, 컴퓨터 비전 분야에서 현재 널리 쓰이는 대표적인 기술 중 하나입니다.

## 📍Task
OCR task는 글자 검출 (text detection), 글자 인식 (text recognition), 정렬기 (Serializer) 등의 모듈로 이루어져 있습니다.

하지만 본 대회에서는 '글자 검출' task 만을 해결하게 됩니다.
또한 model, loss, east_dataset 등은 변경할 수 없고 dataset을 새로 구축하거나 pre-processing, data augmentation을 변경하거나 train에서 learning rate scheduling을 변경하는 등 제약이 있습니다.

Input : 글자가 포함된 전체 이미지

Output : bbox 좌표가 포함된 UFO Format

## 💾Dataset
### Train Dataset
- ICDAR2015
- ICDAR2017
- ICDAR2019
### Validation Dataset
- ICDAR2017_KOREAN


## 🗓️Timeline
![image](https://user-images.githubusercontent.com/29935109/211737039-ffd0d017-336b-4932-9f0f-7a0f0f31cb51.png)


## 🏔️Environments
### <img src="https://cdn3.emoji.gg/emojis/4601_github.png" alt="drawing" width="16"/>  GitHub
- 모든 코드들의 버전관리
- GitFlow를 이용한 효율적인 전략
- Issue를 통해 버그나 프로젝트 관련 기록
- PR을 통한 code review
- 총 11개의 PR, 43개의 commit

### <img src="https://img.icons8.com/ios-filled/500/notion.png" alt="drawing" width="16"/> Notion
- 노션을 이용하여 실험결과등을 정리
- 회의록을 매일 기록하여 일정을 관리
- 가설 설정 및 결과 분석등을 기록
- 캘린더를 사용하여 주간 일정 관리

### <img src="https://cdn.icon-icons.com/icons2/2699/PNG/512/atlassian_jira_logo_icon_170511.png" alt="drawing" width="16"/> Jira
- 발생하는 모든 실험의 진행상황 기록
- 로드맵을 통한 스케줄 관리
- 효율적인 일 분배 및 일관성 있는 branch 생성
- 총 18개의 Issue 발생

### <img src="https://avatars.githubusercontent.com/u/26401354?s=200&v=4" alt="drawing" width="16"/> WandB
- 실험들의 기록 저장 및 공유
- 데이터셋의 성능 비교
- Hyperparameter 및 validation f1 score 기록
- 총 312시간 기록

## ⚙️Requirements
```
Ubuntu 18.04.5 LTS
Intel(R) Xeon(R) Gold 5120 CPU @ 2.20GHz
NVIDIA Tesla V100-PCIE-32GB

lanms==1.0.2
numpy==1.21.3
opencv-python==4.6.0.66
shapely==1.7.1
tqdm==4.62.3
matplotlib
albumentations==1.1.0
pandas==1.3.4
wandb==0.13.6
gdown==4.6.0
pytorch=1.7.1
```

## 🎉Results🎉
>### Public LB : 2nd (f1 0.7166)
![image](https://user-images.githubusercontent.com/29935109/211737069-f95f1668-a372-4dbd-9c75-12af28b9a9cf.png)
>### Private LB : 4th (f1 0.7034)
![image](https://user-images.githubusercontent.com/29935109/211737091-9fd8223b-0958-4c3d-8480-bec15d265572.png)


## ⬇️Please Look at our Wrap-Up Report for more details
[![image](https://user-images.githubusercontent.com/62556539/200262300-3765b3e4-0050-4760-b008-f218d079a770.png)](https://gratis-keyboard-88d.notion.site/Data-wrap-up-report-12b152c127a24c2ca33e3c11501ed804)

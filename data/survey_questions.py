"""앱 안에서 열리는 '샘플 설문' 문항 (mock).

★ 실제 운영에서는 Google Forms 를 쓰고 .env 의 SURVEY_PRE_URL / SURVEY_POST_URL 에 주소를 넣으세요.
   주소가 비어 있을 때만 이 샘플 설문이 나타납니다.
   문항을 고치고 싶다면 아래 목록만 수정하면 화면이 자동으로 바뀌어요.

문항 형식
    id       분석할 때 쓰는 이름(영문)
    type     select(하나 고르기) | multiselect(여러 개 고르기) | scale(1~5점)
    label    화면에 보이는 질문
    options  select/multiselect 의 보기
    low/high scale 의 양 끝 설명
"""

PRE_QUESTIONS = [
    {
        "id": "last_checkup",
        "type": "select",
        "label": "가장 최근에 건강검진을 받은 시기는 언제인가요?",
        "options": ["1년 이내", "1~2년 전", "2년보다 더 오래전", "받아본 적 없어요"],
    },
    {
        "id": "skip_reasons",
        "type": "multiselect",
        "label": "건강검진을 미룬 이유가 있다면 골라주세요. (여러 개 선택 가능)",
        "options": ["시간이 없어서", "건강하다고 생각해서", "결과가 걱정돼서", "비용이 부담돼서", "어디서 받는지 몰라서", "특별한 이유는 없어요"],
    },
    {
        "id": "intent_pre",
        "type": "scale",
        "label": "이번에 건강검진을 받을 생각은 어느 정도인가요?",
        "low": "전혀 없어요",
        "high": "꼭 받을 거예요",
    },
]

POST_QUESTIONS = [
    {
        "id": "change_after",
        "type": "select",
        "label": "건강검진을 받고 나서 건강검진에 대한 생각이 어떻게 달라졌나요?",
        "options": ["더 중요하게 생각하게 됐어요", "큰 변화는 없어요", "생각보다 간단했어요", "아직 잘 모르겠어요"],
    },
    {
        "id": "intent_post",
        "type": "scale",
        "label": "앞으로도 정기적으로 건강검진을 받을 생각은 어느 정도인가요?",
        "low": "전혀 없어요",
        "high": "꼭 받을 거예요",
    },
    {
        "id": "campaign_help",
        "type": "scale",
        "label": "이 캠페인이 건강검진을 받는 데 도움이 되었나요?",
        "low": "도움 안 됐어요",
        "high": "많이 도움 됐어요",
    },
]

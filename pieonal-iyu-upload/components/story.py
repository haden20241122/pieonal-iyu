"""홈 화면: '왜 피어날 이유일까요?' — 캠페인 이름에 담은 마음.

생각의 흐름:  건강을 챙기는 일을 '숙제'가 아니라 '나를 피우는 일'로 다시 불러보고 싶었다
            → 한창 피어나는 시기(20대)에, 몸도 같이 돌보자
            → 그래서 검진을 받은 뒤에 '나의 피어날 이유'를 한 줄로 적어 SNS에 남긴다
문구를 고칠 때는 아래 STORY_ITEMS 와 STORY_LEAD 만 바꾸면 돼요.
"""
import streamlit as st

from components.layout import h

STORY_TITLE = "왜 ‘피어날 이유’일까요?"
STORY_LEAD = (
    "건강검진이라고 하면 귀찮은 일부터 떠오르죠. 그래서 이름부터 다르게 불러보기로 했어요. "
    "건강을 챙기는 건 해야 하는 숙제가 아니라, 내가 피어나는 일이라고요."
)
STORY_ITEMS = [
    (
        "지금이 피어나는 때예요",
        "스무 살 무렵은 인생에서 꽃봉오리가 막 열리는 시기예요. 가장 환하게 피어날 때, 몸도 같이 돌봐주면 좋겠다는 마음으로 시작했어요.",
    ),
    (
        "검진은 출발선이에요",
        "내 몸이 지금 어떤 상태인지 한 번 확인해 두면, 앞으로 하고 싶은 일을 마음 편히 할 수 있어요. 아프고 나서 걱정하는 것보다 먼저요.",
    ),
    (
        "그래서 이유를 물어요",
        "검진을 받고 나면 ‘나는 뭘 하려고 건강하고 싶지?’ 하고 한 줄만 적어 SNS에 남겨요. 그게 나의 피어날 이유가 돼요.",
    ),
]
STORY_CLOSE = "건강해야 오래, 환하게 피어 있을 수 있으니까요."


def render_name_story() -> None:
    items = "".join(
        f'<div class="pr-story__item"><span class="pr-story__num">{i}</span><h3>{h(title)}</h3><p>{h(text)}</p></div>'
        for i, (title, text) in enumerate(STORY_ITEMS, start=1)
    )
    st.html(
        f"""
        <section class="pr-story" aria-labelledby="pr-story-title">
          <div class="pr-eyebrow">이름에 담은 마음</div>
          <h2 class="pr-story__title" id="pr-story-title">{h(STORY_TITLE)}</h2>
          <p class="pr-story__lead">{h(STORY_LEAD)}</p>
          <div class="pr-story__grid">{items}</div>
          <p class="pr-story__close">🌼 {h(STORY_CLOSE)}</p>
        </section>
        """
    )

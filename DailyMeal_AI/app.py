# app.py
import streamlit as st
import requests

# =========================
# 🔑 OpenRouter API 설정
# =========================
API_KEY = "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"
MODEL_NAME = "deepseek/deepseek-chat"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


# =========================
# 🧠 프롬프트 생성
# =========================
def build_prompt(
    name, gender, age, height, weight,
    activity, goal, meals, allergy, budget, style
):
    allergy_text = allergy if allergy.strip() else "없음"

    return f"""
너는 전문 영양사이자 피트니스 코치다.
학생도 이해할 수 있는 쉬운 문장으로 하루 식단을 구성해줘.

[사용자 정보]
- 이름: {name if name else "사용자"}
- 성별: {gender}
- 나이: {age}세
- 키: {height}cm
- 몸무게: {weight}kg
- 활동량: {activity}
- 목표: {goal}
- 하루 식사 횟수: {meals}끼
- 알레르기: {allergy_text}
- 예산: {budget}
- 선호 스타일: {style}

[출력 형식]
1) 아침
- 메뉴:
- 설명:
- 칼로리:
- 단백질(g):

2) 점심
- 메뉴:
- 설명:
- 칼로리:
- 단백질(g):

3) 저녁
- 메뉴:
- 설명:
- 칼로리:
- 단백질(g):

[하루 요약]
- 총 칼로리:
- 영양 비율 (P/C/F):
- 목표에 얼마나 적합한지 간단 평가:
- 추가 팁 2~3개 작성:

조건:
- 한국어로 작성
- 현실적으로 구할 수 있는 음식만
"""


# =========================
# 🤖 OpenRouter 모델 호출
# =========================
def generate_meal_plan(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "너는 현실적인 한국 영양사이다."},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(BASE_URL, headers=headers, json=body)

    if res.status_code != 200:
        return f"❌ API 오류 발생\n\n{res.text}"

    return res.json()["choices"][0]["message"]["content"]


# =========================
# 🎨 Streamlit UI
# =========================
def main():
    st.set_page_config(page_title="DailyMeal AI", page_icon="🍱", layout="wide")

    st.title("🍱 DailyMeal AI")
    st.write("AI가 당신에게 맞는 하루 식단을 설계합니다!")

    left, right = st.columns([1, 1.2])

    # 입력 영역
    with left:
        st.subheader("1️⃣ 정보 입력")

        name = st.text_input("이름 (선택)")
        gender = st.selectbox("성별", ["남성", "여성", "기타"])
        age = st.number_input("나이", 10, 80, 17)
        height = st.number_input("키(cm)", 130.0, 210.0, 170.0)
        weight = st.number_input("몸무게(kg)", 30.0, 200.0, 60.0)

        activity = st.selectbox(
            "활동량",
            ["거의 앉아서 생활", "가벼운 활동", "주 2~3회 운동", "매일 운동"]
        )

        goal = st.radio("목표", ["다이어트", "벌크업", "체중 유지"], horizontal=True)
        meals = st.radio("식사 횟수", [2, 3, 4], index=1, horizontal=True)

        allergy = st.text_area(
            "알레르기 / 못 먹는 음식",
            placeholder="없으면 비워두세요",
        )

        budget = st.selectbox("예산 수준", ["저렴하게", "보통", "상관없음"])

        style = st.selectbox(
            "식단 스타일",
            [
                "건강 담백 스타일",
                "단백질 중심 운동 스타일",
                "학생 현실 스타일",
                "편의점 위주 현실 스타일"
            ],
        )

        generate = st.button("🍽 식단 생성하기", use_container_width=True)

    # 출력 영역
    with right:
        st.subheader("2️⃣ DailyMeal AI 결과")

        if generate:
            with st.spinner("AI가 식단을 생성 중입니다..."):
                prompt = build_prompt(
                    name, gender, age, height, weight,
                    activity, goal, meals, allergy, budget, style
                )
                result = generate_meal_plan(prompt)

            st.success("🎉 식단 생성 완료!")
            st.markdown(result)
        else:
            st.info("왼쪽에서 정보를 입력하고 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()

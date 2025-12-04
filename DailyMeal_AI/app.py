# app.py
import streamlit as st

# =========================
# 🔧 간단한 계산 유틸 함수들
# =========================

def estimate_bmr(gender: str, age: int, height: float, weight: float) -> float:
    """기초대사량 대략 계산 (Mifflin-St Jeor 근사)"""
    if gender == "남성":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # 여성 + 기타는 여성식으로 처리
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def activity_factor(activity: str) -> float:
    """활동량에 따른 계수"""
    if "거의 앉아서" in activity:
        return 1.2
    if "가벼운 활동" in activity:
        return 1.375
    if "2~3회" in activity:
        return 1.55
    if "매일 운동" in activity:
        return 1.725
    return 1.3


def goal_adjustment(goal: str) -> float:
    """목표에 따른 칼로리 조정 계수"""
    if goal == "다이어트":
        return 0.85
    if goal == "벌크업":
        return 1.1
    return 1.0  # 체중 유지


def get_base_menus(style: str, budget: str):
    """스타일 + 예산에 따른 기본 메뉴 후보들"""
    # 아주 간단하게 몇 가지 세트만 준비
    if "단백질" in style:
        breakfast = "현미밥 + 계란프라이 2개 + 닭가슴살 슬라이스 + 방울토마토"
        lunch = "닭가슴살 샐러드 + 삶은 고구마 1개 + 플레인 요거트"
        dinner = "연어구이 + 찐 브로콜리 + 현미밥 작은 공기"
    elif "편의점" in style:
        breakfast = "편의점 삼각김밥 1개 + 삶은 계란 2개 + 두유 1팩"
        lunch = "편의점 닭가슴살 샐러드 + 컵밥(잡곡밥) 1개"
        dinner = "편의점 도시락(단백질 위주 제품) + 샐러드팩"
    elif "학생 현실" in style:
        breakfast = "시리얼 + 우유 1컵 + 바나나 1개"
        lunch = "학교 급식(밥 + 국 + 반찬) 기준, 밥은 조금 남기기"
        dinner = "집밥(밥 + 찌개 + 반찬 2~3가지)에서 밥은 평소보다 1/3 적게"
    else:  # 건강 담백 스타일
        breakfast = "오트밀 + 견과류 한 줌 + 블루베리 + 저지방 우유"
        lunch = "현미밥 + 두부조림 + 나물류 반찬 + 김치"
        dinner = "닭가슴살 구이 + 샐러드 + 고구마 1개"

    # 예산에 따른 간단한 보정 설명
    if budget == "저렴하게":
        budget_note = "가격을 최대한 줄이기 위해 계란, 두부, 닭가슴살, 제철 채소 위주로 구성했습니다."
    elif budget == "상관없음":
        budget_note = "가격 제한 없이, 영양과 맛을 모두 고려한 식단입니다."
    else:
        budget_note = "일반적인 학생 기준의 평균적인 가격대를 고려한 식단입니다."

    return breakfast, lunch, dinner, budget_note


def split_calories(total_cal: int, meals: int):
    """끼니 수에 따라 칼로리 대략 배분"""
    if meals == 2:
        return [int(total_cal * 0.45), int(total_cal * 0.55), 0]
    elif meals == 4:
        # 아침/간식/점심/저녁 느낌
        return [
            int(total_cal * 0.25),
            int(total_cal * 0.1),
            int(total_cal * 0.35),
            int(total_cal * 0.3),
        ]
    else:  # 기본 3끼
        return [
            int(total_cal * 0.3),
            int(total_cal * 0.4),
            int(total_cal * 0.3),
        ]


def protein_target(goal: str, weight: float) -> int:
    """목표에 따른 단백질 목표(대략 g)"""
    if goal == "벌크업":
        return int(weight * 2.0)
    if goal == "다이어트":
        return int(weight * 1.6)
    return int(weight * 1.4)


# =========================
# 🧠 로컬 "AI" 식단 생성기
# =========================

def generate_meal_plan_local(
    name, gender, age, height, weight,
    activity, goal, meals, allergy, budget, style
):
    # 1) 하루 필요 칼로리 대략 계산
    bmr = estimate_bmr(gender, age, height, weight)
    tdee = bmr * activity_factor(activity)
    target_cal = int(tdee * goal_adjustment(goal))
    target_protein = protein_target(goal, weight)

    # 2) 스타일/예산에 따른 기본 메뉴 후보
    breakfast_menu, lunch_menu, dinner_menu, budget_note = get_base_menus(style, budget)

    # 3) 알레르기/제한 음식 반영 (아주 단순한 텍스트 처리)
    allergy_note = ""
    allergy = allergy.strip()
    if allergy:
        allergy_note = f"\n※ 주의: '{allergy}' 관련 음식은 최대한 제외하거나 대체 식품을 선택해야 합니다."

    # 4) 끼니별 칼로리 분배
    cal_split = split_calories(target_cal, meals)

    # 5) 출력 텍스트 구성
    name_display = name if name.strip() else "사용자"

    lines = []
    lines.append(f"### 🧾 {name_display}님을 위한 DailyMeal AI 식단 요약")
    lines.append("")
    lines.append(f"- 대략 필요 칼로리(TDEE 기준): **{int(tdee)} kcal**")
    lines.append(f"- 목표에 맞춘 하루 섭취 칼로리: **약 {target_cal} kcal**")
    lines.append(f"- 권장 단백질 섭취량: **약 {target_protein} g**")
    lines.append("")
    lines.append(f"예산/스타일 참고: {budget_note}")
    if allergy_note:
        lines.append(allergy_note)
    lines.append("---")

    # 아침
    if meals >= 2:
        lines.append("#### 🥣 1) 아침")
        lines.append(f"- 메뉴: {breakfast_menu}")
        lines.append(f"- 설명: 아침에는 소화가 잘 되는 탄수화물 + 단백질을 함께 섭취해 에너지를 확보하는 것이 좋습니다.")
        lines.append(f"- 예상 칼로리: 약 {cal_split[0]} kcal")
        lines.append(f"- 예상 단백질: 약 {int(target_protein * 0.3)} g")
        lines.append("")

    # 점심
    lines.append("#### 🍛 2) 점심")
    lines.append(f"- 메뉴: {lunch_menu}")
    lines.append("- 설명: 점심은 활동량이 가장 많은 시간대이므로, 탄수화물/단백질/지방을 골고루 섭취하는 것이 좋습니다.")
    if len(cal_split) >= 2:
        lunch_cal = cal_split[1]
    else:
        lunch_cal = int(target_cal * 0.4)
    lines.append(f"- 예상 칼로리: 약 {lunch_cal} kcal")
    lines.append(f"- 예상 단백질: 약 {int(target_protein * 0.4)} g")
    lines.append("")

    # 저녁
    if meals >= 3:
        lines.append("#### 🍽 3) 저녁")
        lines.append(f"- 메뉴: {dinner_menu}")
        lines.append("- 설명: 저녁에는 과한 탄수화물을 줄이고, 단백질과 채소 위주로 섭취하면 체중 관리에 도움이 됩니다.")
        if meals == 2:
            dinner_cal = cal_split[1]
        elif meals == 3:
            dinner_cal = cal_split[2]
        else:
            dinner_cal = cal_split[3] if len(cal_split) > 3 else int(target_cal * 0.3)
        lines.append(f"- 예상 칼로리: 약 {dinner_cal} kcal")
        lines.append(f"- 예상 단백질: 약 {int(target_protein * 0.3)} g")
        lines.append("")

    # 간단 간식/추가 안내 (4끼일 때)
    if meals == 4:
        lines.append("#### 🍎 + 간식 제안")
        lines.append("- 예시: 플레인 요거트, 삶은 계란 1개, 아몬드 한 줌, 작은 바나나 1개 등")
        lines.append("- 설명: 간식은 식사 사이에 과하지 않게, 단백질이나 식이섬유 위주로 선택하는 것이 좋습니다.")
        lines.append(f"- 예상 칼로리: 약 {cal_split[1]} kcal")
        lines.append("")

    # 하루 요약
    lines.append("---")
    lines.append("### 📌 하루 요약")
    lines.append(f"- 목표: **{goal}**")
    lines.append(f"- 예상 총 섭취 칼로리: **약 {target_cal} kcal**")
    lines.append(f"- 예상 단백질 섭취량: **약 {target_protein} g** (대략)")
    lines.append("")
    if goal == "다이어트":
        lines.append("- 평가: 현재 목표에 맞게 기초대사량보다 약간 낮은 수준으로 설정했습니다.")
        lines.append("- 팁: 늦은 밤 야식, 단 음료(탄산, 밀크티 등)는 최대한 피하는 것이 좋습니다.")
    elif goal == "벌크업":
        lines.append("- 평가: 근육 증가를 위해 유지 칼로리보다 약간 높게 설정했습니다.")
        lines.append("- 팁: 식사 후에 우유 + 땅콩버터 토스트 같은 고열량 간식을 추가해도 좋습니다.")
    else:
        lines.append("- 평가: 현재 체중을 유지하기에 적당한 수준으로 설정했습니다.")
        lines.append("- 팁: 주 2~3회 가벼운 운동과 함께 균형 잡힌 식단을 유지하면 좋습니다.")
    lines.append("")
    lines.append("- 공통 팁: 물은 하루 1.5L 이상 충분히 마시고, 너무 짠 음식은 줄이는 것이 좋습니다.")

    return "\n".join(lines)


# =========================
# 🎨 Streamlit UI
# =========================

def main():
    st.set_page_config(page_title="DailyMeal AI (Offline)", page_icon="🍱", layout="wide")

    st.title("🍱 DailyMeal AI")
    st.write("외부 API 없이, 간단한 로직으로 하루 식단을 추천해 주는 버전입니다.")

    left, right = st.columns([1, 1.3])

    with left:
        st.subheader("1️⃣ 정보 입력")

        name = st.text_input("이름 (선택)")

        gender = st.selectbox("성별", ["남성", "여성", "기타"])
        age = st.number_input("나이", 10, 80, 17)
        height = st.number_input("키(cm)", 130.0, 210.0, 170.0)
        weight = st.number_input("몸무게(kg)", 30.0, 200.0, 60.0)

        activity = st.selectbox(
            "활동량",
            ["거의 앉아서 생활", "가벼운 활동", "주 2~3회 운동", "매일 운동"],
        )

        goal = st.radio("목표", ["다이어트", "벌크업", "체중 유지"], horizontal=True)
        meals = st.radio("하루 식사 횟수", [2, 3, 4], index=1, horizontal=True)

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
                "편의점 위주 현실 스타일",
            ],
        )

        generate = st.button("🍽 식단 생성하기", use_container_width=True)

    with right:
        st.subheader("2️⃣ DailyMeal AI 결과")

        if generate:
            with st.spinner("로컬 엔진이 식단을 계산하는 중입니다..."):
                result = generate_meal_plan_local(
                    name, gender, age, height, weight,
                    activity, goal, meals, allergy, budget, style
                )
            st.success("🎉 식단 생성 완료!")
            st.markdown(result)
        else:
            st.info("왼쪽에서 정보를 입력하고 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()

import re
import streamlit as st
from pypdf import PdfReader

# إعدادات الصفحة
st.set_page_config(
    page_title="أداة تحليل رخص البناء ودراسة الجدوى",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ أداة تحليل رخص البناء وتوزيع المساحات والجدوى")
st.write("قم برفع ملف رخصة البناء (PDF) لاستخراج البيانات وتطبيق نموذج الدراسة والحسابات الاستثمارية.")

# 1. رفع ملف الـ PDF
uploaded_file = st.file_uploader("اختر ملف رخصة البناء (PDF)", type=["pdf"])

if uploaded_file is not None:
    # قراءة الملف واستخراج النصوص
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    st.success("تم قراءة الملف بنجاح!")

    # 2. استخراج الحقول الأساسية باستخدام التعبيرات المنتظمة (Regex)
    area_match = re.search(r"المساحة[:\s]*([\d,.]+)", text)
    total_area = float(area_match.group(1).replace(",", "")) if area_match else 500.0  # قيمة افتراضية للاختبار

    is_commercial = "تجاري" in text
    is_residential = "سكني" in text
    usage_type = []
    if is_commercial:
        usage_type.append("تجاري")
    if is_residential:
        usage_type.append("سكني")
    usage_str = " و ".join(usage_type) if usage_type else "سكني / تجاري"

    units_match = re.search(r"عدد الوحدات[:\s]*(\d+)", text)
    total_units = int(units_match.group(1)) if units_match else 6  # قيمة افتراضية

    floors_match = re.search(r"عدد الأدوار[:\s]*(\d+)", text)
    total_floors = int(floors_match.group(1)) if floors_match else 3  # قيمة افتراضية

    # عرض البيانات المستخرجة
    st.subheader("📊 ملخص بيانات الرخصة المستخرجة:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي مساحة الأرض", f"{total_area:,.2f} م²")
    col2.metric("نوع الاستخدام", usage_str)
    col3.metric("عدد الأدوار", total_floors)
    col4.metric("عدد الوحدات", total_units)

    # 3. محرك دراسة الجدوى وتوزيع المساحات
    st.markdown("---")
    st.subheader("📑 نموذج دراسة الجدوى وتوزيع المساحات المقترح:")

    # افتراضات الحسابات
    coverage_ratio = 0.60  # نسبة التغطية النظامية (60% من مساحة الأرض)
    ground_building_area = total_area * coverage_ratio
    estimated_total_built_area = ground_building_area * total_floors  # إجمالي مساحة البناء (BUA)
    efficiency_ratio = 0.80  # كفاءة المساحات القابلة للبيع/الاستثمار
    sellable_area = estimated_total_built_area * efficiency_ratio

    # عرض حسابات المساحات
    st.markdown("### 📐 تحليل وتوزيع المساحات الإنشائية")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("مساحة البناء للدور الأرضي", f"{ground_building_area:,.2f} م²")
    m_col2.metric("إجمالي مساحة البناء (BUA)", f"{estimated_total_built_area:,.2f} م²")
    m_col3.metric("المساحة القابلة للبيع / الاستثمار", f"{sellable_area:,.2f} م²")

    # حسابات الجدوى المالية التقديرية
    st.markdown("### 💰 مؤشرات الجدوى المبدئية")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        avg_unit_size = sellable_area / total_units if total_units > 0 else 0
        st.info(f"• متوسط مساحة الوحدة الواحدة (تقريبي): **{avg_unit_size:,.2f} م²**")
        
        parking_required = total_units * 1.5  # اشتراط 1.5 موقف لكل وحدة
        st.info(f"• المواقف المطلوبة تقريبياً: **{int(parking_required)} موقف**")

    with col_f2:
        estimated_cost_per_sqm = st.number_input("تكلفة البناء التقديرية للمتر (ريال)", value=1800, step=100)
        expected_sale_price_sqm = st.number_input("سعر البيع/الاستثمار المتوقع للمتر (ريال)", value=3500, step=100)
        
        total_construction_cost = estimated_total_built_area * estimated_cost_per_sqm
        potential_revenue = sellable_area * expected_sale_price_sqm
        estimated_profit = potential_revenue - total_construction_cost

        st.success(f"• إجمالي تكلفة البناء التقديرية: **{total_construction_cost:,.0f} ريال**")
        st.success(f"• العائد المتوقع (قبل قيمة الأرض والمصاريف الإدارية): **{estimated_profit:,.0f} ريال**")

    with st.expander("عرض النص الكامل المستخرج من الرخصة للمراجعة"):
        st.text(text)
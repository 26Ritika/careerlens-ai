import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from resume_analyzer import (
    extract_text_from_pdf,
    extract_skills_from_text,
    calculate_match_score,
    predict_level,
    check_ats_score,
    get_missing_skills,
    get_ai_tips,
    check_star_stories,
    rewrite_bullet_point,
    generate_interview_questions,
    generate_cover_letter,
    generate_skills_roadmap,
    analyze_resume_screenshot,
    analyze_linkedin_profile,
    generate_cold_email,
    search_jobs
)
from company_data import company_data

st.set_page_config(
    page_title="CareerLens AI",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #f0f0f5; }
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:20px;">
    <h1 style="color:#00FF88; font-size:48px;">🔍 CareerLens AI</h1>
    <p style="color:#666; font-size:16px;">AI-powered resume analyzer for top tech companies</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; gap:8px; justify-content:center; margin-bottom:24px; flex-wrap:wrap;">
    <span style="background:#4285F422; border:1px solid #4285F4; border-radius:8px; padding:6px 12px; color:#4285F4; font-size:12px;">🔵 Google</span>
    <span style="background:#FF990022; border:1px solid #FF9900; border-radius:8px; padding:6px 12px; color:#FF9900; font-size:12px;">🟠 Amazon</span>
    <span style="background:#0866FF22; border:1px solid #0866FF; border-radius:8px; padding:6px 12px; color:#0866FF; font-size:12px;">🔵 Meta</span>
    <span style="background:#00A4EF22; border:1px solid #00A4EF; border-radius:8px; padding:6px 12px; color:#00A4EF; font-size:12px;">🟢 Microsoft</span>
    <span style="background:#E5091422; border:1px solid #E50914; border-radius:8px; padding:6px 12px; color:#E50914; font-size:12px;">🔴 Netflix</span>
    <span style="background:#55555522; border:1px solid #888; border-radius:8px; padding:6px 12px; color:#aaa; font-size:12px;">⚫ Apple</span>
    <span style="background:#0A66C222; border:1px solid #0A66C2; border-radius:8px; padding:6px 12px; color:#0A66C2; font-size:12px;">🔷 LinkedIn</span>
    <span style="background:#00000022; border:1px solid #555; border-radius:8px; padding:6px 12px; color:#aaa; font-size:12px;">⚫ Uber</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 CareerLens AI")

    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

    selected_company = st.selectbox(
        "🏢 Target Company",
        list(company_data.keys()),
        format_func=lambda x: f"{company_data[x]['logo']} {x}"
    )

    st.divider()

    analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

    st.divider()
    st.markdown(f"""
    ### About {selected_company}
    *Culture:* {company_data[selected_company]['culture']}

    *💡 Tip:* {company_data[selected_company]['tip']}
    """)

# ── Analysis ──────────────────────────────────────────────────────────────────
if uploaded_file and analyze_btn:
    for key in ["ai_tips","rewritten","questions_out","cover_out","roadmap",
                "screenshot_out","linkedin_out","cold_email_out","jobs_out"]:
        if key in st.session_state:
            del st.session_state[key]

    with st.spinner("🤖 CareerLens AI analyzing your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

        if not resume_text:
            st.error("Could not read PDF!")
            st.stop()

        match_score    = calculate_match_score(resume_text, selected_company)
        found_skills   = extract_skills_from_text(resume_text)
        missing_skills = get_missing_skills(resume_text, selected_company)
        level_code, level_name = predict_level(resume_text, selected_company)
        ats_score, ats_issues  = check_ats_score(resume_text)
        star_score, has_s, has_t, has_a, has_r = check_star_stories(resume_text)

        st.session_state["resume_text"]    = resume_text
        st.session_state["match_score"]    = match_score
        st.session_state["found_skills"]   = found_skills
        st.session_state["missing_skills"] = missing_skills
        st.session_state["level_code"]     = level_code
        st.session_state["level_name"]     = level_name
        st.session_state["ats_score"]      = ats_score
        st.session_state["ats_issues"]     = ats_issues
        st.session_state["star_score"]     = star_score
        st.session_state["has_s"]          = has_s
        st.session_state["has_t"]          = has_t
        st.session_state["has_a"]          = has_a
        st.session_state["has_r"]          = has_r
        st.session_state["company"]        = selected_company
        st.session_state["analyzed"]       = True

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("analyzed"):

    resume_text      = st.session_state["resume_text"]
    match_score      = st.session_state["match_score"]
    found_skills     = st.session_state["found_skills"]
    missing_skills   = st.session_state["missing_skills"]
    level_code       = st.session_state["level_code"]
    level_name       = st.session_state["level_name"]
    ats_score        = st.session_state["ats_score"]
    ats_issues       = st.session_state["ats_issues"]
    star_score       = st.session_state["star_score"]
    has_s            = st.session_state["has_s"]
    has_t            = st.session_state["has_t"]
    has_a            = st.session_state["has_a"]
    has_r            = st.session_state["has_r"]
    selected_company = st.session_state["company"]

    company       = company_data[selected_company]
    company_color = company["color"]

    st.markdown(f"## 📊 Results for {company['logo']} {selected_company}")

    # ── Score cards ───────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        score_color = "#34A853" if match_score >= 70 else "#FBBC04" if match_score >= 50 else "#EA4335"
        st.markdown(f'<div class="metric-card"><div style="font-size:40px;font-weight:900;color:{score_color}">{match_score}</div><div style="color:#666;font-size:11px;">MATCH /100</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="metric-card"><div style="font-size:28px;font-weight:900;color:{company_color}">{level_code}</div><div style="color:#ccc;font-size:11px;">{level_name[:15]}</div><div style="color:#666;font-size:10px;">LEVEL</div></div>', unsafe_allow_html=True)

    with col3:
        ats_color = "#34A853" if ats_score >= 70 else "#FBBC04" if ats_score >= 50 else "#EA4335"
        st.markdown(f'<div class="metric-card"><div style="font-size:40px;font-weight:900;color:{ats_color}">{ats_score}</div><div style="color:#666;font-size:11px;">ATS /100</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="metric-card"><div style="font-size:40px;font-weight:900;color:#7B61FF">{len(found_skills)}</div><div style="color:#666;font-size:11px;">SKILLS</div></div>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<div class="metric-card"><div style="font-size:40px;font-weight:900;color:#00FF88">{star_score}</div><div style="color:#666;font-size:11px;">STAR /100</div></div>', unsafe_allow_html=True)

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match_score,
            title={'text': f"{selected_company} Match"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': company_color},
                'steps': [
                    {'range': [0,  50], 'color': "#1a1a2e"},
                    {'range': [50, 75], 'color': "#16213e"},
                    {'range': [75,100], 'color': "#0f3460"}
                ],
                'threshold': {'line': {'color': "#00FF88", 'width': 4},
                              'thickness': 0.75, 'value': 75}
            }
        ))
        fig.update_layout(paper_bgcolor="#0d1117", font_color="#f0f0f5", height=280)
        st.plotly_chart(fig, use_container_width=False)

    with col_right:
        categories = ['Skills','Keywords','ATS','STAR','Experience']
        values = [
            len(found_skills) / len(company["required_skills"]) * 100,
            match_score, ats_score, star_score, min(match_score + 10, 100)
        ]
        fig2 = go.Figure(go.Scatterpolar(
            r=values, theta=categories, fill='toself',
            fillcolor=f"{company_color}", line_color=company_color
        ))
        fig2.update_layout(
            polar=dict(bgcolor="#161b22", radialaxis=dict(visible=True, range=[0,100])),
            paper_bgcolor="#0d1117", font_color="#f0f0f5",
            title="Skills Radar", height=280
        )
        st.plotly_chart(fig2, use_container_width=False)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9,tab10,tab11,tab12 = st.tabs([
        "✅ Skills", "❌ Missing", "📋 ATS", "⭐ STAR", "💡 AI Tips",
        "✍️ Rewriter", "🎤 Interview Qs", "📝 Cover Letter",
        "📸 Screenshot", "🔗 LinkedIn", "📧 Cold Email", "🌐 Job Search"
    ])

    with tab1:
        st.markdown("### ✅ Skills Found")
        if found_skills:
            cols = st.columns(4)
            for i, skill in enumerate(found_skills):
                with cols[i % 4]:
                    st.markdown(f'<div style="background:#34A85322;border:1px solid #34A853;border-radius:8px;padding:8px;margin:4px;text-align:center;color:#34A853;font-size:13px;">✅ {skill}</div>', unsafe_allow_html=True)
        else:
            st.warning("No matching skills found!")

    with tab2:
        st.markdown(f"### ❌ Missing Skills for {selected_company}")
        if missing_skills:
            cols = st.columns(4)
            for i, skill in enumerate(missing_skills):
                with cols[i % 4]:
                    st.markdown(f'<div style="background:#EA433522;border:1px solid #EA4335;border-radius:8px;padding:8px;margin:4px;text-align:center;color:#EA4335;font-size:13px;">❌ {skill}</div>', unsafe_allow_html=True)
            st.divider()
            st.markdown("### 🗺️ Learning Roadmap")
            if st.button("Generate Roadmap", key="roadmap_btn"):
                with st.spinner("Creating your roadmap..."):
                    st.session_state["roadmap"] = generate_skills_roadmap(missing_skills, selected_company)
            if "roadmap" in st.session_state:
                st.markdown(f'<div style="background:#161b22;border-left:4px solid #7B61FF;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:1.8;">{st.session_state["roadmap"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)
        else:
            st.success("You have all required skills!")

    with tab3:
        st.markdown("### 📋 ATS Compatibility")
        ats_color = "#34A853" if ats_score >= 70 else "#FBBC04" if ats_score >= 50 else "#EA4335"
        st.markdown(f'<div style="background:#161b22;border:1px solid {ats_color};border-radius:12px;padding:20px;margin-bottom:16px;"><h2 style="color:{ats_color}">ATS Score: {ats_score}/100</h2></div>', unsafe_allow_html=True)
        if ats_issues:
            for issue in ats_issues:
                st.markdown(f'<div style="background:#161b22;border-left:4px solid #EA4335;border-radius:8px;padding:12px;margin:6px 0;color:#ccc;">{issue}</div>', unsafe_allow_html=True)
        else:
            st.success("Great ATS compatibility!")

    with tab4:
        st.markdown("### ⭐ STAR Story Analysis")
        st.markdown(f"*STAR Score: {star_score}/100*")
        for name, found, desc in [
            ("Situation", has_s, "Setting context"),
            ("Task",      has_t, "Your responsibilities"),
            ("Action",    has_a, "What YOU did"),
            ("Result",    has_r, "Measurable outcomes")
        ]:
            color = "#34A853" if found else "#EA4335"
            icon  = "✅" if found else "❌"
            st.markdown(f'<div style="background:#161b22;border:1px solid {color};border-radius:8px;padding:12px;margin:6px 0;"><b style="color:{color}">{icon} {name}</b><span style="color:#666;"> — {desc}</span></div>', unsafe_allow_html=True)

    with tab5:
        st.markdown(f"### 💡 AI Tips for {selected_company}")
        if st.button("Generate Tips", key="tips"):
            with st.spinner("AI generating tips..."):
                st.session_state["ai_tips"] = get_ai_tips(resume_text, selected_company, match_score)
        if "ai_tips" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #00FF88;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:1.8;">{st.session_state["ai_tips"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)

    with tab6:
        st.markdown("### ✍️ Resume Bullet Rewriter")
        st.markdown(f"Paste a weak bullet point and get {selected_company}-style rewrites!")
        bullet_input = st.text_area("Paste your weak bullet point:", placeholder="e.g. Worked on backend systems and fixed bugs", height=100)
        if st.button("✍️ Rewrite!", key="rewrite"):
            if bullet_input:
                with st.spinner("AI rewriting..."):
                    st.session_state["rewritten"] = rewrite_bullet_point(bullet_input, selected_company)
            else:
                st.warning("Please enter a bullet point!")
        if "rewritten" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #FBBC04;border-radius:8px;padding:20px;"><b style="color:#FBBC04">Rewritten Versions:</b><br/><br/><span style="color:#ccc;line-height:1.8;">{st.session_state["rewritten"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)

    with tab7:
        st.markdown(f"### 🎤 Likely {selected_company} Interview Questions")
        if st.button("🎤 Generate Questions", key="questions"):
            with st.spinner("Generating questions..."):
                st.session_state["questions_out"] = generate_interview_questions(resume_text, selected_company)
        if "questions_out" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #4285F4;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:2.0;">{st.session_state["questions_out"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)

    with tab8:
        st.markdown("### 📝 Cover Letter Generator")
        job_role = st.text_input("Job Role", placeholder=f"e.g. Senior Software Engineer at {selected_company}")
        if st.button("📝 Generate Cover Letter", key="cover"):
            if job_role:
                with st.spinner("Writing cover letter..."):
                    st.session_state["cover_out"] = generate_cover_letter(resume_text, selected_company, job_role)
            else:
                st.warning("Please enter job role!")
        if "cover_out" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #EA4335;border-radius:8px;padding:20px;"><b style="color:#EA4335">Cover Letter:</b><br/><br/><span style="color:#ccc;line-height:1.8;">{st.session_state["cover_out"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)
            st.text_area("Copy from here:", value=st.session_state["cover_out"], height=200)

    with tab9:
        st.markdown("### 📸 Resume Screenshot Analyzer")
        st.markdown("Upload a screenshot or photo of any resume for instant AI analysis!")
        screenshot = st.file_uploader("Upload Resume Image", type=["jpg","jpeg","png"], key="screenshot")
        if st.button("🔍 Analyze Screenshot", key="analyze_screenshot"):
            if screenshot:
                with st.spinner("AI analyzing image..."):
                    st.session_state["screenshot_out"] = analyze_resume_screenshot(screenshot)
            else:
                st.warning("Please upload an image!")
        if "screenshot_out" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #7B61FF;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:1.8;">{st.session_state["screenshot_out"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)

    with tab10:
        st.markdown("### 🔗 LinkedIn Profile Analyzer")
        st.markdown(f"Optimize your LinkedIn for {selected_company} recruiters!")
        linkedin_url = st.text_input("Your LinkedIn URL", placeholder="https://linkedin.com/in/yourname")
        if st.button("🔗 Analyze LinkedIn", key="linkedin_btn"):
            if linkedin_url:
                with st.spinner("Analyzing your LinkedIn profile..."):
                    st.session_state["linkedin_out"] = analyze_linkedin_profile(linkedin_url, selected_company)
            else:
                st.warning("Please enter your LinkedIn URL!")
        if "linkedin_out" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #0A66C2;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:1.8;">{st.session_state["linkedin_out"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)

    with tab11:
        st.markdown("### 📧 Cold Email Generator")
        st.markdown(f"Write cold emails that get responses from {selected_company} recruiters!")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            your_name = st.text_input("Your Name", placeholder="John Doe")
        with col_e2:
            recipient_role = st.selectbox("Email Recipient", [
                "Hiring Manager", "Recruiter", "Engineering Manager",
                "Tech Lead", "HR Manager", "VP of Engineering"
            ])
        if st.button("📧 Generate Cold Emails", key="cold_email_btn"):
            if your_name:
                with st.spinner("Writing cold emails..."):
                    st.session_state["cold_email_out"] = generate_cold_email(
                        resume_text, selected_company, recipient_role, your_name
                    )
            else:
                st.warning("Please enter your name!")
        if "cold_email_out" in st.session_state:
            st.markdown(f'<div style="background:#161b22;border-left:4px solid #EA4335;border-radius:8px;padding:20px;"><span style="color:#ccc;line-height:1.8;">{st.session_state["cold_email_out"].replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)
            st.text_area("Copy from here:", value=st.session_state["cold_email_out"], height=200)

    with tab12:
        st.markdown("### 🌐 Job Search")
        st.markdown("Find real jobs matching your skills!")
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            job_query = st.text_input("Job Title / Skills", placeholder="e.g. Python Developer, ML Engineer")
        with col_j2:
            job_location = st.selectbox("Location", [
                "India", "Remote", "USA", "UK", "Singapore",
                "Bangalore", "Mumbai", "Delhi", "Hyderabad"
            ])
        use_company_filter = st.checkbox(f"Search only at {selected_company}")
        if st.button("🔍 Search Jobs", key="job_search_btn"):
            if job_query:
                with st.spinner("Searching jobs..."):
                    company_filter = selected_company if use_company_filter else None
                    jobs, error = search_jobs(job_query, job_location, company_filter)
                    if error:
                        st.error(error)
                    else:
                        st.session_state["jobs_out"] = jobs
            else:
                st.warning("Please enter a job title!")

        if "jobs_out" in st.session_state and st.session_state["jobs_out"]:
            jobs = st.session_state["jobs_out"]
            st.markdown(f"### Found {len(jobs)} Jobs")
            for job in jobs:
                title      = job.get("job_title", "N/A")
                company_n  = job.get("employer_name", "N/A")
                location   = (job.get("job_city") or "") + " " + (job.get("job_country") or "")
                apply_link = job.get("job_apply_link", "#")
                posted     = job.get("job_posted_at_datetime_utc", "")[:10] if job.get("job_posted_at_datetime_utc") else "Recent"
                employment = job.get("job_employment_type", "")
                st.markdown(f"""
                <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px;margin:10px 0;">
                    <div style="color:#00FF88;font-size:16px;font-weight:700;">{title}</div>
                    <div style="color:#aaa;font-size:13px;margin-top:4px;">🏢 {company_n}</div>
                    <div style="color:#666;font-size:12px;margin-top:2px;">📍 {location.strip()} · {employment}</div>
                    <div style="color:#555;font-size:11px;margin-top:2px;">📅 Posted: {posted}</div>
                    <a href="{apply_link}" target="_blank" style="display:inline-block;margin-top:12px;background:#00FF8822;border:1px solid #00FF88;border-radius:8px;padding:6px 16px;color:#00FF88;text-decoration:none;font-size:13px;font-weight:600;">Apply Now →</a>
                </div>
                """, unsafe_allow_html=True)

    # ── Company Criteria ──────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"### 🎯 {selected_company} Hiring Criteria")
    criteria = company_data[selected_company]["hiring_criteria"]
    cols = st.columns(min(len(criteria), 4))
    for i, criterion in enumerate(criteria[:8]):
        with cols[i % min(len(criteria), 4)]:
            st.markdown(f'<div style="background:#161b22;border:1px solid {company_color}44;border-radius:8px;padding:10px;margin:4px;text-align:center;"><span style="color:{company_color};font-size:12px;">🎯 {criterion}</span></div>', unsafe_allow_html=True)

else:
    st.markdown('<div style="text-align:center;padding:20px;"><h2 style="color:#fff;">How CareerLens AI Works</h2></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for i, (icon, title, desc) in enumerate([
        ("📄","Upload Resume","Upload your PDF resume"),
        ("🏢","Select Company","Choose target company"),
        ("🤖","AI Analysis","BERT + ML analyzes resume"),
        ("📊","Get Results","Score + tips + tools")
    ]):
        with [col1,col2,col3,col4][i]:
            st.markdown(f'<div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;text-align:center;"><div style="font-size:36px;">{icon}</div><h3 style="color:#fff;margin:8px 0;">{title}</h3><p style="color:#666;font-size:13px;">{desc}</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:32px;color:#555;">
        <h3>12 Features In One App!</h3>
        <p>✅ Skills | ❌ Gaps | 📋 ATS | ⭐ STAR | 💡 Tips | ✍️ Rewriter</p>
        <p>🎤 Interview | 📝 Cover Letter | 📸 Screenshot | 🔗 LinkedIn | 📧 Cold Email | 🌐 Jobs</p>
    </div>""", unsafe_allow_html=True)

st.divider()
st.markdown('<p style="text-align:center;color:#444;font-size:12px;">🔍 CareerLens AI</p>', unsafe_allow_html=True)
import os
import re
import base64
import requests
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from company_data import company_data
import PyPDF2

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file!")

client = Groq(api_key=api_key)

def ask_groq(prompt, system_prompt=None):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        result = response.choices[0].message.content
        return result if result and result.strip() else "⚠️ AI returned empty response. Try again."
    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text.strip()
    except:
        return ""

def extract_skills_from_text(text):
    all_skills = [
        "Python", "Java", "JavaScript", "C++", "C#",
        "React", "Node.js", "Angular", "Vue", "TypeScript",
        "Machine Learning", "Deep Learning", "NLP",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Git", "Linux", "System Design", "Microservices",
        "REST API", "GraphQL", "Distributed Systems",
        "Data Structures", "Algorithms", "Problem Solving",
        "Swift", "Kotlin", "Go", "Rust", "Scala",
        "Hadoop", "Spark", "Kafka", "Redis",
        "Leadership", "Communication", "Teamwork",
        "Agile", "Scrum", "DevOps", "CI/CD"
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in all_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills

def calculate_match_score(resume_text, company_name):
    company = company_data[company_name]
    resume_lower = resume_text.lower()
    required_skills = company["required_skills"]
    found_skills = sum(1 for s in required_skills if s.lower() in resume_lower)
    skills_score = (found_skills / len(required_skills)) * 40
    keywords = company["keywords"]
    found_keywords = sum(1 for k in keywords if k.lower() in resume_lower)
    keywords_score = (found_keywords / len(keywords)) * 30
    experience_patterns = [r'\d+ years?', r'\d+ months?', r'senior',
                           r'lead', r'principal', r'architect']
    exp_found = sum(1 for p in experience_patterns if re.search(p, resume_lower))
    experience_score = min((exp_found / 3) * 20, 20)
    achievement_patterns = [r'\d+%', r'increased', r'decreased',
                            r'improved', r'reduced', r'achieved',
                            r'built', r'launched', r'million']
    ach_found = sum(1 for p in achievement_patterns if re.search(p, resume_lower))
    achievement_score = min((ach_found / 5) * 10, 10)
    return round(skills_score + keywords_score + experience_score + achievement_score)

def predict_level(resume_text, company_name):
    resume_lower = resume_text.lower()
    company = company_data[company_name]
    levels = list(company["levels"].keys())
    if any(w in resume_lower for w in ["principal", "architect", "director"]):
        return levels[-1], company["levels"][levels[-1]]
    elif any(w in resume_lower for w in ["staff", "lead", "10+ years"]):
        return levels[-2], company["levels"][levels[-2]]
    elif any(w in resume_lower for w in ["senior", "5+ years", "6+ years"]):
        idx = 2 if len(levels) > 2 else -1
        return levels[idx], company["levels"][levels[idx]]
    elif any(w in resume_lower for w in ["3+ years", "4+ years"]):
        return levels[1], company["levels"][levels[1]]
    else:
        return levels[0], company["levels"][levels[0]]

def check_ats_score(resume_text):
    score = 100
    issues = []
    words = len(resume_text.split())
    if words < 200:
        score -= 20
        issues.append("❌ Resume too short (under 200 words)")
    elif words > 1000:
        score -= 10
        issues.append("⚠️ Resume might be too long (over 1000 words)")
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        score -= 15
        issues.append("❌ No email address found")
    if not re.search(r'\d+%|\d+ million|\d+ thousand', resume_text):
        score -= 15
        issues.append("❌ No quantified achievements (add numbers like 40% or $2M)")
    action_verbs = ["built", "developed", "led", "improved", "designed",
                    "implemented", "created", "launched", "managed"]
    found_verbs = sum(1 for v in action_verbs if v in resume_text.lower())
    if found_verbs < 3:
        score -= 10
        issues.append("⚠️ Add more action verbs (built, led, designed…)")
    return max(score, 0), issues

def get_missing_skills(resume_text, company_name):
    company = company_data[company_name]
    resume_lower = resume_text.lower()
    return [s for s in company["required_skills"] if s.lower() not in resume_lower]

def get_ai_tips(resume_text, company_name, score):
    company = company_data[company_name]
    prompt = f"""You are an expert career coach specializing in {company_name} hiring.
Resume Score: {score}/100
Company Culture: {company['culture']}
Key Hiring Criteria: {', '.join(company['hiring_criteria'][:4])}
Resume (first 600 chars): {resume_text[:600]}
Give exactly 5 specific, actionable tips to improve this resume for {company_name}.
Number each tip clearly (1. 2. 3. 4. 5.)
Be direct and specific — no generic advice.
End with one motivating sentence."""
    return ask_groq(prompt)

def check_star_stories(resume_text):
    text_lower = resume_text.lower()
    has_s = any(w in text_lower for w in ["when", "while", "during", "at", "worked"])
    has_t = any(w in text_lower for w in ["responsible", "tasked", "needed", "goal"])
    has_a = any(w in text_lower for w in ["built", "developed", "implemented", "led"])
    has_r = any(w in text_lower for w in ["resulted", "achieved", "improved", "increased", "%"])
    star_score = sum([has_s, has_t, has_a, has_r]) * 25
    return star_score, has_s, has_t, has_a, has_r

def rewrite_bullet_point(bullet_point, company_name):
    company = company_data[company_name]
    prompt = f"""You are a professional resume writer for {company_name}.
Company culture: {company['culture']}
Weak bullet point: "{bullet_point}"
Rewrite into 3 strong versions.
Rules:
- Start with STRONG action verb
- Include specific numbers or metrics
- Show clear business impact
- Match {company_name} culture
- Maximum 2 lines each
Format:
Version 1: [rewritten bullet]
Version 2: [rewritten bullet]
Version 3: [rewritten bullet]"""
    return ask_groq(prompt)

def generate_interview_questions(resume_text, company_name):
    company = company_data[company_name]
    skills = extract_skills_from_text(resume_text)
    skills_str = ', '.join(skills[:10]) if skills else "general software engineering"
    prompt = f"""You are a senior interviewer at {company_name}.
Company culture: {company['culture']}
Hiring criteria: {', '.join(company['hiring_criteria'][:4])}
Candidate skills: {skills_str}
Generate 10 interview questions.
Format:
[Technical] 1. Question
[Technical] 2. Question
[Technical] 3. Question
[Behavioral] 4. Question
[Behavioral] 5. Question
[Behavioral] 6. Question
[System Design] 7. Question
[System Design] 8. Question
[Role Specific] 9. Question
[Role Specific] 10. Question
After each question add: 💡 Tip: one line advice"""
    return ask_groq(prompt)

def generate_cover_letter(resume_text, company_name, job_role):
    company = company_data[company_name]
    skills = extract_skills_from_text(resume_text)
    skills_str = ', '.join(skills[:8]) if skills else "software engineering"
    prompt = f"""You are an expert cover letter writer.
Company: {company_name}
Role: {job_role}
Company culture: {company['culture']}
Top candidate skills: {skills_str}
Resume summary: {resume_text[:300]}
Write a 3-paragraph cover letter:
1. Strong hook (NOT "I am applying for...")
2. Connect top 3 skills to {company_name} needs
3. Confident call to action
Rules:
- Under 300 words
- Mention {company_name} at least twice
- No generic phrases"""
    return ask_groq(prompt)

def generate_skills_roadmap(missing_skills, company_name):
    skills_str = ', '.join(missing_skills[:8]) if missing_skills else "core engineering skills"
    prompt = f"""You are a career coach for {company_name}.
Missing skills: {skills_str}
Create a 3-month learning roadmap.
Format:
📅 Month 1 — Foundation
Skills: [list]
Resources: [free resources]
Goal: [outcome]

📅 Month 2 — Building
Skills: [list]
Resources: [free resources]
Goal: [outcome]

📅 Month 3 — Practice & Apply
Skills: [list]
Resources: [free resources]
Goal: [outcome]

✅ Final milestone: [one sentence]
Include YouTube channels, free courses, official docs."""
    return ask_groq(prompt)

def analyze_resume_screenshot(image_file):
    try:
        image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this resume image and provide:
1. Overall Resume Score (0-100)
2. Top 5 skills visible
3. Experience level detected
4. 3 strengths
5. 3 weaknesses
6. 5 specific improvements
Be detailed and specific."""
                    }
                ]
            }],
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"

def analyze_linkedin_profile(linkedin_url, company_name):
    try:
        prompt = f"""You are a LinkedIn profile expert and career coach for {company_name}.
LinkedIn URL: {linkedin_url}
Based on best LinkedIn practices and {company_name} hiring standards, provide:
1. 📋 Profile Completeness Score (0-100)
2. 🎯 5 improvements for LinkedIn headline
3. 💼 How to optimize About section for {company_name}
4. 🔑 Top keywords to add for {company_name} recruiters
5. 📸 Profile photo and banner tips
6. 🌟 How to make experience section stand out
7. 🤝 Networking strategy for {company_name}
Be specific and actionable!"""
        return ask_groq(prompt)
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_cold_email(resume_text, company_name, recipient_role, your_name):
    try:
        skills = extract_skills_from_text(resume_text)
        skills_str = ', '.join(skills[:6]) if skills else "software engineering"
        company = company_data[company_name]
        prompt = f"""You are an expert at writing cold outreach emails that get responses.
Write a cold email from {your_name} to a {recipient_role} at {company_name}.
Candidate skills: {skills_str}
Company culture: {company['culture']}
Resume summary: {resume_text[:300]}

VERSION 1 — Short & Direct (under 100 words):
Subject: [subject]
[email body]

VERSION 2 — Story-driven (under 150 words):
Subject: [subject]
[email body]

VERSION 3 — Value-first (under 150 words):
Subject: [subject]
[email body]

Rules:
- Never start with "I am reaching out"
- Show specific knowledge of {company_name}
- Clear single call to action
- Professional but human tone"""
        return ask_groq(prompt)
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_jobs(query, location="India", company_filter=None):
    try:
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if not rapidapi_key:
            return None, "❌ RAPIDAPI_KEY not found in .env file! Add it to your .env file."
        url = "https://jsearch.p.rapidapi.com/search"
        search_query = f"{query} at {company_filter} in {location}" if company_filter else f"{query} in {location}"
        params = {
            "query": search_query,
            "num_results": "10",
            "date_posted": "month"
        }
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if "data" not in data or not data["data"]:
            return None, "No jobs found. Try different search terms or location."
        return data["data"], None
    except requests.exceptions.Timeout:
        return None, "❌ Request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return None, "❌ Connection error. Check your internet connection."
    except Exception as e:
        return None, f"❌ Job search error: {str(e)}"
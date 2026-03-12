import re
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from jobs.models import Job
from applications.models import Application
from accounts.models import Profile
from ideas.models import StartupIdea
from PyPDF2 import PdfReader
from io import BytesIO


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return ""


def extract_skills_from_text(text):
    """Extract skills from resume text using keyword matching"""
    text = text.lower()
    
    # Common tech skills
    skills_list = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'git', 'linux', 'machine learning', 'deep learning',
        'data science', 'analytics', 'tableau', 'power bi', 'excel', 'word', 'powerpoint',
        'communication', 'leadership', 'teamwork', 'problem solving', 'agile', 'scrum',
        'project management', 'product management', 'marketing', 'sales', 'seo', 'sem',
        'graphic design', 'ui/ux', 'figma', 'sketch', 'photoshop', 'illustrator'
    ]
    
    found_skills = []
    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
    
    return found_skills


def calculate_match_score(job_skills, resume_skills):
    """Calculate match score between job requirements and resume skills using simple set logic"""
    if not job_skills or not resume_skills:
        return 0

    job_skills = [s.lower().strip() for s in job_skills]
    resume_skills = [s.lower().strip() for s in resume_skills]

    matched = set(resume_skills) & set(job_skills)
    match_percent = (len(matched) / len(job_skills)) * 100
    return round(match_percent, 2)


def generate_idea_summary(title, problem, solution, target_audience):
    """Generate AI summary for startup idea"""
    summary = f"A startup idea focused on {target_audience} that addresses {problem[:100]}..."
    if len(problem) > 100:
        summary += " The proposed solution involves implementing a system to provide value through innovative approaches."
    return summary


def analyze_idea_strengths_weaknesses(title, problem, solution, target_audience):
    """Analyze strengths and weaknesses of a startup idea"""
    strengths = []
    weaknesses = []
    
    # Analyze problem statement
    if len(problem) > 50:
        strengths.append("Clear problem statement identified")
    else:
        weaknesses.append("Problem statement could be more detailed")
    
    # Analyze solution
    if len(solution) > 50:
        strengths.append("Solution is well-defined")
    else:
        weaknesses.append("Solution needs more elaboration")
    
    # Analyze target audience
    if len(target_audience) > 20:
        strengths.append("Target audience clearly defined")
    else:
        weaknesses.append("Target audience needs more specificity")
    
    # Check for innovation keywords
    innovation_keywords = ['innovative', 'unique', 'novel', 'disrupt', 'transform', 'revolutionary']
    has_innovation = any(kw in solution.lower() for kw in innovation_keywords)
    if has_innovation:
        strengths.append("Shows potential for innovation")
    
    return strengths, weaknesses


def calculate_market_score(category):
    """Calculate market potential score based on category"""
    category_scores = {
        'technology': 9,
        'healthcare': 9,
        'finance': 8,
        'education': 8,
        'e-commerce': 7,
        'food': 6,
        'travel': 6,
        'real_estate': 7,
        'entertainment': 7,
        'social': 8,
        'other': 5
    }
    return category_scores.get(category, 5)


def generate_trend_analysis(category):
    """Generate trend analysis for a startup category"""
    trend_analyses = {
        'technology': "Tech startups continue to see strong investor interest, especially in AI, cloud, and cybersecurity sectors.",
        'healthcare': "Healthcare tech is growing rapidly with focus on telemedicine, health tracking, and AI diagnostics.",
        'finance': "Fintech solutions are disrupting traditional banking with digital payments, blockchain, and robo-advisors.",
        'education': "EdTech remains strong with online learning, skill development, and remote education platforms.",
        'e-commerce': "E-commerce continues to grow with focus on personalization, social commerce, and sustainability.",
        'food': "Food tech is evolving with meal delivery, ghost kitchens, and sustainable food solutions.",
        'travel': "Travel tech is recovering with focus on experiences, remote work travel, and sustainable tourism.",
        'real_estate': "PropTech is transforming real estate with digital platforms, smart homes, and fractional ownership.",
        'entertainment': "Entertainment is shifting to streaming, gaming, and interactive content experiences.",
        'social': "Social impact startups are gaining traction with focus on sustainability, equity, and community.",
        'other': "Market analysis depends on specific niche and implementation strategy."
    }
    return trend_analyses.get(category, "Market potential varies based on specific implementation and market conditions.")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def match_resume(request):
    """Match resume with job requirements"""
    job_id = request.data.get('job_id')
    resume_file = request.FILES.get('resume')
    
    if not job_id:
        return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not resume_file:
        return Response({'error': 'resume file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Extract text from PDF
    text = extract_text_from_pdf(resume_file)
    
    if not text:
        return Response({'error': 'Could not extract text from PDF'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract skills
    skills = extract_skills_from_text(text)
    
    # Calculate match score
    match_score = calculate_match_score(job.skills, skills)
    
    return Response({
        'job_id': job_id,
        'job_title': job.title,
        'extracted_skills': skills,
        'job_required_skills': job.skills,
        'match_score': match_score
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_jobs(request):
    """Recommend jobs based on user profile"""
    user = request.user
    
    if user.role != 'seeker':
        return Response({'error': 'Only job seekers can get recommendations'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found. Please create a profile first.'}, status=status.HTTP_404_NOT_FOUND)
    
    user_skills = profile.skills or []
    
    if not user_skills:
        return Response({
            'message': 'No skills found in profile. Please update your profile with skills.',
            'recommendations': []
        })
    
    # Get approved jobs
    jobs = Job.objects.filter(status='approved')
    
    recommendations = []
    for job in jobs:
        score = calculate_match_score(job.skills, user_skills)
        if score > 0:
            recommendations.append({
                'job_id': job.id,
                'title': job.title,
                'company': job.recruiter.company.name if hasattr(job.recruiter, 'company') else 'Unknown',
                'location': job.location,
                'job_type': job.job_type,
                'match_score': score
            })
    
    # Sort by match score
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return Response({
        'user_skills': user_skills,
        'recommendations': recommendations[:20]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_idea(request):
    """Analyze a startup idea using AI"""
    title = request.data.get('title')
    problem_statement = request.data.get('problem_statement')
    solution = request.data.get('solution')
    target_audience = request.data.get('target_audience')
    category = request.data.get('category', 'other')
    
    if not all([title, problem_statement, solution, target_audience]):
        return Response({
            'error': 'title, problem_statement, solution, and target_audience are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate insights
    summary = generate_idea_summary(title, problem_statement, solution, target_audience)
    strengths, weaknesses = analyze_idea_strengths_weaknesses(title, problem_statement, solution, target_audience)
    market_score = calculate_market_score(category)
    trend_analysis = generate_trend_analysis(category)
    
    return Response({
        'title': title,
        'ai_summary': summary,
        'ai_strengths': strengths,
        'ai_weaknesses': weaknesses,
        'ai_market_score': market_score,
        'ai_trend_analysis': trend_analysis
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parse_resume(request):
    """Parse resume and extract skills"""
    resume_file = request.FILES.get('resume')
    
    if not resume_file:
        return Response({'error': 'resume file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract text from PDF
    text = extract_text_from_pdf(resume_file)
    
    if not text:
        return Response({'error': 'Could not extract text from PDF'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract skills
    skills = extract_skills_from_text(text)
    
    return Response({
        'extracted_skills': skills,
        'text_preview': text[:500]
    })


def calculate_skill_gap(job_skills, user_skills):
    """Calculate matched and missing skills using simple set logic"""
    if not job_skills:
        return [], []

    if not user_skills:
        return [], job_skills

    job_skills_lower = set(s.lower().strip() for s in job_skills)
    user_skills_lower = set(s.lower().strip() for s in user_skills)

    matched = list(job_skills_lower & user_skills_lower)
    missing = list(job_skills_lower - user_skills_lower)

    return matched, missing


def extract_years_from_experience(experience_str):
    """Extract years from experience string like '3 years', '2-4 years', '5+ years'"""
    if not experience_str:
        return None
    
    import re
    
    # Match patterns like "3 years", "2-4 years", "5+ years", "3-5"
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)?',  # 3 years, 3yrs, 3+
        r'(\d+)\s*-\s*(\d+)',  # 2-4 years
    ]
    
    for pattern in patterns:
        match = re.search(pattern, experience_str.lower())
        if match:
            if len(match.groups()) == 1:
                return int(match.group(1))
            elif len(match.groups()) == 2:
                # Return average for range
                return (int(match.group(1)) + int(match.group(2))) // 2
    
    return None


def calculate_experience_gap(job_experience, user_experience):
    """Calculate experience gap"""
    if not job_experience:
        return None
    
    if not user_experience:
        return {
            'required': job_experience,
            'you_have': 'Not specified',
            'gap_description': f'Job requires {job_experience} of experience'
        }
    
    # Parse experience requirements
    job_years = extract_years_from_experience(job_experience)
    user_years = extract_years_from_experience(user_experience)
    
    if job_years and user_years is not None:
        gap = job_years - user_years
        if gap > 0:
            gap_description = f'You need {gap} more year(s) of experience'
        elif gap < 0:
            gap_description = f'You exceed the requirement by {abs(gap)} year(s)'
        else:
            gap_description = 'You meet the experience requirement'
        
        return {
            'required': job_experience,
            'you_have': user_experience,
            'gap_years': gap,
            'gap_description': gap_description
        }
    
    return {
        'required': job_experience,
        'you_have': user_experience,
        'gap_description': f'Job requires {job_experience} of experience'
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def job_match_details(request):
    """Get detailed match information for a job including skill gap and experience gap"""
    job_id = request.data.get('job_id')
    
    if not job_id:
        return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Only seekers can get job match details
    if user.role != 'seeker':
        return Response({'error': 'Only job seekers can get job match details'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get user's profile and skills
    try:
        profile = user.profile
        user_skills = profile.skills or []
    except Profile.DoesNotExist:
        user_skills = []
    
    # Get work experience from profile
    user_experience = None
    if profile.employment_history and len(profile.employment_history) > 0:
        # Calculate total years of experience from employment history
        total_years = 0
        for job_exp in profile.employment_history:
            if 'duration' in job_exp:
                years = extract_years_from_experience(job_exp.get('duration', ''))
                if years:
                    total_years += years
        if total_years > 0:
            user_experience = f"{total_years} years"
    elif profile.is_fresher:
        user_experience = "Fresher (0 years)"
    
    # Calculate skill match
    matched_skills, missing_skills = calculate_skill_gap(job.skills or [], user_skills)
    
    # Calculate match score
    match_score = calculate_match_score(job.skills or [], user_skills)
    
    # Calculate experience gap
    experience_gap = calculate_experience_gap(job.experience_level, user_experience)
    
    return Response({
        'job_id': job.id,
        'job_title': job.title,
        'match_score': match_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'experience_gap': experience_gap,
        'user_skills': user_skills,
        'job_skills': job.skills or []
    })

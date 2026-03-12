from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def create_notification(user, title, message, notification_type, link=None):
    """
    Helper function to create a notification for a user.
    
    Args:
        user: User instance or user ID
        title: Notification title
        message: Notification message
        notification_type: Type of notification (application, status, message, job, interview, system)
        link: Optional link to redirect user
    
    Returns:
        Notification instance
    """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
    return notification


def notify_job_application(application):
    """Create notification when a job application is submitted"""
    job = application.job
    recruiter = job.recruiter
    
    create_notification(
        user=recruiter,
        title='New Job Application',
        message=f'{application.applicant.username} applied for {job.title}',
        notification_type='application',
        link=f'/recruiter/applicants/{job.id}/'
    )


def notify_application_status(application, old_status, new_status):
    """Create notification when application status changes"""
    applicant = application.applicant
    
    status_messages = {
        'shortlisted': 'Congratulations! You have been shortlisted',
        'rejected': 'Your application was not selected',
        'interview': 'You have been invited for an interview',
    }
    
    message = status_messages.get(new_status, f'Your application status changed to {new_status}')
    
    create_notification(
        user=applicant,
        title='Application Status Update',
        message=message,
        notification_type='status',
        link=f'/applications/{application.id}/'
    )


def notify_new_message(conversation, message):
    """Create notification when a new message is sent"""
    # Find the other participant
    for participant in conversation.participants.all():
        if participant.id != message.sender.id:
            create_notification(
                user=participant,
                title='New Message',
                message=f'{message.sender.username}: {message.content[:50]}...',
                notification_type='message',
                link=f'/chat/?conversation={conversation.id}'
            )
            break


def notify_job_posted(job):
    """Create notification when a new job is posted (for admin)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Notify all admins
    admins = User.objects.filter(role='admin')
    for admin in admins:
        create_notification(
            user=admin,
            title='New Job Posted',
            message=f'A new job "{job.title}" has been posted by {job.recruiter.company_name}',
            notification_type='job',
            link=f'/admin/jobs/'
        )


def notify_interview_scheduled(application, interview_details):
    """Create notification when an interview is scheduled"""
    applicant = application.applicant
    
    create_notification(
        user=applicant,
        title='Interview Scheduled',
        message=f'Your interview for {application.job.title} has been scheduled',
        notification_type='interview',
        link=f'/applications/{application.id}/'
    )

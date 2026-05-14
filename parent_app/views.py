"""
parent_app/views.py — مُحدَّث
"""
import logging
import os
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from learning.models import (
    Parent, Performancereport, Student,
    Learningsession, Attentionlog,
)
from accounts.models import Notification

logger = logging.getLogger(__name__)

_ALLOWED_AVATAR_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
_MAX_AVATAR_SIZE    = 2 * 1024 * 1024

_MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpg',
    b'\x89PNG':      'png',
    b'GIF8':         'gif',
    b'RIFF':         'webp',
}


def _verify_image(file_obj) -> bool:
    header = file_obj.read(12)
    file_obj.seek(0)
    for magic in _MAGIC_BYTES:
        if header.startswith(magic):
            return True
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return True
    return False


def _parent_required(view_func):
    from functools import wraps
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        role = getattr(request.user, 'userrole', None)
        if role not in ('Parent',) and not request.user.is_staff:
            messages.error(request, 'هذه الصفحة لأولياء الأمور فقط.')
            return redirect('accounts:login')
        parent = Parent.objects.filter(
            userid=request.user
        ).select_related('childid__userid').first()
        if not parent and not request.user.is_staff:
            messages.warning(request, 'يرجى إكمال بياناتك أولاً.')
            return redirect('accounts:complete_profile')
        request.parent_obj = parent
        return view_func(request, *args, **kwargs)
    return wrapper


@_parent_required
def parent_portal(request):
    parent = request.parent_obj
    reports, child, avg_score = [], None, 0

    if parent and parent.childid:
        child   = parent.childid
        reports = list(
            Performancereport.objects
            .filter(studentid=child)
            .select_related('lessonid__subjectid', 'lessonid__teacherid__userid')
            .order_by('-reportdate')
        )
        scores    = [r.testscore for r in reports if r.testscore is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # ── الإشعارات الجديدة لولي الأمر ────────────────────────────
    unread_notifications = []
    all_notifications    = []
    if child:
        all_notifications = list(
            Notification.objects
            .filter(
                recipient  = request.user,
                notif_type__in = [
                    'parent_lesson', 'parent_test', 'parent_result',
                    'parent_attention', 'parent_grade', 'schedule_update',
                ],
            )
            .order_by('-created_at')[:30]
        )
        unread_notifications = [n for n in all_notifications if not n.is_read]
        # تعليم كإشعارات مقروءة
        if unread_notifications:
            Notification.objects.filter(
                pk__in=[n.pk for n in unread_notifications]
            ).update(is_read=True)

    # ── تجميع تقارير المواد ──────────────────────────────────────
    subject_reports = []
    if reports:
        from collections import defaultdict
        subj_map = defaultdict(list)
        for r in reports:
            if r.lessonid and r.lessonid.subjectid:
                subj_map[r.lessonid.subjectid.subjectname].append(r)
        for subj_name, reps in subj_map.items():
            scores_list = [r.testscore for r in reps if r.testscore is not None]
            avg_g  = round(sum(scores_list) / len(scores_list), 1) if scores_list else 0
            subject_reports.append({
                'subject_name': subj_name,
                'completion':   min(100, len(reps) * 20),
                'grade':        f'{avg_g}%',
            })

    # ملاحظات المعلمين (إشعارات parent_grade + parent_attention)
    teacher_notes = [
        {
            'teacher_name': 'النظام',
            'date':         n.created_at.strftime('%Y-%m-%d'),
            'text':         n.body,
        }
        for n in all_notifications
        if n.notif_type in ('parent_attention', 'parent_grade')
    ][:5]

    return render(request, 'parent_app/parent_portal.html', {
        'parent':                parent,
        'child':                 child,
        'reports':               reports[:10],
        'avg_score':             avg_score,
        'subject_reports':       subject_reports,
        'all_notifications':     all_notifications,
        'unread_notifications':  unread_notifications,
        'unread_count':          len(unread_notifications),
        'teacher_notes':         teacher_notes,
    })


@_parent_required
def reports_dashboard(request):
    parent = request.parent_obj
    child = parent.childid

    sessions = (
        Learningsession.objects
        .filter(studentid=child)
        .select_related('lessonid')
        .order_by('-starttime')
    )

    timeline = []
    for session in sessions:
        if session.avgfocusscore is None:
            continue
        timeline.append({
            'date': session.starttime.strftime('%Y-%m-%d'),
            'score': float(session.avgfocusscore),
            'lesson': session.lessonid.lessontitle if session.lessonid else 'جلسة',
            'session_id': session.sessionid,
        })

    overall_focus = round(
        sum(item['score'] for item in timeline) / len(timeline), 1
    ) if timeline else 0.0

    distracted_logs = Attentionlog.objects.filter(
        sessionid__in=sessions, isdistracted=True
    )
    from collections import Counter
    hour_counts = Counter(log.logtime.hour for log in distracted_logs)
    top_times = [
        {'label': f'{hour:02d}:00', 'count': count}
        for hour, count in hour_counts.most_common(3)
    ]

    recent_scores = [item['score'] for item in timeline[:5]]
    previous_scores = [item['score'] for item in timeline[5:10]]
    if recent_scores and previous_scores:
        recent_avg = sum(recent_scores) / len(recent_scores)
        previous_avg = sum(previous_scores) / len(previous_scores)
        if recent_avg > previous_avg + 2:
            insight_text = 'تحسن ملحوظ في تركيز الطفل خلال الجلسات الأخيرة.'
        elif recent_avg < previous_avg - 2:
            insight_text = 'هناك تراجع طفيف في جودة التركيز؛ يُنصح بإراحة الطفل قليلاً قبل الجلسة القادمة.'
        else:
            insight_text = 'التركيز ثابت مع بعض التحسن المستمر؛ استمر في دعم الطفل بالبيئة الهادئة.'
    else:
        insight_text = 'نحتاج المزيد من الجلسات لعرض تحليل دقيق لتحسين التركيز.'

    return render(request, 'parent_app/reports_dashboard.html', {
        'parent':     parent,
        'child':      child,
        'timeline':   timeline,
        'overall_focus': overall_focus,
        'top_times':  top_times,
        'insight_text': insight_text,
        'recent_sessions': sessions[:5],
    })


@_parent_required
def child_report(request):
    parent = request.parent_obj
    child = parent.childid

    sessions = (
        Learningsession.objects
        .filter(studentid=child)
        .select_related('lessonid')
        .order_by('-starttime')
    )

    rows = []
    for session in sessions:
        logs = Attentionlog.objects.filter(sessionid=session)
        distracted = logs.filter(isdistracted=True).count()
        total = logs.count() or 1
        rows.append({
            'session': session,
            'lesson': session.lessonid.lessontitle if session.lessonid else 'جلسة',
            'avg_focus': float(session.avgfocusscore or 0),
            'distractions': distracted,
            'focus_rate': round((total - distracted) / total * 100, 1),
        })

    return render(request, 'parent_app/child_report.html', {
        'parent': parent,
        'child': child,
        'rows': rows,
    })


@_parent_required
def session_details(request, session_id):
    parent = request.parent_obj
    child = parent.childid

    session = get_object_or_404(
        Learningsession,
        sessionid=session_id,
        studentid=child,
    )
    logs = list(Attentionlog.objects.filter(sessionid=session).order_by('logtime'))
    timeline = []
    total = len(logs) or 1
    distracted = 0
    for log in logs:
        distracted = distracted + (1 if log.isdistracted else 0)
        timeline.append({
            'time': log.logtime.strftime('%H:%M:%S'),
            'score': float(log.focuspercentage),
            'status': log.isdistracted and log.actiontaken or 'focused',
        })

    focus_rate = round((total - distracted) / total * 100, 1)
    insight = 'تحسن جيد في التركيز' if focus_rate >= 70 else 'يحتاج الطفل انتباهاً إضافياً خلال الجلسات المقبلة.'
    if len(logs) >= 2:
        first_half = logs[:len(logs)//2]
        second_half = logs[len(logs)//2:]
        first_avg = sum([float(l.focuspercentage) for l in first_half]) / len(first_half)
        second_avg = sum([float(l.focuspercentage) for l in second_half]) / len(second_half)
        if second_avg > first_avg + 1:
            insight = 'التركيز تحسن في نهاية الجلسة مقارنة بالبداية.'
        elif second_avg < first_avg - 1:
            insight = 'لاحظنا انخفاضاً في التركيز مع تقدم الجلسة.'
        else:
            insight = 'تركيز الطفل ثابت طوال الجلسة.'

    return render(request, 'parent_app/session_details.html', {
        'parent': parent,
        'child': child,
        'session': session,
        'timeline': timeline,
        'focus_rate': focus_rate,
        'distracted_count': distracted,
        'insight': insight,
    })


@login_required
def parent_profile(request):
    parent = Parent.objects.filter(
        userid=request.user
    ).select_related('childid__userid', 'userid').first()
    child  = parent.childid if parent else None

    if request.method == 'POST':
        bio    = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', request.POST.get('bio', '')).strip()[:300]
        avatar = request.FILES.get('avatar')
        remove = request.POST.get('remove_avatar') == '1'
        errors = []

        if remove and not avatar:
            if request.user.avatar:
                request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.bio = bio
            request.user.save(update_fields=['avatar', 'bio'])
            messages.success(request, 'تمت إزالة الصورة وحفظ الملف الشخصي.')
            return redirect('parent:profile')

        if avatar:
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in _ALLOWED_AVATAR_EXT:
                errors.append('صيغة الصورة غير مدعومة.')
            elif avatar.size > _MAX_AVATAR_SIZE:
                errors.append('حجم الصورة يتجاوز 2MB.')
            elif not _verify_image(avatar):
                errors.append('الملف المرفوع ليس صورة صحيحة.')
            else:
                fname = f'avatars/parent_{request.user.pk}{ext}'
                fpath = os.path.join(settings.MEDIA_ROOT, fname)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                with open(fpath, 'wb') as dest:
                    for chunk in avatar.chunks():
                        dest.write(chunk)
                request.user.avatar = fname

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            request.user.bio = bio
            update_fields = ['bio']
            if avatar and not errors:
                update_fields.append('avatar')
            request.user.save(update_fields=update_fields)
            messages.success(request, 'تم حفظ الملف الشخصي.')
        return redirect('parent:profile')

    return render(request, 'parent_app/profile.html', {
        'parent': parent,
        'child':  child,
    })
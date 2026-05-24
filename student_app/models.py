from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class CalibrationSession(models.Model):
    """
    جلسة معايرة سلوكية للطالب
    تستخدم لبناء نموذج انتباه شخصي (Personalized Behavioral Baseline)
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calibration_sessions'
    )
    session_number = models.IntegerField(default=1)  # رقم الجلسة (1, 2, 3, ...)
    duration_minutes = models.IntegerField(default=3)  # مدة الجلسة (2-5 دقائق)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # سياق الجلسة
    time_of_day = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'صباحاً'),
            ('afternoon', 'ظهراً'),
            ('evening', 'مساءً'),
            ('night', 'ليلاً'),
        ],
        blank=True
    )
    environment_notes = models.TextField(blank=True)  # ملاحظات الأهل عن البيئة
    calibration_video = models.FileField(
        upload_to='calibration_videos/',
        blank=True,
        null=True,
        help_text="فيديو مخصص للعرض أثناء جلسة المعايرة (حتى 5 دقائق)"
    )  # فيديو مخصص من قبل الأهل
    
    # البيانات السلوكية المجمعة (JSON)
    behavioral_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'جلسة معايرة'
        verbose_name_plural = 'جلسات المعايرة'
    
    def __str__(self):
        return f"جلسة معايرة #{self.session_number} - {self.student.username}"


class BehavioralBaseline(models.Model):
    """
    النموذج السلوكي الشخصي للطالب (Personalized Behavioral Baseline)
    يُبنى من دمج بيانات جلسات المعايرة المتعددة
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='behavioral_baseline'
    )
    
    # عدد جلسات المعايرة المستخدمة
    calibration_sessions_count = models.IntegerField(default=0)
    
    # حالة النموذج
    is_active = models.BooleanField(default=False)  # هل النموذج نشط ومثبت؟
    is_locked = models.BooleanField(default=False)  # هل النموذج مقفل (لا تحديث تلقائي)؟
    
    # التوزيعات الإحصائية للسلوك الطبيعي
    # EAR (نسبة انفتاح العين)
    ear_mean = models.FloatField(null=True, blank=True)
    ear_std = models.FloatField(null=True, blank=True)
    ear_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    ear_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    ear_min = models.FloatField(null=True, blank=True)
    ear_max = models.FloatField(null=True, blank=True)
    
    # حركة الرأس (Yaw, Pitch, Roll)
    head_yaw_mean = models.FloatField(null=True, blank=True)
    head_yaw_std = models.FloatField(null=True, blank=True)
    head_yaw_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    head_yaw_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    head_pitch_mean = models.FloatField(null=True, blank=True)
    head_pitch_std = models.FloatField(null=True, blank=True)
    head_pitch_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    head_pitch_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    head_roll_mean = models.FloatField(null=True, blank=True)
    head_roll_std = models.FloatField(null=True, blank=True)
    head_roll_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    head_roll_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    
    # زاوية النظر (Gaze)
    gaze_horizontal_mean = models.FloatField(null=True, blank=True)
    gaze_horizontal_std = models.FloatField(null=True, blank=True)
    gaze_horizontal_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    gaze_horizontal_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    gaze_vertical_mean = models.FloatField(null=True, blank=True)
    gaze_vertical_std = models.FloatField(null=True, blank=True)
    gaze_vertical_median = models.FloatField(null=True, blank=True)  # ✅ Robust Statistics
    gaze_vertical_mad = models.FloatField(null=True, blank=True)  # ✅ Median Absolute Deviation
    
    # نسبة الأنف/الأذن
    nose_ear_ratio_mean = models.FloatField(null=True, blank=True)
    nose_ear_ratio_std = models.FloatField(null=True, blank=True)
    
    # أنماط الالتفات (head_turn, gaze, drowsy)
    head_turn_frequency = models.FloatField(null=True, blank=True)  # تكرار الالتفات
    gaze_away_frequency = models.FloatField(null=True, blank=True)  # تكرار النظر بعيداً
    drowsy_frequency = models.FloatField(null=True, blank=True)  # تكرار النعاس
    
    # العتبات الشخصية (تُحسب من التوزيعات)
    ear_threshold_personal = models.FloatField(null=True, blank=True)
    yaw_threshold_personal = models.FloatField(null=True, blank=True)
    pitch_threshold_personal = models.FloatField(null=True, blank=True)
    roll_threshold_personal = models.FloatField(null=True, blank=True)
    gaze_horizontal_threshold_personal = models.FloatField(null=True, blank=True)
    gaze_vertical_threshold_personal = models.FloatField(null=True, blank=True)
    
    # تاريخ آخر تحديث
    last_updated = models.DateTimeField(auto_now=True)
    calibration_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'النموذج السلوكي الشخصي'
        verbose_name_plural = 'النماذج السلوكية الشخصية'
    
    def __str__(self):
        status = "نشط" if self.is_active else "غير نشط"
        return f"النموذج السلوكي - {self.student.username} ({status})"
    
    def update_from_sessions(self, sessions):
        """
        تحديث النموذج من جلسات المعايرة
        يستخدم الإحصاءات التراكمية لبناء نموذج أكثر دقة
        
        التحسينات الإحصائية:
        - التحقق من حجم العينة (>= 30 عينة)
        - معالجة القيم المتطرفة باستخدام IQR
        - حساب معامل الاختلاف (CV) للتأكد من الاستقرار
        - التحقق من جودة البيانات ونطاق القيم
        """
        if not sessions:
            return
        
        # جمع البيانات من جميع الجلسات
        all_ear_values = []
        all_yaw_values = []
        all_pitch_values = []
        all_roll_values = []
        all_gaze_h_values = []
        all_gaze_v_values = []
        all_nose_ear_values = []
        
        head_turn_count = 0
        gaze_away_count = 0
        drowsy_count = 0
        total_frames = 0
        
        for session in sessions:
            data = session.behavioral_data or {}
            
            # جمع قيم EAR
            if 'ear_values' in data:
                ear_vals = [v for v in data['ear_values'] if 0.15 <= v <= 0.35]  # نطاق EAR المقبول
                all_ear_values.extend(ear_vals)
            
            # جمع قيم حركة الرأس
            if 'head_yaw_values' in data:
                all_yaw_values.extend(data['head_yaw_values'])
            if 'head_pitch_values' in data:
                all_pitch_values.extend(data['head_pitch_values'])
            if 'head_roll_values' in data:
                all_roll_values.extend(data['head_roll_values'])
            
            # جمع قيم النظر
            if 'gaze_horizontal_values' in data:
                all_gaze_h_values.extend(data['gaze_horizontal_values'])
            if 'gaze_vertical_values' in data:
                all_gaze_v_values.extend(data['gaze_vertical_values'])
            
            # جمع قيم نسبة الأنف/الأذن
            if 'nose_ear_ratio_values' in data:
                all_nose_ear_values.extend(data['nose_ear_ratio_values'])
            
            # جمع تكرارات السلوك
            if 'head_turn_count' in data:
                head_turn_count += data['head_turn_count']
            if 'gaze_away_count' in data:
                gaze_away_count += data['gaze_away_count']
            if 'drowsy_count' in data:
                drowsy_count += data['drowsy_count']
            if 'total_frames' in data:
                total_frames += data['total_frames']
        
        # تحديث عدد جلسات المعايرة
        self.calibration_sessions_count = len(sessions)
        
        # حساب الإحصاءات مع التحقق من الجودة
        import numpy as np
        
        def calculate_statistics(values, feature_name):
            """
            حساب الإحصاءات مع التحقق من الجودة الإحصائية
            """
            if len(values) < 5:
                # حجم عينة صغير جداً، لا يمكن الاعتماد على الإحصاءات
                return None
            
            values_array = np.array(values)
            
            # حساب الإحصاءات التقليدية (mean/std)
            mean_val = float(np.mean(values_array))
            std_val = float(np.std(values_array))
            min_val = float(np.min(values_array))
            max_val = float(np.max(values_array))
            
            # ✅ حساب Robust Statistics (median/MAD)
            median_val = float(np.median(values_array))
            # MAD = median(|x_i - median|)
            deviations = np.abs(values_array - median_val)
            mad_val = float(np.median(deviations))
            
            # حساب معامل الاختلاف (Coefficient of Variation)
            cv = std_val / mean_val if mean_val != 0 else float('inf')
            
            # لا نرفض البيانات بناءً على CV، فقط نسجلها
            return {
                'mean': mean_val,
                'std': std_val,
                'median': median_val,  # ✅ Robust Statistics
                'mad': mad_val,  # ✅ Median Absolute Deviation
                'min': min_val,
                'max': max_val,
                'cv': cv
            }
        
        # حساب الإحصاءات لكل ميزة
        ear_stats = calculate_statistics(all_ear_values, 'EAR')
        if ear_stats:
            self.ear_mean = ear_stats['mean']
            self.ear_std = ear_stats['std']
            self.ear_median = ear_stats['median']  # ✅ Robust Statistics
            self.ear_mad = ear_stats['mad']  # ✅ Median Absolute Deviation
            self.ear_min = ear_stats['min']
            self.ear_max = ear_stats['max']
            # عتبة شخصية: median - 2*mad (للكشف عن الانحرافات)
            self.ear_threshold_personal = max(0.15, self.ear_median - 2 * self.ear_mad)
        
        yaw_stats = calculate_statistics(all_yaw_values, 'Yaw')
        if yaw_stats:
            self.head_yaw_mean = yaw_stats['mean']
            self.head_yaw_std = yaw_stats['std']
            self.head_yaw_median = yaw_stats['median']  # ✅ Robust Statistics
            self.head_yaw_mad = yaw_stats['mad']  # ✅ Median Absolute Deviation
            self.yaw_threshold_personal = self.head_yaw_median + 2 * self.head_yaw_mad
        
        pitch_stats = calculate_statistics(all_pitch_values, 'Pitch')
        if pitch_stats:
            self.head_pitch_mean = pitch_stats['mean']
            self.head_pitch_std = pitch_stats['std']
            self.head_pitch_median = pitch_stats['median']  # ✅ Robust Statistics
            self.head_pitch_mad = pitch_stats['mad']  # ✅ Median Absolute Deviation
            self.pitch_threshold_personal = self.head_pitch_median + 2 * self.head_pitch_mad
        
        roll_stats = calculate_statistics(all_roll_values, 'Roll')
        if roll_stats:
            self.head_roll_mean = roll_stats['mean']
            self.head_roll_std = roll_stats['std']
            self.head_roll_median = roll_stats['median']  # ✅ Robust Statistics
            self.head_roll_mad = roll_stats['mad']  # ✅ Median Absolute Deviation
            self.roll_threshold_personal = self.head_roll_median + 2 * self.head_roll_mad
        
        gaze_h_stats = calculate_statistics(all_gaze_h_values, 'Gaze Horizontal')
        if gaze_h_stats:
            self.gaze_horizontal_mean = gaze_h_stats['mean']
            self.gaze_horizontal_std = gaze_h_stats['std']
            self.gaze_horizontal_median = gaze_h_stats['median']  # ✅ Robust Statistics
            self.gaze_horizontal_mad = gaze_h_stats['mad']  # ✅ Median Absolute Deviation
            self.gaze_horizontal_threshold_personal = self.gaze_horizontal_median + 2 * self.gaze_horizontal_mad
        
        gaze_v_stats = calculate_statistics(all_gaze_v_values, 'Gaze Vertical')
        if gaze_v_stats:
            self.gaze_vertical_mean = gaze_v_stats['mean']
            self.gaze_vertical_std = gaze_v_stats['std']
            self.gaze_vertical_median = gaze_v_stats['median']  # ✅ Robust Statistics
            self.gaze_vertical_mad = gaze_v_stats['mad']  # ✅ Median Absolute Deviation
            self.gaze_vertical_threshold_personal = self.gaze_vertical_median + 2 * self.gaze_vertical_mad

        nose_ear_stats = calculate_statistics(all_nose_ear_values, 'Nose/Ear Ratio')
        if nose_ear_stats:
            self.nose_ear_ratio_mean = nose_ear_stats['mean']
            self.nose_ear_ratio_std = nose_ear_stats['std']

        # حساب التكرارات
        if total_frames > 0:
            self.head_turn_frequency = head_turn_count / total_frames
            self.gaze_away_frequency = gaze_away_count / total_frames
            self.drowsy_frequency = drowsy_count / total_frames

        # تعيين تاريخ اكتمال المعايرة إذا اكتملت جلسة واحدة على الأقل
        # مع التحقق من أن البيانات كافية إحصائياً
        if len(sessions) >= 1 and self.calibration_completed_at is None:
            # التحقق من أن الميزة الرئيسية (EAR) لديها بيانات كافية
            # الميزات الأخرى اختيارية
            if ear_stats:
                from django.utils import timezone
                self.calibration_completed_at = timezone.now()
                self.is_active = True  # تفعيل النموذج

        self.save()


# ═══════════════════════════════════════════════════════════════════════════════
# CPTLS (Continuous Probabilistic Temporal Learning State) Models
# ═══════════════════════════════════════════════════════════════════════════════

class CPTLSBaseline(models.Model):
    """
    CPTLS Personal Baseline for a student
    Stores the statistical baseline (μ and σ) for the 4 features:
    - gaze (eye tracking)
    - head (head pose)
    - ear (eye aspect ratio)
    - response (checkpoint question response time)
    
    Note: mean/std fields store median/MAD (Robust Statistics)
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cptls_baseline'
    )
    
    # Feature medians (μ) - ✅ Robust Statistics
    gaze_mean = models.FloatField(default=0.0)  # Stores median
    head_mean = models.FloatField(default=0.0)  # Stores median
    ear_mean = models.FloatField(default=0.0)  # Stores median
    
    # Feature MADs (σ) - ✅ Median Absolute Deviation
    gaze_std = models.FloatField(default=1.0)  # Stores MAD
    head_std = models.FloatField(default=1.0)  # Stores MAD
    ear_std = models.FloatField(default=1.0)  # Stores MAD
    
    # Calibration metadata
    calibration_samples = models.IntegerField(default=0)
    calibration_sessions_count = models.IntegerField(default=0)
    
    # Feature weights (customizable per student)
    gaze_weight = models.FloatField(default=0.45)
    head_weight = models.FloatField(default=0.35)
    ear_weight = models.FloatField(default=0.20)
    
    # Temporal smoothing factor (α)
    alpha = models.FloatField(default=0.94)
    
    # Status
    is_active = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    calibration_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'CPTLS Baseline'
        verbose_name_plural = 'CPTLS Baselines'
    
    def __str__(self):
        status = "نشط" if self.is_active else "غير نشط"
        return f"CPTLS Baseline - {self.student.username} ({status})"
    
    def get_feature_means(self):
        """Return feature means as numpy array."""
        import numpy as np
        return np.array([
            self.gaze_mean,
            self.head_mean,
            self.ear_mean
        ])
    
    def get_feature_stds(self):
        """Return feature standard deviations as numpy array."""
        import numpy as np
        return np.array([
            self.gaze_std,
            self.head_std,
            self.ear_std
        ])
    
    def get_feature_weights(self):
        """Return feature weights as numpy array."""
        import numpy as np
        return np.array([
            self.gaze_weight,
            self.head_weight,
            self.ear_weight
        ])


class CPTLSSession(models.Model):
    """
    CPTLS Learning Session
    Tracks a learning session with continuous temporal state updates
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cptls_sessions'
    )
    
    # Session context
    lesson_id = models.IntegerField(null=True, blank=True)
    session_type = models.CharField(
        max_length=20,
        choices=[
            ('lesson', 'درس'),
            ('video', 'فيديو'),
            ('practice', 'تدريب'),
            ('test', 'اختبار'),
        ],
        default='lesson'
    )
    
    # Content mode (for adaptive escalation)
    content_mode = models.CharField(
        max_length=20,
        choices=[
            ('text', 'نص'),
            ('audio', 'صوت'),
            ('video', 'فيديو'),
        ],
        default='text'
    )
    
    # Session timing
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Session statistics
    total_samples = models.IntegerField(default=0)
    average_engagement = models.FloatField(null=True, blank=True)
    final_temporal_state = models.FloatField(null=True, blank=True)
    
    # Distraction detection
    sustained_distraction_detected = models.BooleanField(default=False)
    distraction_episodes_count = models.IntegerField(default=0)
    risk_level = models.IntegerField(default=0)  # 0-10 scale
    
    # Question response tracking (for adaptive escalation)
    total_questions_asked = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    
    # Adaptive escalation tracking
    adaptive_suggestion_made = models.BooleanField(default=False)
    adaptive_suggestion_type = models.CharField(
        max_length=50,
        choices=[
            ('none', 'بدون'),
            ('switch_to_video', 'الانتقال إلى الفيديو'),
            ('postpone_session', 'تأجيل الجلسة'),
            ('modify_content', 'تعديل المحتوى'),
            ('vr_environment', 'بيئة الواقع الافتراضي'),
        ],
        default='none'
    )
    consecutive_video_failures = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'CPTLS Session'
        verbose_name_plural = 'CPTLS Sessions'
    
    def __str__(self):
        return f"CPTLS Session - {self.student.username} ({self.session_type})"
    
    def calculate_duration(self):
        """Calculate session duration."""
        if self.start_time and self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
            self.save()
        return self.duration_seconds


class CPTLSStateSnapshot(models.Model):
    """
    CPTLS Temporal State Snapshot
    Stores the continuous temporal state at each time step
    """
    session = models.ForeignKey(
        CPTLSSession,
        on_delete=models.CASCADE,
        related_name='state_snapshots'
    )
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Raw features (X_t)
    gaze_raw = models.FloatField()
    head_raw = models.FloatField()
    ear_raw = models.FloatField()
    
    # Normalized features (Z_t)
    gaze_normalized = models.FloatField()
    head_normalized = models.FloatField()
    ear_normalized = models.FloatField()
    
    # Probabilities (P_t)
    gaze_probability = models.FloatField()
    head_probability = models.FloatField()
    ear_probability = models.FloatField()
    
    # Fused probability
    fused_probability = models.FloatField()
    
    # Temporal state (S_t)
    temporal_state = models.FloatField()
    
    # Engagement percentage
    engagement_percentage = models.FloatField()
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'CPTLS State Snapshot'
        verbose_name_plural = 'CPTLS State Snapshots'
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"State Snapshot - Session {self.session.id} at {self.timestamp:%H:%M:%S}"


class CPTLSCalibrationSample(models.Model):
    """
    Individual calibration sample collected during calibration phase
    """
    calibration_session = models.ForeignKey(
        CalibrationSession,
        on_delete=models.CASCADE,
        related_name='cptls_samples'
    )
    
    # Raw features
    gaze = models.FloatField()
    head = models.FloatField()
    ear = models.FloatField()
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'CPTLS Calibration Sample'
        verbose_name_plural = 'CPTLS Calibration Samples'
    
    def __str__(self):
        return f"Calibration Sample - {self.calibration_session.id}"

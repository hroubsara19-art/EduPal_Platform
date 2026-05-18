# Attention Tracking System - Implementation & Deployment Guide

**Last Updated**: May 18, 2026  
**System Status**: ✅ Core features validated, ready for ML integration  
**Deployment Target**: Django 5.2.9 with PostgreSQL  

---

## Quick Start for Developers

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Student Video Lesson Interface              │
│  (student_app/templates/student_app/lesson_video.html)│
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼──────────────────┐  ┌─────▼─────────────────┐
│  AttentionTracker    │  │  Web APIs Used        │
│  State Machine       │  │  • getUserMedia()     │
│                      │  │  • Web Speech API     │
│  - isTracking        │  │  • <video> events     │
│  - attentionState    │  │  • setTimeout()       │
│  - distractionTime   │  │  • Fetch API (future) │
│  - Alert flags       │  └───────────────────────┘
└──────────────────────┘

┌──────────────────────────────────────┐
│  Backend (Future Integration)        │
│  • AttentionLog model                │
│  • /api/log-attention-event/         │
│  • Teacher Analytics Dashboard       │
└──────────────────────────────────────┘
```

### Current Implementation Status

✅ **Frontend Complete**
- Attention state machine with 15 state variables
- Video lifecycle event handlers (play/pause/ended)
- Dual-tier alert system (3s text + 5s audio+pause)
- Pause/resume state coordination
- Web Speech API audio alerts

⏳ **Pending - ML Integration**
- Replace `simulateAttentionDetection()` with real model
- Two options:
  1. **TensorFlow.js + FaceMesh** (browser-based, real-time)
  2. **Backend API** (server-based, more accurate)

⏳ **Pending - TTS Integration**
- Move from Web Speech API to Azure Cognitive Services
- Fallback to Web Speech API if unavailable

---

## File Structure

```
adhd_learning_system/
├── student_app/
│   ├── templates/student_app/
│   │   └── lesson_video.html         ← Main implementation (596 lines)
│   │       ├── HTML structure
│   │       ├── AttentionTracker state machine
│   │       ├── Event handlers
│   │       └── UI components (alerts, overlay, buttons)
│   ├── urls.py                       ← Added dev_impersonate endpoint
│   ├── views.py                      ← Added dev_impersonate view
│   └── models.py
│
├── setup_test_student.py             ← Test infrastructure
├── create_test_user.py               ← User creation helper
├── manage.py
└── requirements.txt
```

---

## Key Components Explained

### 1. AttentionTracker State Machine

Located in [lesson_video.html (lines 308-329)](student_app/templates/student_app/lesson_video.html#L308-L329)

```javascript
const AttentionTracker = {
  // Core tracking state
  isEnabled: false,           // Manually enabled by user
  isTracking: false,          // Actively monitoring attention
  cameraActive: false,        // Camera permission granted
  videoPlaying: false,        // Video currently playing
  
  // Attention state
  attentionState: 'attentive',     // 'attentive' | 'distracted'
  distractionStartTime: null,       // When distraction began
  distractionDuration: 0,           // How long distracted
  
  // Alert state
  shortAlertShown: false,     // 3s alert shown
  longAlertActive: false,     // 5s alert + video pause active
  
  // Pause/resume coordination
  wasTrackingBeforePause: false,    // Flag to resume tracking
  
  // Infrastructure
  videoStream: null,          // Camera stream handle
  trackingCheckInterval: null,     // Monitor interval ID
  alertAudioPlaying: false,   // Audio synthesis in progress
  
  // Context
  studentName: 'Student',     // From Django template
  cameraPermissionAsked: false,    // Don't re-ask permission
  
  // Simulation (temporary)
  simulationStartTime: null,  // For mock attention detection
};
```

### 2. Configuration

Located in [lesson_video.html (lines 330-340)](student_app/templates/student_app/lesson_video.html#L330-L340)

```javascript
AttentionTracker.config = {
  shortDistraction: 3000,     // 3s before short alert
  longDistraction: 5000,      // 5s before long alert + pause
  attentionCheckRate: 500,    // Check attention every 500ms
  attentionConfirmDelay: 1000 // Wait 1s after focus returns before resume
};
```

**Tuning Guide**:
- Increase `shortDistraction` to reduce sensitivity
- Increase `longDistraction` to give more warning
- Decrease `attentionCheckRate` for more responsive detection (CPU cost)
- Decrease `attentionConfirmDelay` for faster resume

### 3. Event Lifecycle

```
┌─────────────┐
│ Video Plays │
└──────┬──────┘
       │
       ├─→ onVideoPlay()
       │   ├─→ Request camera permission (first time only)
       │   ├─→ Start attention monitoring
       │   └─→ If wasTrackingBeforePause=true, resume tracking
       │
       ├─→ If camera granted:
       │   ├─→ startAttentionMonitoring()
       │   └─→ Poll every 500ms via simulateAttentionDetection()
       │
       └─→ Monitor for distraction...
           ├─→ 3s distracted → showShortAlert()
           └─→ 5s distracted → pauseVideo() + showLongAlert() + playAudioAlert()

┌──────────────┐
│ Video Paused │
└──────┬───────┘
       │
       ├─→ onVideoPause()
       │   ├─→ Set wasTrackingBeforePause=true (save state)
       │   ├─→ isTracking=false (stop monitoring)
       │   ├─→ stopAttentionMonitoring() (clear interval)
       │   └─→ clearAlerts() (dismiss any active alerts)
       │
       └─→ All state preserved for resume

┌──────────────┐
│ Video Play   │ (Resume from pause)
└──────┬───────┘
       │
       ├─→ onVideoPlay()
       │   └─→ Check wasTrackingBeforePause flag
       │       ├─→ If true: resume tracking (set isTracking=true)
       │       └─→ resetDistractionState() (clean slate)
       │
       └─→ Tracking continues from pause point
```

### 4. Attention Detection (Current: Simulation)

Located in [lesson_video.html (lines 521-540)](student_app/templates/student_app/lesson_video.html#L521-L540)

**Current Implementation** (Simulation):
```javascript
simulateAttentionDetection: function() {
  // Fake pattern: 8s attentive → 3s distracted (repeating)
  const elapsed = (Date.now() - this.simulationStartTime) % 11000;
  return elapsed < 8000 ? 'attentive' : 'distracted';
}
```

**To Replace With Real ML**:
```javascript
simulateAttentionDetection: function() {
  // Option 1: TensorFlow.js in browser
  // return await this.detectFaceAttention(); // Returns 'attentive'|'distracted'
  
  // Option 2: Backend API call
  // const response = await fetch('/api/detect-attention/', {
  //   method: 'POST',
  //   body: JSON.stringify({ frame: videoFrame })
  // });
  // return response.ok ? response.data.state : 'attentive';
}
```

**Required Interface**:
- Input: Current video frame (from `<video>` element)
- Output: String ('attentive' or 'distracted')
- Latency: <100ms preferred for real-time response

### 5. Alert System

#### Short Alert (3 seconds)
Located in [lesson_video.html (lines 596-640)](student_app/templates/student_app/lesson_video.html#L596-L640)

```javascript
showShortAlert: function() {
  // Appears after 3s of distraction
  // Messages: 3 randomized Arabic options
  // - "{{name}}، تابع معنا!" (Follow with us!)
  // - "{{name}}، التركيز قليلاً" (Focus a bit)
  // - "{{name}}، عودة للفيديو" (Back to video)
  
  // UI: 💡 icon, 2s duration, no video pause
  // Then disappears automatically
}
```

#### Long Alert (5+ seconds)
Located in [lesson_video.html (lines 642-710)](student_app/templates/student_app/lesson_video.html#L642-L710)

```javascript
showLongAlert: function() {
  // Appears after 5s of sustained distraction
  // Video automatically paused
  // 🔴 icon appears with message
  // Audio alert plays via Web Speech API
  // Alert stays until focus returns + 1s
  
  // Messages: 3 randomized with student name
  // Audio: Arabic TTS at pitch=1.1, volume=0.8
  
  // Mutes video during speech, unmutes after
}
```

---

## Integration Points for ML

### Option 1: TensorFlow.js + FaceMesh (Recommended)

**Pros**:
- Real-time, browser-based
- No server calls needed
- Works offline
- Privacy-preserving (no faces sent to server)

**Cons**:
- Higher CPU usage
- Requires good lighting for face detection
- Limited accuracy without training

**Implementation**:
```javascript
// 1. Load model
await Promise.all([
  tf.loadLayersModel(...),
  facemesh.load()
]);

// 2. In attention monitoring loop:
const predictions = await facemesh.estimateFaces(videoElement);
const eyeOpen = predictions[0].landmarks[159][2] > 0.5; // Z-axis confidence
return eyeOpen ? 'attentive' : 'distracted';
```

**Integration Point**: Replace `simulateAttentionDetection()` in [line 533](student_app/templates/student_app/lesson_video.html#L533)

### Option 2: Backend API (Azure Cognitive Services)

**Pros**:
- More accurate
- Works in low light
- Centralized logging
- Can track trends server-side

**Cons**:
- Requires server calls (latency)
- Privacy: frames sent to server
- Cost: API charges

**Implementation**:
```javascript
// In attention monitoring loop:
const frame = await this.captureVideoFrame();
const response = await fetch('/api/detect-attention/', {
  method: 'POST',
  body: JSON.stringify({ frame: frame }),
  headers: { 'X-CSRFToken': getCsrfToken() }
});
const data = await response.json();
return data.attentionState; // 'attentive' | 'distracted'
```

**Backend Endpoint** (to create):
```python
# student_app/views.py
@require_http_methods(["POST"])
def detect_attention_api(request):
    frame_data = json.loads(request.body).get('frame')
    
    # Call Azure Cognitive Services or ML model
    attention_state = detect_attention_from_frame(frame_data)
    
    return JsonResponse({
        'attentionState': attention_state,  # 'attentive' | 'distracted'
        'confidence': 0.95
    })
```

---

## Deployment Checklist

### Pre-Production (Before Alpha)

- [ ] ML algorithm integrated and tested
- [ ] TTS service upgraded from Web Speech API
- [ ] Console.logs removed or moved to DEBUG conditional
- [ ] Error handling reviewed for edge cases
- [ ] Camera permission UI improved with explanations
- [ ] Configuration values tuned based on feedback

### Production (Before Release)

- [ ] Backend logging system created (`AttentionLog` model)
- [ ] Analytics dashboard implemented
- [ ] Teacher documentation written
- [ ] Student documentation written
- [ ] Parent notification system integrated
- [ ] GDPR compliance reviewed (camera usage)
- [ ] Performance testing with 100+ concurrent students
- [ ] Accessibility testing (WCAG 2.1 AA)
- [ ] Load testing on database

### Security Considerations

- [ ] Camera stream never stored (real-time processing only)
- [ ] Attention events logged with student anonymization option
- [ ] HTTPS enforced for camera access
- [ ] CSRF tokens on API endpoints
- [ ] Rate limiting on detection API
- [ ] Storage retention policy (auto-delete after 90 days)

---

## Testing Guide

### Unit Tests (JavaScript)

```javascript
// Test pause/resume state persistence
test('wasTrackingBeforePause preserves tracking state', () => {
  AttentionTracker.isTracking = true;
  AttentionTracker.onVideoPause();
  expect(AttentionTracker.wasTrackingBeforePause).toBe(true);
  
  AttentionTracker.videoPlaying = true;
  AttentionTracker.onVideoPlay();
  expect(AttentionTracker.isTracking).toBe(true);
  expect(AttentionTracker.wasTrackingBeforePause).toBe(false);
});

// Test alert timing
test('short alert appears at 3 seconds', () => {
  AttentionTracker.attentionState = 'distracted';
  AttentionTracker.distractionStartTime = Date.now() - 3500;
  AttentionTracker.updateDistraction();
  expect(AttentionTracker.shortAlertShown).toBe(true);
});
```

### Integration Tests (Django + Playwright)

```javascript
// Test full flow
test('complete attention tracking flow', async () => {
  // 1. Load lesson page
  await page.goto('/lesson/video/167/');
  
  // 2. Simulate play
  await page.click('.video-player');
  await page.waitForFunction(() => window.AttentionTracker.isTracking);
  
  // 3. Simulate distraction
  await page.evaluate(() => {
    AttentionTracker.attentionState = 'distracted';
    AttentionTracker.distractionStartTime = Date.now() - 5500;
  });
  
  // 4. Verify alert appears
  const alert = await page.waitForSelector('.attention-alert');
  expect(alert).toBeTruthy();
});
```

### Manual Testing Script

**Test Environment Setup**:
```bash
# 1. Start Django server
python manage.py runserver 0.0.0.0:8001

# 2. Login as test student
# URL: http://localhost:8001/dev/impersonate/teststudent/167/

# 3. Open Developer Tools (F12)
# 4. Go to Console tab
# 5. Run test commands:

AttentionTracker.init();
// See: "AttentionTracker initialized"

// Test pause/resume
video.play();
// Wait for camera permission dialog
video.pause();
// Verify: wasTrackingBeforePause = true
video.play();
// Verify: tracking resumed, wasTrackingBeforePause = false
```

---

## Troubleshooting

### Issue: "Camera permission denied"
**Cause**: Browser policy or user refused  
**Solution**: Application gracefully continues without camera (no video pause feature, but continues tracking)  
**Check**: `cameraActive` should be false, `isTracking` should be false

### Issue: "AttentionTracker not defined"
**Cause**: Page.evaluate() context issue or script not loaded  
**Solution**: Call `AttentionTracker.init()` manually in console  
**Prevention**: Add error handling in template script load

### Issue: "Audio alert doesn't play"
**Cause**: Browser Speech API unsupported or no speaker output  
**Solution**: Upgrade to Azure TTS service  
**Fallback**: Continue without audio, visual alert still works

### Issue: "Video keeps pausing unexpectedly"
**Cause**: False distraction detections (incorrect ML model)  
**Solution**: Retrain or recalibrate attention detection algorithm  
**Workaround**: Increase `longDistraction` threshold temporarily

---

## Performance Monitoring

### Metrics to Track

1. **Attention Detection Latency**
   - Target: <100ms per detection
   - Monitor: `Date.now() - detectionStartTime`

2. **CPU Usage**
   - Target: <5% per student during tracking
   - Monitor: Browser DevTools Performance tab

3. **False Positive Rate**
   - Target: <10% of distractions are false
   - Monitor: Teacher analytics dashboard

4. **Camera Permission Success Rate**
   - Target: >90% of students grant permission
   - Monitor: Logging system

5. **Audio Alert Completion Time**
   - Target: <2s for full message playback
   - Monitor: Timing in browser logs

---

## References

- [lesson_video.html - Full Implementation](student_app/templates/student_app/lesson_video.html)
- [ATTENTION_TRACKING_VALIDATION_REPORT.md - Test Results](ATTENTION_TRACKING_VALIDATION_REPORT.md)
- [Attention Tracking Auto-Activation Update](ATTENTION_TRACKING_AUTO_ACTIVATION_UPDATE.md)

---

## Support & Questions

For implementation questions or issues:
1. Check the troubleshooting section above
2. Review browser console logs (`[AttentionTracker]` prefix)
3. Consult [ATTENTION_TRACKING_VALIDATION_REPORT.md](ATTENTION_TRACKING_VALIDATION_REPORT.md) for known limitations
4. Test with developer console: `AttentionTracker` object inspection

**Next Step**: Integrate ML algorithm and schedule alpha testing with real students.

---

**Last Updated**: May 18, 2026  
**System Status**: ✅ Ready for ML integration and alpha testing

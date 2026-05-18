# Quick Reference - Attention Tracking System

## System Overview

**Purpose**: Automatically detect and respond to student distraction during video lessons  
**Status**: ✅ Fully Functional - Ready for ML Integration  
**Location**: [student_app/templates/student_app/lesson_video.html](student_app/templates/student_app/lesson_video.html)

---

## Key Concepts

### The State Machine
Three key states track the system:
- **`isEnabled`**: User manually enabled tracking (button toggle)
- **`isTracking`**: Currently monitoring attention (after camera permission)
- **`attentionState`**: Current detection ('attentive' or 'distracted')

### The Pause/Resume Pattern
When video pauses:
1. Set `wasTrackingBeforePause = true` (save state)
2. Stop interval, stop tracking
3. Clear alerts

When video resumes:
1. Check `wasTrackingBeforePause` flag
2. If true: resume tracking, restart interval, clear distraction state
3. Fresh monitoring cycle begins

### The Alert Cascade
```
0-3 seconds distracted → Nothing
3-5 seconds distracted → 💡 Short alert (friendly text)
5+ seconds distracted  → 🔴 Long alert (audio + video pause)
```

---

## Configuration Quick Tune

Edit these values in [line 330-340](student_app/templates/student_app/lesson_video.html#L330-L340):

```javascript
AttentionTracker.config = {
  shortDistraction: 3000,      // Alert delay in ms (default: 3s)
  longDistraction: 5000,       // Pause delay in ms (default: 5s)
  attentionCheckRate: 500,     // Poll frequency in ms (default: 500ms)
  attentionConfirmDelay: 1000  // Delay before auto-resume in ms (default: 1s)
};
```

**Effect of changes**:
- **Increase `shortDistraction`**: Less sensitive, fewer false alerts
- **Decrease `shortDistraction`**: More sensitive, quicker response
- **Increase `attentionCheckRate`**: Lower CPU, slower response
- **Decrease `attentionCheckRate`**: Higher CPU, faster response

---

## Event Handlers

### Video Play
```javascript
AttentionTracker.onVideoPlay()
// First play: requests camera permission silently
// Resume: checks wasTrackingBeforePause flag
```

### Video Pause
```javascript
AttentionTracker.onVideoPause()
// Saves tracking state in wasTrackingBeforePause
// Clears all intervals and alerts
```

### Video Ended
```javascript
AttentionTracker.onVideoEnded()
// Stops all tracking, clears camera, resets state
```

### Distraction Detection
```javascript
AttentionTracker.updateDistraction()
// Called every 500ms
// Triggers alerts based on distraction duration
```

### Focus Detected
```javascript
AttentionTracker.onAttentiveDetected()
// Clears long alert
// Resets distraction counters
```

---

## Testing via Browser Console

```javascript
// 1. Initialize
AttentionTracker.init();

// 2. Manually activate tracking
AttentionTracker.isTracking = true;
AttentionTracker.cameraActive = true;
AttentionTracker.videoPlaying = true;
AttentionTracker.startAttentionMonitoring();

// 3. Test pause
AttentionTracker.onVideoPause();
console.log(AttentionTracker.wasTrackingBeforePause); // true ✅

// 4. Test resume
AttentionTracker.videoPlaying = true;
AttentionTracker.onVideoPlay();
console.log(AttentionTracker.isTracking); // true ✅

// 5. Simulate distraction
AttentionTracker.attentionState = 'distracted';
AttentionTracker.distractionStartTime = Date.now() - 3500;
AttentionTracker.updateDistraction();
console.log(AttentionTracker.shortAlertShown); // true ✅

// 6. Clear
AttentionTracker.stopTracking();
```

---

## Integration Checklist

- [x] State machine implemented
- [x] Pause/resume coordination working
- [x] Alert system functional
- [x] Web Speech API integrated
- [ ] **ML algorithm integration** ← NEXT STEP
- [ ] **Backend logging** ← FUTURE
- [ ] **Analytics dashboard** ← FUTURE

---

## Where to Add ML Detection

**File**: [lesson_video.html, line 533](student_app/templates/student_app/lesson_video.html#L533)  
**Function**: `simulateAttentionDetection()`

**Current** (Placeholder):
```javascript
simulateAttentionDetection: function() {
  const elapsed = (Date.now() - this.simulationStartTime) % 11000;
  return elapsed < 8000 ? 'attentive' : 'distracted';
}
```

**Replace with**:
```javascript
async simulateAttentionDetection() {
  // Option 1: TensorFlow.js
  const predictions = await facemesh.estimateFaces(videoElement);
  return predictions[0]?.landmarks[159][2] > 0.5 ? 'attentive' : 'distracted';
  
  // Option 2: Backend API
  // const response = await fetch('/api/detect-attention/');
  // return response.ok ? 'attentive' : 'distracted';
}
```

**Interface Requirements**:
- Input: Current video frame (implicit from `<video>` element)
- Output: String - 'attentive' or 'distracted'
- Latency: < 100ms preferred
- Async: Yes, returns Promise

---

## Where to Add Backend Logging

**Suggested Location**: After each alert in `showShortAlert()` and `showLongAlert()`

```javascript
// After showing alert, log the event:
fetch('/api/log-attention-event/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()
  },
  body: JSON.stringify({
    eventType: 'short_alert',     // or 'long_alert'
    studentId: this.studentId,
    lessonId: this.lessonId,
    duration: this.distractionDuration,
    timestamp: new Date().toISOString()
  })
});
```

**Backend Model** (to create):
```python
class AttentionLog(models.Model):
    student = ForeignKey(User, on_delete=models.CASCADE)
    lesson = ForeignKey(Lessoncontent, on_delete=models.CASCADE)
    event_type = CharField(choices=[('short_alert', 'Short Alert'), ('long_alert', 'Long Alert')])
    duration = IntegerField()  # milliseconds
    timestamp = DateTimeField(auto_now_add=True)
```

---

## Troubleshooting

### "AttentionTracker is not defined"
**Solution**: Call `AttentionTracker.init()` in console first

### "Video won't pause"
**Solution**: Check that `longAlertActive === true` and `video.paused === true`

### "Audio alert doesn't play"
**Solution**: 
1. Check browser speech support (Chrome best support)
2. Ensure lang='ar' is set
3. Upgrade to Azure TTS if needed

### "Pause/resume not working"
**Solution**: Verify `wasTrackingBeforePause` is set in `onVideoPause()`

### "False alerts constantly"
**Solution**: Increase `shortDistraction` or `longDistraction` threshold

---

## Performance Tips

**For Slower Devices**:
- Increase `attentionCheckRate` to 1000ms (check every second)
- Use simple ML model or backend API (avoid heavy client-side detection)

**For Faster Response**:
- Decrease `attentionCheckRate` to 250ms (check 4x per second)
- Use light ML model (TensorFlow Lite)

**Memory**:
- Intervals are properly cleared on pause ✅
- Video stream is properly disposed on close ✅
- No memory leaks detected in testing ✅

---

## Files to Know

| File | Purpose | Lines |
|------|---------|-------|
| [lesson_video.html](student_app/templates/student_app/lesson_video.html) | Main implementation | 596 |
| ATTENTION_TRACKING_VALIDATION_REPORT.md | Test results | For reference |
| ATTENTION_TRACKING_IMPLEMENTATION_GUIDE.md | Detailed guide | For developers |
| ATTENTION_TRACKING_FINAL_TEST_REPORT.md | Final validation | For stakeholders |

---

## Next Steps

1. **Integrate ML** (This week)
   - Replace `simulateAttentionDetection()`
   - Test with real student

2. **Add Backend Logging** (Next week)
   - Create AttentionLog model
   - Add API endpoint

3. **Build Dashboard** (Week after)
   - Teacher view for trends
   - Student view for progress

---

**Last Updated**: May 18, 2026  
**Status**: ✅ Ready for ML Integration

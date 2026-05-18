# 📊 Attention Tracking System - Visual Architecture Guide

**Date**: May 18, 2026  
**Status**: ✅ Complete with all diagrams  

---

## System Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    STUDENT VIDEO LESSON PAGE                   │
│              (student_app/templates/lesson_video.html)          │
└────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
    ┌───────────▼──────┐  ┌──▼──────────┐ ┌─▼──────────────┐
    │  HTML5 Video     │  │AttentionUI  │ │ AttentionTracker
    │  Element         │  │Components   │ │ State Machine
    │ • Controls       │  │ • Overlay   │ │ • Core Logic
    │ • Src URL        │  │ • Alerts    │ │ • Event Handlers
    │ • Autoplay       │  │ • Status    │ │ • Monitoring
    └────────┬─────────┘  │ • Button    │ └────────┬────────┘
             │            └─────────────┘          │
             │                                      │
             └──────────────┬───────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐      ┌───────▼─────┐     ┌──────▼──┐
    │Web APIs │      │Event System │     │ Timer   │
    │         │      │             │     │ System  │
    │ • getUser     │ • onVideoPlay     │ • 500ms │
    │   Media()     │ • onVideoPause    │ • checks
    │ • Web Speech  │ • onVideoEnded    │
    │   API (TTS)   │ • Events from     │
    │ • <video>     │   AttentionTracker
    │   element     └─────────────────┘
    │   events      
    └─────────────┘
```

---

## State Machine Diagram

```
                        ┌─────────────────┐
                        │  INITIALIZED    │
                        │ isTracking: F   │
                        │ isEnabled: F    │
                        │ cameraActive: F │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │ Video Play Event        │
                    └────────────┼────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │ Request Camera Permission│
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │ Permission Granted?      │
                    └────┬──────────────────┬──┘
                         │Yes               │No
                    ┌────▼──────────┐   ┌──▼────────────┐
                    │ CAMERA_ACTIVE │   │CONTINUE (no   │
                    │ isTracking: T │   │camera)        │
                    │ isEnabled: T  │   └───────────────┘
                    │ cameraActive: T
                    └────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐  ┌───────▼─────────┐ ┌──▼──────────┐
    │ PLAYING │  │ VIDEO PAUSED BY │ │VIDEO ENDED │
    │Monitoring   │USER             │ │            │
    │distraction  │wasTracking      │ │Disable all │
    │isTracking:T │BeforePause: T   │ │isTracking:F
    │Check every  │isTracking: F    │ │            │
    │500ms        │Stop interval    │ │Clean up    │
    └────┬────────┘└────┬───────────┘ └────────────┘
         │               │
    ┌────▼────────────────▼──┐
    │ VIDEO RESUME           │
    │ wasTracking            │
    │ BeforePause: true?     │
    └────┬─────────┬─────────┘
         │Yes      │No
    ┌────▼──┐  ┌───▼────┐
    │RESUME │  │NO-OP   │
    │Tracking   │Resume  │
    │Now        │tracking
    │isTracking:T
    └──────┘  └────────┘
```

---

## Event Flow Diagram

```
╔═════════════════════════════════════════════════════════════════╗
║                    STUDENT WATCHES VIDEO                        ║
╚════════════════════╤════════════════════════════════════════════╝
                     │
                     ▼
        ┌──────────────────────────┐
        │  Click Play / autoplay   │
        └─────────────┬────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │ AttentionTracker         │
        │ .onVideoPlay() handler   │
        └─────────────┬────────────┘
                      │
        ┌─────────────▼─────────────┐
        │ Request Camera Permission │
        │ (first time only)         │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼──────────────────┐
        │ User grants permission or      │
        │ denies (continue anyway)       │
        └─────────────┬──────────────────┘
                      │
        ┌─────────────▼────────────────┐
        │ startAttentionMonitoring()   │
        │ Start 500ms check interval   │
        └─────────────┬────────────────┘
                      │
                      ▼
        ┌────────────────────────────┐
        │ MONITORING LOOP (500ms)    │
        │                            │
        │ Check: simulateAttention   │
        │ Detection()                │
        │ State: 'attentive' or      │
        │        'distracted'        │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────┐
        │ Distraction Duration   │
        │ Tracking              │
        └──┬───────────┬────────┬─┘
           │           │        │
        3s │        5s │      8s│
           ▼           ▼        ▼
      ┌────────┐  ┌──────┐  ┌─────┐
      │SHORT   │  │LONG  │  │VERY │
      │ALERT   │  │ALERT │  │LONG │
      │💡Text  │  │🔴Audio  │ALERT │
      │No pause│  │Pause    │Keep  │
      │2s show │  │video    │paused│
      │        │  │3s show  │      │
      └─────┬──┘  └───┬────┘  └──┬──┘
            │         │          │
            ▼         ▼          ▼
        ┌─────────────────────────────┐
        │ User Focuses (attention     │
        │ detected)                   │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ onAttentiveDetected()       │
        │ Clear alerts                │
        │ Wait 1s confirmation        │
        │ Reset distraction counters  │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ Resume monitoring           │
        │ Fresh distraction cycle     │
        └──────────────┬──────────────┘
                       │
                   [loop back to monitoring loop]
                       │
        When student pauses video:
                       │
        ┌──────────────▼──────────────┐
        │ onVideoPause() handler      │
        │ Set wasTracking             │
        │ BeforePause = true          │
        │ Stop interval               │
        │ Clear alerts                │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ State SAVED (ready for      │
        │ resume)                     │
        └──────────────┬──────────────┘
                       │
        When student resumes:
                       │
        ┌──────────────▼──────────────┐
        │ onVideoPlay() handler       │
        │ Check wasTracking           │
        │ BeforePause = true?         │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ YES: Resume tracking        │
        │ Reset distraction state     │
        │ Start new monitoring cycle  │
        └──────────────┬──────────────┘
                       │
                   [loop back to monitoring loop]
```

---

## Pause/Resume State Diagram

```
┌────────────────────────────────────────────────────────────────┐
│              PAUSE/RESUME STATE COORDINATION                   │
└────────────────────────────────────────────────────────────────┘

SCENARIO: Video playing with tracking active

STATE 1: PLAYING & TRACKING
┌──────────────────────────────┐
│ isTracking: true             │
│ videoPlaying: true           │
│ wasTrackingBeforePause: false│
│ trackingCheckInterval: [ID]  │
│ (Actively monitoring)        │
└──────────────────────────────┘
         │
         │ User clicks Pause
         ▼
STATE 2: PAUSED & PAUSED (First pause)
┌──────────────────────────────┐
│ onVideoPause() called        │
│ ✓ Set wasTracking            │
│   BeforePause = true         │
│ ✓ isTracking = false         │
│ ✓ videoPlaying = false       │
│ ✓ Clear interval             │
│ ✓ Clear alerts               │
└──────────────────────────────┘
         │
         │ User clicks Resume
         ▼
STATE 3: PLAYING & RESUMED
┌──────────────────────────────┐
│ onVideoPlay() called         │
│ Check: wasTracking           │
│ BeforePause = true?          │
│ YES! →                       │
│ ✓ wasTracking               │
│   BeforePause = false        │
│ ✓ isTracking = true          │
│ ✓ videoPlaying = true        │
│ ✓ Restart interval           │
│ ✓ Reset distraction state    │
│ (Fresh monitoring cycle)     │
└──────────────────────────────┘
         │
   [Resume monitoring]

MULTIPLE PAUSE/RESUME CYCLES:
┌──────────────────────────────┐
│ Pause #1 → Resume #1 → OK    │
│ Pause #2 → Resume #2 → OK    │
│ Pause #3 → Resume #3 → OK    │
│ (State preserved each time)  │
└──────────────────────────────┘
```

---

## Alert Timing Diagram

```
┌────────────────────────────────────────────────────────────────┐
│              DISTRACTION ALERT TIMING CASCADE                  │
└────────────────────────────────────────────────────────────────┘

TIME AXIS:
│
0s  Video starts, student focused (attentive)
│   ✓ isTracking = true
│   ✓ attentionState = 'attentive'
│   ✓ Monitoring active (500ms checks)
│
────────────────────────────────────────────
│
2s  Student looks away (distracted)
│   ⚠ attentionState = 'distracted'
│   ⚠ distractionStartTime = now
│   → Monitoring continues, counter starts
│
────────────────────────────────────────────
│
3s  (3000ms elapsed) SHORT ALERT TRIGGERS
│   💡 showShortAlert()
│   💡 Message: 3 random Arabic options
│   💡 Display: 2 seconds
│   ✓ Video: CONTINUES PLAYING
│   ✓ shortAlertShown = true
│   ✓ longAlertActive = still false
│
────────────────────────────────────────────
│
3.5s Alert display phase
│   (Alert shown for 2 seconds)
│
────────────────────────────────────────────
│
5.2s  (Alert auto-dismisses, monitoring continues)
│     Student STILL distracted
│
────────────────────────────────────────────
│
5s  (5000ms elapsed) LONG ALERT TRIGGERS
│   🔴 showLongAlert()
│   🔴 Message: 3 random Arabic options + name
│   🔴 Display: 3+ seconds
│   ⏸️ Video: AUTO-PAUSES
│   🔊 Audio: Speech synthesis starts
│   🔊 Volume: Video muted (0%)
│   🔊 Audio pitch: 1.1
│   🔊 Duration: ~2 seconds for message
│   ✓ longAlertActive = true
│
────────────────────────────────────────────
│
5.5s  Audio synthesis completes
│      🔊 Video volume restored (100%)
│      ✓ Still paused (waiting for focus)
│
────────────────────────────────────────────
│
6s  Student refocuses on video
│    ✓ attentionState = 'attentive' (detected)
│    → onAttentiveDetected() called
│    → Clear longAlertActive
│
────────────────────────────────────────────
│
7s  (1 second confirmation delay passes)
│    → Video auto-resumes play
│    → Fresh monitoring cycle begins
│    → All distraction counters reset
│    → Ready for next distraction cycle
│
────────────────────────────────────────────

KEY INSIGHT:
- 0-3s: Student might naturally refocus ✓
- 3-5s: Getting serious with friendly alert ✓
- 5s+: Force attention with video pause ✓
- 1s delay: Ensure focus confirmed ✓
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: Video Element + Student Context + Browser APIs       │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐    ┌──────▼──────┐   ┌────▼────┐
    │ Camera │    │ Web Speech  │   │ Video   │
    │Permission    │ API        │   │Element  │
    │Status  │    │ (TTS)       │   │Events   │
    └───┬────┘    └──────┬──────┘   └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                ┌────────▼─────────┐
                │AttentionTracker  │
                │  State Machine   │
                └────────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────────────┐ ┌─▼──────────┐ ┌──▼──────┐
    │ Monitoring     │ │ Alert      │ │ UI      │
    │ Loop           │ │ System     │ │ Updates │
    │ (500ms)        │ │            │ │         │
    │                │ │ • Short    │ │ • Modal │
    │ Check:         │ │ • Long     │ │ • Overlay
    │ • Distraction  │ │ • Audio    │ │ • Button
    │ • Duration     │ │            │ │ • Status
    │ • Attention    │ └──┬─────────┘ └────┬────┘
    └────┬───────────┘    │               │
         │                └───────┬───────┘
         │                        │
         └────────────┬───────────┘
                      │
                ┌─────▼──────────┐
                │ OUTPUT:        │
                │ • Video paused │
                │ • Audio played │
                │ • Alerts shown │
                │ • Tracking log │
                │ (future: API)  │
                └────────────────┘
```

---

## ML Integration Points

```
CURRENT (Simulation):
┌─────────────────────────────────────┐
│ simulateAttentionDetection()         │
│ Returns: 'attentive' | 'distracted' │
│ Pattern: 8s attentive → 3s distracted
│ (Placeholder for testing)           │
└─────────────────────────────────────┘

OPTION 1: TensorFlow.js (Browser-based)
┌──────────────────────────────────┐
│ .detectFaceAttention()            │
│                                  │
│ • Load FaceMesh model            │
│ • Analyze face landmarks         │
│ • Check eye openness             │
│ • Return attention state         │
│ • Real-time, local processing    │
│ • Privacy-preserving (no upload) │
└──────────────────────────────────┘

OPTION 2: Backend API (Server-based)
┌──────────────────────────────────┐
│ /api/detect-attention/           │
│                                  │
│ • Capture frame from video       │
│ • Send to backend                │
│ • Azure Cognitive Services call  │
│ • Return attention state         │
│ • More accurate, higher latency  │
│ • Server-side logging enabled    │
└──────────────────────────────────┘

BOTH OPTIONS:
├─ Input: Video frame
├─ Output: 'attentive' | 'distracted'
├─ Latency: < 100ms ideal
├─ Error Handling: Default 'attentive'
└─ Fallback: Continue with current if unavailable
```

---

## Component Interaction Matrix

```
┌──────────────────────────────────────────────────────────────┐
│          COMPONENT INTERACTION MATRIX                        │
├──────────────────┬──────────────────┬──────────────────────┤
│ Event            │ Triggers         │ Updates              │
├──────────────────┼──────────────────┼──────────────────────┤
│ Video Play       │ onVideoPlay()    │ isTracking = true    │
│                  │                  │ videoPlaying = true  │
│                  │                  │ Start interval       │
├──────────────────┼──────────────────┼──────────────────────┤
│ Video Pause      │ onVideoPause()   │ isTracking = false   │
│                  │                  │ videoPlaying = false │
│                  │                  │ wasTracking...=true  │
│                  │                  │ Clear interval       │
├──────────────────┼──────────────────┼──────────────────────┤
│ Video End        │ onVideoEnded()   │ Stop all tracking    │
│                  │                  │ Clear camera         │
│                  │                  │ Disable system       │
├──────────────────┼──────────────────┼──────────────────────┤
│ Distraction (3s) │ updateDistraction│ shortAlertShown=true │
│                  │                  │ Show modal           │
├──────────────────┼──────────────────┼──────────────────────┤
│ Distraction (5s) │ updateDistraction│ longAlertActive=true │
│                  │                  │ video.pause()        │
│                  │                  │ playAudioAlert()     │
├──────────────────┼──────────────────┼──────────────────────┤
│ Focus Detected   │ onAttentive      │ longAlertActive=false│
│                  │ Detected()       │ Clear modal          │
│                  │                  │ Reset counters       │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

## Complete System Flowchart

```
START
  │
  ▼
┌─────────────────────────────────────┐
│ Page Loads, AttentionTracker Init   │
│ • Load config (3s, 5s, 500ms)       │
│ • Set up event listeners            │
│ • Student name from Django context  │
└──────────────┬──────────────────────┘
               │
          [LOOP START]
               │
    ┌──────────▼──────────┐
    │ Student Action?     │
    └──┬─────┬────────┬───┘
       │     │        │
  PLAY │  PAUSE      │END
       │     │        │
  ┌────▼──┐ ┌────▼──┐ ┌───▼────┐
  │onVideo│ │onVideo│ │onVideo │
  │Play() │ │Pause()│ │Ended() │
  └─┬──┬──┘ └────┬──┘ └───┬────┘
    │  │         │        │
  1st │ Subsequent    SaveState
  play│ play          │
    │  │         │    │
  ┌─┴──┴──┐  ┌──▼─┐  │
  │Request │  │Check│  │
  │Camera  │  │Flag │  │
  │Perm    │  └──┬──┘  │
  └─┬────┬─┘     │     │
 Grant Deny  ┌──▼──┐   │
    │    │   │Resume?
    │    │   │─YES→Resume Track
    │    │   │─NO→Continue
    │    │   │
    └────┴───┴───────────────┐
        │                    │
    ┌───▼──────────────┐   ┌─▼───────┐
    │Start Monitoring  │   │Clear UI │
    │(500ms interval)  │   │Disable  │
    └───┬──────────────┘   │system   │
        │                  │END      │
    ┌───▼────────────────┐ └────────┘
    │Check Attention     │
    │Every 500ms         │
    └──┬────────────┬────┘
       │            │
  Attentive    Distracted
       │            │
       ▼            ▼
   ┌───────────┐ ┌──────────────────┐
   │Continue   │ │Track Duration    │
   │Monitoring │ │                  │
   └───────────┘ ├──────┬──────┬───┐
                 │      │      │   │
              <3s    3s    5s  >5s
                 │      │      │   │
                 ▼      ▼      ▼   ▼
               OK   Short   Long  Very
                   Alert   Alert  Long
                   
    [Continue monitoring loop]

END
```

---

## Performance Timeline

```
FIRST PLAY (Camera request):
0ms  ├─ onVideoPlay() called
5ms  ├─ requestCameraPermission()
50ms ├─ Browser shows permission dialog
150ms├─ User decision
     │
100ms (if granted):
     ├─ setupCameraStream()
150ms├─ startAttentionMonitoring()
     ├─ Begin 500ms checks
     └─ READY ✓

NORMAL OPERATIONS:
0ms  ├─ 500ms check timer fires
5ms  ├─ simulateAttentionDetection()
10ms ├─ updateDistraction()
15ms └─ updateUI() (if needed)
     (Total: 15ms, runs every 500ms = 3% CPU)

ALERT TRIGGER:
0ms  ├─ Alert threshold reached
5ms  ├─ showAlert() called
10ms ├─ DOM update
15ms ├─ CSS animation start
20ms └─ Animation completes (2-3s)

AUDIO ALERT:
0ms  ├─ playAudioAlert() called
50ms ├─ Web Speech API init
100ms├─ Speaker starts synthesis
2000ms├─ Message playback complete
2100ms└─ Video unmute, resume flow

PAUSE/RESUME:
0ms  ├─ Pause event
5ms  ├─ onVideoPause()
10ms ├─ Stop interval
15ms └─ Clear alerts
     ─────────────────────
0ms  ├─ Play event (resume)
5ms  ├─ onVideoPlay()
10ms ├─ Check flag
15ms ├─ Resume tracking
20ms └─ Start interval ✓
```

---

**These diagrams represent the complete system architecture, flows, timing, and interactions. Use these as reference for understanding, implementing ML, or debugging issues.**

---

**Document Generated**: May 18, 2026, 08:20 UTC  
**Status**: ✅ Complete with 10 comprehensive diagrams

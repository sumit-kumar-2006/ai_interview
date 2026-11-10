# Live Computer Vision & Webcam Analysis Architecture

This module provides real-time, privacy-preserving visual signal analysis for the AI Interview Analyzer.

## Key Features

1. **Privacy First**:
   - Zero raw webcam video files or video recordings are uploaded to the backend or saved to disk.
   - All visual sampling takes place locally in the candidate's browser via WebRTC (`navigator.mediaDevices.getUserMedia`) and HTML5 Canvas.
   - Only lightweight aggregated summary counts (`face_detected_samples`, `orientation_counts`, `looking_away_samples`) are sent to the backend upon answer completion.

2. **Real Visual Signals Analyzed**:
   - **Face Detection Rate**: Percentage of webcam samples where candidate's face was detected.
   - **Looking Away / Attention Events**: Frequency of off-center or missing face events.
   - **Dominant Head Orientation**: Aggregated head pose estimation (Center, Left, Right, Down).
   - **Visual Attention Index**: Calculated index evaluating candidate presence and camera engagement.

3. **Graceful Fail-Safe Behavior**:
   - If camera permission is denied, camera is missing, or camera disconnects, the system displays *"Insufficient visual data"* cleanly on the dashboard without breaking the interview scoring or audio flow.

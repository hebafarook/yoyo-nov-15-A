"""
MediaPipe Computer Vision System
Pose Detection & Form Analysis for Soccer Training
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math

@dataclass
class PoseAnalysis:
    exercise_type: str
    form_score: float  # 0-100
    detected_issues: List[str]
    corrections: List[str]
    rep_count: int
    angles: Dict[str, float]
    timestamp: str

class MediaPipePoseAnalyzer:
    """Main pose analysis engine using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def analyze_frame(self, frame: np.ndarray, exercise_type: str) -> Optional[Dict]:
        """
        Analyze a single frame for pose detection
        Returns pose landmarks and analysis
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = results.pose_landmarks.landmark
        
        # Calculate key angles based on exercise type
        angles = self._calculate_angles(landmarks)
        
        # Analyze form based on exercise
        if exercise_type == "squat":
            analysis = self._analyze_squat(angles, landmarks)
        elif exercise_type == "lunge":
            analysis = self._analyze_lunge(angles, landmarks)
        elif exercise_type == "sprint":
            analysis = self._analyze_sprint_form(angles, landmarks)
        else:
            analysis = self._analyze_general(angles, landmarks)
        
        return {
            "landmarks": landmarks,
            "angles": angles,
            "analysis": analysis,
            "pose_detected": True
        }
    
    def _calculate_angles(self, landmarks) -> Dict[str, float]:
        """
        Calculate key joint angles from landmarks
        """
        angles = {}
        
        # Get landmark positions
        def get_coords(idx):
            lm = landmarks[idx]
            return [lm.x, lm.y, lm.z]
        
        # Hip angle (left side)
        if len(landmarks) > 28:
            shoulder_l = get_coords(self.mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            hip_l = get_coords(self.mp_pose.PoseLandmark.LEFT_HIP.value)
            knee_l = get_coords(self.mp_pose.PoseLandmark.LEFT_KNEE.value)
            angles['hip_left'] = self._calculate_angle_3d(shoulder_l, hip_l, knee_l)
            
            # Knee angle (left side)
            ankle_l = get_coords(self.mp_pose.PoseLandmark.LEFT_ANKLE.value)
            angles['knee_left'] = self._calculate_angle_3d(hip_l, knee_l, ankle_l)
            
            # Ankle angle
            foot_l = get_coords(self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value)
            angles['ankle_left'] = self._calculate_angle_3d(knee_l, ankle_l, foot_l)
            
            # Same for right side
            shoulder_r = get_coords(self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            hip_r = get_coords(self.mp_pose.PoseLandmark.RIGHT_HIP.value)
            knee_r = get_coords(self.mp_pose.PoseLandmark.RIGHT_KNEE.value)
            ankle_r = get_coords(self.mp_pose.PoseLandmark.RIGHT_ANKLE.value)
            
            angles['hip_right'] = self._calculate_angle_3d(shoulder_r, hip_r, knee_r)
            angles['knee_right'] = self._calculate_angle_3d(hip_r, knee_r, ankle_r)
            
            # Torso angle (verticality)
            shoulder_mid = [(shoulder_l[i] + shoulder_r[i])/2 for i in range(3)]
            hip_mid = [(hip_l[i] + hip_r[i])/2 for i in range(3)]
            angles['torso_angle'] = self._calculate_torso_lean(shoulder_mid, hip_mid)
        
        return angles
    
    def _calculate_angle_3d(self, a: List[float], b: List[float], c: List[float]) -> float:
        """
        Calculate angle between three 3D points
        b is the vertex
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _calculate_torso_lean(self, shoulder: List[float], hip: List[float]) -> float:
        """
        Calculate torso lean from vertical (0 = perfectly vertical)
        """
        dx = shoulder[0] - hip[0]
        dy = shoulder[1] - hip[1]
        
        angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        return angle
    
    def _analyze_squat(self, angles: Dict, landmarks) -> Dict:
        """
        Analyze squat form
        """
        issues = []
        corrections = []
        form_score = 100
        
        knee_angle = angles.get('knee_left', 180)
        hip_angle = angles.get('hip_left', 180)
        torso_angle = angles.get('torso_angle', 0)
        
        # Check squat depth
        if knee_angle > 100:
            issues.append("Squat not deep enough")
            corrections.append("🔽 Lower hips until thighs are parallel to ground (knee angle ~90°)")
            form_score -= 20
        elif knee_angle < 70:
            issues.append("Squat too deep - risk of knee strain")
            corrections.append("⚠️ Stop at parallel or slightly below")
            form_score -= 10
        
        # Check torso position
        if torso_angle > 30:
            issues.append("Torso leaning too far forward")
            corrections.append("🧘 Keep chest up, maintain upright torso (max 20-30° lean)")
            form_score -= 15
        
        # Check knee tracking
        # Compare knee and ankle positions
        knee_pos = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle_pos = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        if abs(knee_pos.x - ankle_pos.x) > 0.1:  # Knee caving in or out
            issues.append("Knee tracking issue detected")
            corrections.append("🦵 Push knees out in line with toes - don't let them cave in")
            form_score -= 15
        
        # Hip symmetry check
        hip_diff = abs(angles.get('hip_left', 180) - angles.get('hip_right', 180))
        if hip_diff > 10:
            issues.append("Hip asymmetry detected")
            corrections.append("⚖️ Balance weight evenly on both legs")
            form_score -= 10
        
        return {
            "form_score": max(0, form_score),
            "issues": issues,
            "corrections": corrections,
            "knee_depth": knee_angle,
            "hip_depth": hip_angle,
            "verdict": "Excellent" if form_score >= 85 else "Good" if form_score >= 70 else "Needs Work"
        }
    
    def _analyze_lunge(self, angles: Dict, landmarks) -> Dict:
        """
        Analyze lunge form
        """
        issues = []
        corrections = []
        form_score = 100
        
        # Front knee angle
        front_knee = angles.get('knee_left', 180)
        
        # Check front knee depth
        if front_knee > 110:
            issues.append("Lunge not deep enough")
            corrections.append("🔽 Drop back knee closer to ground - front knee ~90°")
            form_score -= 20
        
        # Check front knee doesn't pass toes excessively
        knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        
        if knee.x > ankle.x + 0.15:  # Knee way past ankle
            issues.append("Front knee too far forward")
            corrections.append("⚠️ Keep front knee over ankle - don't let it pass toes")
            form_score -= 15
        
        # Torso position
        torso = angles.get('torso_angle', 0)
        if torso > 20:
            issues.append("Torso leaning forward")
            corrections.append("💪 Keep torso upright and core engaged")
            form_score -= 10
        
        return {
            "form_score": max(0, form_score),
            "issues": issues,
            "corrections": corrections,
            "front_knee_angle": front_knee,
            "verdict": "Excellent" if form_score >= 85 else "Good" if form_score >= 70 else "Needs Work"
        }
    
    def _analyze_sprint_form(self, angles: Dict, landmarks) -> Dict:
        """
        Analyze sprint/running form
        """
        issues = []
        corrections = []
        form_score = 100
        
        # Check arm position
        shoulder_l = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow_l = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist_l = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        # Arm angle should be ~90 degrees
        arm_angle = self._calculate_angle_3d(
            [shoulder_l.x, shoulder_l.y, shoulder_l.z],
            [elbow_l.x, elbow_l.y, elbow_l.z],
            [wrist_l.x, wrist_l.y, wrist_l.z]
        )
        
        if arm_angle > 110 or arm_angle < 70:
            issues.append("Arm angle suboptimal")
            corrections.append("💪 Maintain 90° elbow angle during arm swing")
            form_score -= 10
        
        # Check torso lean (should be slight forward lean)
        torso = angles.get('torso_angle', 0)
        if torso > 25:
            issues.append("Excessive forward lean")
            corrections.append("🏃 Slight lean is good (5-15°), but maintain upright posture")
            form_score -= 15
        elif torso < 3:
            issues.append("Too upright - need slight forward lean")
            corrections.append("➡️ Lean slightly forward from ankles (not waist)")
            form_score -= 10
        
        return {
            "form_score": max(0, form_score),
            "issues": issues,
            "corrections": corrections,
            "arm_angle": arm_angle,
            "torso_lean": torso,
            "verdict": "Excellent" if form_score >= 85 else "Good" if form_score >= 70 else "Needs Work"
        }
    
    def _analyze_general(self, angles: Dict, landmarks) -> Dict:
        """
        General movement analysis
        """
        return {
            "form_score": 75,
            "issues": [],
            "corrections": ["Continue with proper form"],
            "verdict": "Good"
        }
    
    def draw_landmarks(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """
        Draw pose landmarks on frame
        """
        annotated_frame = frame.copy()
        
        # Draw landmarks
        self.mp_drawing.draw_landmarks(
            annotated_frame,
            landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        
        return annotated_frame

class RepCounter:
    """Count exercise repetitions"""
    
    def __init__(self, exercise_type: str):
        self.exercise_type = exercise_type
        self.rep_count = 0
        self.state = "up"  # or "down"
        self.last_angle = 180
    
    def update(self, angles: Dict) -> int:
        """
        Update rep count based on angles
        """
        if self.exercise_type == "squat":
            return self._count_squat(angles)
        elif self.exercise_type == "lunge":
            return self._count_lunge(angles)
        else:
            return self.rep_count
    
    def _count_squat(self, angles: Dict) -> int:
        """
        Count squat reps based on knee angle
        """
        knee_angle = angles.get('knee_left', 180)
        
        # Down phase: knee angle < 100
        if knee_angle < 100 and self.state == "up":
            self.state = "down"
        
        # Up phase: knee angle > 150 after being down
        elif knee_angle > 150 and self.state == "down":
            self.state = "up"
            self.rep_count += 1
        
        return self.rep_count
    
    def _count_lunge(self, angles: Dict) -> int:
        """
        Count lunge reps
        """
        front_knee = angles.get('knee_left', 180)
        
        if front_knee < 100 and self.state == "up":
            self.state = "down"
        elif front_knee > 150 and self.state == "down":
            self.state = "up"
            self.rep_count += 1
        
        return self.rep_count

class VideoAnalyzer:
    """Analyze entire videos or frame sequences"""
    
    def __init__(self):
        self.pose_analyzer = MediaPipePoseAnalyzer()
    
    def analyze_video(self, video_path: str, exercise_type: str) -> Dict:
        """
        Analyze an entire video file
        """
        cap = cv2.VideoCapture(video_path)
        
        rep_counter = RepCounter(exercise_type)
        frame_analyses = []
        
        frame_count = 0
        analyzed_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Analyze every 5th frame to reduce processing
            if frame_count % 5 == 0:
                analysis = self.pose_analyzer.analyze_frame(frame, exercise_type)
                
                if analysis:
                    analyzed_frames += 1
                    frame_analyses.append(analysis['analysis'])
                    
                    # Update rep count
                    reps = rep_counter.update(analysis['angles'])
        
        cap.release()
        
        # Aggregate results
        if frame_analyses:
            avg_form_score = sum(a['form_score'] for a in frame_analyses) / len(frame_analyses)
            all_issues = [issue for a in frame_analyses for issue in a['issues']]
            issue_counts = {issue: all_issues.count(issue) for issue in set(all_issues)}
            
            return {
                "total_frames": frame_count,
                "analyzed_frames": analyzed_frames,
                "rep_count": rep_counter.rep_count,
                "average_form_score": round(avg_form_score, 1),
                "common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "exercise_type": exercise_type
            }
        else:
            return {
                "error": "No pose detected in video",
                "total_frames": frame_count
            }

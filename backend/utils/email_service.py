# Email Service for Training Reminders and Notifications
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send HTML email via SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_daily_training_reminder(self, user_email: str, user_name: str, 
                                     player_name: str, exercises: List[dict]) -> bool:
        """Send daily training reminder"""
        subject = f"⚽ Training Reminder - {player_name}"
        
        exercises_html = ""
        for ex in exercises[:3]:  # Show first 3 exercises
            exercises_html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{ex.get('name', 'Exercise')}</strong><br>
                <small>{ex.get('duration', 15)} minutes - {ex.get('category', 'Training')}</small>
            </li>
            """
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #003d7a 0%, #1e5f8c 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: #f5e6d3; margin: 0;">⚽ Yo-Yo Elite Soccer</h1>
                    <p style="color: #f5e6d3; margin: 10px 0 0 0;">Daily Training Reminder</p>
                </div>
                
                <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none;">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    
                    <p>Time for today's training session for <strong>{player_name}</strong>! 🎯</p>
                    
                    <div style="background: #f0f8ff; padding: 20px; border-left: 4px solid #003d7a; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #003d7a;">Today's Exercises:</h3>
                        <ul style="list-style-type: none; padding-left: 0;">
                            {exercises_html}
                        </ul>
                    </div>
                    
                    <p><strong>Remember to:</strong></p>
                    <ul>
                        <li>✅ Check in before starting your training</li>
                        <li>✅ Complete all exercises with proper form</li>
                        <li>✅ Check out after finishing</li>
                        <li>✅ Stay hydrated and warm up properly</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}" 
                           style="background: #003d7a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Open Training App
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                        Don't want these reminders? <a href="#">Update your notification preferences</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_check_in_reminder(self, user_email: str, user_name: str, player_name: str) -> bool:
        """Send check-in reminder before training time"""
        subject = f"⏰ Don't forget to check in - {player_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #ff9800; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h2 style="color: white; margin: 0;">⏰ Training Starts Soon!</h2>
                </div>
                
                <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none;">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    
                    <p>Your training session for <strong>{player_name}</strong> is about to begin!</p>
                    
                    <div style="background: #fff3e0; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <p style="font-size: 18px; margin: 0;"><strong>📍 Remember to CHECK IN</strong></p>
                        <p style="margin: 10px 0 0 0;">Track your progress and stay accountable!</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/training" 
                           style="background: #ff9800; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Check In Now
                        </a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_weekly_progress_summary(self, user_email: str, user_name: str, 
                                     player_name: str, stats: dict) -> bool:
        """Send weekly progress summary"""
        subject = f"📊 Weekly Progress Report - {player_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #4caf50 0%, #81c784 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">📊 Weekly Progress Report</h1>
                </div>
                
                <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none;">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    
                    <p>Here's <strong>{player_name}</strong>'s training summary for this week:</p>
                    
                    <div style="background: #f1f8f4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0;"><strong>Training Days Completed:</strong></td>
                                <td style="text-align: right; color: #4caf50; font-size: 20px; font-weight: bold;">
                                    {stats.get('completed_days', 0)}/{stats.get('scheduled_days', 5)}
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0;"><strong>Total Exercises:</strong></td>
                                <td style="text-align: right; font-size: 18px;">{stats.get('total_exercises', 0)}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0;"><strong>Training Time:</strong></td>
                                <td style="text-align: right; font-size: 18px;">{stats.get('total_minutes', 0)} min</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0;"><strong>Consistency Score:</strong></td>
                                <td style="text-align: right; font-size: 18px;">{stats.get('consistency', 0)}%</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p><strong>Keep up the great work! 💪</strong></p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/progress" 
                           style="background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View Full Report
                        </a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_milestone_achievement(self, user_email: str, user_name: str, 
                                   player_name: str, milestone: str) -> bool:
        """Send milestone achievement notification"""
        subject = f"🏆 Achievement Unlocked - {player_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: #003d7a; margin: 0;">🏆 Achievement Unlocked!</h1>
                </div>
                
                <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none; text-align: center;">
                    <p style="font-size: 18px;">Congratulations <strong>{user_name}</strong>!</p>
                    
                    <div style="background: #fff9e6; padding: 30px; border-radius: 8px; margin: 20px 0;">
                        <div style="font-size: 48px; margin-bottom: 10px;">🎯</div>
                        <h2 style="color: #003d7a; margin: 10px 0;">{milestone}</h2>
                        <p style="color: #666; margin: 10px 0 0 0;"><strong>{player_name}</strong> has reached a new milestone!</p>
                    </div>
                    
                    <p>Keep pushing forward to reach even greater heights! 🚀</p>
                    
                    <div style="margin: 30px 0;">
                        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/achievements" 
                           style="background: #ffd700; color: #003d7a; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View All Achievements
                        </a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)

# Global email service instance
email_service = EmailService()

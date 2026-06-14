"""Email service for sending reminders via SMTP."""
import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.email_config import EmailConfig
from ..models.reminder import Reminder
from ..utils.crypto import decrypt

logger = logging.getLogger(__name__)


class EmailService:

    def send_reminder(self, db: Session, reminder: Reminder) -> bool:
        """Send a single reminder email. Returns True on success."""
        config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
        if not config or not config.enabled:
            logger.warning("Email not configured or disabled, skipping reminder")
            return False

        auth = decrypt(config.auth_code)
        if not auth:
            logger.error("Failed to decrypt email auth_code")
            return False

        task = reminder.task
        subject = f"任务提醒：{task.title}"
        body = f"任务「{task.title}」的提醒。\n截止日期：{task.due_date or '未设定'}\n优先级：{task.priority}"

        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = config.sender_email
            msg["To"] = config.sender_email

            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
                server.login(config.sender_email, auth)
                server.sendmail(config.sender_email, [config.sender_email], msg.as_string())

            logger.info(f"Reminder sent for task {task.id}: {task.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reminder for task {task.id}: {e}")
            return False

    def send_test(self, db: Session) -> tuple[bool, str]:
        """Send a test email to verify configuration."""
        config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
        if not config:
            return False, "邮件配置未找到"

        auth = decrypt(config.auth_code)
        if not auth:
            return False, "授权码解密失败，请重新填写"

        try:
            msg = MIMEText("这是一封来自时间管理平台的测试邮件。配置正确！", "plain", "utf-8")
            msg["Subject"] = "测试邮件 - 时间管理平台"
            msg["From"] = config.sender_email
            msg["To"] = config.sender_email

            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
                server.login(config.sender_email, auth)
                server.sendmail(config.sender_email, [config.sender_email], msg.as_string())

            return True, "测试邮件发送成功"
        except Exception as e:
            return False, f"发送失败：{str(e)}"

    def scan_and_send(self, db: Session):
        """Called by APScheduler. Scans for due reminders and sends them."""
        now = datetime.utcnow()
        reminders = (
            db.query(Reminder)
            .filter(Reminder.remind_at <= now, Reminder.sent == False, Reminder.fail_count < 3)
            .all()
        )
        for r in reminders:
            success = self.send_reminder(db, r)
            if success:
                r.sent = True
                r.fail_count = 0
            else:
                r.fail_count += 1
            db.commit()

import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from decouple import config

GMAIL_USER = config("GMAIL_USER", default="")
GMAIL_APP_PASSWORD = config("GMAIL_APP_PASSWORD", default="")
ADMIN_NOTIFY_EMAIL = config("ADMIN_NOTIFY_EMAIL", default=GMAIL_USER)


def _send(to: str, subject: str, html: str) -> None:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"100:0 연구소 <{GMAIL_USER}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_USER, to, msg.as_string())


def _send_async(to: str, subject: str, html: str) -> None:
    threading.Thread(target=_send, args=(to, subject, html), daemon=True).start()


def send_submission_confirmation(
    to_email: str,
    submission_no: str,
    incident_type: str,
    region_sido: str,
    bank_name: str,
    account_number_masked: str,
    account_holder: str,
) -> None:
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"></head>
<body style="font-family: sans-serif; color: #0a0a0a; max-width: 560px; margin: 0 auto; padding: 32px 24px;">
  <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">영상 제보 접수 완료</h2>
  <p style="font-size: 14px; color: #888; margin-bottom: 32px;">100:0 연구소</p>

  <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888; width: 120px;">접수번호</td>
      <td style="padding: 10px 0; font-weight: 600;">{submission_no}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">사고 유형</td>
      <td style="padding: 10px 0;">{incident_type}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">지역</td>
      <td style="padding: 10px 0;">{region_sido}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">지급 계좌</td>
      <td style="padding: 10px 0;">{bank_name} {account_number_masked} ({account_holder})</td>
    </tr>
    <tr>
      <td style="padding: 10px 0; color: #888;">현재 상태</td>
      <td style="padding: 10px 0;">검수 대기</td>
    </tr>
  </table>

  <div style="background: #f8f8f8; padding: 16px; font-size: 13px; color: #555; margin-bottom: 24px; line-height: 1.6;">
    운영팀 검수 후 채택 여부가 결정됩니다.<br>
    채택된 영상은 입력하신 계좌로 <strong>건당 5,000원</strong>이 지급됩니다.<br>
    검수 과정에서 추가 확인이 필요한 경우 연락드릴 수 있습니다.
  </div>

  <p style="font-size: 12px; color: #aaa;">
    본 메일은 발신 전용입니다. 문의는 서비스 내 채널을 이용해 주세요.
  </p>
</body>
</html>
"""
    _send_async(to_email, f"[100:0 LAB] 영상 제보 접수 완료 — {submission_no}", html)


def send_admin_new_submission(
    submission_no: str,
    submitter_email: str,
    incident_type: str,
    region: str,
    submission_id: int,
) -> None:
    if not ADMIN_NOTIFY_EMAIL:
        return
    admin_url = f"https://www.100to0lab.com/admin/submissions/{submission_id}"
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"></head>
<body style="font-family: sans-serif; color: #0a0a0a; max-width: 560px; margin: 0 auto; padding: 32px 24px;">
  <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">새 제보가 접수되었습니다</h2>
  <p style="font-size: 14px; color: #888; margin-bottom: 32px;">100:0 연구소 관리자 알림</p>

  <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888; width: 120px;">접수번호</td>
      <td style="padding: 10px 0; font-weight: 600;">{submission_no}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">제보자 이메일</td>
      <td style="padding: 10px 0;">{submitter_email}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">사고 유형</td>
      <td style="padding: 10px 0;">{incident_type}</td>
    </tr>
    <tr style="border-bottom: 1px solid #e5e5e5;">
      <td style="padding: 10px 0; color: #888;">지역</td>
      <td style="padding: 10px 0;">{region}</td>
    </tr>
  </table>

  <a href="{admin_url}"
     style="display: inline-block; background: #0a0a0a; color: #fff; padding: 12px 24px; font-size: 14px; font-weight: 600; text-decoration: none;">
    검수하러 가기 →
  </a>
</body>
</html>
"""
    _send_async(ADMIN_NOTIFY_EMAIL, f"[100:0 LAB] 새 제보 접수 — {submission_no}", html)

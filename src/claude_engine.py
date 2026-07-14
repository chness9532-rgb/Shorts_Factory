import os
from anthropic import Anthropic

# 🔐 [보안] 키는 코드에 박지 않고 환경변수에서 읽어온다.
#    등록:  setx ANTHROPIC_API_KEY "sk-ant-..."   (등록 후 터미널/VSCode 재시작)
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def ask_claude(system_instruction, user_message):
    """
    클로드 AI에게 질문을 던지고 답변을 받아오는 범용 함수
    """
    if not CLAUDE_API_KEY:
        print("❌ [클로드 엔진 에러] 환경변수 ANTHROPIC_API_KEY 가 없습니다.")
        print("   PowerShell에서:  setx ANTHROPIC_API_KEY \"sk-ant-...\"  등록 후 터미널을 재시작하세요.")
        return None
    try:
        # 본사 다이렉트 주소 세팅
        client = Anthropic(
            api_key=CLAUDE_API_KEY,
            base_url="https://api.anthropic.com"
        )
        
        # 🎯 [소름 돋는 핵심 변경] 본사 캡처 화면 공식 가이드에 적힌 신형 모델 ID 그대로 매칭!
        message = client.messages.create(
            model="claude-sonnet-4-6",  # 👈 앤트로픽 최신형 공식 모델 ID!!
            max_tokens=1000,
            temperature=0.7,
            system=system_instruction,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text.strip()
        
    except Exception as e:
        print(f"❌ [클로드 엔진 에러] 통신 실패: {e}")
        return None
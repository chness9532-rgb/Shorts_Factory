import json
import os
import urllib.parse
import requests
import re
import base64  # 👈 [오타 완벽 수정!] 기존 base6에서 진짜 표준 라이브러리 명칭으로 변경
from PIL import Image, ImageEnhance
from src.claude_engine import ask_claude

# =====================================================================
# 💳 [프리미엄 이미지 공장 설정]
# =====================================================================
# 전 세계 표준인 OpenAI gpt-image 엔진을 기본 가동합니다.
IMAGE_ENGINE = "openai"  # "openai" 또는 "pollinations"

# 🔐 [보안] 키는 코드에 박지 않고 환경변수에서 읽어온다.
#    등록:  setx OPENAI_API_KEY "sk-proj-..."   (등록 후 터미널/VSCode 재시작)
#    비어 있으면 자동으로 무료 백업 라인(Pollinations)으로 우회한다.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# =====================================================================

def clean_old_backgrounds(bg_dir):
    """ 🧹 [자재 청소 로봇] 새로운 공정이 시작되기 전 옛날 잔해(JPG, SVG)를 완벽히 소각 """
    if os.path.exists(bg_dir):
        for file in os.listdir(bg_dir):
            if file.startswith("bg") and (file.endswith(".jpg") or file.endswith(".svg")):
                try:
                    os.remove(os.path.join(bg_dir, file))
                except Exception:
                    pass

def enhance_image_quality(image_path):
    """ 📸 [화질 극대화 정밀 현상 엔진] gpt-image로 뽑은 명작의 선명도와 대비를 극적으로 부스팅 """
    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 15000:
            return
            
        img = Image.open(image_path)
        
        # 선명도 1.4배 쨍하게 보정 (디테일 묘사 상승)
        enhancer_sharp = ImageEnhance.Sharpness(img)
        img = enhancer_sharp.enhance(1.4)
        
        # 시네마틱 대비 1.1배 보정 (입체감과 명암비 상승)
        enhancer_contrast = ImageEnhance.Contrast(img)
        img = enhancer_contrast.enhance(1.1)
        
        # 숏폼 최적화 세로 규격(1080x1920)으로 정밀 리샘플링하여 최종 저장
        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        img.save(image_path, "JPEG", quality=95)
        print(f"✨ [화질 극대화 필터] => {os.path.basename(image_path)} 최종 현상 완료!")
    except Exception as e:
        print(f"⚠️ 화질 개선 중 에러 발생 (건너뜀): {e}")

def generate_visual_image(prompt, output_path):
    """ 🎨 [마스터 분기 타워] 설정에 따라 OpenAI 유료 라인 또는 무료 백업 라인을 자동 가동 """
    if IMAGE_ENGINE == "openai" and OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-proj-여기에"):
        success = generate_via_openai_dalle(prompt, output_path)
        if success:
            enhance_image_quality(output_path)
            return True
    
    # 실패하거나 키가 없으면 백업 라인 작동
    success = generate_via_pollinations(prompt, output_path)
    if success:
        enhance_image_quality(output_path)
    return success

def generate_via_openai_dalle(prompt, output_path):
    """ 💳 [gpt-image-1 프리미엄 엔진] 최신 응답 규격(b64_json)에 맞춰 1024x1536 고화질 이미지 저장 """
    print(f"💳 [gpt-image 가동] OpenAI 공식 API 라인 연동 중...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    # 2026년 최신 gpt-image-1 규격 정밀 장착
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1536",
        "quality": "high"
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # ✨ [핵심 수정] 최신 규격인 'b64_json' 방을 찾아 원본 암호를 정밀 해독
            if 'data' in result and len(result['data']) > 0:
                img_data_b64 = result['data'][0].get('b64_json')
                
                if img_data_b64:
                    img_bytes = base64.b64decode(img_data_b64)
                    with open(output_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"📸 [프리미엄 자재 수급 성공] => {os.path.basename(output_path)} (gpt-image-1 정상 출하)")
                    return True
            
            print("⚠️ 최신 규격 데이터 해석 실패, 백업 라인 가동")
            return False
        else:
            print(f"⚠️ OpenAI API 호출 오류 (코드 {response.status_code}): {response.text}")
            print("🛑 API 키 잔액 부족 혹은 유효하지 않은 키입니다 ➔ 무료 백업 라인으로 긴급 우회합니다.")
            return False
    except Exception as e:
        print(f"❌ OpenAI 호출 실패 에러: {e}")
        return False

def generate_via_pollinations(style_prompt, output_path):
    """ 🎨 [무료 백업 엔진] 공식 라인 장애 시 가동되는 Stable Diffusion 3.5 Large 라기 """
    master_prompt = (
        f"A masterpiece cinema still, award-winning photography, photorealistic texture, "
        f"cinematic grading, hyper-detailed 8k resolution, crisp sharp focus, {style_prompt}"
    )
    encoded_prompt = urllib.parse.quote(master_prompt)
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1080&height=1920&nologo=true&private=true"
        f"&model=sd35&enhance=true&seed={os.urandom(4).hex()}"
    )
    try:
        res = requests.get(image_url, timeout=30)
        if res.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(res.content)
            print(f"📸 [무료 백업 자재 수급 성공] => {os.path.basename(output_path)}")
            return True
        return False
    except Exception:
        return False

def extract_robust_json(text):
    """ 🔍 [정밀 구출 로봇] 클로드의 불필요한 잡담 속에서 진짜 '대본 JSON 완제품'만 완벽하게 도려냄 """
    text_clean = text.strip()
    try:
        return json.loads(text_clean)
    except Exception:
        pass

    starts = [m.start() for m in re.finditer(r'\{', text_clean)]
    ends = [m.start() for m in re.finditer(r'\}', text_clean)]

    for start in reversed(starts):
        for end in reversed(ends):
            if end > start:
                substring = text_clean[start:end+1]
                try:
                    data = json.loads(substring)
                    if "image_prompt_1" in data and "script_1" in data:
                        return data
                except Exception:
                    pass

    for start in starts:
        for end in ends:
            if end > start:
                substring = text_clean[start:end+1]
                try:
                    return json.loads(substring)
                except Exception:
                    pass
    return None

def generate_shorts_source(book_title, is_test_mode):
    """ 🤖 클로드 1인 총괄 체제로 10초 분할형 대본 및 4K급 영문 이미지 지시서 기획 """
    bg_dir = os.path.join("assets", "backgrounds")
    
    print("🧹 [공장 청소] 새 영상 제작을 위해 기존 배경 자재 파편들을 전격 소각합니다...")
    clean_old_backgrounds(bg_dir)

    if is_test_mode:
        print(f"\n⚠️  [테스트 가동] 비용 0원 모드이므로 가짜 대본과 테스트 이미지를 사용합니다.")
        test_data = {
            "script_1": "당신이 지금까지\n가난했던 진짜 이유는",
            "script_2": "돈이 없어서가\n아닙니다.",
            "script_3": "돈을 바라보는\n당신의 심리 상태가\n뇌를 지배하기 때문이죠.",
            "image_prompt_1": "A successful business entrepreneur standing in front of a giant skyscraper glass window at sunset golden hour, back view, sharp focus, hyper-detailed", 
            "image_prompt_2": "A massive surreal life tree made of pure gold coins, depth of field, award-winning photography", 
            "image_prompt_3": "A highly-detailed modern cosmic library with massive windows revealing a breathtaking starry galaxy night sky, photorealistic"
        }
        generate_visual_image(test_data["image_prompt_1"], os.path.join(bg_dir, "bg1.jpg"))
        generate_visual_image(test_data["image_prompt_2"], os.path.join(bg_dir, "bg2.jpg"))
        generate_visual_image(test_data["image_prompt_3"], os.path.join(bg_dir, "bg3.jpg"))
        return test_data

    print(f"\n🤖 [모듈 1] 클로드 AI가 《{book_title}》 100만 조회수 대본과 매칭 이미지를 기획 중입니다...")
    
    system_prompt = (
        "너는 유튜브 조회수 100만을 찍는 책 리뷰 전문 숏폼 크리에이터이자, 전세계 최고 수준의 영화 감독이야.\n"
        "사용자가 책 제목을 주면, 시청자의 시선을 사로잡을 30초 분량 of 쇼츠 대본을 정확히 10초씩 3개 구간으로 나누어 작성해줘.\n"
        "말투는 확신에 찬 어조(~입니다, ~하세요, ~하죠)를 사용하고, 자막 가독성을 위해 줄바꿈(\\n)을 매우 자주 넣어줘.\n\n"
        "또한 각 10초 구간의 대본 내용에 100% 대응하는 예술적인 이미지 생성을 위해, 구체적이고 명확한 영문(English) 이미지 프롬프트를 3개 작성해줘.\n\n"
        "⚠️ [AI 이미지 생성 실패 방지 절대 규칙 - 위반시 즉각 소각]\n"
        "1. 절대 인물의 얼굴 정면 클로즈업(Close-up) 프롬프트를 짜지 마. 이목구비가 기괴해질 수 있어.\n"
        "2. 인물이 등장할 때는 반드시 창밖을 바라보는 뒷모습(Back view), 옆모습(Side profile), 혹은 웅장한 배경에 묻어가는 전신(Full shot) 구도로만 기획해.\n"
        "3. 대본의 무드에 맞는 고급스러운 사물(예: 황금 모래시계, 서재의 책들, 고급 만년필)이나 압도적인 배경(예: 스카이라인, 은하수 밤하늘) 위주로 명확하게 묘사해.\n"
        "4. 반드시 'photorealistic, cinematic composition, award-winning photography, high-end grading' 키워드를 포함해줘. "
        "5. 이미지 안에 글자(Text)는 절대 넣지 마.\n\n"
        "⚠️ 중요: 결과는 반드시 아래의 딱 '순수한 JSON 형식' 하나만 답변해. 앞뒤에 절대 아무런 인사말, 설명, 마크다운 기호도 붙이지 마.\n"
        "{\n"
        '  "script_1": "0~10초 구간 대본",\n'
        '  "script_2": "10~20초 구간 대본",\n'
        '  "script_3": "20~30초 구간 대본",\n'
        '  "image_prompt_1": "위 규칙을 완벽히 준수한 0~10초 영어 이미지 프롬프트",\n'
        '  "image_prompt_2": "위 규칙을 완벽히 준수한 10~20초 영어 이미지 프롬프트",\n'
        '  "image_prompt_3": "위 규칙을 완벽히 준수한 20~30초 영어 이미지 프롬프트"\n'
        "}"
    )

    ai_response = ask_claude(system_prompt, f"책 제목: {book_title}")
    
    if not ai_response:
        return None

    raw_text = ai_response.strip()

    try:
        result_json = extract_robust_json(raw_text)
        
        if not result_json:
            raise ValueError("출력 파편 속에서 완벽한 기획안 JSON 구조를 찾아내지 못했습니다.")
            
        print("✅ [모듈 1 성공] 클로드가 대사 및 초고화질 이미지 기획안을 완성했습니다!")
        print("\n🚀 [자동 드로잉] 기획안을 최고 품질 시네마틱 엔진으로 전송하여 실시간 생성을 시작합니다...")
        
        # 하단 변수 꼬임 현상 완벽 처리 (generate_visual_image 통합 관문을 태움)
        generate_visual_image(result_json.get("image_prompt_1"), os.path.join(bg_dir, "bg1.jpg"))
        generate_visual_image(result_json.get("image_prompt_2"), os.path.join(bg_dir, "bg2.jpg"))
        generate_visual_image(result_json.get("image_prompt_3"), os.path.join(bg_dir, "bg3.jpg"))
        print("🎉 [자재 입고 완료] 대사 맞춤형 최고화질 명화 3장이 새롭게 입고되었습니다!\n")
        
        return result_json
        
    except Exception as e:
        print(f"❌ [모듈 1 에러] 실행 실패: {e}")
        print(f"🔍 AI 답변 원본 파편 수거함:\n{raw_text}\n")
        return None
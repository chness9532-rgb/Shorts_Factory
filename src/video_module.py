import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from moviepy import TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip

def generate_tts_audio(text, output_audio_path):
    """ 🎙️ [오디오 공정] AI 성우가 대본에 숨소리를 넣으며 낭독 음성 생성 """
    print("🎙️ [오디오 공정] AI 성우가 대본에 숨소리를 넣으며 낭독 중입니다...")
    clean_text = text.strip().replace("\n\n", ". ").replace("\n", ", ").replace('"', "'")
    
    command = [
        "edge-tts",
        "--voice", "ko-KR-SunHiNeural",
        "--rate=-8%",  
        "--text", clean_text,
        "--write-media", output_audio_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0
    except Exception:
        return False

def build_video_with_subtitles(script_data, output_filename):
    """ 🎬 [시네마틱 FHD 조립 엔진] 1080x1920 고화질, 자막 마감, 배경음악 합성 구현 """
    print("🎬 [모듈 2] FHD 시네마틱 와이드 자막 조립 및 타임라인 싱크 매칭 시작...")
    
    # 🎯 [화질 혁명] 세로 FHD 1080x1920 정식 쇼츠 규격으로 전격 격상!
    video_width = 1080
    video_height = 1920
    
    if isinstance(script_data, dict):
        s1 = script_data.get("script_1", "")
        s2 = script_data.get("script_2", "")
        s3 = script_data.get("script_3", "")
    else:
        lines = script_data.split("\n\n")
        s1 = lines[0] if len(lines) > 0 else script_data
        s2 = lines[1] if len(lines) > 1 else ""
        s3 = lines[2] if len(lines) > 2 else ""

    full_voice_text = f"{s1}\n\n{s2}\n\n{s3}"
    
    audio_dir = os.path.join("outputs", "audios")
    temp_audio_path = os.path.join(audio_dir, output_filename.replace(".mp4", ".mp3"))
    
    tts_success = generate_tts_audio(full_voice_text, temp_audio_path)
    
    audio_duration = 30.0
    if tts_success and os.path.exists(temp_audio_path):
        try:
            temp_audio = AudioFileClip(temp_audio_path)
            audio_duration = temp_audio.duration
            temp_audio.close()
            print(f"⏱️ [길이 감지] AI 성우의 총 낭독 시간: {audio_duration:.2f}초")
        except Exception as e:
            print(f"⚠️ 오디오 길이 측정 실패: {e}")
            
    segment_duration = audio_duration / 3.0
    
    bg_clips = []
    txt_clips = []
    colors = [(20, 24, 33), (32, 21, 38), (17, 34, 30)] 
    bg_dir = os.path.join("assets", "backgrounds")
    font_path = os.path.join("assets", "fonts", "font.ttf")

    if not os.path.exists(font_path):
        print("❌ 에러: 폰트 파일이 없습니다!")
        return False

    scripts_packet = [s1, s2, s3]
    
    # 🎯 [시네마틱 비율 마감] FHD 화면에 맞춰 상하단 검은 띠 비율을 15%로 확장
    bar_height = int(video_height * 0.15) 
    
    for i in range(1, 4):
        bg_image_path = os.path.join(bg_dir, f"bg{i}.jpg")
        
        if os.path.exists(bg_image_path) and os.path.getsize(bg_image_path) > 100:
            print(f"📸 [화면 {i} 조립] 다운로드된 고품질 DALL-E 3 이미지 수급...")
        else:
            canvas = Image.new("RGB", (video_width, video_height), color=colors[i-1])
            canvas.save(bg_image_path, "JPEG", quality=95)
        
        # 원본 소스를 1080x1920 해상도 클립으로 완전 쨍하게 리사이징
        bg_clip = ImageClip(bg_image_path).with_duration(segment_duration).resized((video_width, video_height))
        
        # [안전한 슬로우 줌인 트랜스폼] 버벅임 없는 리샘플링 적용
        def make_zoom(get_frame, t, sd=segment_duration):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            scale = 1.0 + 0.10 * (t / sd) # 부드럽게 10% 줌인
            new_w, new_h = int(w * scale), int(h * scale)
            
            img = Image.fromarray(frame)
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            img_cropped = img_resized.crop((left, top, left + w, top + h))
            return np.array(img_cropped)

        bg_clip = bg_clip.transform(make_zoom)
        bg_clips.append(bg_clip)
        
        current_script = scripts_packet[i-1]
        if current_script.strip():
            # 🎯 [상단 와이드 바] 영화 필름 효과 구현
            top_bar = TextClip(
                text=" ", font_size=1, size=(video_width, bar_height),
                bg_color='black', method='caption'
            ).with_duration(segment_duration).with_position(('center', 'top'))

            # 🎯 [하단 와이드 바] 자막 영역 블랙박스 마감
            bottom_bar = TextClip(
                text=" ", font_size=1, size=(video_width, bar_height),
                bg_color='black', method='caption'
            ).with_duration(segment_duration).with_position(('center', 'bottom'))

            # 🎯 [자막 퀄리티 디테일 조정] 폰트 크기 대폭 키우고 가독성 확보
            txt_clip = TextClip(
                text=current_script, 
                font_size=56, # FHD 해상도에 맞춰 굵고 웅장한 크기로 확장            
                color='white',             
                font=font_path, 
                size=(video_width - 120, bar_height - 20), # 좌우 여백을 넓혀 텍스트 줄바꿈 깔끔하게 처리
                method='caption'
            ).with_duration(segment_duration).with_position(('center', 'center'))
            
            bottom_filled_bar = CompositeVideoClip([bottom_bar, txt_clip], size=(video_width, bar_height)).with_position(('center', 'bottom'))
            
            start_time = (i - 1) * segment_duration
            script_final_clip = CompositeVideoClip([top_bar, bottom_filled_bar], size=(video_width, video_height)).with_start(start_time)
            txt_clips.append(script_final_clip)
            
    background = concatenate_videoclips(bg_clips).with_duration(audio_duration)
    final_video = CompositeVideoClip([background] + txt_clips).with_duration(audio_duration)
    
    # 🎯 [오디오 및 BGM 합성 공정]
    final_audio = None
    if tts_success and os.path.exists(temp_audio_path):
        voice_audio = AudioFileClip(temp_audio_path)
        
        # 만약 assets 폴더에 bgm.mp3가 존재하면 자동으로 믹싱 가동!
        bgm_path = os.path.join("assets", "bgm.mp3")
        if os.path.exists(bgm_path):
            try:
                from moviepy import CompositeAudioClip
                print("🎵 [BGM 합성] assets/bgm.mp3 음원을 발견하여 목소리 뒤로 믹싱합니다...")
                bgm_audio = AudioFileClip(bgm_path).with_duration(audio_duration)
                
                # BGM 볼륨은 잔잔하게 -18dB 이하로 줄이고, 목소리는 쨍하게 유지
                bgm_audio = bgm_audio.with_volume_factor(0.12) # 12% 크기로 배경에 깔아둠
                voice_audio = voice_audio.with_volume_factor(1.2) # 성우 목소리는 120% 증폭
                
                final_audio = CompositeAudioClip([bgm_audio, voice_audio])
            except Exception as e:
                print(f"⚠️ BGM 합성 실패 (목소리만 적용): {e}")
                final_audio = voice_audio
        else:
            print("💡 안내: assets 폴더에 bgm.mp3 파일을 넣어두시면 다음 생성부터 자동으로 BGM이 합성됩니다.")
            final_audio = voice_audio
            
    if final_audio:
        final_video = final_video.with_audio(final_audio)
    
    video_dir = os.path.join("outputs", "videos")
    final_output_path = os.path.join(video_dir, output_filename)
    
    print("📦 [최종 인코딩] 고화질 맞춤 비주얼과 성우 오디오 최종 결합 중...")
    # FHD 출력을 위해 해상도 옵션을 단단히 걸고 인코딩
    final_video.write_videofile(
        final_output_path, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac', 
        preset='medium', # 선명한 화질을 위한 압축률 최적화
        logger=None
    ) 
    print(f"🎉 [풀패키지 완제품 출하] 최종 영상 확인 ➡️ {final_output_path}\n")
    return True
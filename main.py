import os

def initialize_factory():
    """ 🏭 공장 창고 폴더 정밀 점검 """
    required_dirs = [
        os.path.join("outputs", "scripts"),
        os.path.join("outputs", "audios"),
        os.path.join("outputs", "videos")
    ]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

def delete_shorts_set_by_list():
    """ 💣 창고를 스캔해서 배열(리스트)로 보여주고 선택 삭제 """
    print("\n==================================================")
    print("💣 Shorts Factory: 실패작 리스트 선택 폭파 시스템")
    print("==================================================")
    
    video_dir = os.path.join("outputs", "videos")
    if not os.path.exists(video_dir):
        print("🔍 창고가 비어있습니다.")
        return
        
    all_files = os.listdir(video_dir)
    video_list = [f for f in all_files if f.endswith(".mp4")]
    
    if not video_list:
        print("🔍 창고 영상 보관함이 완전히 비어있습니다!")
        return
        
    print("📋 [현재 창고에 보관 중인 쇼츠 완제품 목록]")
    print("--------------------------------------------------")
    for index, video_name in enumerate(video_list):
        print(f" [{index + 1}] {video_name}")
    print(" [0] 취소하고 메인으로 돌아가기")
    print("--------------------------------------------------")
    
    try:
        choice_input = input("👉 삭제할 영상의 번호를 입력하세요: ").strip()
        choice_idx = int(choice_input) - 1
        
        if choice_idx == -1:
            print("🛑 삭제를 취소합니다.")
            return
            
        if choice_idx < 0 or choice_idx >= len(video_list):
            print("❌ 잘못된 번호입니다.")
            return
            
        selected_video = video_list[choice_idx]
        base_name = os.path.splitext(selected_video)[0]
        
        targets = [
            os.path.join("outputs", "videos", f"{base_name}.mp4"),
            os.path.join("outputs", "audios", f"{base_name}.mp3"),
            os.path.join("outputs", "scripts", f"{base_name}_prompts.txt")
        ]
        
        print(f"\n🗑️  [{base_name}] 관련 3대 세트 자재 소각을 시작합니다...")
        print("--------------------------------------------------")
        
        deleted_count = 0
        for target_path in targets:
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"🔥 완전 소각 완료: {target_path}")
                deleted_count += 1
                
        print("--------------------------------------------------")
        print(f"✨ [청소 완료] {base_name} 세트 자재 {deleted_count}개가 깔끔하게 증발했습니다!")
        
    except ValueError:
        print("❌ 숫자만 입력하셔야 합니다!")

if __name__ == "__main__":
    initialize_factory()
    
    print("==================================================")
    print("🏭 Shorts Factory v2.8: 마스터 공장 컨트롤 타워")
    print("==================================================")
    print("1️⃣  쇼츠 완제품 생산 라인 가동")
    print("2️⃣  실패작 세트 목록 확인 및 선택 삭제 (배열 리스트)")
    print("==================================================")
    
    main_choice = input("👉 원하시는 작업 번호를 선택하세요 (1 또는 2): ").strip()
    
    if main_choice == '2':
        delete_shorts_set_by_list()
        exit()
        
    elif main_choice == '1' or main_choice == '':
        from src.llm_module import generate_shorts_source
        from src.video_module import build_video_with_subtitles
        
        mode_input = input("\n🛠️  테스트 모드로 가동할까요? (비용 0원=y / 진짜 AI 가동=n): ").strip().lower()
        is_test_mode = (mode_input == 'y')
        
        target_book = input("✍️  쇼츠로 만들 책 제목을 입력하세요: ").strip()
        
        if not target_book:
            print("❌ 책 제목이 입력되지 않아 공장 가동을 취소합니다.")
        else:
            video_dir = os.path.join("outputs", "videos")
            expected_filename = f"{target_book}_shorts.mp4"
            
            if os.path.exists(os.path.join(video_dir, expected_filename)):
                print(f"\n📢 [알림] 창고에 이미 《{target_book}》 영상 완제품이 존재합니다!")
                overwrite_choice = input("👉 어떻게 할까요? (새 번호로 추가 생성=1 / 취소하고 기존 파일 보존=2): ").strip()
                if overwrite_choice == '2':
                    print("🛑 [작업 중단] 기존 파일의 안전을 위해 공장 가동을 멈춥니다.")
                    exit()
                counter = 1
                while True:
                    unique_base_name = f"{target_book}_shorts_{counter}"
                    if not os.path.exists(os.path.join(video_dir, f"{unique_base_name}.mp4")):
                        break
                    counter += 1
            else:
                unique_base_name = f"{target_book}_shorts"
            
            final_script_name = f"{unique_base_name}_prompts.txt"
            final_video_name = f"{unique_base_name}.mp4"
            
            print(f"✨ [공정 통합] 이번 생산 라인은 [{unique_base_name}] 세트로 통합 출하됩니다.")
            print("--------------------------------------------------")

            factory_output = generate_shorts_source(target_book, is_test_mode)
            
            # 🎯 [메모장 기록 공정] 쪼개진 3단 분할 대본을 알아보기 쉽도록 메모장에 정리 기록
            if factory_output and not is_test_mode:
                script_path = os.path.join("outputs", "scripts", final_script_name)
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(f"============ 《{target_book}》 쇼츠 자재 세트 ({unique_base_name}) ============\n\n")
                    f.write(f"[📜 1구간 대본 (0~10초)]\n{factory_output.get('script_1', '')}\n\n")
                    f.write(f"[📜 2구간 대본 (10~20초)]\n{factory_output.get('script_2', '')}\n\n")
                    f.write(f"[📜 3구간 대본 (20~30초)]\n{factory_output.get('script_3', '')}\n\n")
                    f.write("============================================================================")
                print(f"📄 [대본 동기화] 영상과 짝을 이루는 분할 대본 입고 완료 ➡️ {script_path}")

            # 🎯 [완제품 빌드 공정] 대본 패키지와 비디오 이름 전달
            if factory_output:
                success = build_video_with_subtitles(factory_output, final_video_name)
                if success:
                    print("==================================================")
                    print(f"🏁 [공장 가동 완료] 세트 완제품 안전 입고 완료!")
                    print(f"📦 영상 창고: outputs/videos/{final_video_name}")
                    print("==================================================")
    else:
        print("❌ 잘못된 번호를 선택하셨습니다.")
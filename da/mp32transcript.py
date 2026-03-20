import whisper
import torch
import os
from whisper.utils import get_writer

def transcribe_bluey():
    # 1. Setup paths
    audio_path = r"C:\Users\michael\Documents\Parlay\da\Suspekt - kinky fætter.mp3"
    output_dir = os.path.dirname(audio_path)
    
    # 2. Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- [STATUS] Device detected: {device.upper()} ---")
    
    if device == "cuda":
        print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ GPU NOT DETECTED. Re-run the pip install command above.")

    # 3. Load Model
    print("--- [STEP 1/2] Loading 'medium' model into VRAM... ---")
    model = whisper.load_model("medium", device=device)

    # 4. Transcribe with progress
    print(f"--- [STEP 2/2] Transcribing {os.path.basename(audio_path)} ---")
    print("Live Progress Below:")
    
    result = model.transcribe(
        audio_path, 
        language="da", 
        fp16=True,      # This will now work without warnings
        verbose=True    # This prints the text to your screen as it's processed
    )

    # 5. Export SRT (The Chris Brown/Rihanna format)
    print("\n--- [FINAL] Saving SRT file... ---")
    writer = get_writer("srt", output_dir)
    
    # Standard subtitle settings for easier reading
    writer(result, audio_path, {"max_line_width": 42, "max_line_count": 2})
    
    print(f"✅ Success! File saved at: {os.path.join(output_dir, 'Suspekt - kinky fætter.srt')}")

if __name__ == "__main__":
    transcribe_bluey()
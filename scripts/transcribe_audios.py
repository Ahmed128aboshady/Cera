import whisper
import os

model = whisper.load_model('base')

f1 = r"C:\Users\Video Editor\Downloads\New folder (12)\WhatsApp Ptt 2026-08-22 at 8.12.10 PM.ogg"
f2 = r"C:\Users\Video Editor\Downloads\New folder (12)\WhatsApp Ptt 2026-08-22 at 8.15.19 PM.ogg"

res1 = model.transcribe(f1, language='ar')
res2 = model.transcribe(f2, language='ar')

out_path = r"C:\Users\Video Editor\.gemini\antigravity\brain\8fd5d34c-5bb2-41a0-b7fe-a3deb14e778c\scratch\voice_transcripts.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("=== التسجيل الصوتي الأول (8.12 PM) ===\n")
    f.write(res1['text'] + "\n\n")
    f.write("=== التسجيل الصوتي الثاني (8.15 PM) ===\n")
    f.write(res2['text'] + "\n")

print("Transcription saved successfully to voice_transcripts.txt")

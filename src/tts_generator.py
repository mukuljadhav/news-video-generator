import os
import numpy as np
import soundfile as sf


class TTSGenerator:
    def __init__(self, voice_style: str = "female"):
        self.voice_style = voice_style
        self.use_gtts = True
        
        print("🎤 Initializing Text-to-Speech engine...")
        print("   Using gTTS (Google Text-to-Speech)")
        print("✅ TTS engine ready")
    
    def generate_speech(self, text: str, output_path: str) -> str:
        print(f"\n🎙️  Generating speech...")
        print(f"   Text length: {len(text)} characters")
        print(f"   Estimated duration: {len(text.split()) / 2.5:.1f} seconds")
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
            print(f"✅ Speech generated: {output_path}")
            
            return output_path
        
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
            print("   Attempting fallback method...")
            return self._generate_fallback(text, output_path)
    
    def _generate_fallback(self, text: str, output_path: str) -> str:
        try:
            import pyttsx3
            
            print("   Using pyttsx3 as fallback TTS")
            
            engine = pyttsx3.init()
            
            voices = engine.getProperty('voices')
            if self.voice_style == "male" and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
            elif self.voice_style == "female" and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            print(f"✅ Fallback speech generated: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"❌ Fallback TTS also failed: {e}")
            return self._generate_silent_audio(output_path, duration=30)
    
    def _generate_silent_audio(self, output_path: str, duration: int = 30) -> str:
        print(f"   Generating {duration}s silent audio as last resort")
        
        sample_rate = 22050
        audio = np.zeros(int(sample_rate * duration))
        
        sf.write(output_path, audio, sample_rate)
        
        return output_path
    
    def get_audio_duration(self, audio_path: str) -> float:
        try:
            import librosa
            audio, sr = librosa.load(audio_path)
            duration = librosa.get_duration(y=audio, sr=sr)
            return duration
        except:
            try:
                audio, sr = sf.read(audio_path)
                duration = len(audio) / sr
                return duration
            except:
                return 30.0


class AdvancedTTSGenerator:
    def __init__(self, voice_style: str = "female"):
        self.voice_style = voice_style
        
        print("🎤 Initializing Advanced TTS (gTTS)...")
        print("   Using Google Text-to-Speech API")
        print("✅ Advanced TTS ready")
    
    def generate_speech(self, text: str, output_path: str) -> str:
        print(f"\n🎙️  Generating high-quality speech...")
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
            print(f"✅ High-quality speech generated: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"❌ Error with advanced TTS: {e}")
            fallback = TTSGenerator(self.voice_style)
            return fallback.generate_speech(text, output_path)


if __name__ == "__main__":
    tts = TTSGenerator(voice_style="female")
    
    sample_text = """
    Tesla CEO Elon Musk has announced ambitious plans for the company's future. 
    The electric vehicle manufacturer continues to push boundaries in innovation 
    and sustainable transportation.
    """
    
    output_file = "./output/test_speech.wav"
    tts.generate_speech(sample_text, output_file)
    
    duration = tts.get_audio_duration(output_file)
    print(f"\n📊 Audio duration: {duration:.2f} seconds")

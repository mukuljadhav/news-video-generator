from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import os
from typing import List, Tuple
import math
import platform


class VideoCreator:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.resolution = (1920, 1080)
        self.fps = 24
        
        system = platform.system()
        if system == "Darwin":
            self.font = r"/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            self.fallback_fonts = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                r"/System/Library/Fonts/Supplemental/Arial Black.ttf"
            ]
        elif system == "Windows":
            self.font = "C:\\Windows\\Fonts\\arialbd.ttf"
            self.fallback_fonts = ["C:\\Windows\\Fonts\\arial.ttf", "Arial"]
        else:
            self.font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            self.fallback_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "DejaVu-Sans"
            ]
    
    def create_video(
        self,
        script: str,
        audio_path: str,
        image_paths: List[str],
        output_filename: str,
        title_text: str = None
    ) -> str:
        print(f"\n🎬 Creating video...")
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        print(f"   Audio duration: {total_duration:.2f}s")
        print(f"   Using {len(image_paths)} images")
        
        video_clips = self._create_image_clips(image_paths, total_duration)
        
        if title_text:
            video_clips = self._add_title_overlay(video_clips, title_text)
        
        script_lines = self._split_script_for_captions(script)
        video_clips = self._add_captions(video_clips, script_lines, total_duration)
        
        final_video = CompositeVideoClip(video_clips, size=self.resolution)
        final_video = final_video.with_audio(audio_clip)
        final_video = final_video.with_duration(total_duration)
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"   Rendering video (this may take a few minutes)...")
        
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        
        audio_clip.close()
        final_video.close()
        
        print(f"✅ Video created: {output_path}")
        print(f"   Duration: {total_duration:.2f}s")
        print(f"   Size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        
        return output_path
    
    def _create_image_clips(self, image_paths: List[str], total_duration: float) -> List[ImageClip]:
        if not image_paths:
            raise ValueError("No images provided for video creation")
        
        duration_per_image = total_duration / len(image_paths)
        
        clips = []
        current_time = 0
        
        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                print(f"   ⚠️  Image not found: {image_path}, skipping")
                continue
            
            clip = (ImageClip(image_path)
                   .with_duration(duration_per_image)
                   .with_start(current_time)
                   .resized(self.resolution)
                   .with_position('center'))
            
            clips.append(clip)
            current_time += duration_per_image
        
        return clips
    
    def _add_title_overlay(self, clips: List, title_text: str) -> List:
        try:
            for font in [self.font] + self.fallback_fonts:
                try:
                    title_clip = (TextClip(
                        text=title_text,
                        font_size=70,
                        color='white',
                        font=font,
                        text_align='center',
                        size=(self.resolution[0] - 200, None)
                    )
                    .with_position(('center', 100))
                    .with_duration(5)
                    .with_start(0))
                    
                    clips.append(title_clip)
                    break
                except Exception as font_error:
                    if font == self.fallback_fonts[-1]:
                        raise font_error
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Could not create title overlay: {e}")
        
        return clips
    
    def _split_script_for_captions(self, script: str, words_per_caption: int = 8) -> List[str]:
        words = script.split()
        
        lines = []
        for i in range(0, len(words), words_per_caption):
            line = ' '.join(words[i:i + words_per_caption])
            lines.append(line)
        
        return lines
    
    def _add_captions(self, clips: List, caption_lines: List[str], total_duration: float) -> List:
        if not caption_lines:
            return clips
        
        duration_per_caption = total_duration / len(caption_lines)
        
        for i, line in enumerate(caption_lines):
            try:
                for font in [self.font] + self.fallback_fonts:
                    try:
                        caption = (TextClip(
                            text=line,
                            font_size=40,
                            color='white',
                            font=font,
                            text_align='center',
                            bg_color='black',
                            size=(self.resolution[0] - 300, None),
                            method='caption'
                        )
                        .with_position(('center', self.resolution[1] - 200))
                        .with_duration(duration_per_caption)
                        .with_start(i * duration_per_caption))
                        
                        clips.append(caption)
                        break
                    except Exception as font_error:
                        if font == self.fallback_fonts[-1]:
                            raise font_error
                        continue
            
            except Exception as e:
                print(f"   ⚠️  Could not create caption {i+1}: {e}")
                continue
        
        return clips
    
    def create_simple_video(
        self,
        audio_path: str,
        image_paths: List[str],
        output_filename: str
    ) -> str:
        print(f"\n🎬 Creating simple video without captions...")
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        duration_per_image = total_duration / len(image_paths)
        
        video_clips = []
        for image_path in image_paths:
            clip = (ImageClip(image_path)
                   .with_duration(duration_per_image)
                   .resized(self.resolution))
            video_clips.append(clip)
        
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.with_audio(audio_clip)
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        audio_clip.close()
        final_video.close()
        
        print(f"✅ Simple video created: {output_path}")
        return output_path


class AdvancedVideoCreator(VideoCreator):
    def create_professional_video(
        self,
        script: str,
        audio_path: str,
        image_paths: List[str],
        output_filename: str,
        title_text: str = None,
        subtitle_style: str = "bottom"
    ) -> str:
        print(f"\n🎬 Creating professional video with advanced effects...")
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        clips = []
        
        background_clips = self._create_ken_burns_clips(image_paths, total_duration)
        clips.extend(background_clips)
        
        if title_text:
            title_clip = self._create_animated_title(title_text)
            if title_clip:
                clips.append(title_clip)
        
        caption_clips = self._create_word_by_word_captions(script, total_duration)
        clips.extend(caption_clips)
        
        final_video = CompositeVideoClip(clips, size=self.resolution)
        final_video = final_video.with_audio(audio_clip)
        final_video = final_video.with_duration(total_duration)
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"   Rendering professional video...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            logger=None
        )
        
        audio_clip.close()
        final_video.close()
        
        print(f"✅ Professional video created: {output_path}")
        return output_path
    
    def _create_ken_burns_clips(self, image_paths: List[str], total_duration: float) -> List:
        duration_per_image = total_duration / len(image_paths)
        
        clips = []
        current_time = 0
        
        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                continue
            
            clip = ImageClip(image_path).with_duration(duration_per_image)
            
            zoom_factor = 1.2 if i % 2 == 0 else 0.8
            
            clip = (clip
                   .resized(lambda t: 1 + (zoom_factor - 1) * t / duration_per_image)
                   .with_position('center')
                   .with_start(current_time))
            
            clips.append(clip)
            current_time += duration_per_image
        
        return clips
    
    def _create_animated_title(self, title_text: str):
        try:
            title = (TextClip(
                text=title_text,
                font_size=80,
                color='white',
                font='Arial-Bold',
                text_align='center'
            )
            .with_position(('center', 'center'))
            .with_duration(4)
            .with_start(0))
            
            return title
        except Exception as e:
            print(f"   ⚠️  Could not create animated title: {e}")
            return None
    
    def _create_word_by_word_captions(self, script: str, total_duration: float) -> List:
        words = script.split()
        time_per_word = total_duration / len(words)
        
        caption_clips = []
        
        words_per_group = 5
        
        for i in range(0, len(words), words_per_group):
            group = ' '.join(words[i:i+words_per_group])
            start_time = i * time_per_word
            duration = words_per_group * time_per_word
            
            try:
                caption = (TextClip(
                    text=group,
                    font_size=45,
                    color='white',
                    font='Arial-Bold',
                    text_align='center',
                    bg_color='rgba(0,0,0,0.6)',
                    size=(self.resolution[0] - 400, None)
                )
                .with_position(('center', self.resolution[1] - 180))
                .with_start(start_time)
                .with_duration(duration))
                
                caption_clips.append(caption)
            
            except Exception as e:
                continue
        
        return caption_clips


if __name__ == "__main__":
    creator = VideoCreator()
    
    sample_images = ["./data/images/image_0.jpg", "./data/images/image_1.jpg"]
    sample_audio = "./output/test_speech.wav"
    sample_script = "This is a test video with captions showing how the video creator works."
    
    creator.create_video(
        script=sample_script,
        audio_path=sample_audio,
        image_paths=sample_images,
        output_filename="test_video.mp4",
        title_text="Test Video"
    )

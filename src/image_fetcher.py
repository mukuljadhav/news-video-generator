import requests
from typing import List, Dict
import os
import time


class ImageFetcher:
    def __init__(self, cache_dir: str = "./data/images"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.unsplash_api = "https://source.unsplash.com"
        self.pexels_api = "https://images.pexels.com/photos"
        self.picsum_api = "https://picsum.photos"
    
    def fetch_images(self, keywords: List[str], num_images: int = 5) -> List[str]:
        print(f"\n🖼️  Fetching {num_images} background images...")
        print(f"   Keywords: {', '.join(keywords[:3])}")
        
        image_paths = []
        
        for i in range(num_images):
            keyword = keywords[i % len(keywords)] if keywords else "news"
            
            image_path = self._download_unsplash_image(keyword, i)
            
            if not image_path:
                image_path = self._download_picsum_image(i)
            
            if image_path:
                image_paths.append(image_path)
            else:
                placeholder = self._create_placeholder_image(i)
                if placeholder:
                    image_paths.append(placeholder)
        
        if not image_paths:
            raise Exception("Failed to fetch or create any images")
        
        print(f"✅ Fetched {len(image_paths)} images")
        return image_paths
    
    def _download_unsplash_image(self, keyword: str, index: int) -> str | None:
        try:
            keyword_clean = keyword.replace(' ', '-').lower()
            
            url = f"{self.unsplash_api}/1920x1080/?{keyword_clean}&sig={index}"
            
            response = requests.get(url, timeout=10, stream=True, allow_redirects=True)
            
            if response.status_code == 503:
                print(f"   ⚠️  Unsplash API unavailable (503) for {keyword}, using placeholder")
                return None
            
            response.raise_for_status()
            
            image_path = os.path.join(self.cache_dir, f"image_{index}_{keyword_clean[:20]}.jpg")
            
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   ✓ Downloaded: {keyword} → {os.path.basename(image_path)}")
            
            time.sleep(0.5)
            
            return image_path
        
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Unsplash failed for {keyword}, using placeholder")
            return None
        except Exception as e:
            print(f"   ⚠️  Failed to download {keyword}: {e}")
            return None
    
    def _download_picsum_image(self, index: int) -> str | None:
        try:
            url = f"{self.picsum_api}/1920/1080?random={index}"
            
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            image_path = os.path.join(self.cache_dir, f"picsum_image_{index}.jpg")
            
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   ✓ Fallback image from Picsum")
            return image_path
        
        except Exception as e:
            return None
    
    def _create_placeholder_image(self, index: int) -> str | None:
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (1920, 1080), color=(30, 50, 80))
            
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
                except:
                    font = ImageFont.load_default()
            
            text = "NEWS"
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            position = ((1920 - text_width) // 2, (1080 - text_height) // 2)
            draw.text(position, text, fill=(255, 255, 255), font=font)
            
            image_path = os.path.join(self.cache_dir, f"placeholder_{index}.jpg")
            img.save(image_path, quality=85)
            
            return image_path
        
        except Exception as e:
            print(f"   ⚠️  Failed to create placeholder: {e}")
            return None
    
    def clear_cache(self):
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir)
            print("🗑️  Image cache cleared")


if __name__ == "__main__":
    fetcher = ImageFetcher()
    keywords = ["technology", "innovation", "business", "future"]
    images = fetcher.fetch_images(keywords, num_images=3)
    
    print(f"\n📁 Images saved:")
    for img in images:
        print(f"   {img}")

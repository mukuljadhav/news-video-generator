import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict
import json
import re
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class ContentAnalyzer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn", use_quantized: bool = False):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🤖 Loading language model: {model_name}")
        print(f"   Device: {self.device}")
        
        if "bart" in model_name.lower():
            print(f"   ⚡ Using BART-Large-CNN (400M params, ~1.6GB) - Professional-grade news summarization")
        elif "flan-t5" in model_name.lower():
            print(f"   ⚡ Using FLAN-T5 (250M params, ~1GB) - Instruction-tuned summarization")
        else:
            print(f"   ⚡ Using {model_name}")
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        
        if self.device == "cpu":
            self.model = self.model.to(self.device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print("✅ Model loaded successfully")
    
    def analyze_articles(self, articles: List[Dict], perspective: str, max_tokens: int = 2000) -> Dict:
        articles_text = self._prepare_articles_text(articles)
        
        print(f"\n🔍 Analyzing {len(articles)} articles with perspective: '{perspective}'")
        
        prompt = self._create_analysis_prompt(articles_text, perspective)
        
        response = self._generate_response(prompt, max_tokens=max_tokens)
        
        analysis = self._parse_analysis(response)
        
        return analysis
    
    def _prepare_articles_text(self, articles: List[Dict], max_length: int = 4000) -> str:
        combined_text = []
        
        for article in articles[:15]:
            content = article.get('content', '')[:800]
            if len(content) > 100:
                combined_text.append(content)
        
        full_text = " ".join(combined_text)
        
        return full_text[:max_length]
    
    def _create_analysis_prompt(self, articles_text: str, perspective: str) -> str:
        prompt = articles_text
        return prompt
    
    def _generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=400,
                min_length=150,
                length_penalty=2.0,
                num_beams=6,
                early_stopping=True,
                no_repeat_ngram_size=3
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return response.strip()
    
    def _parse_analysis(self, response: str) -> Dict:
        script = self._deduplicate_sentences(response)
        
        try:
            json_match = re.search(r'\{.*\}', script, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                if 'script' in analysis:
                    analysis['script'] = self._deduplicate_sentences(analysis['script'])
            else:
                analysis = {
                    "script": script,
                    "key_points": self._extract_key_points(script),
                    "sources_used": [],
                    "search_keywords": []
                }
        except json.JSONDecodeError:
            analysis = {
                "script": script,
                "key_points": self._extract_key_points(script),
                "sources_used": [],
                "search_keywords": []
            }
        
        if not analysis.get("search_keywords"):
            analysis["search_keywords"] = self._extract_keywords(analysis.get("script", ""))
        
        print(f"✅ Generated script with {len(analysis.get('key_points', []))} key points")
        
        return analysis
    
    def _deduplicate_sentences(self, text: str) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        unique_sentences = []
        seen_sentences = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            normalized = sentence.lower().strip('.,!? ')
            
            if normalized not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(normalized)
        
        return ' '.join(unique_sentences)
    
    def _extract_key_points(self, text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        key_points = [s.strip() for s in sentences if len(s.strip()) > 20]
        return key_points[:7]
    
    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        common_words = {'The', 'This', 'That', 'These', 'Those', 'According', 'However', 'Moreover'}
        keywords = [w for w in words if w not in common_words]
        
        return list(set(keywords))[:5]
    
    def generate_simple_script(self, articles: List[Dict], perspective: str, target_duration: int = 60) -> str:
        print(f"\n📝 Generating simplified script for perspective: '{perspective}'")
        
        relevant_content = []
        
        for article in articles:
            content = f"{article['title']}. {article['content']}"
            relevant_content.append(content)
        
        combined_text = " ".join(relevant_content)[:3000]
        
        words_per_second = 2.5
        target_words = int(target_duration * words_per_second)
        
        prompt = f"""Summarize the following articles focusing on {perspective}. Write a detailed summary with approximately {target_words} words.

Articles:
{combined_text}

Summary:"""
        
        script = self._generate_response(prompt, max_tokens=800)
        script = self._deduplicate_sentences(script)
        
        words = script.split()
        if len(words) > target_words * 1.2:
            script = " ".join(words[:int(target_words * 1.1)])
        
        print(f"✅ Generated {len(script.split())} word script")
        
        return script


if __name__ == "__main__":
    sample_articles = [
        {
            "title": "Tesla Stock Rises on Strong Q4 Earnings",
            "content": "Tesla reported strong quarterly earnings, beating analyst expectations. CEO Elon Musk announced plans for expansion.",
            "source": "Reuters"
        },
        {
            "title": "Concerns Raised Over Tesla Autopilot Safety",
            "content": "Safety regulators have opened an investigation into Tesla's autopilot feature following several incidents.",
            "source": "BBC"
        }
    ]
    
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze_articles(sample_articles, "positive views")
    
    print("\n📊 Analysis Results:")
    print(json.dumps(analysis, indent=2))

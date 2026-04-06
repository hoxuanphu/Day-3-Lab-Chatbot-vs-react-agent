import os
import sys
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Đảm bảo root dự án nằm trong PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows console encoding for Vietnamese + emoji
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

from src.agent.rag_baseline import RAGBaselineAgent
from src.agent.agent import HistoryAgent
from src.tools.tool_registry import ToolRegistry
from src.core.gemini_provider import GeminiProvider

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Lớp wrapper để đếm Token và Latency từ LLM
class ProxyLLM:
    def __init__(self, provider: GeminiProvider):
        self.provider = provider
        self.reset()

    def reset(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.calls = 0

    def generate(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        result = self.provider.generate(prompt, system_prompt)
        usage = result.get("usage", {})
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        self.total_tokens += usage.get("total_tokens", 0)
        self.calls += 1
        return result

def run_eval():
    questions = [
        "Tổng thống Mỹ nào đã bị ám sát vào ngày 22-11-1963?",
        "Trong 3 năm (1965-1968), tổng số vốn đầu tư vào công nghiệp địa phương ở miền Bắc tăng gấp bao nhiêu lần so với ba năm trước chiến tranh phá hoại?",
        "Tại sao Đảng và Chính phủ lại chủ trương tập trung phát triển công nghiệp địa phương (quy mô vừa và nhỏ) trong những năm 1965-1968 thay vì tập trung vào các nhà máy lớn ở Trung ương?",
        "Hãy đối chiếu và phân tích sự khác biệt về số lượng xí nghiệp và nguồn vốn đầu tư giữa hai mảng: 'Công nghiệp sản xuất tư liệu sản xuất (nhóm A)' và 'Công nghiệp sản xuất tư liệu tiêu dùng (nhóm B)' trong giai đoạn 1965 - 1968. Dữ liệu này phản ánh điều gì về đường lối kinh tế của Đảng?",
        "thịt bò có vị gì"
    ]

    results = []
    
    # Khởi tạo providers và registry (dùng chung cho cả 2 mode)
    base_llm = GeminiProvider(model_name="gemini-2.5-flash")
    proxy_llm = ProxyLLM(base_llm)
    tool_registry = ToolRegistry(data_path="data/data.md")

    # Khởi tạo Agents
    baseline_agent = RAGBaselineAgent(llm=proxy_llm, data_path="data/data.md", use_semantic=False)
    history_agent = HistoryAgent(llm=proxy_llm, tool_registry=tool_registry)

    modes = ["baseline", "agent"]

    print("\n" + "="*80)
    print("BẮT ĐẦU ĐÁNH GIÁ CHẤT LƯỢNG (EVALUATION)")
    print("="*80)

    for q_idx, question in enumerate(questions, 1):
        print(f"\n[Q{q_idx}] {question}")
        
        for mode in modes:
            print(f"  -> Đang chạy mode: {mode.upper()}...", end="", flush=True)
            
            proxy_llm.reset()
            start_time = time.time()
            error = None
            answer = ""
            loops = 0

            try:
                if mode == "baseline":
                    answer = baseline_agent.run(question)
                    loops = 1 
                else:
                    answer = history_agent.run(question)
                    loops = proxy_llm.calls 

            except Exception as e:
                error = str(e)
                print(f" [LỖI: {error}]")
            
            elapsed = time.time() - start_time
            print(f" Hoàn thành ({elapsed:.2f}s)")

            results.append({
                "id": q_idx,
                "mode": mode,
                "latency": round(elapsed, 2),
                "loops": loops,
                "tokens": proxy_llm.total_tokens,
                "error": "None" if not error else error,
                "answer": answer[:80].replace("\n", " ") + "..."
            })

    # Hiển thị kết quả
    print("\n" + "="*80)
    print("KẾT QUẢ SO SÁNH")
    print("="*80)
    
    if HAS_PANDAS:
        df = pd.DataFrame(results)
        print(df[["id", "mode", "latency", "loops", "tokens", "error"]])
        
        print("\n--- Summary (Average) ---")
        summary = df.groupby("mode").agg({
            "latency": "mean",
            "loops": "mean",
            "tokens": "mean"
        }).round(2)
        print(summary)
        
        df.to_csv("data/evaluation_results.csv", index=False)
    else:
        # Simple text formatting if pandas is not available
        header = f"{'ID':<4} | {'Mode':<10} | {'Latency':<8} | {'Loops':<6} | {'Tokens':<8} | {'Error'}"
        print(header)
        print("-" * len(header))
        for r in results:
            print(f"{r['id']:<4} | {r['mode']:<10} | {r['latency']:<8.2f} | {r['loops']:<6} | {r['tokens']:<8} | {r['error']}")
        
        # Save to JSON as fallback
        with open("data/evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Kết quả đã được lưu tại thư mục data/")

if __name__ == "__main__":
    run_eval()

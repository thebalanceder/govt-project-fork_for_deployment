#!/usr/bin/env python3
"""
医疗资料爬虫：常见疾病 + 医患沟通
爬取 MedlinePlus、PMC 等权威来源，输出 markdown 供知识库导入。
"""

import re
import time
import html
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": "HealthMate-Crawler/1.0 (educational; knowledge-base)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en,zh;q=0.9",
}
# 请求间隔（秒），避免对目标站造成压力
DELAY = 1.5
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge_base"
REQUEST_TIMEOUT = 30


# ========== 常见疾病（MedlinePlus 英文） ==========
DISEASE_URLS = [
    # 呼吸道 / 感染
    ("commoncold", "https://medlineplus.gov/commoncold.html", "感冒"),
    ("flu", "https://medlineplus.gov/flu.html", "流感"),
    ("fever", "https://medlineplus.gov/fever.html", "发热"),
    ("cough", "https://medlineplus.gov/cough.html", "咳嗽"),
    ("sorethroat", "https://medlineplus.gov/sorethroat.html", "咽喉痛"),
    ("pneumonia", "https://medlineplus.gov/pneumonia.html", "肺炎"),
    ("acutebronchitis", "https://medlineplus.gov/acutebronchitis.html", "急性支气管炎"),
    ("asthma", "https://medlineplus.gov/asthma.html", "哮喘"),
    # 消化
    ("diarrhea", "https://medlineplus.gov/diarrhea.html", "腹泻"),
    ("constipation", "https://medlineplus.gov/constipation.html", "便秘"),
    ("heartburn", "https://medlineplus.gov/heartburn.html", "烧心"),
    ("nausea", "https://medlineplus.gov/nauseaandvomiting.html", "恶心呕吐"),
    # 疼痛与常见症状
    ("headache", "https://medlineplus.gov/headache.html", "头痛"),
    ("backpain", "https://medlineplus.gov/backpain.html", "背痛"),
    ("stomachache", "https://medlineplus.gov/indigestion.html", "消化不良/腹痛"),
    ("pain", "https://medlineplus.gov/pain.html", "疼痛"),
    # 慢病
    ("diabetes", "https://medlineplus.gov/diabetes.html", "糖尿病"),
    ("hypertension", "https://medlineplus.gov/highbloodpressure.html", "高血压"),
    # 皮肤
    ("rash", "https://medlineplus.gov/rashes.html", "皮疹"),
    # 心理
    ("anxiety", "https://medlineplus.gov/anxiety.html", "焦虑"),
    ("depression", "https://medlineplus.gov/depression.html", "抑郁"),
    ("insomnia", "https://medlineplus.gov/insomnia.html", "失眠"),
    # 其他常见
    ("allergies", "https://medlineplus.gov/allergy.html", "过敏"),
    ("urinarytractinfection", "https://medlineplus.gov/urinarytractinfections.html", "尿路感染"),
]

# 医患沟通相关 (slug, url, 中文名, 是否用 PMC 解析)
PATIENT_COMMUNICATION_URLS = [
    ("doctor-patient-communication-review", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3096184/", "医患沟通综述", True),
    ("ahrq-physician-communication", "https://www.ahrq.gov/cahps/quality-improvement/improvement-guide/6-strategies-for-improving/communication/strategy6gtraining.html", "AHRQ 医生沟通技能", False),
    ("shared-decision-making", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4046525/", "医患共同决策", True),
]


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name)[:80]


def fetch(url: str) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print(f"  [请求失败] {url}: {e}")
        return None


def parse_medlineplus(html_text: str, url: str) -> str:
    """解析 MedlinePlus 健康主题页，提取 Summary 等核心内容"""
    soup = BeautifulSoup(html_text, "html.parser")

    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else ""

    # 只提取 Summary 下的 What is / What causes / symptoms / treatments / Can ... be prevented
    summary_pattern = re.compile(
        r"^(What is|What causes|What are the (symptoms|treatments)|Can .+ be prevented)",
        re.I,
    )
    sections = []
    in_summary = False
    for h in soup.find_all(["h2", "h3"]):
        text = h.get_text(strip=True)
        if text == "Summary":
            in_summary = True
            continue
        if in_summary and not summary_pattern.match(text):
            break  # 离开 Summary 区
        if summary_pattern.match(text):
            block = []
            for s in h.find_all_next():
                if s.name in ("h2", "h3", "h4") and s != h:
                    break
                if s.name == "p":
                    block.append(s.get_text(strip=True))
                elif s.name == "ul":
                    for li in s.find_all("li"):
                        t = li.get_text(strip=True)
                        if t and len(t) > 10:
                            block.append(f"- {t}")
            if block:
                sections.append(f"## {text}\n\n" + "\n\n".join(block))

    if not sections:
        main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|main"))
        if main:
            for p in main.find_all("p")[:15]:
                t = p.get_text(strip=True)
                if len(t) > 30 and "skip" not in t.lower():
                    sections.append(t)

    body = "\n\n".join(sections) if sections else ""
    return f"""# {title_text}

来源: {url}

{body}

---
*以上内容来自 MedlinePlus，供健康科普参考，不替代专业医疗建议。*
"""


def parse_generic_article(html_text: str, url: str, title_override: str = "") -> str:
    """通用文章解析，适用于 AHRQ、PSNet 等"""
    soup = BeautifulSoup(html_text, "html.parser")
    title = title_override or (soup.find("h1") or soup.find("title"))
    title = title.get_text(strip=True) if hasattr(title, "get_text") else str(title)[:200]

    paras = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if len(t) > 50:
            paras.append(t)
    body = "\n\n".join(paras[:40])
    return f"""# {title}

来源: {url}

{body}

---
*以上内容供医学教育与健康科普参考。*
"""


def parse_pmc(html_text: str, url: str) -> str:
    """解析 PMC 文章页，提取正文"""
    soup = BeautifulSoup(html_text, "html.parser")

    title_el = soup.find("h1") or soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""

    paras = []
    for div in soup.find_all("div", class_=re.compile("article-body|abstract|sec")):
        for p in div.find_all("p"):
            t = p.get_text(strip=True)
            if len(t) > 40:
                paras.append(t)

    if not paras:
        for p in soup.find_all("p"):
            t = p.get_text(strip=True)
            if len(t) > 60 and "copyright" not in t.lower() and "pmc" not in t.lower():
                paras.append(t)

    body = "\n\n".join(paras[:50])
    return f"""# {title}

来源: {url}

{body}

---
*以上内容来自 PubMed Central，供医学教育与研究参考。*
"""


def crawl_diseases():
    diseases_dir = OUTPUT_DIR / "diseases"
    diseases_dir.mkdir(parents=True, exist_ok=True)

    for item in DISEASE_URLS:
        slug, url = item[0], item[1]
        name_cn = item[2] if len(item) > 2 else slug
        print(f"[疾病] {name_cn} - {url}")
        r = fetch(url)
        if not r:
            continue
        content = parse_medlineplus(r.text, url)
        fname = sanitize_filename(slug) + ".md"
        (diseases_dir / fname).write_text(content, encoding="utf-8")
        time.sleep(DELAY)


def crawl_patient_communication():
    comm_dir = OUTPUT_DIR / "patient_communication"
    comm_dir.mkdir(parents=True, exist_ok=True)

    for item in PATIENT_COMMUNICATION_URLS:
        slug, url, name = item[0], item[1], item[2]
        use_pmc = item[3] if len(item) > 3 else "pmc" in url.lower()
        print(f"[医患沟通] {name} - {url}")
        r = fetch(url)
        if not r:
            continue
        content = parse_pmc(r.text, url) if use_pmc else parse_generic_article(r.text, url, name)
        fname = sanitize_filename(slug) + ".md"
        (comm_dir / fname).write_text(content, encoding="utf-8")
        time.sleep(DELAY)


def main():
    print("医疗资料爬虫 - 常见疾病 + 医患沟通")
    print(f"输出目录: {OUTPUT_DIR}\n")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    crawl_diseases()
    print()
    crawl_patient_communication()

    print("\n完成。文件已保存至 knowledge_base/")


if __name__ == "__main__":
    main()

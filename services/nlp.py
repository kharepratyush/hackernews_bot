import asyncio
import io
import pprint
import re
from typing import Literal

import aiohttp
import requests
from bs4 import BeautifulSoup
from langchain.schema import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

from config import settings


class NLPService:
    def __init__(self):
        self.client = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_URL,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    async def classify_topic(self, text: str) -> str:

        class DocumentClassModel(BaseModel):
            text_class: Literal[
                "Machine Learning",
                "Artificial Intelligence",
                "Deep Learning",
                "Reinforcement Learning",
                "Natural Language Processing",
                "Computer Vision",
                "Data Science",
                "Statistics",
                "AI Agents & Tools",
                "Big Data & Data Engineering",
                "Business Intelligence & Analytics",
                "Programming",
                "Compiler & Language Design",
                "Algorithms & Data Structures",
                "Frameworks & Libraries",
                "Testing & QA",
                "DevOps & Infrastructure",
                "CI/CD & Deployment",
                "Version Control & Collaboration",
                "Operating Systems",
                "Distributed Systems",
                "Networking & Protocols",
                "Cloud Computing & Virtualization",
                "Containers & Orchestration (Docker, Kubernetes)",
                "Information Security",
                "Cryptography",
                "Privacy & Compliance",
                "Web Development",
                "API Design & Microservices",
                "Mobile Development",
                "Blockchain Protocols",
                "Decentralized Apps (dApps)",
                "Cryptocurrency & DeFi",
                "Hardware Design & Architecture",
                "Internet of Things (IoT)",
                "Robotics & Embedded Systems",
                "Startup Culture & Entrepreneurship",
                "Product Management",
                "Venture Capital & Fundraising",
                "Growth & Marketing",
                "Mathematics",
                "Physics",
                "Biology & Chemistry",
                "Academic Research & Papers",
                "User Experience (UX)",
                "User Interface (UI)",
                "Visual & Interaction Design",
                "Career Advice & Hiring",
                "Remote Work & Collaboration Tools",
                "Time Management & Productivity Hacks",
                "Game Development",
                "VR/AR",
                "Interactive Media",
                "Tech Policy & Regulation",
                "Ethics & Social Impact",
                "Privacy Debates",
                "Show HN",
                "Ask HN",
                "Jobs & Hiring",
                "YC News & Announcements",
                "Other",
            ] = Field(
                ...,
                description='Class of the document to the question. Use "Other" if none of the above apply.',
            )

        prompt = (
            "Classify this title into text class based on technology; respond with exactly one label."
            f"\n\nDetails: {text}"
        )

        msg = HumanMessage(content=prompt)
        resp: AIMessage = await self.client.with_structured_output(
            DocumentClassModel
        ).ainvoke([msg])
        return resp.text_class.strip()

    async def _extract_text_html(self, url: str, verify_ssl: bool = True) -> str:
        connector = aiohttp.TCPConnector(ssl=verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)

    async def _extract_text_pdf(self, url: str, verify_ssl: bool = True) -> str:
        connector = aiohttp.TCPConnector(ssl=verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=20) as resp:
                resp.raise_for_status()
                content = await resp.read()
        reader = PdfReader(io.BytesIO(content))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)

    def _clean_text(self, text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    async def summarize_article(self, url: str) -> str:
        verify_ssl = False  # Add more domains as needed
        try:
            if url.lower().endswith(".pdf"):
                text = await self._extract_text_pdf(url, verify_ssl=verify_ssl)
            else:
                text = await self._extract_text_html(url, verify_ssl=verify_ssl)

            snippet = text[:3000]
            prompt = f"Summarize the following in three sentences:\n\n{snippet}"
            msg = HumanMessage(content=prompt)
            resp: AIMessage = await self.client.ainvoke([msg])
            return self._clean_text(resp.content.strip())
        except Exception as e:
            print(f"Error summarizing article: {e}")
            return ""


async def main():
    nlp = NLPService()
    title = "A simple search engine from scratch"
    summary = await nlp.summarize_article(
        "https://bernsteinbear.com/blog/simple-search/"
    )
    print("summary", summary)

    text = title + "\n\n" + summary
    text_class = await nlp.classify_topic(text)
    print("text_class", text_class)


if __name__ == "__main__":
    asyncio.run(main())

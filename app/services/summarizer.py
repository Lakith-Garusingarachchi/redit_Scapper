import os
from groq import Groq
from dotenv import load_dotenv
from app.models.reddit import Community, Thread

load_dotenv()

GROQ_MODEL = "llama3-8b-8192"


def get_groq_client() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_community(community: Community) -> str:
    client = get_groq_client()

    thread_titles = "\n".join([f"- {t.title}" for t in community.threads[:15]])

    prompt = f"""You are summarizing a Reddit community.

Community: r/{community.name}
Title: {community.title}
Description: {community.description}
Subscribers: {community.subscribers:,}

Recent thread titles:
{thread_titles}

Write a 2-3 sentence summary of what this community is about, what topics they actively discuss, and the general tone or culture of the community."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


def summarize_thread(thread: Thread) -> str:
    client = get_groq_client()

    comments_text = "\n".join([f"- {c.body}" for c in thread.top_comments[:4]])

    prompt = f"""You are summarizing a Reddit thread.

Title: {thread.title}
Post body: {thread.body or "(no text — this is a link or image post)"}

Top comments:
{comments_text or "(no comments available)"}

Write a 2-3 sentence summary covering the main topic of the post and the key discussion points raised in the comments."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()

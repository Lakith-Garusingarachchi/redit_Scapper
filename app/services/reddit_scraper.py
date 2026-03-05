import os
import praw
from dotenv import load_dotenv
from app.models.reddit import Community, Thread, Comment

load_dotenv()


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "RedditThreadExplorer/1.0"),
    )


def scrape_reddit(category: str, max_communities: int = 5, max_threads: int = 20) -> list[Community]:
    reddit = get_reddit_client()
    communities = []

    for subreddit in reddit.subreddits.search(category, limit=max_communities):
        threads = []

        for submission in subreddit.hot(limit=max_threads):
            submission.comments.replace_more(limit=0)

            top_comments = []
            for comment in list(submission.comments)[:5]:
                if hasattr(comment, "body") and comment.body not in ("[deleted]", "[removed]"):
                    top_comments.append(
                        Comment(
                            author=str(comment.author) if comment.author else "[deleted]",
                            body=comment.body[:600],
                            score=comment.score,
                        )
                    )

            threads.append(
                Thread(
                    id=submission.id,
                    title=submission.title,
                    url=f"https://reddit.com{submission.permalink}",
                    upvotes=submission.score,
                    upvote_ratio=submission.upvote_ratio,
                    num_comments=submission.num_comments,
                    body=submission.selftext[:1200] if submission.selftext else None,
                    top_comments=top_comments,
                )
            )

        communities.append(
            Community(
                name=subreddit.display_name,
                title=subreddit.title,
                description=subreddit.public_description or "",
                subscribers=subreddit.subscribers or 0,
                threads=threads,
            )
        )

    return communities

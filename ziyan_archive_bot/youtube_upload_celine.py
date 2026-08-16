from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from oauth_channel_check import get_credentials, get_my_channel

RETRIABLE_STATUS_CODES = {500, 502, 503, 504}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload satu video ke channel Celine setelah preflight OAuth."
    )
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--tags", default="", help="Tag dipisahkan koma")
    parser.add_argument("--category", default="22")
    parser.add_argument(
        "--privacy",
        choices=("private", "unlisted", "public"),
        default="private",
        help="Gunakan private untuk uji pertama.",
    )
    parser.add_argument("--client", type=Path, default=Path("client_secret.json"))
    parser.add_argument("--token", type=Path, default=Path("token_celine.json"))
    parser.add_argument(
        "--expected-channel",
        action="append",
        required=True,
        help="Sebaiknya satu ID Celine yang sudah diverifikasi. Bisa diulang untuk kandidat sementara.",
    )
    parser.add_argument("--max-retries", type=int, default=10)
    return parser.parse_args()


def resumable_upload(insert_request, max_retries: int) -> dict:
    response = None
    retry = 0
    while response is None:
        try:
            _, response = insert_request.next_chunk()
            if response is not None and "id" not in response:
                raise RuntimeError(f"Response upload tidak memiliki video ID: {response}")
        except HttpError as exc:
            if exc.resp.status not in RETRIABLE_STATUS_CODES:
                raise
            retry += 1
            if retry > max_retries:
                raise RuntimeError(
                    f"Upload gagal setelah {max_retries} retry; HTTP {exc.resp.status}"
                ) from exc
            sleep_seconds = min(60, (2**retry) + random.random())
            print(f"Retry HTTP {exc.resp.status} dalam {sleep_seconds:.1f} detik...")
            time.sleep(sleep_seconds)
    return response


def main() -> int:
    args = parse_args()
    if not args.file.is_file():
        raise SystemExit(f"File video tidak ditemukan: {args.file}")

    credentials = get_credentials(args.client, args.token)
    channel = get_my_channel(credentials)
    expected = set(args.expected_channel)
    if channel["id"] not in expected:
        raise SystemExit(
            "STOP: token OAuth bukan untuk channel target. "
            f"Ditemukan {channel['id']} ({channel['title']!r}); target {sorted(expected)}"
        )

    youtube = build("youtube", "v3", credentials=credentials)
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    body = {
        "snippet": {
            "title": args.title,
            "description": args.description,
            "categoryId": args.category,
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    if tags:
        body["snippet"]["tags"] = tags

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(
            str(args.file),
            chunksize=8 * 1024 * 1024,
            resumable=True,
        ),
    )
    response = resumable_upload(request, args.max_retries)

    video_id = response["id"]
    response_channel_id = response.get("snippet", {}).get("channelId")
    if response_channel_id != channel["id"]:
        raise SystemExit(
            "SAFETY_STOP: response video berada pada channel berbeda dari preflight. "
            f"preflight={channel['id']}, response={response_channel_id}, video={video_id}"
        )

    print(f"UPLOAD_OK video_id={video_id}")
    print(f"URL=https://youtu.be/{video_id}")
    print(f"CHANNEL_ID={response_channel_id}")
    print(f"PRIVACY={response.get('status', {}).get('privacyStatus', args.privacy)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

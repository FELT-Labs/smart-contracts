import http.server
import shutil
from pathlib import Path

from brownie import accounts, config

# Set root directory
ROOT = Path(__file__).parent.parent


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["owner_key"])


def copy_project_contract(chain_id):
    """Copy project contract to appropriate folder."""
    chain = "dev" if chain_id == 1337 else chain_id
    shutil.copy(ROOT / "build/contracts/ProjectContract.json", ROOT / f"build/deployments/{chain}/")


# Class for serving build directory
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "build/deployments"), **kwargs)


def server_build_directory(port=8100):
    with http.server.HTTPServer(("", 8100), Handler) as httpd:
        print(f"Server started at http://localhost:{port}")
        print("You can stop the server using Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")

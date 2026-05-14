"""Server runner module for zlsp CLI."""


def start_server(args):  # pylint: disable=unused-argument
    """Start the LSP server."""
    print("Starting Zolo LSP Server...")
    from zlsp.server.lsp_server import main as server_main  # pylint: disable=import-outside-toplevel
    server_main()

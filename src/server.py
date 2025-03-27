import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from constitutional_court import get_constitutional_court_decision
from supreme_court import get_supreme_court_decision
from supreme_admin_court import get_supreme_admin_court_decision
from act_proposals import ActProposals
import logging


def create_server():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("mcp-decisions")
    logger.setLevel(logging.DEBUG)
    logger.info("Starting MCP Decisions")

    # Initialize base MCP server
    server = Server("decisions")

    init_options = InitializationOptions(
        server_name="decisions",
        server_version="0.8",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    proposals = ActProposals()

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        Name must be maximum of 64 characters
        """
        return [
            types.Tool(
                name="get-supreme-court-decision",
                description="Get Czech Supreme court decision based on case number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "case_number": {
                            "type": "string",
                            "description": "Case number of the decision. Must contain 2 digits, break, than text 'Cdo' or 'Tdo', break and than case number, slash and year(e.g. 21 Cdo 1096/2021). If it does not contain text 'Cdo' or 'Tdo', it is not valid Supreme court case number",
                        },
                    },
                    "required": ["case_number"],
                },
            ),
            types.Tool(
                name="get-supreme-administrative-court-decision",
                description="Get Czech Supreme Administrative court decision based on case number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "case_number": {
                            "type": "string",
                            "description": "Case number of the decision. Must contain 1 or 2 digits, break, than registry identificator (one of the following: As | Ads | Afs | Aprk | Aprn | Ars | Azs | Ao | Aos | Av | Komp | Konf | Kse | Kseo | Kss | Ksz | Nk | Na | Ns | Nad | Nao | Obn | Pst | Vol | Rs | Nv), break and than case number, slash and year(e.g. 7 As 218/2021). If it does not contain correct registry identificator, it is not valid Supreme Administrative court case number",
                        },
                    },
                    "required": ["case_number"],
                },
            ),
            types.Tool(
                name="get-constitutional-court-decision",
                description="Get Constitutional court decision based on case number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "case_number": {
                            "type": "string",
                            "description": "Case number of the decision. Must contain senate number (Pl., I., II. etc), dot, than 'ÚS', break and than case number, slash and year(e.g. I.ÚS 23/23 or Pl.ÚS 1589/22). If it does not contain 'ÚS', it is not valid Constitutional court case number",
                        },
                    },
                    "required": ["case_number"],
                },
            ),
            types.Tool(
                name="get-act-proposal-info-by-number",
                description="Get information on proposals in Czech Chamber of Deputies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "proposal_number": {
                            "type": "number",
                            "description": "Number of the proposal to find, e.g. 5 or 255",
                        },
                    },
                    "required": ["proposal_number"],
                },
            ),
            types.Tool(
                name="find-act-proposal-by-name",
                description="Find all acts or amendments proposals by the name of the act in the Chamber of Deputies.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "act_name": {
                            "type": "string",
                            "description": "Name of the act to search (e.g. zákoník práce, o inspekci práce). Do not use 'zákon' at the start of the name. Instead of 'zákon o inspekci práce', use only 'o inspekci práce'",
                        },
                    },
                    "required": ["act_name"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
            name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool execution requests.
        """
        if not arguments:
            raise ValueError("Missing arguments")


        if name == "get-supreme-court-decision":
            case_no = arguments.get("case_number")
            if not case_no:
                raise ValueError("Missing case number parameter")

            result_text = get_supreme_court_decision(case_no)

            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]

        elif name == "get-supreme-administrative-court-decision":
            case_no = arguments.get("case_number")
            if not case_no:
                raise ValueError("Missing case number parameter")

            result_text = get_supreme_admin_court_decision(case_no)

            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]

        elif name == "get-constitutional-court-decision":
            case_no = arguments.get("case_number")
            if not case_no:
                raise ValueError("Missing case number parameter")

            result_text = get_constitutional_court_decision(case_no)

            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]

        elif name == "get-act-proposal-info-by-number":
            proposal_number = str(arguments.get("proposal_number"))
            if not proposal_number:
                raise ValueError("Missing proposal number parameter")

            result_text = proposals.query_data(proposal_number)

            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]

        elif name == "find-act-proposal-by-name":
            act_name = arguments.get("act_name")
            if not act_name:
                raise ValueError("Missing name of the act to find")

            result_text = proposals.query_proposals(act_name)

            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    return server, init_options



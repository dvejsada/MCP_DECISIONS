from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated, Union
from components.utils.detect_court import detect_court_type
from components.constitutional_court import get_constitutional_court_decision
from components.supreme_court import get_supreme_court_decision
from components.supreme_admin_court import get_supreme_admin_court_decision
from components.act_proposals import ActProposals


mcp = FastMCP("MCP Court Decisions")

act_proposals = ActProposals()

@mcp.tool(
    name="get-court-decision",
    description="Get Czech court decision based on case number. Automatically detects which court (Supreme Court, Supreme Administrative Court, or Constitutional Court) based on case number format.",
    tags={"czech", "court", "legal"},
    annotations={"title": "Czech Court Decision Lookup"}
)
async def get_court_decision(
        case_number: Annotated[str, Field(
            description="Case number of the decision. Supported formats: Supreme Court (contains 'Cdo' or 'Tdo', e.g. '21 Cdo 1096/2021'), Supreme Administrative Court (contains registry identificator like As, Ads, Afs, etc., e.g. '7 As 218/2021'), Constitutional Court (contains 'ÚS', e.g. 'I.ÚS 23/23' or 'Pl.ÚS 1589/22')"
        )]
) -> str:
    """Get Czech court decision with automatic court type detection."""

    # Detect court type based on case number format
    court_type = detect_court_type(case_number)

    try:
        if court_type == "supreme":
            return await get_supreme_court_decision(case_number)
        elif court_type == "supreme_administrative":
            return await get_supreme_admin_court_decision(case_number)
        elif court_type == "constitutional":
            return await get_constitutional_court_decision(case_number)
        else:
            return f"Neznámý formát čísla spisu: {case_number}. Podporované formáty:\n" \
                   f"- Nejvyšší soud: obsahuje 'Cdo' nebo 'Tdo' (např. '21 Cdo 1096/2021')\n" \
                   f"- Nejvyšší správní soud: obsahuje registrátor As, Ads, Afs, atd. (např. '7 As 218/2021')\n" \
                   f"- Ústavní soud: obsahuje 'ÚS' (např. 'I.ÚS 23/23' nebo 'Pl.ÚS 1589/22')"
    except Exception as e:
        return f"Chyba při získávání rozhodnutí: {str(e)}"


@mcp.tool(
    name="search-act-proposal",
    description="Search for act proposals in Czech Chamber of Deputies by number or name.",
    tags={"czech", "parliament", "legislation", "acts"},
    annotations={"title": "Czech Act Proposal Search"}
)
async def search_act_proposal(
        query: Annotated[Union[int, str], Field(
            description="Search by proposal number (integer like 5, 255) or act name (string like 'o inspekci práce', 'zákoník práce'). For act names, do not include 'zákon' at the beginning."
        )]
) -> str:
    """Search for act proposals by number or name."""

    global act_proposals

    try:
        if isinstance(query, int):
            return await act_proposals.query_data(query)
        else:
            # It's a string, treat as act name
            return await act_proposals.query_proposals(query)

    except Exception as e:
        return f"Chyba při vyhledávání návrhu: {str(e)}"



if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8957,
        log_level="debug",
        path="/mcp"
    )
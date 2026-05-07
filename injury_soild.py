from __future__ import annotations

import json

from app.services.data_repository import get_player_repository
from app.services.injury import build_future_risk_response


def main() -> None:
    response = build_future_risk_response(get_player_repository())
    print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

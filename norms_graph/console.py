from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from norms_graph.coordination_hub import Application, run, sensitivity, verify


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='norms_graph', description='多边人工智能治理规则冲突解析图谱')
    commands = root.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    check = commands.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    compare = commands.add_parser("sensitivity")
    compare.add_argument("--fixture", required=True)
    compare.add_argument("--baseline-scheme", required=True)
    compare.add_argument("--candidate-scheme", required=True, action="append",
                         help="candidate mapping scheme file; repeat to compare several schemes")
    compare.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "run":
        result = run(args.fixture, args.database, args.output)
    elif args.command == "verify":
        result = verify(args.database, args.output)
    elif args.command == "sensitivity":
        result = sensitivity(args.fixture, args.baseline_scheme, args.candidate_scheme, args.output)
    else:
        result = Application(args.database).inspect()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

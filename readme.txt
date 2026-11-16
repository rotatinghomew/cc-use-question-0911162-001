多边人工智能治理规则冲突解析图谱

运行验收：
python3 -m norms_graph run --fixture fixtures/acceptance.json --database /tmp/norms_graph.sqlite3 --output /tmp/norms_graph-output

核验：
python3 -m norms_graph verify --database /tmp/norms_graph.sqlite3 --output /tmp/norms_graph-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.conflict_signal.test_conflict_pressure -v

构建检查：
python3 -m compileall -q norms_graph tests

映射口径敏感性比较（同一批规则版本下对比映射方案）：
1) 先正常发布案卷
python3 -m norms_graph run --fixture fixtures/sensitivity/scenario.json --database /tmp/sens.sqlite3 --output /tmp/sens-dossier
2) 在同一案卷内追加敏感性报告；--candidate-scheme 可重复以并存多个候选口径
python3 -m norms_graph sensitivity --fixture fixtures/sensitivity/scenario.json \
  --baseline-scheme fixtures/sensitivity/baseline-scheme.json \
  --candidate-scheme fixtures/sensitivity/candidate-scheme-harmonized.json \
  --candidate-scheme fixtures/sensitivity/candidate-scheme-partial.json \
  --output /tmp/sens-dossier
3) 复核：重放报告内嵌的原始条款证据并与已发布 decisions.json 对齐
python3 -m norms_graph verify --database /tmp/sens.sqlite3 --output /tmp/sens-dossier

敏感性模块测试：
python3 -m unittest discover -s tests/sensitivity -v

口径与可追溯约定：
- 冲突核按原始 rule_version 分组比较；rule_catalog_fingerprint 固定实际使用的规则/护栏目录，目录不一致时报告而非强行比较。
- 每个冲突核同时保存基线与候选两套结果（决策、冲突压力、组内/总体排名、delta），状态分为 substantive / ranking_only / unresolved / unchanged。
- 术语未解析时标记 unresolved 并保留原始词项证据；未解析核不会进入任何方案的零冲突清单（缺失不等于零冲突）。
- 无 sensitivity-report.json 的既有案卷仍按原口径通过 verify；summary.json 与 rules.csv 会与 decisions.json 底层证据交叉复核。

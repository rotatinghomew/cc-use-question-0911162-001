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

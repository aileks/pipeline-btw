from pipeline_btw.extract.breweries import extract_data


def rows(start, count):
    return [{"id": str(i)} for i in range(start, start + count)]


def test_stops_at_row_limit_and_truncates_partial_page(monkeypatch):
    """Fetching stops once row_limit is reached and the last page is truncated to fit."""
    calls = []

    def fake_fetch(params):
        calls.append(dict(params))
        page = params["page"]
        return rows((page - 1) * params["per_page"], params["per_page"])

    monkeypatch.setattr("pipeline_btw.extract.breweries.fetch_data", fake_fetch)

    result = extract_data(row_limit=120, rows_per_page=50)

    assert len(result) == 120
    assert [row["id"] for row in result] == [str(i) for i in range(120)]
    assert [params["page"] for params in calls] == [1, 2, 3]
    assert all(params["per_page"] == 50 for params in calls)


def test_does_not_fetch_extra_page_when_limit_exactly_reached(monkeypatch):
    """No extra page is requested when the limit divides evenly into whole pages."""
    calls = []

    def fake_fetch(params):
        calls.append(params["page"])
        return rows((params["page"] - 1) * 50, 50)

    monkeypatch.setattr("pipeline_btw.extract.breweries.fetch_data", fake_fetch)

    result = extract_data(row_limit=100, rows_per_page=50)

    assert calls == [1, 2]
    assert len(result) == 100


def test_stops_when_api_returns_empty_page(monkeypatch):
    """Extraction stops early when the API returns an empty page below the row limit."""
    def fake_fetch(params):
        if params["page"] <= 2:
            return rows((params["page"] - 1) * 50, 50)
        return []

    monkeypatch.setattr("pipeline_btw.extract.breweries.fetch_data", fake_fetch)

    result = extract_data(row_limit=500, rows_per_page=50)

    assert len(result) == 100
